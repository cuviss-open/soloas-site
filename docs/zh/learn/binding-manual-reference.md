---
title: "UE_Angelscript 绑定篇——手工绑定 2 - 绑定手册"
order: 52
category: binding
---
# UE_Angelscript 绑定篇——手工绑定 2 - 绑定手册

这里先放个 Angelscript 官方文档链接。

https://www.angelcode.com/angelscript/sdk/docs/manual/index.html

部分内容与 [UE_Angelscript 绑定篇——手工绑定 1 - 基础理解](binding-manual-basics.md) 有所重复，权当强调一次，另外也是为了上下文更完整一点点。

# 基础原理

本节将阐述 AngelScript 与 C++ 在 Unreal 框架下绑定的本质原理与执行机制。

### 本质

**本质上绑定就是把“同一块内存地址”在 C++ 和 AngelScript 两边暴露出来，但在两边它们可以有不同的名字或标识符。** 这使得 C++ 与 AS 在不同层语义下共享同一内存语义，实现零拷贝的类型映射。

具体说：

- **内存地址**：是物理位置，不变。C++ 对象在内存里占一块空间，AS 绑定的引用或指针就是指向同一块地址。
- **C++ 层代号**：变量名、对象指针、迭代器等。
- **AS 层代号**：脚本里看到的名字（函数名、变量名、引用），可以和 C++ 不同。

### 映射方式

AS 自己的绑定系统要映射 CPP 与 AS 的变量名，需要两部分的内容，一个是符号 `Signature`, 另外一个是符号对应的指针（类指针、成员指针、函数指针、全局变量指针等）

这些绑定的信息，都必须声明在一个全局变量中，然后这个变量会依据顺序运行其中的 lambada，从而实现绑定。

举例如下：

```cpp
AS_FORCE_LINK const FAngelscriptBinds::FBind Bind_FColor(FAngelscriptBinds::EOrder::Late, []
{
	// 具体的绑定代码
});
```

- 其中 `AS_FORCE_LINK` 是一个宏，可以当作格式代码，都带上。

- `const FAngelscriptBinds::FBind` 是绑定类型，这个类型的作用就是初始化的时候，将其初始化的参数传给一个全局变量 `FAngelscriptBinds::GetBindArray()`，等到需要真正开始绑定的时候，调用 `FAngelscriptBinds::CallBinds()` 函数。

可以看到，这里用了构造函数来传值 --> 收集到全局变量中 --> 等待合适时机按顺序批量注册。

- `Bind_FColor` 不多说了，一个变量名而已，只要不重名，不重要，一般不会再用到它，不过建议还是写成 `Bind_`加上类型的方式，方便检索。

我个人喜欢写类型的全名，不要去掉 F 之类的前缀。

- `FAngelscriptBinds::EOrder::Late` 是绑定顺序，顺序很重要，特别是依赖于其他绑定内容的时候，顺序出错就绑定不上了。

这个绑定顺序是可以自己改的，它底层就是 -100，0，100，可以强转为 int32，然后自由地更改顺序。当然直接输入数字也是可以的，因为 FAngelscriptBinds::FBind 本来就是支持输入 int32 当作参数的。

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

这里还值得强调的是，可以将声明的绑定和函数的绑定分开，好处是当此绑定类型的成员或者函数依赖于其他绑定类型的时候，不用怎么考虑绑定先后的顺序。

个人建议是 `Early` 前后绑定声明，`Normal` 或者 `Late` 前后绑定依赖于其他类型的内容。
因为分开绑定了，那么绑定声明的变量可以加后缀为 `_Declaration`，另外一个绑定就正常起名即可。

执行流程可简单总结为：

1. 通过全局构造收集绑定 →
2. 延迟执行注册函数 →
3. 注册类型信息 →
4. 建立映射关系。

- 具体的绑定代码，下文详解。

# 基础绑定

### 绑定声明

需要一个具体的类型，尖括号里的就是类型，然后一个 AS 里的类型名。

