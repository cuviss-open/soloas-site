---
title: "UE_Angelscript — Source 1: how UE classes are bound to AS"
order: 40
category: internals
---
# UE_Angelscript — Source 1: how UE classes are bound to AS

UE-Angelscript is a UE fork with two main parts:

1. Changes to Unreal Engine source.
2. The UE-Angelscript plugin itself.

This article focuses on the plugin’s framework and key details.

The question is: how do UE classes get bound to Angelscript?

There is not room for every detail. Treat this as an architectural overview.

Corrections are welcome if I have misunderstood anything.

Prerequisites: C++, UE and Angelscript knowledge.
# Preface

## Changes to UE source

HAZE changed quite a lot of UE source to integrate closely with the engine.

Changes are generally enclosed by these comments for easy searching:
`// HAZE FIX`
`// END HAZE FIX`
Search globally to locate the edited areas.

They are scattered around, so this article does not analyze them.

## The Angelscript plugin

The core plugin lives under Plugins/Angelscript in the engine directory.
AngelscriptEnhancedInput, AngelscriptGAS and AngelscriptStructUtils provide bindings for specific modules and are not core functionality.

## **Module structure**

The directories and build scripts divide the plugin into these main parts. `AngelscriptCode` is the core runtime module, `AngelscriptEditor` supplies editor extensions, and `AngelscriptLoader` handles startup and coordination:

- **Source/AngelscriptCode**
   Core script-engine integration, bindings and runtime logic.
- **Source/AngelscriptEditor**
   Editor menus, tools, commands and other extensions.
- **Source/AngelscriptLoader**
   Script loading, initialization and engine integration.
- **ThirdParty**
   Third-party dependencies, chiefly AngelScript source and headers.

```
Non-editor mode
AngelscriptLoader ------> AngelscriptCode -------> AngelScript (3rd)

Editor mode
AngelscriptLoader ------> AngelscriptEditor ------> AngelscriptCode -------> AngelScript (3rd)
```

## **Bringing in Angelscript**

Angelscript is a scripting language commonly used alongside C++. It performs well and has C++-like syntax.

Its C++ integration is convenient, with simple APIs and detailed configuration. C++ code generally needs only one header, angelscript.h.

After importing it, UE-Angelscript wraps some original methods and classes in several places to connect Cpp and Angelscript better — in practice, to write less repetitive code.

Overall, Angelscript gives a lightweight, fast scripting extension suited to a C++ engine. UE-Angelscript feels efficient and comfortable to use.

# Binding UE classes to AS

First, a simplified complete flowchart:

```
The main call flow from UE startup to type binding (simplified):

+-----------------------------+
| UE startup / plugin loaded          |
+-----------------------------+
              |
              v
+-----------------------------+
| The AngelscriptLoader module is the entry point |
| void FAngelscriptLoaderModule::StartupModule() |
+-----------------------------+
              |
              v
+-----------------------------+
| The AngelscriptCode module does nothing else on initialization; it has a set of callable functions, including a separate initialization function |
| FAngelscriptCodeModule::InitializeAngelscript() |
+-----------------------------+
              |
              v
+-----------------------------+
| The real initialization starts here |
| FAngelscriptManager::Initialize()  |
| It has three phases |
| PreInitialize_GameThread, Initialize_AnyThread, PostInitialize_GameThread |
+-----------------------------+
              |
              v
+-----------------------------+
| This function contains the part that binds all types |
| FAngelscriptManager::Initialize_AnyThread() |
+-----------------------------+
              |
              v
+-----------------------------+
| FAngelscriptManager::BindScriptTypes() |
+-----------------------------+
              |
              v
+-----------------------------+
| Bind all FBinds |
| void FAngelscriptBinds::CallBinds()  |
+-----------------------------+
              |
              v
+-----------------------------+
| Call the bound lambdas in the order of the FBinds |
|   GetBindArray().Sort();
	for (auto& Function : GetBindArray())
	    Function.Function();   |
+-----------------------------+
```

void FAngelscriptManager::PreInitialize_GameThread() creates two UPackages: /Script/Angelscript and /Script/AngelscriptAssets. AS code lives in the /Script/Angelscript package. PreInitialize also reads UAngelscriptSettings and configures the VM.

void FAngelscriptManager::Initialize_AnyThread() is the core. This article mainly analyzes its contents. It can run off the game thread.

void FAngelscriptManager::PostInitialize_GameThread() simply broadcasts a delegate so external code knows initialization has finished.
## UE classes are bound through FBinds lambdas

The plugin uses the `FBinds` constructor mechanism, with each binding defined as a lambda.

The singleton returned by GetBindArray() holds all these lambdas and their ordering, then runs them in that order.

Here is an example FBind:

```cpp
AS_FORCE_LINK const FAngelscriptBinds::FBind Bind_AActor_Base((int32)FAngelscriptBinds::EOrder::Late-1, []
{
    auto AActor_ = FAngelscriptBinds::ExistingClass("AActor");
    // omitted
});
```

Initializing this variable registers its contents in the GetBindArray() singleton. To bind another Cpp type, add another FBind variable.

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

