---
title: "UE_Angelscript — Tricks of the trade"
order: 15
category: tips
---
# UE_Angelscript — Tricks of the trade

Here are some interesting ways to make writing logic more comfortable. Yes, life goes on without them. These tricks are the icing on the cake.

This article mainly covers fluent null checks and casts, ScriptMethod as an alternative Mixin form, DeterminesOutputType, and changing arbitrary UPROPERTY values through reflection.

# Fluent null checks

AS UObjects have no pointer symbol, but are essentially pointers. We normally null-check a pointer before use. Cpp makes that simple:

```cpp
if (ThisObject*)
```

AS normally uses these two common forms:

```cpp
if (ThisObject != nullptr)

if (IsValid(ThisObject))
```

The second also checks whether the object is marked for garbage collection, preventing access to an object already marked as garbage. It is more widely applicable.

AS is less concise here. Implicit conversion is technically possible, but AS deliberately minimizes it.

How can the check read more smoothly? Use a mixin for chained calls:

```cpp
if (ThisObject.IsValid_())
```

It is simple and needs no C++ code. Add this in an AS file:

```cpp
// Mixin version of IsValid(const UObject Object)
mixin bool IsValid_(const UObject Object)
{
	return IsValid(Object);
}
```

I add an underscore because I do not want to disturb the normal global IsValid() spelling. This mixin is no longer quite like a member function because it accepts nullptr; the suffix distinguishes it.

Chained calls read more smoothly and remove the explicit nullptr comparison, further hiding pointer concepts in AS.

**Addition: IsValid involves GC. If you do not need that check, or want maximum performance, compare directly with nullptr.**

For example — again, the underscore distinguishes a nullptr-accepting mixin from a member-like function:

```cpp
mixin bool IsNull_(UObject Obj)
{
	return Obj==nullptr;
}
```

# Fluent Cast calls

This uses a Mixin too, but a cpp one.

Normally we write Cast just as in C++:

```cpp
auto A = Cast<AActor>(ThisObject);
```

For a fluent style, this would be more comfortable:

```cpp
auto A = ThisObject.CastTo(AActor);
```

UE reflection makes it easy to implement.
Add two UObject Mixin functions using the useful DeterminesOutputType specifier. It infers the return type from reflected type information.

```cpp
// Cast to Typed UObject, if false , return nullptr
UFUNCTION(ScriptCallable,  Meta = (DeterminesOutputType = "TypedClass"))
static UObject* CastTo_(UObject* Object, const TSubclassOf<UObject>& TypedClass)
{
    if (Object->IsA(TypedClass))
       return Object;
    return nullptr;
}

// Cast to Typed UObject, if false , will check false
UFUNCTION(ScriptCallable, Meta = (DeterminesOutputType = "TypedClass"))
static UObject* CastToChecked(UObject* Object, const TSubclassOf<UObject>& TypedClass)
{
    check(Object->IsA(TypedClass));
    return Object;
}
```

The extra check version is there when we need the Cast to succeed.

A Mixin is like adding a member function. Normally it need not null-check this, so the functions above need not null-check UObject. This is how AS binding libraries generally work.

**Addition: a Cast accepting nullptr could be written as below, but newer versions disallow null C++ Mixin receivers, so this no longer works.**

For reference — the underscore again marks a nullptr-accepting convenience rather than a normal member function:

```cpp
/**
 * Cast to Typed UObject, if false , return nullptr.
 * Can be used by any UObject even nullptr.
 */
UFUNCTION(ScriptCallable,  Meta = (DeterminesOutputType = "TypedClass"))
static UObject* CastTo_(UObject* Object, const TSubclassOf<UObject>& TypedClass)
{
    if (!Object) return nullptr;
    if (Object->IsA(TypedClass))
       return Object;
    return nullptr;
}
```

# Combining fluent null checks and Cast

Compare these:

```cpp
// the original way
if (IsValid(Cast<AActor>(ThisObject)))

if (Cast<AActor>(ThisObject) != nullptr)

// the new way
if (ThisObject.CastTo(AActor).IsValid_())
```

The new form clearly reads more intuitively and is more comfortable to write and read, does it not? If you disagree, of course you are even more right!

One addition: do not write ordinary code this way. Use IsA() if you only need a type check. If you need the CastTo result, keep it in a variable before the if.

# ScriptMethod, an alternative Mixin form

Traditional Mixins require a new UObject whenever adding functionality to another class. That can get tedious. UE’s native specifiers can help.

This one was designed for scripting languages such as Python. Interestingly, AS can use it too, and rather nicely.

Here is the English explanation:

The omitted excerpt describes this metadata’s role in Unreal Engine.

Here is an official DataTable function-library example.

The Mixin becomes much easier to write, but DataTable:: namespace calls no longer work. Existing AS code using that form must change.

```cpp
class UDataTableFunctionLibrary : public UBlueprintFunctionLibrary
{
    GENERATED_UCLASS_BODY()

	// Returns whether or not Table contains a row named RowName
  	UFUNCTION(BlueprintCallable, Category = "DataTable", meta=(ScriptMethod="DoesRowExist"))
 	static ENGINE_API bool DoesDataTableRowExist(const UDataTable* Table, FName RowName);

	UFUNCTION(BlueprintCallable, Category = "DataTable", meta=(ScriptMethod="GetRowNames"))
	static ENGINE_API void GetDataTableRowNames(const UDataTable* Table, TArray<FName>& OutRowNames);
```

ScriptMethod can omit `=`, leaving the function name unchanged.

In the following test, ScriptMethodMutable has no effect in AS. Alone it does not work, and paired with ScriptMethod it does not make const data mutable. Mutability depends entirely on whether the first parameter is const. UPARAM(ref) likewise has no effect here.

So ScriptMethod works as a single-function Mixin form. One Blueprint function library can add Mixins for several types, with constness entirely determined by the first parameter.

Here is a test case for the behavior above, if you want to verify it:

```cpp
UCLASS()
class YOUR_API UTestStructFunctionLibrary : public UBlueprintFunctionLibrary
{
    GENERATED_BODY()

    /// ScriptMethod
    UFUNCTION(ScriptCallable,  meta = (ScriptMethod))
    static void TestScriptMethod_Const(const FTestStruct& TestStruct, FName Name)
    {
       // do nothing
    };
    UFUNCTION(ScriptCallable,  meta = (ScriptMethod))
    static void TestScriptMethod(FTestStruct& TestStruct, FName Name)
    {
       // do nothing
    };
    /// ScriptMethodMutable, must use with ScriptMethod, only use with struct
    UFUNCTION(ScriptCallable,  meta = (ScriptMethod, ScriptMethodMutable))
    static void TestScriptMethodMutable_Const(const FTestStruct& TestStruct, FName Name)
    {
       // do nothing
    };
    UFUNCTION(ScriptCallable,  meta = (ScriptMethod, ScriptMethodMutable))
    static void TestScriptMethodMutable(FTestStruct& TestStruct, FName Name)
    {
       // do nothing
    };

    /// UPARAM, must use with ScriptMethod
UFUNCTION(ScriptCallable,  meta = (ScriptMethod))
    static void Test_UPARAM_Const(UPARAM(ref) const FTestStruct& TestStruct, FName Name)
    {
       // do nothing
    };
    UFUNCTION(ScriptCallable,  meta = (ScriptMethod))
    static void Test_UPARAM(UPARAM(ref) FTestStruct& TestStruct, FName Name)
    {
       // do nothing
    };

    /// UPARAM, must use with ScriptMethod
UFUNCTION(ScriptCallable,  meta = (ScriptMethod, ScriptMethodMutable))
    static void Test_UPARAM_Const2(UPARAM(ref) const FTestStruct& TestStruct, FName Name)
    {
       // do nothing
    };
    UFUNCTION(ScriptCallable,  meta = (ScriptMethod, ScriptMethodMutable))
    static void Test_UPARAM2(UPARAM(ref) FTestStruct& TestStruct, FName Name)
    {
       // do nothing
    };
};
```

