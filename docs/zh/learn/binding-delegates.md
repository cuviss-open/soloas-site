---
title: "UE_Angelscript 绑定篇——Delegate 自由调用，看似虚幻，实尽在手中"
order: 53
category: binding
---
# UE_Angelscript 绑定篇——Delegate 自由调用，看似虚幻，实尽在手中

**对于绑定到AS，基于本文的思路，还可以发展出更好更简洁的方式，不过需要对 Cpp 和 AS 的内存对应有比较深刻的理解——通过内存的对应关系，可以直接让 Cpp 的委托映射到 AS 中使用，除了不能放进 UPROPERTY 之外，当作普通的类型来用，没什么缺点。**

**虽然如此，此文的整体思路还是有很大参考价值的，更好的方式是从此改善而来的。**

预警，本文包含大量的 cpp 代码，试图解释一个整体的思路。本文因整体方案代码量过多，不会将所有的实现（特别是 cpp 宏的代码）都列出。

预警，不必过多纠结于代码，看整体思路，因为本文需要不少AS 绑定相关知识，建议先看本系列文章的其他绑定篇。
# 前言

UE 里的委托是一种很好用的回调写法，如需要十分具体的相关内容请查看官方文档。

这里从两个维度区分委托。

1、UE 的委托分为普通委托和动态委托。

普通委托简单高效，开销小，仅用于 cpp，而动态委托可以给到蓝图使用，说是略增加开销。

2、UE 的委托又分为单播、多播。

单播和多播的区别是单播可以只可以绑定一个回调，而多播可以绑定多个回调；单播可以声明返回值，而多播没有返回值（可以通过传引用参数实现类似返回值的效果）。

另外，提一个 UE 里的事件，也是一种委托，只是限定了使用范围。提到这个的用意是区分一下 AS 的 event ， AS 的 event 不是 UE 里的事件委托。

3、小结

动态单播委托、动态多播委托，两个才是主要给蓝图使用。其中动态单播委托最自由，因为它可以写在函数签名的各个部分，正因为如下，它最适合作为 UE 里其他普通委托转换为蓝图或 AS 可用的中间体。

# 整体思路

先提一下 AS 里的委托的简要信息，这些内容在 UE-Angelscipt 的官方文档有提及用法。

AS 里的 Delegates 等价于 Cpp 的动态委托`DECLARE_DYNAMIC_DELEGATE()`。AS 里的 Events 等价于 Cpp 的动态多播委托 `DECLARE_DYNAMIC_MULTICAST_DELEGATE()` 。

上文提到，想要实现 UE 的普通委托转换为 AS 可用的委托，可以通过将动态单播委托作为中间体，这个动态单播委托就对应于 AS 里的 Delegates。

记下来说下如何绑定任意普通单播、普通多播委托为动态单播委托。这里用到了一个关键的写法，调用普通单播、普通多播委托的 Lambda 函数可以实现核心的转换操作。

以下这段代码是将普通单播转为动态委托。代码来源于 Lyra 示例项目。

```cpp
UFUNCTION(ScriptCallable)
static FUIExtensionPointHandle K2_RegisterExtensionPointForContext(UUIExtensionSubsystem* UIExtensionSubsystem, const FGameplayTag& ExtensionPointTag, UObject* ContextObject, EUIExtensionPointMatch ExtensionPointTagMatchType, const TArray<UClass*>& AllowedDataClasses, FExtendExtensionPointDynamicDelegate ExtensionCallback)
{
    return UIExtensionSubsystem->RegisterExtensionPointForContext(ExtensionPointTag,ContextObject, ExtensionPointTagMatchType, AllowedDataClasses, FExtendExtensionPointDelegate::CreateWeakLambda(ExtensionCallback.GetUObject(), [this, ExtensionCallback](EUIExtensionAction Action, const FUIExtensionRequest& Request) {
    ExtensionCallback.ExecuteIfBound(Action, Request);
    }));
};
```

那么如何将多播委托转换为动态委托？这里就不贴代码了，因为以下的示例主要讲的就是这个内容。

这里的示例是将多播委托转换为动态委托，委托因为更简单，就不赘述了，如果需要实现，可以将这个示例简化一下，使用前文提到的写法来变更即可。

示例开始前，再次强调一下。下文的包装是一种通用解法，为了实现绑定委托的自由而生，为了这个自由，会增加复杂度，不过在之后，又用宏来简化了写法，这样一来，这种包装才又了更大的意义。