不管 CPP 里叫什么名，AS 里可以取一样的名，也可以是不一样的，设置可以将 CPP 里不是模板的类型，在 AS 解释为模板的形式。

关于 AS 模板里 `T` 的类型，是在后续 AS 里用的时候才进行解释的，用的时候，AS 会将具体的 `T` 的类型返回来，然后调用绑定里的回调函数： `TemplateCallback`,这个回调给了你判断类型是否合理的机会，也能进行其他的操作。

总而言之，绑定声明的阶段，只是告诉 AS 我这里有叫做 XXX 的类型，其内存布局是这样的，至于 CPP 里的名称叫什么，AS 并不关心，输入这个 CPP 的类型，只是为了确定内存布局。

```cpp
auto FBox_ = FAngelscriptBinds::ValueClass<FBox>("FBox", Flags);

// if template
FBindFlags ItFlags;
ItFlags.bTemplate = true;
ItFlags.TemplateType = "<T>";
auto TArrayIterator_ = FAngelscriptBinds::ValueClass<FArrayIterator>("TArrayIterator<class T>", ItFlags);
```

一旦声明过后，就可以这么直接找到这个绑定：

```cpp
auto FBox_ = FAngelscriptBinds::ExistingClass("FBox");

// if template
auto TArrayIterator_ = FAngelscriptBinds::ExistingClass("TArrayIterator<T>");
```

以下代码，可以验证到，CPP 的变量名，仅仅是用于确定内存布局信息。

- `alignof` 返回某个类型的**对齐要求**（alignment requirement），即该类型的对象在内存中必须放在的地址倍数。
- `sizeof` 返回一个类型或对象所占用的内存大小（以字节为单位）。
- 模板函数 `asGetTypeTraits<T>()` 的作用，其实就是**把 C++ 类型 `T` 的特性（构造/析构/赋值/拷贝等）转换成 AngelScript 运行时需要的 flag**，从而告诉 AngelScript 如何管理这个类型在脚本里的生命周期。

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

如果有些类型的大小是可变的，怎么办？比如 TOptional 是持有值的，会根据值具体的类型而变化大小，那么此时就需在绑定的时候增加 FLags，同时调用 TemplateSizeCalculatorFunctions 来告诉 AS 这个类型的大小是怎么确定的。

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

### 类型信息的关联

这里涉及到一个 叫做 FAngelscriptType 的类型，此类型如下所示，是设计用来做中间商的。

为什么需要这个类型呢？

UE 本身有类型描述，比如 UClass，而 AS 自身有 asITypeInfo，asITypeInfo 里有一个 plainUserData 可以存 UE 的类型描述，比如存 UClass。二者可以关联起来，类型信息相当的全面了。

但是吧，如果还有其他类型信息，该放在哪里呢？比如这个类型是不是当作 UProperty、是不是可以放进模板里、是不是可以排序等等好多信息。

这个时候，就创造了一个 FAngelscriptType 来描述了。FAngelscriptType 没有成员，全是成员函数，供子类实现。

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

当然子类会有成员，比如常见的类型 UCLASS 和 USTRUCT

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

类型描述是有了，类型使用的时候，具体是怎么用的，比如是否有 const、是否是引用等，然后又创造了一个类用于描述具体的使用情况。

这个类拥有几个成员，都是类型使用的关键，还描述了内部类型的情况（容器也是一种类型， SubTypes 大于 0，那么就是容器类型了）。

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

这个 FAngelscriptTypeUsage 有多种构造方式，常用的有 FromTypeId，FromProperty，FromClass，FromStruct；
（其中 FromClass，FromStruct 是从全局变量 `FAngelscriptTypeDatabase::Get()` 里尝试获取其对应的 FAngelscriptType，如果获取不到，会从 UASClass 或者 UASStruct 获取信息。）

FromTypeId 相当有用，特别是绑定泛型函数的时候。

回到类型信息的绑定话题上，举个例子如下

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

