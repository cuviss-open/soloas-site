---
title: "UE_Angelscript 源码篇 1：UE 的类绑定到 AS 的流程"
order: 40
category: internals
---
# UE_Angelscript 源码篇 1：UE 的类绑定到 AS 的流程

UE-Angelscript 是 UE 的一个分支，内容主要包括两个方面：

1. 对 Unreal Engine 源码的修改；
2. UE-Angelscript 插件本身的实现。

本文侧重于 UE-Angelscript 插件本身的框架逻辑和关键信息。

以问题为导向，本篇回答的问题是：UE 的类是如何绑定到 Angelscript 的？

当然，本文限于篇幅，不能说明所有细节，读者就当看个大体架构吧。

或有理解错误，还望不吝赐教。

阅读条件——需有 C++ 、 UE 、Angelscript 的相关知识。
# 前言

## 对 UE 源码的修改

为了与 UE 一体化交互，HAZE 对 UE 源码修改了确实不少。

所有修改通常由如下注释包裹，便于快速定位：  
`// HAZE FIX`  
`// END HAZE FIX`  
可通过全局搜索定位修改区域。

此部分内容零零碎碎分散在各处，本文就不对其进行分析了。

## Angelscript 插件本身

UE-Angelscript 插件的核心内容在引擎目录下的 Plugins/Angelscript 里。
这里提一下，另外的插件 AngelscriptEnhancedInput、AngelscriptGAS、AngelscriptStructUtils 都是专门针对特定模块的绑定，不属于核心内容。

## **插件的模块结构**

从目录结构和构建脚本来看，插件主要分为以下几个部分，其中 `AngelscriptCode` 是运行时逻辑的核心模块，`AngelscriptEditor` 提供编辑器扩展，`AngelscriptLoader` 负责启动流程及模块间协作：

- **Source/AngelscriptCode**  
   主要负责核心脚本引擎的集成、脚本绑定、运行时逻辑等。
- **Source/AngelscriptEditor**  
   提供编辑器相关的扩展，如菜单、工具、编辑器命令等。
- **Source/AngelscriptLoader**  
   负责脚本的加载、初始化和与引擎的集成。
- **ThirdParty**  
   存放第三方依赖（主要是 AngelScript 源码和头文件）。

```
非编辑器模式
AngelscriptLoader ------> AngelscriptCode -------> AngelScript (3rd)

编辑器模式
AngelscriptLoader ------> AngelscriptEditor ------> AngelscriptCode -------> AngelScript (3rd)
```

## **简述 Angelscript 的引入**

Angelscript 是一个脚本语言，一般作为 C++ 的脚本辅助开发，性能很好，语法也类似 C++。

这门语言与 C++ 的交互十分方便，提供了简单易用的 API 和详细的可配置参数。在 C++ 端操作时，一般只需要 Include 一个头文件即可，即 angelscript.h 。

引入 angelscript 之后，UE-Angelscript 插件在不同的地方都对 angelscript 原始的一些方法和类进行了封装，这是为了更好地链接 Cpp 与 Angelscript 之间的代码（实际上是为了少写点重复代码）。

总体而言，Angelscript 提供了轻量、高性能的脚本扩展能力，适合嵌入到以 C++ 为核心的引擎中，从使用来看，UE- Angelscript 的集成确实高效且舒适。

# UE 的类绑定到 AS

先上一张完整的简化流程图。

```
以下为从 UE 启动到类型绑定的主要调用流程（简化版）：

+-----------------------------+
| UE 启动/插件被加载          |
+-----------------------------+
              |
              v
+-----------------------------+
| AngelscriptLoader 模块是入口 |
| void FAngelscriptLoaderModule::StartupModule() |
+-----------------------------+
              |
              v
+-----------------------------+
| AngelscriptCode 模块初始化不做其他事，有一批可被调用的函数，其中有独立的初始化函数 |
| FAngelscriptCodeModule::InitializeAngelscript() |
+-----------------------------+
              |
              v
+-----------------------------+
| 真正的初始化开始于此 |
| FAngelscriptManager::Initialize()  |
| 分三个流程为 |
| PreInitialize_GameThread、Initialize_AnyThread、PostInitialize_GameThread |
+-----------------------------+
              |
              v
+-----------------------------+
| 其中此函数包含有绑定所有类型的部分 |
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
| 绑定所有 FBinds |
| void FAngelscriptBinds::CallBinds()  |
+-----------------------------+
              |
              v
+-----------------------------+
| 按照 FBinds 的顺序，调用绑定的 Lambda|
|   GetBindArray().Sort();
	for (auto& Function : GetBindArray())
	    Function.Function();   |
+-----------------------------+
```

