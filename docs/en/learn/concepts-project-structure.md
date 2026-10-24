---
title: "UE_Angelscript — A project structure to work with"
order: 12
category: concepts
---
# UE_Angelscript — A project structure to work with

After some experimenting, I have settled on a few rules for project structure.
These are the rules I currently use for myself, just for reference.

# Inheritance — Blueprint --> AS --> Cpp

## Every class inherited in AS comes through a Cpp middle layer.

The AS portion of It Takes Two’s game code is public. A quick read shows that its Actors do not inherit directly from the engine’s AActor; they inherit from a separate AHazeActor. Outside inheritance, AActor is still used normally.

That suggests a middle layer between the engine and AS code, with a few benefits:
When you need to add or change something, do it in your own middle layer. You are not left staring at an engine class, unsure whether to change it. Binding and other modifications are also freer in that layer.

## Most Blueprints have an AS parent.

Blueprints are convenient to configure and avoid hard-coded paths. Using AS does not mean abandoning Blueprints when they are useful. I prefer treating them as configuration tables. AS code can also easily find which Blueprint inherits a class, and navigation is convenient.
Having an AS parent makes iteration quick: edit, save, and it is ready, just as quickly as writing a Blueprint script and saving it.

Using a Blueprint class as a member in AS is much like Cpp. For a `UUserWidget` class, for example, use `TSubclassOf<UUserWidget>`.

# Composition — Actor + Component throughout

## Important Actor inheritance chains include ModularGamePlayActors.

This module is in Valley of the Ancient or Lyra.
Its benefit is automatic AddComponent behavior for GameFeatures.

## Make a project-specific Actor middle layer.

Inheriting Actors is common. To avoid inheriting directly from AActor and keep things flexible, make your own general-purpose Actor. If one is not enough, make several.

Optionally, add a switch and implement GameFeature auto-add behavior, following ModularGamePlayActors.

## Important Components inherit from ModularGamePlay.

These Components have plenty of convenient glue functions. Bind them once yourself; the function templates need special handling to return the corresponding base type.

## Put UInterfaces into ActorComponents.

Some modules use UInterface heavily. Rewriting all of that is out of the question, so wrap what can be wrapped simply.

Move the implementation from the Actor itself into its Component. For example, instead of the Actor implementing a dialogue interface, let its Component implement it.

# Subsystems — inherit from AS

AS has its own set of Subsystems:

- `UScriptWorldSubsystem` for world subsystems
- `UScriptGameInstanceSubsystem` for game instance subsystems
- `UScriptLocalPlayerSubsystem` for local player subsystems
- `UScriptEditorSubsystem` for editor subsystems
- `UScriptEngineSubsystem` for engine subsystems
  They expose many useful overridable functions through inheritance, so deriving from them saves a lot of work.

# GAS — inherit from AS

GAS (GameplayAbilitySystem) does not expose much to Blueprints to begin with. Binding it yourself would be a pain. Fortunately, the official AngelscriptGAS binding plugin is provided; just enable it.

One thing to watch: some native struct bindings need another wrapper because this plugin does not modify engine source.

Even with the many official bindings, there are still gaps that need your own Mixin or manual binding.