struct FBindFunction
{
    int32 BindOrder;
    TFunction<void()> Function;

    bool operator<(const FBindFunction& Other) const
    {
       return BindOrder < Other.BindOrder;
    }

};
// ……
```

Source: AngelscriptBinds.h: FAngelscriptBinds::FBind (excerpt; remaining lines omitted).

## How are so many UE classes handled in batches?

Besides primitives, the main script-facing reflected UE types are UObject, UScriptStruct, UEnum and Delegate.

UObject and UScriptStruct account for most of them.

The plugin handles those two in batches.

As mentioned, FBinds lambdas implement every binding.

These two variables bind UObjects.

### Early-stage UObject binding

```cpp
AS_FORCE_LINK const FAngelscriptBinds::FBind Bind_BlueprintType_Declarations(FAngelscriptBinds::EOrder::Early, []
{
    // Bind any clasess that are BlueprintType
    for (UClass* Class : TObjectRange<UClass>())
    {
       if (!ShouldBindEngineType(Class))
          continue;

       // Bind into angelscript engine
       FString ClassName = FAngelscriptType::GetBoundClassName(Class);
       BindUClass(Class, ClassName);
    }

    BindUClassLookup();
});
```

BindUClass is the main binding function. It stores information for bound types in the FAngelscriptTypeDatabase singleton.

For UClass types, it associates the angelscript type with UClass, so AS need not distinguish StaticClass from the class itself.

A little deeper: this uses `plainUserData`, **a custom pointer field on each AngelScript type’s `asCTypeInfo` structure**. Think of it as **attaching a custom C++ pointer to a script type for lookup or parameter handling on the C++ side**.

```cpp
static void BindUClass(UClass* Class, const FString& TypeName)
{
    // Bind into angelscript engine
    auto Class_ = FAngelscriptBinds::ReferenceClass(TypeName, Class);

    // Register angelscript type
    auto Type = MakeShared<FUObjectType>(Class, TypeName, Class_.GetTypeInfo());
    FAngelscriptType::Register(Type);

    // Tell the angelscript type what UClass is associated with it
    auto* TypeInfo = (asCTypeInfo*)Class_.GetTypeInfo();
    if (TypeInfo != nullptr)
    {
       TypeInfo->plainUserData = (SIZE_T)Class;

#if WITH_EDITOR
       const FString& Tooltip = Class->GetMetaData(NAME_Func_Tooltip);
       if (Tooltip.Len() != 0)
          FAngelscriptDocs::AddUnrealDocumentationForType(TypeInfo->GetTypeId(), Tooltip);

       if (IsEditorOnlyClass(Class))
          TypeInfo->flags |= asOBJ_EDITOR_ONLY;

       if (ShouldDisallowInstantiation(Class))
          TypeInfo->flags |= asOBJ_DISALLOW_INSTANTIATION;
#endif
    }
}
```

One level deeper is FAngelscriptBinds::ReferenceClass, the function specifically for UObject binding:

```cpp
FAngelscriptBinds FAngelscriptBinds::ReferenceClass(FBindString Name, UClass* UnrealClass)
{
    auto Binds = FAngelscriptBinds(Name, asOBJ_REF | asOBJ_NOCOUNT | asOBJ_IMPLICIT_HANDLE, 0);
    ((asCObjectType*)Binds.ScriptType)->size = UnrealClass->GetStructureSize();
    Binds.ScriptType->alignment = UnrealClass->GetMinAlignment();
    return Binds;
}
```

asOBJ_REF: reference type, UObject\*.
asOBJ_NOCOUNT: no reference counting; UE manages lifetime.
✅ asOBJ_IMPLICIT_HANDLE: allows omitting @, AS’s handle marker.

An AS UObject is really UObject@, corresponding to C++ UObject\*, so it can be nullptr.

BindUClassLookup is also important: it is key to recognizing UObject-related template forms.

Common UE UObject pointer forms — TSubclassOf, TObjectPtr, TWeakObjectPtr and raw pointers — can be handled in one callback, with the result stored in FAngelscriptTypeUsage.

Specifically:
RegisterTypeFinder adds a custom lookup callback so Angelscript can infer the binding type from the Unreal property: which template wrapper it is, or whether it is a raw pointer.

FAngelscriptTypeDatabase’s TArray<FAngelscriptType::FTypeFinder> TypeFinders stores these callbacks for later interpretation.

```cpp
static void BindUClassLookup()
{
    // Register the type used by TSubclassOf
    auto SubclassOfType = MakeShared<FSubclassOfType>();
    FAngelscriptType::Register(SubclassOfType);

    // Register a type that handles script object types generically
    auto ScriptObjectType = MakeShared<FUObjectType>(nullptr, TEXT("UObject"));
    FAngelscriptType::SetScriptObject(ScriptObjectType);

    // Register the type used by TObjectPtr
    auto ObjectPtrType = MakeShared<FObjectPtrType>();
    FAngelscriptType::Register(ObjectPtrType);

    // Register the type used by TWeakObjectPtr
    auto WeakObjectPtrType = MakeShared<FWeakObjectPtrType>();
    FAngelscriptType::Register(WeakObjectPtrType);

    // Register a type finder into the type system that
    // can look up an ObjectProperty's inner angelscript type.
    FAngelscriptType::RegisterTypeFinder([=](FProperty* Property, FAngelscriptTypeUsage& Usage) -> bool
    {
    // omitted
    });
}
```

`BindUClassLookup` is difficult, so here is its purpose again: register special template wrappers such as `TSubclassOf` and `TWeakObjectPtr`, then make AngelScript correctly recognize the UObject types inside them.

### Bind UObject members and methods at Late

Initial UObject binding is complete, but its members and methods also need batch processing. They are registered later because their types are not necessarily UObjects; those types must be registered first.

That is why order matters. Types generally bind at Early, with their members and methods at Late.

In Bind_BlueprintType.cpp:

```cpp
AS_FORCE_LINK const FAngelscriptBinds::FBind Bind_Defaults((int32)FAngelscriptBinds::EOrder::Late+100,
// omitted
```

The binding is long because it handles many cases. Here is its rough flow:

```cpp
Iterate over all UClasses
   │
   ├─► recursively collect parent classes to keep the inheritance order
   │
   ├─► bind all BlueprintType/BlueprintCallable/ScriptCallable functions
   │
   ├─► bind BlueprintGetter/Setter
   │
   ├─► bind all Blueprint-visible / editable properties
   │
   ├─► handle inheritance, copy parent properties/methods
   │
   ├─► bind StaticClass and global variables
   │
   └─► write to the binding database
```

### Bind UScriptStruct and its members

UScriptStruct binding is simpler because reflection recognizes none of its member functions.

Most code is in Bind_UStruct.cpp and follows a similar pattern to UObject. I will not go through it all again.

```cpp
AS_FORCE_LINK const FAngelscriptBinds::FBind Bind_StructDeclarations((int32)FAngelscriptBinds::EOrder::Early+1, []
{
    HardCodeCallingMetaForUnrealStructs();

    for (UScriptStruct* Struct : TObjectRange<UScriptStruct>())
    {
       if (!ShouldBindEngineType(Struct))
          continue;

       FString TypeName = Struct->GetStructCPPName();

       // Bind into angelscript engine
       FBindFlags BindFlags;
       if (Struct->StructFlags & STRUCT_IsPlainOldData)
          BindFlags.ExtraFlags |= asOBJ_POD;
       BindStructType(TypeName, Struct, BindFlags);
    }

    BindStructTypeLookups();
});
```

One important difference from UObject:
**UScriptStruct binds as a value type.**

```cpp
static void BindStructType(const FString& TypeName, UScriptStruct* Struct, FBindFlags& BindFlags)
{
    auto Binds = FAngelscriptBinds::ValueClass(TypeName, Struct, BindFlags);

    // Register angelscript type
    auto Type = MakeShared<FUStructType>(Struct, TypeName);
    Type->ScriptTypeInfo = Binds.GetTypeInfo();
    Type->ScriptTypeInfo->SetUserData(Struct);
    FAngelscriptType::Register(Type);
}
```

Here is the original value-binding function. The crucial flags are:
asOBJ_VALUE | asOBJ_APP_CLASS means “a C++-defined struct/class that is a value type.”

```cpp
static FAngelscriptBinds ValueClass(FBindString Name, UScriptStruct* StructType, FBindFlags Flags)
{
    int Size;
    auto* Ops = StructType->GetCppStructOps();
    if (Ops != nullptr)
       Size = Ops->GetSize();
    else
       Size = StructType->GetPropertiesSize();
    if (Flags.Alignment == -1)
       Flags.Alignment = StructType->GetMinAlignment();
    return ValueClass(Name, Flags, Size);
}

static FAngelscriptBinds ValueClass(FBindString Name, UScriptStruct* StructType, FBindFlags Flags)
{
    int Size;
    auto* Ops = StructType->GetCppStructOps();
    if (Ops != nullptr)
       Size = Ops->GetSize();
    else
       Size = StructType->GetPropertiesSize();
    if (Flags.Alignment == -1)
       Flags.Alignment = StructType->GetMinAlignment();
    return ValueClass(Name, Flags, Size);
}
```

For a value type such as `FVector`, declare a variable and modify its members. An instance is created directly, without a factory function.

```angelscript
FVector v(1, 2, 3);
v *= 2;
```

For a reference type such as `UObject`, a variable declaration gives Nullptr. Use NewObject or another factory, or obtain an existing instance.

```angelscript
UObject obj = GetSomeObject();
Print(obj.GetName());
```

BindStructTypeLookups is much simpler because no template classes are defined for UScriptStruct.

### Other bindings

UEnum is in Bind_UEnum.cpp.

Delegate is in Bind_Delegates.cpp.

Special template types such as TMap, TArray, TSet and TOptional have dedicated handling.

Common types such as FVector and FTransform often need individual manual handling and have their own binding files.

Global functions such as NewObject and SpawnActor are also defined separately.

---

To be continued.
