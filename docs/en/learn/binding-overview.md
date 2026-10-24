---
title: "UE_Angelscript — Binding overview: expose more to AS and Blueprints"
order: 50
category: binding
---
# UE_Angelscript — Binding overview: expose more to AS and Blueprints

## Preface

This article does not dig deeply into the Angelscript (AS) plugin’s internals. It stays at the application level and gives an overview without concrete code.

In cpp, UE’s reflection system recognizes declarations such as UCLASS and USTRUCT. Much of that reflected content is exposed to Blueprints. Put simply, being recognized by UE reflection is a prerequisite for Blueprint visibility. That covers most cases; I will not chase every exception.

AS also uses UE reflection and therefore gets broadly the same bindings as Blueprints. Most Blueprint classes and functions are already bound in AS. Most, mind you: some are Blueprint-only or still missing from AS.

But we want more than Blueprint-like functionality. We want more freedom to reach engine code.

That raises a question: how do we expose cpp code that reflection does not recognize?

There are two broad directions. Bind existing classes through manual registration or Mixins, or inherit, wrap and convert existing classes. Creating your own class makes changes easier.

Everything below assumes you do not want to modify source.

## Manual binding

Look at files beginning with Bind_ in the AS plugin to see existing manual bindings and learn how they work. The code is not too hard, and the plugin supplies helper macros.

Here are the things to watch.

### When is manual binding necessary?

1. A class is not exposed to UE reflection or Blueprints, but we want it.

2. The class is exposed to Blueprints but a member we want is not. We do not want to inherit a class just to reach that member, or write separate Mixin Get and Set functions.

There is another case: a member is exposed as read-only or construction-only. Full access still requires Get or Set functions through manual binding or a Mixin.

3. We want operators such as == and != on the class in AS. At present, manual binding or Mixin binding seems to be the way.

AS maps special function names to operators, such as opEquals to ==.

### What needs care in manual binding?

1. Registration order. Some classes depend on others; failing to register the dependencies first can cause problems.

2. Cpp float must bind as float32.

3. AS scripts have no raw pointers. UClass types become nullable objects, but structs cannot be nullptr and are references. When converting a struct pointer, check whether it can be null so you do not accidentally access an invalid pointer.

4. UE struct inheritance does not inherit bindings. Bind every type you need. Templates or macros can help process them in batches.

5. A UStruct may be BlueprintType, while its derived Ustruct is not and adds no new Blueprint-exposed members. That derived UStruct will not be exposed to AS and needs binding. I usually add BlueprintType, which does not change engine source.

## Mixin binding

Mixins can bind only functions. Think of a static function that receives a class pointer and uses it to modify the object. AS makes calling it look like calling a method on that class. That alone is useful: dot syntax can call a method that did not originally exist on the class, extending it without changing its code.

### When are Mixins useful, and why?

1. UStruct methods cannot be UFUNCTIONs. If you need more functionality on a UStruct and cannot easily change its source, use a Mixin. Manual binding can add it too, but is less direct. A Mixin can also expose its existing ordinary member functions.

2. After several levels of inheritance, a Mixin is convenient for adding behavior to a class in the middle.

3. A class may have many static functions that are awkward to call without dot syntax. A Mixin converts them easily; an AS Mixin is particularly convenient here.

### When are Mixins inconvenient?

Because they bind only functions, types not exposed to AS can be awkward and may need wrapping or conversion.

Mixins work entirely outside the class, so naturally they cannot access Protected members.
## Inheritance, wrapping and conversion

### When is inheritance useful, and why?

I recommend a cpp middle layer for frequently used AS classes. It makes extension convenient, especially virtual overrides: expose a BP version or broadcast a Blueprint-visible dynamic delegate.

Protected members are accessible only to their own class and subclasses. Without changing source, inheritance is the way to reach them.

Also, a parent member marked UPROPERTY can be modified through reflection in a constructor and then exposed to AS. Some Blueprint read-only members, for example, can be made read-write.

### When is wrapping useful, and why?

Here, wrapping means creating a UStruct with a native cpp struct or class as a member. In cpp, those two differ mainly in access permissions.

The new UStruct can expose the wrapped class’s members and methods through manual binding or Mixins.

Is that unnecessary duplication? It has specific uses.

1. Some desired functions take native cpp structs. If you want to preserve roughly the same call style, a wrapper is fairly elegant: replace the parameter type and add a small conversion.

2. AS does not support some things, such as TSharedPtr lifetime management for structs. Wrapping is then necessary. Why is TSharedPtr unsupported? It cannot be UPROPERTY, which could confuse designers. Designer-friendly behavior comes with trade-offs.

3. You want a native cpp struct as a TMap key. FObjectKey, for example, still cannot be a TMap key after manual binding, despite being made for that purpose. I reluctantly wrapped it. This is uncertain; I do not know whether it applies to all native structs.

### When is conversion necessary?

Conversion here means creating something similar but different, with no inheritance or containment relationship to the original. Delegates are the most common example.

Only two delegate forms bind to AS: dynamic delegates become AS delegates, and dynamic multicast delegates become AS events. Dynamic delegates can be UFunction parameters; dynamic multicast delegates can only be class members.

UE needs performance and small memory footprints. Dynamic delegates cost more resources, so native code uses ordinary delegates wherever Blueprint access is unnecessary.

1. Sometimes a cpp function we want takes an ordinary single-cast or multicast delegate. That needs conversion.

Declare a corresponding dynamic delegate, substitute it in a Mixin wrapper, then convert between the delegates in the implementation.

2. Sometimes an ordinary delegate is a class member, and we want an AS function bound to it. If manual binding cannot expose the delegate, add a Mixin much like the conversion above, except you must write the binding logic yourself.

## Summary

Giving AS access to more engine code takes binding work. These are mostly my own views; discussion is welcome if something is wrong.

Not everything is easy to bind. My rough order from easiest to hardest is UClass, UStruct, native struct, then delegate conversion. Fortunately, the common bindings and the hardest template-shaped ones are already provided. For more than Blueprints offer, consider binding, binding, binding.
