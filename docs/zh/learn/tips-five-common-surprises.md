---
title: "UE_Angelscript 奇技淫巧2：你挠头不解的问题，有时只需一句话"
order: 16
category: tips
---
# UE_Angelscript 奇技淫巧2：你挠头不解的问题，有时只需一句话

这些是使用 UE-AS 时候可能遇到的问题，一旦遇到了，你可能会找半天找不到方法。

然而，这些问题，只需要一句话就可以解决了。

# 参数 WorldContext 隐藏了，无法输入怎么办

一句话方案总结：使用函数前，在当前作用域加上 FAngelscriptGameThreadScopeWorldContext(GetWorld())。

如果是蓝图，蓝图可以设定暴露出来 WorldContext 的引脚，而代码是没有引脚的。

最直接的思路是，绑定一个暴露出 WorldContext 参数的函数，然而，这种函数有很多，有没有一种方法可以直接在 AS 代码里自定义世界上下文呢？

有的，代码虽然没有引脚，但是有作用域，我们只需要在同一个大括号范围里（作用域）加上 FAngelscriptGameThreadScopeWorldContext() ，就能让之后的 WorldContext 被替换为你设定的值，直到大括号（作用域）结束。

```cpp
class UGCN_Test : UGameplayCueNotify_Burst
{
	UFUNCTION(BlueprintOverride)
	void OnBurst(AActor Target, FGameplayCueParameters Parameters,
				 FGameplayCueNotify_SpawnResult SpawnResults) const
	{
		// Create a temp WorldContextObject
		auto _World = FAngelscriptGameThreadScopeWorldContext(GetWorld());

		Gameplay::GetPlayerPawn(0);

		Warning(f"Test: {this.GetName()}");
	}
}
```

# 非 UObject 类型的空值如何表示比较好

一句话方案总结：使用 TOptional<>。

UE-AS 里表达空的概念的几种方式：

1，指针（或者类似指针的对象）。

只能是 UObject 使用。AS 里没有指针的概念，没办法对 UStruct 和原生类型（int、float 等）进行判空。

2，默认值或全局变量。

可以考虑指定某个值来表示空的状态，但是会带来其他问题，适用于简单的情况。比如，int 假如设置了 -1 为空，那么-1 这个值就不能表达正常的-1 概念，但如果你确实需要用到 -1 ，那么就得考虑其他值，这个情况多了，会造成混乱。

有人会说，不是有全局变量来表示空值吗？UE 里挺多的。是的，但那是古早的代码惯性了，那种表达方式是不得已而为之，现在如果新增空值表示，可以有更好的写法。

3，给 Struct 增加判空函数。

有一些 cpp 绑定过来的 UStruct 会绑定了判断函数，比如 IsValid 或者 IsNull，但是这种 UStruct 毕竟还是少数，而且，这会增加不少内存消耗，因为这实际上产生了一个对象出来，对象至少占据多大内存，它是一点都不会少的。

4，TOptional<>

UE 里有一个工具就很有用，可以解决指针缺失的情况下的空值概念问题——TOptional<>。AS 脚本对此进行了绑定和优化， 可以在 AS 里愉快地使用这个工具。

这里稍微拓展一下，TOptional<> 类似于 C++标准里的 std::optional，UE 对很多 C++标准库里的有用工具（比如智能指针）都写了自己的实现，这样更加可控，也更能与 UE 的体系相结合。在其他编程语言里，也有类似这种工具，比如 Rust 的 Option<>，和 C++的这个，使用起来基本一致。

当你需要表达无或者空的概念，在没有指针的情况下， TOptional<> 是一个很好的选择。

用法示例

```cpp
TOptional<float> OptionalValue;
OptionalValue = 3.14;

if (OptionalValue.IsSet())
{
    Print(f"Value is: {OptionalValue.GetValue()}");
}
```

# 明明修改了那个变量，为什么没有生效

一句话总结：没明确区分 Struct 的引用与复制。

这个错误源于对 C++ 的认知不足或者疏忽。

