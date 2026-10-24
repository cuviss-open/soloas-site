---
title: "UE_Angelscript 源码篇 2：AS 的类绑定到 UE"
order: 41
category: internals
---
# UE_Angelscript 源码篇 2：AS 的类绑定到 UE

接上篇。

阅读条件——需有 C++ 、 UE 、Angelscript 的相关知识。

# AS 的类编译到 UE 的类

## 问题：AS 的类如何才能让 UE 识别

准确来说， 将 AS 的类绑定到 UE，主要是用 AS 的代码生成反射信息给到 UE 的反射系统。（这里稍微解释一下，UE 的反射系统可以在运行时动态提供类的信息，这是本文所说的绑定到 UE 的概念。）

### 预处理

AS 脚本里可以写类似 U++ 中的 UCLASS、USTRUCT 、UENUM 、 UPROPERTY 、UFUNCTION 等宏，这种宏写在 AS 里，并不参与 AS 引擎本身的编译，它只是提供信息给反射系统。

UE-AS 插件是这么操作的，通过 C++ 来读取 AS 文件，通过宏或者关键字获取需要的反射信息，然后动态生成反射的类型（UClass 等），而原本的 AS 文件代码，会被处理成最终给到 Angelscript 虚拟机运行的内容，其中，宏一般是删掉的。

经过上面的操作，不难看出来，你在 AS 脚本写的代码并不是最终在 Angelscript 虚拟机运行的代码，你的 AS 代码还需要经过插件的预处理，将宏以及一些特殊符号（比如 delegate)给删除或者转换为其他代码，这属于元编程（用代码生成代码）的范畴。

以下，给两段代码进行参考：
这是原本在 AS 里写的，

```C++
UCLASS(Abstract)
class UGameplayAbility_Test : UGameplayAbility
{
    UPROPERTY(Category = "Test")
    float32 TestFloat = 1;
   
	UFUNCTION(BlueprintOverride)
	void ActivateAbility()
	{
		// skip
	}
}
```

这会生成如下代码：

```C++
class UGameplayAbility_Test : UGameplayAbility
{

    float32 TestFloat = 1;

    void ActivateAbility_Implementation()
    {
        // skip
    }
}

const TSubclassOf<UObject> __StaticType_UGameplayAbility_Test;

namespace UGameplayAbility_Test {
    UClass StaticClass() __generated
        {
            return __StaticType_UGameplayAbility_Test;
        }
    }
```

可以看到，所有宏都被去掉了，还会在最后新增一些代码，是用来给类型增加函数的。

接着，我们稍深入一下，看看它是如何预处理 AS 代码的。

这个处理流程主要写在 void FAngelscriptManager::InitialCompile() 函数中，这里会有一个加载脚本的判断，根据条件可以选择使用预编译数据，但一般我们开发的时候，默认是使用 AS 脚本源代码的，此处也着重说的是 AS 脚本源代码的处理。

分析其代码逻辑，总体流程如下：

创建一个预处理器，其构造函数会读取 AS 的配置文件，就是那些项目设置里的可选配置。
这个预处理器是 FAngelscriptPreprocessor Preprocessor；它有一个重要函数叫做
bool FAngelscriptPreprocessor::Preprocess()，里面详细写了它是如何处理 AS 脚本源代码的。

核心流程如下：

---

1. **异步加载脚本文件内容**
   - 如果有异步加载请求，先调用  `PerformAsynchronousLoads()`，确保所有脚本文件内容都已加载到内存。
2. **分块解析（ParseIntoChunks）**
   - 对每个文件，调用  `ParseIntoChunks(File)`，将原始代码分割成多个“块”（Chunk），每个块代表一个类、结构体、全局、枚举等。
3. **检测类、结构体、枚举（DetectClasses/DetectEnum）**
   - 遍历所有块，识别并记录所有类、结构体、枚举的描述信息，生成  `FAngelscriptClassDesc`、`FAngelscriptEnumDesc`  等。
4. **分析类和结构体（AnalyzeClasses/AnalyzeStructs）**
   - 进一步分析每个类/结构体的继承关系、静态成员、自动生成的静态函数等。
5. **处理宏（ProcessMacros）**
   - 处理所有 UPROPERTY/UFUNCTION/UCLASS 等宏，生成属性、方法等描述信息。
6. **处理委托（ProcessDelegates）**
   - 处理脚本中的 delegate/event 相关声明。
7. **广播钩子（OnProcessChunks）**
   - 允许外部监听器对每个预处理器实例进行自定义处理。
8. **处理默认值（ProcessDefaults）**
   - 处理 default 语句，生成默认值代码。
9. **合并块内容（CondenseFromChunks）**
   - 将所有块的内容合并成最终的“预处理后代码”（`File.ProcessedCode`），并追加自动生成的代码。
10. **后处理（PostProcessRangeBasedFor/PostProcessLiteralAssets）**
    - 处理 for-range 语法、asset 语法等特殊语法糖。
11. **广播后处理钩子（OnPostProcessCode）**
    - 允许外部监听器对最终代码做进一步处理。
12. **生成模块代码段**
    - 把  `File.ProcessedCode`  作为代码段（`FCodeSection`）添加到  `File.Module->Code`，供后续编译器使用。
---

可以看到，其做的事情很多，但可以分为：

- 生成预处理后的最终 Angelscript 代码。
- 生成反射信息的描述

最终 Angelscript 代码被编译为 Angelscript 虚拟机运行的字节码；反射信息的描述用于生成 UClass、UScriptStruct 等反射描述类型。

### 编译

预处理完成之后，就是对代码的编译了。编译的实现被写在了 ECompileResult FAngelscriptManager::CompileModules 函数中。