FAngelscriptType::Register 函数是将类型添加到两个全局变量中

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

这里的 TypesByAngelscriptName 是 TMap，可以快速根据类型名找到类型描述信息。
其他的还会根据不同的情况，将信息注册给不同的全局变量。

FAngelscriptType::RegisterTypeFinder 函数是将 FProperty 与 FAngelscriptTypeUsage 关联起来的查找器，可根据 UProperties 创建返回 FAngelscriptTypeUsage，对于可放置于 UProperties 下的容器类型或者指针类型，比如 TMap 、TSubclassOf 等，很是有用的。

FAngelscriptTypeUsage::FromProperty 函数就是根据 TypeFinders 来创建 FAngelscriptTypeUsage 的。此函数如果根据 TypeFinders 找不到，还会查询 TypesImplementingProperties，逐个匹配，这会调用 FAngelscriptType::MatchesProperty。
FAngelscriptType 的类型关联作用在这里又凸显了。
比如以下函数的覆写，就是 FUInt8Type 类型的匹配。

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

### 自定义类型信息的注入

为了方便操作 AS 的类型，很多时候都要给这个 AS 的类型附加额外信息，这些额外信息有专门的指针供存储。

那么我们是什么时候注入 AS 里的类型中的呢？

在函数声明中，比如调用了 FAngelscriptBinds::ValueClass，最终会调用到以下的代码

```cpp
int TypeId = Manager.Engine->RegisterObjectType(ClassName.ToCString(), Size, Flags);

asITypeInfo* ScriptType = Manager.Engine->GetTypeInfoByName(ClassName.ToCString());
```

FAngelscriptBinds 类型里存了 `asITypeInfo* ScriptType;`，ScriptType 就是 AS 的类型信息元数据。

asITypeInfo 只有一个子类 asCTypeInfo， asCTypeInfo 中可以存储自定义的信息，比如可以用来存些反射用的元数据。UE 中的 UObject\* 类型就存了 UClass\* 指针。

```cpp
// User data
void *SetUserData(void *data, asPWORD type);
void *GetUserData() const { return (void*)plainUserData; }
```

注意，此时 AS 的这个 asITypeInfo 还没有存入我们自定义的 UserData。

接下来就看看有哪些方式存入 UserData 吧，其实就两种，普通类型在绑定的时候就可以直接存，而模板类型的在推断出类型的时候存。

- 1，普通类型

在绑定的类型的时候，直接就设置了 UserData

```cpp
auto FVector_ = FAngelscriptBinds::ValueClass<FVector>("FVector", Flags);
FVector_.SetTypeUserData(TBaseStructure<FVector>::Get());
```

有些稍微绕一点而已：

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

出处：Bind_BlueprintType.cpp: Bind_BlueprintType_Declarations（节选，其余行省略）。

2，模板类型

对于模板类型来说，需要用 Callback 的方式确定类型信息，Callback 的时候再将自定义数据写入类型中。

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

出处：Bind_TOptional.cpp: Bind_TOptional（节选，其余行省略）。

### 构造函数

#### 普通类型

构造函数一般的单独写的，相对于普通成员函数不一样。

```cpp
FVector_.Constructor("void f(float64 X, float64 Y, float64 Z)", [](FVector* Address, double X, double Y, double Z)
{
    new(Address) FVector(X, Y, Z);
});
FAngelscriptBinds::SetPreviousBindNoDiscard(true);
SCRIPT_TRIVIAL_NATIVE_CONSTRUCTOR(FVector_, "FVector");
```

- Constructor 函数

函数的参数很简单，就是字符串+函数指针，其中函数的参数要求第一个变量是 `AS 类型`对应的 `CPP 类型`的指针或者引用。
函数内部的写法是 placement new 的写法，这例子中，意思是直接在**已有的地址 `Address`** 上调用 `FVector` 的构造函数。

其最终调用到 AS Engine 的 RegisterObjectBehaviour 函数，将这个对象的行为注册为 asBEHAVE_CONSTRUCT ，让其在 AS 里可以当作构造函数的形式来写。

