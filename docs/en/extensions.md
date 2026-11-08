# Core extensions

## UE interfaces

- AS can inherit C++, AS and Blueprint interfaces.
- Editor scripts can create new interfaces, and Blueprints can inherit interfaces created in AS.

```angelscript
interface IDamageSource
{
    int ComputeDamage(int Value);     // Define the call everyone can receive.
}
class UReceiver : UObject, IDamageSource
{
    UFUNCTION(BlueprintOverride)
    int ComputeDamage(int Value) { return Value + 17; } // Implement the call.
}
```

```angelscript
IDamageSource Target = Cast<IDamageSource>(Object); // Object is an existing reference.
if (Target != nullptr)
    Print(f"{Target.ComputeDamage(5)}");             // Call through the interface.
```

- Interface methods need no `UFUNCTION`; they are registered as Blueprint events automatically, so Blueprints can call and implement them. Add `UFUNCTION(BlueprintPure)` for a pure function (no execution pins in Blueprints; used to read values).
- Implement an interface method in a class with `UFUNCTION(BlueprintOverride)`.
- A class that implements an interface must implement every method without a default body using `UFUNCTION(BlueprintOverride)`; otherwise compilation fails.
- Methods with a default body may be left unimplemented; the class then uses the default. Changing a default method body supports soft reload.
- Restart the editor after changing interface signatures, adding or removing methods, or changing inheritance.
- Packaging and precompiled use of newly declared script interfaces are not yet supported.

## Blueprint inheritance

- A script can inherit a Blueprint parent.
- A script can inherit a Blueprint interface; see [UE interfaces](#ue-interfaces).

To inherit a Blueprint parent, first give the Blueprint a name in the project's `Config/DefaultEngine.ini`, replacing the path with your Blueprint asset path:

```ini
[SoloASCoreExtensions]
+BlueprintAliases=(Name=BP_Enemy,Path="/Game/Blueprints/BP_Enemy.BP_Enemy")
```

The script uses only the name:

```angelscript
import blueprint BP_Enemy;

class UEnemy : BP_Enemy
{
    UFUNCTION(BlueprintOverride)
    void OnBlueprintDeath() {}        // Override an event the Blueprint already has.
}
```

You can also use `CallBlueprint`, `SetBlueprintProperty` and `GetBlueprintProperty` to call functions and access variables on an existing Blueprint object. When a Blueprint inherits a script class, the editor updates the Blueprint subclass after the script parent reloads.

## Blueprint structs

Map a user-created Blueprint struct in the project `Config/DefaultEngine.ini`:

```ini
[SoloASCoreExtensions]
+BlueprintStructBindings=(Name=FMyStruct,Path="/Game/Structs/ST_MyStruct.ST_MyStruct")
```

Register every nested Blueprint struct separately. Restart the editor after changing the configuration or editing a struct used by scripts.

## Call the parent implementation of native events

When overriding a native event, call its original Unreal parent implementation from script to preserve the native default behavior.

## Lambdas for delegates and container algorithms

Use explicit captures to select variables. For value captures, write the type and name; changing the original variable later does not change the captured value.

- Delegates: bind a lambda to a delegate and remember the current variable values. Both dynamic and native delegates are supported: use `BindLambda` for a single callback and `AddLambda` for a multicast event. Delegate lambdas use typed value captures; empty captures, `this`, reference captures and nested lambdas are unsupported.

```angelscript
int Number = 17;
FString Text = "Ready";
FTimerDynamicDelegate Timer;
Timer.BindLambda([int Number, FString Text]() {
    Print(f"{Text}: {Number}");        // Use the values saved when binding.
});
System::SetTimer(Timer, 0.1f, false);   // Run once later.
```

- Container algorithms: arrays support `Sort`, `StableSort`, `FilterByPredicate`, `FindByPredicate`, `IndexOfByPredicate`, `ContainsByPredicate` and `RemoveAll`; sets and maps support `FilterByPredicate`, and maps also support `KeySort` and `ValueSort`. Algorithms run synchronously and accept empty captures, explicit value captures and explicit references to locals; object instance methods also accept `[this]`. `[&]`, capture initializers and nested lambdas are unsupported.

```angelscript
TArray<int> Values;
Values.Add(3);
Values.Add(1);
Values.Add(2);
int Direction = -1;
// Capture Direction; -1 sorts from largest to smallest.
Values.Sort([int Direction](int A, int B) { return Direction * A < Direction * B; });
```

## Turn features off as needed

These features are on by default. Plugin defaults are in `Config/Engine.ini`; put project settings in the project's `Config/DefaultEngine.ini`, for example to disable capturing lambdas:

```ini
[SoloASCoreExtensions]
bEnableExplicitCaptureLambda=false
```

Script interfaces use the `bEnableScriptInterfaces` switch. Restart the editor and regenerate precompiled caches after changing settings.
