---
title: "Nobody can stop me using pointers, except myself"
order: 20
category: essays
---
# Nobody can stop me using pointers, except myself

I finally got tired of living without generic pointers in UE-Angelscript. Binding APIs was especially annoying when the lack of pointers made an empty state hard to express.

Below is just some simple test code for the three smart pointers and raw pointers after binding them. The binding code is complicated and easy to get wrong, so I am not posting it. Blowing up my own code is fine; I can fix it. Blowing up somebody else’s is another matter.

The three smart pointers should not cause much trouble beyond a crash from forgetting a null check. Raw pointers can slip into undefined behavior, `UB`, with very little effort. But if they only receive C++ API results, with constructors disabled so AS code cannot create them everywhere, that is manageable.

- TSharedPtr

```cpp
{
	TSharedPtr<FTestSmartPtr> Pointer = FTestSmartPtr::MakeSharedPtr();
	auto& Ref = Pointer.Get();

	Ref.TestInt = 999;

	{
		// OpAssign
		TSharedPtr<FTestSmartPtr> Pointer2 = Pointer;
		auto& Ref2 = Pointer2.Get();

		Ref2.TestInt = 123;

		T.AssertTrue(Ref.TestInt == Ref2.TestInt);

		T.AssertTrue(Pointer.GetSharedReferenceCount() == 2);
		T.AssertTrue(Pointer2.GetSharedReferenceCount() == 2);

		T.AssertTrue(!Pointer2.IsUnique());

		T.AssertTrue(FDataPtr::Create(Ref) == FDataPtr::Create(Ref2));
	}

	// Destruct
	T.AssertTrue(Pointer.GetSharedReferenceCount() == 1);

	// Reset
	Pointer.Reset();
	T.AssertTrue(!Pointer.IsValid());
	T.AssertTrue(Pointer.GetSharedReferenceCount() == 0);
}
```

- TWeakPtr

```cpp
{
	TSharedPtr<FTestStructInAS> P;
	P.Emplace();
	P.Get().TestInt = 90;

	TWeakPtr<FTestStructInAS> W(P);
	T.AssertTrue(W.IsValid());
	auto P2 = W.Pin();
	T.AssertTrue(P2.GetSharedReferenceCount() == 2);

	W.Reset();
	T.AssertTrue(!W.IsValid());

	W = TWeakPtr<FTestStructInAS>(P);
	T.AssertTrue(W.Pin().GetSharedReferenceCount() == 3);
	T.AssertTrue(P.GetSharedReferenceCount() == 2);

	auto W2 = W;
	T.AssertTrue(W2.Pin().GetSharedReferenceCount() == 3);

	T.AssertTrue(W.Pin().Get().TestInt == 90);

	auto W3 = P.ToWeakPtr();
	T.AssertTrue(W3.IsValid());
	T.AssertTrue(W3.Pin().Get().TestInt == 90);
	T.AssertTrue(W == W3);

	TWeakPtr<FTestStructInAS> W4;
	T.AssertTrue(W != W4);
}
```

- TUniquePtr

```cpp
{
	TUniquePtr<FTestSmartPtr> UniquePtr;
	FTestSmartPtr::MakeUniquePtr(UniquePtr);

	T.AssertTrue(UniquePtr.IsValid());

	UniquePtr.Get().TestInt = 99;
	UniquePtr.Reset();
	T.AssertTrue(!UniquePtr.IsValid());

	UniquePtr.Emplace();
	T.AssertTrue(UniquePtr.IsValid());
	UniquePtr.Get().TestInt = 99;

	UniquePtr.Emplace();
	T.AssertTrue(UniquePtr.IsValid());
	T.AssertTrue(UniquePtr.Get().TestInt == 0);
	}
```

- TRawPtr

```cpp
{
	TRawPtr<FTestSmartPtr> RawPtr;
	T.AssertTrue(!RawPtr.IsValid());
	{
		RawPtr = FTestSmartPtr::MakeRawPtr();

		T.AssertTrue(RawPtr.IsValid());
		RawPtr.Get().TestInt = 9090;

		FTestSmartPtr::DeleteRawPtr(RawPtr);
		RawPtr.Reset();
	}
	T.AssertTrue(!RawPtr.IsValid());
 }
```

After all that tinkering, things finally feel comfortable. Nobody can stop me using pointers, unless I decide not to.