有个 OnBind 的函数，是用来给缓存当前 FunctionId 到一个 PreviouslyBoundFunction 的变量中，这样后续的绑定操作就可以识别到前一个函数，从而给其增加信息，比如增加函数的注释。

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
  类似于 C++ 的 `[[nodiscard]]`，意思是不要忽略返回值。

- SCRIPT_TRIVIAL_NATIVE_CONSTRUCTOR 这个是处理预编译的，有好几个宏，有一个可以增加默认构造函数的参数，比如 ForceInit 在函数签名里没有，但是运行时加上了，这个时候就需要补充。

```cpp
FSphere_.Constructor("void f()", [](FSphere* Address)
{
    new(Address) FSphere(ForceInit);
});
FAngelscriptBinds::SetPreviousBindNoDiscard(true);
SCRIPT_TRIVIAL_NATIVE_CONSTRUCTOR_CUSTOMFORM(FSphere_, "FSphere", "ForceInit");
```

这个预编译可以加速运行时加载的速度，用一个全局表维护了信息。
其实可以不用过多理会细节，是构造函数，就可以附加上这个宏。没有这个，其实也问题不大，运行不会有问题。

```cpp
void FScriptFunctionNativeForm::BindNativeConstructor(FAngelscriptBinds& Binds, const ANSICHAR* Name, bool bTrivial, const ANSICHAR* CustomForm)
{
    if (!FAngelscriptManager::bGeneratePrecompiledData)
       return;
    GScriptNativeForms.Add(FAngelscriptBinds::GetPreviousBind(), new FScriptNativeConstructor(Name, bTrivial, CustomForm));
}
```

#### 模板类型

此部分内容，属于泛型绑定范畴，大多数人可以忽略掉。

```cpp
TOptional_.Constructor("void f()", &FAngelscriptOptionalBinds::Construct);
SCRIPT_NATIVE_TEMPLATED_CALL(TOptional_, "FAngelscriptOptionalBinds::Construct", false);
FAngelscriptBinds::PreviousBindPassScriptObjectTypeAsFirstParam();
```

SCRIPT_NATIVE_TEMPLATED_CALL 其会调用一个加上`_Template`的模板函数

```cpp
static void Construct(FAngelscriptOptional& Optional, asCObjectType* Meta);

template<typename T>
static void Construct_Template(TOptional<T>& Optional)
{
    new (&Optional) TOptional<T>();
}
```

这个函数的信息与之前提到的 SCRIPT_TRIVIAL_NATIVE_CONSTRUCTOR 宏一样保存在

```cpp
static TMap<asIScriptFunction*, FScriptFunctionNativeForm*> GScriptNativeForms;
```

为了什么呢——运行时加速访问，不写的话，也能运行。

- FAngelscriptBinds::PreviousBindPassScriptObjectTypeAsFirstParam()

  这个函数是给刚才绑定的函数注入一个当前绑定类型对应的 `asCObjectType*` 作为第一个参数（绑定的函数的写法格式，默认第一个是绑定类型本身，所以，此处会在写法格式上写在第二位），通过这个 `asCObjectType*` 我们可以访问到类型的很多信息，特别是我们之前存进去的 UserData 。

示例：构造的时候，直接获取类型的信息，然后进行类型相关的操作。

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

#### 小结

光是构造函数，其实已经很多细节需要注意了，但是如果只是使用而言，照猫画虎，还是容易的。

有些类型如果没有绑定构造函数，那么 AS 里就不能主动构造它。这种情况也是有的，有时候是特意而为之，只能从某些函数——比如工厂函数的调用中得到。

### 类成员

通过 .Property 方法，两个参数，一个是字符串，一个是成员指针。

```cpp
FSphere_.Property("float64 W", &FSphere::W);
```

这里需要注意，float 类型在 AS 里都是 float32; double 类型则对应为 float64，绑定的时候需要注意，容易疏漏。

