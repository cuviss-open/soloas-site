---
title: "杂谈：没有人能拦我用 Lambda，除了我自己"
order: 19
category: essays
---
# 杂谈：没有人能拦我用 Lambda，除了我自己

终究还是受不了 UE-Angelscript 没有 Lambda 的日子，特别是 Delegate 绑定的时候，需要传递更多参数，而 Delegate 本身不支持时，相当地麻烦！

经过本系列文章里提到的 [UE_Angelscript 源码篇 2：AS 的类绑定到 UE](internals-angelscript-classes-to-ue.md) 的了解， AS 的文件在最终编译之前都要经过预处理阶段，其中 RangeBasedFor 循环这种语法糖，也是在这个时候解析的。

那么，在预处理阶段，既然可以增加 RangeBasedFor 这种这种循环的语法糖，那么增加 Lambda 语法糖不过分吧。

工具还不够顺手，就需要打磨，所以有本文。

本文会提供一些实现这个语法糖的思路以及最终实现后的 AS 应用代码展示。

# 首先了解 Cpp 里的 Lambda 语法糖是怎么样的呢？

这是 C++ 里写的代码

```cpp
int main()
{
	auto Test = 5;

	auto add = [Test](int a, int b) {
		return a + b;
	};
	add(1, 2);

	return 0;
}
```

其内部处理，会变成这样：
注： 观察 C++ 的底层实现，可以用 https://cppinsights.io/ 这个网站。

```cpp
int main()
{
  int Test = 5;

  class __lambda_6_15
  {
    public:
    inline /*constexpr */ int operator()(int a, int b) const
    {
      return a + b;
    }

    private:
    int Test;

    public:
    __lambda_6_15(int & _Test)
    : Test{_Test}
    {}

  };

  __lambda_6_15 add = __lambda_6_15{Test};
  add.operator()(1, 2);

  return 0;
}
```

观察得知，这是增加了一个匿名类，在 `[]` 里捕获的变量，会映射为此类的成员，另外这个类会有两个函数，
一个是构造函数，用的捕获的变量来进行构造，构造函数参数是引用形式，但成员变量依然是拷贝（值捕获），所以是值传递。
另外一个是类方法的调用函数，`operator()` 就是可以用类名当作方法名的意思。

声明完这个类之后，接着会实例化一个类对象，上面案例中是 `add`, 那么对于 Lambda 的调用，就是调用类方法了 `operator()`。

小结就是，Lambda 就是会声明一个匿名的类，同时实例化一个类对象出来，所谓捕获变量，就是将变量作为这个匿名类构造函数的输入参数而已。

捕获变量，是很好很好用的语法糖！节省书写的代码量。

# UE - Angelscript 里 Lambda 的构造思路

参考 Cpp ，首先需要声明一个匿名的类，这个类在 UE - Angelscript 里有两种，一个是 用 struct 声明， 一个是用 class 声明。

在 UE-Angelscript 中，struct 会被编译为值类型，而 class 默认会继承自 UObject

用 UObject 来做，开销会大些，因为有 CDO （类默认对象）的产生，但是也有好处，提供了反射能力，操作起来更方便些，另外生命周期的管理上，只要设计好持有的关系，就可以放心地交给 UE 自身的 GC 系统。

毕竟是业务层面的代码，这点开销的代价，可以换来更好地体验，自然是值得的。（我不会承认是为了懒得处理生命周期的问题，才选择了 UObject 子类作为匿名类。）

既然方向确定了，先模拟一下吧，毕竟是预处理代码，我们先写一下处理之后的大致情况。

## 设定目标

我心目中预想的调用方式。

```cpp
void Foo()
{
	// ...

	int TempInValue1 = 666;
    FString TempInValue2 = "World";
	FSomeTestDelegate TestDg;

	TestDg.AddFakeLambda([TempInValue1, TempInValue2](float32 Infloat)
	{
	  // do things
	}
	// ...
}
```

为了生命周期更容易管理，也为了实现更加简单，默认 Lambda 对象的生命周期跟随当前的类。

因为是语法糖，所以是代码的替换，以下是心目中合理的替换之后的代码。

