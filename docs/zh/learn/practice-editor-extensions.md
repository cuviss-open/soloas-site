---
title: "UE_Angelscript 实践篇——拓展编辑器，就跟喝水一样简单"
order: 32
category: practice
---
# UE_Angelscript 实践篇——拓展编辑器，就跟喝水一样简单

有时候，想给 Editor 增加点小功能，但是 cpp 写起来很麻烦，反正除非必要，我是看着就不想写了。

那么批处理的东西怎么办，手动一个个来？是不可能的。

之前是用 python 脚本，或者用蓝图应对一下。这里只列举了蓝图和 python，也肯定有其他奇技淫巧，毕竟条条大路通罗马，就看走得累不累了。

# 原方式一，用蓝图

比如，我之前给 Assets 批量重命名，加前缀后缀什么的，蓝图里写了很多，写完之后，看着一团飞线，心想反正不改了，就这样吧。

![批量重命名资产的蓝图图表](../../assets/learn/original-fork/practice-editor-extensions-01.jpg)
![资产脚本操作右键菜单](../../assets/learn/original-fork/practice-editor-extensions-02.jpg)

# 原方式二，用 python

之前用 python 实现了批量增加资产，写起来挺方便的，还能让 AI 帮忙检查和修改，有些就直接让 AI 写，自己检查一下就好，但是用起来不是那么方便。

代码展示和使用展示。
![创建资产的Python脚本](../../assets/learn/original-fork/practice-editor-extensions-03.jpg)

![编辑器Python命令栏](../../assets/learn/original-fork/practice-editor-extensions-04.jpg)

用起来的话，先得放个 Python 文件夹在某个 Content 下，然后在控制台输入命令行。对于不是那么常用的功能还好了，如果是隔一阵就点击的，那么这种输入命令行的方式不是那么高效。

# 新方式：Angescript 的超简单交互方式

### Content Brower 里的资产处理

- 新建一个 .as 文件，以 `#if EDITOR` 和 `#endif` 包裹所有在 Editor 运行的内容。
  这个不用担心忘记，如果忘记了，编辑器会友情提醒你的，这个不得不说，很人性化。

- 声明一个类，继承自 `UScriptAssetMenuExtension`, 官方示例是这么写的：

```cpp
/**
 * Using UScriptAssetMenuExtension allows adding options to the context menu
 * of assets in the Content Browser.
 */
class UExampleAssetMenuExtension : UScriptAssetMenuExtension
{
	// These options should only show up for textures
	default SupportedClasses.Add(UTexture2D::StaticClass());

	// When clicked, will be called once for every selected texture asset
	UFUNCTION(CallInEditor, Category = "Example Texture Actions")
	void ExampleModifyTextureLODBias(FAssetData SelectedAsset, int LODBias = 0)
	{
		UTexture2D SelectedTexture = Cast<UTexture2D>(SelectedAsset.GetSoftObjectPath().TryLoad());
		SelectedTexture.Modify();
		SelectedTexture.LODBias = LODBias;
	}
};
```

其中，`UExampleAssetMenuExtension` 这里随意了，不影响 Editor 里的显示。`default` 语句，是你要处理的资产，示例里处理的是贴图。如果要处理大部分资产怎么办，那就改为 `default SupportedClasses.Add(UObject::StaticClass());` 。

接着，每一个函数，都是一个对资产的操作，Category 是将这些操作打包，比如，我用 RenameActions 打包了一批函数，如下：

![资产重命名扩展代码](../../assets/learn/original-fork/practice-editor-extensions-05.jpg)
![资产重命名操作菜单](../../assets/learn/original-fork/practice-editor-extensions-06.jpg)

需要注意的是，这些函数里如果带有参数，点击这些命令，会弹出对话框，让你输入参数的。即使写上了参数的默认值，仍然会弹出对话框。

## Level 的 Outliner(大纲)的 Actor 处理

这跟 Content Brower 里差不多，只是继承的类不同罢了，这个地方的功能需要继承自`UScriptActorMenuExtension` ,名称里显而易见，处理的就是 Actor，而关卡里能放的就是 Actor。
值得提的一点是，官方在这里示例了，写了如何使用自定义图标：