记住一句话，默认情况下，AS 里的所有对象都是复制传递的（除了函数传参的时候）。这和 C++ 的默认行为一致，唯一的例外是：**AS 函数的参数默认是只读的**，而不像 C++ 会默认复制。

当你不需要修改原对象的时候，使用复制还是引用，结果上来说没有什么差别，性能上，引用大多数时候比复制好，对象越大，效果越明显。
然而，当你需要修改原对象的时候，误用了复制，那么，你修改的是原对象！这会导致匪夷所思的行为，让你陷入一个困境——我明明修改了它，但是为什么没有变化呢？
这种情况比较常出现在从 TArray<> 里取出某个值的时候，比如

```cpp
TArray<AActor> MyActors = GetActors(); // some functions to get Actors
auto Actor = MyActors[0]; // I am sure MyActors is not empty!
Actor.DoSomethingToModifyItself();
```

这个示例中，DoSomethingToModifyItself() 函数修改的是一个复制品，并不会影响原本的那个 Actor。
承接变量的时候，需要这么写

```cpp
auto& Actor = MyActors[0];
```

此时，Actor 就确确实实的代表了原来的首位元素了。

有人会说，那么我都写引用，这样不就好了吗？看情况吧。

对于 UObject 来说，写复制和引用，性能上几乎没差别。对于 UStruct 来说，当 UStruct 比较大的时候，复制会有复制的性能消耗，但是 AS 的 UStruct 被建议使用作为一个简单容器，一般不建议用来存放大型的对象，另外有很多时候，我们希望参数不受原来 UStruct 的影响，所以也会考虑复制来用的。

实际上，在 C++ 中有一个最佳实践：在不需要修改对象的情况下，能加 `const` 就加上。再配合这条——需要修改原对象的时候，如果不是直接操作原对象，那么就用引用。结合可得：

当用新变量承接新对象的时候，需要考虑两个维度，

- 不需要修改它 + 不需要复制一份：const auto&
- 不需要修改它 + 需要复制一份：const auto
- 需要修改它 + 修改原对象，不需要复制一份：auto&
- 需要修改它 + 修改复制后的对象：auto

这里的 auto 可以替换为实际类型，比如 AActor。

接着，简单提一提例外情况了。
这在官方文档里有写，但是如果不体验一下，有可能会忘记。默认情况下，AS 的函数参数是只读的。如果想要修改 Struct，需要在类型后加`&`。它为什么这么设定呢？首先，是为了写得简单些，不用每次都加上 const &；其次，是为了一些性能提升，如果在函数传参时默认复制一份，如果有人经常这么写，一旦这种函数调用量大了，性能损耗积累起来也大的（这种情况发现很难，因为结果一致，并没有程序错误）。

```cpp
// Change the parameter struct so its number is randomized between 0.0 and 1.0
UFUNCTION()
void RandomizeNumberInStruct(FExampleStruct& Struct)
{
    Struct.ExampleNumber = Math::RandRange(0.0, 1.0);
}
```

个人认为，这个修改出来的例外情况挺省心的。这个影响比较多的是 UStruct 以及 int、float 等原生类型。对于 UObject，会涉及到指针的概念，很多时候我们都是调用它的成员和函数，而不是修改它这个指针本身，也许会用到 = nullptr 的操作，但是直接将其修改为另外一个实例的情况较少。对于 UObject，这里得区分修改 UObject 指针本身和修改指针指向的对象，函数传参的限制只是限制了修改 UObject 指针本身。

这里稍微延伸一点，UObject 本质是 UObject@ 这个叫做句柄的东西，不是对象本体，句柄类似于简化版本的 C++的指针，而 UStruct 本质是值类型，就是对象本体。两者的访问成员的方式都是用点号，UE-AS 为了方便书写，特意取消了 UObject @ 这个句柄的标识@，这就导致了 UObject 和 UStruct 的认知难度，两者看起来一样，但是真的很不一样、很不一样！

为了方便理解，你可以将 AS 里的 UStruct 视同为和 int 和 float 等基础类型一致就好，都是代表对象本体。AS 脚本代码中，只有 UObject 不是对象本体。

# 加减乘除的运算符也有先后顺序的限制吗

