---
title: "UE_Angelscript — Garbage collection and reflection for class members"
order: 30
category: practice
---
# UE_Angelscript — Garbage collection and reflection for class members

UObject garbage collection and reflection are already complicated enough in C++. Angelscript simplifies some of it. Digging deeper, I found the changes sensible, but a little harder to understand.

Here is an important conclusion: Angelscript adds UObject class members, including UObjects inside TArray | TMap | TSet members, to GC by default. That makes TWeakObjectPtr worth using more widely. It allows plenty of decoupling because it does not prevent GC and stops reference chains from growing too much.

This article concentrates on garbage collection.

## Garbage collection basics

GC is UE’s separate lifetime-management system for UObjects; only UObjects participate. After NewObject, we normally do not need to manage the object ourselves. GC scans to see whether it is still in use and cleans it up when it is not.

But GC can only see what is marked for it. That is why C++ often marks UObject members with UPROPERTY() just to make GC see them.

For a UObject member, UPROPERTY() has two meanings: inclusion in GC and inclusion in reflection.

C++ does not separate those two uses. Angelscript does: UObject members in structs and classes, including those inside TArray | TMap | TSet, participate in GC whether marked UPROPERTY or not. Angelscript’s UPROPERTY() is then only the marker for exposing members to reflection and Blueprints.

## Interesting facts

### Reflection

**Struct members join reflection by default; class members do not.**

That is one difference between AS classes and structs. Structs join reflection by default and can be traversed through PropertyLink; classes do not. Classes need not, and cannot, include everything by default. This is not only about reducing overhead: some types cannot participate in reflection. Add UPROPERTY() yourself when reflection is needed. Structs are treated as simple data containers, so all their members are reflected; types that cannot be reflected cannot be members.

Being reflected by default does not expose a struct member to Blueprints. Blueprint access still requires UPROPERTY().

```cpp
// Angelscript code
struct FStructTest
{
	UObject Obj; // this is actually a UPROPERTY, reflection can access it
}
// Angelscript code
class UTestObj
{
	UObject Obj; // this is just an ordinary pointer, reflection cannot access it
}
```

### GC

**Structs and classes both add UObject members, including UObjects in TArray | TMap | TSet, to GC by default.**

This change is implemented by the code interpreter. The relevant code is here:

```cpp
void FAngelscriptClassGenerator::DetectAngelscriptReferences(TSharedPtr<FAngelscriptClassDesc> ClassDesc)
 {
	 // skip ...
	if (!bAddedAsUnrealProperty)
	{
	    if(PropertyType.HasReferences())
	    {
	       RefParams.AtOffset = PropertyOffset;
	       RefParams.Names.Push(Name);
	       PropertyType.EmitReferenceInfo(RefParams);
	       RefParams.Names.Pop();
	    }
	}
}
```

So the precise description of the different UObject-member cases is:

```cpp
// What really happens in Angelscript
class UTestObj : public UObject
{
    // Case 1: protected by GC (through UPROPERTY)
    UPROPERTY()
    UObject ProtectedObj;  // GC tracks this reference, so the object will not be reclaimed by accident

    // Case 2: protected by GC (through UPROPERTY)
    UPROPERTY()
    TObjectPtr<UObject> ProtectedObj;

    // Case 3: protected by GC (even without UPROPERTY, unlike C++!)
    UObject UnprotectedObj;  // no UPROPERTY, but GC still tracks this reference

    // Case 4: a safe weak reference
    TWeakObjectPtr<UObject> WeakObj;  // does not stop GC, but can be checked safely
};
```

Yes, there are three ways to be protected by GC and **usually only one way not to be protected**. Ignore other possible wrapper types for now.

Another point: cases 1 through 3 should all still be checked for null before use. In theory they are protected and normally will not be collected, but what if some code forces collection — for example, by calling MarkAsGarbage()? You could end up with a dangling pointer.

## Not preventing GC — TWeakObjectPtr

### Wrapping TWeakObjectPtr

A wrapper can make TWeakObjectPtr easier to use. This first came from a problem in the script itself.

AS has a problem with `TWeakObjectPtr<UObject>`: it keeps reporting errors. UObject is the most basic type, yet its function calls fail while subclasses work. Perhaps that will be fixed later.

```cpp
	{
		TWeakObjectPtr<UObject> WOP;
		// Note: this problem only occurs on the UObject base class; concrete subclasses such as AActor work fine
		// Error: No matching signatures to 'TWeakObjectPtr::Get()'
		auto Obj = WOP.Get();
	}

	{
		TWeakObjectPtr<AActor> WOP;
		// no error
		auto Obj = WOP.Get();
	}
```

What to do? I could not quickly untangle the plugin’s binding source, so I wrote a wrapper that works directly with `TWeakObjectPtr<T>`.

```cpp
    TWeakObjectPtr<UObject> WOP;
    FWeakObjectPtrWrapper Wrapper = WOP;
    Wrapper.Get();
```

Such a wrapper is easy to write in cpp:

```cpp
// Make TWeakObjectPtr<UObject> useful
USTRUCT(BlueprintType)
struct FWeakObjectPtrWrapper
{
    GENERATED_BODY()

    UPROPERTY(EditAnywhere, BlueprintReadWrite)
    TWeakObjectPtr<UObject> WeakObjPtr = nullptr;
```

Then give it the same interface. Other articles in this series cover that in detail, so I will not repeat it.

### Nested TArrays and automatic inference

One useful suggestion: make its TArray form too. Angelscript can do that, but Cpp has advantages, especially convenient automatic inference.

```cpp
// Make TArray<FWeakObjectPtrWrapper> useful
USTRUCT(BlueprintType)
struct FWeakObjectPtrWrapperArray
{
    GENERATED_BODY()

    UPROPERTY(EditAnywhere, BlueprintReadWrite)
    TArray<FWeakObjectPtrWrapper> WeakObjPtrArray;
};
```

Why? Angelscript does not allow a TArray inside another TArray. This saves trouble later.

Containers such as TArray occasionally run into inference problems. Casting every time is annoying. A few Cpp helper functions for inference can save many conversions.
For example:

```cpp
// Get all the valid Typed UObjects to an array
UFUNCTION(ScriptCallable, Meta = (DeterminesOutputType = "TypedClass", ScriptMethod))
static TArray<UObject*> GetTypedArray(const FWeakObjectPtrWrapperArray& PtrWrapperArray, const TSubclassOf<UObject>& TypedClass)
{
    TArray<UObject*> ReturnArray;
    for (auto& PtrWrapper: PtrWrapperArray.WeakObjPtrArray)
    {
       if (PtrWrapper.WeakObjPtr.IsValid() && PtrWrapper.WeakObjPtr->IsA(TypedClass))
       {
          ReturnArray.Add(PtrWrapper.WeakObjPtr.Get());
       }
    }
    return ReturnArray;
}
```

## Summary

Angelscript’s default reflection and GC behavior is good: it removes a lot of boilerplate. It also creates differences between C++ and Angelscript, but overall the benefits outweigh the drawbacks.

Default reflection for structs does not change gameplay logic and brings plenty of benefits.
Default GC for UObject members of structs and classes can lengthen reference chains. Remember to clear references; forgetting usually costs memory rather than affecting gameplay much. Not preventing GC therefore becomes especially useful: use TWeakObjectPtr more. Overall, this is a good trade.

---
