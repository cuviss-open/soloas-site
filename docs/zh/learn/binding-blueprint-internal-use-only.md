---
title: "UE_Angelscript 绑定篇——解决方案：BlueprintInternalUseOnly 函数的增强处理方式"
order: 54
category: binding
---
# UE_Angelscript 绑定篇——解决方案：BlueprintInternalUseOnly 函数的增强处理方式

问题的由来，是有很多有用的函数，蓝图里可以调用，但是 AS 里却不行。这些函数有不少是属于 BlueprintAsyncActionBase 及其子类的。

于是，如何暴露 BlueprintAsyncActionBase 下的 BlueprintInternalUseOnly 的函数，成为了出发点。但这不是终点，还有其他一些类也有这类型的有用函数，比如 UGameplayTask 及其子类，它们也需要得到照顾。

为什么不全部暴露所有的 BlueprintInternalUseOnly 函数？是做不到吗？不是的，恰恰相反，AS 脚本是特意不绑定此类型的函数的。BlueprintInternalUseOnly 标记的用处是向蓝图隐藏这个函数（蓝图有另外的机制来调用这个函数），如果都给 AS 暴露出来了，实际上有违类设计者的初衷了，这会不会造成一些混淆，尚未可知。

所以，一般情况下，这类函数就禁止暴露，然后在使用者需要的时候，自行选择暴露出需要的类，才是最好的方式。

### 方案 1 基础版，直接去掉这个 BlueprintInternalUseOnly，副作用是蓝图出现两个一样的函数

以下是专门处理 BlueprintAsyncActionBase 及其子类的代码，去掉了 BlueprintInternalUseOnly 的标签，这会导致蓝图出现两个一样的函数，一个是异步的，一个是普通的。

如果不在意蓝图出现两个同样的函数，这么写也是相当方便，项目需要暴露什么类就将什么类的 Meta 修改。

方案 1 来自官方论坛的讨论，做法是在绑定前移除所选类函数上的 `BlueprintInternalUseOnly` 元数据。

以上代码以上代码来源于 AS 社区的讨论，实际上还有优化空间，比如缓存目标类的 UClass 指针，减少不必要的查找：

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

### 方案 2 修订版，修改 AS 插件源码：Bind_BlueprintCallable:36

基于论坛讨论的方案修改。

以下处理了 BlueprintAsyncActionBase 和 UGameplayTask 及其子类，只绑定了返回自身的静态函数。

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

因为原始的绑定配置里，碰到 BlueprintInternalUseOnly 就直接不绑定了，现在修改了一下，以下的情况会将这个函数绑定：这个 BlueprintInternalUseOnly 函数的 UClass 是 UBlueprintAsyncActionBase 或其子类，同时这个函数返回的是其自身（也就是常见的返回自身类的 static 函数）。

如果加了 UGameplayTask::StaticClass()这一行，需要在这个脚本模块的 cs 文件 AngelscriptCode.Build.cs 里的 PrivateDependencyModuleNames 添加上依赖模块 "GameplayTasks" 。

注：以上方案 1 和 方案 2 的内容来自于官方论坛的讨论，我只对方案 2 的内容做了一点修改。

**注意，方案 2 修改了后，还需要自己绑定 Active 函数或者 ReadyForActivation 函数，在蓝图里不需要主动调用，但是，cpp 和 AS 都需要调用的。**
（AngelscriptGAS 插件已经绑定了 ReadyForActivation，同时有大量的 AbilityTask 的函数绑定在了 AngelscriptAbilityTask 命名空间下。）

Active 函数的绑定参考如下。

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

### 方案 3 增强版：自由配置需要的 BlueprintInternalUseOnly 函数

原版本的方案 2 ，如果想要增加绑定的类，就需要修改源码，而且需要修改引用的文件，相当麻烦。是不是可以通过配置来实现方便地修改呢？

考虑的方案是通过配置 ini 文件，让 AS 加载的时候读取 ini 文件获取到我们想要跳过的类，然后在绑定的时候进行判断即可。

为了不让每次绑定的时候都读取文件获取相应的类，可以设置一个全局唯一单例来管理。

##### 1，设计配置文件

首先在引擎的 Config 文件夹下新建一个配置文件，比如 AngelscriptBindSetting.ini，内容写上

```ini
; Prefix dont allow
[BindTheClassWithMetaBlueprintInternalUseOnly]
ClassesToBind=BlueprintAsyncActionBase
ClassesToBind=GameplayTask
ClassesToBind=AnimInstance
```

之后如果想增加，就继续增加行数即可。**注意，类名不要前缀。**

##### 2，Bind_BlueprintCallable 文件里增加一个单例

这个单例会在第一次调用的时候构造，之后就不会再重新构造了。
单例的主要作用是读取配置的 ini 文件的内容并且根据内容找到对应的类，将这些类存进 ClassesToBind 这个成员里。

注意，这里的类设计实现了懒加载，只有调用了静态函数 GetInstance 才会生成实例。

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

另外，值得一提的是，如果想把 ini 文件放在项目文件夹的 Config 下，只需要修改 EngineConfigDir 为 ProjectConfigDir 就可以，这样的好处是每个项目都不同，额，不过我不需要，就在引擎里放了。当然，两个地方都放，也可以，这就需要两个地方都读取和加载了，需要的时候可以修改代码实现。

3, 修改 BindBlueprintCallable 函数

前置判断 ClassesToBind，如果为空，就直接跳过了。其余基本和之前的方案一致。

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

方案 2 里有一段代码是用来检查函数返回值是不是当前 Class 或其子类的，它限制只有这类返回值的函数才被绑定，但在这里删除掉了，因为有很多函数的函数值就不是返回自身类型的，那些函数也可以暴露给 AS 使用。

注：此方案主要提供了一个思路，通过配置来决定什么内容应该绑定到 AS 。代码来源是我写的，未经过大量的测试，所以请以参考思路为主。
# 总结

如果之前专门针对这些 BlueprintInternalUseOnly 进行过绑定，现在又采用这种方式将 BlueprintInternalUseOnly 函数暴露出来，可能会产生一些 AS 代码的冲突，比如同名函数的混淆（这来源于类似于 BP\_开头的函数会被截掉前缀，然后同名且同参数了），会要求修改 AS 的代码，实际上不需要，而是取消之前的一些绑定。

另外，有时候出现的不是同名函数，而是重复绑定的错误（这来源于绑定的时候用的同名，而不加任何前缀后缀）：
Failed in call to function 'RegisterObjectMethod' with 'UBlueprintAsyncActionBase' and 'void Activate()' (Code: asALREADY_REGISTERED, -13)

这时候就需要注释掉一些之前的绑定代码了。

最后再提一下，代码都需要测试的哦。这些代码在我的机器和运行环境下，目前没有问题。

---
