---
title: "UE_Angelscript 绑定篇——避坑：不踩一下，怎知是坑"
order: 57
category: binding
---
# UE_Angelscript 绑定篇——避坑：不踩一下，怎知是坑

本篇一条一条地罗列，未必都分门别类了，权当避坑小贴士。

有一些内容在绑定篇的其他地方也会提到，这里再提的话，相当于划重点了吧。

## 不要相信 UStruct 的继承，AS 只认当前的 UStruct

按照 AS 的绑定逻辑，UStruct 如果没有标记为 BlueprintType 或者没有包含暴露给蓝图的内容（继承的不算），那么，这个 UStruct 不会进入 AS 的绑定清单。

也就是说，你会发现，这个 UStruct 在蓝图里用得好好的（因为它的父类暴露给蓝图了），但是 AS 里查无此类！

例如

```cpp
struct FAnimUpdateContext : public FAnimExecutionContext
```

## 不要相信 UStruct 的继承，给它增加绑定功能，你得将子子孙孙都一起处理

如果某个 UStruct 有一群子孙，你给这个爷爷辈的 UStruct 增加了绑定功能，不管是手工绑定还是 Mixin 绑定，都只对你所操作的 UStruct 生效。

总之一句话，UStruct 的继承，在 AS 里就相当于没有。是的，AS 里写代码，UStruct 是不能有继承的，甚至不可以写函数（如果非要给增加函数，用 Mixin 大法）。

## Meta 里有 BlueprintInternalUseOnly ，AS 就不认了

meta = (BlueprintInternalUseOnly = "true")
这个标记加上后，AS 就访问不到这个函数了。

```cpp
// 这个函数没办法被AS访问到
    UFUNCTION(BlueprintCallable, meta = (BlueprintInternalUseOnly = "true"))
    void TestBlueprintInternalUseOnly()
    {
       UE_LOG(LogTemp,Warning,TEXT("Test BlueprintInternalUseOnly UFUNCTION Show"));
    }
};
```

这个本来是限制蓝图的使用范围的，AS 是接过蓝图的大部分内容的，现在同样作用于 AS 。但是 AS 又没有蓝图的一些特性，比如识别使用范围，导致这类函数相当于不能调用。

比较好的解决方式就是 Mixin 绑定，或者新写一些蓝图库函数（针对一些静态函数）。

另外一个方式是通过各种方式，去掉 BlueprintInternalUseOnly。

最后是修改 AS 脚本插件的代码，在 Bind_BlueprintCallable 里放行 BlueprintInternalUseOnly，全部放行就注释掉限制 BlueprintInternalUseOnly 绑定的代码，部分放行就得写各种判断。

如果这个 UClass 被标记为 MinimalAPI，而 BlueprintInternalUseOnly 恰好又被加上了你想调用的 UFUNCTION。因为你写的 Mixin 函数一般在其他模块里，那么正常通过 cpp 是不能调用这个函数的。怎么办？此时，就可以祭出反射大法了，通过反射可以获取、调用已知函数名的成员函数。

针对这个问题，详细的解决方案总结看这里，会列出详细的代码：
[UE_Angelscript 绑定篇——解决方案：BlueprintInternalUseOnly 函数的增强处理方式](binding-blueprint-internal-use-only.md)

## AS 绑定的是原始函数名，而不是 Display 名。

原始函数名会根据规则掐头去尾。
这种情况下，蓝图显示的名称和 AS 里的名称就不一致了。

如蓝图里的 Multi Line Trace By Channel 的原始函数名是 LineTraceMulti， Line Trace By Channel 的原始函数名是 LineTraceSingle。

有时候看到一些蓝图函数，想按图索骥，发现找不到函数名，这时只能跳转到 cpp 的代码来查看这个函数真正名称是什么。

## AS 的 TMap 的 key 会限制一些绑定的原生 struct

举例子：FObjectKey 绑定后，仍然无法用于 TMap 的 key。会报错如下：

```cpp
Attempting to instantiate invalid template type 'TMap<FObjectKey,FGameplayAbilitySpecHandle>': Containers cannot be nested in other containersas
```

