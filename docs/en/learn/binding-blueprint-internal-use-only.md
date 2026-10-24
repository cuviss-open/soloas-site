---
title: "UE_Angelscript — A better way to handle BlueprintInternalUseOnly functions"
order: 54
category: binding
---
# UE_Angelscript — A better way to handle BlueprintInternalUseOnly functions

The problem started with useful functions callable in Blueprints but unavailable in AS. Many belong to BlueprintAsyncActionBase or subclasses.

Exposing their BlueprintInternalUseOnly functions was the starting point, but not the whole problem. Other useful classes, such as UGameplayTask and its subclasses, need attention too.

Why not expose every BlueprintInternalUseOnly function? Is it impossible? Quite the opposite: the scripting plugin deliberately skips them. The marker hides functions from ordinary Blueprints, which use another mechanism to call them. Exposing all of them to AS could violate the class designer’s intent and perhaps cause confusion.

The better approach is to keep them hidden by default and let users select the classes they need.

### Solution 1, basic: remove BlueprintInternalUseOnly; the side effect is duplicate Blueprint functions

The following handles BlueprintAsyncActionBase and subclasses by removing BlueprintInternalUseOnly. Blueprints then show two similar functions: an async version and an ordinary version.

If that duplication does not bother you, this is convenient. Change the metadata of whichever classes the project needs.

Solution 1 comes from the official forum discussion: remove `BlueprintInternalUseOnly` metadata from selected class functions before binding.

That code comes from an AS community discussion. There is room to optimize, such as caching the target UClass pointer instead of repeatedly looking it up:

```cpp
static TArray<UClass*> CachedAsyncActionClasses;
if (CachedAsyncActionClasses.IsEmpty())
{
    for (TObjectIterator<UClass> It; It; ++It)
    {
        if (It->IsChildOf<UBlueprintAsyncActionBase>())
        {
            CachedAsyncActionClasses.Add(*It);
        }
    }
}
```

### Solution 2, revised: edit Bind_BlueprintCallable:36 in the AS plugin

Modified from a solution discussed on the forum.

The following handles BlueprintAsyncActionBase, UGameplayTask and subclasses, binding only static functions returning their own type.

```cpp
// BlueprintInternalUseOnly functions are not bound
// Engine Divergence Start - tdxh - BP Async Actions aren't visible in AS
// Original line: if (Function->HasMetaData(NAME_Function_BlueprintInternalUseOnly)) return;
if (Function->HasMetaData(NAME_Function_BlueprintInternalUseOnly))
   {
       TArray<UClass*> ClassesToBind
       {
            UBlueprintAsyncActionBase::StaticClass(),
            UGameplayTask::StaticClass() // For GAS , so many AbilityTask!
       };

       UClass* OwningClass = CastChecked<UClass>(Function->GetOuter());

    bool bIsChildOfAnyClass = ClassesToBind.ContainsByPredicate([OwningClass](const UClass* Class) {
       return OwningClass->IsChildOf(Class);
    });
    if (!bIsChildOfAnyClass) return;

       const FProperty* ReturnProperty = Function->GetReturnProperty();
       if (ReturnProperty)
       {
            const FObjectProperty* ObjectProperty = CastField<FObjectProperty>(ReturnProperty);
            if (ObjectProperty && !ObjectProperty->PropertyClass->IsChildOf(OwningClass))
            {
               return;
            }
       }
}
// Engine Divergence End
```

Previously, encountering BlueprintInternalUseOnly stopped binding immediately. The revision allows a function when its class is UBlueprintAsyncActionBase or a subclass and its return type is itself — the common static factory pattern.

Adding UGameplayTask::StaticClass() also requires "GameplayTasks" in PrivateDependencyModuleNames in AngelscriptCode.Build.cs.

Note: solutions 1 and 2 came from the official forum discussion. I only modified solution 2 slightly.

**After solution 2, bind Active or ReadyForActivation yourself too. Blueprints invoke these automatically; cpp and AS must call them.**
AngelscriptGAS already binds ReadyForActivation and many AbilityTask functions in the AngelscriptAbilityTask namespace.

Example Active binding:

```cpp
UCLASS(Meta = (ScriptMixin = "UBlueprintAsyncActionBase"))
class XXXX_API UBlueprintAsyncActionBase_MixinLibrary : public UObject
{
    GENERATED_BODY()

public:
    UFUNCTION(ScriptCallable)
    static void BP_Activate(UBlueprintAsyncActionBase* BlueprintAsyncActionBase)
    {
       return BlueprintAsyncActionBase->Activate();
    };
};
```

### Solution 3, enhanced: configure which BlueprintInternalUseOnly functions to expose

Adding another class to solution 2 requires source and include changes, which is tedious. Could configuration make that easier?

Use an ini file: read the desired classes when AS loads, then check them during binding.

A global singleton avoids rereading the file for every function.

##### 1. Design the configuration file

Create a file such as AngelscriptBindSetting.ini in the engine’s Config directory:

```ini
; Prefix dont allow
[BindTheClassWithMetaBlueprintInternalUseOnly]
ClassesToBind=BlueprintAsyncActionBase
ClassesToBind=GameplayTask
ClassesToBind=AnimInstance
```

