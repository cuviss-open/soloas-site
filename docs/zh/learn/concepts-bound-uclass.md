---
title: "UE_Angelscript 认知篇——简述 UClass 被绑后，是什么形状"
order: 14
category: concepts
---
# UE_Angelscript 认知篇——简述 UClass 被绑后，是什么形状

本文主要描述声明为 UClass 的类，绑定到 AS 之后，是什么样的概念。

本文很多都是个人对绑定之后的 UClass 表现出的行为进行概括与归纳，带有较多个人理解色彩，如需更准确地底层描述与定义，建议阅读官方文档或者浏览脚本的绑定源码。

一个东西要想被绑，得先要满足一些条件，所以，先从什么样的 UClass 会被绑说起。

# 什么样的 UClass 和 UFunction 、UPROPERTY 会被 AS 绑定？

在官方文档里有提到：
`UCLASS()` 里有`BlueprintType` 或者有成员函数是`BlueprintCallable`的，会被绑定。
如果想要被跳过，可以添加`NotInAngelscript`修饰符。

其实，有个更简单的方式，能在蓝图里访问到的，不管是蓝图的细节面板还是蓝图的函数，只要能让蓝图访问到，它就会被 AS 绑定过去。

只有少数例外，比如 UE 的接口 UInterface，以及一些特殊的标识符比如`meta = (BlueprintInternalUseOnly = "true")`。
这个标记加上后，AS 就访问不到这个函数了，蓝图在一般情况下，也访问不到这个函数。

```cpp
// 这个函数没办法被AS访问到
    UFUNCTION(BlueprintCallable, meta = (BlueprintInternalUseOnly = "true"))
    void TestBlueprintInternalUseOnly()
    {
       UE_LOG(LogTemp,Warning,TEXT("Test BlueprintInternalUseOnly UFUNCTION Show"));
    }
};
```

# 绑定之后，成了什么形状，怎么用

AS 的写法很像 cpp，但是又不是 cpp, 一个重要的差别在于绑定的时候，隐藏了指针。

UE-AS 里没有指针的概念，脚本官方尽量避免任何指针的概念存在。

不过，毕竟是 cpp 绑定过来的，cpp 的指针不会凭空消失，那么原来的哪些指针去哪里了？UClass 绑定后都变成了什么？

经过一段时间的使用，这些 UClass 可以这么理解，它变成了**跟蓝图差不多的、可以判断是否 Valid （合法） 的一种对象**。

当 UClass 对象 Not Valid （不合法）时，它就是两种状态之一：空对象即 nullptr（空状态）、被回收系统标记为回收但是还没轮到它。

## 关于判空与判 IsValid

因为对象可以是 Not Valid 的，所以在 AS 使用 UClass , 还是得注意是不是 Vaild 的。

在 C++ 中，通常通过判空操作（指针是否为 `nullptr`）来检查对象的有效性，有时候也用使用 `IsValid()` ；而在蓝图中，通常使用 `IsValid()` 来检查对象是否有效；在 AS 里，这两种方式都支持使用，但是写法和 cpp 的有区别，并不能隐式地判空。（隐藏的脚本维护思想是，尽可能减少隐式地转换。）

判空写法，这么写：

```cpp
UAbilitySystemComponent ASC = Cast<AbilitySystemComponent>(GetOuter());
if (ASC == nullptr)
{
	Error("Cannot get UAbilitySystemComponent!");
	return;
}
```

（嗯，这是蓝图做不到，也不需要做到的。如果是 cpp ，很简洁，因为可以隐式转换。）
（说实话，我还是喜欢 cpp 指针判空的隐式转换写法，奈何脚本官方坚持原则。）

IsValid 写法，这么写：

```cpp
UAbilitySystemComponent ASC = Cast<AbilitySystemComponent>(GetOuter());
if (!IsValid(ASC))
{
	Error("Cannot get UAbilitySystemComponent!");
	return;
}
```

（这里的 IsValid 明显是一个全局作用域的函数，与那些定义在类里的不一样，需要注意。）（在判 IsValid 上，蓝图还是有巨大好处的，写这个的时候，蓝图拉跟线就可以了。）

两者的区别，就是它们概念上的差别，Valid 还考虑到了垃圾回收系统的标记。
大多数情况下，使用哪种都不是问题。

## 关于成员与成员函数的使用

用一个类，主要就是用它的成员、成员函数。

如果成员是其他的类，当不确定是否一定合法时，使用前最好记得判空或判 IsValid。

所有的函数调用、成员调用，都是用 `.` 符号， 没有 `->`符号。