void FAngelscriptManager::PreInitialize_GameThread() 这个函数会创建两个UPackage：/Script/Angelscript  和 /Script/AngelscriptAssets，AS 代码的内容，就在 /Script/Angelscript 的 UPackage 里。PreInitialize阶段还会读取 UAngelscriptSettings 的用户设置，设置 Angelscript 虚拟机。

void FAngelscriptManager::Initialize_AnyThread() 这个函数是核心，本文分析的主要就是这个函数里包含的内容了。这里提一下的是，这个函数可以运行在非游戏线程。

void FAngelscriptManager::PostInitialize_GameThread() 只是提供了一个委托的回调，让外部知道初始化完成。
## 说明：UE 的类，都是通过 FBinds 的 Lambda 来绑定到 AS 的

Angelscript 插件通过 `FBinds` 构造器机制来绑定代码，每个绑定以 Lambda 的形式定义。

GetBindArray() 返回的单例会保存这所有的 Lambda，并且这些 Lambda 拥有顺序，会按照顺序来逐一运行 Lambda。

示例的 FBind 如下。

```cpp
AS_FORCE_LINK const FAngelscriptBinds::FBind Bind_AActor_Base((int32)FAngelscriptBinds::EOrder::Late-1, []
{
    auto AActor_ = FAngelscriptBinds::ExistingClass("AActor");
    // 略
});
```

这个变量每次初始化的时候，就会将内容注册到 GetBindArray() 里的单例了，所以，我们如果想将 Cpp 里的类型绑定到 AS ，只需要增加新的 FBind 变量即可。

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

出处：AngelscriptBinds.h: FAngelscriptBinds::FBind（节选，其余行省略）。

## 问题：UE 那么多类，如何批量处理？

UE 里需要给脚本使用的类，除了基础类型外，主要是进入反射系统的 UObject、UScriptStruct、UEnum、Delegate 这几种类型了。

其中，量最大的是 UObject、UScriptStruct。

这两个类型，AS 插件进行了批量化的处理。

刚才提到过，所有的绑定，都是通过 FBinds 的 Lambda 实现的。

绑定 UObject 的 FBinds 是这两个变量。

### Early 阶段绑定 UObject

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

其中调用的 BindUClass 函数，是主要的绑定函数。绑定好的类型，都会将信息保存在 FAngelscriptTypeDatabase 的单例中。

对于 UClass 的类型，这里特意将 angelscript 的类型和 UClass 关联起来，这样的好处是，AS 里不必区分 StaticClass 和类本身了。

拓展：此处利用了 `plainUserData`  —— AngelScript 引擎中为  **每个类型（`asCTypeInfo`）结构体上挂载的一个用户自定义指针字段**，你可以把它理解成： **“给这个脚本类型附加一个自定义的 C++ 指针，以便在 C++ 层可以反查或传参时用到”。**

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

这里再深入一层，提一提 FAngelscriptBinds::ReferenceClass 这个绑定 UObject 的专用函数。

```cpp
FAngelscriptBinds FAngelscriptBinds::ReferenceClass(FBindString Name, UClass* UnrealClass)
{
    auto Binds = FAngelscriptBinds(Name, asOBJ_REF | asOBJ_NOCOUNT | asOBJ_IMPLICIT_HANDLE, 0);
    ((asCObjectType*)Binds.ScriptType)->size = UnrealClass->GetStructureSize();
    Binds.ScriptType->alignment = UnrealClass->GetMinAlignment();
    return Binds;
}
```

asOBJ_REF: 表示这是引用类型（UObject\*）  
asOBJ_NOCOUNT: 不做引用计数（UE 自己管理生命周期）  
✅ asOBJ_IMPLICIT_HANDLE: 允许脚本使用时省略 @ （@在 AS 里是句柄的意思）

