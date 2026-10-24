---
title: "UE_Angelscript 入门篇--再识引擎，似同非同"
order: 11
category: getting-started
---
# UE_Angelscript 入门篇--再识引擎，似同非同

接上篇 [UE_Angelscript 入门篇--安装引擎，打开封印之门](getting-started-install-soloas.md)

- 惊奇的声音：好像是未曾见过的人，你是谁？从哪里来？
- 疑惑的声音：这是？似曾相识，但又不同，这是哪里？
- 画外音：”桃源自古怡然乐，唯有奇缘到此津。“

# 前言

读此文前，需要以下几个前置条件：

- 已经安装 UE_Angelscript 的引擎，并且已经可以打开使用，一如 UE 原始版本的引擎。
- 已经安装有 VSCode , 并且下载了相应的 UE_Angelscript 插件。

本文使用的示例，为 UE_Angelscript 5.4 版本，环境配置等和上篇一致。

# 新建项目

和往常一样，新建一个项目即可，但是记得用 c++ 版本。为什么？因为后续可能用到 cpp 作为辅助，可以确保项目支持更底层的功能扩展，并方便与 Angelscript 脚本结合使用。

![第三人称C++项目模板](../../assets/learn/original-fork/getting-started-engine-01.jpg)

创建完成后，会进入 IDE ，以 Rider 为例，点击右上角的运行按钮，编译项目且运行

![Rider项目运行按钮](../../assets/learn/original-fork/getting-started-engine-02.jpg)

如果一切正常，编译完成后，会打开编辑器 Editor。因为勾选了初学者安装包，需要编译不少 Shaders，这部分内容会比较慢，卡在 45% 是正常现象，不要慌，只要还在动就耐心等待。

![着色器编译进度画面](../../assets/learn/original-fork/getting-started-engine-03.jpg)

# 进入工作区

引擎打开后，点击 Tools (工具)，里面有调整到 Angescript 工作区的快捷方式。

![编辑器脚本菜单入口](../../assets/learn/original-fork/getting-started-engine-04.jpg)

你也可以选择在项目文件夹下，用 VSCode 打开 Script 文件夹，这个文件夹就是 Angelscript 工作区。

跳转到 VSCode 之后，里面空空荡荡，因为还没有新建任何内容。

还记得你的引擎所在路径吧，去那里把所有的 Examples 文件拷贝过来，参考如下

![文件管理器示例目录](../../assets/learn/original-fork/getting-started-engine-05.jpg)

建议可以先拷贝 Examples 文件夹，另外几个文件夹的文件需要启动其他相关插件才能使用，初学者可以暂时忽略。

此时，Examples 文件夹为你提供了一批带有详细注释的参考代码，便于快速上手。

看看 Examples 文件夹下的 Example_Actor.as

![示例Actor类源码](../../assets/learn/original-fork/getting-started-engine-06.jpg)

里面有个 AExampleActorType 类，继承自 AActor，这个类默认会暴露给 Editor，在新建蓝图的时候，可以找到，如下图。

![蓝图父类选择窗口](../../assets/learn/original-fork/getting-started-engine-07.jpg)

你可以考虑复制一个文件，修改类名，然后去测试这些示例文件里提到的内容，如 UPROPERTY 的使用。

当保存.as 文件之后，如果没有错误，会立即在 Editor 里生效。

# 断点调试

VSCode 里按 F5 进入调试模式，左边点开调试的变量监测区。
![VS Code调试菜单](../../assets/learn/original-fork/getting-started-engine-08.jpg)

在 BeginPlay 或者其他想要调试的地方，打断点
![BeginPlay断点标记](../../assets/learn/original-fork/getting-started-engine-09.jpg)

例如，新建一个继承自示例类的蓝图 Actor，并将其放入关卡中，那么 Editor 里点击运行的时候，会触发断点。

![命中断点的变量面板](../../assets/learn/original-fork/getting-started-engine-10.jpg)

右上角的小按钮就是用来一步一步调试的，十分方便。
这跟蓝图里的断点调试有些类似。

# 无缝跳转

在原始 UE 中，Editor 支持无缝跳转到 C++ 的代码实现。而在 UE_Angelscript 中，通过引擎源码的改动，实现了从 Editor 到 Angelscript 的无缝跳转功能。这不仅支持从 Editor 跳转到 VSCode 查看 Angelscript 的代码，还可以从 VSCode 跳转回 Editor，查看相应的蓝图类。

例如，若某个蓝图类继承自 Angelscript 的类，你可以直接点击蓝图类中的父类链接，快速跳转到 Angelscript 的代码实现。

![蓝图父类信息标签](../../assets/learn/original-fork/getting-started-engine-11.jpg)

反之，在 Angelscript 的代码中点击类提示，也能跳转回蓝图类。

![脚本类的蓝图链接](../../assets/learn/original-fork/getting-started-engine-12.jpg)

此外，Editor 的组件交互、Level 里的实例 Actor 的跳转等功能同样被支持。

总之，凡是 cpp 与 Editor 的交互，Angelscript 大都实现了，甚至更丝滑。

# 总结

经过上面的基础操作，可以见到 UE_Angelscript 的引擎版本和原始版本看着差不多，但处处紧密融合，在交互上做了很多的工作，着实是为了设计游戏而量身定制的。

UE_Angelscript 的出现不是为了完全替代蓝图，而是作为 cpp 和蓝图的中间层，补全了 UE 缺少脚本语言的尴尬。

有人说，用 UE 的 cpp 也像脚本，热编译也还行；确实如此，UE 的 C++ 已经颇具脚本语言的特性，有人甚至戏称其为 U++，但还是太多模板代码了，同时还需要管理头文件和模块，这不应该是 Gameplay 主要做的事；热编译当前情况下还不够给力，等半秒和几秒，是完全不同的体验，每次编译 cpp 的时候，就总会想着，如果拥有蓝图这般实时的无感交互，不更好吗？

UE 当下还在开发自己的一套脚本语言，UE 也还有其他第三方的脚本语言。选择什么，是萝卜青菜，各有所爱。我的选择是，选一个经过项目检验的、在维护的、体验足够好的脚本语言，恰好 UE_Angelscript 基本满足了这些要求。

希望你对 UE_Angelscript 的探索充满乐趣，本系列文章如对你有所裨益，不胜荣幸！
