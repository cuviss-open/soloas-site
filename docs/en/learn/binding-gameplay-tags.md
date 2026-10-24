---
title: "UE_Angelscript — Binding native and DataTable GameplayTags"
order: 56
category: binding
---
# UE_Angelscript — Binding native and DataTable GameplayTags

# GameplayTag limitations and solutions

## Known binding issue: DataTable and cpp tags do not appear

UE-AS 5.4 cannot properly bind GameplayTags declared and defined in DataTables or cpp, and does not support GameFeature ini files either.
UE-AS 5.4 only supports tags in `Config/DefaultGameplayTags.ini` and under `Config/Tags`.

For example, create an `.ini` file such as `Test.ini` in `Config/Tags`:

```config
[/Script/GameplayTags.GameplayTagsList]
GameplayTagList=(Tag="DfTest.Test1",DevComment="")
GameplayTagList=(Tag="DfTest.Test2",DevComment="")
GameplayTagList=(Tag="DfTest.Test3",DevComment="")
GameplayTagList=(Tag="DfTest.Test4",DevComment="")
```

Do not add `+` before GameplayTagList. Regenerate project files after adding an ini so it is recognized.

## Known interaction issue

**Adding a Tag in the Editor updates AS immediately, but deletion is not reflected immediately in `GameplayTags::`.**

## Fixing binding: make AS recognize cpp and DataTable GameplayTags

After this change, DataTables allow live interaction.
Without restarting the Editor, a deleted Tag still appears under `GameplayTags::`, but cannot be used. It will fail or return nothing; for example, `FGameplayTag::RequestGameplayTag(n"Test.DfContent.666",false)` returns None.

Reference:
https://discord.com/channels/551756549962465299/551756549962465303/threads/1290243753852014633

Find this binding function, comment out its previous collection paths, and use RequestAllGameplayTags instead. Here is the whole function:

```cpp
bool Bind_AddNewGameplayTags()
{
	bool Result = false;
	// TArray<const FGameplayTagSource*> Sources;
	// UGameplayTagsManager::Get().FindTagSourcesWithType(EGameplayTagSourceType::Native, Sources);
	// UGameplayTagsManager::Get().FindTagSourcesWithType(EGameplayTagSourceType::DefaultTagList, Sources);
	// UGameplayTagsManager::Get().FindTagSourcesWithType(EGameplayTagSourceType::TagList, Sources);
	// UGameplayTagsManager::Get().FindTagSourcesWithType(EGameplayTagSourceType::RestrictedTagList, Sources);
	// UGameplayTagsManager::Get().FindTagSourcesWithType(EGameplayTagSourceType::DataTable, Sources);
	//
	// for (const FGameplayTagSource* Source : Sources)
	// {
	// 	if (Source->SourceTagList != nullptr)
	// 	{
	// 		for (const auto& RowTag : Source->SourceTagList->GameplayTagList)
	// 		{
	// 			Result |= Bind_ProcessGameplayTag(RowTag.Tag);
	// 		}
	// 	}
	//
	// 	if (Source->SourceRestrictedTagList != nullptr)
	// 	{
	// 		for (const auto& RowTag : Source->SourceRestrictedTagList->RestrictedGameplayTagList)
	// 		{
	// 			Result |= Bind_ProcessGameplayTag(RowTag.Tag);
	// 		}
	// 	}
	// }

	// tdxh -- try to fix Problem: If a native game tag is defined with UE_DEFINE_GAMEPLAY_TAG in a game module, it won't appear in GameplayTags:: in AS.
	FGameplayTagContainer Tags;
	UGameplayTagsManager::Get().RequestAllGameplayTags(Tags, false);
	for (const FGameplayTag& Tag : Tags)
	{
		Result |= Bind_ProcessGameplayTag(Tag.GetTagName());
	}

	return Result;
}
```

## The interaction issue? Not solved yet.

I suspect AS is not refreshed on deletion.
It is not a big issue. Deleting Tags is dangerous and not something to do casually anyway.

## Another useful trick: GameplayTag range metadata

It is Categories, not Category. This is much like the cpp restriction.

```cpp
UPROPERTY(Category = "Dialogue|Talking",Meta = (Categories = "UI.Layer"))
FGameplayTag UI_LayerName();
```

## Try not to mix cpp and AS with UGameplayMessageSubsystem

UGameplayMessageSubsystem uses GameplayTags extensively, so I will mention it here.

The official documentation supplies the [GameplayMessageRouter with Angelscript](https://github.com/IncantaUnreal/GameplayMessageRouter) binding. Usage is simple and explained in the Readme, so I will not repeat it.

You may hit problems if the sender and receiver are split between cpp and AS; that can produce errors.

# Summary

GameplayTags are useful. Manage them carefully: later changes are awkward because they spread throughout the code.

If a third-party tool such as Excel manages your GameplayTags, extending the UE editor with one-click live updates becomes an important part of the workflow.

---
