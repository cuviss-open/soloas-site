---
title: "UE_Angelscript 奇技淫巧"
order: 15
category: tips
---
# UE_Angelscript 奇技淫巧

这里列举一些有意思的内容，旨在为了更舒服地写逻辑，是的，没有这些奇技淫巧，我们依然可以生活，这些奇技淫巧是锦上添花，让生活更美好。

本文主要涉及：判空的流畅写法、Cast 的流畅写法、Mixin 的另类写法 ScriptMethod、DeterminesOutputType 的使用、通过反射修改任意 UPROPERTY 参数的介绍。

# 判空的流畅写法

AS 里的 UObject 虽然没有指针符号，但是它本质上是一个指针罢了。对于指针，我们使用之前，一般判空，在 cpp 里，写起来很简单，比如

```cpp
if (ThisObject*)
```

而 AS 里正常情况下，有两种常用写法，如下

```cpp
if (ThisObject != nullptr)

if (IsValid(ThisObject))
```

其中第二种写法还附带了判断是否正在被垃圾回收的功能，防止你使用已经标记为垃圾回收的对象，实际上适用面会更广。

由上可以看出，AS 里的写法比较没那么简洁，AS 里不是不能实现隐式转换，而是 AS 故意为之，尽可能地减少隐式转换的情况。

判空如何才能更顺畅地写出来？用 mixin 功能，实现链式调用，那么就可以这么写了

```cpp
if (ThisObject.IsValid_())
```

要实现这个十分简单，不需要 c++ 代码，只需要在 AS 里找个文件，加上

```cpp
// Mixin version of IsValid(const UObject Object)
mixin bool IsValid_(const UObject Object)
{
	return IsValid(Object);
}
```

我这里加上一个下划线，是因为不想破坏 IsValid() 这个全局函数的正常写法（此时，这个 mixin 函数不再是类似成员函数了，因为可以接受 nullptr，末尾加上个下划线，算是作为区分)。

这种链式调用的写法，会更加的顺畅，同时不用考虑和 nullptr 的比对，将 AS 里指针的概念进一步弱化。

**补充，IsValid 会涉及到 GC , 如果不需要判断是否在 GC 中，或者想要极致的性能，那么可以直接判是不是等于 nullptr.**

写法参考（此时，这个 mixin 函数不再是类似成员函数了，因为可以接受 nullptr，末尾加上个下划线，算是作为区分)：

```cpp
mixin bool IsNull_（UObject Obj）
{
	return Obj==nullptr；
}
```

# Cast 的流畅写法

这里也是用到了 Mixin ，不过需要用到 cpp 的。

正常情况下，我们写 Cast , 是和 c++一样的

```cpp
auto A = Cast<AActor>(ThisObject);
```

而我们想流畅书写，实际上舒服地写法是类似这样的

```cpp
auto A = ThisObject.CastTo(AActor);
```

这可以实现，用到了 UE 的反射系统，实现起来也简单的
需要给 UObject 写两个 Mixin 函数，用到了一个十分有用的标识符 DeterminesOutputType，这个标识符会自动根据反射的类型信息来推断应该返回的类型。

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

这里增加多一个 check 版本，是为了有时候确保 Cast 成功的。

值得一提的是，Mixin 的函数，类似于给类写一个新的成员函数，一般情况下，不必对 this 指针进行判空，在上面的函数里，也就是不需要对 UObject 判空。这也是 AS 各类绑定库的通用写法。

**补充，如果需要让这个 Cast 可以接受 nullptr 作为参数，可以像下方这样（最新版本已经不允许 C++ 的 Mixin 对象为空，所以，这个不能用了。）**

写法参考（此时，这个 mixin 函数不再是类似成员函数了，因为可以接受 nullptr，末尾加上个下划线，算是作为区分)：

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

# 判空与 Cast 的流畅组合写法

可以对比一下

```cpp
// 原始的写法
if (IsValid(Cast<AActor>(ThisObject)))

if (Cast<AActor>(ThisObject) != nullptr)

// 新的写法
if (ThisObject.CastTo(AActor).IsValid_())
```

很明显，新的写法更符合阅读的直觉，写起来与看起来都舒服一些。不是吗？（当然，如果你觉得不是，那一定是你更对！）

补充提一下，正常的代码千万不要这么写，如果只是判断类型，用 IsA() 函数，如果需要 CastTo 的值，应该在 if 之前用一个变量来承接。

# Mixin 的另类写法 ScriptMethod

如果用传统的 Mixin 写法，每对一个类增加功能，都必须要新建一个 UObject , 有时候觉得挺麻烦的，这时候就可以请 UE 原生的标识符出场了。

这个标识符本来设计是给 python 之类的脚本使用，有意思的是，AS 也能用，而且用起来很舒服。

这是英文的解释：

此处摘录的是 Unreal Engine 对该元数据作用的说明。

这里给出一个官方的示例，与 DataTable 相关的函数库。

