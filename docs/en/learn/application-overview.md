---
title: "UE_Angelscript in practice"
order: 1
category: getting-started
---
# UE_Angelscript in practice

Everything here contains some personal interpretation. Take it as reference.

# Documentation overview

Mostly notes summarizing the official documentation.

[UnrealEngine-Angelscript: an overview of the official documentation](official-documentation-overview.md)

# Getting started

How to set up a UE engine that supports Angelscript, with beginners in mind.

[UE_Angelscript — Getting started: install the engine and open the sealed gate](getting-started-install-soloas.md)
[UE_Angelscript — Getting started: getting to know the engine again, familiar yet different](getting-started-engine.md)

# Concepts

Basic ways to think about Angelscipt as a UE scripting language.

[UE_Angelscript — What a bound UClass looks like](concepts-bound-uclass.md)
[UE_Angelscript — A project structure to work with](concepts-project-structure.md)
[UE_Angelscript — Understanding copies and references](concepts-copy-and-reference.md)

# Practice

Practical topics worth writing down, often a little different from ordinary UE development.

[UE_Angelscript — Extending the Editor is as easy as drinking water](practice-editor-extensions.md)
[UE_Angelscript — Separating UI Blueprint presentation and logic](practice-ui-logic-separation.md)
[UE_Angelscript — Extending Animation Blueprints: write the main calculations in code](practice-animation-blueprints.md)
[UE_Angelscript — Free your components and make features modular](practice-component-modularity.md)
[UE_Angelscript — Garbage collection and reflection for class members](practice-gc-reflection.md)
# Binding

An introduction to binding cpp functionality for AS, plus solutions to awkward problems.

[UE_Angelscript — Binding overview: expose more to AS and Blueprints](binding-overview.md)
[UE_Angelscript — Pitfalls: you never know until you step in one](binding-pitfalls.md)
[UE_Angelscript — A remedy for missing Unreal Interfaces](binding-unreal-interfaces.md)
[UE_Angelscript — Binding native and DataTable GameplayTags](binding-gameplay-tags.md)
[UE_Angelscript — A better way to handle BlueprintInternalUseOnly functions](binding-blueprint-internal-use-only.md)

Manual binding
[UE_Angelscript — Manual binding 1: the basics](binding-manual-basics.md)
[UE_Angelscript — Manual binding 2: a binding handbook](binding-manual-reference.md)

Advanced topics
[UE_Angelscript — Call delegates freely: it looks unreal, but it is in your hands](binding-delegates.md)

# Tricks of the trade

Ways to make writing code more comfortable and efficient.

[UE_Angelscript — Tricks of the trade](tips-mixins-and-reflection.md)
[UE_Angelscript — Tricks 2: sometimes one sentence clears up a head-scratcher](tips-five-common-surprises.md)
[UE_Angelscript — Tricks 3: if(Obj) or if(Obj != nullptr)? I pick if(Obj)](tips-object-validity-checks.md)

# Source walkthroughs

Direct source analysis, a step up in complexity. Beginners beware — unless you are feeling bold.

[UE_Angelscript — Source 1: how UE classes are bound to AS](internals-ue-types-to-angelscript.md)
[UE_Angelscript — Source 2: how AS classes are bound to UE](internals-angelscript-classes-to-ue.md)

# Digressions

Just some interesting explorations.

[Nobody can stop me using pointers, except myself](essays-pointers-and-ownership.md)
[Nobody can stop me using lambdas, except myself](essays-lambda-design.md)
[A digression: dynamic types, async and multithreading in AngelScript — I want them all](essays-dynamic-types-and-tasks.md)

---