强调！如果只是为了包装某些委托，掌握委托转为动态委托的写法即可。

# 包装委托的示例

包装委托的示例从这里开始。

想调用的函数如下

```cpp
/** Returns TargetDataSet delegate for a given Ability/PredictionKey pair */
FAbilityTargetDataSetDelegate& AbilityTargetDataSetDelegate(FGameplayAbilitySpecHandle AbilityHandle, FPredictionKey AbilityOriginalPredictionKey);
```

FGameplayAbilitySpecHandle 已经声明为 BlueprintType ,可以识别了，但是 FPredictionKey 需要绑定，这个问题不大，可以比较容易做到。

接着是 FAbilityTargetDataSetDelegate，查看声明，是一个多播委托，不能被蓝图识别。这个比较麻烦一些了。

```cpp
/** Generic callback for returning when target data is available */
DECLARE_MULTICAST_DELEGATE_TwoParams(FAbilityTargetDataSetDelegate, const FGameplayAbilityTargetDataHandle&, FGameplayTag);
```

## 包装

首先，在一个 .h 文件里创造一个类似的动态委托，一个包装用的 UStruct。
接着将这个 UStruct 设计为包含一个多播委托（不能被蓝图识别）的指针。

这个包装用的 UStruct 基本实现了原来的多播委托该有的功能，主要是将多播委托的功能都暴露出来了，唯一不同的是，加入了 AddDynamicDelegate 的函数，让其可以轻松绑定我们新创建的动态委托。

```cpp
/** Generic callback for returning when target data is available */
DECLARE_DYNAMIC_DELEGATE_TwoParams(FAbilityTargetDataSetDelegate_Dynamic, const FGameplayAbilityTargetDataHandle&, InHandle, FGameplayTag, InTag);

struct FAbilityTargetDataSetDelegateWrapper
{
    FAbilityTargetDataSetDelegateWrapper():OriginalEventPtr(nullptr) {}
    FAbilityTargetDataSetDelegateWrapper(FAbilityTargetDataSetDelegate& OriginalEvent)
       : OriginalEventPtr(&OriginalEvent)
    {
    };
    FAbilityTargetDataSetDelegate* OriginalEventPtr;

    // Bind a UObject's Dynamic delegate to OriginalEvent
    FDelegateHandle AddDynamicDelegate(const FAbilityTargetDataSetDelegate_Dynamic& InDynamicDelegate) const
    {
       // Don't allow to have the same delegate!
       if (!OriginalEventPtr || !InDynamicDelegate.IsBound() || !InDynamicDelegate.GetUObject()) return FDelegateHandle();

        FDelegateHandle DelegateHandle = OriginalEventPtr->AddWeakLambda(InDynamicDelegate.GetUObject(), [InDynamicDelegate](const FGameplayAbilityTargetDataHandle&  InHandle, FGameplayTag InTag)
       {
          // ReSharper disable once CppExpressionWithoutSideEffects
          InDynamicDelegate.ExecuteIfBound(InHandle, InTag);
       });

       return DelegateHandle;
    }

    // Broadcasts this delegate to all bound objects, except to those that may have expired.
    // The constness of this method is a lie, but it allows for broadcasting from const functions.    void Broadcast(const FGameplayAbilityTargetDataHandle&  InHandle, FGameplayTag InTag) const
    {
       if (!OriginalEventPtr) return;
       OriginalEventPtr->Broadcast(InHandle, InTag);
    }

    // Removes all functions from this delegate's invocation list.
    void Clear() const
{
       if (!OriginalEventPtr) return;
       OriginalEventPtr->Clear();
    }

    // Removes all functions from this multi-cast delegate's invocation list that are bound to the specified UserObject. Note that the order of the delegates may not be preserved!
    void RemoveAll(const UObject& InObject) const
    {
       if (!OriginalEventPtr) return;
       OriginalEventPtr->RemoveAll(&InObject);
    }

    // Removes a delegate instance from this multi-cast delegate's invocation list (performance is O(N)).
    // Note that the order of the delegate instances may not be preserved    void Remove(const FDelegateHandle& InDelegateHandle) const
    {
       if (!OriginalEventPtr) return;
       OriginalEventPtr->Remove(InDelegateHandle);
    }

    // Checks to see if any functions are bound to this multi-cast delegate.
    bool IsBound() const
    {
       if (!OriginalEventPtr) return false;
       return OriginalEventPtr->IsBound();
    }

    // Checks to see if any functions are bound to the given user object.
    bool IsBoundToObject(const UObject& InObject) const
    {
       if (!OriginalEventPtr) return false;
       return OriginalEventPtr->IsBoundToObject(&InObject);
    }
};
```

