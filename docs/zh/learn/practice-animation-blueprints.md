---
title: "UE_Angelscript 实践篇——拓展动画蓝图，将主要计算逻辑用代码来写"
order: 31
category: practice
---
# UE_Angelscript 实践篇——拓展动画蓝图，将主要计算逻辑用代码来写

动画一般用蓝图来写比较方便调试，因为即时的反馈太重要了。UE 对动画蓝图做了很多的优化，尽可能地让动画蓝图的性能更好。不过再怎么优化，都只是底层的优化，动画蓝图里新增的逻辑还是运行在蓝图虚拟机上的。

在开发效率和性能之间取一个平衡点，就是使用比蓝图更快、同时拥有即时反馈的脚本语言了。经过测试，Angelscript 可以用来拓展动画蓝图。

脚本语言都没办法替代动画蓝图的虚拟机，因此，脚本语言更多是作为辅助工具使用。

# Angelscript 给动画蓝图带来的好处

1、对于更喜欢文字脚本的人来说，能用文字脚本来写就不会用蓝图连连看的，满足这部分人群。至于版本管理，方便比对修改什么的，就不详说了，写过代码的大都懂。

2、如果动画蓝图没有使用多线程计算（像 Lyra 项目那样，UE 里开启多线程优化计算），那么动画蓝图的计算可能会成为性能瓶颈，此时将部分代码转移给 Angelscript ，或有较为明显地改善。（这个推论基于 AngelScript 相较于蓝图的速度优势，具体效果仍需经过实际测试。）

3、如果动画蓝图使用了多线程计算（像 Lyra 项目那样，UE 里开启多线程优化计算），因为计算发生在非游戏线程，那么 Angelscript 提升的性能感知就不会有多大了。（这个推论基于 AngelScript 相较于蓝图的速度优势，具体效果仍需经过实际测试。）

# Angelscript 如何给动画蓝图写各类函数

总体而言，跟其他蓝图很相似。

1、从 UAnimInstance 继承下来一个类，让动画蓝图继承 AS 里的类。

2、 写的所有函数，只要加上   UFUNCTION() 都可以被动画蓝图调用，需要注意的是，在启用了多线程更新时，必须加上 Meta = (BlueprintThreadSafe) 。

3、BlueprintThreadSafe 的标识是告诉蓝图，我这个函数是线程安全的，可以运行在其他线程。至于是不是真的线程安全，需要自己保证。如何保证，下文有专门提及。

4、状态的状态节点，标签要对，函数前面要对，这样才可以被识别和使用。

```cpp
    // 函数参数必须标记为 &，可变引用，否则在蓝图细节面板里没办法识别。余同。
    UFUNCTION(BlueprintCallable, Meta = (BlueprintThreadSafe))
    void UpdateIdleState(FAnimUpdateContext& InContext, FAnimNodeReference& InNode)
```

5，大量的 BlueprintInternalUseOnly 函数需要暴露给 AS ，不然调用不到。暴露这类函数的方法可以参考本系列文章中的“绑定篇”，有专门写如何暴露 BlueprintInternalUseOnly 函数的。

6、对动画蓝图节点的处理在 cpp 里大量使用了蓝图函数库，调用起来没那么直观，可以将其用 Mixin 的方式在 AS 里处理下。

```cpp
mixin bool
IsStateBlendingOut(const FAnimNodeReference& InNode, const FAnimUpdateContext& InContext)
{
	return InNode.ConvertToAnimationState().IsStateBlendingOut(InContext);
}

// 之后就可以这么调用这个函数了
bool bIsStateBlendingOut = InNode.IsStateBlendingOut(InContext);
```

# 最难的是动画蓝图的多线程

难点在于理解 UE 动画蓝图多线程的调用流程，需要下点功夫。

## 动画蓝图如何缓存数据给非游戏线程

在 Lyra 项目里，我们可以发现 Property Access 这节点被大量地使用。这个节点真的是 UE 为了动画师的快乐而将痛苦埋在了代码里。

经过梳理，Property Access 缓存数据的节点在动画流程中大致的运行流程如下。

![动画属性缓存更新流程](../../assets/learn/original-fork/practice-animation-blueprints-01.jpg)

可以看到，这个 Property Access 帮我们做了一件事——即缓存需要游戏线程里用到的数据，从而避免数据竞争问题，确保线程安全。这个方式是蓝图专属的，因为蓝图在编译的时候，会查找这些 Property Access ，然后自动生成一些代码。嗯，没错，生成代码，就可以理解为它就是另外一种形式的宏。

如果是 cpp 里，为了线程安全，有两种缓存数据的方式。
1，从一个叫做 FAnimInstanceProxy 的 UStruct 里获取，这个 Proxy 会同步动画的一些核心数据，比如 GetActorTransform 等，这类核心数据可以从它获取到，是线程安全的。
2，手工地将需要用到的数据保存在继承下来的 UAnimInstance 或 FAnimInstanceProxy 中，更新这些数据的操作写在 NativeUpdateAnimation 里（只是复制，不做过多计算）。

