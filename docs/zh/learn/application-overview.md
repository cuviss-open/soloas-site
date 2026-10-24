---
title: "UE_Angelscript 应用"
order: 1
category: getting-started
---
# UE_Angelscript 应用

所有内容都或多或少包含个人的见解，仅供参考。

# 文档概要

主要是官方文档的概要笔记。

[UnrealEngine-Angelscript 官方文档概要](official-documentation-overview.md)

# 入门篇

主要是如何部署一个可以使用 Angelscript 的 UE 引擎，内容尽量新手向。

[UE_Angelscript 入门篇--安装引擎，打开封印之门](getting-started-install-soloas.md)
[UE_Angelscript 入门篇--再识引擎，似同非同](getting-started-engine.md)

# 认知篇

主要是使用 Angelscipt 作为 UE 脚本语言的一些基本的认知。

[UE_Angelscript 认知篇——简述 UClass 被绑后，是什么形状](concepts-bound-uclass.md)
[UE_Angelscript 认知篇——应用的项目结构参考](concepts-project-structure.md)
[UE_Angelscript 认知篇——理解：复制、引用](concepts-copy-and-reference.md)

# 实践篇

主要是一些值得书写的实践，这些实践内容往往和普通的 UE 开发有一定的差异。

[UE_Angelscript 实践篇——拓展编辑器，就跟喝水一样简单](practice-editor-extensions.md)
[UE_Angelscript 实践篇——解耦 UI 蓝图的表现与逻辑](practice-ui-logic-separation.md)
[UE_Angelscript 实践篇——拓展动画蓝图，将主要计算逻辑用代码来写](practice-animation-blueprints.md)
[UE_Angelscript 实践篇——自由的组件，实现功能模块化](practice-component-modularity.md)
[UE_Angelscript 实践篇——关于类成员的垃圾回收与反射问题](practice-gc-reflection.md)
# 绑定篇

主要是将 cpp 内容绑定给 AS 使用的相关介绍以及一些疑难杂症的解决方案。

[UE_Angelscript 绑定篇——综述：暴露更多内容给 AS 和蓝图](binding-overview.md)
[UE_Angelscript 绑定篇——避坑：不踩一下，怎知是坑](binding-pitfalls.md)
[UE_Angelscript 绑定篇——解决方案：Unreal Interfaces 缺失的缓解药剂](binding-unreal-interfaces.md)
[UE_Angelscript 绑定篇——解决方案：绑定 Native 和 DataTable 的 GameplayTags](binding-gameplay-tags.md)
[UE_Angelscript 绑定篇——解决方案：BlueprintInternalUseOnly 函数的增强处理方式](binding-blueprint-internal-use-only.md)

手工绑定
[UE_Angelscript 绑定篇——手工绑定 1 - 基础理解](binding-manual-basics.md)
[UE_Angelscript 绑定篇——手工绑定 2 - 绑定手册](binding-manual-reference.md)

高阶部分
[UE_Angelscript 绑定篇——Delegate 自由调用，看似虚幻，实尽在手中](binding-delegates.md)

# 奇技淫巧

主要是让写代码更舒服、更高效的一些技巧。

[UE_Angelscript 奇技淫巧](tips-mixins-and-reflection.md)
[UE_Angelscript 奇技淫巧2：你挠头不解的问题，有时只需一句话](tips-five-common-surprises.md)
[UE_Angelscript 奇技淫巧3：选 if(Obj) 还是 if(Obj != nullptr)？秒选 if(Obj)](tips-object-validity-checks.md)

# 源码篇

直接分析源码内容，复杂度高一个级别，小白慎入，大胆的除外。

[UE_Angelscript 源码篇 1：UE 的类绑定到 AS 的流程](internals-ue-types-to-angelscript.md)
[UE_Angelscript 源码篇 2：AS 的类绑定到 UE](internals-angelscript-classes-to-ue.md)

# 杂谈

杂谈而已，记录一些有意思的探索

[杂谈：没有人能拦我用指针，除了我自己](essays-pointers-and-ownership.md)
[杂谈：没有人能拦我用 Lambda，除了我自己](essays-lambda-design.md)
[杂谈：Angelscript 动态类型、异步、多线程，全都要](essays-dynamic-types-and-tasks.md)

---
