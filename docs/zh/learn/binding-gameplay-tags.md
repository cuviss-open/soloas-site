---
title: "UE_Angelscript 绑定篇——解决方案：绑定 Native 和 DataTable 的 GameplayTags"
order: 56
category: binding
---
# UE_Angelscript 绑定篇——解决方案：绑定 Native 和 DataTable 的 GameplayTags

# GameplayTag 限制与解决方式

## 已知绑定的问题：不显示 DataTable 和 cpp 代码里的

UE-AS 5.4 版本，DataTable 和 cpp 代码里声明和定义的 GameplayTag 不能正常绑定，也不支持 GameFeature 里的 ini 。
UE-AS 5.4 版本，只支持了`Config/DefaultGameplayTags.ini` 以及 `Config/Tags` 中的所有标签。

示例：`Config/Tags` 里新建一个`.ini` 文件比如 `Test.ini`

```config
[/Script/GameplayTags.GameplayTagsList]
GameplayTagList=(Tag="DfTest.Test1",DevComment="")
GameplayTagList=(Tag="DfTest.Test2",DevComment="")
GameplayTagList=(Tag="DfTest.Test3",DevComment="")
GameplayTagList=(Tag="DfTest.Test4",DevComment="")
```

注意 ，GameplayTagList 前不要加`+`， 新建一个 ini 需要重新生成项目文件才能识别到。

## 已知交互的问题

**Editor 里添加 Tag 后，可以即时地给到 AS，但是删除的话，`GameplayTags::` 不能即时地反馈。**

## 解决绑定问题：让 AS 识别 cpp 里和 DataTable 里配置的 GameplayTag

修改之后，用 DataTable 就能实现实时交互了。
如果不重启 Editor，对于删除的 Tag ，AS 里的`GameplayTags::` 里还是会显示，但是此时已经不能使用，否则会报错或者获取不到，比如使用 `FGameplayTag::RequestGameplayTag(n"Test.DfContent.666",false) `就会返回 None 了

参考：
https://discord.com/channels/551756549962465299/551756549962465303/threads/1290243753852014633

修改绑定的代码：找到这个函数，然后注释掉之前的那些获取方式，接着使用 RequestAllGameplayTags 来获取。函数整体如下：

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

## 交互的问题？暂时没解决。

估计问题在于删除的时候没有刷新 AS。
这个问题影响不大，没事不会做删除 Tag 这种危险行为。

## 附加一个有用的技巧：GameplayTag 限定范围 Meta

注意是 Categories 而不是 Category。这和 cpp 的限制方式基本一致。

```cpp
UPROPERTY(Category = "Dialogue|Talking",Meta = (Categories = "UI.Layer"))
FGameplayTag UI_LayerName();
```

## UGameplayMessageSubsystem 尽量不要 cpp 和 AS 混用

UGameplayMessageSubsystem 大量的使用了 GameplayTag， 所以在这里提一下。

官方文档里提供了 [GameplayMessageRouter with Angelscript](https://github.com/IncantaUnreal/GameplayMessageRouter) 的绑定。其用法也比较简单，在 Readme 文件里可以看到，就不赘述。

使用的时候，可能会碰到一些问题，不能一个发送信息和接受信息的分别属于 cpp 和 AS, 可能产生报错。

# 总结

GameplayTags 很好用，建议一定要管理好，不然后续想改就比较麻烦，因为它渗透到了代码的各个地方。

另外，如果使用第三方软件来管理 GameplayTags，比如 Excel 等表格工具，那么拓展 UE 编辑器，让其支持 GameplayTags 的实时一键更新，就是工作流中的重要部分。


---
