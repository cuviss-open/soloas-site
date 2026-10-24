---
title: "Nobody can stop me using lambdas, except myself"
order: 19
category: essays
---
# Nobody can stop me using lambdas, except myself

I finally got tired of UE-Angelscript having no lambdas. Delegate binding is especially painful when you need extra parameters that the Delegate itself cannot pass!

From [UE_Angelscript — Source 2: how AS classes are bound to UE](internals-angelscript-classes-to-ue.md) in this series, we know that AS files pass through preprocessing before final compilation. Syntax sugar such as RangeBasedFor loops is parsed there too.

If preprocessing can add sugar like RangeBasedFor, adding lambdas does not sound unreasonable.

When a tool does not quite fit your hand, you polish it. That is why this article exists.

I will describe some implementation ideas for this syntax sugar and show the AS code after it is working.

# First, what does Cpp lambda syntax sugar look like?

Here is the C++ code:

```cpp
int main()
{
	auto Test = 5;

	auto add = [Test](int a, int b) {
		return a + b;
	};
	add(1, 2);

	return 0;
}
```

Internally, it becomes something like this:
Note: you can inspect C++’s underlying transformations at https://cppinsights.io/

```cpp
int main()
{
  int Test = 5;

  class __lambda_6_15
  {
    public:
    inline /*constexpr */ int operator()(int a, int b) const
    {
      return a + b;
    }

    private:
    int Test;

    public:
    __lambda_6_15(int & _Test)
    : Test{_Test}
    {}

  };

  __lambda_6_15 add = __lambda_6_15{Test};
  add.operator()(1, 2);

  return 0;
}
```

You can see an anonymous class being added. Variables captured in `[]` become its members, and it has two functions.
One is a constructor that receives the captured variables. Its parameters are references, but the members are still copies — capture by value — so the result is value passing.
The other is the call operator. `operator()` lets an object be used as though it were a function.

After declaring this class, an instance is created: `add` in the example. Calling the lambda then calls its `operator()` method.

So a lambda declares an anonymous class and creates an instance. Capturing variables just means passing them to that anonymous class’s constructor.

Captures are really, really useful syntax sugar! They save a lot of typing.

# How to build lambdas in UE-Angelscript

Following Cpp, first declare an anonymous class. UE-Angelscript gives us two choices: `struct` or `class`.

A struct is compiled as a value type, while a class inherits from UObject by default.

UObject costs more because it creates a CDO (class default object), but it has benefits too: reflection makes it easier to work with. With carefully designed ownership, lifetime management can be left to UE’s GC.

This is gameplay code, after all. Trading a little overhead for a better experience is worthwhile. I will not admit that I picked a UObject subclass just to avoid handling lifetimes myself.

With a direction chosen, let us simulate it. We are writing preprocessing code, so first sketch what the transformed output should look like.

## Set the target

This is the call syntax I have in mind:

```cpp
void Foo()
{
	// ...

	int TempInValue1 = 666;
    FString TempInValue2 = "World";
	FSomeTestDelegate TestDg;

	TestDg.AddFakeLambda([TempInValue1, TempInValue2](float32 Infloat)
	{
	  // do things
	}
	// ...
}
```

To simplify lifetime management and implementation, the lambda object will follow the lifetime of the current class by default.

Since this is syntax sugar, it replaces code. Here is the transformed code I think makes sense:

```cpp

void Foo()
{
	// ...

	int TempInValue1 = 666;
    FString TempInValue2 = "World";
	FSomeTestDelegate TestDg;

	auto Lambda_Bound = AddPart(UFakeLambda_Bound);
	Lambda_Bound.TempInValue1 = TempInValue1;
	Lambda_Bound.TempInValue2 = TempInValue2;

	TestDg.AddUFunction(Lambda_Bound, n"FakeLambda_Bound_Func");

	// ...
}

class UFakeLambda_Bound : UObjectPart
{
	UPROPERTY()
	bool bIsFakeLambda = true;

	int TempInValue1;
	FString TempInValue2;

	UFUNCTION()
	private void FakeLambda_Bound_Func(float32 Infloat) __generated
	{
		// do things
	}
}
```

Instead of a constructor, I assign captures directly, as in `Lambda_Bound.TempInValue1 = TempInValue1;`. It is shorter.

For readability, I have not matched line counts here. The real transformation should preserve them, otherwise IDE diagnostics point to the wrong lines.

`AddPart` associates a UObject’s lifetime with the caller and is a function I implemented myself. See [UE_Angelscript — Free your components and make features modular](practice-component-modularity.md), but some parts of that article are wrong, especially its explanation of Outer. You may also need What does Outer mean in UE? (Corrected, with a detailed demonstration). Neither article gives a stable solution for linking two UObjects’ lifetimes; you need to implement that yourself.

## Solve the problems one at a time

The two biggest traps were lifetime management, as mentioned above, and precise code mapping. `AddPart` needs careful design.

The other big trap is finding the right code and replacing it correctly. A regex that handles all the different cases can become long and complicated even while you are just getting the flow working.