## 绑定

为了让这个类的函数能被使用，需要绑定到 AS

```cpp
AS_FORCE_LINK FAngelscriptBinds::FBind Bind_FAbilityTargetDataSetDelegateWrapper(
    static_cast<int32>(FAngelscriptBinds::EOrder::Late) + 2000, []
    {
       FAngelscriptBinds ThisBind = FAngelscriptBinds::ValueClass<FAbilityTargetDataSetDelegateWrapper>(
          "FAbilityTargetDataSetDelegateWrapper",FBindFlags());

       ThisBind.Constructor("void f()" , [](FAbilityTargetDataSetDelegateWrapper* Address)
       {
          new(Address) FAbilityTargetDataSetDelegateWrapper();
       });
       FAngelscriptBinds::SetPreviousBindNoDiscard(true);
       SCRIPT_TRIVIAL_NATIVE_CONSTRUCTOR(ThisBind, "FAbilityTargetDataSetDelegateWrapper");

       ThisBind.Method("FDelegateHandle AddDynamicDelegate(const FAbilityTargetDataSetDelegate_Dynamic& InDynamicDelegate) const",METHODPR_TRIVIAL(FDelegateHandle, FAbilityTargetDataSetDelegateWrapper,AddDynamicDelegate, (const FAbilityTargetDataSetDelegate_Dynamic& InDynamicDelegate)));
       SCRIPT_BIND_DOCUMENTATION("Bind a UObject's Dynamic delegate to OriginalEvent")

       ThisBind.Method("void Broadcast(const FGameplayAbilityTargetDataHandle&  InHandle, FGameplayTag InTag) const)",METHODPR_TRIVIAL(void, FAbilityTargetDataSetDelegateWrapper,Broadcast, (const FGameplayAbilityTargetDataHandle&  InHandle, FGameplayTag InTag)));
       SCRIPT_BIND_DOCUMENTATION("Broadcasts this delegate to all bound objects, except to those that may have expired.\n"
          "The constness of this method is a lie, but it allows for broadcasting from const functions.")

       ThisBind.Method("void Clear() const ",METHODPR_TRIVIAL(void, FAbilityTargetDataSetDelegateWrapper, Clear, ()));
       SCRIPT_BIND_DOCUMENTATION("Removes all functions from this delegate's invocation list.")

       ThisBind.Method("void RemoveAll(const UObject& InObject) const",METHODPR_TRIVIAL(void, FAbilityTargetDataSetDelegateWrapper,RemoveAll, (const UObject& InObject)));
       SCRIPT_BIND_DOCUMENTATION("Removes all functions from this multi-cast delegate's invocation list that are bound to the specified UserObject. Note that the order of the delegates may not be preserved!")

       ThisBind.Method("void Remove(const FDelegateHandle& InDelegateHandle) const",METHODPR_TRIVIAL(void, FAbilityTargetDataSetDelegateWrapper,Remove, (const FDelegateHandle& InDelegateHandle)));
       SCRIPT_BIND_DOCUMENTATION(" Removes a delegate instance from this multi-cast delegate's invocation list (performance is O(N)). Note that the order of the delegate instances may not be preserved")

       ThisBind.Method("bool IsBound() const",METHODPR_TRIVIAL(bool, FAbilityTargetDataSetDelegateWrapper,IsBound, ( )));
       SCRIPT_BIND_DOCUMENTATION("Checks to see if any functions are bound to this multi-cast delegate.")

       ThisBind.Method("bool IsBoundToObject(const UObject& InObject) const",METHODPR_TRIVIAL(bool, FAbilityTargetDataSetDelegateWrapper,IsBoundToObject, (const UObject& InObject)));
       SCRIPT_BIND_DOCUMENTATION("Checks to see if any functions are bound to the given user object.")

       ThisBind.Method("FAbilityTargetDataSetDelegateWrapper& opAssign(const FAbilityTargetDataSetDelegateWrapper& Other)",[](FAbilityTargetDataSetDelegateWrapper* Address,const FAbilityTargetDataSetDelegateWrapper& Other) -> FAbilityTargetDataSetDelegateWrapper*
       {
          *Address = Other;
          return  Address;
       });
       SCRIPT_TRIVIAL_NATIVE_ASSIGNMENT(ThisBind, "FAbilityTargetDataSetDelegateWrapper");

    });
```

