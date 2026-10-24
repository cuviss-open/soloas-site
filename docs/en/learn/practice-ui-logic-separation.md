---
title: "UE_Angelscript — Separating UI Blueprint presentation and logic"
order: 34
category: practice
---
# UE_Angelscript — Separating UI Blueprint presentation and logic

A UI has all sorts of widgets. The UE editor is the best place to work on their appearance: what you see is what you get. Their logic usually lives in UI Blueprints, but with so many widgets, maintenance becomes a headache.

Since switching to AS for UI logic, I can put all that scattered logic into code files. It is much easier to manage, and presentation is separated from logic: the UI editor handles appearance, while scripts handle behavior.

The official documentation does not say much about this either.

# A tiny architecture for separating UI Blueprint presentation and logic

One sentence: every widget in the UE editor inherits from an AS class.

Usually they have a one-to-one relationship. A UI widget and an AS class are technically child and parent, but with binding, I think of them as companions.

Move inheritance between UI widgets into the AS classes where possible. In other words, avoid inheritance between UI Blueprints. Why? Because it breaks the one-to-one relationship and makes changes less direct. Enough of that and the complexity can grow considerably.

I will expand on the simple Example_Widget_UMG.as example below.

This tiny architecture naturally starts with a UI-related class inherited from cpp.

```cpp
class UExampleWidget : UUserWidget
```

# Matching UI Blueprint widgets to AS members

Every UI Blueprint widget marked as a variable automatically creates a Blueprint variable, which AS can bind.

This code binds the UI Blueprint’s UTextBlock named MainText as an AS variable.
Once bound, the variable disappears from the Blueprint variable list. The Blueprint can still use it, of course, if you want logic there too.

```cpp
class UExampleWidget : UUserWidget
{
	// bind the Blueprint variable named MainText to this AS variable
    UPROPERTY(BindWidget)
    UTextBlock MainText;
}
```

An extension: UI Blueprints often have animations. Those can be bound too, with these parameters:

```cpp
    UPROPERTY(BindWidgetAnim)
    UWidgetAnimation OnSpawned;
```

With the necessary variables bound, it is time to write the logic.

# PreConstruct and Construct

PreConstruct and Construct are used often, much as they are in UI Blueprints.

```cpp
	UFUNCTION(BlueprintOverride)
	void PreConstruct(bool IsDesignTime)
	{
		AttributeNumber.Font.Size = 12;
	}

   UFUNCTION(BlueprintOverride)
    void Construct()
    {
    }
```

# Binding UI events

If the current UI class owns the event, override the corresponding function directly. Buttons, for example, have OnClicked, OnHovered and OnUnhovered.

For an event on another UI widget, use delegate binding.

Here is an example using CommonUI’s Button class:

```cpp
// the current class is the subject whose events need binding, so just override the function
	UFUNCTION(BlueprintOverride)
	void OnClicked()
	{
	}

// the subject whose events need binding is a member of the class, so bind that member's delegate
YourBoundButton.OnButtonBaseClicked.AddUFunction(this,n"OnButtonBaseClicked")
```

# Checking a UI Blueprint (optional)

OnValidateCompiledWidgetTree is a cpp function for checking UI Blueprints. When a check fails, it can report a Blueprint compilation error.

A UI Blueprint can contain many widgets with special configuration requirements. For example, several copies of the same widget may need different settings as well as different names. Check that here.

The UI Blueprint error-reporting code has no Blueprint version, so AS cannot call it directly either. This needs some manual wrapping and binding. The final result looks like this:

```cpp
#if EDITOR
	UFUNCTION(BlueprintOverride)
	void OnValidateCompiledWidgetTree(const UWidgetTree BlueprintWidgetTree) const
	{
		if (OptionsClass.IsNull())
		{
			ShowCompileLog_Error("OptionsClass is null! Check and Set it in the Editor!");
		}
		if (UserFacingExperience == nullptr)
		{
			ShowCompileLog_Error("UserFacingExperienceDefinition is null! Check and Set it in the Editor!");
		}
		if (QuitGameClass.IsNull())
		{
			ShowCompileLog_Error("QuitGameClass is null! Check and Set it in the Editor!");
		}
	}
#endif
```

ShowCompileLog_Error is a function I added in cpp to report errors.

This wrapping and binding is a little involved: inherit the commonly used UI Blueprint classes and add the functionality there. I will skip those details.

# Decoupled interaction with other classes (optional)

UI Blueprint interaction with other classes often means writing lots of references. Delegates can decouple some of that, but still need at least a one-way reference. Can two classes exchange information without knowing each other? Yes: the global broadcast system UGameplayMessageSubsystem.

This SubSystem has AS bindings. The official documentation provides the [GameplayMessageRouter with Angelscript](https://github.com/IncantaUnreal/GameplayMessageRouter) binding. Its usage is simple and explained in the Readme, so I will not repeat it.

It can decouple UI Blueprints from other code easily. After registering a listener, remember to unregister when it is no longer needed.

# Summary

Let presentation be presentation and logic be logic: the familiar separation of front end and back end. AS’s companion binding for UI Blueprints makes that easy.

It also solves another issue along the way: casts between UI Blueprints gradually expand asset references, while casts between code classes do not have that problem.

Decoupling UI Blueprint presentation and logic has plenty of benefits. A bright future for everyone!

---
