---
title: "UE_Angelscript — Pitfalls: you never know until you step in one"
order: 57
category: binding
---
# UE_Angelscript — Pitfalls: you never know until you step in one

I will list these one by one without necessarily categorizing everything. Treat them as little tips for avoiding traps.

Some also appear elsewhere in the binding series. Repeating them here is a way of underlining the important bits.

## Do not trust UStruct inheritance: AS only recognizes the current UStruct

Under AS binding rules, a UStruct without BlueprintType or its own Blueprint-exposed content — inherited content does not count — does not enter the binding list.

You can therefore have a UStruct that works perfectly in Blueprints because its parent is exposed, yet AS has never heard of it!

For example:

```cpp
struct FAnimUpdateContext : public FAnimExecutionContext
```

## Do not trust UStruct inheritance: adding bindings means handling all its descendants

If a UStruct has many descendants, adding bindings to the grandparent, manually or through a Mixin, only affects that particular UStruct.

In a sentence: UStruct inheritance may as well not exist in AS. Yes, AS structs cannot inherit or even contain functions. Use the mighty Mixin if you insist on adding functions.

## BlueprintInternalUseOnly metadata makes AS ignore it

meta = (BlueprintInternalUseOnly = "true")
With that marker, AS cannot access the function.

```cpp
// this function cannot be accessed from AS
    UFUNCTION(BlueprintCallable, meta = (BlueprintInternalUseOnly = "true"))
    void TestBlueprintInternalUseOnly()
    {
       UE_LOG(LogTemp,Warning,TEXT("Test BlueprintInternalUseOnly UFUNCTION Show"));
    }
};
```

This originally limits Blueprint usage. AS inherits much of Blueprint’s available content, so it inherits this restriction too, but lacks Blueprint features such as recognizing the intended usage scope. The function effectively becomes unavailable.

A reasonable solution is a Mixin or another Blueprint function library, particularly for static functions.

Another option is removing BlueprintInternalUseOnly by one method or another.

The last option is editing the AS plugin’s Bind_BlueprintCallable code to allow it. Comment out the restriction for a global opt-in, or add conditions to allow only some functions.

If the UClass is MinimalAPI and the desired UFUNCTION is BlueprintInternalUseOnly, your Mixin normally lives in another module and cannot call it through cpp. What then? Bring out reflection: find and invoke the member by its known function name.

The detailed solution, with code, is here:
[UE_Angelscript — A better way to handle BlueprintInternalUseOnly functions](binding-blueprint-internal-use-only.md)

## AS binds the original function name, not its Display name

Prefixes and suffixes are trimmed according to naming rules.
That can make the Blueprint display name differ from the AS name.

For example, Blueprint’s Multi Line Trace By Channel is originally LineTraceMulti, while Line Trace By Channel is LineTraceSingle.

When following a Blueprint function by name gets you nowhere, jump into cpp and check its real function name.

## AS TMap keys reject some bound native structs

For example, FObjectKey still cannot be a TMap key after binding. It produces this error:

```cpp
Attempting to instantiate invalid template type 'TMap<FObjectKey,FGameplayAbilitySpecHandle>': Containers cannot be nested in other containersas
```

I do not know whether this is because it has no public members.

One solution is an FObjectKeyWrapper with GetTypeHash and a set of comparison operators.

Update: a better binding approach associates the class with a type derived from TAngelscriptCppType during manual binding. See below. It works for TMap, TArray and TSet.

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

## Do not lose const on the this pointer in a Mixin

Const does not disappear by itself. If the original this pointer is const, the Mixin static function’s first parameter must be const too.

For example:

```cpp
//  the original function of FGameplayAttribute that is to be bound
float GetNumericValueChecked(const UAttributeSet* Src) const;

// this is a Mixin function of FGameplayAttribute
UFUNCTION(BlueprintCallable)
static float BP_GetNumericValueChecked(const FGameplayAttribute& GameplayAttribute, const UAttributeSet* Src)
{
    return GameplayAttribute.GetNumericValueChecked(Src);
};

// after binding, AS shows this function as
float32 FGameplayAttribute.GetNumericValueChecked(const UAttributeSet Src) const

// Summary: the const on the const FGameplayAttribute& GameplayAttribute parameter of the Mixin function becomes the const at the end of the function signature in AS, meaning it does not modify the class members. The final form is basically the same as the original function.
```

## Try not to mix cpp and AS with UGameplayMessageSubsystem

UGameplayMessageSubsystem is a useful decoupling Subsystem, rather like a central broadcaster. It sends different UStructs. See the related article in this series, UE_Angelscript: GameplayMessageSubsystem and GameplayTags.

Passing all those different UStructs can cause problems.

In other words, avoid having the sender in cpp and the receiver in AS, or vice versa, or errors may occur.

## Animation bindings are troublesome when async execution is involved

Lyra, for example, uses async execution. Those calls are convenient in Blueprints but not yet bound in AS — or perhaps I have not figured them out.

## Use Delay carefully, especially the automatically bound version in AS

Similar Delay code in cpp and AS sometimes waits longer in AS.

My guess is that Delay blocks execution, and that blocking somehow interacts with the script VM.

Whatever the reason, use Timer where possible.

## Want template functions? Why not specialize the few you need?

AS does not support templates itself. Template-like forms receive special handling. For convenient cpp template functions, consider specializing a few and exposing them through Mixins or a Blueprint function library.

AS is a lightweight script. You do not need to move everything into it.

---