## AS 如何缓存数据给非游戏线程

AS 里，缓存数据的地方和 cpp 差别不大，只是不能继承 FAnimInstanceProxy ，所以主要将数据缓存在继承下来的 UAnimInstance 里了，用的更新函数是 BlueprintUpdateAnimation 。

如果绑定了 FAnimInstanceProxy 的函数，也是可以调用一些核心数据，这样就省去了缓存核心数据的代码了。

以下是在 AS 里调用 FAnimInstanceProxy 里的函数对比自行缓存了对应的核心数据，经过对比，两个 Log 的内容一致。

```cpp
// 在 AS 中调用 FAnimInstanceProxy 中的函数
System::LogString(f"GetProxyOnAnyThreadBP : {GetProxyOnAnyThreadBP().GetActorTransform().GetLocation()}");

// 自行缓存了对应的核心数据，CacheOwningActorData 是 AS 里定义的 UStruct
System::LogString(f"CacheOwningActorData : {CacheOwningActorData.ActorLocation}");

// CacheOwningActorData 会在 BlueprintUpdateAnimation 函数里更新。

// 经过打印测试，两者同步更新，输出一致。
```

以上，可以佐证 Proxy 会实时更新 Actor 的位置信息。 绑定 Proxy 还是有点用的，省了一些同步更新缓存数据的事情。

# AS 对于动画蓝图的不足之处

1、不支持动画蓝图的接口。

原因是 AS 全面禁用了 UE 的接口，而动画蓝图的接口也同样被禁用了。所以，动画蓝图里主动画与动画层接口之间的交互就没多少办法了。

好在于，一开始就没想着用纯代码的方式写动画逻辑，因为状态机目前还是没办法替代的。

2、AS 的类只能被蓝图继承，而不能反过来，故引起交互的麻烦。

如果不能全用 AS 来写主要逻辑，或者已有的动画蓝图不好全盘修改的时候，就会产生这些问题了。

如果想调用已有的动画蓝图内容，普通的类型还好，可以传参然后修改这个传入的参数，但要是这个动画蓝图还使用了一些蓝图结构体或蓝图枚举类型的时候，就麻烦起来了。

目前的解决方式就是如果 AS 里处理起来过于复杂，蓝图补充就好了。

3、Property Access 确实好用，AS 用不了。

虽然 Cpp 也用不了，但是它有 FAnimInstanceProxy， AS 想要用 FAnimInstanceProxy 需要绑定，而且不能继承它。于是 AS 在缓存游戏线程的数据这个事情上，逊于蓝图和 Cpp 了。

# 拓展相关——动画通知，可以完全用 AS 写

动画通知，其实就是一普通蓝图，用 AS 来写一点问题都没有。

# 拓展相关—— BlueprintSafe 函数

UAnimInstance 有 45 个 BlueprintSafe 函数，很多可以直接用到多线程更新的节点里（UE5.4.4版本）。

```cpp
1: WasAnimNotifyTriggeredInStateMachine
2: WasAnimNotifyTriggeredInSourceState
3: WasAnimNotifyTriggeredInAnyState
4: WasAnimNotifyStateActiveInStateMachine
5: WasAnimNotifyStateActiveInSourceState
6: WasAnimNotifyStateActiveInAnyState
7: WasAnimNotifyNameTriggeredInStateMachine
8: WasAnimNotifyNameTriggeredInSourceState
9: WasAnimNotifyNameTriggeredInAnyState
10: RequestTransitionEvent
11: QueryTransitionEvent
12: QueryAndMarkTransitionEvent
13: IsSyncGroupBetweenMarkers
14: IsSlotActive
15: HasMarkerBeenHitThisFrame
16: GetTimeToClosestMarker
17: GetSyncGroupPosition
18: GetRelevantAnimTimeRemainingFraction
19: GetRelevantAnimTimeRemaining
20: GetRelevantAnimTimeFraction
21: GetRelevantAnimTime
22: GetRelevantAnimLength
23: GetInstanceTransitionTimeElapsedFraction
24: GetInstanceTransitionTimeElapsed
25: GetInstanceTransitionCrossfadeDuration
26: GetInstanceStateWeight
27: GetInstanceMachineWeight
28: GetInstanceCurrentStateElapsedTime
29: GetInstanceAssetPlayerTimeFromEndFraction
30: GetInstanceAssetPlayerTimeFromEnd
31: GetInstanceAssetPlayerTimeFraction
32: GetInstanceAssetPlayerTime
33: GetInstanceAssetPlayerLength
34: GetDeltaSeconds
35: GetCurveValueWithDefault
36: GetCurveValue
37: GetCurrentStateName
38: GetAllCurveNames
39: GetActiveCurveNames
40: ClearTransitionEvents
41: ClearAllTransitionEvents
42: CalculateDirection
43: BlueprintThreadSafeUpdateAnimation
44: Blueprint_GetSlotMontageLocalWeight
45: Blueprint_GetMainAnimInstance
```

---
