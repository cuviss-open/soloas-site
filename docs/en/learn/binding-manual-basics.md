---
title: "UE_Angelscript — Manual binding 1: the basics"
order: 51
category: binding
---
# UE_Angelscript — Manual binding 1: the basics

# Preface

UE-Angelscript already supplies many common bindings. With very few exceptions, scripts can do more than Blueprints.

To write less C++ and get a more C++-like experience in AS, we need to learn how to bind C++ functionality. The official documentation barely covers this.

The **binding series** previously introduced an overview,
[UE_Angelscript — Binding overview: expose more to AS and Blueprints](binding-overview.md). Read it too, to see the available approaches.

That overview describes three: **manual binding**, **Mixin**, and **inheritance/wrapping/conversion**.
**Manual binding** is the most powerful and complex, and is the focus here. Understand it and the others become much easier.

In terms of functionality, **manual binding** contains **Mixin**: it can do whatever a Mixin can do, apart from perhaps unusual exceptions I have not encountered.

Compared with **inheritance/wrapping/conversion**, it covers everything except exposing **BlueprintEvent** and **non-public members or methods**. The concepts articles recommend a C++ middle layer for frequently used AS UClasses, partly for easy extension and partly because manual binding cannot fully replace inheritance and wrapping.

There are other binding solutions and pitfalls in this series. Look them up when you encounter a problem.

# Understanding manual binding

## Manual binding is dirty work

Why has this series not systematically explained the practical steps before now? Because this is both craft and dirty work. Misunderstanding it can mean redoing or refactoring a lot of that work!

After a long period of practice and a little deeper understanding of the script source, I feel I have enough experience to publish this. It is still not guaranteed precise; readers should analyze, judge and try it themselves.

Disclaimer: this is technical sharing, not official documentation. It is for reference and not guaranteed completely correct.

With the disclaimer out of the way, one small point: you may find AS functions without documentation although their Blueprint and C++ APIs are documented. Most likely the binding author could not be bothered to copy it.

Why not? Every binding means another copy. Once the patterns are familiar, the rest is dirty work. Plenty of macro tools help, but it is still dirty work.

## Manual binding is also a craft

Official UClass and UStruct bindings deserve mention. There are enormous numbers of these, and the maintainers wrote batch-registration code. That takes craft!

Template bindings are complicated too. Dirty work, yes, but not simple dirty work: `TArray<>` and `TMap<>` require careful design.

A craft needs knowledge. Beyond UE itself, you need low-level C++, especially memory operations, and some understanding of Angelscript.

How do you learn it?

For practical work, the plugin supplies many examples. Imitating them teaches a lot. When unsure how to bind something, look for a similar binding in the plugin source. It may suddenly click.

# Angelscript binding foundations

Heavily modified as UE-Angelscript is, it is still Angelscript. The language documentation is the starting point.

Official documentation:
https://www.angelcode.com/angelscript/sdk/docs/manual/index.html

It covers the language thoroughly with detailed examples. But UE-Angelscript uses an older, modified version, so treat it as reference.

This article extracts a few important binding concepts.

## Bound types: values and handles

- Values represent the object itself. In UE-Angelscript, that means everything except UObject types; likewise in C++.
- _Object handles_ correspond to UE-Angelscript UObjects and C++ UObject pointers.

In one sentence, UObject and its subclasses are handles; the rest are values.

A value represents itself, so copying duplicates the value. A handle refers to another concrete object; copying the handle does not copy its target.

Handles correspond to pointers. UObjects are often heavyweight. Handles or pointers keep operations lightweight and avoid costly accidental copies.

## Key AS engine concepts

This goes a little deeper; skip it unless needed. It is useful for generic binding.

### AS script engine

`class asCScriptEngine* Engine` is the engine object, accessible through FAngelscriptManager:

```cpp
/* Internal script data. */
class asCScriptEngine* Engine = nullptr;

asIScriptEngine* GetScriptEngine() const
{
    return (asIScriptEngine*)Engine;
}
```

