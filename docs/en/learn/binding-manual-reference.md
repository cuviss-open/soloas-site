---
title: "UE_Angelscript — Manual binding 2: a binding handbook"
order: 52
category: binding
---
# UE_Angelscript — Manual binding 2: a binding handbook

First, the official Angelscript documentation:

https://www.angelcode.com/angelscript/sdk/docs/manual/index.html

Some material repeats [UE_Angelscript — Manual binding 1: the basics](binding-manual-basics.md). Treat it as reinforcement and a way to make the context a little more complete.

# Foundations

This section explains the underlying principles and execution of AngelScript/C++ binding in Unreal.

### The essence

**Binding exposes the same memory address to both C++ and AngelScript, possibly under different names or identifiers.** C++ and AS share the memory while giving it different language-level meanings, allowing zero-copy type mapping.

More specifically:

- **Memory address**: the physical location does not change. A C++ object occupies memory; AS references or pointers point to that same address.
- **C++ name**: a variable, object pointer, iterator, and so on.
- **AS name**: the script-visible function, variable or reference name, which may differ from C++.

### Mapping

AS bindings need two things to map CPP and AS names: a `Signature` and the corresponding pointer, such as a type, member, function or global-variable pointer.

Declare the binding information in a global variable. Its lambda runs in order to perform registration.

For example:

```cpp
AS_FORCE_LINK const FAngelscriptBinds::FBind Bind_FColor(FAngelscriptBinds::EOrder::Late, []
{
	// the concrete binding code
});
```

- `AS_FORCE_LINK` is a macro. Treat it as boilerplate and include it.

- `const FAngelscriptBinds::FBind` is the registration type. During initialization it passes its arguments to the global `FAngelscriptBinds::GetBindArray()`. When registration should actually run, `FAngelscriptBinds::CallBinds()` is called.

The constructor receives data --> a global collects it --> callbacks run in order at the appropriate time.

- `Bind_FColor` is only a variable name. It rarely needs referring to again, so just avoid collisions. I recommend `Bind_` plus the type name for easy searching.

I prefer the full type name, keeping prefixes such as F.

- `FAngelscriptBinds::EOrder::Late` specifies order. This is important when depending on other bound types; the wrong order prevents registration.

The values are -100, 0 and 100. Cast to int32 to customize them freely. Literal numbers also work because FAngelscriptBinds::FBind accepts int32.

```cpp
/* Register functions to be called at bind-time. */
enum class EOrder : int32
{
    Early = -100,
    Normal = 0,
    Late = 100,
};

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

Another point worth emphasizing: separate type declarations from method registration. When members or methods depend on other types, this reduces ordering worries.

I recommend declarations near `Early`, and dependent content near `Normal` or `Late`.
Use `_Declaration` on the declaration variable and a normal name on the other binding.

The flow is:

1. Collect bindings through global constructors →
2. Execute registration callbacks later →
3. Register type information →
4. Establish mappings.

- The concrete registration code is explained below.

# Basic binding

### Type declaration

Supply a concrete C++ type in the angle brackets, then its AS name.

The names can match or differ. A non-template CPP type can even be exposed as a template in AS.

A template’s `T` is resolved when AS uses it. AS returns the concrete subtype and calls `TemplateCallback`, giving you a chance to validate the type and do other work.

In short, declaration tells AS that a type named XXX exists with this memory layout. AS does not care what CPP calls it; the CPP type determines the layout.

```cpp
auto FBox_ = FAngelscriptBinds::ValueClass<FBox>("FBox", Flags);

// if template
FBindFlags ItFlags;
ItFlags.bTemplate = true;
ItFlags.TemplateType = "<T>";
auto TArrayIterator_ = FAngelscriptBinds::ValueClass<FArrayIterator>("TArrayIterator<class T>", ItFlags);
```

After declaration, retrieve the binding directly:

```cpp
auto FBox_ = FAngelscriptBinds::ExistingClass("FBox");

// if template
auto TArrayIterator_ = FAngelscriptBinds::ExistingClass("TArrayIterator<T>");
```

The following shows that the CPP type name is only used to obtain memory-layout information.

- `alignof` gives the **alignment requirement**: the address multiple required for an object of that type.
- `sizeof` gives the size in bytes of a type or object.
- `asGetTypeTraits<T>()` **converts C++ construction, destruction, assignment and copying traits into AngelScript flags**, telling the runtime how to manage the type’s lifetime.

```cpp
template<typename T>
static FAngelscriptBinds ValueClass(FBindString Name, FBindFlags Flags)
{
    if (Flags.Alignment == -1)
       Flags.Alignment = alignof(T);
    Flags.ExtraFlags |= asGetTypeTraits<T>();
    return ValueClass(Name, Flags, sizeof(T));
}
```

What if size varies? TOptional owns a value and changes size with its subtype. Add Flags and call TemplateSizeCalculatorFunctions to tell AS how the size is determined.

```cpp
FBindFlags Flags;
Flags.bTemplate = true;
Flags.TemplateType = "<T>";
Flags.ExtraFlags |= asOBJ_TEMPLATE_SUBTYPE_DETERMINES_SIZE;
Flags.ExtraFlags |= asOBJ_TEMPLATE_SUBTYPE_COVARIANT;
Flags.Alignment = 1;
auto TOptional_ = FAngelscriptBinds::ValueClass("TOptional<class T>", sizeof(bool), Flags);
FAngelscriptManager::Get().Engine->TemplateSizeCalculatorFunctions.Add((asCObjectType*)TOptional_.GetTypeInfo(), &CalculateOptionalSize);
```

### Associating type information

FAngelscriptType is an intermediary designed for this purpose:

Why is it needed?

UE has descriptions such as UClass. AS has asITypeInfo, whose plainUserData can store UClass. Linking them already gives comprehensive information.

But where do we put additional details: whether the type can be a UProperty, a template subtype, sorted, and so on?

FAngelscriptType describes these. It has no data members, only methods implemented by subclasses.

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

Subclasses do have members, such as the common UCLASS and USTRUCT types:

```cpp
/**
 * Type operations for an UObject type.
 */
