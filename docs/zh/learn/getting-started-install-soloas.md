---
title: "UE_Angelscript 入门篇--安装引擎，打开封印之门"
order: 10
category: getting-started
---
# UE_Angelscript 入门篇--安装引擎，打开封印之门

- 苍老的声音：勇士，前面是封印的门，你要打开？
- 坚定的声音：若不打开，我为何而来？
- 画外音：”世之奇伟、瑰怪，非常之观，常在于险远，而人之所罕至焉，故非有志者不能至也。“

# 前言

使用 UE - Angelscript 建议使用自行编译的版本，以下是笔者的一些经验总结，偏小白向。

本文默认读者已经掌握了以下的内容，不过，如果不知道，用到了再学，也不是不行，UE 的官方文档写得很详细，另外还可以问各种 AI。

基础知识：了解 UE C++ 的基础、 Git 的基本操作、基础的网络访问能力、 基础的命令行操作。
硬件配置：不太差的电脑，不然编译会比较慢。

如果只是想体验一下，可以考虑直接下载编译好的版本：
https://github.com/Hazelight/UnrealEngine-Angelscript

直接在 release 里下载编译好的版本。不是每个小版本都有编译好的，比如 UE 5.4 就只有 UE 5.4.2。

对于不是那么经常升级引擎以及修改引擎的，其实也可以用了。而对于想追求最新的、或者体验编译流程的、或者有考虑修改源码的，建议还是自行编译。

# 电脑运行环境配置

## 环境配置查看

先看 UE 对应的版本要求，每一个版本都可能有特定的要求，如果不按照这个来，有比较大的概率遇到编译问题，比如以下链接是 5.4 版本的要求。

https://dev.epicgames.com/documentation/en-us/unreal-engine/unreal-engine-5.4-release-notes#developeriteration


![UE 5.4 Windows、Linux 和 macOS 开发环境要求](../../assets/learn/unreal-engine-54-build-requirements.jpeg)

```
Windows
    Visual Studio 2022 v17.4 or newer
    Windows SDK 10.0.18362 or newer
    LLVM clang
        Minimum: 15.0.0
        Preferred: 16.0.6
    .NET 4.6.2 Targeting Pack
    .NET 6.0

IDE Version the Build farm compiles against
    Visual Studio: Visual Studio 2022 17.8 14.38.33130 toolchain and Windows 10 SDK (10.0.18362.0)
    Xcode: Xcode 14.2

GDK
    Minimum Windows SDK: 10.0.19041.0
    GDK: October 2023 Update 3
    Latest recovery version
    Supported IDE: Visual Studio 2022
```

## 电脑系统 （编译环境的基础）

这个版本推荐的是 Win10 。
如果是 Win11，可以尝试，但是可能得自己解决遇到的问题。

## SDK（可独立安装）

一定注意，要稳妥就不要随意用最新的版本，不然可能出现各种编译问题（当然也可能不会出现）。
根据上方的截图，UE5.4 版本，用 18362 或者 19041 都可以，我使用比较新的 19041。

SDK 可以在控制面板里`Control Panel\All Control Panel Items\Programs and Features` 找到 **Windows Software Development Kit** ，然后可以看到版本，卸载没有用的。安装合适的，这里安装 19041 。

SDK 默认安装在 `C:\Program Files (x86)\Windows Kits`
https://developer.microsoft.com/en-us/windows/downloads/sdk-archive/

这个内容，也能在 Visual Studio 里安装，这里提供了独立的安装方式。

## LLVM clang（可独立安装）

通过命令行 `clang --version` 查看。

```
(base) PS C:\Users\YourHome> clang --version
(built by Brecht Sanders, r5) clang version 17.0.6
Target: x86_64-w64-windows-gnu
Thread model: posix
InstalledDir: D:/DEVELO~1/mingw64/bin
```

这个影响没那么大。

安装来源是：# WinLibs standalone build of GCC and MinGW-w64 for Windows
https://winlibs.com/

