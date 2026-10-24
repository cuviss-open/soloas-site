---
title: "UE_Angelscript 绑定篇——手工绑定 1 - 基础理解"
order: 51
category: binding
---
# UE_Angelscript 绑定篇——手工绑定 1 - 基础理解

# 前言

UE-Angelscript 脚本本身已经提供了大量的常用代码绑定，除了极少的情况外，脚本里能用的功能是大于蓝图的。

为了想要在 AS 里少写点 C++，让书写的体验更接近 C++的代码，这就需要学习如何将 C++的内容绑定到 AS 中，这个在官方文档里是几乎不提的。

本系列文章的**绑定篇**里，之前介绍过了绑定的综述
[UE_Angelscript 绑定篇——综述：暴露更多内容给 AS 和蓝图](binding-overview.md)，建议也要看看，知道整体上都有什么办法能做绑定。

这个综述里提到，绑定代码有三种方式：**手工绑定**、**Mixin**、**继承包装转换**。
其中，**手工绑定** 最为强大，但是也最复杂，本文讲的主要也是这个。一旦理解了 **手工绑定**，那么 **Mixin** 以及 **继承包装转换** 就不在话下了。

**手工绑定** 相对于 **Mixin** ，可以说在功能上是包含关系，也就是说，**Mixin** 能做的，**手工绑定** 都可以（也许有极特殊情况，但我没遇到过）。

**手工绑定** 相对于 **继承包装转换**，除了不能暴露出 **BlueprintEvent** 和 类型的 **非共有成员或函数** 外，其余功能也是包含关系。而本系列文章的**认知篇**提到过，AS 里的声明的 UClass 类型，凡是经常用的，都建议搞一个 C++ 的中间层，除了是因为方便加功能外，还有一个重要原因就是——手工绑定不能完全覆盖住 **继承包装转换** 的功能。

本系列文章还有一些绑定相关的解决方案、避坑操作，读者可以自行查看，一般是遇到问题时就着问题来找答案。

# 手工绑定的理解

## 手工绑定本质上是脏活

本系列文章在此篇之前没有系统地介绍手工绑定的具体操作，为什么？因为这是门手艺活、脏活。这容易产生一个问题——如果理解错误，可能会导致大量的脏活得重做或者重构！

现在经过一段相当长时间的实践，以及对脚本源码理解更深一点点之后，个人认为经验算是足够丰富了，此篇相关的内容就可以发表出来了，但仍不能保证是精准无误的，读者需要自己分析判断以及实践。

免责声明——本文不是官方文档，是技术分享，仅供参考，不保证完全正确。

好了，免责声明完成后，这就简单提一提一个事——有时候你会发现 AS 有一些函数并没有文档说明，而蓝图和 C++的对应 API 是有的，这种情况大概率是绑定的时候懒得写了。

为什么懒得写呢，因为都是拷贝的操作，有多少绑定就有多少拷贝，总而言之，绑定代码一旦熟悉了套路后，剩下的就是脏活了，虽然有大量的宏工具来辅助，但还是脏活。

## 手工绑定也是一门手艺

这里就不得不提官方对 UClass 和 UStruct 类型的绑定了，这些类型数量极其庞大，官方写了批量绑定的代码，这其实是手艺！

另外关于模板的绑定，也是相当的复杂，是脏活没错，但这不是简单的脏活，而是需要精巧的设计。什么 `TArray<>` `TMap<>`等，处理起来并不简单。

凡是手艺活，就需要一些特定的知识，除了 UE 引擎相关的，还需要不少对 C++ 底层知识的理解，特别是内存的操作，另外，Angelscript 这个脚本本身，也是要有点理解的。

如果学习这个手艺呢？

仅就实操而言，UE-Angelscript 这插件已经提供了很多范例，照猫画虎，就可以学到很多很多了。如果碰到了什么不会绑定的，就在插件源码里找找类似的，也许看看就豁然开朗。

# Angelscript 的绑定基础知识

UE-Angelscript 即使是魔改了的 Angelscript，但它仍然是 Angelscript，所以 Angelscript 文档是理解 UE-Angelscript 的出发点。

Angelscript 官方文档链接如下：
https://www.angelcode.com/angelscript/sdk/docs/manual/index.html

这个文档对 Angelscript 本身做了各方各面的介绍，有详细的示例，不过需要注意，因为 UE-Angelscript 使用的不是最新版本，同时做了一些魔改，所以此文档只能是参考。

本文重点关注的是绑定方面的内容，摘取部分重要的概念来说明。

## 绑定类型——值与句柄