struct FUObjectType : TAngelscriptPODType<UObject*>
{
	UClass* Class = nullptr;
	FString ClassName;
	asITypeInfo* ClassScriptType = nullptr;
	// ...

struct FUStructType : FAngelscriptType
{
    UScriptStruct* Struct = nullptr;
    asITypeInfo* ScriptTypeInfo = nullptr;
    FString StructName;
    // ...
```

With descriptions available, we still need each usage’s details: constness, reference direction and more. Another type describes those.

Its few members are central to usage and include nested types. Containers are types too; more than zero SubTypes indicates a container.

```cpp
/**
 * Describes a particular usage of an angelscript type,
 * including all qualifiers, wrappers, and other.
 */
 struct ANGELSCRIPTCODE_API FAngelscriptTypeUsage
{
    TArray<FAngelscriptTypeUsage> SubTypes;
    TSharedPtr<FAngelscriptType> Type;
    bool bIsReference = false;
    bool bIsConst = false;

    union
    {
       class asITypeInfo* ScriptClass;
       class FProperty* UnrealProperty;
       int32 TypeIndex;
    };
	// ...
```

FAngelscriptTypeUsage has several construction methods. Common ones include FromTypeId, FromProperty, FromClass and FromStruct.
FromClass and FromStruct try `FAngelscriptTypeDatabase::Get()` for the corresponding FAngelscriptType, then fall back to UASClass or UASStruct.

FromTypeId is especially useful for generic functions.

Back to associating type information. For example:

```cpp
// const FAngelscriptBinds::FBind Bind_FVector

auto VectorType = MakeShared<FVectorType>();
FAngelscriptType::Register(VectorType);
FAngelscriptType::RegisterTypeFinder([VectorType](FProperty* Property, FAngelscriptTypeUsage& Usage) -> bool
{
    FStructProperty* StructProp = CastField<FStructProperty>(Property);
    if (StructProp == nullptr)
       return false;

    if (StructProp->Struct == FVector_NetQuantize::StaticStruct()
       || StructProp->Struct == FVector_NetQuantize10::StaticStruct()
       || StructProp->Struct == FVector_NetQuantize100::StaticStruct()
       || StructProp->Struct == FVector_NetQuantizeNormal::StaticStruct())
    {
       Usage.Type = VectorType;
       return true;
    }

    return false;
});

```

FAngelscriptType::Register adds the type to two globals:

```cpp
auto& Database = FAngelscriptTypeDatabase::Get();
Database.RegisteredTypes.Add(Type);

Database.TypesByAngelscriptName.Add(AngelscriptName, Type);

// if UClass
Database.TypesByClass.Add(Class, Type);

// if Type->GetData();
Database.TypesByData.Add(Data, Type);

// if (Type->CanQueryPropertyType())
Database.TypesImplementingProperties.Add(Type);
```

TypesByAngelscriptName is a TMap for fast lookup by type name.
Other information is registered in different globals according to the situation.

FAngelscriptType::RegisterTypeFinder associates FProperty with FAngelscriptTypeUsage, creating usage descriptions from UProperties. This is useful for property-compatible containers and pointers such as TMap and TSubclassOf.

FAngelscriptTypeUsage::FromProperty uses TypeFinders to construct the usage. If none matches, it tries TypesImplementingProperties one at a time, calling FAngelscriptType::MatchesProperty.
That shows the intermediary role again.
For example, this override matches FUInt8Type:

```cpp
struct FUInt8Type : TIntegralAngelscriptType<uint8, FByteProperty>
{
    virtual FString GetAngelscriptTypeName() const
    {
       return TEXT("uint8");
    }