一句话总结：在 AS 里，加减乘除等需要有两个变量参与运算的符号，实际上可以理解为类的成员函数，符号在类型的左边和右边，分别对应着不同的函数。

在 C++ 里，为了给程序最大的自由，这种两个变量参与运算的符号，很多都是谁前谁后都没问题的设计。
但到了 AS 里，有的类型就因为绑定的时候没有做完全的绑定，会导致颠倒过来就不成了，比如 FVector \* 5.0 可以，反过来写 5.0 \* FVector 就不行了。

以下是 AS 脚本插件的 FVector 与 float64 的乘法绑定，这种绑定的写法，只支持 FVector \* 5.0 的形式。

```cpp
FVector_.Method("FVector opMul(float64 Scale) const", METHODPR_TRIVIAL(FVector, FVector, operator*, (double) const));
```

那么，如果让 5.0 \* FVector 也受到支持呢？

C++ 里如何实现的呢？源码是这样的，声明了一个全局函数，这样编译器就可以识别到了。

```cpp
template<typename T, typename T2 UE_REQUIRES(std::is_arithmetic_v<T2>)>
FORCEINLINE TVector<T> operator*(T2 Scale, const TVector<T>& V)
{
    return V.operator*(Scale);
}
```

但是 AS 不是按照 C++的方式来绑定全局函数的，它提供了一个方便的绑定写法，使用 opMul_r 来表示当前类在符号右侧（即符号在类的左边）的情况。

基于此，我们可以给 FVector 增加一个成员函数的绑定，让其支持在符号右侧的运算。

```cpp
AS_FORCE_LINK FAngelscriptBinds::FBind Bind_FVector(static_cast<int32>(FAngelscriptBinds::EOrder::Late) + 1000,[]
{
    FAngelscriptBinds ThisBind = FAngelscriptBinds::ExistingClass("FVector");


     ThisBind.Method("FVector opMul_r(const float64 Scale)", [](const FVector& V, const double Scale) -> FVector
     {
       return V * Scale;
     });
});
```

因为 int 、float32 可以隐式转换为 float 类型，我们让其支持 float64，那么 int、float32 也可以使用了。

现在，就可以愉快地写 5 \* FVector 了。

为什么这个没有加入 FVector 的默认绑定中呢？个人猜测大概就是这么一种认知吧，把符号理解为函数，符号的左边是类，右侧是函数的输入参数，比较符合直觉，这种符合直觉的情况适合于设计人员理解。

虽然如此，我还是加上了 opMul_r 的，为什么呢？因为我更倾向于和 C++ 的写法一致。

# 为什么 default 语句有时候会导致崩溃，如何写类似 C++ 构造函数的代码

一句话总结： default 里不能动态生成任何东西，包括但不限于不能 NewObject，不能绑定 Event，default 只适合用来配置 property 的值。

default 可以对应为功能减弱版的 C++ 构造函数，减弱的功能是生成 UObject，也就是常写的 CreateDefaultSubobject<>。

那么就是想要实现 CreateDefaultSubobject 怎么办，对于 AActor 来说，用 UPROPERTY(DefaultComponent) ，如果需要覆盖，用 OverrideComponent 。AS 这种写法反而更加的舒服。如果要设置这些 DefaultComponent 的成员的值，用 default 语句。

default 语句和 DefaultComponent 组合使用，基本能实现 AActor 类型系列在使用 C++构造函数时候的常用功能。

有一个限制是，或者说还没有在 AS 里提供实现的是，C++的 CreateDefaultSubobject 可以创建任意的 UObject 而不仅仅限于 UActorComponent。如果继承的是 AActor，并且真的需要用到在构造阶段就想生成任意的 UObject， 可以写在 void ConstructionScript() 函数中，ConstructionScript 会在每次生成实例的时候都调用一次。

# 小结

本文主要围绕 WorldContext、空值表达、变量引用与复制、运算符号绑定、default 语句等话题展开，这些问题一句话就可以让人恍然大悟，如果不知道的话，也有其他复杂点的方法解决，这种情况，也可称之为一些奇技淫巧吧。

---