```cpp

void Foo()
{
	// ...

	int TempInValue1 = 666;
    FString TempInValue2 = "World";
	FSomeTestDelegate TestDg;

	auto Lambda_Bound = AddPart(UFakeLambda_Bound);
	Lambda_Bound.TempInValue1 = TempInValue1;
	Lambda_Bound.TempInValue2 = TempInValue2;

	TestDg.AddUFunction(Lambda_Bound, n"FakeLambda_Bound_Func");

	// ...
}

class UFakeLambda_Bound : UObjectPart
{
	UPROPERTY()
	bool bIsFakeLambda = true;

	int TempInValue1;
	FString TempInValue2;

	UFUNCTION()
	private void FakeLambda_Bound_Func(float32 Infloat) __generated
	{
		// do things
	}
}
```

我没有写构造函数，而是直接用 `Lambda_Bound.TempInValue1 = TempInValue1;` 这种赋值的方式来处理捕获的变量，代码更简洁。

为了可读性，这里没有将替换的代码的行数进行对应，实现操作中，应该要确保替换代码的行数一致，否则会影响 IDE 的代码提示。

其中 `AddPart` 函数是将某个 UObject 的生命周期与调用者进行关联，属于自己实现的函数。可以参考文章 [UE_Angelscript 实践篇——自由的组件，实现功能模块化](practice-component-modularity.md)，不过这个参考文章中的部分内容有误，特别是关于 Outer 的理解，也许需要看这篇，UE 的 Outer 是什么意思（已更正，后附详细证明） ，这些文章并不能给出稳定地关联两个 UObject 的生命周期的方案，你需要自己实现。

## 一个一个问题地解决

实现的过程中，有两个最大的坑，一个是上文提到的生命周期的坑，`AddPart` 函数的实现，是需要精心设计的。

另外一个大坑是如果精准地找到对应的代码然后进行合适地映射替换，在跑通流程的过程里，正则表达式如果要支持各种各样的情况，需要写很长很复杂的。

在解决了生命周期的问题的情况下，其他问题可以拆解为，

- **替换代码的时机是什么时候**

预处理阶段，需要增加一个给 UE-Angelscript 增加一行代码，在其预处理的早期进行文本的替换。这里可以在 UE-Angelscript 预处理类中找到，不知道在哪的，可以参考文章 [UE_Angelscript 源码篇 2：AS 的类绑定到 UE](internals-angelscript-classes-to-ue.md) 。

- **如何找到我们写的 Lambda 代码**

可以参考 UE-Angelscript 对于其他语法糖的处理，方法是用**正则表达式**来匹配要替换的文本的。所以，需要约定好一些格式，Lambda 的语法特征比较独特，用正则表达式能很好地匹配到。也可以约定函数名，这样就能迅速地定位到在哪里。

我是约定了函数名的，此时，所有 AS 代码里，就不能随便将这个函数名放在注释里，不然增加匹配错误的几率，虽然一般不会匹配错，一般人不会没事把 Lambda 的整个格式写在注释里。

- **找到代码并且解析之后，如何具体地映射**

映射的时候，新增的类名、函数名等，最好都是唯一的，此时为了唯一，可以以文件名来依据，再辅以序号，可以得到唯一的名称。当然也可以辅以所属的类名，但是如果写在全局函数里，这就匹配不到了，最终选择的时候，文件名是一个不错的方式。至于文件名如果获取，UE-Angelscript 在预处理阶段，自然是读取了的，我们只需要拿来用。

这个映射规则自己写好，确保不重复，生成的类名要足够特殊，避免与其他代码的类重名。

- **新增的类，如果代码出错了，怎么调试**

之前提到的代码替换需要行数一致，也是为了在调试的时候，避免行数错位。你总不能中间添加了一个 Lambda 之后，导致其之后的代码报错都行数有误吧。

因为新增的类我们考虑放在文件的末尾了，而且它并不在我们的视线范围内（不在 .as 文件里），所以一旦报错，就会报错在最后一行。