有时候会发现，用 `.` 符号能访问到某个成员，同时它还有一个 Get 函数。这种情况是 AS 自身的处理，如果某个成员有 Get 函数，就默认可以使用 `.` 符号来访问了。不过，访问归访问，想要修改的话，如果这个成员没有暴露给外部访问（一般设置了 Get 函数，都没有暴露给外部访问）同时没有 Set 函数，那么使用 `.` 符号只能获取，而不能去赋值，也就是不能用`=`。
举个例子，假如有个 cpp 的类，给蓝图暴露了 FloatValue， 但是 IntValue 只给了一个 Get 函数。

```CPP
UClass()
class AExampleActorType : AActor
{
	// 略
	int IntValue = 15;

	UPROPERTY(BlueprintReadWrite)
	float FloatValue = 6.0;

	UFUNCTION(BlueprintCallable)
	int GetIntValue()
	{
		return IntValue;
	}
};
```

那么在 AS 里，有这些情况发生

```cpp
class AExampleActor_AS : AActor
{
	UFUNCTION(BlueprintOverride)
    void BeginPlay()
    {
    // 生成一个 AExampleActorType 类的实例
    AExampleActorType Example = SpawnActor(AExampleActorType);；
    // Example 可以无障碍地读写 FloatValue
    Example.FloatValue = 8.0；
    // Example 可以读 IntValue, 并不用写 GetIntValue(),当然写也可以。
    Print(f"{Example.IntValue}");
    // 下面这句会报错，不支持写入。如果 IntValue 有一个Set 函数，那么就可以。
    Example.IntValue = 3;
    }
}
```

拓展，AS 的方法以 `Get..()` 或 `Set..()` 开头的，可以在声明最后加上 `property` ，然后可以当作 properties 一样使用。这叫做 Property Accessor Functions。注意注意！ 自动绑定默认给加上了，使用方便的同时，可能会让人产生一些疑惑。

简单地说， `.` 符号可以访问成员函数的 Get 、 Set 方法的值，将其类似地当作自己的成员。这本质上是一个语法糖。

所以，AS 里输入`.` 符号后出现的提示里，排在前面的并不都是它的实际成员，还可能有一些是成员函数转换过来的。

贴下文档里的官方示例：

```cpp
class AExampleActor : AActor
{
    // property 这个关键词让这个成员函数的值被类似地当作普通成员来访问
    // 这里是 AS 里写的，所以需要加了这个关键词，而 cpp 里的绑定，会默认加的。
    FVector GetRotatedOffset() const property
    {
        return ActorRotation.RotateVector(FVector(0.0, 1.0, 1.0));
    }

    UFUNCTION(BlueprintOverride)
    void BeginPlay()
    {
        // 这里的 RotatedOffset 等价于 GetRotatedOffset()
        Print("Offset at BeginPlay: " + RotatedOffset);
    }
}
```

Cpp 的绑定，所有以`Get...()` 开头的方法，都可以当作 property 来访问，也就是说，`Actor.ActorLocation` 等价于 `Actor.GetActorLocation()`。

如果 Cpp 里只有 Set 开头的方法呢？这种情况下用`.` 符号只读是会报错的，但是后面加上`=`进行赋值却没问题了。

如果有人不喜欢这种自动绑定为 property 的功能，可以在项目设置里关掉：

![项目设置中的属性访问项](../../assets/learn/original-fork/concepts-bound-uclass-01.jpg)

这种隐式的转换带来一些问题：比如去掉了 Get 会新增好多伪成员（有时候 Get 并不是简单地取值，取值一般没有副作用，Get 可不一定），从而使得类的可直接访问成员变得不那么清晰；而去掉了 Set 会使得中间的过程被忽略（有时候 Set 并不是简单地赋值，赋值一般没有副作用，Set 可不一定， 比如触发个委托什么的），这使得类的成员赋值操作变得不那么清晰。

禁用之后，写的代码更加通用，在使用连续`.`调用成员和函数时，哪些是成员，哪些是函数，代码颜色会区分开，很清晰。

如果某天想要开启这个功能的时候，可以无痛衔接，另外，这么写的代码，拷贝回 cpp 也更方便了。值得注意的是，官方示例是按照没有禁用这个功能来写的，如果将官方示例放在了项目里，需要改一点点代码。

一定记住，如果要禁用这个功能，越早越好！

## 关于访问限制的简单说明

与 C++ 中的默认 `private` 访问权限不同，AS 中的类成员默认是 `public`，只有在需要时才会限制访问权限。

限制访问的时候，加上`private` 和 `protected` 等关键字，都是加在声明之前。
`private` 是只有当前类能访问。`protected`是当前类和子类可以访问。`public`不限制访问。

值得注意的是，若要将成员限制为 `private` 或 `protected`，需要在每个成员声明前显式添加修饰符。（它不支持 cpp 那样声明一个区域。）