mixin 写起来方便多了，但是这会导致 DataTable:: 的命名空间的写法不能再使用，如果之前 AS 代码有这种写法，那么需要修改了。

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

ScriptMethod 之后也可以不加 = 号，这样就不会改变函数名。

经过以下的测试，对于 AS 来说，ScriptMethodMutable 没有什么作用，单独用不行，与 ScriptMethod 组合用，也没有让 const 的内容变可修改。内容可不可以修改，完全取决于第一个参数是否是 const。UPARAM(ref) 也和 ScriptMethodMutable 一样，没什么作用。

综上，ScriptMethod 可以当作 mixin 的单函数版本，可以在一个蓝图函数库里对多种类型进行 mixin 的，const 与否，完全取决于第一个参数是否有这个标签。

下方是一个测试函数的用例，用于测试以上内容的，需要的话，也可以用来验证一下是否正确。

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

# Cpp 的 Meta 实现自动类型判断 ：DeterminesOutputType 标识符

这是 Lyra 项目里的一个函数，其会根据 FragmentClass 的类型自动给推断返回类型，蓝图里或 AS 里调用的时候无需 Cast。

```cpp
	UFUNCTION(BlueprintCallable, meta=(DeterminesOutputType=FragmentClass))
	static const ULyraInventoryItemFragment* FindItemDefinitionFragment(TSubclassOf<ULyraInventoryItemDefinition> ItemDef, TSubclassOf<ULyraInventoryItemFragment> FragmentClass);
```

拓展，DeterminesOutputType 支持自动推断 TArray 里的值，还支持多参数推断，支持自动解析结构体内部的 Property 作为基础来推断。

使用示例，可以推断函数的返回类型、数量：

```cpp
	// 函数返回类的自动推断，如果没有配合 DynamicOutputParam 参数， 默认推断返回值
	UFUNCTION(BlueprintCallable, Meta = (DeterminesOutputType = "TypedClass"))
	static TArray<AActor*> MyTestFunc(TSubclassOf<ATestActor> TypedClass);

	// 函数参数的类型推断，与 DynamicOutputParam 配合，支持同时推断多个参数
	UFUNCTION(BlueprintCallable, Meta = (DeterminesOutputType = "TypedClass", DynamicOutputParam = "OutTest,OutTest2"))
	static void MyTestFunc(TSubclassOf<ATestActor> TypedClass, TArray<AActor*>& OutTest, AActor*&  OutTest2);
```

使用示例，用于推断的基础类型：

```cpp
	// TSubclassOf<> 是支持的，上方示例已经有

	// DeterminesOutputType 里还可以接受 UObject
	UFUNCTION(BlueprintCallable, Meta = (DeterminesOutputType = "Object"))
	static TArray<UObject*> MyTestFunc(ATestObject* Object);

	// DeterminesOutputType 支持将 struct 里的 property 作为推断的基础类型
	// 下方就是将 FTestStruct 里的AnyProperty 作为推断的基础
	UFUNCTION(BlueprintCallable, Meta = (DeterminesOutputType = "TestStruct_AnyProperty"))
	static TArray<AActor*> MyTestFunc(const FTestStruct& TestStruct);
};
```

这个 DeterminesOutputType 用好了，可以节省很多无意义的 Cast 代码，如果用在 TArray 上，那么会感觉世界更美好！

# 通过反射修改任意 UPROPERTY 参数

AS 里会遇到一种情况是，某个参数暴露给 AS 了，但是它只给在构造的时候修改，不能在运行时修改。正常做法是在 cpp 里写 Mixin 函数，通过函数来操作。

但是这样总是显得麻烦，还有一种情况是这个参数在 cpp 里不是 public，那么 cpp 正常的访问也不行了。

在确保可靠的情况下，用反射就可以改这种参数了。可以这么说，大部分 Cpp 里的参数，只要进入了反射系统，都能被操作。

一个简单的使用情况如下：

这是测试用例。

```cpp
/// Cpp 的测试用例
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

这是包装了反射函数 SetPropertyFloat 和 GetPropertyFloat 后，在 AS 里的写法。

```cpp
/// AS 里的测试
ATestClass TestClass11 = NewObject(nullptr, ATestClass );

float32 OutValue = 1.0f;
// 我将这个函数放在 Reflect 命名空间下，你随意
Reflect::SetPropertyFloat(TestClass11, n"TestFloat", 9.0f);
Reflect::GetPropertyFloat(TestClass11, n"TestFloat", OutValue);

// FUnitTest& T
T.AssertTrue(OutValue == 9.0f);

// 测试应该通过
```

具体可以参考这篇文章，魔法毕竟是魔法，使用需谨慎。
手搓 UE5 的反射魔法，是黑魔法？是白魔法？

# 小结

本文主要围绕判空、Cast、Mixin 用法、ScriptMethod、DeterminesOutputType、反射修改参数等话题展开，所谓奇技淫巧，主要是将机械重复的工作交给机器处理，让编码更舒适。

---