这个内容，也能在 Visual Studio 里安装，这里提供了独立的安装方式。

## .NET（可独立安装）

控制面板里 `Control Panel\All Control Panel Items\Programs and Features` 里可以找到。

.NET 4.6.2 Targeting Pack
https://dotnet.microsoft.com/zh-cn/download/dotnet-framework

.NET 6.0

https://dotnet.microsoft.com/en-us/download/dotnet/6.0

## Visual Studio （整体开发环境）

Visual Studio 2022 17.8 14.38.33130 toolchain
注意不要随意更新，不然回退麻烦。
里面选择 SDK 同独立的。

需要先卸载 visual studio ，然后选择特定版本的 visual studio
https://learn.microsoft.com/en-us/visualstudio/releases/2022/release-notes-v17.8
上面的网址下载不到特定的社区版

需要用以下命令来下载特定的版本（注意保持网络访问足够通畅）。

```bash
# 这是展示所有版本的命令：
winget show --versions "Microsoft.VisualStudio.2022.Community"

# 此处以 17.9.1 版本为例，输入（注意把里面的 _17.9.1_ 替换成您实际需要安装的版本）：

winget install -v 17.9.1 "Microsoft.VisualStudio.2022.Community"

# （安装过程中，可能会弹出提示 Do you agree to all the source agreement terms? [Y] Yes [N] No:

# 如果弹出了以上提示，输入 **y**，按下回车运行。）
```

我这安装这个版本：

```bash
winget install -v 17.8.6 "Microsoft.VisualStudio.2022.Community"
```

一会之后，终端里会得到一个网址：
https://download.visualstudio.microsoft.com/download/pr/5bebe58c-9308-4a5b-9696-b6f84e90a32e/f125ea2f51f323f78d612b08a77134ce9f94e7a0c6e43041a1d13804651dc27e/vs_Community.exe

这个就是特定版本 17.8.6 的 exe 安装文件！如果只是想要 17.8.6 的，直接用上面的链接也行。

下载了专用版本的 Installer 后，用这个来修改配置的包。

![Visual Studio Installer 中的 C++ 工作负载和组件选择](../../assets/learn/visual-studio-installer-workloads.jpeg)

去掉 win11 SDK，修改 win 10 SDK 为合适版本 ，

增加 .Net 6 运行时 和 .Net Framework 4.62 目标包。

勾选 Unreal Engine 测试适配器

生成工具选择： `MSVC 143 - VS 2022 C++ x64/x86 生成工具（v14.38-17.8)` 。（这里如果不选择，后续编译的时候，Visual Studio 也会提示的。

安装步骤需要更详细的话，参考 UE 官方文档。
https://dev.epicgames.com/documentation/zh-cn/unreal-engine/setting-up-visual-studio-development-environment-for-cplusplus-projects-in-unreal-engine?application_version=5.4

MSVC 工具链安装好后，在以下文件夹，将它们加入系统的 path 。

```
C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Tools\MSVC\14.38.33130

C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Tools\MSVC\14.38.33130\bin\Hostx64\x64
```

打开后，如果之前没配置，可能显示需要额外的组件，`MSVC 143 - VS 2022 C++ x64/x86 生成工具（v14.38-17.8)`，安装就是了。可能是 VC 工具的补丁？反正不管了，提示了需要这个，安装即可。

## 配置编译的设置 （可选，不要随意调）

以下文件，注意替换用户名。
`C:\Users\YourHome\AppData\Roaming\Unreal Engine\UnrealBuildTool\BuildConfiguration.xml ` 是编译的配置文件，可以自定义很多编译选项，如果不想理会，不用配置这个，系统会给一些默认值的。

类似的，F:\A_UE\UnrealEngine_Angelscript_55\Engine\Saved\UnrealBuildTool 也有这个文件。

这是我针对 AMD 5900X 和 64G 内存和 VS 2022 ，做的配置。其中 PCH 还是太高了，后续我会考虑调低的。 每个参数如果有不懂的，把这些配置复制给 AI，AI 会讲清楚的，当然也不能完全相信 AI 的建议，因为 AI 可能会给一些老的配置推荐。

