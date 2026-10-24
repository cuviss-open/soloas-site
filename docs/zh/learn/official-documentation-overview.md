---
title: "UnrealEngine-Angelscript 官方文档概要"
order: 2
category: getting-started
---
# UnrealEngine-Angelscript 官方文档概要

# 主要介绍

脚本维护者： [Hazelight](https://angelscript.hazelight.se)，双人成行（ [It Takes Two](https://www.ea.com/games/it-takes-two) ）的制作公司。

脚本代码情况：是一个 UnrealEngine 的分支（fork)，为了和引擎交互更密切，修改了源码，提供了几个插件：Angelscript、AngelscriptGAS、AngelscriptEnhancedInput、AngelscriptStructUtils 。另外还提供了 [GameplayMessageRouter with Angelscript](https://github.com/IncantaUnreal/GameplayMessageRouter) 的绑定。

脚本编写平台： Vscode, 提供了插件 [Visual Studio Code Extension](https://marketplace.visualstudio.com/items?itemName=Hazelight.unreal-angelscript) 和 [Unreal Angelscript Clang-Format](https://marketplace.visualstudio.com/items?itemName=Hazelight.unreal-angelscript-clang-format)，支持自动补全等常见语言工具拥有的功能，相当方便。还有很重要的是，支持在 VSCode 里设置断点来 Debug。

脚本定位：在 cpp 和 蓝图之间，作为中间层。cpp 编译太慢，经常要重启编辑器，另外有大量的模板代码和注意事项；而蓝图编写太繁琐，复杂逻辑太麻烦，二进制不方便比对。AS 作为中间层，就解决了这两方面的问题。cpp 就作为给 AS 暴露更多的功能代码的一层，负责中转和处理需要性能的部分，蓝图就作为最终的配置资产，偶尔有一点点简单逻辑。

脚本语言特性：AS 静态类型语言，写法太特么像 cpp 了，就类似 cpp 的精简版，代码在 cpp 和 AS 之间迁移很方便。UE-AS 还做了大量的编写优化，比 U++ 写法简单很多。

美中不足：众口难调，脚本的维护方有一套自己的逻辑体系，虽然蓝图里的大部分功能在 AS 里都能用，但 UE 的接口 UInterface 没有支持。这会导致部分写在接口里的代码不能自动绑定到 AS, 在 AS 里也不能通过接口来调用函数，不过通过 AS 的 Mixin 特性，可以比较方便的绑定很多接口函数的调用了。如果有些接口的函数是需要覆写的，那么只能在 cpp 的子类里进行包装。

使用者要求：
会从源码编译引擎，不然只能下载官方编译好的某个特定版本，不是所有 UE 的版本都提供了二进制版。
会将 cpp 的代码封装给脚本使用，不然有些暴露给蓝图的功能用不了，比如部分异步调用的 latent 函数。

# Functions and BlueprintEvents

## Blueprint 可调用 AngleScript 的 Function

### 类方法

UFUNCTION()

```cpp
class AExampleActor : AActor
{
    UFUNCTION()
    void MyMethodForBlueprint()
    {
        Print("I can be called from a blueprint!");
    }
}
```

不需要声明为`BlueprintCallable`，因为这是默认的。
#cpp_different

### 全局作用域函数

加`UFUNCTION()`的全局作用域函数，可类似于静态函数，可被蓝图调用，相当于写在 Blueprint Function Libraries 一样。

```cpp
// Example global function that moves an actor somewhat
UFUNCTION()
void ExampleGlobalFunctionMoveActor(AActor Actor, FVector MoveAmount)
{
    Actor.ActorLocation += MoveAmount;
}
```

## Blueprint 可重写 AngleScript 的 Function

UFUNCTION(BlueprintEvent)

```cpp
class AExampleActor : AActor
{
    UFUNCTION(BlueprintEvent)
    void OverridableFunction()
    {
        Print("This will only print if not overridden from a child BP.");
    }
}
```

AS 不区分`BlueprintImplementableEvent` 和 `BlueprintNativeEvent` ，都是要有默认实现的，即都类似于`BlueprintNativeEvent`。
#cpp_different

建议区分基础实现与蓝图实现，这样可以确保蓝图里不会漏掉调用基础实现。

```cpp
class AExamplePickupActor : AActor
{
    void PickedUp()
    {
        // We always want this script code to run, even if our blueprint child wants to do something too
        Print(f"Pickup {this} was picked up!");
        SetActorHiddenInGame(false);

        // Call the separate blueprint event
        BP_PickedUp();
    }

    // Allows blueprints to add functionality, does not contain any code
    UFUNCTION(BlueprintEvent, DisplayName = "Picked Up")
    void BP_PickedUp() {}
}
```

## AngleScript 重写 Cpp 的 Function

UFUNCTION(BlueprintOverride)

```cpp
class AExampleActor : AActor
{
    UFUNCTION(BlueprintOverride)
    void BeginPlay()
    {
        Print("I am a BeginPlay override");
    }

    UFUNCTION(BlueprintOverride)
    void Tick(float DeltaSeconds)
    {
        Print("I get called every tick");
    }
}
```

visual studio code 里点击类，然后边上的电灯泡（Ctrl + .) 可以查看哪些可被重写。
提示里也会有。
AS 会自动去除 Cpp 函数里的前缀，如`BP_`、`K2_` 、`Received_`。（只针对一些没有声明函数显示名称的，即 DisplayName 。）

## AngleScript 调用 Super Function

### 重写 AS 的方法时

- 重写 AS 的方法时 ，基础方法没有`BlueprintEvent`的标记：
  函数声明之后加上 override，直接用 `Super::`。
  所有 AS 的方法默认都是 virtual 的。

- 重写 AS 的方法 时，基础方法有 `BlueprintEvent` 标记：
  加上标记：UFUNCTION(BlueprintOverride)
  **有 BlueprintEvent 标记的，就需要 BlueprintOverride，像重写 cpp 的一样**

```cpp
class AScriptParentActor : AActor
{
    void PlainMethod(FVector Location)
    {
        Print("AScriptParentActor::PlainMethod()");
    }

    UFUNCTION(BlueprintEvent)
    void BlueprintEventMethod(int Value)
    {
        Print("AScriptParentActor::BlueprintEventMethod()");
    }
}

class AScriptChildActor : AScriptParentActor
{
    // Any script method can be overridden
    void PlainMethod(FVector Location) override
    {
        Super::PlainMethod(Location);
        Print("AScriptChildActor::PlainMethod()");
    }

    // Overriding a parent BlueprintEvent requires BlueprintOverride
    UFUNCTION(BlueprintOverride)
    void BlueprintEventMethod(int Value)
    {
        Super::BlueprintEventMethod(Value);
        Print("AScriptChildActor::BlueprintEventMethod()");
// ……
```

出处：Hazelight documentation: Super function example（节选，其余行省略）。

### 重写 Cpp 的方法时

- 重写 cpp 的`BlueprintNativeEvent` 方法时，没办法调用 `Super::`(技术限制)。
  解决方案就是，声明一个`BlueprintImplementEvent`用来重写然后调用`BlueprintNativeEvent` 的方法，或者基础实现放在其他的`Callable`函数里。
- 重写 cpp 的`BlueprintImplementEvent` 方法时，没有可调用的内容。
- 其他函数，如果不是重写的，可以直接调用，不需要 Super。

总结，从 Cpp 继承的类，一般没有 Super 的命名空间， 不能在代码里写 Super::。
Super 调用父类方法，只建议从子方法调用当前方法的父类方法，而调用其他子方法的父类方法虽然可以，但是容易出错，AS 会报 warning ,如 `Calling Super::TestSuper from different child function BeginPlay_Implementationas`。

# Properties and Accessors

## 专有的类成员

不加`UPROPERTY()`标记即可。

## 暴露给 Unreal 的类成员

加`UPROPERTY()`标记即可。

#### 默认是 `EditAnywhere`

#cpp_different
可以增加编辑限制符

```cpp
class AExampleActor : AActor
{
    // Can only be edited from the default values in a blueprint, not on instances in the level
    UPROPERTY(EditDefaultsOnly)
    float DefaultsProperty = 10.0;

    // Can only be edited on instances in the level, not in blueprints
    UPROPERTY(EditInstanceOnly)
    FVector InstanceProperty = FVector(0.0, 100.0, 0.0);

    // The value can be seen from property details anywhere, but *not* changed
    UPROPERTY(VisibleAnywhere)
    FName VisibleProperty = NAME_None;

    // This property isn't editable anywhere at all
    UPROPERTY(NotEditable)
    TArray<int> VisibleProperty;
}
```

#### 默认是 `BlueprintReadWrite`

#cpp_different
可以增加读写限制符

```cpp
class AExampleActor : AActor
{
    // This property can be both read and written from blueprints
    UPROPERTY()
    float BlueprintProperty = 10.0;

    // This property can use `Get` nodes in blueprint, but not `Set` nodes
    UPROPERTY(BlueprintReadOnly)
    float ReadOnlyProperty = 0.0;

    // This property cannot be accessed by blueprint nodes at all
    UPROPERTY(BlueprintHidden)
    int NoBlueprintProperty = 5;
}
```

## `Category` 分类

类似于 Cpp 。

```cpp
class AExampleActor : AActor
{
    UPROPERTY(Category = "First Category")
    float FirstProperty = 0.0;

    UPROPERTY(Category = "Second Category")
    float SecondProperty = 0.0;

    UPROPERTY(Category = "Second Category|Child Category")
    FString ChildProperty = "StringValue";
}
```

## 方法变成属性来访问

AS 的方法以 `Get..()` 或 `Set..()` 开头的，可以在声明最后加上 `property` ，然后可以当作 properties 一样使用。这叫做 Property Accessor Functions。

```cpp
class AExampleActor : AActor
{
    // The `property` keyword lets this function be used as a property instead
    FVector GetRotatedOffset() const property
    {
        return ActorRotation.RotateVector(FVector(0.0, 1.0, 1.0));
    }

    UFUNCTION(BlueprintOverride)
    void BeginPlay()
    {
        // This automatically calls GetRotatedOffset() when used as a property
        Print("Offset at BeginPlay: "+RotatedOffset);
    }
}
```

Cpp 的绑定，所有以`Get...()` 开头的方法，都可以当作 property 来访问，也就是说，`Actor.ActorLocation` 等价于 `Actor.GetActorLocation()`。

## 访问限制

默认是 public，`private` 和 `protected` 加在声明之前。类方法也同样适用。

```cpp
class AExampleActor : AActor
{
    private FVector Offset;
    protected bool bIsMoving = false;

    bool IsMoving() const
    {
        return bIsMoving;
    }

    protected void ToggleMoving()
    {
        bIsMoving = !bIsMoving;
    }
}
```

# Actors 和 Components

`UCLASS()` 不是必须的，但可以加上，配置修饰符。

## Default Components

写在修饰符中。
`UPROPERTY(DefaultComponent)`

```cpp
class AExampleActor : AActor
{
    UPROPERTY(DefaultComponent)
    USceneComponent SceneRoot;
    UPROPERTY(DefaultComponent)
    UMyComponent MyComponent;
}
```

## Component Attachments

加上修饰符`RootComponent` 表示为 Root，组件默认挂在 root
加上修饰符`Attach =` 和 `AttachSocket =`可以自定义挂在的组件

```cpp
class AExampleActor : AActor
{
    // Explicit root component
    UPROPERTY(DefaultComponent, RootComponent)
    USceneComponent SceneRoot;

    // Will be attached to SceneRoot by default, as no attachment is specified
    UPROPERTY(DefaultComponent)
    USkeletalMeshComponent CharacterMesh;

    // Will be attached to the CharacterMesh' RightHand socket
    UPROPERTY(DefaultComponent, Attach = CharacterMesh, AttachSocket = RightHand)
    UStaticMeshComponent WeaponMesh;

    // Will be attached to the WeaponMesh
    UPROPERTY(DefaultComponent, Attach = WeaponMesh)
    UStaticMeshComponent ScopeMesh;
}
```

## Default Statements

默认的声明，关键字 default 加在语句之前。
用于 subobject 以及父类的 properties 的初始化。这类似于写在 Cpp 构造函数中。

```cpp
class AExampleActor : AActor
{
    UPROPERTY(DefaultComponent, RootComponent)
    USceneComponent SceneRoot;

    UPROPERTY(DefaultComponent)
    USkeletalMeshComponent CharacterMesh;

    // The character mesh is always placed a bit above the actor root
    default CharacterMesh.RelativeLocation = FVector(0.0, 0.0, 50.0);

    UPROPERTY(DefaultComponent)
    UStaticMeshComponent ShieldMesh;

    // The shield mesh is hidden by default, and should only appear when taking damage
    default ShieldMesh.bHiddenInGame = true;
    // The shield mesh should not have any collision
    default ShieldMesh.SetCollisionEnabled(ECollisionEnabled::NoCollision);
}
```

## Working with Components

### Retrieving Components

`UMyComponentClass::Get()`,获取不到返回 `nullptr`

```cpp
AActor Actor;

// Retrieve the first skeletal mesh component we can find on the actor
USkeletalMeshComponent SkelComp = USkeletalMeshComponent::Get(Actor);

// Find the specific skeletal mesh component with this component name
USkeletalMeshComponent WeaponComp = USkeletalMeshComponent::Get(Actor, n"WeaponMesh");
```

`UMyComponentClass::GetOrCreate()` ,获取不到就创建一个

```cpp
// Find our own interaction handling component on the actor.
// If it does not exist, create it.
UInteractionComponent InteractComp = UInteractionComponent::GetOrCreate(Actor);

// Find an interaction handling component specifically named "ClimbingInteraction",
// or create a new one with that name
auto ClimbComp = UInteractionComponent::GetOrCreate(Actor, n"ClimbingInteraction");
```

### Adding New Components

`UMyComponentClass::Create()`，和`Get()`类似，名称是可选的。

```cpp
ACharacter Character;

// Create a new static mesh component on the character and attach it to the character mesh
UStaticMeshComponent NewComponent = UStaticMeshComponent::Create(Character);
NewComponent.AttachToComponent(Character.Mesh);
```

如果有动态的类型，如`TSubclassOf<>` 或 `UClass`， 可以用 Actor 的通用方法，如`Actor.GetComponent()`, `Actor.GetOrCreateComponent()`, `Actor.CreateComponent()`。

## Spawning Actors

```cpp
// Spawn a new Example Actor at the specified location and rotation
FVector SpawnLocation;
FRotator SpawnRotation;
AExampleActor SpawnedActor = AExampleActor::Spawn(SpawnLocation, SpawnRotation);
```

### Spawning a Blueprinted Actor

声明`TSubclassOf<>`的成员，然后用全局函数 `SpawnActor()`

```cpp
class AExampleSpawner : AActor
{
    /**
     * Which blueprint example actor class to spawn.
     * This needs to be configured either in the level,
     * or on a blueprint child class of the spawner.
     */
    UPROPERTY()
    TSubclassOf<AExampleActor> ActorClass;

    UFUNCTION(BlueprintOverride)
    void BeginPlay()
    {
        FVector SpawnLocation;
        FRotator SpawnRotation;

        AExampleActor SpawnedActor = Cast<AExampleActor>(
            SpawnActor(ActorClass, SpawnLocation, SpawnRotation)
        );
    }
}
```

## Construction Script

这是重写 Cpp 给蓝图的构造函数。也类似于构造函数了。

```cpp
class AExampleActor : AActor
{
    // How many meshes to place on the actor
    UPROPERTY()
    int SpawnMeshCount = 5;

    // Which static mesh to place
    UPROPERTY()
    UStaticMesh MeshAsset;

    UFUNCTION(BlueprintOverride)
    void ConstructionScript()
    {
        Print(f"Spawning {SpawnMeshCount} meshes from construction script!");

        for (int i = 0; i < SpawnMeshCount; ++i)
        {
            // Construct a new static mesh on this actor
            UStaticMeshComponent MeshComp = UStaticMeshComponent::Create(this);
            // Set the mesh we wanted for it
            MeshComp.SetStaticMesh(MeshAsset);
        }
    }
}
```

## Getting All Actors or Components

获取某一个特定的：`Actor.GetComponentsByClass()`。

```cpp
AActor Actor;

TArray<UStaticMeshComponent> StaticMeshComponents;
Actor.GetComponentsByClass(StaticMeshComponents);

for (UStaticMeshComponent MeshComp : StaticMeshComponents)
{
    Print(f"Static Mesh Component: {MeshComp.Name}");
}
```

获取 Level 中全部的 Actor，通过全局函数：`GetAllActorsOfClass()`。
最好只在一开始获取一次，然后存起来。

```cpp
// Find all niagara actors currently in the level
TArray<ANiagaraActor> NiagaraActors;
GetAllActorsOfClass(NiagaraActors);
```

## Override Components

重写覆盖父类的组件：UPROPERTY 中配置 `OverrideComponent =`

```cpp
class ABaseActor : AActor
{
    // This base actor specifies a root component that is just a scene component
    UPROPERTY(DefaultComponent, RootComponent)
    USceneComponent SceneRoot;
}

class AChildActor : ABaseActor
{
    /**
     * Because static meshes are a type of scene component,
     * we can use an override component to turn the base class' root
     * scene component into a static mesh.
     */
    UPROPERTY(OverrideComponent = SceneRoot)
    UStaticMeshComponent RootStaticMesh;
}
```

这类似于在 cpp 的构造函数里：`ObjectInitializer.SetDefaultSubobjectClass()`。

# Function Libraries

可以通过类似 `System::SetTimer()` 的方式调用函数库。

```cpp
class ATimerExample : AActor
{
    UFUNCTION(BlueprintOverride)
    void BeginPlay()
    {
        // Execute this.OnTimerExecuted() after 2 seconds
        System::SetTimer(this, n"OnTimerExecuted", 2.0, bLooping = false);
    }

    UFUNCTION()
    private void OnTimerExecuted()
    {
        Print("Timer executed!");
    }
}
```

## Common Libraries

- [Math::](https://angelscript.hazelight.se/api/index.html#CClass:Math) - All standard math functionality
- [Gameplay::](https://angelscript.hazelight.se/api/index.html#CClass:Gameplay) - Game functionality such as streaming, damage, player handling
- [System::](https://angelscript.hazelight.se/api/index.html#CClass:System) - Engine functionality such as timers, traces, debug rendering
- [Niagara::](https://angelscript.hazelight.se/api/index.html#CClass:Niagara) - Spawning and controlling particle systems
- [Widget::](https://angelscript.hazelight.se/api/index.html#CClass:Widget) - UMG widget functionality

## Namespace Simplification

AS 的函数库，来自于 Cpp 的 blueprint function library classes，然后做了一些名称的简化，以方便使用。
这些都被去头去尾：

- U...Statics
- U...Library
- U...FunctionLibrary
- UKismet...Library
- UKismet...FunctionLibrary
- UBlueprint...Library
- UBlueprint...FunctionLibrary

  去掉之后，命名就简化为类似的情况：

- `UNiagaraFunctionLibrary` becomes `Niagara::`
- `UWidgetBlueprintLibrary` becomes `Widget::`
- `UKismetSystemLibrary` becomes `System::`
- `UGameplayStatics` becomes `Gameplay::`

## Math Library

数学库用了 Cpp 的版本，而忽略了`UKismetMathLibrary` 的。

# FName Literals

`n"NameLiteral"` 的写法，可以让任何 string 都在编译期初始化，而不是在运行时查表。
Name literals 有很多用处，其中一个例子是用来绑定委托。

```cpp
delegate void FExampleDelegate();

class ANameLiteralActor : AActor
{
    TMap<FName, int> ValuesByName;

    void UseNameLiteral()
    {
        FName NameVariable = n"MyName";
        ValuesByName.Add(NameVariable, 1);

        FExampleDelegate Delegate;
        Delegate.BindUFunction(this, n"FunctionBoundToDelegate");
        Delegate.ExecuteIfBound();

        // Due to the name literal, no string manipulation happens
        // in calls to UseNameLiteral() during runtime.
    }

    UFUNCTION()
    void FunctionBoundToDelegate()
    {
        Print("Delegate executed");
    }
}
```

# Formatted Strings

格式化字符串，类似于 python，其中花括号的转义：`f"{{"` is equivalent to `"{"`.

```cpp
// Format Strings begin with f" and can hold expressions
// inside braces to replace within the string.
Print(f"Called from actor {GetName()} at location {ActorLocation}");

// Adding a = at the end of the expression will print the expression first
// For example:
Print(f"{DeltaSeconds =}");
// This prints:
//   DeltaSeconds = 0.01

// Format specifiers can be added following similar syntax to python's f-strings:
Print(f"Three Decimals: {ActorLocation.Z :.3}"); // Format float at three decimals of precision

Print(f"Extended to 10 digits with leading zeroes: {400 :010d}"); // 0000000400
Print(f"Hexadecimal: {20 :#x}"); // 0x14
Print(f"Binary: {1574 :b}"); // 11000100110
Print(f"Binary 32 Bits: {1574 :#032b}"); // 0b00000000000000000000011000100110

// Alignment works too
Print(f"Aligned: {GetName() :>40}"); // Adds spaces to the start of GetName() so it is 40 characters
Print(f"Aligned: {GetName() :_<40}"); // Adds underscores to the end of GetName() so it is 40 characters

// You can combine the equals with a format specifier
Print(f"{DeltaSeconds =:.0}");
// This prints:
//   DeltaSeconds = 0

// Enums by default print a full debug string
Print(f"{ESlateVisibility::Collapsed}"); // "ESlateVisibility::Collapsed (1)"
// ……
```

出处：Hazelight documentation: Formatted Strings example（节选，其余行省略）。

# Structs and References

AS 的 Class ，都是 UObject，可被 unreal 垃圾回收。

Structs 不能有 `UFUNCTION()`成员，可以有普通的，但是普通的不能被蓝图调用。

```cpp
struct FExampleStruct
{
    /* Properties with UPROPERTY() in a struct will be accessible in blueprint. */
    UPROPERTY()
    float ExampleNumber = 4.0;

    UPROPERTY()
    FString ExampleString = "Example String";

    /* Properties without UPROPERTY() will still be in the struct, but cannot be seen by blueprint. */
    float ExampleHiddenNumber = 3.0;
};
```

## Passing and Returning Structs

可以被当作正常类型使用。

```cpp
UFUNCTION()
FExampleStruct CreateExampleStruct(float Number)
{
    FExampleStruct ResultStruct;
    ResultStruct.ExampleNumber = Number;
    ResultStruct.ExampleString = f"{Number}";

    return ResultStruct;
}

UFUNCTION(BlueprintPure)
bool IsNumberInStructEqual(FExampleStruct Struct, float TestNumber)
{
    return Struct.ExampleNumber == TestNumber;
}
```

## Struct References

默认情况下，AS 的函数参数是只读的。如果想要修改 Struct，需要在类型后加`&`。

```cpp
// Change the parameter struct so its number is randomized between 0.0 and 1.0
UFUNCTION()
void RandomizeNumberInStruct(FExampleStruct& Struct)
{
    Struct.ExampleNumber = Math::RandRange(0.0, 1.0);
}
```

## Declaring Out Parameters

声明一个在蓝图中为输出的参数，需要在类型后加`&out`。这也适用于基础类型。

```cpp
UFUNCTION()
void OutputRandomizedStruct(FExampleStruct&out OutputStruct, bool&out bOutSuccessful)
{
    FExampleStruct ResultStruct;
    ResultStruct.ExampleNumber = Math::RandRange(0.0, 1.0);

    OutputStruct = ResultStruct;
    bOutSuccessful = true;
}
```

## Automatic References for Function Parameters

函数的参数，会默认是不可变引用类型：const & 。
这是为了方便和性能。
也就是说，形参`FVector` 等价于 `const FVector&`。
#cpp_different
所以，形参`FVector&` 是可变引用类型，才可以修改它。
形参`FVector&out`会被蓝图识别为输出端。

# Unreal Networking Features

`UFUNCTION()` 可加上 `NetMulticast`, `Client`, `Server` and/or `BlueprintAuthorityOnly`，函数就会自动使用 RPC。

默认是`reliable`, 如果要 unreliable RPC message，添加 `Unreliable`标识符。
#cpp_different

`UPROPERTY()` 可标记为`Replicated`，可以用标识符`ReplicationCondition`配置复制的条件。
如果要这些属性和 RPC 函数起作用，前提是 Actor 和 Component 被设置为 replicate，这可以用`default`语句来设置。

```cpp
class AReplicatedActor : AActor
{
    // Set the actor's replicates property to default to true,
    // so its declared replicated properties work.
    default bReplicates = true;

    // Will always be replicated when it changes
    UPROPERTY(Replicated)
    bool bReplicatedBool = true;

    // Only replicates to the owner
    UPROPERTY(Replicated, ReplicationCondition = OwnerOnly)
    int ReplicatedInt = 0;

    // Calls OnRep_ReplicatedValue whenever it is replicated
    UPROPERTY(Replicated, ReplicatedUsing = OnRep_ReplicatedValue)
    int ReplicatedValue = 0;

    UFUNCTION()
    void OnRep_ReplicatedValue()
    {
        Print("Replicated Value has changed!");
    }
}
```

`ReplicationCondition`的条件和 Cpp 的 ELifetimeCondition 枚举一致。

- None
- InitialOnly
- OwnerOnly
- SkipOwner
- SimulatedOnly
- AutonomousOnly
- SimulatedOrPhysics
- InitialOrOwner
- Custom
- ReplayOrOwner
- ReplayOnly
- SimulatedOnlyNoReplay
- SimulatedOrPhysicsNoReplay
- SkipReplay

`UPROPERTY`中使用`ReplicatedUsing`，可以当 replicated 时，调用标记了`UFUNCTION()`的方法。

# Delegates and Events

## Delegates

等价于 Cpp 的动态委托`DECLARE_DYNAMIC_DELEGATE()`。可以有返回值。 #cpp_different
在全局作用域里声明`delegate`。
使用`BindUFunction` 和 `ExecuteIfBound`。
被绑定的方法要声明为`UFUNCTION()`。

```cpp
// Declare a new delegate type with this function signature
delegate void FExampleDelegate(UObject Object, float Value);

class ADelegateExample : AActor
{
    FExampleDelegate StoredDelegate;

    UFUNCTION(BlueprintOverride)
    void BeginPlay()
    {
        // Bind the delegate so executing it calls this.OnDelegateExecuted()
        StoredDelegate.BindUFunction(this, n"OnDelegateExecuted");

        // You can also create new bound delegates by using the constructor:
        StoredDelegate = FExampleDelegateSignature(this, n"OnDelegateExecuted");
    }

    UFUNCTION()
    private void OnDelegateExecuted(UObject Object, float Value)
    {
        Print(f"Delegate was executed with object {Object} and value {Value}");
    }

    UFUNCTION(BlueprintOverride)
    void Tick(float DeltaSeconds)
    {
        // If the delegate is bound, execute it
        StoredDelegate.ExecuteIfBound(this, DeltaSeconds);
    }
}
```

## Events

类似于 Delegate，但是可以绑定多个函数。
等价于 Cpp 的动态多播委托 `DECLARE_DYNAMIC_MULTICAST_DELEGATE()` 。 不可以有返回值，必须是 void。 #cpp_different
在全局作用域里声明`event`。
使用`AddUFunction()` 和 `Broadcast()`。
被绑定的方法要声明为`UFUNCTION()`。

```cpp
event void FExampleEvent(int Counter);

class AEventExample : AActor
{
    UPROPERTY()
    FExampleEvent OnExampleEvent;

    private int CallCounter = 0;

    UFUNCTION(BlueprintOverride)
    void BeginPlay()
    {
        // Add two functions to be called when the event is broadcast
        OnExampleEvent.AddUFunction(this, n"FirstHandler");
        OnExampleEvent.AddUFunction(this, n"SecondHandler");
    }

    UFUNCTION()
    private void FirstHandler(int Counter)
    {
        Print("Called first handler");
    }

    UFUNCTION()
    private void SecondHandler(int Counter)
    {
        Print("Called second handler");
    }

// ……
```

出处：Hazelight documentation: Events example（节选，其余行省略）。

### Events in Blueprint

将 Event 声明为`UPROPERTY()`，就可以在蓝图中获取到，也就是会出现在`Event Dispatchers`的列表。即 Class Defaults -- Events。

### Tip: Automatic signature generation in Visual Studio Code

绑定委托的时候，如果没有创建被绑定的函数，可以点击灯泡或者 Ctrl + . ，`Generate Method`，自动帮忙创建。

```cpp
	UFUNCTION(BlueprintOverride)
	void BeginPlay()
	{
        OnExampleEvent.AddUFunction(this,n"OnExampleEventCalled");
	}
    // 可以自动创建下方的函数
	UFUNCTION()
	private void OnExampleEventCalled(int Counter)
	{
	}
```

# Mixin Methods

相当于在 class 之外声明方法。可用于添加方法到一个 cpp 类，或者写不同类型的共用的方法。mixin 声明的函数，第一个参数是此函数绑定给的类型，其余参数是函数的正常参数。

```cpp
// Mixin method that teleports any actor
// The first, 'Self' parameter gets set to the actor it is called on
mixin void ExampleMixinTeleportActor(AActor Self, FVector Location)
{
    Self.ActorLocation = Location;
}

void Example_MixinMethod()
{
    // Call the mixin method on an actor
    // Note how ActorReference is passed into Self automatically
    AActor ActorReference;
    ActorReference.ExampleMixinTeleportActor(FVector(0.0, 0.0, 100.0));
}
```

当给 struct 创建 mixin 的时候，增加&符号，让其可被修改。

```cpp
mixin void SetVectorToZero(FVector& Vector)
{
    Vector = FVector(0, 0, 0);
}

void Example_StructMixin()
{
    FVector LocalValue;
    LocalValue.SetVectorToZero();
}
```

还可以从 cpp 端给一些类添加 mixin 方法。

# Gameplay Tags

`FGameplayTag` 会被绑定到全局命名空间`GameplayTags`。所有非字母数字字符，包括点分隔符，都被转换成下划线\_。

```cpp
// Assuming there is a GameplayTag named "UI.Action.Escape"
FGameplayTag TheTag = GameplayTags::UI_Action_Escape;
```

# Editor-Only Script

## Preprocessor Blocks

`#if EDITOR` 和 `#endif ` 包裹的是仅供编译器的语句。

```cpp
class AExampleActor : AActor
{
#if EDITOR
    default PivotOffset = FVector(0, 0, 10);
#endif

    UFUNCTION(BlueprintOverride)
    void ConstructionScript()
    {
#if EDITOR
        SetActorLabel("Example Actor Label");
#endif
    }
}
```

其他几个有用的宏语句条件：
`EDITORONLY_DATA` - Whether properties that are only relevant to the editor are readable.  
`RELEASE` - 游戏采用 Shipping 或 Test 构建配置。
`TEST` - 游戏采用 Debug、Development 或 Test 构建配置。

## Editor-Only Directories

在烘焙的构建中（cooked builds），文件夹名为`Editor`、`Examples`、`Dev` ，会被自动忽略。

## Testing with Simulate-Cooked Mode

这是为了测试写在 Editor-Only 的内容不小心影响主程序的。

`-as-simulate-cooked` 用于模拟烘焙构建的情况，可搭配`AngelscriptTest`使用。

```shell
UnrealEditor-Cmd.exe "MyProject.uproject" -as-simulate-cooked -run=AngelscriptTest
```

# Subsystems

## Using a Subsystem

`USubsystemClass::Get()`。需要注意的是，很多子系统是*Editor Subsystems*，这不能被游戏使用，需要写在 Editor-Only 的脚本中。

```cpp
void TestCreateNewLevel()
{
    auto LevelEditorSubsystem = ULevelEditorSubsystem::Get();
    LevelEditorSubsystem.NewLevel("/Game/NewLevel");
}
```

## Creating a Subsystem

五个可以继承的 Subsystem。

- `UScriptWorldSubsystem` for world subsystems
- `UScriptGameInstanceSubsystem` for game instance subsystems
- `UScriptLocalPlayerSubsystem` for local player subsystems
- `UScriptEditorSubsystem` for editor subsystems
- `UScriptEngineSubsystem` for engine subsystems

```cpp
class UMyGameWorldSubsystem : UScriptWorldSubsystem
{
    UFUNCTION(BlueprintOverride)
    void Initialize()
    {
        Print("MyGame World Subsystem Initialized!");
    }

    UFUNCTION(BlueprintOverride)
    void Tick(float DeltaTime)
    {
        Print("Tick");
    }

    // Create functions on the subsystem to expose functionality
    UFUNCTION()
    void LookAtMyActor(AActor Actor)
    {
    }
}

void UseMyGameWorldSubsystem()
{
    auto MySubsystem = UMyGameWorldSubsystem::Get();
    MySubsystem.LookAtMyActor(nullptr);
}
```

subsystem 里声明的`UFUNCTION` 都会暴露到蓝图中。

## Local Player Subsystems

获取 Local Player Subsystem 需要传入`ULocalPlayer`给 `::Get()`函数。(直接传入`APlayerController`也是可行的。)

```cpp
class UMyPlayerSubsystem : UScriptLocalPlayerSubsystem
{
}

void UseScriptedPlayerSubsystem()
{
    ULocalPlayer RelevantPlayer = Gameplay::GetPlayerController(0).LocalPlayer;
    auto MySubsystem = UMyPlayerSubsystem::Get(RelevantPlayer);
}
```

# Angelscript Test Support

## Unit Tests

```cpp
void Test_NameOfTheTestCase(FUnitTest& T)
{
    // Fails the test.
    T.AssertTrue(false);
    T.AssertEquals(1, 1 + 1);
    T.AssertNotNull(nullptr);
}
```

如果要测试的文件是 File.as，一般将测试代码放在 File_Test.as。

### Running Unit Tests

单元测试是热重载的，在 Editor 的 Windows > OutputLog 里可以看到测试信息。
也可以用命令行测试：

```shell
Engine\Binaries\Win64\UnrealEditor-Cmd.exe \Path\To\your.uproject -NullRHI -NoSound -NoSplash -ExecCmds="Automation RunTests Angelscript.UnitTests" -TestExit "Automation Test Queue Empty+Found 0 Automation Tests, based on" -unattended -stdout -as-exit-on-error
```

### Installing a Custom Game Mode for Unit Tests

在 project 的 .ini 文件中可以配置专属于测试的 GameMode。

```ini
[/Script/EngineSettings.GameMapsSettings]
...
+GameModeClassAliases=(Name="UnitTest",GameMode="/Game/Testing/UnitTest/BP_UnitTestGameMode.BP_UnitTestGameMode_C")
```

## Integration Tests

MyTestName_IntegrationTest.as

```cpp
void IntegrationTest_MyTestName(FIntegrationTest& T)
{
}
```

IntegrationTest_MyTestName.umap 添加到 /Content/Testing/ 下。Map 的名称必须和 test 的名称一致，只是多了后缀.umap。
当然这个 Map 的路径也是可以在.ini 文件里配置的：

```ini
[/Script/AngelscriptCode.AngelscriptTestSettings]
IntegrationTestMapRoot=/Game/Testing/
```

可以在测试中获取放置的 Actor 或者生成它们。

```cpp
// Looks up an actor in the map
AActor GetActorByLabel(UClass Class, const FName& Label)
{
#if EDITOR
    TArray<AActor> Actors;
    GetAllActorsOfClass(Class, Actors);

    for (AActor Actor: Actors)
    {
        if (Actor.GetActorLabel() == Label)
        {
            return Actor;
        }
    }

    FString AllActorLabels = "";
    for (AActor Actor: Actors)
    {
        AllActorLabels += "- " + Actor.GetActorLabel() + "\n";
    }

    if (AllActorLabels.IsEmpty())
    {
        Throw(
            "Did not find an actor with class " + Class.GetName() +
            " and label " + Label + ". In fact, there no actors in this level.");
    }
    else
    {
// ……
```

出处：Hazelight documentation: integration-test Actor lookup（节选，其余行省略）。

### Latent Automation Commands

这是延迟命令，可以让测试延迟。

### Running Integration Test

组合测试不会自动运行，而是通过 Test Automation window in Unreal 来。
也可以通过类似单元测试的命令行，需要将 Angelscript.UnitTests 替换为 Angelscript.IntegrationTests。
在 Tools > Session Frontend 里。
https://dev.epicgames.com/documentation/en-us/unreal-engine/automation-system-user-guide-in-unreal-engine?application_version=5.4

### Complex Integration Tests

还可以动态生成测试。

```cpp
void ComplexIntegrationTest_PotionsAreTooStrongForKnight_GetTests(TArray<FString>& OutTestCommands)
{
     for (APotion Potion: MyGame::GetPotionRegistry().GetAllPotions())
     {
         OutTestCommands.Add(Potion.GetName().ToString());
     }
}

void ComplexIntegrationTest_PotionsAreTooStrongForKnight(FIntegrationTest& T)
{
    FString PotionName = T.GetParam();
    APotion Potion = MyGame::GetPotionRegistry().LookupPotion(PotionName);
    AKnight Knight = Cast<AKnight>(GetActorByLabel(AKnight::StaticClass(), n"Knight"));
    AActor PotionSeller = GetActorByLabel(AActor::StaticClass(), n"PotionSeller");

    // Order the knight to walk over to the potion seller and try to buy a potion.
    Knight.BuyPotionFrom(PotionSeller, Potion);
    T.AddLatentAutomationCommand(UExpectResponse("My potions are too strong for you traveller.", Knight, PotionSeller));
}
```

## Code Coverage

代码测试里的选项，打开的话，会使得 Editor 启动时间变慢 20 秒，记得关闭。
这会生成文件到 Saved/CodeCoverage ，打开 index.html 可以看到内容。

# Overview of Differences for C++ Unreal Developers

## Objects Instead of Pointers

任何声明为`UObject` 类型的变量，自动变成 object 的引用。没有指针。没有`->`arrow，只有`.` dots。( Cpp 的引用，本质上是不能为空的指针。)
不用特意将 property 声明为`UPROPERTY()`以防止被垃圾回收。脚本的所有 object references 都自动插入 GC 。

```cpp
void TeleportActorToOtherActor(AActor ActorReference, AActor TeleportToActor)
{
    FTransform TeleportToTransform = TeleportToActor.GetActorTransform();
    ActorReference.SetActorTransform(TeleportToTransform);
}
```

## Default Accessibility for Properties

`UPROPERTY()` 默认是 `EditAnywhere` 和 `BlueprintReadWrite`。
需要限制读写的时候，用`NotEditable`和 `NotBlueprintCallable`。
这种默认标识符可以在项目设置里修改。Plugins - Angelscript 里。
**这样的目的是为了简化标识符，`UPROPERTY()` 不再用于垃圾收集，那么声明它的意思就是让 Editor 和蓝图访问到。**

## Use the `default` Keyword Instead of Constructors

subobjects 里配置属性，使用 default 。

```cpp
class AExampleActor : AActor
{
    // Set default values for class properties in the class body
    UPROPERTY()
    float ConfigurableValue = 5.0;

    // Set default values for subobjects with `default` statements
    UPROPERTY(DefaultComponent)
    UCapsuleComponent CapsuleComponent;
    default CapsuleComponent.CapsuleHalfHeight = 88.0;
    default CapsuleComponent.CapsuleRadius = 40.0;
    default CapsuleComponent.bGenerateOverlapEvents = true;
}
```

## Floating Point Width

UE 从 5.0 开始使用 double，但是为了让蓝图的人不引起困惑，将 double 类型还是叫做 float。
AS 跟随这个选择，所以脚本里声明的 float , 实际上是 64-bit double。如果要声明指定长度的浮点数，可以选择明确为`float32` or `float64`。

```cpp
float ValueDouble = 1.0; // <-- This is a 64-bit double-precision float
float32 ValueSingle = 1.f; // <-- This is a 32-bit single-precision float
float64 ValueAlsoDouble = 1.0; // <-- This is *also* a 64-bit double-precision float
```

double 还是可以写的，如果需要，可以在项目设置的 Plugin - Angelscript 里禁止写 double 。

因为这个原因，cpp 绑定函数的时候，涉及到 float 时，绑定的签名需要写 float32。

为了不至于看 cpp 代码的时候，float 是 32 位的，然而 AS 里的代码 float 却是 64 位的，可以考虑明确 写 float32 和 float64 (或 double)。
# Automatic Bindings

自动绑定的原则：如果能在蓝图使用，就能在脚本里使用。
如果某项功能可从 Blueprint 使用，那么它也应该能从 Angelscript 使用。

## Class Bindings

`UCLASS()` 里有`BlueprintType` 或者有成员函数是`BlueprintCallable`的，会被绑定。
如果想要被跳过，可以添加`NotInAngelscript`修饰符。

## Struct Bindings

`USTRUCT()`里有`BlueprintType`或者包含有任何可以被蓝图访问或编辑的属性。

如果想要被跳过，可以添加`NoAutoAngelscriptBind`修饰符。

## Property Bindings

### Read/Write Flags

`UPROPERTY`声明有`BlueprintReadWrite`或 `BlueprintReadOnly` 会被自动绑定。其中，`BlueprintReadOnly`的话，会变成`const`，不能在脚本里修改。

如果只想让脚本访问而不需要蓝图访问，可以使用 `ScriptReadWrite`或者`ScriptReadOnly`。

### Editable Flags

Properties 声明了`EditAnywhere`、`EditInstanceOnly`、`EditDefaultsOnly`的会被绑定。
如果一个 property 只有一个 editable flag，但是没有声明 blueprint access flag ，在脚本中只能使用`default` statement 访问到。

### Skipping Properties

添加`NotInAngelscript`，会让脚本跳过绑定，即使有 blueprint 可以访问到的标签。

## Function Bindings

### Callable Flags

`UFUNCTION`有`BlueprintCallable`或`BlueprintPure`，会自动绑定。
如果要暴露一个 function 给 AS，但是不给蓝图，可以只添加 `ScriptCallable`。

### Blueprint Events

`UFUNCTION`有`BlueprintImplementableEvent`或`BlueprintNativeEvent`，可以被脚本和蓝图重写。

### Skipping Functions

添加`NotInAngelscript`，会让脚本跳过绑定，即使有 blueprint 可以访问到的标签。

### Deprecated Functions

这废弃的 Function 不会被绑定。
脚本中没有弃用警告功能，因此当 Epic 弃用某些 api 时，引擎升级可能需要更改脚本。

### Static Functions

`UCLASS`里静态函数会被绑定到全局的函数库里，命名空间的名称会依据规则简化。

### Enum Bindings

任何`UENUM()`都可以在脚本里调用。

# Script Mixin Libraries

使用 cpp 是因为，有些没有暴露给蓝图的内容，脚本获取不到。通过 mixin 可以在 cpp 注入，进而在不修改原有 cpp 代码的情况下，将一些内容暴露给蓝图使用。

## Mixin Libraries for Structs

给 Struct 注入 FUNCTION（一般情况 Struct 在自动绑定的时候，方法因为不能带有 UFUNCTION，所以没办法暴露，这个时候可以用 Mixin 注入的方式。）

```cpp
UCLASS(Meta = (ScriptMixin = "FVector"))
class UFVectorScriptMixinLibrary : public UObject
{
	GENERATED_BODY()
public:

	// This will be accessible in script as
	//     FVector Vector;
	//     Vector.ResetTo(4.0);
	UFUNCTION(ScriptCallable)
	static void ResetTo(FVector& Vector, float NewValue)
	{
		Vector = FVector(NewValue, NewValue, NewValue);
	}

	// This will become a const method, as it takes
	// a const reference to the mixin type:
	//  Usable in script as both   Vector.SummedValue
	//                        or   Vector.GetSummedValue()
	UFUNCTION(ScriptCallable)
	static float GetSummedValue(const FVector& Vector)
	{
		return Vector.X+Vector.Y+Vector.Z;
	}
}
```

## Mixin Libraries for Classes

给已经有的 Class 注入 FUNCTION，这样就不用修改原来的 Class 代码了。

```cpp
UCLASS(Meta = (ScriptMixin = "AActor"))
class UMyActorMixinLibrary : public UObject
{
	GENERATED_BODY()
public:

	// This can be used in script as:
	//  Actor.TeleportToOrigin();
	UFUNCTION(ScriptCallable)
	static void TeleportToOrigin(AActor* Actor)
	{
		Actor->SetActorLocation(FVector(0, 0, 0));
	}
}
```

脚本已经提供了很多 Mixin 注入的函数，这些函数没有暴露到蓝图中。
Engine/Plugins/Angelscript/Source/AngelscriptCode/Public/FunctionLibraries

# Using Precompiled Scripts

### 使用预编译脚本功能

#### 功能说明

通常，当引擎启动时，AngelScript 插件会读取项目脚本文件夹中的所有 `.as` 文件，然后解析并编译它们。  
在某些平台（例如低速 CPU 或硬盘的设备）上，这个过程可能会花费较长时间。

为了解决这个问题并加快打包版本的启动速度，可以让打包后的游戏生成**预编译脚本缓存**文件。  
当存在预编译脚本缓存文件时，插件会直接从缓存加载已编译的脚本字节码，而不再逐一加载、解析和编译脚本文件。

此外，插件还支持将脚本**转译为 C++ 源代码**，这些源代码可以像字节码一样工作。将这些代码加入项目后重新编译游戏的可执行文件，AngelScript 的 JIT（即时编译）系统会将虚拟机字节码执行替换为原生的 C++ 代码。这会显著提升脚本代码的运行效率。

---

### 使用方法

#### 生成预编译脚本缓存

**注意：预编译脚本缓存必须由将要加载它的相同 `.exe` 文件生成。**

1. **打包游戏**  
   按照你需要的配置打包你的游戏。

2. **运行打包后的 `.exe` 文件生成缓存**  
   使用命令行运行 `ProjectName.exe`，并添加参数：

   ```bash
   -as-generate-precompiled-data
   ```

3. **生成缓存文件**  
   运行后会生成一个名为 `PrecompiledScript.Cache` 的文件，位于 `ProjectName/Script/` 文件夹中。  
   该文件需要包含在游戏的发布版本中。

4. **加载缓存**  
   在下次运行游戏时，脚本将直接从该预编译缓存中加载，而不是重新解析和编译 `.as` 脚本文件。

---

#### 转译 C++ 代码

预编译脚本的生成步骤还会输出一个名为 `AS_JITTED_CODE/` 的文件夹，其中每个脚本文件都会有对应的 C++ 文件。

1. **将代码复制到项目中**  
   将 `AS_JITTED_CODE/` 文件夹复制到你的项目源码目录中。

2. **重新编译游戏可执行文件**  
   在包含 `AS_JITTED_CODE/` 的情况下重新编译 `.exe`。

3. **运行游戏**  
   使用新的 `.exe` 和 `PrecompiledScript.Cache` 文件时，AngelScript 插件会自动运行对应的优化后的 C++ 代码来代替原始字节码执行。

---

### 兼容性注意事项

由于预编译脚本缓存直接包含了 C++ 属性的硬编码字节偏移量和结构大小信息，因此需要确保以下兼容性：

1. **缓存与可执行文件匹配**  
   **永远不要**使用一个 `.exe` 生成的 `PrecompiledScript.Cache` 文件加载另一个 `.exe`。  
   每次重新构建 `.exe` 时，都需要用新 `.exe` 重新生成缓存文件。

2. **脚本文件更新时无需重建 `.exe`**  
   你可以修改 `.as` 脚本文件并生成新的 `PrecompiledScript.Cache` 文件，而无需重新编译 `.exe`。  
   **但是**，如果 `.exe` 中包含了 C++ 代码，则新的脚本缓存文件将与旧 `.exe` 不匹配，必须重新编译 `.exe` 才能使用。

---

### 动态脚本重加载的限制

- 当使用 `PrecompiledScript.Cache` 时，`.as` 脚本文件不会被加载，因此对这些文件的更改不会生效，也无法启用脚本热重载功能。

- 如果需要禁用预编译脚本并重新启用开发模式，可以在命令行中添加参数：
  ```bash
  -as-development-mode
  ```

这样可以绕过预编译脚本的加载逻辑，回到直接加载 `.as` 脚本文件的模式。

# Development Status

## Platform Support

Windows, PS5, and Xbox Series X|S platforms 这些平台是 Hazelight 测试过的，其他平台有一些团队测试可用。

## Known Limitations

`Super::Function()` 只能调用 AS 的上级 Function，不能调用 C++的`BlueprintNativeEvent`的方法。
Unreal Interfaces (IInterface/UInterface) 不能在 AS 中使用。