```cpp
UCLASS(Abstract) // Remove this line to make the extension Enabled
class UExampleActorMenuExtension : UScriptActorMenuExtension
{
	// Specify one or more classes for which the menu options show
	default SupportedClasses.Add(AActor::StaticClass());

	// Every function with the CallInEditor specifier will become a context menu option
	UFUNCTION(CallInEditor)
	void ExampleActorMenuExtension()
	{
	}

	// The function's Category will be used to create sub-menus
	UFUNCTION(CallInEditor, Category = "Example Category")
	void ExampleOptionInSubCategory()
	{
	}

	// Custom icons can be specified with the `EditorIcon` meta tag:
	UFUNCTION(CallInEditor, Category = "Example Category", Meta = (EditorIcon = "Icons.Link"))
	void ExampleOptionWithIcon()
	{
	}
```

可以看到，是通过 Meta 来表示的，这里用的是 UE 自带的图标。如果是自定义的图标，怎么添加，我暂时用不到，读者自行研究了。

## 增加菜单栏或工具栏按钮

菜单栏，是最上面的一栏，工具栏，是标签下方的一栏。
如果想要很多折叠的功能，就添加到菜单栏里，如果经常用的功能，就放在工具栏里。
如图，我就放了一个更新 GameplayTags 的按钮，用来在编辑器外更新了相关的.ini 文件后，主动更新 GameplayTags。
![标签更新按钮](../../assets/learn/original-fork/practice-editor-extensions-07.jpg)

因为菜单栏和工具栏都放在了同一个类里，所以写法有点不同，详情如下。

### 菜单栏（MainMenu）

```cpp
/**
 * Other editor menus can be extended with UScriptEditorMenuExtension.
 */
UCLASS(Abstract) // Remove this line to make the extension Enabled
class UExampleEditorMenuExtension : UScriptEditorMenuExtension
{
	// This is the same extension point used by UToolMenus::ExtendMenu
	// In this example, we extend the top menu of the main window:
	default ExtensionPoint = n"MainFrame.MainMenu";

	UFUNCTION(CallInEditor, Category = "My Example Menu")
	void ExampleMainMenuOption()
	{
	}

	UFUNCTION(CallInEditor, Category = "My Example Menu | Example Sub Menu")
	void ExampleSubMenuOption()
	{
	}
};
```

`ExtensionPoint` 这句是固定的，指名道姓地要添加到菜单栏（MainMenu）里。Category 就是显示在菜单栏里的名称，支持子名称，写法就是加一下`|`分隔符。

### 工具栏（LevelEditorToolBar）

这里的`ExtensionPoint` 也是固定的，明白写出要加到`LevelEditorToolBar`。

在这里，就会有个疑问，是不是还有其他的`ExtensionPoint` 可以写？如果有，官方示例为什么不展示出来？我没有深入研究这部分的实现代码，不过转念一想，有很大的必要增加其他的吗，目前的这些够用了吗？答曰：够用了。

# Angelscript 拓展编辑器功能的优势总结

（注：不是说其他方式不好，而是从使用方便的角度考虑，cpp 大佬、蓝图大佬和 python 大佬或许有调用方便的用法，毕竟能成为大佬，手里有两把刷子是肯定的。）

## 优势

- 迭代速度飞快。跟蓝图几乎一样的迭代速度，ctrl s 就可以测试了。
- 调用方式简单。跟原生的按钮差不多的体验，无需到命令行里输入。
- 拓展写法轻松。只需要继承类，写一个 default 语句，然后就开始写方法了。
- 防呆设计合理。如果你忘记了将这些类包裹进#if 语句中，会教人好好学习的。
- 文本格式 YES。 这涉及到版本控制之类的内容，以及一个基本的认知——文本能承载的信息量远大于可视化节点编程。

## 劣势

- 只能在 AS 的 UE 版本里使用。而且这是一个分支版本，不是简单装个插件就能用的，脚本官方会提供有大版本的二进制包，而不是每个小版本都提供，比如 UE 5.4 只有一个 UE 5.4.2。
- 没有 cpp 的万能。有些模块还是会调用 cpp 的函数，比如我写一个更新 ini 文件加载的功能，AS 里没有，就只能在 cpp 了写好了。
- 没有蓝图的和蔼可亲。总得需要更多一些编程知识的。

# 彩蛋：Editor --> Angescript --> cpp --> .bat

最后给个不错的彩蛋——如何在 Editor 里一键调用 .bat 文件。从此打通任督二脉，一批古早的 .bat 可以再次飞翔。

在 cpp 里写一个函数，调用 windows 的 cmd 命令来运行.bat 文件，暴露给 AS 或者蓝图使用。

结合 Editor 的拓展，就可以实现在编辑器里点击一下，就运行.bat 文件。

