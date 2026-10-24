---
title: "UE_Angelscript — Call delegates freely: it looks unreal, but it is in your hands"
order: 53
category: binding
---
# UE_Angelscript — Call delegates freely: it looks unreal, but it is in your hands

**For binding to AS, the idea here can be developed into something better and simpler. With a deeper understanding of corresponding Cpp and AS memory layouts, Cpp delegates can map directly into AS. Apart from not being usable in UPROPERTY, they can behave like ordinary types without much downside.**

**Even so, this article’s overall approach remains useful: the better method grew out of it.**

Warning: there is a lot of cpp code here to explain an overall design. The full solution is too large to list every implementation, particularly the cpp macros.

Warning: do not fixate on every line; follow the idea. This needs substantial AS-binding knowledge, so read the other binding articles first.
# Preface

UE delegates are a useful callback mechanism. Consult the official documentation for full details.

We can distinguish delegates along two dimensions.

1. UE has ordinary delegates and dynamic delegates.

Ordinary delegates are simple, efficient and low-overhead, for cpp only. Dynamic delegates work with Blueprints at a slightly higher cost.

2. Delegates are also single-cast or multicast.

Single-cast holds one callback; multicast holds several. Single-cast can return a value; multicast cannot, though reference parameters can achieve a similar effect.

UE events are delegates too, with restricted access. I mention this to distinguish them from AS events: AS event is not UE’s event delegate.

3. A quick wrap-up

Dynamic single-cast and dynamic multicast are the two main Blueprint forms. Dynamic single-cast is the most flexible because it fits throughout a function signature. That makes it the best intermediary for converting ordinary UE delegates into Blueprint- or AS-usable forms.

# The overall idea

First, a little about AS delegates, whose usage is described in the official UE-Angelscipt documentation.

AS Delegates correspond to Cpp dynamic delegates, `DECLARE_DYNAMIC_DELEGATE()`. AS Events correspond to dynamic multicast delegates, `DECLARE_DYNAMIC_MULTICAST_DELEGATE()`.

As mentioned, a dynamic single-cast delegate can bridge ordinary UE delegates into AS. That intermediary corresponds to an AS Delegate.

Next, how do we convert arbitrary ordinary single-cast and multicast delegates into dynamic single-cast delegates? The key is their lambda-binding functions, which perform the conversion.

This code converts an ordinary single-cast delegate to a dynamic delegate. It comes from Lyra:

```cpp
UFUNCTION(ScriptCallable)
static FUIExtensionPointHandle K2_RegisterExtensionPointForContext(UUIExtensionSubsystem* UIExtensionSubsystem, const FGameplayTag& ExtensionPointTag, UObject* ContextObject, EUIExtensionPointMatch ExtensionPointTagMatchType, const TArray<UClass*>& AllowedDataClasses, FExtendExtensionPointDynamicDelegate ExtensionCallback)
{
    return UIExtensionSubsystem->RegisterExtensionPointForContext(ExtensionPointTag,ContextObject, ExtensionPointTagMatchType, AllowedDataClasses, FExtendExtensionPointDelegate::CreateWeakLambda(ExtensionCallback.GetUObject(), [this, ExtensionCallback](EUIExtensionAction Action, const FUIExtensionRequest& Request) {
    ExtensionCallback.ExecuteIfBound(Action, Request);
    }));
};
```

What about multicast? I will not show it separately here because that is what the example below covers.

The example converts multicast to dynamic delegates. Single-cast is simpler; simplify the example and use the approach above if needed.

Before starting, one more emphasis: this wrapper is a general solution created for freedom in delegate binding. That freedom adds complexity. Macros later simplify the syntax, making the wrapper more worthwhile.

If you only need a few delegate wrappers, learning the ordinary-to-dynamic conversion is enough.

# A delegate-wrapping example

The example starts here.

This is the function we want:

```cpp
/** Returns TargetDataSet delegate for a given Ability/PredictionKey pair */
FAbilityTargetDataSetDelegate& AbilityTargetDataSetDelegate(FGameplayAbilitySpecHandle AbilityHandle, FPredictionKey AbilityOriginalPredictionKey);
```

FGameplayAbilitySpecHandle is already BlueprintType and recognized. FPredictionKey needs binding, which is relatively easy.

FAbilityTargetDataSetDelegate is a multicast delegate, not recognizable by Blueprints. That is more troublesome.

```cpp
/** Generic callback for returning when target data is available */
DECLARE_MULTICAST_DELEGATE_TwoParams(FAbilityTargetDataSetDelegate, const FGameplayAbilityTargetDataHandle&, FGameplayTag);
```

## Wrap it

In a .h file, first create a corresponding dynamic delegate and a wrapper UStruct.
Give that UStruct a pointer to the multicast delegate Blueprints cannot recognize.