    bool MatchesProperty(const FAngelscriptTypeUsage& Usage, const FProperty* Property, EPropertyMatchType MatchType) const override
    {
       if (auto* ByteProp = CastField<FByteProperty>(Property))
       {
          if (ByteProp->Enum == nullptr)
             return true;
       }

       return false;
    }
};
```

### Injecting custom type information

We often attach extra information to an AS type for convenient handling. Dedicated pointers hold this data.

When do we inject it?

Type declaration, such as FAngelscriptBinds::ValueClass, eventually reaches:

```cpp
int TypeId = Manager.Engine->RegisterObjectType(ClassName.ToCString(), Size, Flags);

asITypeInfo* ScriptType = Manager.Engine->GetTypeInfoByName(ClassName.ToCString());
```

FAngelscriptBinds stores `asITypeInfo* ScriptType`, the AS type metadata.

asITypeInfo has one subclass, asCTypeInfo, which can store custom information such as reflection metadata. UObject\* types store UClass\* pointers.

```cpp
// User data
void *SetUserData(void *data, asPWORD type);
void *GetUserData() const { return (void*)plainUserData; }
```

At this point, our UserData is not yet in asITypeInfo.

There are two ways to store it: ordinary types at binding time, template types when their concrete type is inferred.

- 1. Ordinary types

Set UserData while binding:

```cpp
auto FVector_ = FAngelscriptBinds::ValueClass<FVector>("FVector", Flags);
FVector_.SetTypeUserData(TBaseStructure<FVector>::Get());
```

Some cases take a slightly indirect route:

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
// ……
```

Source: Bind_BlueprintType.cpp: Bind_BlueprintType_Declarations (excerpt; remaining lines omitted).

2. Template types

Determine type information through a Callback, then store custom data during that callback.

```cpp
AS_FORCE_LINK const FAngelscriptBinds::FBind Bind_TOptional(FAngelscriptBinds::EOrder::Early, []
{
	// ...
    auto TOptional_ = FAngelscriptBinds::ValueClass("TOptional<class T>", sizeof(bool), Flags);
 	// ...
    TOptional_.TemplateCallback("bool f(int&in Type, int&out ErrorMessage)",
       [](asITypeInfo* TemplateType, asCString* ErrorMessage) -> bool
    {
       return FOptionalOperations::ValidateOptionalOperations(TemplateType, ErrorMessage) != nullptr;
    });

FOptionalOperations* FOptionalOperations::ValidateOptionalOperations(asITypeInfo* TemplateType, asCString* ErrorMessage)
{
    if (FOptionalOperations* Ops = static_cast<FOptionalOperations*>(TemplateType->GetUserData()))
    {
       return Ops->bValid ? Ops : nullptr;
    }

    const FAngelscriptTypeUsage Type = FAngelscriptTypeUsage::FromTypeId(TemplateType->GetSubTypeId(0));

    if (!Type.CanBeTemplateSubType())
    {
       if (ErrorMessage != nullptr)
          *ErrorMessage = "Containers cannot be nested in other containers";
       return nullptr;
    }

    FOptionalOperations* Ops = new FOptionalOperations(Type);
    TemplateType->SetUserData(Ops);
// ……
```

Source: Bind_TOptional.cpp: Bind_TOptional (excerpt; remaining lines omitted).

### Constructors

#### Ordinary types

Constructors are normally bound separately and differ from ordinary methods:

```cpp
FVector_.Constructor("void f(float64 X, float64 Y, float64 Z)", [](FVector* Address, double X, double Y, double Z)
{
    new(Address) FVector(X, Y, Z);
});
FAngelscriptBinds::SetPreviousBindNoDiscard(true);
SCRIPT_TRIVIAL_NATIVE_CONSTRUCTOR(FVector_, "FVector");
```

- Constructor

The parameters are a string and function pointer. The function’s first argument must point or refer to the CPP type corresponding to the AS type.
The body uses placement new: here it constructs `FVector` at the **existing address `Address`**.

This eventually calls the engine’s RegisterObjectBehaviour with asBEHAVE_CONSTRUCT, allowing constructor syntax in AS.

OnBind caches the current FunctionId in PreviouslyBoundFunction. Later registration operations can then add information, such as documentation, to the preceding function.

```cpp
BindExternBehaviour(asBEHAVE_CONSTRUCT, Signature, asFUNCTION(Fun), ASAutoCaller::MakeFunctionCaller(Fun), UserData);

void FAngelscriptBinds::BindExternBehaviour(asEBehaviours Beh, FBindString Signature, asSFuncPtr Ptr, ASAutoCaller::FunctionCaller Caller, void* UserData)
{
    auto& Manager = FAngelscriptManager::Get();
    int FunctionId = Manager.Engine->RegisterObjectBehaviour(ClassName.ToCString(), Beh, Signature.ToCString(), Ptr, asCALL_CDECL_OBJFIRST, *(asFunctionCaller*)&Caller);
    OnBind(FunctionId, UserData, nullptr);
}
```

- FAngelscriptBinds::SetPreviousBindNoDiscard(true)
  Similar to C++ `[[nodiscard]]`: do not ignore the return value.

- SCRIPT_TRIVIAL_NATIVE_CONSTRUCTOR handles precompilation. Several related macros exist. One adds implicit constructor arguments, such as ForceInit, absent from the signature but supplied at runtime.

```cpp
FSphere_.Constructor("void f()", [](FSphere* Address)
{
    new(Address) FSphere(ForceInit);
});
FAngelscriptBinds::SetPreviousBindNoDiscard(true);
SCRIPT_TRIVIAL_NATIVE_CONSTRUCTOR_CUSTOMFORM(FSphere_, "FSphere", "ForceInit");
```

Precompilation speeds runtime loading, using a global information table.
You need not dwell on every detail: attach this macro for constructors. Omitting it generally does not stop execution.

```cpp
void FScriptFunctionNativeForm::BindNativeConstructor(FAngelscriptBinds& Binds, const ANSICHAR* Name, bool bTrivial, const ANSICHAR* CustomForm)
{
    if (!FAngelscriptManager::bGeneratePrecompiledData)
       return;
    GScriptNativeForms.Add(FAngelscriptBinds::GetPreviousBind(), new FScriptNativeConstructor(Name, bTrivial, CustomForm));
}
```

#### Template types

This is generic binding; most people can skip it.

```cpp
TOptional_.Constructor("void f()", &FAngelscriptOptionalBinds::Construct);
SCRIPT_NATIVE_TEMPLATED_CALL(TOptional_, "FAngelscriptOptionalBinds::Construct", false);
FAngelscriptBinds::PreviousBindPassScriptObjectTypeAsFirstParam();
```

SCRIPT_NATIVE_TEMPLATED_CALL invokes a template function suffixed `_Template`:

```cpp
static void Construct(FAngelscriptOptional& Optional, asCObjectType* Meta);

template<typename T>
static void Construct_Template(TOptional<T>& Optional)
{
    new (&Optional) TOptional<T>();
}
```

Its information is stored alongside that of SCRIPT_TRIVIAL_NATIVE_CONSTRUCTOR:

```cpp
static TMap<asIScriptFunction*, FScriptFunctionNativeForm*> GScriptNativeForms;
```

Why? Faster runtime access. It still runs without this.

- FAngelscriptBinds::PreviousBindPassScriptObjectTypeAsFirstParam()