```xml
<?xml version="1.0" encoding="utf-8" ?>
<Configuration xmlns="https://www.unrealengine.com/BuildConfiguration">
    <WindowsPlatform>
        <!-- 提高PCH内存分配，适配大规模源码 -->
        <PCHMemoryAllocationFactor>600</PCHMemoryAllocationFactor>
    </WindowsPlatform>
    <ParallelExecutor>
        <!-- 并行编译设置 -->
        <ProcessorCountMultiplier>1</ProcessorCountMultiplier>
        <MaxProcessorCount>24</MaxProcessorCount>
    </ParallelExecutor>
    <BuildConfiguration>
        <!-- 启用XGE或禁用，取决于分布式编译是否可用 -->
        <bAllowXGE>false</bAllowXGE>
        <!-- 最大并行编译任务数 -->
        <MaxParallelActions>24</MaxParallelActions>
        <!-- 禁用Unity Build以提升增量编译性能(不经常修改引擎，就开启） -->
        <bUseUnityBuild>true</bUseUnityBuild>
        <!-- 启用PCH支持 -->
        <bUsePCHFiles>true</bUsePCHFiles>
    </BuildConfiguration>
</Configuration>
```

AMD 5900X 没开超频，全量编译 UE 5.4 ，耗时约 42 分钟。

注意，PCHMemoryAllocationFactor 这个值修改会让引擎重新生成 PCH （预编译头） ，相当于触发了部分内容的重新编译。所以，这个定了后，后面就不要随意改动这个数了，触发引擎的重新编译又会是漫长的等待。

网上说法是PCHMemoryAllocationFactor 默认是750。 而我设置 1000 会经常报错。

# 自编译 Unreal Engine 的步骤

### 编译流程：

### 拉取仓库

注意，建议在准备装编译版的地方，预留 256 G 硬盘空间，而且建议是要在 SSD 硬盘上。

可以考虑 Fork 一份 angelscript-master 分支，如果没有 Fork，就直接用 Angelscript 的。
拉取仓库：

```bash
git clone https://github.com/Hazelight/UnrealEngine-Angelscript.git
```

拉取到本地需要一些时间，我用对应需要的 tag 新建了一个分支 v5.4 的分支：

```bash
git checkout -b angelscript-v5.4 tags/angelscript-5.4-last
```

`angelscript-5.4-last` 这个 tag 对应是其实是 5.4.4 版本。

### 更新依赖

Setup.bat 更新依赖
生成项目文件：GenerateProjectFiles.bat
没问题的输出如下：

```
F:\A_UE\UnrealEngine_Angelscript>F:\A_UE\UnrealEngine_Angelscript\Setup.bat
Checking dependencies...
Registering git hooks...
Installing prerequisites...

F:\A_UE\UnrealEngine_Angelscript>F:\A_UE\UnrealEngine_Angelscript\GenerateProjectFiles.bat
Setting up Unreal Engine project files...
Using bundled DotNet SDK version: 6.0.302
Log file: F:\A_UE\UnrealEngine_Angelscript\Engine\Programs\UnrealBuildTool\Log_GPF.txt

Some Platforms were skipped due to invalid SDK setup: Android, Linux, LinuxArm64.
See the log file for detailed information


Generating VisualStudio project files:
Binding IntelliSense data... 100%
Writing project files...
Forcing LEGACY XCODE because host OS is not Mac
Writing project files... 100%

Generating QueryTargets data for editor...
Total execution time: 7.13 seconds
```

### 开始编译

点击 UE5.sln 在 VisualStudio 打开，
将解决方案配置设置为 **开发编辑器（Development Editor）**。
将解决方案平台设置为 **Win64**。
右键单击 UE 目标并选择 **构建（Build）**。


![Visual Studio 中选择 Development Editor 和 Win64 配置](../../assets/learn/visual-studio-build-configuration.jpeg)

### 运行编辑器