类成员不支持 BitField（位域） 类型的，因为无法正常的取地址，这在 UE 里有不少，因为 UE 为了节省内存，有些参数就用 BitField 来表达了。这个时候绑定只好写 Get Set 函数了。

### 类函数

函数绑定用 .Method，前面参数是字符串，后面是函数指针。后面的参数，可以通过 METHOD_TRIVIAL 和 METHODPR_TRIVIAL 两个宏来快速书写。
如果有些自定义函数，可以写在其他地方，然后像成员函数那样的模式进行取地址，比如`&FAngelscriptOptionalBinds::Reset` 。
另外还可以直接输入 lambada 。

以上这些函数，第一个参数都必须是当前绑定的类型，或指针，或引用。（一般 UObject 用指针，struct 用引用。）

```cpp
// METHOD_TRIVIAL
FSphere_.Method("float32 GetVolume() const", METHOD_TRIVIAL(FSphere, GetVolume));

// METHODPR_TRIVIAL
FVector4f_.Method("FVector4f opSub(const FVector4f& Other) const", METHODPR_TRIVIAL(FVector4f, FVector4f, operator-, (const FVector4f&) const));

// function pointer
TOptional_.Method("void Reset()", &FAngelscriptOptionalBinds::Reset);

// lambada （这里有点小问题，UClass* 前没有加 const,虽然可以绑定，但是不那么严谨）
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

参考 Bind_WorldType Bind_NetMode 和 Bind_AsyncTraceType

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

只要其自身或者有成员可以被蓝图使用，就会默认进行绑定了。
如果是那些标记了 USTRUCT 但是没有暴露给蓝图的呢？这里提供一个超级简单的方式，在 AS 绑定代码运行之前，修改 USTRUCT 的 meta ，让其可以被识别绑定，那就好了。

我直接给一个宏，直接调用宏就可以了。

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

当你要绑定某个标记有 USTRUCT 的类型时，直接在某个 Cpp 文件里写一行就可以了（#include 文件自行解决）。

```cpp
FORCE_BIND_USTRUCT（FTestStruct)
```

有意思的一个问题，如果是标记了 UPROPERTY 成员，是不是也可以在这个时机修改 meta 来绑定呢？
当然可以了，这对于那些绑定了一半（只允许在面板里修改，限制蓝图修改）的参数来说，是可用的绑定方式之一。

# UCLASS

UCLASS 同理，没有被绑定的，可以添加 meta，然后让 AS 体系自动绑定。

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

使用方式

```cpp
FORCE_BIND_UCLASS（FTestClass)
```

# Plain struct

需要绑定最多的内容，这大概是除了模板类型之外，最麻烦的绑定类型了。

有个奇技淫巧是，新建一个 USTRUCT 并且标记为 BlueprintType，然后 AS 绑定系统就自动帮你注册好了，至于绑定成员和方法，就手动来。但是在这里不展示这种方式，而是按照正常流程来。

此处以 FObjectKey 为例。

- 创建一个 FAngelscriptType 类型
  一般是继承于 ` TAngelscriptCppType<NativeType>`，然后覆写一些函数。
  下方的这两个函数，一般都需要覆写的，直接指名了 Angelscript 里这个类型叫什么，以及 Cpp 里叫什么，一般这两个名是一样的。

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

- 创建一个 FAngelscriptBinds::FBind 全局变量用于绑定声明
  绑定顺序一般是在 Early 阶段附近。
  绑定声明的同时，将 FAngelscriptType 类型关联起来。
  SetTypeUserData 看情况是否设置（此处不设置）。

如果类型是 POD，可以设置 Flags 的，这样 AS 在处理这个类型的时候，会简单直接更高效点。当然如果不清楚是否应该设置为 POD，直接设置 false 就好了。

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

- 创建一个 FAngelscriptBinds::FBind 全局变量用于成员和函数
  绑定顺序一般是在 Late 阶段以后
  如果构造函数没有绑定，一般都要绑定一个默认构造函数，否则 Angelscript 里无法直接声明。

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

这个案例里，没有成员函数，有数个构造函数，还有一批方法。这些都是照猫画虎可以绑定的。

构造函数用到了 placenew，在给定地址上进行类型构造的意思。

在函数绑定中，如果是写 lambda 来绑定的，第一个参数默认是当前类型在 Cpp 里是什么。一般 struct 类型都写成引用的形式，比如 `const FObjectKey& Address`，但是你写成指针，也不会有问题，至于是否写 const , 原则上是要和函数对应起来的，但是你实在是要不写，它也不会出错。为什么如此？因为 lambda 是 Cpp 这边的符号而已，只要代表的是同一份内存，怎么写都可以的。当然，还是建议规规矩矩来写，否则，就不规范了，出问题也难检查。

## 原生 struct 子类如何返回父类指针

struct 绑定之后，是不认 cpp 里的继承关系的，如果想要使用转换，就需要自己写一个。

```cpp
struct FComponentQueryParams : public FCollisionQueryParams

