# 环境配置与快速上手

## 环境配置

### 引擎版本

<!-- generated-engine-support:start -->
- 当前适配：原版 UE 5.4.4、5.5.4、5.6.1、5.7.4、5.8.4。
- 最新已适配版本的验证范围最完整。未列出的补丁版本不保证可用。
<!-- generated-engine-support:end -->
- 各版本的行为差异见[不同 UE 版本的适配差异](ue-version-differences.md)。
- 源码构建引擎（同一适配 tag）理论上功能等价，但不作保证。

### 操作系统

- Windows 11 x64 是主要支持与验收平台；Windows 10 理论上支持，但不作保证。
- macOS 15 及以上是弱支持，仅做有限的编译验证，不做行为保证。

### C++ 工具链

- 使用预编译包时，纯蓝图工程在编辑器内可以直接使用；打包要求见发布说明。
- Windows 使用源码包需要 C++ 工程和 Visual Studio 工具链，安装后需要编译项目。macOS 使用源码包需通过对应 UE 版本要求的 Xcode 工具链编译；当前仅做有限的编译验证。
- 项目路径请只使用英文字母、数字和常见符号，避免中文等非英文字符，否则 UE 在编译 C++ 时可能找不到文件。这是 UE 和 Visual Studio 编译器的限制，与 soloAS 无关。

### 代码编辑器