编译完成后，接下来就是运行编译器了。

将启动项目设置为 **UE5**

**右键单击** **UE** 项目，**将鼠标悬停于** Debug **上，然后单击** 启动新实例（Start New Instance）\*\* 以启动编辑器。（或者按 F5)


![在 Visual Studio 中启动 Unreal Editor 新实例](../../assets/learn/visual-studio-launch-editor.jpeg)

如果一切顺利，应该就正常打开了 UE 的 Editor，如果 UE 的官方版本一样，该怎么使用就怎么使用，只是除了不能直接和 Epic Game Launcher 联动了，插件什么的，得自己编译使用。不过，既然我们都能编译引擎，区区插件而已，不在话下。

# 编译完成后的配置

## 引擎的启动文件在哪

可以考虑通过脚本启动。不过，一般都是启动项目，而不是专门去启动引擎。

```bash
@echo off

cd /d %~dp0

start .\UnrealEngine_Angelscript\Engine\Binaries\Win64\UnrealEditor.exe

pause
```

也可以通过将这个文件设置为快捷方式，放到桌面或者固定在工具栏。

## 第三方插件的安装

安装到引擎的目录下(没有这个目录就新建即可)
~\Engine\Plugins\Marketplace
如果是开发相关的,比如 RiderLink,安装再其中的 Developer 下
~\Engine\Plugins\Marketplace\Developer

## 代码编辑器的选择与配置

### VSCode

- VSCode 是必须的，是写 UE - Angelscript 代码的编辑器。

按照 UE - Angelscript 的官方文档，装上对应的插件 `Unreal Angelscript` 和 `Unreal AngelScript Clang-Format`，之后就可以愉快地探索了。

关于 VSCode 的调试，按 F5 开始调试模式，在 Editor 里运行，可以像蓝图一样通过断点来一步步调试了。

VSCode 开源免费，自由拓展，但是 UE 项目过于庞大，放进 VSCode 里太卡，一般不会这么做（虽然官方也提供了一些支持，但是配置麻烦、重要的是跳转很卡）。

不过 VSCode 用来写脚本，就非常非常地合适了。 UE - Angelscript 的插件做了 UE Editor 和 VSCode 之间的桥梁，反应迅速，只要不是巨量的重构，都是即点即开，开发体验上没有停顿。（此处对比的是 cpp 在的热编译。）

### Visual Studio

- Visual Studio 一般也是必须的，它用来配置运行环境很方便。社区版的功能足够，目前也针对 UE 有了不少优化。即使如此有不少小问题，但它是可以商用的（有限制条件）。

首次编译引擎，都用 Visual Studio 吗？按照官方文档，就是用这个来的，这个学习成本和设置比较简单一些，而且有社区版，大家都可以尝试。

以下是一些可选的 VS 相关的一些插件和配置

#### 调出 UE 集成配置

工具-选项-unrealengine-配置页-在启动时显示-true
这个会调出 UE 集成配置。

#### vc-ue-extensions

https://github.com/microsoft/vc-ue-extensions
前提是 vs installer 里安装了 Visual Studio Tools for Unreal Engine
将插件的代码拉取到引擎的 plugins 的 Marketplace 目录（没有就创建）

```
cd F:\A_UE\UnrealEngine_Angelscript\Engine\Plugins\Marketplace
git clone https://github.com/microsoft/vc-ue-extensions
```

然后在 VS 里编译 UE5 就可以了。

( 如果安装 Resharper c++ 了，可以考虑关掉蓝图分析，VS 本身的蓝图分析并不准确)

#### 命名约定检查器

项目根目录下配置
然后可以在项目目录下生成 .editorconfig
文件从 vc-ue-extensions 插件拷贝即可。
https://raw.githubusercontent.com/microsoft/vc-ue-extensions/main/Source/.editorconfig

#### HLSL 支持:

https://marketplace.visualstudio.com/items?itemName=TimGJones.HLSLToolsforVisualStudio
然后可以在项目目录下生成 shadertoolsconfig.json

