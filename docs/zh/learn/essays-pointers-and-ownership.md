---
title: "杂谈：没有人能拦我用指针，除了我自己"
order: 20
category: essays
---
# 杂谈：没有人能拦我用指针，除了我自己

终究还是受不了 UE-Angelscript 没有通用指针的日子，特别是 API 绑定的时候，遇到指针缺失带来的空状态难以表达的问题。

以下仅记录将三大智能指针和裸指针绑定好的简单测试代码，绑定代码复杂且易错，不贴（炸了我的代码可以，我自己能修，但是炸了别人的，可不好）。

三大智能指针不会有什么问题，顶多是指针没判空造成崩溃。但是裸指针稍不注意，就可能产生未定义行为`UB`，不过如果只是用来承接 CPP 的 API，并且禁用构造函数，不让在 AS 代码里到处用，那倒是可控。

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

一顿操作猛如虎，算是舒服了，没有人能阻挡我用指针，除非我不想用。