Once the lifetime problem is solved, the other questions break down as follows.

- **When should the replacement happen?**

During preprocessing. Add a line to UE-Angelscript that performs the text replacement early in that phase. Look in its preprocessing class; if you are unsure where, see [UE_Angelscript — Source 2: how AS classes are bound to UE](internals-angelscript-classes-to-ue.md).

- **How do we find our lambda code?**

Follow how UE-Angelscript handles its other syntax sugar: use a **regular expression** to match the text to replace. We need formatting conventions. Lambda syntax is distinctive enough for a regex to match it well. A reserved function name can also make the location easy to identify.

I chose a reserved function name. That means AS comments should not casually contain that name, because it raises the chance of a false match. It rarely goes wrong; people do not normally put a full lambda expression in a comment for no reason.

- **After finding and parsing it, how should the mapping work?**

Generated class and function names should be unique. Start from the filename and add a sequence number. The owning class name could help, but that does not work for a global function, so the filename is a useful choice. The preprocessor already knows the filename; we just need to use it.

Define the naming rule carefully so it produces no duplicates. Make generated class names distinctive enough to avoid collisions with other code.

- **How do we debug errors in a generated class?**

Preserving line counts during replacement also avoids line mismatches in debugging. Adding a lambda halfway through a file should not make every later error point to the wrong line.

We plan to put the new class at the end of the file. Since it is not actually visible in the `.as` file, an error there gets reported at the last line.

Even if you receive a line number, you still have to understand it from the error message. A small lambda body is easy to recognize; a large one is not. If the body needs a lot of code, put that in a separate function and let the lambda forward to it. Even as a relay, it saves plenty of code.

Because the lambda body is actually at the end of the file and invisible, the IDE cannot set breakpoints in it. Another mapping scheme might make that possible, but I have not tried to implement one.

## A quick wrap-up

The flow finally works. Perhaps the IDE plugin could be changed to offer hints, but I cannot be bothered. Those hints do not help me much because I wrote the syntax sugar.

One small regret: capture types are not easy to infer automatically, so they must be stated explicitly. Preprocessing only replaces text; it has no complete type-inference mechanism.

Explicit capture types have pros and cons. They make it easy to capture globals from another file, but you have to write a type every time. Given the difficulty of inferring types at the syntax-sugar stage, explicit types will do.

The final callable form is:

```cpp
void Foo()
{
	// ...

	int TempInValue1 = 666;
    FString TempInValue2 = "World";
	FSomeTestDelegate TestDg;

	TestDg.AddFakeLambda([int TempInValue1, FString TempInValue2]
	(float32 Infloat)
	{
	  // do things
	}
	// ...
}
```

For single-cast delegates I could not use the different function name `BindFakeLambda`; this keeps naming aligned with UE C++’s single-cast and multicast binding functions.

# Final test code

The test type can contain different kinds of information in different positions. Deliberately break code to inspect IDE diagnostics, or try individual breakpoints.

```cpp
class ATestLambda : AActor
{
	FTestDelegate_OneParamReal TestDelegate;
	FTestMulticastDelegate_TwoParamsReal TestEvent;

	void TriggerLambda()
	{
		TestDelegate.ExecuteIfBound(666);
		TestEvent.Broadcast(2.f, 3.f);
	}

	void BindLambda()
	{
		FName TestName = n"Good";
		int TempInValue1 = 666;
		FString TempInValue2 = "World";

		TestDelegate.BindFakeLambda([int TempInValue1, FString TempInValue2, FName TestName](float32 Infloat) {
			Log(f"Hello {TempInValue2} -- {TestName} : Infloat {Infloat} : TempInValue1 {TempInValue1}");
		});

		TestEvent.AddFakeLambda([int TempInValue1, FString TempInValue2, FName TestName](float32 Infloat, float64 InDouble) {
			Log(f"Hello {TempInValue2} -- {TestName} : Infloat {Infloat} : InDouble {InDouble}: TempInValue1 {TempInValue1}");
		});
	}
}
```

Code that triggers the test:

```cpp
void Test_Lambda_InAS(FUnitTest& T)
{
	auto Actor = SpawnActor(ATestLambda);

	T.AssertTrue(!Actor.TestDelegate.IsBound());
	T.AssertTrue(!Actor.TestEvent.IsBound());

	Actor.BindLambda();

	T.AssertTrue(Actor.TestDelegate.IsBound());
	T.AssertTrue(Actor.TestEvent.IsBound());

	Actor.TriggerLambda();
}
```

The test passes and prints some logs.

# Summary

Many official UE-Angelscript scripting features are aimed at people with modest programming experience. Lambda support would add some learning overhead.

But for people used to lambdas, doing without them is uncomfortable. A long call chain with lots of callback functions gets rather tedious.

Every convenience has a price. Concise syntax costs learning and debugging effort. A simple syntax-sugar implementation means giving up some debugging convenience. My answer here is to put almost foolproof code inside the lambda — code that does not need breakpoints.

And so, where lambdas do not exist, we can imitate them.

Nobody can stop me using lambdas, except myself.
