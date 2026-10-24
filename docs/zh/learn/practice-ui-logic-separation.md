---
title: "UE_Angelscript 实践篇——解耦 UI 蓝图的表现与逻辑"
order: 34
category: practice
---
# UE_Angelscript 实践篇——解耦 UI 蓝图的表现与逻辑

UI 设计的时候，有各种各样的 UI 部件，它们的显示是最好在 UE 编辑器中操作的，毕竟所见即所得。它们的逻辑部分，一般情况是写在 UI 的蓝图中，但是因为 UI 部件十分多，维护起来就十分的麻烦。

自从用了 AS 的来写 UI 的逻辑，分散在各处的 UI 逻辑都被统一写到代码文件中了，管理起来十分方便，而且实现了显示与逻辑的解耦，UI 编辑器只负责显示，而脚本代码负责逻辑处理。

这是官方文档里也比较少介绍的内容。

# UI 蓝图表现与逻辑分离的微型架构

一句话：每一个 UE 编辑器里的小部件，都继承于某一个 AS 的类。

一般情况下，是一对一的关系，UI 部件和 AS 的类虽然是子类父类的关系，但是因为有了绑定，可以理解为是一种伴生的关系。

UI 部件之间继承的关系，最好都转移到 AS 的类之间，也即，尽量不要出现 UI 蓝图之间的继承关系，为什么？因为一旦蓝图之间继承了，一对一的关系被打破，事情变得麻烦，修改起来不那么直观了，这种情况多了之后，也许复杂度就大大提升。

以下，都以 Example_Widget_UMG.as 文件为简单的例子加以拓展描述。

这个微型架构的最开始，肯定是从 cpp 那里继承下来一个 UI 相关的类。

```cpp
class UExampleWidget : UUserWidget
```

# UI 蓝图 与 AS 类成员的对应关系

每一个勾选为变量的 UI 蓝图部件，都会自动生成一个蓝图中的变量，而这个变量，可以在 AS 里进行绑定。

这个代码就是将 UI 蓝图名为 MainText 的 UTextBlock 绑定到 AS 里作为变量使用。
一旦绑定，蓝图的变量栏里就不会再出现这个变量。当然，蓝图还是可以使用这个变量的（如果蓝图里还想写逻辑）。

```cpp
class UExampleWidget : UUserWidget
{
	// 将名为 MainText 的蓝图变量绑定到此 AS 变量
    UPROPERTY(BindWidget)
    UTextBlock MainText;
}
```

拓展：UI 蓝图经常有各类动画，动画也是可以绑定的，代码参数如下。

```cpp
    UPROPERTY(BindWidgetAnim)
    UWidgetAnimation OnSpawned;
```

经过上面的操作，可以将需要的变量都绑定好，之后就是写逻辑了。

# 预构造和构造函数

预构造函数和构造函数是经常要用的，它们的使用方式，与 UI 蓝图区别不大。

```cpp
	UFUNCTION(BlueprintOverride)
	void PreConstruct(bool IsDesignTime)
	{
		AttributeNumber.Font.Size = 12;
	}

   UFUNCTION(BlueprintOverride)
    void Construct()
    {
    }
```

# UI 事件的绑定

如果是当前 UI 的类就有的事件，那么直接覆写对应的函数就可以了，比如 Button 就有 OnClicked、OnHovered 和 OnUnhovered 等。

如果想绑定的 UI 部件的事件，那么就需要用绑定委托的写法了。

这是 CommonUI 里的 Button 类的例子：

```cpp
// 当前类就是需要绑定事件的主体，覆写函数即可
	UFUNCTION(BlueprintOverride)
	void OnClicked()
	{
	}

// 需要绑定事件的主体是类的成员,就绑定这个成员的委托
YourBoundButton.OnButtonBaseClicked.AddUFunction(this,n"OnButtonBaseClicked")
```

# UI 蓝图的检查（可选）

OnValidateCompiledWidgetTree 这个函数是 cpp 里用于检查 UI 蓝图的，如果检查不通过，可以在蓝图里抛出编译错误。

因为 UI 蓝图部件众多，它们的参数有时候需要特殊的配置，比如同样的部件，复制了几份，它们的不同除了名称外，还必须设置某个参数不同，那么就可以在这里进行检查了。

不过 UI 蓝图的错误抛出代码没有提供蓝图版本，AS 里也无法直接调用。这时候就需要做一些手工的包装与绑定了。最终实现的效果示例如下：

```cpp
#if EDITOR
	UFUNCTION(BlueprintOverride)
	void OnValidateCompiledWidgetTree(const UWidgetTree BlueprintWidgetTree) const
	{
		if (OptionsClass.IsNull())
		{
			ShowCompileLog_Error("OptionsClass is null! Check and Set it in the Editor!");
		}
		if (UserFacingExperience == nullptr)
		{
			ShowCompileLog_Error("UserFacingExperienceDefinition is null! Check and Set it in the Editor!");
		}
		if (QuitGameClass.IsNull())
		{
			ShowCompileLog_Error("QuitGameClass is null! Check and Set it in the Editor!");
		}
	}
#endif
```

ShowCompileLog_Error 是自行在 cpp 里增加的一个函数，用于抛出错误。

这种包装与绑定略复杂，需要继承下来 UI 蓝图的常用类，然后再添加功能，这里略过。

# UI 蓝图与其他类的解耦交互（可选）

UI 蓝图与其他类交互时，通常需要编写大量引用代码，其中委托可以用来做一定程度的解耦，但是委托毕竟还是至少需要单向引用的，有没有办法让互不知道的两个类相互传递信息呢？有的，就是全局广播系统 UGameplayMessageSubsystem 。

这个 SubSystem 有 AS 的绑定，官方文档里提供了 [GameplayMessageRouter with Angelscript](https://github.com/IncantaUnreal/GameplayMessageRouter) 的绑定。其用法也比较简单，在 Readme 文件里可以看到，就不赘述。

通过这个系统，可以轻松地将 UI 蓝图与其他内容进行解耦。这个系统的使用记得注册为监听者之后，之后不需要的时候别忘记了注销。

# 总结

让表现归于表现，让逻辑归于逻辑，就是常说的前后端分离，AS 对 UI 蓝图的伴生绑定，让这得以轻松实现。

另外这也顺带解决了一个问题——UI 蓝图之间的 Cast 会带来逐渐膨胀的资产引用问题，而代码之间的 Cast 就没有关系。

解耦 UI 蓝图的表现与逻辑，好处多多，大家都有光明的未来！

---