AS 的 UObject 实际上是 UObject@ ，对应于 C++ 里的 UObject\* ，所以 AS 的 UObject 可以为 nullptr。

BindUClassLookup 也是得提一提的，它是 AS 识别一些关于 UObjct 模板的关键。

Unreal Engine 常用的 UObject 指针相关模板类型，如 TSubclassOf 、TObjectPtr 、TWeakObjectPtr 、裸指针等，都可以在一个回调函数里处理，处理好之后将相关的信息存入 FAngelscriptTypeUsage 。

具体如下：
注册一个自定义类型查找器（RegisterTypeFinder），使 Angelscript 能够根据 Unreal 属性的具体类型动态推断绑定类型——是哪个模板类型，或者是裸指针；

FAngelscriptTypeDatabase 里 TArray<FAngelscriptType::FTypeFinder> TypeFinders 会保存回调函数的信息，这是给后续解释的时候调用的。

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
    // 略
    });
}
```

`BindUClassLookup` 比较难理解，它的作用再小结一下，就是注册一批特殊的模板包装类型（如 `TSubclassOf`、`TWeakObjectPtr`），并设置 AngelScript 在解析时能够正确识别这些包装器内部的 UObject 类型。

### `Late` 阶段绑定 UObject 成员和成员函数

之前完成了初始的 UObject 绑定，但是 UObject 里还有很多成员和成员函数，也是需要批量来处理的，这个被放到了更迟一些的绑定顺序了，为什么呢？因为这些成员和成员函数，又不是 UObject 的类型，这些还需要先行绑定了才能让 AS 找到。

排序的作用就是在于此了，一般都是在 Early 阶段绑定类型，之后在 Late 阶段绑定类型的成员和成员函数。

写在 Bind_BlueprintType.cpp

```cpp
AS_FORCE_LINK const FAngelscriptBinds::FBind Bind_Defaults((int32)FAngelscriptBinds::EOrder::Late+100,
// 略
```

这个绑定十分的长，因为要处理各种各样的情况，这是大致的绑定流程。

```cpp
遍历所有UClass
   │
   ├─► 递归收集父类，保证继承顺序
   │
   ├─► 绑定所有 BlueprintType/BlueprintCallable/ScriptCallable 的函数
   │
   ├─► 绑定 BlueprintGetter/Setter
   │
   ├─► 绑定所有蓝图可见/可编辑属性
   │
   ├─► 处理继承，复制父类属性/方法
   │
   ├─► 绑定 StaticClass 和全局变量
   │
   └─► 写入绑定数据库
```

### 绑定 UScriptStruct 及其成员

UScriptStruct 的绑定相对简单一些，因为没有成员函数能被反射系统识别的。

绑定的代码主要写在 Bind_UStruct.cpp ,绑定的写法类似于 UObject 。不再详细说那么多啦。

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

不过还是得提一下 UObject 的不同之处！
**UScriptStruct 被绑定为了值类型**

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

关于值类型的绑定函数，原代码如下，关键的是——
asOBJ_VALUE | asOBJ_APP_CLASS 表示“这是一个 C++ 定义的 struct/class，它是值类型”

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

绑定为值类型（举例`FVector`），可以直接声明一个变量，然后修改其中的成员，简单方便，无需工厂函数就直接生成实例。

```angelscript
FVector v(1, 2, 3);
v *= 2;
```

绑定为引用类型（举例`UObject`），如果直接声明一个变量，其会是 Nullptr，要生成实例，必须使用 NewObject 等工厂函数或者从别处获取一个实例。

```angelscript
UObject obj = GetSomeObject();
Print(obj.GetName());
```

BindStructTypeLookups 的函数简单不少，因为没有给 USciptStruct 设定模板类。

### 绑定其他内容

UEnum 在 Bind_UEnum.cpp

Delegate 在 Bind_Delegates.cpp

还有一些特殊的类型，TMap、TArray、TSet、TOptional 等模板类型，是有专门处理的。

另外，常用的 FVector \ FTransform 等，好多都是得手工单独处理，这些会有单独的绑定文件。

还有一些全局函数，也是单独写的，比如 NewObject， SpawnActor 等。

---

未完待续