因为报错就算给了行数，你也只能通过报错信息来了解报错情况，如果 Lambda 里的代码简单的时候还好，很容易辨认，但是如果复杂了，就难以辨认了。如果 Lambda 的函数体需要有很多代码，应该单独写一个函数，Lambda 仅作为中转调用就好。（Lambda 就算作为中间接力，也能省很多代码。）

因为 Lambda 函数体的代码实际是放在了文件的最后，并且不可见，所以调试的时候，在 IDE 是没法打点调试 Lambda 函数体的。也许可以通过其他映射的方式做到，但是我没有考虑要实现这个。

## 小结

最终算是能跑通流程了，IDE 里或许可以改改插件增加提示，但是，懒得改了，这提示对我来说，用处不大，因为这是我写的语法糖。

有点小遗憾，捕获的时候，捕获变量的类型不方便自动推导，于是需要在捕获的时候明确类型。这是因为预处理阶段只做文本替换，并没有完整的类型推导机制，所以只能显式标注类型。

捕获需要明确类型的情况，有利有弊，有利的是，可以方便地直接获取到不在当前文件的全局变量，不利的是，每次需要多写捕获的类型。鉴于捕获的实现在语法糖层面进行推导类型的难度，还是手工明确捕获类型吧。

最终实现的可调用代码格式如下：

```cpp
void Foo()
{
	// ...

	int TempInValue1 = 666;
    FString TempInValue2 = "World";
	FSomeTestDelegate TestDg;

	TestDg.AddFakeLambda([int TempInValue1, FString TempInValue2]
	(float32 Infloat)
	{
	  // do things
	}
	// ...
}
```

对于单播, 我用不了不同的函数名 `BindFakeLambda`，这是为了与 UE C++ 对单播和多播的绑定函数的命名协调。

# 最终过测代码示例

测试的类型，其中可以增加各种信息，摆放位置，以及故意写错代码查看 IDE 提示，以及单点调试等。

```cpp
class ATestLambda : AActor
{
	FTestDelegate_OneParamReal TestDelegate;
	FTestMulticastDelegate_TwoParamsReal TestEvent;

	void TriggerLambda()
	{
		TestDelegate.ExecuteIfBound(666);
		TestEvent.Broadcast(2.f, 3.f);
	}

	void BindLambda()
	{
		FName TestName = n"Good";
		int TempInValue1 = 666;
		FString TempInValue2 = "World";

		TestDelegate.BindFakeLambda([int TempInValue1, FString TempInValue2, FName TestName](float32 Infloat) {
			Log(f"Hello {TempInValue2} -- {TestName} : Infloat {Infloat} : TempInValue1 {TempInValue1}");
		});

		TestEvent.AddFakeLambda([int TempInValue1, FString TempInValue2, FName TestName](float32 Infloat, float64 InDouble) {
			Log(f"Hello {TempInValue2} -- {TestName} : Infloat {Infloat} : InDouble {InDouble}: TempInValue1 {TempInValue1}");
		});
	}
}
```

触发测试的代码

```cpp
void Test_Lambda_InAS(FUnitTest& T)
{
	auto Actor = SpawnActor(ATestLambda);

	T.AssertTrue(!Actor.TestDelegate.IsBound());
	T.AssertTrue(!Actor.TestEvent.IsBound());

	Actor.BindLambda();

	T.AssertTrue(Actor.TestDelegate.IsBound());
	T.AssertTrue(Actor.TestEvent.IsBound());

	Actor.TriggerLambda();
}
```

测试通过，同时会打印一些 Log。

# 总结

UE-Angelscript 官方提供的脚本功能，很多是面对大量编程基础一般的人，如果增加 Lambda 的支持，确实会导致一些理解成本。

不过对于用过 Lambda 的人来说，没有它，总是难受的，特别是当你的调用链很长的时候，写一堆的回调函数，有些烦琐了。

凡事有利有弊，简洁的写法，也有代价的，除了学习成本，还有调试成本。简单地语法糖实现方式，终究需要放弃一些调试的便利了。本文的方案，对于调试问题的应对方式就是，在 Lambda 里写些几乎不会出错、并且不需要断点调试的代码。

至此，没有 Lambda 的地方，也可以仿造一个。

没有人能拦我用 Lambda，除了我自己。
