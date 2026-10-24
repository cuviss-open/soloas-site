---
title: "UE_Angelscript 认知篇——理解：复制、引用"
order: 13
category: concepts
---
# UE_Angelscript 认知篇——理解：复制、引用

# 前言

本文解释关于 UE-Angelscript 脚本语言使用中，最好具备的认知基础——复制、引用。

# C ++ 基础概念

学过一点 C++ 的，多多少少都知道 C++ 在函数参数传递中，默认是按值传递（复制）的，想要操作原来的对象，要么用原对象，要么用指针，要么用引用。

什么是原对象？
就是值本身。对象一般可以理解为，连续的一块内存，刻画了对象的具体细节。
（一块代表某种事物的内存，可以有初始的名字，比如张三。）

什么是指针？
基础概念，是一个保存了一个内存地址的对象，不多解释了。
指针的概念，带来一个好处——操作数据方便，只要传对象的地址定位，就可以操作对象了。
（其本身也是一个对象，但是这个对象很特殊，它保存着其他对象的地址，比如，对张三的 GPS 定位，通过定位，我们可以精准地找到张三。）

什么是引用？
是个对象的别名，操作引用，就和操作原对象一样。
引用的底层实现本质上也是指针，只是语法上引用不能重新绑定，且解引用是隐式的；在 C++ 里，一般使用者可以这么认为，那是编译器的事情，只需要理解为别名就好了。但是涉及到 Angelscript 与 C++ 的交互时，引用本质是指针的情况，是不能忽略的，否则，会产生难以理解的一些问题。
（在使用者的概念上，就是对象的别名，别名是什么意思？比如，张三是对象原名，那么我们可以其一个张三的别名——张铁柱，别名可以很多的，都代表了张三这个对象。）

何为复制？
将一个对象完整地复制一份出来，就是复制。
（我们再说说张三这个对象，如果复制，那么就会成为李四，这时候，就同时存在张三和李四，虽然刚复制完成时，他们两个是一模一样的，但是后续的人生就各走各的了。）

为何要区分复制和引用。
复制需要性能和存储开销的，一般情况下，当然是能不复制最好了。引用就是在这个时候出现的，一个对象到了新环境（比如某个函数），这个环境并不在意原来对象叫什么，进来的对象，只要坑位对了，那么统一为叫做某个名字或者代码，比如 9527。
（张三如果进入新环境，被叫做狗蛋或者 9527，都没办法，张三身不由己，只能入乡随俗，虚拟的张三，只是提线木偶，莫得感情，更别说自由，只是希望人类在有好处的时候，别给错了复制出来的张三分身。）

# UE 与 Angelscript 的数据对应关系

## 值类型

在 UE 与 Angelscript 的数据对应中，所有的基础类型，都是值类型对应，比如
int 和 float 等， 你在 AS 里操作的这些类型，都是操作值本身。

还有很多绑定的类型，比如 FString FName FColor FVector 等。
一句话总结，`除了 UObject 及其子类外，UE-Angelscript 的类型都是值类型`。

**Angelscript 与 C++ 写法一致**
比如 `FTestStruct`

## 代理类型

（或者叫做指针类型、引用类型，反正不是对象本身，而是对象的地址。）

目前已知只有 `UObject` 及其子类绑定为代理类型，在 Angelscript 里，这种代理类型对应为 Handle （句柄），实际上，Angelscript 对这种类型的完整写法是 `UObject@`，不过，UE-Angelscript 脚本绑定的时候，声明它可以省略 `@`， 于是大家都忽略掉`@`，这造成一个视觉问题——所有的 UObject 就看着和值类型一样，并无特殊标记，然而它们确实不是同一类。

**对于 Angelscript 与 C++ 写法不一致**
在 Angelscript 里写 `UObject`， 对应为 C++ 里的`UObject*`。

## 模板类型——三大容器 TArray TMap TSet

可以理解为复合类型，比如 `TArray<UObject>`， 主类型是 `TArray`，子类型是 `UObject` 。

**对于值类型，Angelscript 与 C++ 写法一致**
比如 `TArray<FTestStruct>`

**对于 UObject, Angelscript 与 C++ 写法不一致**
在 Angelscript 里写 `TArray<UObject>`， 对应为 C++ 里的`TArray<UObject*>`。