Add more lines for more classes. **Omit class-name prefixes.**

##### 2. Add a singleton in Bind_BlueprintCallable

It is constructed on first use and not again afterward.
Its main job is to read the ini, resolve the named classes and store them in ClassesToBind.

This uses lazy initialization: only the static GetInstance call creates it.

```cpp

class FClassesToBind_BlueprintInternalUseOnly
{
public:
    static FClassesToBind_BlueprintInternalUseOnly& GetInstance()
    {
       static FClassesToBind_BlueprintInternalUseOnly Instance;

       // Only call Initialize() if not already initialized
       if (!Instance.bInitialized)
       {
          Instance.Initialize();
       }

       return Instance;
    }

	bool ShouldBindClass(const UClass* InClass) const
	{
		for (const UClass* ClassToBind : ClassesToBind)
		{
			if (InClass->IsChildOf(ClassToBind))
				return true;
		}
		return false;
	}

    // Initialized and ClassesToBind is not Empty
    bool IsValid() const
    {
       return bInitialized && !ClassesToBind.IsEmpty();
    }

private:
    /** only GetInstance() can access this function */
    FClassesToBind_BlueprintInternalUseOnly()
    {
       // Lazy Initialization to Initialize()
}

    void Initialize()
    {
       if (bInitialized) return;

       TSet<FName> ClassesToBindNames;

       // explicit load AngelscriptBindSetting.ini
       const FString ConfigFilePath = FPaths::Combine(FPaths::EngineConfigDir(), TEXT("AngelscriptBindSetting.ini"));

       if (!FPaths::FileExists(ConfigFilePath))
       {
          UE_LOG(LogTemp, Warning, TEXT("Can not find .ini:  %s"), *ConfigFilePath);
          return;
       };
       GConfig->LoadFile(ConfigFilePath);

       const FString ConfigSection = TEXT("BindTheClassWithMetaBlueprintInternalUseOnly");
       const FString KeyName = TEXT("ClassesToBind");
       TArray<FString> ClassNames;

       if (GConfig->GetArray(*ConfigSection, *KeyName, ClassNames, ConfigFilePath))
       {
          for (const FString& ClassName : ClassNames)
          {
             ClassesToBindNames.Emplace(FName(*ClassName));
             UE_LOG(LogTemp, Log, TEXT("ClassesNameToBind from ini:  %s"), *ClassName);
          }
       }
       else
       {
          UE_LOG(LogTemp, Warning, TEXT("ConfigFile ' %s ' have not ConfigSection: %s or KeyName:  %s"), *ConfigFilePath,*ConfigSection, *KeyName);
          return;
       }

       for (TObjectIterator<UClass> It; It; ++It)
       {
          if (ClassesToBindNames.Contains(It->GetFName()))
          {
             UE_LOG(LogTemp, Log, TEXT("Binding BlueprintInternalUseOnly: %s"), *It->GetName());
             ClassesToBind.Emplace(*It);
          }
       }

       bInitialized = true;
    }

private:
    TSet<UClass*> ClassesToBind;
    bool bInitialized = false;
};
```

To put the ini in the project’s Config directory instead, change EngineConfigDir to ProjectConfigDir. Each project can then use a different file. I do not need that, so I kept mine in the engine. Both locations could also be read and loaded if you modify the code when needed.

3. Modify BindBlueprintCallable

Check ClassesToBind first and skip when empty. The rest largely matches the previous solution.

```cpp
// BlueprintInternalUseOnly functions are not bound
// Engine Divergence Start - tdxh - BP Async Actions aren't visible in AS
// Original line: if (Function->HasMetaData(NAME_Function_BlueprintInternalUseOnly)) return;
if (Function->HasMetaData(NAME_Function_BlueprintInternalUseOnly))
   {
    if (!FClassesToBind_BlueprintInternalUseOnly::GetInstance().IsValid()) return;

       UClass* OwningClass = CastChecked<UClass>(Function->GetOuter());

    if (!FClassesToBind_BlueprintInternalUseOnly::GetInstance().ShouldBindClass(OwningClass)) return;
}
// Engine Divergence End
```

Solution 2 checked whether the function returned the current Class or a subclass, binding only those results. That restriction is removed here: many useful functions return something else and can still be exposed to AS.

This primarily demonstrates configuration-driven binding selection. I wrote the code and have not tested it extensively, so treat it as an implementation idea.
# Summary

If you previously bound BlueprintInternalUseOnly functions individually, then expose them through this approach too, AS may report ambiguous names. Prefixes such as BP\_ get removed, leaving identical names and parameters. The diagnostic may ask you to change AS code, but the real fix is removing redundant bindings.

Sometimes it is a duplicate registration rather than merely an ambiguous name, because the binding uses exactly the same name without prefixes or suffixes:
Failed in call to function 'RegisterObjectMethod' with 'UBlueprintAsyncActionBase' and 'void Activate()' (Code: asALREADY_REGISTERED, -13)

Comment out the earlier redundant binding in that case.

One final reminder: test the code. It currently works on my machine and in my environment.

---