原始的那个想要调用的函数，此时可以绑定为

```cpp
    ThisBind.Method(
"FAbilityTargetDataSetDelegateWrapper AbilityTargetDataSetDelegate(const FGameplayAbilitySpecHandle AbilityHandle, const FPredictionKey AbilityOriginalPredictionKey)",
    [](UAbilitySystemComponent* This, const FGameplayAbilitySpecHandle AbilityHandle, const FPredictionKey AbilityOriginalPredictionKey) -> FAbilityTargetDataSetDelegateWrapper
    {
       return  FAbilityTargetDataSetDelegateWrapper{This->AbilityTargetDataSetDelegate(AbilityHandle, AbilityOriginalPredictionKey)};
    });
```

## AS 里使用

AS 里使用方式如下。

```cpp

FDelegateHandle OnTargetDataReadyCallbackDelegateHandle;

FAbilityTargetDataSetDelegateWrapper DelegateWrapper;

FAbilityTargetDataSetDelegate_Dynamic InDynamicDelegate;
InDynamicDelegate.BindUFunction(this, n"OnTargetDataReadyCallback");

DelegateWrapper = ASC.AbilityTargetDataSetDelegate(GetCurrentAbilitySpecHandle(), GetCurrentActivationInfo().GetActivationPredictionKey());

OnTargetDataReadyCallbackDelegateHandle = DelegateWrapper.AddDynamicDelegate(InDynamicDelegate);
```

# 高阶操作——使用宏包装与绑定，参照声明动态委托的方式

这个操作是为了将上文的包装简化写法，我们不可能每遇到一个委托就手工写一个上方的函数。于是，参照 UE 实现委托声明的宏写法，我们其实可以经过巧妙地设计宏，从而实现一行代码就搞定这种委托绑定的声明。

宏的写法相当复杂，为了实现这个，需要写大量的代码（因为要实现多个参数），不过好在于，写一次终身受益，经过一番努力，最终实现了一行代码就声明了前文我们对委托的包装。

以下内容只是实现之后的写法，可供参考。

我们写好的专用宏，放在一个专门的文件里，比如叫做 DelegateWrapper.h , 哪里需要就 include 它。

#### 声明一个动态委托，必须写在 UE 反射系统识别的头文件里

注意，必须在有 "XXXX.generated.h" 的头文件里声明，让反射系统识别到。(.generated.h 的头文件需要有 UStruct 或者 UClass，这个文件才会被反射系统真正识别。)
声明的这个动态委托，命名必须是对应的原始委托 + `_Dynamic`

```cpp
///////////////////////////////////////////////////////////////
/// DECLARE_DYNAMIC_DELEGATE HERE, add suffix: _Dynamic
/// DECLARE_DYNAMIC_DELEGATE Must be Set before all Wrapper
///////////////////////////////////////////////////////////////

// Test only
DECLARE_DYNAMIC_DELEGATE_TwoParams(FDssTestDelegate_Dynamic, int, InInt,  float, InFloat);

// FSimpleDelegate
DECLARE_DYNAMIC_DELEGATE(FSimpleDelegate_Dynamic);

// FSimpleMulticastDelegate
DECLARE_DYNAMIC_DELEGATE(FSimpleMulticastDelegate_Dynamic);

// FAbilityTargetDataSetDelegate
DECLARE_DYNAMIC_DELEGATE_TwoParams(FAbilityTargetDataSetDelegate_Dynamic, const FGameplayAbilityTargetDataHandle&, InHandle, FGameplayTag, InTag);
```

注意，UE 的这个宏需要有分号！另外，必须放在除了 # include 之外的所有内容的前面。

#### 声明一个动态委托的包装类型

宏定义说明，类似于 delegate 的写法。
普通的单播委托用 `DELEGATE_WRAPPER`， 多播委托就用 `MULTICAST_DELEGATE_WRAPPER` ，可以附加 0-6 个参数，不设置返回值（实在需要返回值，传入可修改变量也是一样的）。

```cpp
DELEGATE_WRAPPER_TwoParams(DelegateName, Param1Type, Param1Name, Param2Type, Param2Name)
```