ThisBind.Method("FCollisionQueryParams& ToParent()",[](FComponentQueryParams& Self) -> FCollisionQueryParams&
{
    return Self;  // 直接返回父类部分的引用
});
```

# 运算符

opAssign 是绑定赋值符号，一般和拷贝构造函数一起，要有都有，要没有就都没有。

opEquals 、 opNotEquals 和 opCmp 是绑定比较运算符。其中 opCmp 涵盖了 opEquals 、 opNotEquals， 如果 opEquals 、 opNotEquals 绑定了，会优先用 opEquals 、 opNotEquals。 opCmp 的绑定比较有意思，返回值的 int, 通过返回值与 0 的大小比较来得出大于等于小于。

opCmp：

- **返回值为负数**：当前对象小于比较对象（`<`）。
- **返回值为零**：当前对象等于比较对象（`==`）。
- **返回值为正数**：当前对象大于比较对象（`>`）。

能用的运算符对应的绑定方法名，都可以在这个页面找到。

https://www.angelcode.com/angelscript/sdk/docs/manual/doc_script_class_ops.html

注：Mixin 也支持这种运算符绑定，只要写这种方法名且按照其写法来就可以了。

例如：

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

# 全局变量

十分简单，直接参考：

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

# 全局函数

十分简单，直接参考：

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

# 泛型绑定前置知识

## 如何获取 Cpp 绑定到 AS 的内容

顺着 FAngelscriptBinds::FAngelscriptBinds 能找到一个 DataBase ，里面存有从 Cpp 绑定到 AS 的内容，如果不够用，可以在这个函数里增加一些。

```cpp

void FAngelscriptType::Register(TSharedRef<FAngelscriptType> Type)

// 所有从 cpp到 AS 的绑定都经过这个函数
FAngelscriptBinds::FAngelscriptBinds(FBindString Name, int32 Flags, int32 Size)

// 比如，可考虑在这个函数增加一些你想要的数据结构
static TMap<int, FName> TypeId_BindName;
static TMap<int, FName> BindName_TypeId;
```

## 如何精准定位一个 AS 的类型

此部分探索稍微深一些，是泛型绑定的基础。

### 基础类型

对应 bool int 等基础类型，有唯一的 FAngelscriptType 与之对应。

基础类型的 TypeId 是固定的

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

TypeName 也是固定的。

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

### 脚本里声明的类

脚本里的声明的类型，不是一对一的。是一个 FAngelscriptType 对应多个类型，因此这些 FAngelscriptType 并没有存在真正有用的类型信息来区分同样的类型，只有 Usage 才有可能区分开。

```cpp
UObject 对应 FAngelscriptType::GetScriptStruct()

delegate 对应 FAngelscriptType::GetScriptDelegate()
event 对应 FAngelscriptType::GetScriptMulticastDelegate()