- 值类型，对象本身，对应于——在 UE-Angelscript 里就是除了 UObject 类型之外的一切类型； 在 C++ 里也是如此。
- 对象句柄，_Object handles_ ，对应于——在 UE-Angelscript 里的 UObject 类型；在 C++ 里，对应于 UObject 指针。

总之一句话，UE-Angelscript 里的 UObject 及其子类，都是对象句柄类型；除此之外，都是值类型。

值类型和对象句柄的核心区别就是，值类型指代自身，拷贝的话，就是将自己复刻一个出来，而对象句柄用来指代其他具体的对象，拷贝的话，仅仅是拷贝自身而已，不拷贝其指代的对象。

为什么存在对象句柄，这是要和指针对应。UObject 这种类型很多都是重量级的，用对象句柄或者指针来操作，会轻量化很多，而且可以防止不小心的拷贝带来的性能问题。

## AS 引擎一些关键内容

这部分内容稍微深一点，不需要的时候可以跳过。但要了解泛型绑定，这是最好要了解的。

### AS 脚本引擎

`class asCScriptEngine* Engine` 是 AS 引擎对象，在 FAngelscriptManager 里可以获取到

```cpp
/* Internal script data. */
class asCScriptEngine* Engine = nullptr;

asIScriptEngine* GetScriptEngine() const
{
    return (asIScriptEngine*)Engine;
}
```

asC 开头的，都是对象本身，asI 开头的，是接口， Angelscript 喜欢这么写，即使接口只有一个子类，所以，常用的那些接口和对象本身类型都是可以互相强转的。

### AS 模块

UE-Angelscript 里，我们只用一个 AS 模块。Angelscript 支持多模块，就看使用者是否使用了，UE-Angelscript 选择的是单模块模式。

```cpp
const asCModule* Module = static_cast<asCModule*>(Engine->GetModuleByIndex(0));
```

这个 API 如果获取不到会返回 nullptr。

因为是单模块的设计，所以，我们在 AS 里声明的类型，最终都是一下的模块形式：

```cpp
auto ObjPath = f"/Script/Angelscript.{ParentNameStr}";

UClass ParentClass = Cast<UClass>(FindObject(ObjPath));
```

AS 声明的类都在 `/Script/Angelscript `里。
注意，类的开头的 A U F 等不可以有，枚举除外，枚举则是必须完整。

Engine 和 Module 如有类似的 API，一般 Module 获取到的比较精准。比如 AS 里定义的全局函数和全局函数这种，都是在 Module 的命名空间里。

### AS 类型信息

```cpp
asCTypeInfo* Info = (asCTypeInfo*)Engine->GetTypeInfoById(TypeId);
```

asCTypeInfo 有 AS 能用的类型的所有类型信息，不管是绑定过来的还是自身声明的类型，都有一个对应的 asCTypeInfo ，我们可以方便地获取到很多类型信息，比如 `GetName()` 就轻松地获取到了类型名。

asCTypeInfo 有一个成员，我们在做泛型绑定的时候经常用到，就是 `typeId`,这和 C++ 的不一样，是 Angelscript 　独立的一套　 ID 体系，每个类型对应唯一的一个。

asCTypeInfo 还有一个关键的成员 `plainUserData`,这是给用户自定义数据的指针，UE-Angelscript 用它来存放了某类型相关的反射信息的类型，比如 UObject 及其子类，就会在`plainUserData`存 `UClass*`。

当然并不是所有 `plainUserData` 都存有反射信息的内容，看具体情况了，比如 UE-Angelscript 里对 UENUM 的处理就没有统一（截至到 UE5.5 版本），C++ 里声明的 UENUM 在对应的 asCTypeInfo 里存了 `UEnum*` ，而 AS 声明的，就没有。

## 绑定方法的封装——FAngelscriptBinds::Bind

### 原理简析

首先，对 C++ 与 AS 的交互，用一个全局单例来管理，即

```cpp
FAngelscriptManager::Get()
```

在哪里都经常看到它。不过作为大总管，绑定的事情虽然涉及不少，但是核心的绑定代码还是交给专门的小弟来处理，即

```cpp
struct ANGELSCRIPTCODE_API FAngelscriptBinds
```

FAngelscriptBinds 作为小弟，其又安排了一个小弟来作为跑腿的，让绑定信息可以传给大总管 FAngelscriptManager ，即

```cpp
FAngelscriptBinds::Bind
```

这个类型完全就是跑腿作用，利用它的构造函数来注册绑定内容

