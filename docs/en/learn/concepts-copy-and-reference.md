---
title: "UE_Angelscript — Understanding copies and references"
order: 13
category: concepts
---
# UE_Angelscript — Understanding copies and references

# Preface

This article explains some useful foundations for UE-Angelscript: copies and references.

# C++ basics

Anyone with a little C++ knows that function parameters normally pass by value — copying. To operate on the original, use the original object, a pointer or a reference.

What is the original object?
The value itself. Think of an object as a contiguous block of memory describing its details.
A block representing something may have an initial name, say Zhang San.

What is a pointer?
Basically, an object holding a memory address. No need to elaborate.
Pointers make data convenient to operate on: pass the object’s address to locate it.
The pointer is itself an object, but a special one holding another object’s address — GPS coordinates for Zhang San, letting us find him precisely.

What is a reference?
An alias for an object. Operating on the reference operates on the original.
Underneath, a reference is essentially a pointer, except the syntax cannot rebind it and dereferencing is implicit. In ordinary C++ use, leaving that to the compiler and thinking “alias” is enough. But for Angelscript/C++ interaction, ignoring the underlying pointer can produce confusing problems.
What does an alias mean? If the original name is Zhang San, Zhang Tiezhu can be another name for him. Many names can refer to that same object.

What is copying?
Making a complete copy of an object.
Copy Zhang San and you get Li Si. Both now exist. They are identical just after copying, but go on to live separate lives.

Why distinguish copying and references?
Copying costs processing and storage, so avoid it when possible. References help when an object enters a new setting, such as a function. That setting does not care what the original was called. Put it in the right slot and it is called a particular name or number, say 9527.
If Zhang San enters a setting that calls him Gou Dan or 9527, he has no choice. Virtual Zhang San is a puppet without feelings, let alone freedom. He only hopes humans will not accidentally give his rewards to a copied Zhang San instead.

# UE and Angelscript data correspondence

## Value types

Primitive UE types such as int and float map to value types in Angelscript. Operating on them in AS operates on the value itself.

Many bound types, such as FString, FName, FColor and FVector, do too.
In a sentence: `apart from UObject and its subclasses, UE-Angelscript types are value types`.

**Angelscript and C++ use the same spelling.**
For example, `FTestStruct`.

## Proxy types

Or call them pointer types or reference types. The point is that they represent an address rather than the object itself.

As far as I know, only `UObject` and its subclasses bind as proxy types. Angelscript calls these Handles. Their full spelling is actually `UObject@`, but UE-Angelscript allows the `@` to be omitted. Everyone omits it, creating a visual problem: UObjects look just like values, with no special marker, although they are quite different.

**Angelscript and C++ use different spelling.**
Angelscript `UObject` corresponds to C++ `UObject*`.

## Template types — TArray, TMap and TSet

Think of these as compound types. In `TArray<UObject>`, `TArray` is the main type and `UObject` is the subtype.

**Value types use the same spelling in Angelscript and C++.**
For example, `TArray<FTestStruct>`.

**UObject uses different spelling.**
Angelscript `TArray<UObject>` corresponds to C++ `TArray<UObject*>`.

`TMap` and `TSet` work similarly.

Container iterators such as TArrayConstIterator and TArrayIterator are much the same.

## Template types — UObject pointers

TObjectPtr, TWeakObjectPtr, TSoftObjectPtr and so on.

These are compound types too. In `TObjectPtr<UObject>`, the main type is `TObjectPtr`, with subtype `UObject`.

**Angelscript and C++ use the same spelling.**
For example, `TObjectPtr<UObject>`.

## Other template types

These generally are not for UObjects.

For `TOptional<FTestStruct>`, the main type is `TOptional` and subtype is `FTestStruct`.
TOptional holds values, not UObjects. UObjects already express emptiness with nullptr, so another layer is unnecessary.

**Angelscript and C++ use the same spelling.**
For example, `TOptional<FTestStruct>`.

# Angelscript mostly follows C++ copy and reference rules

## With some exceptions

For `UStruct` and `FString\FName\FText` function parameters, anything other than a mutable reference `&` becomes `const &` by default.

Three of the following four functions are equivalent!
GetDataPtr is equivalent to GetDataPtr_InputConst and GetDataPtr_InputConstRef.