  This injects the current bound type’s `asCObjectType*` as the first argument of the function just registered. In the written binding format, the instance itself is already first, so this appears second. It gives access to type information, particularly the UserData stored earlier.

Example: obtain type information during construction and perform type-specific work.

```cpp
void FAngelscriptOptionalBinds::Construct(FAngelscriptOptional& Optional, asCObjectType* Meta)
{
    auto* Ops = FOptionalOperations::GetOptionalOperations(Meta);
    if (Ops->bIsIntrusive)
    {
       Ops->Type.Type->InitializeIntrusiveUnsetOptionalValue(Ops->Type, &Optional);
    }
    else
    {
       *Ops->GetIsSetPtr(Optional) = false;
    }
}
```

#### A quick wrap-up

Even constructors have many details, but following existing examples is straightforward when simply using the pattern.

A type without a bound constructor cannot be explicitly constructed in AS. Sometimes this is deliberate: instances come only from functions such as factories.

### Members

Use .Property with a signature string and member pointer:

```cpp
FSphere_.Property("float64 W", &FSphere::W);
```

Cpp float is float32 in AS, and double is float64. This is easy to overlook.

Bitfields cannot bind as ordinary members because their addresses cannot be taken. UE uses many bitfields to save memory. Bind Get/Set functions instead.

### Methods

.Method takes a signature string and function pointer. METHOD_TRIVIAL and METHODPR_TRIVIAL make member-pointer syntax quicker.
Custom helpers can live elsewhere and be referenced with member-style address syntax, such as `&FAngelscriptOptionalBinds::Reset`.
Lambdas can be supplied directly too.

These functions must receive the current bound type first, by pointer or reference. UObject normally uses pointers; structs normally use references.

```cpp
// METHOD_TRIVIAL
FSphere_.Method("float32 GetVolume() const", METHOD_TRIVIAL(FSphere, GetVolume));

// METHODPR_TRIVIAL
FVector4f_.Method("FVector4f opSub(const FVector4f& Other) const", METHODPR_TRIVIAL(FVector4f, FVector4f, operator-, (const FVector4f&) const));

// function pointer
TOptional_.Method("void Reset()", &FAngelscriptOptionalBinds::Reset);

// lambada (there is a small issue here: UClass* has no const; it can still be bound, but it is less rigorous)
UClass_.Method("UClass GetSuperClass() const", [](UClass* Class) -> UClass*
{
	return Class->GetSuperClass();
});
```

```cpp
FSphere_.Method("FSphere opAdd(const FSphere& Other) const", METHODPR_TRIVIAL(FSphere, FSphere, operator+, (const FSphere&) const));
FSphere_.Method("FSphere& opAddAssign(const FSphere& Other)", METHODPR_TRIVIAL(FSphere&, FSphere, operator+=, (const FSphere&)));
```

# UENUM

See Bind_WorldType, Bind_NetMode and Bind_AsyncTraceType:

```cpp
AS_FORCE_LINK const FAngelscriptBinds::FBind Bind_WorldType((int32)FAngelscriptBinds::EOrder::Early, []
{
    auto WorldType_ = FAngelscriptBinds::Enum("EWorldType");
    WorldType_["None"]       = EWorldType::None;
    WorldType_["Game"]       = EWorldType::Game;
    WorldType_["Editor"]      = EWorldType::Editor;
    WorldType_["PIE"]        = EWorldType::PIE;
    WorldType_["EditorPreview"]    = EWorldType::EditorPreview;
    WorldType_["GamePreview"]  = EWorldType::GamePreview;
    WorldType_["GameRPC"]     = EWorldType::GameRPC;
    WorldType_["Inactive"]    = EWorldType::Inactive;
});

AS_FORCE_LINK const FAngelscriptBinds::FBind Bind_NetMode((int32)FAngelscriptBinds::EOrder::Early, []
{
    auto NetMode_ = FAngelscriptBinds::Enum("ENetMode");
    NetMode_["NM_Client"] = ENetMode::NM_Client;
    NetMode_["NM_DedicatedServer"] = ENetMode::NM_DedicatedServer;
    NetMode_["NM_ListenServer"] = ENetMode::NM_ListenServer;
    NetMode_["NM_Standalone"] = ENetMode::NM_Standalone;
    NetMode_["NM_MAX"] = ENetMode::NM_MAX;
});

AS_FORCE_LINK const FAngelscriptBinds::FBind Bind_AsyncTraceType((int32)FAngelscriptBinds::EOrder::Early, []
{
    auto TraceType_ = FAngelscriptBinds::Enum("EAsyncTraceType");
    TraceType_["Test"]  = EAsyncTraceType::Test;
    TraceType_["Single"] = EAsyncTraceType::Single;
    TraceType_["Multi"]     = EAsyncTraceType::Multi;
});
```

# USTRUCT

A struct with Blueprint-usable members or Blueprint visibility normally binds automatically.
For USTRUCT types not exposed to Blueprints, a very simple approach is changing metadata before AS registration, making them discoverable.

Here is a macro to call directly:

```cpp
// force bind UScriptStruct (Cpp)
// this runs (EOrder Early - 1) before Bind_BlueprintType_Declarations // add "ForceAngelscriptBind" as "" to USTRUCT
#define FORCE_BIND_USTRUCT(TypeToBind) \
AS_FORCE_LINK const FAngelscriptBinds::FBind ForceBoundUStruct_##TypeToBind((int32)FAngelscriptBinds::EOrder::Early - 1, []\
{\
    UField* Field = TypeToBind::StaticStruct();\
    Field->SetMetaData(TEXT("ForceAngelscriptBind"), TEXT(""));\
});
```

To bind a USTRUCT-marked type, write one line in a Cpp file and handle includes yourself:

```cpp
FORCE_BIND_USTRUCT(FTestStruct)
```

Could UPROPERTY metadata be changed at this stage too?
Yes. This is one way to bind partly exposed fields, such as those editable in the panel but inaccessible to Blueprint modification.

# UCLASS

Likewise, add metadata to an unbound UCLASS and let the AS system register it:

```cpp
// force bind UClass (Cpp)
// this runs  (EOrder Early - 1) before Bind_StructDeclarations
// add "BlueprintType" as "true" to UCLASS
#define FORCE_BIND_UCLASS(TypeToBind)\
AS_FORCE_LINK const FAngelscriptBinds::FBind ForceBoundUClass_##TypeToBind((int32)FAngelscriptBinds::EOrder::Early - 1, []\
{\
    UField* Field = TypeToBind::StaticClass();\
    Field->SetMetaData(TEXT("BlueprintType"), TEXT("true"));\
});
```

Usage:

```cpp
FORCE_BIND_UCLASS(FTestClass)
```

# Plain struct

This needs the most registration work, probably the hardest type after templates.

One trick is creating a BlueprintType USTRUCT so AS registers it automatically, then manually adding methods and members. I will follow the normal full process here instead.

Take FObjectKey as the example.

- Create an FAngelscriptType.
  Usually derive from `TAngelscriptCppType<NativeType>` and override methods.
  These two overrides normally name the type in Angelscript and Cpp, usually identically.

```cpp

struct FAngelscriptType_FObjectKey : TAngelscriptCppType<FObjectKey>
{
	FString GetAngelscriptTypeName() const override { return TEXT("FObjectKey"); }

	bool GetCppForm(const FAngelscriptTypeUsage& Usage, FCppForm& OutCppForm) const override
	{
		OutCppForm.CppType = GetAngelscriptTypeName();
		return true;
	}
};
```

- Create a global FAngelscriptBinds::FBind for declarations.
  Usually near Early.
  Associate FAngelscriptType at declaration time.
  SetTypeUserData if needed; not here.

For POD types, set the corresponding Flags so AS handles them more directly and efficiently. If unsure, simply use false.

```cpp
AS_FORCE_LINK FAngelscriptBinds::FBind Bind_FObjectKey_Declaration(
	static_cast<int32>(FAngelscriptBinds::EOrder::Early) + 1, []
	{
		FBindFlags Flags;
		Flags.bPOD = false;
		FAngelscriptBinds ThisBind = FAngelscriptBinds::ValueClass<FObjectKey>("FObjectKey", Flags);
		auto AngelscriptType_FObjectKey = MakeShared<FAngelscriptType_FObjectKey>();
		FAngelscriptType::Register(AngelscriptType_FObjectKey);
	});
```

- Create a global FAngelscriptBinds::FBind for members and functions.
  Usually at or after Late.
  Bind a default constructor if none exists, otherwise AS cannot directly declare an instance.

```cpp
AS_FORCE_LINK FAngelscriptBinds::FBind Bind_ObjectKey((int32)FAngelscriptBinds::EOrder::Late + 100,[]
{
    FAngelscriptBinds ThisBind = FAngelscriptBinds::ExistingClass("FObjectKey");

    ThisBind.Constructor("void f()" , [](FObjectKey* Address)
    {
       new(Address) FObjectKey();
    });
    FAngelscriptBinds::SetPreviousBindNoDiscard(true);
    SCRIPT_TRIVIAL_NATIVE_CONSTRUCTOR(ThisBind, "FObjectKey");

    ThisBind.Constructor("void f(const FObjectKey& Other)" , [](FObjectKey* Address, const FObjectKey& Other)
    {
       new(Address) FObjectKey(Other);
    });
    FAngelscriptBinds::SetPreviousBindNoDiscard(true);
    SCRIPT_TRIVIAL_NATIVE_CONSTRUCTOR(ThisBind, "FObjectKey");

    ThisBind.Constructor("void f(const UObject Object)" , [](FObjectKey* Address, const UObject& Object)
    {
       new(Address) FObjectKey(&Object);
    });
    FAngelscriptBinds::SetPreviousBindNoDiscard(true);
    SCRIPT_TRIVIAL_NATIVE_CONSTRUCTOR(ThisBind, "FObjectKey");

    ThisBind.Method("bool opAssign(const FObjectKey& Other) const", []( FObjectKey& Address, const FObjectKey& Other)
    {
       return Address = Other;
    });

    ThisBind.Method("bool opEquals(const FObjectKey& Other) const", [](const FObjectKey& Address, const FObjectKey& Other)
    {
       return Address.operator==(Other);
    });
    ThisBind.Method("bool opNotEquals(const FObjectKey& Other) const", [](const FObjectKey& Address, const FObjectKey& Other)
    {
       return Address.operator!=(Other);
    });

    ThisBind.Method("int opCmp(const FObjectKey& Other) const", [](const FObjectKey& Address, const FObjectKey& Other)
    {
       if (Address.operator< (Other)) return -1;
       if (Address.operator> (Other)) return 1;
       return 0;
    });

    ThisBind.Method("UObject ResolveObjectPtr() const", METHOD_TRIVIAL(FObjectKey, ResolveObjectPtr));
    SCRIPT_BIND_DOCUMENTATION(
       "Attempt to access the object from which this key was constructed.\n"
       "Returns:The object used to construct this key, or nullptr if it is no longer valid\n");

    ThisBind.Method("UObject ResolveObjectPtrEvenIfGarbage() const", METHOD_TRIVIAL(FObjectKey, ResolveObjectPtrEvenIfGarbage));
    SCRIPT_BIND_DOCUMENTATION(
    "Attempt to access the object from which this key was constructed, even if it is marked as Garbage.\n"
    "Returns:The object used to construct this key, or nullptr if it is no longer valid\n");

    ThisBind.Method("UObject ResolveObjectPtrEvenIfUnreachable() const", METHOD_TRIVIAL(FObjectKey, ResolveObjectPtrEvenIfUnreachable));
    SCRIPT_BIND_DOCUMENTATION(
    "Attempt to access the object from which this key was constructed, even if it is RF_PendingKill or RF_Unreachable\n"
    "Returns:The object used to construct this key, or nullptr if it is no longer valid\n");

});
```

This example has several constructors and methods but no member functions. Follow the existing patterns to bind them.

Constructors use placement new to construct at the supplied address.

With a lambda binding, its first argument corresponds to the native Cpp type. Structs normally use a reference, such as `const FObjectKey& Address`, but a pointer works too. Constness should match the function, although omitting const does not necessarily fail. Why? The lambda is a Cpp symbol; either form can represent the same memory. Still, follow conventions to keep mistakes easier to diagnose.

## Returning a base pointer from a native struct subclass

Bound structs do not inherit Cpp inheritance relationships. Write an explicit conversion:

```cpp
struct FComponentQueryParams : public FCollisionQueryParams

ThisBind.Method("FCollisionQueryParams& ToParent()",[](FComponentQueryParams& Self) -> FCollisionQueryParams&
{
    return Self;  // return a reference to the parent part directly
});
```

# Operators

opAssign binds assignment. It generally accompanies copy construction: provide both or neither.

opEquals, opNotEquals and opCmp bind comparisons. opCmp covers equality and inequality too, but explicit opEquals and opNotEquals take precedence. Its int result is compared against zero to determine ordering.

opCmp:

- **Negative result**: current object is less than the other, `<`.
- **Zero**: equal, `==`.
- **Positive**: greater, `>`.

All available operator-binding names are listed here:

https://www.angelcode.com/angelscript/sdk/docs/manual/doc_script_class_ops.html

Mixins can bind operators too; use these names and their required forms.

For example:

```cpp
UCLASS(Meta = (ScriptMixin = "FUIExtensionHandle"))
class  UUIExtensionHandle_MixinLibrary : public UObject
{
    GENERATED_BODY()

public:
	UFUNCTION(ScriptCallable)
	static bool opEquals(const FUIExtensionHandle& UIExtensionHandle, const FUIExtensionHandle& Other)
	{
	    return UIExtensionHandle == Other;
	}

	UFUNCTION(ScriptCallable)
	static bool opNotEquals(const FUIExtensionHandle& UIExtensionHandle, const FUIExtensionHandle& Other)
	{
	    return UIExtensionHandle != Other;
	}
};
```

# Global variables

Simple enough; follow this example:

```cpp
AS_FORCE_LINK FAngelscriptBinds::FBind Bind_FComponentQueryParams((int32)FAngelscriptBinds::EOrder::Late + 999,[]
{
	FAngelscriptBinds ThisBind = FAngelscriptBinds::ValueClass<FComponentQueryParams>("FComponentQueryParams", FBindFlags());

	{
		FAngelscriptBinds::FNamespace ns("FComponentQueryParams");
		FAngelscriptBinds::BindGlobalVariable("const FComponentQueryParams DefaultComponentQueryParams", &FComponentQueryParams::DefaultComponentQueryParams);
	}
});
```

# Global functions

Again, follow this example:

```cpp
AS_FORCE_LINK const FAngelscriptBinds::FBind Bind_FGAAddonBinds((int32)FAngelscriptBinds::EOrder::Normal, []
{
    FAngelscriptBinds::FNamespace ns("GA");
    FAngelscriptBinds::BindGlobalFunction(
      "FGameplayAbilityTargetDataHandle TakeOwnershipOfTargetData(const FGameplayAbilityTargetDataHandle& InData)",
       FUNC(FGAAddonBinds::TakeOwnershipOfTargetData));
    FAngelscriptBinds::SetPreviousBindArgumentDeterminesOutputType(0);
});
```

# Prerequisites for generic binding

## Finding Cpp content bound into AS

Follow FAngelscriptBinds::FAngelscriptBinds to a DataBase holding Cpp-to-AS bindings. Add information there if it is insufficient.

```cpp

void FAngelscriptType::Register(TSharedRef<FAngelscriptType> Type)

// every binding from cpp to AS goes through this function
FAngelscriptBinds::FAngelscriptBinds(FBindString Name, int32 Flags, int32 Size)

// for example, you could add some data structures you want in this function
static TMap<int, FName> TypeId_BindName;
static TMap<int, FName> BindName_TypeId;
```

## Identifying an AS type precisely

This goes deeper and underpins generic binding.

### Primitive types

Primitives such as bool and int each have a unique FAngelscriptType.

Their TypeIds are fixed:

```cpp
asTYPEID_VOID           = 0,
asTYPEID_BOOL           = 1,
asTYPEID_INT8           = 2,
asTYPEID_INT16          = 3,
asTYPEID_INT32          = 4,
asTYPEID_INT64          = 5,
asTYPEID_UINT8          = 6,
asTYPEID_UINT16         = 7,
asTYPEID_UINT32         = 8,
asTYPEID_UINT64         = 9,
asTYPEID_FLOAT32          = 10,
asTYPEID_FLOAT64         = 11,

asTYPEID_LAST_PRIMITIVE  = asTYPEID_FLOAT64,
```

Their TypeNames are fixed too:

```cpp
case asTYPEID_BOOL: Usage.Type = FAngelscriptType::GetByAngelscriptTypeName(TEXT("bool")); break;
case asTYPEID_INT8: Usage.Type = FAngelscriptType::GetByAngelscriptTypeName(TEXT("int8")); break;
case asTYPEID_INT16: Usage.Type = FAngelscriptType::GetByAngelscriptTypeName(TEXT("int16")); break;
case asTYPEID_INT32: Usage.Type = FAngelscriptType::GetByAngelscriptTypeName(TEXT("int")); break;
case asTYPEID_INT64: Usage.Type = FAngelscriptType::GetByAngelscriptTypeName(TEXT("int64")); break;
case asTYPEID_UINT8: Usage.Type = FAngelscriptType::GetByAngelscriptTypeName(TEXT("uint8")); break;
case asTYPEID_UINT16: Usage.Type = FAngelscriptType::GetByAngelscriptTypeName(TEXT("uint16")); break;
case asTYPEID_UINT32: Usage.Type = FAngelscriptType::GetByAngelscriptTypeName(TEXT("uint")); break;
case asTYPEID_UINT64: Usage.Type = FAngelscriptType::GetByAngelscriptTypeName(TEXT("uint64")); break;
case asTYPEID_FLOAT32: Usage.Type = FAngelscriptType::GetByAngelscriptTypeName(TEXT("float32")); break;
case asTYPEID_FLOAT64: Usage.Type = FAngelscriptType::GetByAngelscriptTypeName(TEXT("float64")); break;
```

### Script-declared types

These do not map one-to-one. One FAngelscriptType represents several types, so that description alone cannot distinguish them. Usage can.

```cpp
UObject maps to FAngelscriptType::GetScriptStruct()

delegate maps to FAngelscriptType::GetScriptDelegate()
event maps to FAngelscriptType::GetScriptMulticastDelegate()

UScriptStruct maps to FAngelscriptType::GetScriptStruct()
UEnum maps to FAngelscriptType::GetScriptEnum()
```

This function handles script types separately:

```cpp
FAngelscriptTypeUsage FAngelscriptTypeUsage::FromTypeId(int32 TypeId)
```

Usage.Type is one of the forms above.
The actual script type data lives in `Usage.ScriptClass`.

### Cpp-bound types

```
Usage.Type = FAngelscriptType::GetByAngelscriptTypeName(ANSI_TO_TCHAR(ScriptType->GetName()));
Usage.ScriptClass = ScriptType;
```

Only Cpp-bound types have templates and subtypes. Their ScriptType information goes into Usage:

```cpp
// Add type usage for template subtypes
if (ScriptType->flags & asOBJ_VALUE)
{
    asCObjectType* ObjectType = (asCObjectType*)ScriptType;
    for (int32 i = 0, SubTypeCount = ObjectType->templateSubTypes.GetLength(); i < SubTypeCount; ++i)
    {
       FAngelscriptTypeUsage SubTypeUsage = FAngelscriptTypeUsage::FromDataType(ObjectType->templateSubTypes[i]);
       if (!SubTypeUsage.IsValid())
       {
          Usage.Type = nullptr;
          Usage.SubTypes.Empty();
          break;
       }

       Usage.SubTypes.Add(MoveTemp(SubTypeUsage));
    }
}
```

UASClass stores AS type information:

```cpp
Usage.ScriptClass = (asITypeInfo*)ASClass->ScriptTypePtr;

Usage.ScriptClass = (asITypeInfo*)ASStruct->ScriptType;
```

### A quick wrap-up

Looking deeply at FAngelscriptType raises a question: why are script-declared types grouped under a few shared FAngelscriptTypes instead of one unique description per type?

Scattered code like this shows that script UObjects share one FAngelscriptType. That alone sometimes cannot identify the concrete type. FAngelscriptTypeUsage matters because it can store asCTypeInfo, which identifies the concrete script type.

```cpp
virtual FString GetAngelscriptTypeName() const override
{
    ensure(Class != nullptr);
    return ClassName;
}

FAngelscriptTypeUsage FAngelscriptTypeUsage::FromTypeId(int32 TypeId)
// there is a line
// Script objects use a specialized type that isn't in the normal by-name map


// Register a type that handles script object types generically
auto ScriptObjectType = MakeShared<FUObjectType>(nullptr, TEXT("UObject"));
FAngelscriptType::SetScriptObject(ScriptObjectType);
```

Each TypeId has one asCTypeInfo, except primitives.
Each bound Cpp type has one FAngelscriptType, but not the reverse.

```cpp
asCTypeInfo* ScriptType = (asCTypeInfo*)Manager.Engine->GetTypeInfoById(TypeId);
```

After plenty of analysis and experiments, the conclusions are:

- TypeId and type name
  Every type has a unique TypeId, so it can identify any AS type. Duplicate names are forbidden, making names one-to-one identifiers too.

- asCTypeInfo
  Identifies every non-primitive type.

- FAngelscriptTypeUsage
  Built from TypeId and capable of storing asCTypeInfo, it can represent every type too.

- FAngelscriptType
  Represents Cpp-bound types individually, but maps one-to-many for script types.

# Generic functions

### Generic parameters: question-mark binding

Here is a useful function returning any input’s AS type name.

The question mark resembles a Cpp template parameter.
One `?` in the AS signature corresponds to two native arguments: the data pointer and its TypeId. With those, Cpp knows what it needs to perform the operation.

TypeId precisely identifies a type. One useful tool retrieves asCTypeInfo and then its name; that works only for non-primitive types.

Another is FAngelscriptTypeUsage, which supplies the name, size, alignment and more. It is useful for operating on UE objects.

Much of the earlier generic-binding discussion concerns relationships between these descriptions. Sort them out to use them comfortably.

```cpp
FName UReflectLibrary::GetTypeName(void*, int TypeId)
{
    if (TypeId < 0) return NAME_None;
    const asCScriptEngine* Engine = FAngelscriptManager::Get().Engine;
    if (TypeId > asTYPEID_LAST_PRIMITIVE)
    {
       asCTypeInfo* Info = (asCTypeInfo*)Engine->GetTypeInfoById(TypeId);
       if (!Info) return NAME_None;
          return Info->GetName();
    }
    //  For PRIMITIVE
    const FAngelscriptTypeUsage Usage = FAngelscriptTypeUsage::FromTypeId(TypeId);
    return FName(Usage.Type->GetAngelscriptTypeName(Usage));
}

// GetTypeName
FAngelscriptBinds::BindGlobalFunction("FName GetTypeName(const ?&in Anything)",&UReflectLibrary::GetTypeName);
SCRIPT_BIND_DOCUMENTATION("Get TypeName in Angelscript by input anything, not include subtype")
```

This simple function does not operate on the void pointer. For that, FAngelscriptTypeUsage is generally preferable because it wraps UE’s own tools and handles specific UE memory operations more reliably. Again, avoid manually manipulating memory for UE types such as USTRUCT. Problems usually come from mishandled construction or destruction.

Question-mark bindings accept const, &, in and out modifiers. I consider three forms useful and do not recommend the rest. Details:

```cpp
UEnum GetEnumFromValue(?&in EnumValue) // accepts any input (except const)

UEnum GetEnumFromValue(?&out EnumValue) // takes references only, not temporary values.

// the call below only works with ?&in; otherwise you have to define a variable first and pass it in
DssReflect::GetEnumFromValue(ETimelineDirection::Backward);

// to let it accept const input, write it like this
UEnum GetEnumFromValue(const ?&in EnumValue) // accepts any input (including const)
```

### General-purpose function binding: .GenericMethod

Study this example for usage. It binds multiple AS function forms to one generic native callback; below, several Delegate method forms share it.

Several AS signatures --> one general Cpp implementation.

```cpp
void CallSparseDelegate(asIScriptGeneric* InGeneric)
{
    asCGeneric* Generic = static_cast<asCGeneric*>(InGeneric);

    auto* Function = Generic->GetFunction();
    auto* Sig = (FBlueprintEventSignature*)Function->GetUserData();
    void* Object = Generic->GetObject();

    FSparseDelegate& ScriptDelegate = *(FSparseDelegate*)Object;
    if (!ScriptDelegate.IsBound())
       return;

    FScriptCall& Call = CurrentCall();
    for (int32 Arg = 0; Arg < Sig->ArgCount; ++Arg)
       Call.PushArgument<false>(Sig->Arguments[Arg], Generic->GetAddressOfArg(Arg));
    if (Sig->ReturnType.IsValid())
    {
       void* ReturnPtr = Generic->GetAddressOfReturnLocation();
       if (Sig->bInitReturn)
          Sig->ReturnType.ConstructValue(ReturnPtr);
       else if (Sig->bZeroReturnPtr)
          *(void**)ReturnPtr = nullptr;
       Call.PushArgument<false,false>(Sig->ReturnType, &ReturnPtr);
    }

    USparseDelegateFunction* SparseDelegateFunc = CastChecked<USparseDelegateFunction>(Sig->UnrealFunction);
    UObject* OwningObject = FSparseDelegateStorage::ResolveSparseOwner(ScriptDelegate, SparseDelegateFunc->OwningClassName, SparseDelegateFunc->DelegateName);
    FMulticastScriptDelegate* MulticastDelegate = FSparseDelegateStorage::GetMulticastDelegate(OwningObject, SparseDelegateFunc->DelegateName);
    if (MulticastDelegate != nullptr)
// ……
```

Source: Bind_Delegates.cpp: CallSparseDelegate (excerpt; remaining lines omitted).

### Remaining limitations

A generic function cannot return `?`. Sometimes a desired result must instead be passed as a reference parameter.

Extra binding code can make AS infer a return type from an input, but this workaround needs another parameter as a type reference.

# Generic types

Basic binding already introduced some template registration.

This is much more complicated than generic functions. Those can sometimes be copied from examples without understanding memory deeply. Generic types, especially something like `TOptional<>`, cannot.

One point must be clear: AS has concrete types, not true generics. What we call a generic is a container! Anything with subtypes is a container, and the main container type is what we call the generic.

An AS generic has one TypeId because one container type needs only one ID. Its subtypes can vary enormously. asCTypeInfo stores subtype information. UE-AS sometimes adds a dedicated descriptor for convenient subtype access and stores it in UserData.

To learn generic-type binding, study the plugin’s `TOptional<>` binding. It is a classic example.

I first explored generics for one-to-one smart- and raw-pointer APIs. Now I think raw pointers could sometimes map to `TOptional<>`, preserving empty states for non-UObjects, except member-pointer bindings. Smart pointers, especially TSharedPtr, remain necessary; I cannot find replacement APIs.

Controlling ownership or doing async and multithreaded operations in AS also needs TSharedPtr or related bound types. That is more of an enthusiast’s approach.

Most script usage does not need custom generic-type binding. Given the difficulty and limited need, I will omit it here.

---

For me, this article serves as an ordinary binding handbook.

---