The wrapper implements essentially the original multicast delegate’s operations, mainly exposing them. The one difference is AddDynamicDelegate, which conveniently binds our new dynamic delegate.

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

## Bind it

Bind the class to AS so its functions can be used:

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

The original desired function can now bind as:

```cpp
    ThisBind.Method(
"FAbilityTargetDataSetDelegateWrapper AbilityTargetDataSetDelegate(const FGameplayAbilitySpecHandle AbilityHandle, const FPredictionKey AbilityOriginalPredictionKey)",
    [](UAbilitySystemComponent* This, const FGameplayAbilitySpecHandle AbilityHandle, const FPredictionKey AbilityOriginalPredictionKey) -> FAbilityTargetDataSetDelegateWrapper
    {
       return  FAbilityTargetDataSetDelegateWrapper{This->AbilityTargetDataSetDelegate(AbilityHandle, AbilityOriginalPredictionKey)};
    });
```

## Use it in AS

Usage in AS:

```cpp

FDelegateHandle OnTargetDataReadyCallbackDelegateHandle;

FAbilityTargetDataSetDelegateWrapper DelegateWrapper;

FAbilityTargetDataSetDelegate_Dynamic InDynamicDelegate;
InDynamicDelegate.BindUFunction(this, n"OnTargetDataReadyCallback");

DelegateWrapper = ASC.AbilityTargetDataSetDelegate(GetCurrentAbilitySpecHandle(), GetCurrentActivationInfo().GetActivationPredictionKey());

OnTargetDataReadyCallbackDelegateHandle = DelegateWrapper.AddDynamicDelegate(InDynamicDelegate);
```

# Advanced: wrap and bind through macros, like dynamic-delegate declarations

This simplifies the wrapper above. We cannot write that entire setup by hand for every delegate. Following UE’s delegate declaration macros, careful macro design can reduce the declaration to one line.

The macros are complicated and take a lot of code to support multiple parameters. The good part is writing them once and benefiting forever. After some effort, one line declares the wrapper above.

The following shows only the syntax after implementation, for reference.

Put the custom macros in a dedicated file such as DelegateWrapper.h and include it where needed.

#### Declare a dynamic delegate in a header recognized by UE reflection

It must be in a header with "XXXX.generated.h" so reflection recognizes it. That header needs a UStruct or UClass to be processed.
The delegate name must be the original delegate name plus `_Dynamic`.

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

UE’s macro needs a semicolon! Also, place it before everything except includes.

#### Declare the dynamic-delegate wrapper type

Macro definitions resemble delegate declarations.
Use `DELEGATE_WRAPPER` for single-cast and `MULTICAST_DELEGATE_WRAPPER` for multicast. Support zero to six arguments without return values; mutable parameters can carry results if needed.

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

This wrapper is a native cpp class implementing the usual binding and unbinding operations. Unlike normal Blueprint delegates, it binds through a corresponding `_Dynamic` delegate.

Why not a UE type? UE types contain reflection macros that cannot be nested inside other macros, preventing a one-macro type declaration. Also, some types remain unknown to reflection even in a UStruct, so manual binding is still needed.

### Bind the wrapper in the appropriate place, normally a binding cpp file

The macro resembles the delegate declaration but adds script type names at the end, in order.

```cpp
MULTICAST_DELEGATE_WRAPPER_BIND_TwoParams(DelegateName, Param1Type, Param1Name, Param2Type, Param2Name, Param1Type_Bind, Param2Type_Bind)
```

Do not include this binding file from other files.
The trailing binding-name strings handle names differing from the native type. The classic case is cpp float, which must bind as float32.

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

The custom macro needs no trailing semicolon, though adding one is harmless.

It binds the type at `static_cast<int32>(FAngelscriptBinds::EOrder::Early) - 100`, then its functions at `static_cast<int32>(FAngelscriptBinds::EOrder::Late) + 10000`. Other type bindings can therefore freely use the wrappers, while most other types are registered before the wrapper methods. Dynamic single-cast declarations already exclude Blueprint-unknown parameters, so the main remaining dependency is FDelegateHandle, included by the macro itself. Just bind it before Late + 10000.

That reflects a broader registration rule: native bindings should have two parts, type declaration followed by everything else. Put declarations at Early and other work at Normal or Late as needed. Since AS binds many things at Normal, Late is a useful default for the rest: more dependencies are ready, and existing AS bindings of the same name are not overwritten.

# Summary

Giving AS more engine access costs some performance — dynamic delegates cost more than ordinary delegates — and effort to wrap the code. Delegate binding is probably the most awkward kind after template functions.

This approach gives freedom in delegate binding at the cost of writing a complicated wrapper once. Complexity moves; it does not disappear. Here it is packaged in macros, implemented once and reused. More calls amortize the work. If you need many delegate bindings, or just want the freedom, this is one direction.

Perhaps you have a more elegant solution. Corrections are welcome.