- VS Code，安装 Hazelight 的 Unreal Angelscript 扩展，详见 [Hazelight 文档站](https://angelscript.hazelight.se)。
- 工作区设为工程的 `Script` 文件夹；补全、诊断、跳转、断点、变量和继续执行都可用。
- 正常启动编辑器，不要加 `-NoMessaging` 或 `-NoASDebugServer`，它们会关掉扩展用到的 DebugServer。

## 快速上手

1. **新建项目**：用原版 UE 新建一个项目。
2. **复制插件**：从 [Releases](https://github.com/cuviss-open/soloAS/releases/latest) 下载适用于当前 UE 版本的最新包。预编译包和源码包都解压到项目的 `Plugins/` 下，得到 `Plugins/soloAS/`。调试符号包仅在调试或查看崩溃堆栈时需要，解压到同一位置覆盖文件。Win11 可以直接解压，Win10 需要先安装 7-Zip。
3. **生成并构建**（Windows 使用源码包时）：关闭编辑器，在 `.uproject` 上右键选择 **Generate Visual Studio project files**，打开 `.sln`，构建 `<项目名>Editor`、Win64、Development，再打开 `.uproject`。
4. **启用插件**：核心脚本支持及其必需依赖会自动启用；用到 GAS 或 Enhanced Input 绑定时，在编辑器的插件窗口启用 `AngelscriptGAS` 或 `AngelscriptEnhancedInput`，并按提示重启编辑器。
5. **写代码**：之后就可以在 `<Project>/Script/` 里写 AngelScript（`.as`）代码；`<Project>` 表示你的项目目录，例如 `MyProject/Script/`。修改脚本不需要重启编辑器。第一个脚本见下。

<!-- generated-release-assets:start -->
### 0.1.3 发布文件

可使用发布页的 `SHA256SUMS` 核验文件。macOS 仅提供源码，验证范围有限。

| 文件 | UE 版本 | 平台 | 大小 |
| --- | --- | --- | ---: |
| `soloAS-0.1.3-source.zip` | 5.4.4, 5.5.4, 5.6.1, 5.7.4, 5.8.4 | Win64, macOS | 约 3.4 MB |
| `soloAS-0.1.3-ue5.4.4-win64-symbols.7z` | 5.4.4 | Win64 | 约 418.5 MB |
| `soloAS-0.1.3-ue5.4.4-win64.7z` | 5.4.4 | Win64 | 约 102.9 MB |
| `soloAS-0.1.3-ue5.5.4-win64-symbols.7z` | 5.5.4 | Win64 | 约 463.6 MB |
| `soloAS-0.1.3-ue5.5.4-win64.7z` | 5.5.4 | Win64 | 约 197.4 MB |
| `soloAS-0.1.3-ue5.6.1-win64-symbols.7z` | 5.6.1 | Win64 | 约 499.6 MB |
| `soloAS-0.1.3-ue5.6.1-win64.7z` | 5.6.1 | Win64 | 约 205.3 MB |
| `soloAS-0.1.3-ue5.7.4-win64-symbols.7z` | 5.7.4 | Win64 | 约 522.9 MB |
| `soloAS-0.1.3-ue5.7.4-win64.7z` | 5.7.4 | Win64 | 约 202.7 MB |
| `soloAS-0.1.3-ue5.8.4-win64-symbols.7z` | 5.8.4 | Win64 | 约 567.6 MB |
| `soloAS-0.1.3-ue5.8.4-win64.7z` | 5.8.4 | Win64 | 约 205.3 MB |
<!-- generated-release-assets:end -->

保存一个继承 `AActor` 的脚本类，在 `BeginPlay` 里打印文字。把它放进关卡或由游戏逻辑生成后，游戏视口会显示 “Hello from soloAS!” 数秒，Output Log 也会记录这段文字：

```angelscript
class AFirstScriptActor : AActor
{
    bool bHelloWorldShown = false;

    UFUNCTION(BlueprintOverride)
    void BeginPlay()
    {
        Print("Hello from soloAS!");
        bHelloWorldShown = true;
    }
}
```

## 更新 soloAS

**方式一：通过 soloAS 菜单更新（Windows 正式发布包，0.1.3 起）**

Windows 上，按完整目录安装的正式预编译包或正式源码包可通过菜单更新；需已打开项目并保留发布清单（清单中包含校验和地址）。仓库源码检出、目录不完整或缺少发布清单时，请先手动安装正式包。在编辑器的 [**SoloAS** 菜单](soloas-menu.md)中选择 **Check for updates（检查更新）**。发现新版本时，点击 **Update (restart editor to finish)（更新，重启后完成）**，soloAS 会自动下载并校验文件。按提示重启编辑器后，更新程序会自动替换文件并重新打开项目。插件目录中由你修改或新增的配置会保留；如有冲突，会列出供你处理。更新失败时会自动恢复旧版本。插件安装在引擎目录时可能需要管理员授权；如拒绝授权，请按方式二手动更新。Mac 请使用方式二。

**方式二：整体替换（适用于所有版本）**

1. 关闭编辑器，并查看[更新日志](changelog.md)以及[不同 UE 版本的适配差异](ue-version-differences.md)中与你使用的 UE 版本对应的内容。
2. 确认插件实际安装根是项目的 `Plugins/soloAS/` 或目标引擎的 `<UE>/Engine/Plugins/soloAS/`，并备份该目录中自行修改或新增的文件。替换同一个安装位置：删除原有的整个 `soloAS/` 目录，再从 [Releases](https://github.com/cuviss-open/soloAS/releases/latest) 下载新包并解压到相同的 `Plugins/` 目录；不要直接覆盖旧文件，以免新版已删除的文件残留。如果插件直接放在 `Plugins/` 文件夹下，请删除 `Plugins/`（或 `<UE>/Engine/Plugins/`）下的 `AngelscriptRuntime/`、`SoloASBridge/`、`AngelscriptGAS/` 和 `AngelscriptEnhancedInput/` 文件夹，再解压新包。根据新版本默认值合并备份中的自定义配置。若编辑器日志提示重复安装，请按下方“插件目录与依赖”中的说明移除多余副本。
3. 使用源码包时，重新编译 C++ 工程。
4. 打开编辑器，等待脚本自动重新编译，并查看输出日志。

项目自己的配置保存在项目的 `Config/` 目录中，不受插件更新影响。

## 插件目录与依赖

预编译包和源码包解压到项目的 `Plugins/` 后，都会得到 `Plugins/soloAS/`，其目录结构如下：

| 目录 | 插件身份 | 用途 |
| --- | --- | --- |
| `AngelscriptRuntime/` | `Angelscript`（Runtime） | AngelScript 运行时与脚本支持 |
| `SoloASBridge/` | `SoloASBridge` | soloAS 与 Unreal Engine 的集成 |
| `AngelscriptManualBindPlugins/AngelscriptGAS/` | `AngelscriptGAS` | GAS 绑定 |
| `AngelscriptManualBindPlugins/AngelscriptEnhancedInput/` | `AngelscriptEnhancedInput` | Enhanced Input 绑定 |

`soloAS/` 是包含上述插件的发布目录，不是插件。Runtime 的目录名为 `AngelscriptRuntime`，描述符为 `Angelscript.uplugin`，UE 插件名为 `Angelscript`。路径中的 `<UE>` 表示引擎安装目录，例如 `C:/Program Files/Epic Games/UE_5.8`。插件也可以放在 `<UE>/Engine/Plugins/` 下供该引擎的多个项目使用，项目级安装更便于项目固定自己的版本。不要在引擎和项目里同时安装同名插件，也不要在项目里留两份。

核心脚本插件会自动启用所需依赖。GAS 和 Enhanced Input 绑定默认关闭，只有项目使用相关功能时才在插件窗口启用 `AngelscriptGAS` 或 `AngelscriptEnhancedInput`。`StateTree` 是可选依赖，只有项目使用相关功能时才需启用。

使用源码包，或更改了插件的 C++ 之后，关闭编辑器，重新生成项目文件并重建 Editor target，再启动编辑器。命令中的 `<UE>`、`<ProjectName>` 和 `<Project>` 分别替换为引擎目录、项目名和项目目录，例如 `C:/UE_5.8`、`MyGame`、`D:/MyGame`。命令行的等价构建：

```bat
"<UE>\Engine\Build\BatchFiles\Build.bat" <ProjectName>Editor Win64 Development -Project="<Project>\<ProjectName>.uproject" -NoUBA -NoMessaging
```

常见提示：

- 重复安装：`The same version (v1) of plugin 'Angelscript' exists at '<第一处路径>' and '<第二处路径>' - second location will be ignored.`，删掉多余的一份。
- 缺少依赖：`This project requires the 'Angelscript' plugin, which has a missing dependency on the 'SoloASBridge' plugin.` 后面还有两段：`Would you like to disable it?` 和 `If you do, you will no longer be able to open any assets created with it. If not, the application will close.`，检查 `SoloASBridge` 目录是否放对。
- 模块缺失：`Plugin 'Angelscript' failed to load because module 'AngelscriptCode' could not be found.  Please ensure the plugin is properly installed, otherwise consider disabling the plugin for this project.`，重新生成项目文件并构建 Editor。
- 版本不符：`Plugin 'Angelscript' failed to load because module 'AngelscriptCode' does not appear to be compatible with the current version of the engine.  The plugin may need to be recompiled.`，用当前引擎重新编译。
