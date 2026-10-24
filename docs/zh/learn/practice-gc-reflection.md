---
title: "UE_Angelscript 实践篇——关于类成员的垃圾回收与反射问题"
order: 30
category: practice
---
# UE_Angelscript 实践篇——关于类成员的垃圾回收与反射问题

UObject 的垃圾回收与反射本来在 C++ 里已经足够复杂了，Angelscript 对其进行了一些简化处理，然而，真正深究起来，发现这个改变是合理的，但是理解难度会增加一点点了。

先说一个 Angelscript 里值得重视的结论：因为 Angelscript 默认将类成员中的 UObject 类型及TArray | TMap | TSet 类型里的 UObject都放进了 GC，所以 TWeakObjectPtr 应该值得被推广使用，可以进行很多解耦操作，因为它不阻止 GC，防止引用链过度膨胀。

本文更侧重于垃圾回收。

## 垃圾回收的基础概念

垃圾回收，即 GC，是 UE 里单独管理 UObject 的生命周期的系统，只有 UObject 被纳入管理中，平常我们 NewObject 之后，其实可以不用去管理它，GC 系统会自动扫描判断它还是不是被使用，不被使用就清理掉。

但是 GC 系统只能看到标记给它看的内容，所以 C++ 里经常会有 UObject 作为类成员，然后标记上 UPROPERTY() ，仅仅是为了让它可以被 GC 看到。

UPROPERTY() 这个标记，对于 UObject 类成员来说，有两种意义，一个是纳入 GC 系统，另外一个是纳入反射系统。

C++ 没有对 UPROPERTY() 关于 UObject 类成员的两种功能进行拆分，但是 Angelscript 进行拆分了，struct | class 里的 UObject 类成员以及 TArray | TMap | TSet 类成员里的 UObject，都纳入了 GC 系统，无论其是否标记 UPROPERTY，然后 Angelscript 的 UPROPERTY() 就仅仅作为暴露给反射系统及蓝图的标记。

## 有趣的事实

### 关于反射系统

**struct 的成员都默认加入反射系统，而 class 不是。**

AS 里的 class 与 struct 不一样的一个点，struct 默认都给加入反射系统了，通过 PropertyLink 的反射遍历可以随意访问，而 class 却没有这个默认行为。原因是 class 没必要也不能默认加入，不只是为了减少一点开销，而是确实有些类型无法加入反射系统，所以，需要反射的时候再自己手动加 UPROPERTY()；而 struct 是被当作数据持有类型的简单容器，就都纳入反射系统了，不能纳入的类型是不可以作为类成员的。

虽然 struct 默认都给加入反射系统了，但是加入了反射系统不代表就暴露给蓝图访问，如果想要蓝图能访问到，还是得加上 UPROPERTY() 标记。

```cpp
// Angelscript 代码
struct FStructTest
{
	UObject Obj; // 这实际上是 UPROPERTY，反射可以访问到
}
// Angelscript 代码
class UTestObj
{
	UObject Obj; // 这就是一个普通的指针，反射无法被访问到
}
```

### 关于 GC 系统

**struct 和 class 都默认将 UObject 类成员和 TArray | TMap | TSet 三大容器里的 UObject 加入 GC。**

这种行为的变化，实际上是利用代码解释器来做到的，其加入的代码在：

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

所以，总结之后，对 UObject 成员类型的各种情况的精确表述是

```cpp
// Angelscript 中的真实情况
class UTestObj : public UObject
{
    // 情况1：受GC保护（通过UPROPERTY）
    UPROPERTY()
    UObject ProtectedObj;  // GC会追踪此引用，对象不会被意外回收

    // 情况2：受GC保护（通过UPROPERTY）
    UPROPERTY()
    TObjectPtr<UObject> ProtectedObj;

    // 情况3：受GC保护（即使没有UPROPERTY，与C++不同！）
    UObject UnprotectedObj;  // 没有UPROPERTY，但GC仍会追踪此引用

    // 情况4：安全的弱引用
    TWeakObjectPtr<UObject> WeakObj;  // 不会阻止GC，但可安全检查
};
```

啊，没错，受 GC 保护 有三种写法，而**不受 GC 保护的写法通常只有一种**。（暂时忽略掉其他可能存在的相关封装类型。）

还有一点值得提的是，不管是，上述情况 1 到 3，都是用的时候最好要判空的，因为虽然理论上受到保护，一般不会被清理，但是万一有地方写了强制回收的代码呢，比如 有哪些地方写了 MarkAsGarbage()，那么就会导致悬垂指针的出现。

## 不阻止 GC —— TWeakObjectPtr 的使用

### 封装 TWeakObjectPtr

要方便的使用 TWeakObjectPtr，可以考虑封装一层来用，这首先源于一个脚本自身的问题。

AS 里存在一个问题，`TWeakObjectPtr<UObject>` 的使用，那是一直报错啊，它是最基础的类别了，但是居然函数调用出错，而子类可以正常使用。（也许以后会修好吧。）

```cpp
	{
		TWeakObjectPtr<UObject> WOP;
		// 注：此问题仅出现在UObject基类，具体子类如AActor则正常
		// 报错：No matching signatures to 'TWeakObjectPtr::Get()'
		auto Obj = WOP.Get();
	}

	{
		TWeakObjectPtr<AActor> WOP;
		// no error
		auto Obj = WOP.Get();
	}
```

那么怎么办，暂时理不清插件绑定源码里出现了什么问题， 就干脆自己写一个包装类好了，让其可以无缝地与 `TWeakObjectPtr<T>` 类型交互。

```cpp
    TWeakObjectPtr<UObject> WOP;
    FWeakObjectPtrWrapper Wrapper = WOP;
    Wrapper.Get();
```

这种包装类在 cpp 里写十分简单

```cpp
// Make TWeakObjectPtr<UObject> useful
USTRUCT(BlueprintType)
struct FWeakObjectPtrWrapper
{
    GENERATED_BODY()

    UPROPERTY(EditAnywhere, BlueprintReadWrite)
    TWeakObjectPtr<UObject> WeakObjPtr = nullptr;
```

然后给它附加一模一样的接口就可以了。（本专栏里的其他文章已经有详细介绍，这里不再赘述。）

### TArray 嵌套与自动推断

有个不错的建议是，顺带也把它的 TArray 形式也写了。这个在 Angelscript 也可以写，但是在 Cpp 写有好处的，特别是自动推断的便利。

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

为什么呢？因为 Angelscript 里不允许 TArray 里套 TArray，为以后省事。

TArray 等容器时不时遇到推断的问题，每次 Cast 是很烦的，可以在 Cpp 写点自动推断的函数来辅助，这个技巧很好用，省掉很多类型转换的代码。
例如：

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

## 总结

Angelscript 默认加反射、加 GC 的行为是好的，减少了很多代码负担，但是这也会造成 C++ 与 Angelscript 之间表达的不一致，不过总体利大于弊。

struct 默认加反射不会影响游戏逻辑本身，反而增加了很多好处，利远远大于弊。
struct 和 class 默认给 UObject 加 GC，可能会导致引用链的增加，需要注意清理引用（如果忘记清理，一般只是增加内存消耗，对游戏逻辑影响比较少），所以不阻止 GC 反而成为了需要特别重视的情况，也就是 TWeakObjectPtr 得用得更多一些，总体利大于弊。

---
