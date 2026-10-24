---
title: "UE_Angelscript — Tricks 2: sometimes one sentence clears up a head-scratcher"
order: 16
category: tips
---
# UE_Angelscript — Tricks 2: sometimes one sentence clears up a head-scratcher

These are problems you may run into with UE-AS. When you hit one, you can spend ages searching for an answer.

Yet each can be solved with one sentence.

# What if WorldContext is hidden and cannot be supplied?

The one-sentence solution: add FAngelscriptGameThreadScopeWorldContext(GetWorld()) in the current scope before calling the function.

Blueprints can expose a WorldContext pin. Code has no pins.

The obvious approach is binding a function with an explicit WorldContext parameter. But there are many such functions. Can AS code define its own world context directly?

Yes. Code has scopes rather than pins. Add FAngelscriptGameThreadScopeWorldContext() inside the same braces, and subsequent WorldContext use is replaced with your chosen value until that scope ends.

```cpp
class UGCN_Test : UGameplayCueNotify_Burst
{
	UFUNCTION(BlueprintOverride)
	void OnBurst(AActor Target, FGameplayCueParameters Parameters,
				 FGameplayCueNotify_SpawnResult SpawnResults) const
	{
		// Create a temp WorldContextObject
		auto _World = FAngelscriptGameThreadScopeWorldContext(GetWorld());

		Gameplay::GetPlayerPawn(0);

		Warning(f"Test: {this.GetName()}");
	}
}
```

# How should a non-UObject type express an empty value?

The one-sentence solution: use TOptional<>.

UE-AS has several ways to express emptiness:

1. Pointers or pointer-like objects.

Only UObjects can use this. AS has no pointer concept and cannot null-check UStructs or native primitives such as int and float.

2. Default values or globals.

A special value can mean empty, but brings other problems and suits simple cases. If -1 means empty, it cannot also mean the ordinary number -1. When you really need -1, choose something else. Enough of this becomes confusing.

Someone might say UE has many globals representing empty values. True, but that is inertia from older code, a workaround of its time. New code has better choices.

3. A validity function on the Struct.

Some bound cpp UStructs have IsValid or IsNull, but they are a minority. This also uses memory: you have actually created an object, with its full size.

4. TOptional<>

UE’s TOptional<> solves the empty-value problem when pointers are unavailable. The AS plugin binds and optimizes it, making it pleasant to use.

A small digression: TOptional<> is like the C++ standard’s std::optional. UE implements its own versions of many useful standard-library tools, including smart pointers, for control and integration. Other languages have similar tools: Rust’s Option<> works much like this C++ type.

When you need “none” or “empty” without pointers, TOptional<> is a good choice.

Example:

```cpp
TOptional<float> OptionalValue;
OptionalValue = 3.14;

if (OptionalValue.IsSet())
{
    Print(f"Value is: {OptionalValue.GetValue()}");
}
```

# I changed that variable. Why did nothing happen?

One sentence: Struct references and copies were not clearly distinguished.

This comes from overlooking or not fully understanding C++ behavior.

Remember: AS objects are copied by default, except when passed as function parameters. This matches C++, with one exception: **AS function parameters are read-only by default**, rather than defaulting to copies.

When you do not need to change the original, a copy and reference produce the same result. References usually perform better, especially for large objects.
But when you need to change the original and mistakenly use a copy, you are changing the original object! That leads to baffling behavior: I clearly changed it, so why did nothing change?
It often happens while retrieving a value from TArray<>, for example:

```cpp
TArray<AActor> MyActors = GetActors(); // some functions to get Actors
auto Actor = MyActors[0]; // I am sure MyActors is not empty!
Actor.DoSomethingToModifyItself();
```

Here, DoSomethingToModifyItself() changes a copy and does not affect the original Actor.
Receive the variable this way instead:

```cpp
auto& Actor = MyActors[0];
```

Now Actor really refers to the original first element.

Could we just use references everywhere? It depends.

For UObjects, copying and referencing have almost the same cost. Large UStructs incur copy costs, but AS structs are recommended as simple data containers rather than large objects. Also, sometimes we want parameters isolated from changes to the original, so copying is useful.

A C++ best practice is to add `const` whenever the object need not change. Combine that with this rule: when modifying the original indirectly, use a reference. We get:

Two dimensions to consider when receiving an object in a new variable:

- No modification + no separate copy: const auto&
- No modification + separate copy: const auto
- Modify original + no copy: auto&
- Modify a separate copy: auto

Replace auto with a concrete type such as AActor if desired.

Now for the exception.
The official documentation explains it, but it is easy to forget until you try it. AS function parameters are read-only by default. To modify a Struct, add `&` after its type. Why? First, less typing: no `const &` on every parameter. Second, performance. Default copies in frequently called functions can accumulate substantial cost, which is difficult to spot because the result remains correct.

```cpp
// Change the parameter struct so its number is randomized between 0.0 and 1.0
UFUNCTION()
void RandomizeNumberInStruct(FExampleStruct& Struct)
{
    Struct.ExampleNumber = Math::RandRange(0.0, 1.0);
}
```

I find this exception convenient. It affects UStructs and primitives such as int and float most. UObjects involve pointers. Usually we call their members rather than replace the pointer itself. We may assign nullptr, but replacing it with a different instance is less common. Distinguish changing the UObject pointer from changing its target: the parameter restriction only limits changes to the pointer.

A UObject is really a Handle, `UObject@`, rather than the object itself. It resembles a simplified C++ pointer. A UStruct is a value, the object itself. Both use dot access, and UE-AS deliberately removes the `@` marker for convenient syntax. That makes them harder to distinguish. They look the same but are very, very different!

For a simple model, treat AS UStructs like int and float: they represent their own values. In AS code, only UObject is not the object itself.

# Do arithmetic operators also care about operand order?

One sentence: AS binary operators can be understood as member functions, and putting the type on the left or right invokes different functions.

C++ gives programmers a lot of freedom; many binary operations are designed to work in either order.
In AS, incomplete binding for some types means reversing operands fails. FVector * 5.0 may work while 5.0 * FVector does not.

Here is the AS plugin’s FVector multiplication binding with float64. It supports only FVector * 5.0:

```cpp
FVector_.Method("FVector opMul(float64 Scale) const", METHODPR_TRIVIAL(FVector, FVector, operator*, (double) const));
```

How can we support 5.0 * FVector too?

Cpp declares a global function that the compiler recognizes:

```cpp
template<typename T, typename T2 UE_REQUIRES(std::is_arithmetic_v<T2>)>
FORCEINLINE TVector<T> operator*(T2 Scale, const TVector<T>& V)
{
    return V.operator*(Scale);
}
```

AS does not bind that global function in the C++ way. Instead, its convenient opMul_r form means the current type is on the operator’s right.

So add a member binding for FVector’s right-hand operation:

```cpp
AS_FORCE_LINK FAngelscriptBinds::FBind Bind_FVector(static_cast<int32>(FAngelscriptBinds::EOrder::Late) + 1000,[]
{
    FAngelscriptBinds ThisBind = FAngelscriptBinds::ExistingClass("FVector");


     ThisBind.Method("FVector opMul_r(const float64 Scale)", [](const FVector& V, const double Scale) -> FVector
     {
       return V * Scale;
     });
});
```

Because int and float32 implicitly convert to float, supporting float64 also supports those types.

Now 5 * FVector works happily.

Why was this not a default FVector binding? My guess is the mental model: an operator is a function, the left operand is the class, and the right operand is its argument. That is intuitive for designers.

Even so, I added opMul_r because I prefer consistency with C++.

# Why can default crash, and how do I write C++-constructor-like code?

One sentence: default cannot dynamically create anything — including NewObject or Event binding. It is only for configuring property values.

Think of default as a reduced C++ constructor, without UObject creation through the familiar CreateDefaultSubobject<>.

For AActors, use UPROPERTY(DefaultComponent) instead of CreateDefaultSubobject. Use OverrideComponent to replace one. AS makes this more comfortable. Configure DefaultComponent member values with default statements.

Together, default and DefaultComponent cover most common AActor-family constructor work.

One limitation, or something AS has not implemented, is that C++ CreateDefaultSubobject can create any UObject, not only UActorComponents. If an AActor really needs arbitrary UObjects created during construction, put that in void ConstructionScript(). It runs whenever an instance is created.

# A quick wrap-up

This article covers WorldContext, empty values, copies and references, operator binding and default statements. One sentence can make each problem click. Without it, there are more complicated solutions too — a fair description of these tricks of the trade.

---