`TMap` 和 `TSet` 同理。

另外还有迭代器 TArrayConstIterator、TArrayIterator 等这种容器的迭代器，也是差不多的。

## 模板类型—— UObject 指针

TObjectPtr 、TWeakObjectPtr、TSoftObjectPtr 等

可以理解为复合类型，比如 `TObjectPtr<UObject>`， 主类型是 `TObjectPtr`，子类型是 `UObject` 。

**Angelscript 与 C++ 写法一致**
比如`TObjectPtr<UObject>`

## 模板类型——其他

一般不用于 UObject。

可以理解为复合类型，比如 `TOptional<FTestStruct>`， 主类型是 `TOptional`，子类型是 `FTestStruct` 。
TOptional 不用于持有 UObject，只用于值类型。（原因在于 UObject 可以用 nullptr 表达空状态，无需多此一举。）

**Angelscript 与 C++ 写法一致**
比如`TOptional<FTestStruct>`

# Angelscript 基本和 C++的复制与引用规则基本一致

## 特例除外

例外，对于 `UStruct` 以及 `FString\FName\FText`，在函数编写的时候，只要参数类型不是单独的可变引用`&`，那么传参的时候，默认就会成为 `const &`。

一下四个函数中，有三个是等价的！
函数 GetDataPtr，等价于 GetDataPtr_InputConst ，等价于 GetDataPtr_InputConstRef

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

其余情况，和 C++的规则是一样的。

虽说如此，在 UE-Angelscript 的官方文档也这么写，但是，那该如何证明呢？
证明的逻辑，是这样的：一个值如果被传入函数中，如果是被复制，其地址会更改，我们只需要比较地址，就知道是不是一样了。

代码如下。
注：其中用到了 FDataPtr 是一个存指针的结构体，其 ToString() 函数会将指针转为 FString，而`FDataPtr::Create` 这种需要自定义绑定的特殊函数，需要会绑定泛型函数才可以操作，涉及其他比较深一点的绑定技巧，这里不详解释，所以，以下就当作伪代码吧。

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

// 测试代码

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

同理，可以检验 `FString\FName\FText` 也是如此。

而其余类型，就是默认的 Cpp 规则了。

为什么有这样的特例呢？优化性能、简化书写吧。因为如果一个 UStruct 如果占用内存很大，那么复制的开销是很大的。
UObject 占用的内存一般更大，怎么不优化它？Angelscript 的 UObject 本质上是一个指针而已，传的都是指针，复制就复制吧，不会有什么性能压力。
还有，基础类型比如 int 等呢？这些类型占据的内存也很小，复制也无所谓了。

## 还是有较大复制开销的情况需要注意

`TArray<FTestStruct>` 这种值类型，每当调用 Add 函数，都会复制一次 `FTestStruct`。

把它取出来的时候，新手可能会忘记加上 `&`，那么，也会复制一次。

复制本身可能只是性能开销，但如果你的目的是修改容器内的元素，复制出来的只是副本，那么修改不会影响原容器中的值。

所以，承接容器里的值，不想产生不必要的复制，建议还是这样吧

```cpp
TArray<FTestStruct> TempArray;
TempArray.Add(FTestStruct()); // 确保非空
const auto& TempConst = TempArray[0];
auto& TempMutable = TempArray[0];
```

值得注意的是，UObject 始终是特例，如果是 `TArray<UObject>`这种，因为 UObject 本质上是指针，就算复制了，也只是复制了指针而已，还是可以操作到实际的 UObject 对象的。

---

# 总结

即使是写脚本，即使是 UE-Angelscript 特意优化了函数传参，如果引用和复制的规则不清晰，还是可能会导致大量复制的出现，特别是在使用容器的时候。

当然，复制的出现只是耗费点性能，然而如果将复制当作引用来使用，那么，业务逻辑就问题大了。

所以啊，既然表面上没有了指针的存在，那么——**复制的归复制，引用的归引用**，就像凯撒名言——**“凡属于凯撒的，应归凯撒；凡属于上帝的，应归上帝。”**

别混淆了两者的边界，不然就陷入 **指鹿为马** 的泥潭。

当然，读者聪慧如斯，自然可以理解二者差异了。

---