```cpp
///////////////////////////////////////////////////////////////
/// all Wrapper HERE ///////////////////////////////////////////////////////////////

// Test only
DELEGATE_WRAPPER_TwoParams(FDssTestDelegate, int, InInt,  float, InFloat)

// FSimpleDelegate
DELEGATE_WRAPPER(FSimpleDelegate)

// FSimpleMulticastDelegate
MULTICAST_DELEGATE_WRAPPER(FSimpleMulticastDelegate)

// FAbilityTargetDataSetDelegate
MULTICAST_DELEGATE_WRAPPER_TwoParams(FAbilityTargetDataSetDelegate, const FGameplayAbilityTargetDataHandle&, InHandle, FGameplayTag, InTag)
```

这包装类型是原生的 cpp 类，基本实现了委托应有的绑定与解绑等功能。唯一和正常绑定到蓝图的委托不同的是，绑定函数是通过绑定一个对应的`_Dynamic` 委托来实现的。

不用 UE 的类是因为，UE 的类包含有反射用的宏，这些宏不能被其他宏包含，这就使得不能实现一个宏声明这个类型了。另外一个原因是，就算声明为 UStruct，也还是有一些类型是反射系统不识别的，最终还是需要手工绑定。

### 在适当的位置绑定包装类型，一般是绑定用的 cpp 文件

宏定义说明，类似于 delegate 的写法，但是增加了绑定类型，附加在最后，按顺序来写。

```cpp
MULTICAST_DELEGATE_WRAPPER_BIND_TwoParams(DelegateName, Param1Type, Param1Name, Param2Type, Param2Name, Param1Type_Bind, Param2Type_Bind)
```

这个绑定用的文件注意不能被其他文件 include 。
设计绑定宏时，末尾增加绑定的字串识别，这是为了应对绑定名与原类型名称不一致的情况，比如最典型的就是 float, cpp 的 float 需要绑定为 float32 。

```cpp
///////////////////////////////////////////////////////////////
/// all Wrapper BIND here, don't include this file by other file
///////////////////////////////////////////////////////////////
 // Test only
DELEGATE_WRAPPER_BIND_TwoParams(FDssTestDelegate, int, InInt,  float, InFloat, int, float32);

// FSimpleDelegate DELEGATE_WRAPPER_BIND(FSimpleDelegate);

// FSimpleMulticastDelegate
MULTICAST_DELEGATE_WRAPPER_BIND(FSimpleMulticastDelegate)

// FAbilityTargetDataSetDelegate
MULTICAST_DELEGATE_WRAPPER_BIND_TwoParams(FAbilityTargetDataSetDelegate, const FGameplayAbilityTargetDataHandle&, InHandle, FGameplayTag, InTag, const FGameplayAbilityTargetDataHandle&, FGameplayTag)
```

这个自定义的宏，无需在末尾加分号，当然加了也没问题。

这个宏会在 `static_cast<int32>(FAngelscriptBinds::EOrder::Early) - 100` 的时机绑定类型本身，然后在 `static_cast<int32>(FAngelscriptBinds::EOrder::Late) + 10000` 的时机绑定各种函数。这基本确保了其他类型的绑定可以随意调用这些包装类型，包装类型的函数在绑定的时候，其余的类型也基本绑定完成（其实因为动态单播的声明原因，可以杜绝蓝图不识别的参数了，所以唯一剩下的就是 FDelegateHandle 这个宏里本来就包含的类型了，这个类型只要确保在 Late + 10000 之前绑定了就好。)

这就涉及到绑定的逻辑了，所有原生类型的绑定最好包含两部分，一个部分是类型自身的绑定，然后接着是其余内容。类型自身的绑定最好放到 Early, 其余内容视情况放在 Normal 或者 Late 。因为 AS 自身的很多绑定会放在 Normal，所以其余内容建议放在 Late , 这样更置后，可以确保更多的内容绑定好了，而且可以确保不会覆盖 AS 已经有的绑定（如果同名的话）。

# 总结

想让 AS 访问更多的引擎代码，除了付出一点性能损失（委托从普通变为动态开销多一点），还需要付出一些精力将代码封装。委托的绑定，大概是除了模板函数之外最麻烦的绑定了。

本文实现了委托绑定的自由，代价是需要写一次复杂的包装。你看，复杂度只会转移，不会消失。本文的整体实现方案将复杂度封装在了宏里，一次实现，多次受用。调用越多，时间成本摊销之后，就回本了。如果需要大量地绑定委托，或者只是为了自由，此方案是一个方向。

当然，也许读者有更优雅的方式，望不吝赐教。
