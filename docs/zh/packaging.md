# 项目打包

## 打包入口

1. 地图、烘焙、Pak/IoStore、目标等选项在 **SoloAS → UE 打包设置** 中设置，这里打开 UE 原生的“项目设置 → 项目 → 打包”页面。
2. **SoloAS → 打包项目…** 打开 UE 项目启动器，按 UE 原生流程打包。脚本以源码形式随包交付。
3. 需要字节码或半 AOT 时，在 **SoloAS → soloAS 打包设置** 中选择交付方式和输出目录，再按下文使用命令行或 AI 辅助打包。

## 字节码打包

不分发主体 AS 源码，并减少启动时的预处理和编译。函数仍由 VM 执行字节码，不是原生加速；缓存里的程序数据可以被分析，不能当作加密或防逆向。

在 soloAS 打包设置选择“字节码”，或在 CLI 方案里设置 `deliveryMode=bytecode`，然后运行 soloAS 打包 CLI。工具会生成匹配的预编译缓存，收集到发布副本的 `Script/` 并在打包后检查。基础缓存包括 `Binds.Cache`、`Binds.Cache.Headers` 和 `PrecompiledScript.Cache`；包内不应包含项目 `.as` 源码。

- **缓存与 exe 不匹配**：没有源码的包会报 `ASR-PRECOMPILED-NO-SOURCE: No compatible precompiled script cache and no script source files are available.`，由维护者重新发布匹配的缓存。`Loaded angelscript precompiled data was for a different build configuration. Discarding all precompiled data.` 表示缓存是用另一套配置生成的。

## 半 AOT 打包（static JIT）

把可生成的 AS 函数转成 C++ 编进 Game，减少这些函数的 VM 开销；AS 运行时、反射和字节码入口仍然保留。代价是更长的 C++ 编译时间和更大的可执行文件，不保证所有函数都更快。

在 soloAS 打包设置选择“半 AOT”，或在 CLI 方案里设置 `deliveryMode=semi_aot`，然后运行 soloAS 打包 CLI。生成预编译数据的同一轮会输出 JIT 的 C++ 文件，`sync-jit` 命令把它们放进 C++ 消费模块；消费模块不存在时会自动生成并登记到 Game target，之后每次生成都自动同步并重编 Game。顺序固定为“生成、重编 Game、打包”，只重新 cook 不会把 C++ 链进 exe。`check-package` 命令应判定为“半 AOT 包”：JIT 消费模块已经链进 exe，包里是匹配的缓存。

- **怎样进包**：JIT 的 C++ 通过正常编译进入 exe，不靠放进 Pak；缓存按字节码打包的规则进包。
- **缓存与 exe 的 JIT 不匹配**：会提示 `Loaded angelscript precompiled data does not match the transpiled C++ in the game binary. Transpiled code will not be used!`，改走缓存里的字节码，主要影响性能。模块缓存集合不匹配时可能整组失效。

## 用脚本和 CI 打包

随插件提供的 `soloas_package.py` 与原生设置页读取同一份工程配置，可在脚本或 CI 中读取、修改配置、管理方案、执行检查、打包和查询结果。soloAS CLI 自动化目前仅支持 Win64。`<Tool>` 是已安装插件里的 `Build/PackagingTool/soloas_package.py`：

```text
python <Tool> --project <Game.uproject> profiles list --json
python <Tool> --project <Game.uproject> config read --platform Win64 --json
python <Tool> --project <Game.uproject> precheck --json
python <Tool> --project <Game.uproject> run --json
python <Tool> --project <Game.uproject> status --job <id> --json
```

不带 `--profile` 时使用工程默认值。需要可重复的命名方案时，先创建，再指定方案运行：

```text
python <Tool> --project <Game.uproject> profiles save --name Shipping-bytecode --overrides '{"configuration":"Shipping","deliveryMode":"bytecode"}' --json
python <Tool> --project <Game.uproject> run --profile Shipping-bytecode --json
```

`precheck` 报告配置、可选工具链探测和待检查项；`run` 在构建前执行完整检查。脚本返回可供 CI 读取的结构化进度和结果。配置写入会返回修改差异；每次执行都记录对应的方案和输入版本，便于复查和重复构建。

## 让 AI 帮你准备和执行打包

在 **SoloAS → AI 辅助开发** 完成连接后，告诉 AI 你的交付目标，例如“创建 Windows Shipping 字节码方案，检查配置并打包”。AI 会读取当前工程设置，给出需要的修改和差异，保存方案并启动打包；你可以继续查询进度、定位失败的阶段和查看最终结果。AI 和命令行使用同一套打包流程，并读取原生设置页写入的工程默认配置。

连接 MCP 后，可使用 `soloas_package_config`、`soloas_package_config_write`、`soloas_package_profiles_save`、`soloas_package_precheck`、`soloas_package_run`、`soloas_package_status` 和 `soloas_package_cancel` 完成相同流程。