#### UnrealVS

安装文件位置：
`<UNREAL_ENGINE_ROOT>\Engine\Extras\UnrealVS\VS_VERSION\UnrealVS.vsix`
安装和使用方式
https://dev.epicgames.com/documentation/zh-cn/unreal-engine/using-the-unrealvs-extension-for-unreal-engine-cplusplus-projects

#### Favorite Documents

在扩展 - 管理拓展里添加。也可以下载后，关闭 VS，双击安装。
https://marketplace.visualstudio.com/items?itemName=SergeyVlasov.FavoriteDocuments

#### 其他

CodeMaid.VS2022 、 Resharper c++ （非免费）、VSCode Theme Converte

### Rider

- Rider 可以考虑使用，针对 UE 进行了非常多的优化，比 Visual Studio 好很多，但是需要比较大的电脑内存才可以起飞，目前，个人版可以学习研究使用，个人版不可商用。

项目在进行编译的时候是不是可以用 Rider？经过测试，是可以的。

Rider 里就没有那么多自由安装的插件了，不过 UE 开发中，该有的功能大都有，有些做得相当的好。如果电脑配置足够，支持得了商业版本，是非常不错的选择。

如果用 Rider，可以这么操作，引擎的编译一开始用 VS ，后续不管什么编译都用 Rider，cpp 代码也都用 Rider 写，Angelscript 用 vscode 写。

# 注意事项

## 如何防止修改到引擎源码

用脚本将~\Engine\Source\Runtime 的`'.h', '.hpp', '.c', '.cpp', '.cs'`设置为只读，如果需要做 Editor 的扩展，Source\Editor 也处理一下。

根据前人的经验教训，有这么一条铁律，请注意：
**永远记得，在源码版虚幻引擎的解决方案中，不要使用 Visual Studio 的【清理】和【重新生成】功能！**

有些人可能会想着能不能编译一个二进制版本的，按照官方版本，是可以的，不过这又是另外一个坑，配置起来不简单。如有兴趣，自行尝试，以下是一些相关链接：

官方文档：
https://dev.epicgames.com/documentation/en-us/unreal-engine/installed-build-reference-guide-for-unreal-engine

需要装了 Windows 10 SDK ，Windows Debugging Tools 记得勾选：
https://developer.microsoft.com/en-us/windows/downloads/sdk-archive/

环境 SDK 配置要找到对应版本：
https://dev.epicgames.com/documentation/en-us/unreal-engine/unreal-engine-5.4-release-notes#developeriteration

相关的重要代码

```bash
.\Engine\Build\BatchFiles\RunUAT.bat BuildGraph -target="Make Installed Build Win64" -script="Engine/Build/InstalledEngineBuild.xml" -clean

.\Engine\Build\BatchFiles\RunUAT.bat BuildGraph -script=Engine/Build/InstalledEngineBuild.xml -target="Make Installed Build Win64" -nosign -set:GameConfigurations=Development;Shipping -set:WithWin64=true -set:WithAndroid=false -set:WithDDC=true -set:WithLinux=false -set:WithLinuxArm64=false -set:WithIOS=false -set:WithTVOS=false -set:WithMac=false -clean

```

另外，网上有个办法，让引擎自动识别自己为安装版本，不过经过我的实测，不那么好用，如果后续改回来，可能会触发引擎的全量编译。
不过还是将这个方法放这里了，说不准以后有用：
文件夹`~\Engine\Build`下的 SourceDistribution.txt 改为 InstalledBuild.txt 。
InstalledBuild.txt 可以写上版本 AS_5.4 （好像没什么用）。

改好之后，右键点击项目文件，切换版本的时候，会提示为 `Binary build at (路径)`。
## 源码版本的项目清理步骤

针对虚幻引擎源码版，项目级别的清理步骤：

（1）删除项目根目录中：**Binaries**、**Build**、**DerivedDataCache** 和 **Intermediate** 文件夹，以及 **sln** 文件。

