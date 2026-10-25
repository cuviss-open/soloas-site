# 环境配置与快速上手

## 环境配置

### 引擎版本

- 当前适配版本为 UE 5.8.4，推荐使用官方 Launcher 安装版。
- 源码构建引擎（同一适配 tag）理论上功能等价，但不作保证。

### 操作系统

- Windows 11 x64 是主要支持与验收平台；Windows 10 理论上支持，但不作保证。
- macOS 15 及以上是弱支持，仅做有限的编译验证，不做行为保证。

### C++ 工具链

- 使用预编译包时，纯蓝图工程在编辑器内可以直接使用；打包要求见发布说明。
- 使用源码包需要 C++ 工程和 Visual Studio 工具链，安装后需要编译项目。

### 代码编辑器

- VS Code，安装 Hazelight 的 Unreal Angelscript 扩展，详见 [Hazelight 文档站](https://angelscript.hazelight.se)。
- 工作区设为工程的 `Script` 文件夹；补全、诊断、跳转、断点、变量和继续执行都可用。
- 正常启动编辑器，不要加 `-NoMessaging` 或 `-NoASDebugServer`，它们会关掉扩展用到的 DebugServer。

## 快速上手

1. **新建项目**：用原版 UE 新建一个项目。
2. **复制插件**：x.x.x 为 soloAS 版本，uex.x.x 为适配的 UE 版本，从 [Releases](https://github.com/cuviss-open/soloAS/releases/latest) 页面下载最新版本，二选一：
   - 预编译包（推荐）：`soloAS-x.x.x-uex.x.x-win64.7z`，解压到项目的 `Plugins/` 下即可使用。Win11 可以直接解压，Win10 需要先安装 7-Zip。
   - 源码包：`soloAS-x.x.x-uex.x.x-source.zip`，需要 C++ 工程和 Visual Studio 工具链，按下面“插件目录与依赖”放进 `<Project>/Plugins/`。
   - 调试符号：`soloAS-x.x.x-uex.x.x-win64-symbols.7z`，只在调试或查看崩溃堆栈时需要，解压覆盖到同一位置。
3. **生成并构建**（使用源码包时）：关闭编辑器，在 `.uproject` 上右键选择 **Generate Visual Studio project files**，打开 `.sln`，构建 `<项目名>Editor`、Win64、Development，再打开 `.uproject`。
4. **启用插件**：`Angelscript` 默认启用，`SoloASBridge` 随它自动启用；用到 GAS 或 Enhanced Input 绑定时，在编辑器的插件窗口启用 `AngelscriptGAS` 或 `AngelscriptEnhancedInput`，并按提示重启编辑器。
5. **写代码**：之后就可以在 `<Project>/Script/` 里写 AngelScript（`.as`）代码，修改脚本不需要重启编辑器。第一个脚本见下。

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

## 插件目录与依赖

源码包含四个插件，按下表放进 `<Project>/Plugins/`，预编译包解压到 `Plugins/` 后即可使用：

| 源码包中的目录 | 放入 `<Project>/Plugins/` 后的目录 |
| --- | --- |
| `AngelscriptRuntime/` | `soloAS/AngelscriptRuntime/` |
| `SoloASBridge/` | `soloAS/SoloASBridge/` |
| `AngelscriptManualBindPlugins/AngelscriptGAS/` | `soloAS/AngelscriptManualBindPlugins/AngelscriptGAS/` |
| `AngelscriptManualBindPlugins/AngelscriptEnhancedInput/` | `soloAS/AngelscriptManualBindPlugins/AngelscriptEnhancedInput/` |

`soloAS/` 只是整理插件的父目录，不是插件。Runtime 的源码目录叫 `AngelscriptRuntime`，描述符是 `Angelscript.uplugin`，UE 插件名为 `Angelscript`。目录名可以保留，也可以按项目需要自定义。插件也可以放在 `<UE>/Engine/Plugins/` 下供该引擎的多个项目使用，项目级安装更便于项目固定自己的版本。不要在引擎和项目里同时安装同名插件，也不要在项目里留两份。

| 插件 | 依赖的插件 | 默认状态 |
| --- | --- | --- |
| `Angelscript`（Runtime） | `SoloASBridge` | 默认启用，Bridge 随之启用 |
| `SoloASBridge` | `DataValidation`、`StateTree` | 默认关闭，由 Runtime 依赖启用 |
| `AngelscriptGAS` | `GameplayAbilities`、`Angelscript` | 默认关闭，使用 GAS 绑定时启用 |
| `AngelscriptEnhancedInput` | `EnhancedInput`、`Angelscript` | 默认关闭，使用输入绑定时启用 |

使用源码包，或更改了插件的 C++ 之后，关闭编辑器，重新生成项目文件并重建 Editor target，再启动编辑器。命令行的等价构建：

```bat
"<UE>\Engine\Build\BatchFiles\Build.bat" <ProjectName>Editor Win64 Development -Project="<Project>\<ProjectName>.uproject" -NoUBA -NoMessaging
```

常见提示：

- 重复安装：`The same version (v1) of plugin 'Angelscript' exists at '<第一处路径>' and '<第二处路径>' - second location will be ignored.`，删掉多余的一份。
- 缺少依赖：`This project requires the 'Angelscript' plugin, which has a missing dependency on the 'SoloASBridge' plugin.` 后面还有两段：`Would you like to disable it?` 和 `If you do, you will no longer be able to open any assets created with it. If not, the application will close.`，检查 `SoloASBridge` 目录是否放对。
- 模块缺失：`Plugin 'Angelscript' failed to load because module 'AngelscriptCode' could not be found.  Please ensure the plugin is properly installed, otherwise consider disabling the plugin for this project.`，重新生成项目文件并构建 Editor。
- 版本不符：`Plugin 'Angelscript' failed to load because module 'AngelscriptCode' does not appear to be compatible with the current version of the engine.  The plugin may need to be recompiled.`，用当前引擎重新编译。