为什么要这么做？因为积累了一些精心打造的.bat 文件，让它们继续发光发热嘛。比如 Update GameplayTags 的小功能，就是用.bat 将 xls 表格转为 ini 文件，然后再读取到 UE 的，以下的桥梁函数功不可没。

```cpp
/// .h 文件

/** 静态方法，用于在蓝图中执行 .bat 文件, 需要输入绝对路径，路径需要用 / 。  
 * bat 文件最后加上 timeout /t 1 /nobreak >nul 或用 ping 方式来稍微延迟一下，  
 * 来让这个进程读取 cmd 窗口输出的内容过去,  不要写 pause 。  
 * Bat 文件不要从普通用户跳转为管理员，这样的话算是运行完成了，就不会阻塞当前进程来获取输出  
 **/
 **/UFUNCTION(BlueprintCallable, Category = "Utilities")
static void RunBatchFile(const FString& BatchFilePath);

/// .cpp 文件
void UExampleEditorFunctionLibrary::RunBatchFile(const FString& BatchFilePath)
{
	// 检查文件是否存在
	if (!FPaths::FileExists(BatchFilePath))
	{
		UE_LOG(LogTemp, Error, TEXT("Batch file does not exist: %s"), *BatchFilePath);
		return;
	}

	// 设置工作目录（使用批处理文件的目录）
	FString WorkingDirectory = FPaths::GetPath(BatchFilePath);

	// 为批处理文件添加 cmd /c 前缀（确保正确执行批处理命令）
	FString CommandLine = FString::Printf(TEXT("/c \"%s\""), *BatchFilePath);

	// 创建管道
	void* ReadPipe = nullptr;
	void* WritePipe = nullptr;
	if (!FPlatformProcess::CreatePipe(ReadPipe, WritePipe))
	{
		UE_LOG(LogTemp, Error, TEXT("Failed to create pipes."));
		return;
	}

	// 启动进程
	FProcHandle ProcHandle = FPlatformProcess::CreateProc(
		TEXT("cmd.exe"), // 使用 cmd.exe 运行批处理文件
		*CommandLine, // 命令行参数
		false, // 是否允许进程在后台运行
		true, // 是否阻塞
		false, // 是否允许进程继承父进程的环境变量
		nullptr, // 输出句柄
		0, // 环境变量设置（默认使用父进程）
		*WorkingDirectory, // 工作目录
		WritePipe // 将输出连接到管道
	);

	if (!ProcHandle.IsValid())
	{
		UE_LOG(LogTemp, Error, TEXT("Failed to launch batch file: %s"), *BatchFilePath);
		FPlatformProcess::ClosePipe(ReadPipe, WritePipe);
		return;
	}

	UE_LOG(LogTemp, Log, TEXT("Successfully launched the batch file: %s"), *BatchFilePath);

	// 读取子进程输出
	// bat 文件最后加上 timeout /t 1 /nobreak >nul 或用 ping 方式来稍微延迟一下，
	// 来让这个进程读取 cmd 窗口输出的内容过去, 不要写 pause
	UE_LOG(LogTemp, Log, TEXT("\n "));
	UE_LOG(LogTemp, Log, TEXT("\n****** The Log from Batch File start *****\n"));
	FString Output;
	while (FPlatformProcess::IsProcRunning(ProcHandle))
	{
		Output = FPlatformProcess::ReadPipe(ReadPipe);
		if (!Output.IsEmpty())
		{
			UE_LOG(LogTemp, Log, TEXT("%s"), *Output);
		}

		FPlatformProcess::Sleep(0.05f); // 每次循环时暂停一会，减少 CPU 使用率
	}
	UE_LOG(LogTemp, Log, TEXT("\n****** The Log from Batch File End *****\n"));
	UE_LOG(LogTemp, Log, TEXT("\n "));

	// 清理资源
	FPlatformProcess::ClosePipe(ReadPipe, WritePipe);
	FPlatformProcess::CloseProc(ProcHandle);

	UE_LOG(LogTemp, Log, TEXT("Batch file execution completed: %s"), *BatchFilePath);
}
```

注：这个函数在我这里运行没问题，凡是涉及代码的，读者仍需自行测试，切勿照猫画虎。

#  总结，天降 UE-AS，拓展编辑器，就跟喝水一样简单。

有对比才有伤害，天下苦编辑器拓展久矣！如果你尝试或者看看怎么用 cpp 拓展，就知道了

前提是，你得读一下文档，这不会比熟练使用蓝图难多少，毕竟，这脚本语言的维护出发点就是给设计师与工程师一起使用的。（目前连 lambda 都没有，因为考虑到设计师可能难以理解。）