```cpp
struct ANGELSCRIPTCODE_API FBind
{
    FBind(int32 BindOrder, TFunction<void()> Function)
    {
       FAngelscriptBinds::RegisterBinds(BindOrder, Function);
    }

    FBind(EOrder BindOrder, TFunction<void()> Function)
    {
       FAngelscriptBinds::RegisterBinds((int32)BindOrder, Function);
    }

    FBind(TFunction<void()> Function)
    {
       FAngelscriptBinds::RegisterBinds(0, Function);
    }
};
```

提这个小弟的跑腿是因为，我们的绑定代码核心是与它打交道，只要你在写绑定代码，那真是得天天见面！

这个小弟的跑腿工作，只是把我们写的绑定代码转交给一个 GetBindArray() 这个全局单例，这个全局单例最终才是给大总管 FAngelscriptManager 交差的。毕竟大总管 FAngelscriptManager 日理万机，如果直接对接那么多绑定工作，还是不合适的。

```cpp
static TArray<FBindFunction>& GetBindArray()
{
    static TArray<FBindFunction> BindArray;
    return BindArray;
}

void FAngelscriptBinds::RegisterBinds(int32 BindOrder, TFunction<void()> Function)
{
    GetBindArray().Add({BindOrder, Function});
}
```

这个小结的内容在**源码篇**里将上下文流程都讲过了，这里只是重点提了整个流程中与绑定最密切的部分。

这里得到一个结论——每构造一个`FAngelscriptBinds::Bind` 实例，就会将构造这个实例的参数（绑定顺序、绑定运行的函数）暂时存起来，然后等待 FAngelscriptManager 在合适的时机调用。

### 绑定顺序

构造一个`FAngelscriptBinds::Bind` 实例，第一个重要参数就是绑定顺序。当你缺省不写时，是 0。

一般情况下，会用一个 Enum 来控制顺序而不是直接使用数字。

```cpp
enum class EOrder : int32
{
    Early = -100,
    Normal = 0,
    Late = 100,
};
```

对于这几个阶段，插件源码里虽然没有直接的注释，但是通过查看各类绑定的代码，可以大概得到这么一个用法——
Early 阶段一般用于绑定声明，以及参数为空、参数为自身类型、参数为基础类型的构造函数。
Normal 阶段用于比较少。
Late 阶段一般用于绑定构造函数、成员、成员函数。

绑定顺序挺重要的，如果写错，使用了没有绑定过声明的类型，那么就会导致这个绑定报错，一般会在 Log 里报出来说某某绑定注册失败。

### 绑定函数体

这里列举一些最常见的绑定函数以及重要概念，重在讲解基础知识。

构造一个`FAngelscriptBinds::Bind` 实例的第二个参数是一个函数指针，一般用匿名函数 Lambda 来写。

在函数体内部，一般是先声明一个 FAngelscriptBinds 变量，然后就对这个 FAngelscriptBinds 变量进行操作。

```cpp
auto FQuat_ = FAngelscriptBinds::ValueClass<FQuat>("FQuat", Flags);
FAngelscriptType::Register(MakeShared<FQuatType>());
FQuat_.SetTypeUserData(TBaseStructure<FQuat>::Get());
```

这里的 `ValueClass` 是在 Early 阶段绑定声明，这里绑定方式顾名思义，是值类型绑定。（另外还有 `ReferenceClass` 用于引用类型绑定，可以绑定为 Angelscript 的对象句柄，只对 UObject 使用。）

`FAngelscriptType::Register` 函数是注册一个描述类型 `FAngelscriptType` 给刚刚声明的类型，这个描述类型的重要用途之一是 UE-Angelscript 插件用于描述这个类型作为其他类型的成员的时候有什么特性。

对于描述类型 `FAngelscriptType` ，是一个重要概念，后续会单独解释。

凡是绑定的普通 struct 新类型，最好都要自定义一个`FAngelscriptType`，否则就可能会面临一些问题，比如默认情况下，无法放入 TArray 等容器中。

`SetTypeUserData` 则是配置用户自定义的类型信息，这里是将 UScriptStruct 类型信息注入了 asCObjectType 的 plainUserData，以供后续使用。

```cpp
FAngelscriptBinds FQuat_ = FAngelscriptBinds::ExistingClass("FQuat");
```

`ExistingClass` 用于获取之前已经绑定声明的类型对应的 FAngelscriptBinds，从而对其进行其他绑定操作。

FAngelscriptBinds 有很多绑定方法，最常用的是

```cpp
Constructor
Property
Method
```

Constructor 是用来绑定构造函数的，Property 是用来绑定成员的，Method 是用来绑定成员函数的。

所有这些绑定，本质上是同一份内存在 C++里和在 Angelscript 的映射，这同一份的内存，在 C++ 叫这么一个名称，比如`张三`，在 Angelscript 里未必叫`张三`，你可以指定叫做`李四`，甚至可以指定为`李四<小白>`（泛型绑定）。