简化的流程如下

```
   ├─► 递归收集所有待编译模块及依赖
   │
   ├─► Stage 1: 生成类型信息（CompileModule_Types_Stage1）
   │
   ├─► 并行解析脚本源码（BuildParallelParseScripts）
   │
   ├─► 生成类型元数据（BuildGenerateTypes）
   │
   ├─► Stage 2: 生成函数元数据（CompileModule_Functions_Stage2）
   │
   ├─► 处理依赖与类型引用替换
   │
   ├─► 类布局、全局变量分配
   │
   ├─► Stage 3: 编译脚本代码（CompileModule_Code_Stage3）
   │
   ├─► Stage 4: 初始化全局变量（CompileModule_Globals_Stage4）
   │
   ├─► 模块切换与热重载（SwapInModules）
   │
   ├─► 清理、后处理、注册测试
   │
   └─► 返回编译结果（ECompileResult）
```

可以看到，主要是分为 4+ N 辅助阶段，里面的编译细节其实相当复杂繁琐。但其实我们可以重点关注预处理时候的两部分内容都去了哪里。

预处理后的最终 Angelscript 代码：

本体的 Angelscript 代码编译完成后，其后会以字节码运行，这部分是 Angelscript 语言自带的特性。在这里并不会详细说明 Angelscript 的运行机制， 所以从略了。

反射信息的描述：

这个值得多说一些。UE 反射系统中的 UObject 是用 UClass 描述的，而 AS 插件使用继承 UClass 的一个类型——UASClass，UASClass 里增加了更多的描述信息，这个类就是此阶段生成的。

我们完全可以重点关注一个问题，这个问题清晰了，其他的自然而然地容易明白——UASClass 是如何生成的？

经过查询，代码中的调用链如下：
InitialCompile()  
   └─► CompileModules()  
         └─► FAngelscriptClassGenerator::AddModule()  
               └─► FAngelscriptClassGenerator::Setup()  
                     └─► FAngelscriptClassGenerator::PerformSoftReload()/PerformFullReload()  
                           └─► 生成并注册 UASClass

这个调用是在【模块切换与热重载（SwapInModules）】阶段，这一步是在整个流程的较末阶段，主要是为了确保 Angelscript 本身的代码可以编译成功（Stage 4 运行完成，没错误的话，就算代码没问题，此时才去更新 UE 的反射信息，挺合理的） 。

UASClass 为了将 UE 与 AS 的沟通便利，同时为了方便 C++ 调用 AS 类型的信息，增加了不少成员和成员函数。

比如 AS 代码里增加的特性——可直接在 AS 里用 UPROPERTY 声明 DefaultComponent，这个特性用起来很舒适的！

这个特性的 DefaultComponent 信息被写在 UASClass 的`TArray<FDefaultComponent> DefaultComponents`变量里， `FDefaultComponent` 详细列出了这个成员的反射信息； `OverrideComponents` 同理。

```C++
	struct FDefaultComponent
	{
		UClass* ComponentClass;
		FName ComponentName;
		SIZE_T VariableOffset;
		bool bIsRoot;
		bool bEditorOnly;
		FName Attach;
		FName AttachSocket;
	};
```

主要类型的链接桥梁不仅仅有 UASClass ，还有 UASStruct、UASFunction（UASFunction 下又分为多个变体）。

这几个链接的桥梁基本足够脚本使用了。

有人也许还会疑惑，不是还有 UEnum、delegate 吗？它们不需要反射信息？

需要反射信息的，但是 UEnum 没有专门继承一个类型来描述它，它比较简单，目前还不打算给它新增描述信息（这实际上会带来一些自省的难度，不过还是有办法解决的）。

AS 里实现的 delegate/event，实际上会被预处理为一个 struct 类。

脚本官方示例里有 FExampleEventSignature 这个 delegate/event，其实际上会被替换为以下一大段代码：

```C++
struct FExampleEventSignature {_FMulticastScriptDelegate _Inner;FExampleEventSignature() __generated no_discard {}FExampleEventSignature(const FExampleEventSignature& Other) __generated no_discard { this = Other; }FExampleEventSignature& opAssign(const FExampleEventSignature& Other) __generated { _Inner = Other._Inner; return this; }void Broadcast(UObject Object, float Value) const __generated {if (!_Inner.IsBound()) return; __Evt_PushArgument__UObject(Object); __Evt_PushArgument__float(Value); __Evt_ExecuteDelegate(_Inner);}void AddUFunction(const UObject Object, const FName& FunctionName) __generated { _Inner.AddUFunction(Object, FunctionName, __DelegateSignature(this)); }void Unbind(UObject Object, const FName& FunctionName) __generated { _Inner.Unbind(Object, FunctionName); }void UnbindObject(UObject Object) __generated { _Inner.UnbindObject(Object); }bool IsBound() const __generated { return _Inner.IsBound(); }void Clear() __generated { _Inner.Clear(); }};
```

看着挺乱，实际上就是一个 struct 类型和一批函数。这个代码是预处理时期批量替换的，不是给人看的，所以它也不需要格式化。

UASFunction 类似 UASClass 的，增加了一些描述信息，同时因为返回值或者其他特性的不同，继承下来一批 UASFunction，覆写它的 RuntimeCallFunction 和 RuntimeCallEvent 函数。

至此，AS 脚本里我们常写的那些类型都过了一遍，有详有略，算给个大体印象了。

如需了解细节的，还是看看源码吧（让人头大）。友情提醒，C++ 的实现文件还是不要一开始就沉浸其中，比如预处理的实现部分——操作字符来生成代码（我打开时，内心：我就随意翻翻，打扰了，再见！）。

---