UScriptStruct 对应 FAngelscriptType::GetScriptStruct()
UEnum 对应 FAngelscriptType::GetScriptEnum()
```

详细可在这个函数里看到，这个函数会对脚本里的类型进行单独处理。

```cpp
FAngelscriptTypeUsage FAngelscriptTypeUsage::FromTypeId(int32 TypeId)
```

Usage.Type 只有上面这几种。
这些脚本的类型，数据会存在 `Usage.ScriptClass` 了。

### cpp 绑定的类型

```
Usage.Type = FAngelscriptType::GetByAngelscriptTypeName(ANSI_TO_TCHAR(ScriptType->GetName()));
Usage.ScriptClass = ScriptType;
```

只有 Cpp 绑定的才有模板类型，然后才有子类型，会将 ScriptType 里的类型存进 Usage

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

UASClass 有字段存 AS 的类型信息

```cpp
Usage.ScriptClass = (asITypeInfo*)ASClass->ScriptTypePtr;

Usage.ScriptClass = (asITypeInfo*)ASStruct->ScriptType;
```

### 小结

如果深入分析 FAngelscriptType，可能会有个疑问：脚本里声明的类型，被统一的 FAngelscriptType 来管理了几大类型，而没有给它们每个都创建唯一的 FAngelscriptType。

通过一些零碎在各个地方的代码，如下，可以获知，脚本里的 UObject 类型就只有一种 FAngelscriptType 。这会导致一个问题，单纯依靠一个 FAngelscriptType 有时是得不到具体类型的。所以 FAngelscriptTypeUsage 的用处就大了，它可以存 asCTypeInfo， 然后才是能获取到具体的脚本类型。

```cpp
virtual FString GetAngelscriptTypeName() const override
{
    ensure(Class != nullptr);
    return ClassName;
}

FAngelscriptTypeUsage FAngelscriptTypeUsage::FromTypeId(int32 TypeId)
// 有一句
// Script objects use a specialized type that isn't in the normal by-name map


// Register a type that handles script object types generically
auto ScriptObjectType = MakeShared<FUObjectType>(nullptr, TEXT("UObject"));
FAngelscriptType::SetScriptObject(ScriptObjectType);
```

每个 TypeId 对应唯一一个 asCTypeInfo（基础类型除外）。
被绑定的 Cpp 类型对应唯一一个 FAngelscriptType，反过来不行。

```cpp
asCTypeInfo* ScriptType = (asCTypeInfo*)Manager.Engine->GetTypeInfoById(TypeId);
```

在进行很多分析与尝试后，我们有以下结论：

- TypeId 、类型名
  TypeId 是所有类型都有的，并且唯一，所以它才能代表 Angelscript 里所有的类型。因为 Angelscript 里不允许类型重名，所以类型名称也可以代表类型，且也是一对一。

- asCTypeInfo
  asCTypeInfo 能代表除了基础类型外的所有其他类型。

- FAngelscriptTypeUsage
  由输入 TypeId 而生成的 FAngelscriptTypeUsage，因为 TypeId 的缘故以及其自身可以存储 asCTypeInfo 的缘故，它也能代表所有类型。

- FAngelscriptType
  FAngelscriptType 可以代表 Cpp 绑定过去的类型，而脚本的类型就只能是一对多。

# 泛型函数

### 泛型参数绑定——问号绑定

以下给出一个有用的函数，在 AS 里获取任意输入内容的类型名称。

这里的绑定用到了问号，问号从观感上来看，有点类似于 Cpp 里的模板参数。
一个在 AS 函数签名里的问号，会对应于 Cpp 函数的两个内容，一个是内容所在的指针，一个是其 TypeId。有了指针和 TypeId，也就相当于知道了这个输入内容的一切，所以 Cpp 函数里就能执行计算了。

关于利用 TypeId，其可以精准定位一个类型，有两个工具挺好用的，一个是通过其获取 asCTypeInfo，然后 asCTypeInfo 里可以获取类型名，这个只能是非原生类型才能用。

另外一个工具是 FAngelscriptTypeUsage，其除了可以获取类型名外，还可以获取到类型的大小、对齐等各种各样的信息，是操作 UE 对象的高效工具。

之前提到了很多类型绑定的泛型相关的内容，重点都是这些类型信息之间的关系，只有理清楚了，才能用起来游刃有余。

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

这个函数相对简单，并没有对 void 指针进行操作，如果需要操作它，一般都是用 FAngelscriptTypeUsage 的工具比较好，因为 FAngelscriptTypeUsage 是封装了 UE 本身的工具，对 UE 中一些特定类型的内存操作比较稳当。再次强调，建议不要试图手工操作 UE 类型的内存，比如 USTRUCT ，发生了问题，一般都是没处理好构造和析构带来的。

关于问号的绑定，其有附加的 const & in out 等参数，有 3 种个人认为值得选用的，其余都不建议。详细情况如下：

```cpp
UEnum GetEnumFromValue(?&in EnumValue) // 可以接受任何的输入（不包括const)