Names starting with asC are concrete objects; asI names are interfaces. Angelscript uses this even when an interface has only one implementation, so commonly used interfaces and concrete types can be cast between.

### AS modules

UE-Angelscript uses one AS module. Angelscript supports multiple modules if the host wants them; UE-Angelscript chooses single-module mode.

```cpp
const asCModule* Module = static_cast<asCModule*>(Engine->GetModuleByIndex(0));
```

This API returns nullptr if nothing is found.

With a single module, declared AS types ultimately use this module form:

```cpp
auto ObjPath = f"/Script/Angelscript.{ParentNameStr}";

UClass ParentClass = Cast<UClass>(FindObject(ObjPath));
```

AS classes live under `/Script/Angelscript`.
Omit A, U and F class-name prefixes. Enums are the exception and require their full names.

When Engine and Module offer similar APIs, Module generally gives a more precise result. Global AS functions, for example, belong to the Module namespace.

### AS type information

```cpp
asCTypeInfo* Info = (asCTypeInfo*)Engine->GetTypeInfoById(TypeId);
```

asCTypeInfo describes every usable AS type, whether bound or script-declared. It makes information such as `GetName()` easy to obtain.

Its `typeId` member is often useful in generic binding. Unlike C++’s identifiers, this is Angelscript’s independent ID system, with a unique ID per type.

Another key member is `plainUserData`, a pointer for host-defined data. UE-Angelscript stores reflection-type information there: UObject types, for example, store a `UClass*`.

Not every plainUserData contains reflection data. UENUM handling is not uniform as of UE 5.5: a C++ UENUM stores `UEnum*` in asCTypeInfo, while an AS-declared enum does not.

## Wrapping registration methods: FAngelscriptBinds::Bind

### A short explanation

A global singleton manages C++/AS interaction:

```cpp
FAngelscriptManager::Get()
```

You see it everywhere. But the busy manager delegates core registration work to a helper:

```cpp
struct ANGELSCRIPTCODE_API FAngelscriptBinds
```

FAngelscriptBinds then has its own errand-runner to pass registration information to FAngelscriptManager:

```cpp
FAngelscriptBinds::Bind
```

This type is purely a courier, registering content through its constructor:

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

I mention the courier because binding code interacts with it constantly. Write bindings and you will meet it every day!

It passes our registration code to the GetBindArray() singleton, which eventually reports to FAngelscriptManager. The manager already has enough to do without directly handling every registration.

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

The source walkthrough covers the surrounding flow. This section focuses on the part most closely tied to binding.

The conclusion: constructing an `FAngelscriptBinds::Bind` stores its parameters — ordering and the registration function — until FAngelscriptManager calls them at the appropriate time.

### Binding order

The first important constructor parameter is order. Omit it and it defaults to 0.

An Enum normally specifies the order instead of a literal number:

```cpp
enum class EOrder : int32
{
    Early = -100,
    Normal = 0,
    Late = 100,
};
```

The plugin does not directly document these stages, but existing bindings suggest:
Early normally declares types and constructors with no arguments, same-type arguments or primitive arguments.
Normal is used less often.
Late normally binds constructors, members and methods.

Order matters. Refer to an undeclared type and registration fails, normally with a log message identifying the binding.

### Registration function body

Here are common binding methods and important basic concepts.

The second `FAngelscriptBinds::Bind` parameter is a function pointer, usually written as a lambda.

Inside, declare an FAngelscriptBinds variable and operate on it:

```cpp
auto FQuat_ = FAngelscriptBinds::ValueClass<FQuat>("FQuat", Flags);
FAngelscriptType::Register(MakeShared<FQuatType>());
FQuat_.SetTypeUserData(TBaseStructure<FQuat>::Get());
```

`ValueClass` declares a value type at Early. `ReferenceClass` binds reference types as AS object handles and is used only for UObjects.

