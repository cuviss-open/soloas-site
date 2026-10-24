---
title: "UE_Angelscript 认知篇——应用的项目结构参考"
order: 12
category: concepts
---
# UE_Angelscript 认知篇——应用的项目结构参考

经过一些摸索，总结了一点项目结构的规则。
这是我现在给自己定的，仅供参考。

# 继承关系----蓝图-->AS-->Cpp

## 所有 AS 里继承的类，都来自于 Cpp 的中间层。

双人成行的游戏代码的 AS 部分是公开的，通过简单地阅读可以发现，它的 Actor 继承都不是直接继承引擎的 AActor，而是单独的 AHazeActor，不过除了继承之外的使用过程中，AActor 还是正常用。

由此，可以想到，继承关系中，用一个中间层隔离引擎和 AS 代码，可以起到如下好处：
当需要增加或修改功能的时候，就往自己中间层里增加修改，而不会望着引擎的那个类，改也不是，不改也不是。另外，绑定和修改等等，也是这种中间层比较自由。

## 绝大部分蓝图的父类，都来自于 AS。

蓝图的好处是配置方便，不用写硬路径，所以用了 AS，蓝图在需要的时候，还是配合使用的。个人更喜欢将蓝图当作配置表，AS 代码里也很方便地知道哪个类被什么蓝图继承了，跳转也很方便。
蓝图的父类来自于 AS，方便在于快速迭代，AS 修改保存，立等可取，和在蓝图里写脚本，然后点击保存一样快。

AS 里将蓝图的类当作类成员，和 cpp 差不多，比如声明`UUserWidget`，可以用`TSubclassOf<UUserWidget>`

# 组合关系----都是 Actor + Component

## 关键的 Actor 继承链里包含 ModularGamePlayActors

这个模块在古代山谷或者 Lyra 项目里。
好处是，可以实现 GameFeature 的 AddComponent 自动添加。

## 定制专用 Actor 作为中间层

继承 Actor 是很常见的事情，为了不支持继承自 AActor 以及自由，定制一个自己的通用 Actor。如果一个不够，定制多个也不是不可以。

可选地，配置一个开关参数，参考 ModularGamePlayActors， 实现一下 GameFeature 的自动添加特性。

## 关键的 Component 继承自 ModularGamePlay

这些 Component 里有大量的胶水函数，使用起来比较方便，需要自己绑定一次，绑定的时候，函数模板需要特定地将返回类型变成对应的基类。

## 如用 UInterface ，打包进 ActorComponent

有些模块大量使用了 UInterface，重写是不可能重写的，能简单包装的，自然就包装起来了。

作用体将原本的 Actor 本体，转换为它的 Component 里。比如原本是 Actor 本体实现对话的接口，现在就让 Actor 的 Component 来实现。

# Subsystem----继承自AS 

AS 有自己的一套 Subsystem：

- `UScriptWorldSubsystem` for world subsystems
- `UScriptGameInstanceSubsystem` for game instance subsystems
- `UScriptLocalPlayerSubsystem` for local player subsystems
- `UScriptEditorSubsystem` for editor subsystems
- `UScriptEngineSubsystem` for engine subsystems
  里面通过继承暴露了很多有用的可覆写函数，所以，从这里继承下来省了很多事。

# GAS ----继承自AS 

GAS 系统（GameplayAbilitySystem) 本来暴露给蓝图的内容就不是很多，所以如果需要自己绑定，很麻烦，幸好官方提供了绑定的插件 AngelscriptGAS，只需要打开即可。

值得注意的是，有些对原生 struct 的绑定不得不进行二次包装（因为这个插件不修改引擎源码）。

另外，即使官方提供了很多绑定，仍然有些欠缺的，需要自己通过Mixin或者手工绑定了。