UEnum GetEnumFromValue(?&out EnumValue) // 只能传引用，不能传临时的值。

// 下方的调用，只能是　?&in　才可以，　否则就需要先定义一变量再传入
DssReflect::GetEnumFromValue(ETimelineDirection::Backward);

// 要想让其可以接受const 的输入，需要这么
UEnum GetEnumFromValue(const ?&in EnumValue) // 可以接受任何的输入（包括const)
```

### 通用函数绑定—— .GenericMethod

可以研究以下示例得到使用方式，这种绑定方式的好处是——批量地绑定不同的函数给 AS，下方示例就是将多种 Delegate 的各种函数形式都绑定给 AS 了。

也就是说，多个 AS 里的函数签名--> Cpp 里只写一个通用的函数与之对应。

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

出处：Bind_Delegates.cpp: CallSparseDelegate（节选，其余行省略）。

### 泛型函数绑定遗留问题

泛型函数的返回值，不能写问号。这导致，有些时候，不能不将想要作为返回值的参数转为引用参数传入。

绑定时候可以通过附加代码，让 AS 引擎根据某个输入参数来决定返回的类型，这是一种变通的方法，但是需要多增加一个参数用来作为类型参考。

# 泛型类型

在基础绑定里，已经介绍了部分模板类型绑定的内容。

这个比泛型函数复杂等级高好多，之前的泛型绑定，在不理解内存逻辑的情况下，尚可照猫画虎，而泛型类型就不大行了，特别是复杂点的泛型，比如 `TOptional<>`。

需要明确一个事，AS 里没有真正的泛型，而只有一个个具体化的类型。所谓泛型，是一个容器！凡是拥有子类型的，都是容器，而容器本体，就是我们所说的泛型。

AS 里的泛型，只有一个 TypeId，因为它就是一个容器类型而已，分配一个 TypeId 就够了。但是这个类型的变化在于子类型可以千变万化，在 AS 中，asCTypeInfo 可以存储子类型的信息，而 UE-AS 脚本，一般为了方便调用，有时专门写一个类来维护子类型的情况，然后存入 asCTypeInfo 的 UserData 里。

如果想要学习绑定泛型类型的，建议参考脚本本身 `TOptional<>` 的绑定，这个写得十分经典。

之前我涉猎泛型类型的绑定，是为了智能指针和裸指针的 API 一对一，但是现在想想，裸指针也可以对应为 `TOptional<>`，那么非 UObject 的空状态绑定也是可以做到一对一（除了成员指针的绑定）； 但智能指针特别是 TSharedPtr 还是需要的，找不到 API 的替代品。

另外，如果要在 AS 里控制所有权，进行异步、多线程等操作，TSharedPtr 或者相关的绑定类型是必需品，当然这种情况是比较极客点的做法。

结论就是，泛型类型的绑定对于脚本的大多数使用情况而言，不需要。故限于难度以及大部分人并不需要这种绑定，所有本文略。

---

此文，于个人而言，权当普通的绑定手册使用。

---