2）通过 .uproject 重新生成 Visual Studio 项目文件，此步骤会重新生成 **sln** 文件 和 **Intermediate** 文件夹。

（3）打开 sln 项目解决方案，将自建项目【设为启动项目】，并构建项目（特别注意不能重新构建项目），会重新生成 **Binaries** 和 **Build** 文件夹。

（4）运行项目，打开编辑器的同时会重新生成 **DerivedDataCache** 文件夹。

（5）始终记得：

**在源码版虚幻引擎的解决方案中，不要使用 Visual Studio 的【清理】和【重新生成】功能！**

**在源码版虚幻引擎的解决方案中，不要使用 Visual Studio 的【清理】和【重新生成】功能！**

**在源码版虚幻引擎的解决方案中，不要使用 Visual Studio 的【清理】和【重新生成】功能！**

嗯，怎么提醒都不为过！

### 隐藏彩蛋！！

经过我的调试，项目进行过程中，清理文件是经常做的。而每次都手动删除那几个文件夹，着实太累了，然后我写了一个脚本，只需要放到项目文件夹下，就会按照上方的清理步骤来处理当前项目，清理干净后，重新编译项目，就是一个全新的编译了。

为什么要这么做？当出现一个编译错误很难找到原因，或者冒出一些莫名其妙的运行时错误的时候，这个方法有奇效。

以下是代码，运行之前，务必考虑做好备份，自行承担风险。我的电脑运行完美，不代表你的也可以，切记切记。

注意！ `ENGINE_ROOT` 需要更改为你的自己引擎的目录！不然重新生成 Visual Studio 项目文件会不生效。

```shell
:: 一键清理 UE 项目文件，之后可重新编译项目
@echo off
:: 设置项目根目录路径（默认为当前脚本所在目录）
set PROJECT_ROOT=%~dp0

:: 设置引擎根目录路径（根据实际情况修改）
set ENGINE_ROOT=你的引擎目录，比如 F:\UE\UnrealEngine_Angelscript

:: 切换到项目根目录
cd /d "%PROJECT_ROOT%"

:: 定义需要删除的文件夹和文件
set FOLDERS_TO_DELETE=Binaries Build DerivedDataCache Intermediate
set FILES_TO_DELETE=*.sln

:: 提示即将执行的操作
echo 正在清理以下内容:
for %%F in (%FOLDERS_TO_DELETE%) do echo    文件夹: %%F
for %%F in (%FILES_TO_DELETE%) do echo    文件: %%F

:: 删除文件夹
for %%F in (%FOLDERS_TO_DELETE%) do (
    if exist "%%F" (
        echo 删除文件夹: %%F
        rmdir /s /q "%%F"
    ) else (
        echo 文件夹 %%F 不存在，跳过。
    )
)

:: 删除文件
for %%F in (%FILES_TO_DELETE%) do (
    echo 删除文件: %%F
    del /q "%%F"
)

:: 检查是否存在 .uproject 文件
set UPROJECT_FILE=
for %%F in (*.uproject) do set UPROJECT_FILE=%%F

if "%UPROJECT_FILE%"=="" (
    echo 未找到 .uproject 文件，无法重新生成项目文件。
    pause
    exit /b 1
)

:: 重新生成 Visual Studio 项目文件
echo 重新生成 Visual Studio 项目文件...
"%ENGINE_ROOT%\Engine\Binaries\DotNET\UnrealBuildTool\UnrealBuildTool.exe" -projectfiles -project="%PROJECT_ROOT%%UPROJECT_FILE%" -game

echo 清理完成！
pause
```

# 总结

使用自编译引擎，是个不错地学习 UE 的方式，可以更加深刻地了解 UE 项目的本质，一个 UE 项目本质上就是【引擎】模块们 + 【项目】模块们组合起来的一个 cpp 项目。

通过自编译引擎，以及尝试自己去创建模块，就能明白我们的开发，就是在原来的积木上增加自己的积木。

也只有通过自编译引擎，才可以自由地修改引擎的一些内容（谨慎、谨慎）。
