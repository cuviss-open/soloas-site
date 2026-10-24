# 项目打包

命令以 Windows PowerShell 为例，`$UE`、`$Project`、`$Target`、`$Release` 分别是引擎根目录、`.uproject` 完整路径、Game target 名和发布目录。

## 共同步骤

1. 编译 Shipping Game：

   ```powershell
   & "$UE/Engine/Build/BatchFiles/Build.bat" $Target Win64 Shipping "-Project=$Project" -WaitMutex -NoHotReload -NoUBA
   ```

2. 用 Platforms → Windows → Package Project 选择 Shipping，或执行 BuildCookRun：

   ```powershell
   & "$UE/Engine/Build/BatchFiles/RunUAT.bat" -nocompileuat -WaitForUATMutex BuildCookRun "-project=$Project" -NoP4 -platform=Win64 -clientconfig=Shipping -cook -stage -pak -package -archive "-archivedirectory=$Release" -nobuild -unattended -utf8output
   ```

3. 检查包：`UnrealPak.exe <发布包中的.pak> -List` 查看包内文件，再启动发布目录里的游戏，进入用到脚本的关卡调用一个代表性函数。游戏正常退出不能证明脚本已加载。

## 带源码打包

适用于先把游戏交付跑通，或允许玩家查看、修改脚本：运行时读取 `.as` 并编译，启动时有脚本编译时间。Pak 可以提取出源码。

直接按共同步骤的 1、2、3 执行。

没有预编译缓存时，项目的 `Script/` 会被一起打进 Pak。

## 字节码打包

不分发主体 AS 源码，并减少启动时的预处理和编译。函数仍由 VM 执行字节码，缓存里的程序数据可以被分析，不能当作加密或防逆向。

1. 清掉要发布的项目 `Script/` 里旧的缓存文件：`Binds.Cache`、`Binds.Cache.Headers` 和 `PrecompiledScript*.Cache`。
2. 按共同步骤的第 1 步编译 Shipping Game。
3. 用 Shipping exe 生成匹配的预编译数据，不能用编辑器生成的。进程写完后会自己退出：

   ```powershell
   & "<构建输出中的Shipping.exe>" -as-generate-precompiled-data -as-write-bind-db -unattended -nocrashreports -NullRHI -NoMessaging -NoASDebugServer -NoSound -NoSplash
   ```

4. 把实际写出的三个文件原样复制回要发布的项目的 `Script/`，不要混用另一轮生成的文件，找不到这三个文件就停止：

   ```text
   Binds.Cache
   Binds.Cache.Headers
   PrecompiledScript.Cache
   ```

   输出在 `<项目>/Saved/Cooked/Windows/<项目名>/Script/`。
5. 按共同步骤的 1、2、3 重新编译、打包、检查；检查时确认包里有这三个缓存文件，没有项目 `.as`。

- **无源码包需要哪些文件**：就是上面三个缓存文件，三个都存在且非空时，Shipping 构建默认只把这三个文件打进 Pak，不再带项目 `.as`。
- **旧缓存会被拒绝**：缓存与 exe 不匹配时，没有源码的包会报 `ASR-PRECOMPILED-NO-SOURCE: No compatible precompiled script cache and no script source files are available.`，需要重新生成并重新发布匹配的缓存。`Loaded angelscript precompiled data was for a different build configuration. Discarding all precompiled data.` 表示缓存是用另一套配置生成的。

## 半 AOT 打包

把可生成的 AS 函数转成 C++ 编进游戏，减少虚拟机开销；运行时仍保留字节码入口。代价是 C++ 编译时间更长、exe 更大。详见 [Hazelight 官方说明](https://angelscript.hazelight.se/cpp-bindings/precompiled-data/)。

1. 清掉要发布的项目 `Script/` 里旧的缓存文件：`Binds.Cache`、`Binds.Cache.Headers` 和 `PrecompiledScript*.Cache`，以及项目模块里旧的 `AS_JITTED_CODE`。
2. 按共同步骤的第 1、2 步编译 Shipping Game 并打包一次。
3. 在包目录运行 Shipping exe 生成预编译数据，不能用编辑器生成的。进程写完后会自己退出：

   ```powershell
   & "<构建输出中的Shipping.exe>" -as-generate-precompiled-data -as-write-bind-db -unattended -nocrashreports -NullRHI -NoMessaging -NoASDebugServer -NoSound -NoSplash
   ```

   保存包根目录下生成的整个 `AS_JITTED_CODE/`，以及 `Binds.Cache`、`Binds.Cache.Headers`、`PrecompiledScript.Cache` 三个文件。
4. 把 `AS_JITTED_CODE/` 原样复制到游戏的 C++ 模块，例如 `Source/MyGame/AS_JITTED_CODE/`。不要改文件后缀，也不要手工 include 生成的 cpp。
5. 在这个模块的 `Build.cs` 里加上 `AngelscriptCode`，以及脚本用到的原生模块依赖。同时用 GAS 和 Enhanced Input 的示例：

   ```csharp
   PrivateDependencyModuleNames.AddRange(new[] { "AngelscriptCode", "EnhancedInput", "GameplayAbilities", "GameplayTasks", "AngelscriptGAS", "AngelscriptEnhancedInput" });
   ```
6. 改了 `Build.cs` 后重新生成项目文件。
7. 把第 3 步保存的三个缓存文件放回要发布的项目的 `Script/`，必须在打包之前放回。然后按共同步骤的 1、2、3 重新编译、打包、检查；检查时确认包里有这三个缓存文件、没有项目 `.as`，运行时代表玩法正常。

- **缓存和 exe 必须配套**：只为加入这批生成的 C++ 而重编，不需要重新生成缓存；改了脚本、引擎、插件或其他 C++ 后，要从第 2 步重新开始。
- **缓存要在打包前放回**：打包后才放回缓存不会更新已经生成的 Pak。

打包流程可以进一步优化，拟在后续增加特性时提供。