# Automatic return-type inference through Cpp metadata: DeterminesOutputType

This Lyra function infers its return type from FragmentClass, avoiding Cast calls in Blueprints and AS.

```cpp
	UFUNCTION(BlueprintCallable, meta=(DeterminesOutputType=FragmentClass))
	static const ULyraInventoryItemFragment* FindItemDefinitionFragment(TSubclassOf<ULyraInventoryItemDefinition> ItemDef, TSubclassOf<ULyraInventoryItemFragment> FragmentClass);
```

Further uses: DeterminesOutputType can infer TArray element types, use multiple parameters, and infer from a Property inside a struct.

Example of inferring the returned type and count:

```cpp
	// Automatic inference of the function's return class; without the DynamicOutputParam parameter, the return value is inferred by default
	UFUNCTION(BlueprintCallable, Meta = (DeterminesOutputType = "TypedClass"))
	static TArray<AActor*> MyTestFunc(TSubclassOf<ATestActor> TypedClass);

	// Type inference of function parameters; together with DynamicOutputParam, several parameters can be inferred at once
	UFUNCTION(BlueprintCallable, Meta = (DeterminesOutputType = "TypedClass", DynamicOutputParam = "OutTest,OutTest2"))
	static void MyTestFunc(TSubclassOf<ATestActor> TypedClass, TArray<AActor*>& OutTest, AActor*&  OutTest2);
```

Example of the base type used for inference:

```cpp
	// TSubclassOf<> is supported; the example above already has it

	// DeterminesOutputType can also accept UObject
	UFUNCTION(BlueprintCallable, Meta = (DeterminesOutputType = "Object"))
	static TArray<UObject*> MyTestFunc(ATestObject* Object);

	// DeterminesOutputType supports using a property of a struct as the base type for inference
	// below, the AnyProperty in FTestStruct is used as the base of the inference
	UFUNCTION(BlueprintCallable, Meta = (DeterminesOutputType = "TestStruct_AnyProperty"))
	static TArray<AActor*> MyTestFunc(const FTestStruct& TestStruct);
};
```

Used well, DeterminesOutputType saves plenty of pointless Cast code. With TArray, it can make the world feel a little better!

# Changing arbitrary UPROPERTY values through reflection

Sometimes an AS-exposed field can only be changed during construction, not at runtime. Normally we add a cpp Mixin to operate on it.

That is tedious, and a non-public cpp field may be inaccessible even from ordinary cpp code.

When it is safe to do so, reflection can change it. Most Cpp fields that enter reflection can be operated on.

Here is a simple usage example.

The test case:

```cpp
/// Cpp test case
UCLASS(Blueprintable)
class ATestClass : public AActor
{
    GENERATED_BODY()
public:
    ATestClass(){ TestFloat= 666.f;};
private:
    UPROPERTY()
    float TestFloat;
};
```

After wrapping SetPropertyFloat and GetPropertyFloat, this is the AS form:

```cpp
/// AS test
ATestClass TestClass11 = NewObject(nullptr, ATestClass );

float32 OutValue = 1.0f;
// I put this function in the Reflect namespace; do as you like
Reflect::SetPropertyFloat(TestClass11, n"TestFloat", 9.0f);
Reflect::GetPropertyFloat(TestClass11, n"TestFloat", OutValue);

// FUnitTest& T
T.AssertTrue(OutValue == 9.0f);

// the test should pass
```

See this article for details. Magic is still magic: use it carefully.
Handcrafting UE5 reflection magic: black magic or white magic?

# A quick wrap-up

This article covers null checks, Cast, Mixins, ScriptMethod, DeterminesOutputType and reflection-based property changes. These tricks mostly give repetitive mechanical work to the machine, making code more comfortable to write.

---