不知道是不是因为它没有 public 的成员。

解决方案，是用一个 FObjectKeyWrapper 包装起来，实现 GetTypeHash 函数以及一批重载操作符的比较函数。

更新：更好地绑定方案，需要在手工绑定时候将这个类关联一个继承自 TAngelscriptCppType 的类，参考如下。此方案适用于 TMap、TArray、TSet。

```cpp
#include "Binds/Helper_CppType.h"
///// Add this
struct FObjectKeyType : TAngelscriptCppType<FObjectKey>
{
	FString GetAngelscriptTypeName() const override
	{
		return TEXT("FObjectKey");
	}

	bool GetCppForm(const FAngelscriptTypeUsage& Usage, FCppForm& OutCppForm) const override
	{
		OutCppForm.CppType = GetAngelscriptTypeName();
		return true;
	}
};

AS_FORCE_LINK FAngelscriptBinds::FBind Bind_ObjectKey((int32)FAngelscriptBinds::EOrder::Late + 100,[]
{
	FBindFlags Flags;
	Flags.bPOD = true;
	FAngelscriptBinds ThisBind = FAngelscriptBinds::ValueClass<FObjectKey>("FObjectKey", Flags);
	///// Add this
	FAngelscriptType::Register(MakeShared<FObjectKeyType>());
```

## Mixin 绑定的时候，this 指针 的 const 标识符不能丢

需要记住，const 不会凭空丢失。Mixin 绑定的时候，const 如果修饰 this 指针，那么 Mixin 的静态函数的首个参数，也必须带 const 。

举例如下。

```cpp
//  这个要被绑定的 FGameplayAttribute 的原始函数
float GetNumericValueChecked(const UAttributeSet* Src) const;

// 这是 FGameplayAttribute 的一个 Mixin 函数
UFUNCTION(BlueprintCallable)
static float BP_GetNumericValueChecked(const FGameplayAttribute& GameplayAttribute, const UAttributeSet* Src)
{
    return GameplayAttribute.GetNumericValueChecked(Src);
};

// 绑定后，AS 里会将这个函数显示为
float32 FGameplayAttribute.GetNumericValueChecked(const UAttributeSet Src) const

// 总结：Mixin 函数 的 const FGameplayAttribute& GameplayAttribute 的 const 变成了 AS 里函数签名末尾的 const ，表示不修改类成员。最终的形式和原始函数基本一致。
```

## UGameplayMessageSubsystem 尽量不要 cpp 和 AS 混用

UGameplayMessageSubsystem 是一个不错的解耦 Subsystem ，类似于一个中枢广播系统，发送的信息是各种各样的 UStruct 。可以先看看本专栏的相关文章——UE_Angelscript 之 GameplayMessageSubsystem 与 GameplayTags 。

因为 UGameplayMessageSubsystem 传递的是各种各种的 UStruct ，这些 UStruct 可能在传递的时候出现问题。

就是说，最好不要一个发送信息和接受信息的分别属于 cpp 和 AS，不然可能产生报错。

## 动画系统的绑定，涉及异步执行的时候，很麻烦

比如 Lyra 示例项目，采用了异步执行的方案，那些异步调用在蓝图里写起来比较方便，在 AS 里就还没有这类绑定。（或者是我还没研究明白。）

## 谨慎使用 Delay 函数。AS 里自动绑定好的 Delay 更要谨慎使用。

AS 里和 cpp 同时类似的 Delay 代码，AS 版本的有时候会导致 Delay 的时间变长。

问题原因，个人推测是 Delay 的机制是阻塞进程，这种阻塞或许与脚本的虚拟机相互影响。

不管什么原因吧，能用 Timer 就用 Timer。

## 想绑定模板函数？放弃吧，特例出来几个不好么？

AS 本身不支持模板，类似模板的一些写法，是经过特殊处理的。如果想使用 cpp 里的一些方便的模板函数，可以考虑特例出来几个，通过 Mixin 或者直接写入蓝图函数库。

AS 只是个轻量化的脚本，不用什么都往里面搬运。

---