有时候，你可以做一些神奇的操作，只要内存布局一致，比如 C++ 里的 M 和 N 类型的内存布局一致（这是因为我不方便访问 M ，从而复刻了一个 N），那么把 N 映射为 Angelscript 里叫做 M 的类型，也完全没有问题。

## 描述类型 `FAngelscriptType` 与 USage

### FAngelscriptType

它的注释如下，可以理解为是一个描述 Angelscript 类型自身情况以及与其他类型如何沟通的结构体。

```cpp
/**
 * FAngelscriptType holds all information necessary to
 * communicate types between their UClass/FProperty variants
 * and the methods angelscript needs to know about them.
 *
 * This will be subclassed by various Binds_*.cpp files
 * in order to implement specific type operations.
 */
struct ANGELSCRIPTCODE_API FAngelscriptType : TSharedFromThis<FAngelscriptType>
```

有这么一些相对的概念需要区分：

- UCLASS 类型 --> UClass 类型信息
  每一个 UObject 都有一个 UClass 对应。

- USTRUCT 类型 --> UScriptStruct 类型信息
  每一个 USTRUCT 都有一个 UScriptStruct 对应。
  有时候表述为 UnrealUStruct，在一些文章里也会简化写 UStruct，但需注意语境，因为 UStruct 也是一个类型，是 UClass 和 UScriptStruct 的父类。

- UENUM 类型 --> UEnum 类型信息
  每一个 UENUM 都有一个 UEnum 对应。

- `所有 Angelscript 里出现的类型` --> `asCTypeInfo` 类型信息
  asCTypeInfo 中的 plainUserData 可以存 UClass、UScriptStruct、UEnum 等各种各样的信息，看具体需求。

- `所有 Angelscript 里出现的类型` --> `FAngelscriptType` 类型描述信息
  FAngelscriptType 和 asCTypeInfo 其实有些内容是可以对应的，但是 FAngelscriptType 可以高度自定义，而我们不想修改 asCTypeInfo，所以用 FAngelscriptType 。

### FAngelscriptTypeUsage

它的注释如下，可以理解为每一个类型的具体使用情况。比如大家都是 TArray 类型，明显会根据 Array 里子类型、数量等信息而产生不同的使用情况。另比如大家都是 UObject 类型，也会有 const 与否的不同。这个类就是用来描述这些情况的。

```cpp
/**
 * Describes a particular usage of an angelscript type,
 * including all qualifiers, wrappers, and other.
 */
struct ANGELSCRIPTCODE_API FAngelscriptTypeUsage
```

这个类型在绑定相关的内容中，用的比较多的是泛型绑定时的类型比对。因为它可以沟通 FAngelscriptType ，同时可以**直接从 TypeId 生成**。

```cpp
// Match a type usage to an angelscript TypeId
static FAngelscriptTypeUsage FromTypeId(int32 FAngelscriptType);
```

直接从 TypeId 生成，意味着什么呢，意味着泛型绑定的极大便利，可以验证用户输入的类型是否正确！限于篇幅，此处就不深入泛型绑定的内容了。

## 全流程绑定三部曲

因为 USTRUCT 、 UCLASS 、 UENUM 都被插件处理了，所以我们实际要全流程绑定的，主要是普通的结构体 plain struct ，所以这里就以 plain struct 为例。
假设你已经有了 FTestStruct 这么一个结构体。

- 创建一个 FAngelscriptType 类型
  一般是继承于 ` TAngelscriptCppType<NativeType>`，然后覆写一些函数。

- 创建一个 FAngelscriptBinds::FBind 全局变量用于绑定声明
  绑定顺序一般是在 Early 阶段附近。
  绑定声明的同时，将 FAngelscriptType 类型关联起来。
  SetTypeUserData 看情况是否设置。

- 创建一个 FAngelscriptBinds::FBind 全局变量用于成员和函数
  绑定顺序一般是在 Late 阶段以后
  如果构造函数没有绑定，一般都要绑定一个默认构造函数，否则 Angelscript 里无法直接声明。

---

本篇主要讲解了基础知识以及最后给出手工绑定的三部曲，如果有时间了再整理具体的绑定细节，这些内容都是所谓的手艺了。

现阶段，UE C++ 的 API 除了 Lambda 等函数指针、模板、接口以外，都可以比较容易地和 Angelscript 一一对应，包括裸指针，不一定非得绑定为引用类型。这种 API 的对应，对于 C++ 和 Angelscript 同时用的人来说，会比较舒适。

---
