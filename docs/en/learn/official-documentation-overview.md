---
title: "UnrealEngine-Angelscript: an overview of the official documentation"
order: 2
category: getting-started
---
# UnrealEngine-Angelscript: an overview of the official documentation

# Introduction

Script maintainer: [Hazelight](https://angelscript.hazelight.se), the studio behind [It Takes Two](https://www.ea.com/games/it-takes-two).

The code is an UnrealEngine fork. Source changes integrate it closely with the engine. It provides Angelscript, AngelscriptGAS, AngelscriptEnhancedInput and AngelscriptStructUtils plugins, plus [GameplayMessageRouter with Angelscript](https://github.com/IncantaUnreal/GameplayMessageRouter) bindings.

Writing environment: VSCode, with [Visual Studio Code Extension](https://marketplace.visualstudio.com/items?itemName=Hazelight.unreal-angelscript) and [Unreal Angelscript Clang-Format](https://marketplace.visualstudio.com/items?itemName=Hazelight.unreal-angelscript-clang-format). They provide autocomplete and other familiar language tools, which is convenient. Importantly, VSCode breakpoints support debugging.

Its role is a layer between cpp and Blueprints. Cpp builds slowly, often needs an Editor restart and carries much boilerplate and many caveats. Blueprints are tedious for complex logic and hard to diff as binaries. AS between them addresses both. Cpp becomes the layer exposing more functionality to AS and handling performance-sensitive work; Blueprints become final configuration assets with occasional simple logic.

Language features: AS is statically typed and looks so damn much like cpp — almost a simplified version. Moving code between cpp and AS is convenient. UE-AS adds many writing conveniences, much simpler than U++.

The drawback: not everyone agrees on design. The maintainers have their own approach. Most Blueprint functionality works in AS, but UInterface does not. Interface code therefore cannot bind automatically or be called through an interface in AS. Mixins can conveniently bind many interface calls. Overrides need a cpp subclass wrapper.

User requirements:
Know how to compile the engine, otherwise use one of the official binaries, which are not available for every UE version.
Know how to wrap cpp functionality for scripts, otherwise some Blueprint-exposed features, such as certain async latent functions, remain unavailable.

# Functions and BlueprintEvents

## Calling AngleScript functions from Blueprint

### Class methods

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

`BlueprintCallable` is unnecessary because it is the default.
#cpp_different

### Global functions

A global `UFUNCTION()` acts much like a static function and is callable by Blueprints, like a Blueprint Function Library entry.

```cpp
// Example global function that moves an actor somewhat
UFUNCTION()
void ExampleGlobalFunctionMoveActor(AActor Actor, FVector MoveAmount)
{
    Actor.ActorLocation += MoveAmount;
}
```

## Blueprint-overridable AngleScript functions

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

AS does not distinguish `BlueprintImplementableEvent` from `BlueprintNativeEvent`. Both need a default implementation, like `BlueprintNativeEvent`.
#cpp_different

Separate the base implementation from the Blueprint hook so a Blueprint cannot accidentally omit the base call.

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

## AngleScript overrides of Cpp functions

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

In VSCode, select the class and use the light bulb, Ctrl+., to see overridable functions.
Autocomplete shows them too.
AS removes prefixes such as `BP_`, `K2_` and `Received_`, for functions without an explicit DisplayName.

## Calling Super from AngleScript

### Overriding an AS method

- When the base has no `BlueprintEvent`:
  Add override after the declaration and call `Super::` directly.
  All AS methods are virtual by default.

- When the base has `BlueprintEvent`:
  Add UFUNCTION(BlueprintOverride).
  **BlueprintEvent needs BlueprintOverride, just like a cpp override.**

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

Source: Hazelight documentation: Super function example (excerpt; remaining lines omitted).

### Overriding a Cpp method

- A cpp `BlueprintNativeEvent` override cannot call `Super::` because of technical limitations.
  Expose a `BlueprintImplementEvent` hook that calls the BlueprintNativeEvent method, or put the base implementation in another Callable function.
- A cpp `BlueprintImplementEvent` has no implementation to call.
- Other functions that are not overrides can be called directly without Super.

Generally, a cpp-derived class has no Super namespace, so `Super::` cannot be written there.
Only call the current method’s own base method through Super. Calling another child method’s base implementation may work but is error-prone and produces a warning, such as `Calling Super::TestSuper from different child function BeginPlay_Implementationas`.

# Properties and Accessors

## Script-only members

Omit `UPROPERTY()`.

## Members exposed to Unreal

Add `UPROPERTY()`.

#### `EditAnywhere` by default

#cpp_different
Add editing restrictions if needed:

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

#### `BlueprintReadWrite` by default

#cpp_different
Add access restrictions if needed:

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

## Category

Much like Cpp:

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

## Accessing methods as properties

AS methods starting with `Get..()` or `Set..()` can end in `property` and be used like properties. These are Property Accessor Functions.

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

Bound Cpp methods starting with `Get...()` can be accessed as properties: `Actor.ActorLocation` is equivalent to `Actor.GetActorLocation()`.

## Access restrictions

Public is the default. Put `private` or `protected` before each declaration. Methods work the same way.

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

# Actors and Components

`UCLASS()` is optional, but can carry specifiers.

## Default Components

Use a specifier:
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

`RootComponent` marks the root; components attach to it by default.
Use `Attach =` and `AttachSocket =` for a different attachment.

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

Put default before a statement.
It initializes subobjects and parent properties, like a Cpp constructor.

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

`UMyComponentClass::Get()` returns `nullptr` if missing:

```cpp
AActor Actor;

// Retrieve the first skeletal mesh component we can find on the actor
USkeletalMeshComponent SkelComp = USkeletalMeshComponent::Get(Actor);

// Find the specific skeletal mesh component with this component name
USkeletalMeshComponent WeaponComp = USkeletalMeshComponent::Get(Actor, n"WeaponMesh");
```

`UMyComponentClass::GetOrCreate()` creates it if missing:

```cpp
// Find our own interaction handling component on the actor.
// If it does not exist, create it.
UInteractionComponent InteractComp = UInteractionComponent::GetOrCreate(Actor);

// Find an interaction handling component specifically named "ClimbingInteraction",
// or create a new one with that name
auto ClimbComp = UInteractionComponent::GetOrCreate(Actor, n"ClimbingInteraction");
```

### Adding New Components

`UMyComponentClass::Create()` resembles Get; the name is optional.

```cpp
ACharacter Character;

// Create a new static mesh component on the character and attach it to the character mesh
UStaticMeshComponent NewComponent = UStaticMeshComponent::Create(Character);
NewComponent.AttachToComponent(Character.Mesh);
```

For a dynamic type such as `TSubclassOf<>` or `UClass`, use Actor’s general `Actor.GetComponent()`, `Actor.GetOrCreateComponent()` or `Actor.CreateComponent()`.

## Spawning Actors

```cpp
// Spawn a new Example Actor at the specified location and rotation
FVector SpawnLocation;
FRotator SpawnRotation;
AExampleActor SpawnedActor = AExampleActor::Spawn(SpawnLocation, SpawnRotation);
```

### Spawning a Blueprinted Actor

Declare a `TSubclassOf<>` member and call the global `SpawnActor()`:

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

This overrides the construction hook Cpp exposes to Blueprints, rather like a constructor.

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

Get particular components with `Actor.GetComponentsByClass()`:

```cpp
AActor Actor;

TArray<UStaticMeshComponent> StaticMeshComponents;
Actor.GetComponentsByClass(StaticMeshComponents);

for (UStaticMeshComponent MeshComp : StaticMeshComponents)
{
    Print(f"Static Mesh Component: {MeshComp.Name}");
}
```

Get all Actors of a type in the level through the global `GetAllActorsOfClass()`.
Prefer doing this once initially and retaining the results.

```cpp
// Find all niagara actors currently in the level
TArray<ANiagaraActor> NiagaraActors;
GetAllActorsOfClass(NiagaraActors);
```

## Override Components

Use `OverrideComponent =` in UPROPERTY to replace a parent component:

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

This resembles `ObjectInitializer.SetDefaultSubobjectClass()` in a cpp constructor.

# Function Libraries

Call libraries with forms such as `System::SetTimer()`:

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

AS function libraries come from Cpp Blueprint function-library classes, with simplified names.
These prefixes and suffixes are removed:

- U...Statics
- U...Library
- U...FunctionLibrary
- UKismet...Library
- UKismet...FunctionLibrary
- UBlueprint...Library
- UBlueprint...FunctionLibrary

  The results look like:

- `UNiagaraFunctionLibrary` becomes `Niagara::`
- `UWidgetBlueprintLibrary` becomes `Widget::`
- `UKismetSystemLibrary` becomes `System::`
- `UGameplayStatics` becomes `Gameplay::`

## Math Library

Uses Cpp math instead of `UKismetMathLibrary`.

# FName Literals

`n"NameLiteral"` initializes a string at compile time instead of looking it up at runtime.
Name literals have many uses, including delegate binding.

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

Similar to Python. Escape braces with `f"{{"`, equivalent to `"{"`.

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

Source: Hazelight documentation: Formatted Strings example (excerpt; remaining lines omitted).

# Structs and References

AS classes are UObjects, collected by Unreal GC.

Structs cannot have `UFUNCTION()` members. Ordinary methods are allowed but are not callable by Blueprints.

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

Use them like ordinary types:

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

AS parameters are read-only by default. Add `&` after a Struct type to modify it.

```cpp
// Change the parameter struct so its number is randomized between 0.0 and 1.0
UFUNCTION()
void RandomizeNumberInStruct(FExampleStruct& Struct)
{
    Struct.ExampleNumber = Math::RandRange(0.0, 1.0);
}
```

## Declaring Out Parameters

Add `&out` after the type for a Blueprint output parameter. This works with primitives too.

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

Parameters are immutable references, const &, by default.
This is for convenience and performance.
`FVector` as a parameter is equivalent to `const FVector&`.
#cpp_different
`FVector&` is a mutable reference, allowing modification.
`FVector&out` becomes a Blueprint output pin.

# Unreal Networking Features

Add `NetMulticast`, `Client`, `Server` and/or `BlueprintAuthorityOnly` to `UFUNCTION()` for automatic RPC handling.

`reliable` is the default. Add `Unreliable` for unreliable RPC messages.
#cpp_different

Mark properties `Replicated` and configure conditions through `ReplicationCondition`.
The Actor or Component must replicate for properties and RPCs to work; set that through `default` statements.

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

`ReplicationCondition` uses Cpp ELifetimeCondition names:

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

`ReplicatedUsing` on `UPROPERTY` invokes a `UFUNCTION()` when replication occurs.

# Delegates and Events

## Delegates

Equivalent to Cpp dynamic delegates, `DECLARE_DYNAMIC_DELEGATE()`. Return values are allowed. #cpp_different
Declare `delegate` in global scope.
Use `BindUFunction` and `ExecuteIfBound`.
The bound method needs `UFUNCTION()`.

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

Like a Delegate, but holds several functions.
Equivalent to Cpp dynamic multicast, `DECLARE_DYNAMIC_MULTICAST_DELEGATE()`. No return value: it must be void. #cpp_different
Declare `event` in global scope.
Use `AddUFunction()` and `Broadcast()`.
The bound methods need `UFUNCTION()`.

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

Source: Hazelight documentation: Events example (excerpt; remaining lines omitted).

### Events in Blueprint

Mark the Event `UPROPERTY()` to expose it under Event Dispatchers, or Class Defaults → Events.

### Automatic signatures in Visual Studio Code

When binding a method that does not exist, use the light bulb or Ctrl+. → Generate Method to create it.

```cpp
	UFUNCTION(BlueprintOverride)
	void BeginPlay()
	{
        OnExampleEvent.AddUFunction(this,n"OnExampleEventCalled");
	}
    // the function below can be created automatically
	UFUNCTION()
	private void OnExampleEventCalled(int Counter)
	{
	}
```

# Mixin Methods

Declare methods outside a class. They can extend cpp classes or share functionality across types. The first parameter is the receiver type; the rest are ordinary arguments.

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

Add & for a struct mixin to allow modification:

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

Mixins can also be added from cpp.

# Gameplay Tags

`FGameplayTag` binds in the global `GameplayTags` namespace. Non-alphanumeric characters, including dots, become underscores, `_`.

```cpp
// Assuming there is a GameplayTag named "UI.Action.Escape"
FGameplayTag TheTag = GameplayTags::UI_Action_Escape;
```

# Editor-Only Script

## Preprocessor Blocks

`#if EDITOR` and `#endif` wrap Editor-only code:

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

Other useful conditions:
`EDITORONLY_DATA` - Whether properties that are only relevant to the editor are readable.
`RELEASE` - Whether the game is built in either the Shipping or Test build configurations.
`TEST` - Whether the game is built in Debug, Development, or Test build configurations.

## Editor-Only Directories

Cooked builds automatically ignore directories named `Editor`, `Examples` and `Dev`.

## Testing with Simulate-Cooked Mode

This checks whether Editor-only code accidentally affects the game.

`-as-simulate-cooked` simulates a cooked build and can be combined with `AngelscriptTest`.

```shell
UnrealEditor-Cmd.exe "MyProject.uproject" -as-simulate-cooked -run=AngelscriptTest
```

# Subsystems

## Using a Subsystem

Use `USubsystemClass::Get()`. Many are Editor Subsystems and cannot be used by the game; keep them in Editor-only scripts.

```cpp
void TestCreateNewLevel()
{
    auto LevelEditorSubsystem = ULevelEditorSubsystem::Get();
    LevelEditorSubsystem.NewLevel("/Game/NewLevel");
}
```

## Creating a Subsystem

Five bases are available:

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

Subsystem `UFUNCTION`s are exposed to Blueprints.

## Local Player Subsystems

Pass `ULocalPlayer` to `::Get()` for a Local Player Subsystem. Passing `APlayerController` directly also works.

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

For File.as, tests normally go in File_Test.as.

### Running Unit Tests

Unit tests run on hot reload. Results appear in Windows → OutputLog in the Editor.
Command-line testing is available too:

```shell
Engine\Binaries\Win64\UnrealEditor-Cmd.exe \Path\To\your.uproject -NullRHI -NoSound -NoSplash -ExecCmds="Automation RunTests Angelscript.UnitTests" -TestExit "Automation Test Queue Empty+Found 0 Automation Tests, based on" -unattended -stdout -as-exit-on-error
```

### A Custom Game Mode for Unit Tests

Configure a test-specific GameMode in the project ini:

```ini
[/Script/EngineSettings.GameMapsSettings]
...
+GameModeClassAliases=(Name="UnitTest",GameMode="/Game/Testing/UnitTest/BP_UnitTestGameMode.BP_UnitTestGameMode_C")
```

## Integration Tests

MyTestName_IntegrationTest.as:

```cpp
void IntegrationTest_MyTestName(FIntegrationTest& T)
{
}
```

Put IntegrationTest_MyTestName.umap under /Content/Testing/. Its name must match the test name, with .umap appended.
The root is configurable in ini:

```ini
[/Script/AngelscriptCode.AngelscriptTestSettings]
IntegrationTestMapRoot=/Game/Testing/
```

Tests can find placed Actors or spawn them:

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

Source: Hazelight documentation: integration-test Actor lookup (excerpt; remaining lines omitted).

### Latent Automation Commands

These let tests wait through latent commands.

### Running Integration Tests

Integration tests do not run automatically. Use Unreal’s Test Automation window.
The command-line form resembles unit tests, replacing Angelscript.UnitTests with Angelscript.IntegrationTests.
Find it under Tools → Session Frontend:
https://dev.epicgames.com/documentation/en-us/unreal-engine/automation-system-user-guide-in-unreal-engine?application_version=5.4

### Complex Integration Tests

Tests can also be generated dynamically:

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

Enabling coverage adds about 20 seconds to Editor startup, so remember to turn it off.
Reports go to Saved/CodeCoverage. Open index.html to view them.

# Differences for C++ Unreal developers

## Objects Instead of Pointers

A `UObject` variable automatically becomes an object reference. No pointers, no `->`, only dots. A Cpp reference is essentially a non-null pointer.
Properties need not be marked `UPROPERTY()` just to avoid collection. All script object references are added to GC automatically.

```cpp
void TeleportActorToOtherActor(AActor ActorReference, AActor TeleportToActor)
{
    FTransform TeleportToTransform = TeleportToActor.GetActorTransform();
    ActorReference.SetActorTransform(TeleportToTransform);
}
```

## Default Property Accessibility

`UPROPERTY()` defaults to `EditAnywhere` and `BlueprintReadWrite`.
Use `NotEditable` and `NotBlueprintCallable` to restrict access.
Change these defaults in Project Settings → Plugins → Angelscript.
**The aim is simpler specifiers. UPROPERTY() no longer controls GC; declaring it means allowing Editor and Blueprint access.**

## Use default Instead of Constructors

Configure subobject properties with default:

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

UE began using double in 5.0 but kept the name float to avoid confusing Blueprint users.
AS follows that choice: script float is a 64-bit double. Use explicit `float32` or `float64` for a specific width.

```cpp
float ValueDouble = 1.0; // <-- This is a 64-bit double-precision float
float32 ValueSingle = 1.f; // <-- This is a 32-bit single-precision float
float64 ValueAlsoDouble = 1.0; // <-- This is *also* a 64-bit double-precision float
```

Double can still be written. Project Settings → Plugins → Angelscript can disable that spelling.

Consequently, cpp float must be float32 in binding signatures.

To avoid confusion between 32-bit cpp float and 64-bit AS float, consider explicitly writing float32 and float64, or double.
# Automatic Bindings

The rule: if Blueprint can use it, scripts should be able to use it.
If it can be used from Blueprint, it should be usable from Angelscript.

## Class Bindings

`UCLASS()` with `BlueprintType` or `BlueprintCallable` methods is bound.
Add `NotInAngelscript` to skip it.

## Struct Bindings

`USTRUCT()` with `BlueprintType` or any Blueprint-readable or editable property is bound.

Use `NoAutoAngelscriptBind` to skip it.

## Property Bindings

### Read/Write Flags

`BlueprintReadWrite` or `BlueprintReadOnly` properties bind automatically. BlueprintReadOnly becomes const and cannot be modified in scripts.

For script-only access, use `ScriptReadWrite` or `ScriptReadOnly`.

### Editable Flags

Properties marked `EditAnywhere`, `EditInstanceOnly` or `EditDefaultsOnly` are bound.
An editable property without a Blueprint access flag can only be accessed through a `default` statement in scripts.

### Skipping Properties

`NotInAngelscript` skips a property even with Blueprint-access flags.

## Function Bindings

### Callable Flags

`BlueprintCallable` or `BlueprintPure` UFUNCTIONs bind automatically.
Use only `ScriptCallable` to expose a function to AS without Blueprint access.

### Blueprint Events

`BlueprintImplementableEvent` and `BlueprintNativeEvent` functions can be overridden by scripts and Blueprints.

### Skipping Functions

`NotInAngelscript` skips functions even when Blueprint-callable.

### Deprecated Functions

Deprecated functions are not bound.
Scripts have no deprecation warnings, so an engine upgrade may require script changes when Epic deprecates APIs.

### Static Functions

Static UCLASS functions bind into global libraries with simplified namespaces.

### Enum Bindings

Any `UENUM()` is available in scripts.

# Script Mixin Libraries

Cpp lets us expose content unavailable to Blueprints and therefore scripts. Mixins inject functions without changing the original cpp class.

## Mixin Libraries for Structs

Inject FUNCTIONs into Structs. Ordinary struct methods cannot have UFUNCTION and therefore do not auto-bind; Mixins supply them.

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

Inject FUNCTIONs into existing Classes without editing their source:

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

The script plugin already supplies many Mixins not exposed to Blueprints:
Engine/Plugins/Angelscript/Source/AngelscriptCode/Public/FunctionLibraries

# Using Precompiled Scripts

### Precompiled script support

#### What it does

Normally the plugin reads, parses and compiles every `.as` file in the project script directory at engine startup.
That can take time on devices with slow CPUs or storage.

A packaged game can generate a **precompiled script cache** to improve startup.
When the cache exists, the plugin loads compiled bytecode from it instead of loading and compiling each source file.

The plugin can also **transpile scripts to C++ source**. These files perform the same work as bytecode. Add them to the project and rebuild the game executable; AngelScript’s JIT system replaces VM execution with native C++, substantially improving script execution speed.

---

### Usage

#### Generate a precompiled script cache

**Generate the cache with the same .exe that will load it.**

1. **Package the game**
   Use the desired configuration.

2. **Run the packaged executable to generate the cache**
   Launch `ProjectName.exe` with:

   ```bash
   -as-generate-precompiled-data
   ```

3. **Generated cache**
   This creates `PrecompiledScript.Cache` under `ProjectName/Script/`.
   Include it in the distributed game.

4. **Load the cache**
   The next launch loads precompiled scripts instead of parsing and compiling `.as` files.

---

#### Transpile C++ code

The generation step also writes `AS_JITTED_CODE/`, with a C++ file corresponding to each script file.

1. **Copy the generated code into the project**
   Put `AS_JITTED_CODE/` in the project source directory.

2. **Rebuild the game executable**
   Compile the .exe with that directory included.

3. **Run the game**
   With the new executable and PrecompiledScript.Cache, the plugin runs optimized C++ instead of the original bytecode.

---

### Compatibility

The cache contains hard-coded C++ property offsets and struct sizes. These constraints follow:

1. **Match cache and executable**
   **Never** load one executable’s generated cache with another executable.
   Regenerate the cache after rebuilding the .exe.

2. **Script changes need not rebuild the executable**
   Scripts can change and generate a new cache without recompiling the .exe.
   **However**, if the executable includes generated C++ code, the new cache no longer matches the old .exe; rebuild it.

---

### Dynamic script reload limits

- With PrecompiledScript.Cache, `.as` source is not loaded. Source edits have no effect and hot reload is unavailable.

- To bypass precompiled data and return to development mode, add:
  ```bash
  -as-development-mode
  ```

This restores direct `.as` loading.

# Development Status

## Platform Support

Hazelight has tested Windows, PS5 and Xbox Series X|S. Other teams report other platforms working.

## Known Limitations

`Super::Function()` only calls AS parent methods, not C++ BlueprintNativeEvent implementations.
Unreal Interfaces, IInterface/UInterface, are unavailable in AS.
