# 核心扩展

## UE 接口

- AS 支持继承 C++、AS、蓝图接口。
- 编辑器脚本支持新建接口，蓝图可以继承 AS 建立的接口。

```angelscript
interface IDamageSource
{
    int ComputeDamage(int Value);     // 约定大家都能接收的调用。
}
class UReceiver : UObject, IDamageSource
{
    UFUNCTION(BlueprintOverride)
    int ComputeDamage(int Value) { return Value + 17; } // 实现这个调用。
}
```

```angelscript
IDamageSource Target = Cast<IDamageSource>(Object); // Object 是已有对象引用。
if (Target != nullptr)
    Print(f"{Target.ComputeDamage(5)}");             // 通过接口调用。
```

- 接口里的方法不用写 `UFUNCTION`，会自动注册为蓝图事件：蓝图可以调用，也可以在蓝图中实现。需要纯函数（蓝图中没有执行引脚，只用于取值）时写 `UFUNCTION(BlueprintPure)`。
- 在类中实现接口方法时，写 `UFUNCTION(BlueprintOverride)`。
- 没有默认方法体的接口方法，实现接口的类必须用 `UFUNCTION(BlueprintOverride)` 实现，否则编译报错。
- 带默认方法体的接口方法，类可以不重写，直接使用默认实现；修改默认方法体支持软重载。
- 修改接口签名、增删接口方法或改变继承关系后，重启编辑器。
- 新建脚本接口的打包和预编译使用尚未支持。

## 蓝图继承

- 脚本可以继承蓝图父类。
- 脚本可以继承蓝图接口，见 [UE 接口](#ue-接口)。

继承蓝图父类时，先在项目 `Config/DefaultEngine.ini` 中给蓝图取一个名字，把路径换成你的蓝图资产路径：

```ini
[SoloASCoreExtensions]
+BlueprintAliases=(Name=BP_Enemy,Path="/Game/Blueprints/BP_Enemy.BP_Enemy")
```

脚本只用名字：

```angelscript
import blueprint BP_Enemy;

class UEnemy : BP_Enemy
{
    UFUNCTION(BlueprintOverride)
    void OnBlueprintDeath() {}        // 覆盖蓝图已有的事件。
}
```

也可以用 `CallBlueprint`、`SetBlueprintProperty`、`GetBlueprintProperty` 调用已有蓝图对象的函数和变量。蓝图继承脚本类时，编辑器会在脚本父类重载后更新蓝图子类。

## 蓝图结构体

在项目 `Config/DefaultEngine.ini` 中配置结构体的脚本名和资产路径：

```ini
[SoloASCoreExtensions]
+BlueprintStructBindings=(Name=FMyStruct,Path="/Game/Structs/ST_MyStruct.ST_MyStruct")
```

嵌套使用的蓝图结构体也要逐个登记。配置后重启编辑器；修改已被脚本使用的蓝图结构体后，也要重启编辑器。

## 原生事件的父类实现

重写原生事件时，可从脚本调用 Unreal 父类的原始实现，保留原生默认行为。

## 委托和容器算法的 lambda

使用显式捕获指定变量。按值捕获写类型和变量名；之后修改原变量，不会改变捕获的值。

- 委托：为委托绑定 lambda，并记住当时的变量值。动态和原生委托都可使用：单个回调用 `BindLambda`，多播事件用 `AddLambda`。委托 lambda 使用有类型的值捕获，不支持空捕获、`this`、引用捕获或嵌套 lambda。

```angelscript
int Number = 17;
FString Text = "Ready";
FTimerDynamicDelegate Timer;
Timer.BindLambda([int Number, FString Text]() {
    Print(f"{Text}: {Number}");        // 使用绑定时保存的值。
});
System::SetTimer(Timer, 0.1f, false);   // 稍后执行一次。
```

- 容器算法：数组支持 `Sort`、`StableSort`、`FilterByPredicate`、`FindByPredicate`、`IndexOfByPredicate`、`ContainsByPredicate` 和 `RemoveAll`；集合及映射支持 `FilterByPredicate`，映射还支持 `KeySort`、`ValueSort`。算法同步执行，支持空捕获、显式值捕获、局部变量的显式引用捕获；对象实例方法还支持 `[this]`。不支持 `[&]`、捕获初始化或嵌套 lambda。

```angelscript
TArray<int> Values;
Values.Add(3);
Values.Add(1);
Values.Add(2);
int Direction = -1;
// 捕获 Direction；为 -1 时从大到小排。
Values.Sort([int Direction](int A, int B) { return Direction * A < Direction * B; });
```

## 按需关闭功能

启用核心扩展插件后，以上能力默认开启。插件默认配置位于 `Config/Engine.ini`；项目设置写在项目 `Config/DefaultEngine.ini`，例如关闭带捕获的 lambda：

```ini
[SoloASCoreExtensions]
bEnableExplicitCaptureLambda=false
```

脚本接口使用 `bEnableScriptInterfaces` 开关。更改设置后重启编辑器，并重新生成预编译缓存。