```cpp
	FString GetDataPtr(FTestStructInAS A)
	{
		return FDssDataPtr::Create(A).ToString();
	}

	FString GetDataPtr_InputConst(const FTestStructInAS A)
	{
		return FDssDataPtr::Create(A).ToString();
	}

	FString GetDataPtr_InputRef(FTestStructInAS& A)
	{
		return FDssDataPtr::Create(A).ToString();
	}

	FString GetDataPtr_InputConstRef(const FTestStructInAS& A)
	{
		return FDssDataPtr::Create(A).ToString();
	}
```

Other cases follow C++ rules.

The official UE-Angelscript documentation says this too, but how do we prove it?
If a value is copied into a function, its address changes. Compare the addresses to see whether they are the same.

Here is the code.
Note: FDataPtr stores a pointer, and its ToString() converts that pointer to FString. Special custom bindings such as `FDataPtr::Create` require generic-function binding and other deeper techniques not explained here. Treat this as pseudocode.

```cpp
namespace TestGetDataPtr
{
	/// #tag UStruct
	// UStruct in AS is a value type in AS, it needs to be passed by reference to improve performance. We don't want to add const & every time, so we make it as const & in function by default.
	FString GetDataPtr(FTestStructInAS A)
	{
		return FDataPtr::Create(A).ToString();
	}
	// const UStruct params will be added  & too
	FString GetDataPtr_InputConst(const FTestStructInAS A)
	{
		return FDataPtr::Create(A).ToString();
	}
	FString GetDataPtr_InputRef(FTestStructInAS& A)
	{
		return FDataPtr::Create(A).ToString();
	}

	FString GetDataPtr_InputConstRef(const FTestStructInAS& A)
	{
		return FDataPtr::Create(A).ToString();
	}
}

// test code

// #tag  UStruct function
{
	auto Obj = FTestStructInAS();
	auto DataPtr = FDataPtr::Create(Obj).ToString();

	// by default,the function Struct params will be added const &
	auto GetDataPtr = TestGetDataPtr::GetDataPtr(Obj);
	T.AssertTrue(GetDataPtr == DataPtr);

	auto GetDataPtr_InputRef = TestGetDataPtr::GetDataPtr_InputRef(Obj);
	T.AssertTrue(GetDataPtr_InputRef == DataPtr);

	auto GetDataPtr_InputConstRef = TestGetDataPtr::GetDataPtr_InputConstRef(Obj);
	T.AssertTrue(GetDataPtr_InputConstRef == DataPtr);

	// by default,the function Struct params with const will be added  &
	auto GetDataPtr_InputConst = TestGetDataPtr::GetDataPtr_InputConst(Obj);
	T.AssertTrue(GetDataPtr_InputConst == DataPtr);
}
```

The same check works for `FString\FName\FText`.

Other types follow the normal Cpp rules.

Why this exception? Probably performance and simpler syntax. Copying a large UStruct can be expensive.
UObjects are usually larger, so why not optimize them? An Angelscript UObject is essentially a pointer; passing and copying it costs very little.
What about int and other primitives? Those are tiny, so copying is fine too.

## Cases where copying still costs a lot

Every Add on a value container such as `TArray<FTestStruct>` copies one `FTestStruct`.

A beginner might forget `&` when retrieving an element, causing another copy.

Copying may merely cost performance. But if you meant to change the element, changing a copy leaves the container untouched.

To avoid unnecessary copies when receiving a container value, I recommend this:

```cpp
TArray<FTestStruct> TempArray;
TempArray.Add(FTestStruct()); // make sure it is not empty
const auto& TempConst = TempArray[0];
auto& TempMutable = TempArray[0];
```

UObject remains the exception. In `TArray<UObject>`, a UObject is essentially a pointer. Copying it copies only the pointer, so you can still operate on the actual UObject.

---

# Summary

Even in scripts, even with UE-Angelscript’s optimized parameter passing, unclear copy/reference rules can create lots of copies, particularly with containers.

Copies cost performance. Treating a copy as a reference, though, can seriously break gameplay logic.

Since pointers have disappeared from view, **let copies be copies and references be references**. As the saying attributed to Caesar goes: **“Render unto Caesar the things that are Caesar’s, and unto God the things that are God’s.”**

Do not blur the boundary, or you will end up calling a deer a horse.

Of course, an astute reader like you can understand the difference.

---