`FAngelscriptType::Register` registers an `FAngelscriptType` description for the newly declared type. One important use is telling the plugin how that type behaves as another type’s member.

`FAngelscriptType` is important enough for its own explanation below.

New plain-struct bindings should generally define a custom `FAngelscriptType`; without one, problems can include being unusable in TArray and similar containers.

`SetTypeUserData` sets host-defined type data. Here it puts UScriptStruct information into asCObjectType’s plainUserData for later use.

```cpp
FAngelscriptBinds FQuat_ = FAngelscriptBinds::ExistingClass("FQuat");
```

`ExistingClass` retrieves the FAngelscriptBinds for an already-declared type so more registrations can be added.

FAngelscriptBinds has many methods. The most common are:

```cpp
Constructor
Property
Method
```

Constructor binds constructors, Property binds fields, and Method binds member functions.

All of this maps the same memory between C++ and Angelscript. A C++ object called `Alice` need not have that name in AS. It can be `Bob`, or even `Bob<Charlie>` in a generic binding.

Matching memory layouts allow surprising tricks. If C++ types M and N have identical layouts — perhaps I copied inaccessible M into N — N can map to an AS type named M without trouble.

## Type descriptions: FAngelscriptType and Usage

### FAngelscriptType

Its comment is below. Think of a structure describing an AS type and its interaction with other types.

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

Distinguish these pairs:

- UCLASS type --> UClass type information
  Each UObject has a corresponding UClass.

- USTRUCT type --> UScriptStruct type information
  Each USTRUCT has a UScriptStruct.
  Sometimes called UnrealUStruct, or shortened to UStruct in articles. Context matters: UStruct is also the parent type of UClass and UScriptStruct.

- UENUM type --> UEnum type information
  Each UENUM has a UEnum.

- `Every type appearing in Angelscript` --> `asCTypeInfo` information
  Its plainUserData can hold UClass, UScriptStruct, UEnum or other information as needed.

- `Every type appearing in Angelscript` --> `FAngelscriptType` description
  Some information overlaps asCTypeInfo, but FAngelscriptType is highly customizable and avoids modifying asCTypeInfo.

### FAngelscriptTypeUsage

Its comment is below. It describes a type’s particular usage. TArrays differ in subtypes, counts and other details; UObjects differ in constness. This type records such differences.

```cpp
/**
 * Describes a particular usage of an angelscript type,
 * including all qualifiers, wrappers, and other.
 */
struct ANGELSCRIPTCODE_API FAngelscriptTypeUsage
```

It is often used to compare types in generic binding. It connects to FAngelscriptType and can be **created directly from TypeId**.

```cpp
// Match a type usage to an angelscript TypeId
static FAngelscriptTypeUsage FromTypeId(int32 FAngelscriptType);
```

Why does that matter? It makes generic binding much more convenient: validate the type supplied by the user! Space does not permit exploring that further here.

## The three steps of complete binding

The plugin already handles USTRUCT, UCLASS and UENUM. Full custom binding mainly concerns plain structs, so assume an FTestStruct exists.

- Create an FAngelscriptType.
  Usually derive from `TAngelscriptCppType<NativeType>` and override methods.

- Create a global FAngelscriptBinds::FBind for declarations.
  Normally run near Early.
  Associate FAngelscriptType while declaring the type.
  SetTypeUserData if appropriate.

- Create a global FAngelscriptBinds::FBind for members and functions.
  Normally run at or after Late.
  Bind a default constructor if none exists, otherwise AS cannot declare a value directly.

---

This article covers the foundations and the three-step process. When time permits, I will organize the practical details — the craftsmanship.

At present, UE C++ APIs generally map fairly easily to Angelscript, apart from lambda-like function pointers, templates and interfaces. Even raw pointers need not always become reference types. This correspondence feels comfortable when working in both C++ and Angelscript.

---
