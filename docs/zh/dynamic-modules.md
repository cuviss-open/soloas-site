# 功能模组（Feature Mod）

## 介绍

功能模组让你把一段玩法写成可独立装载、卸载和更新的 **FeatureMod**，日常简称 Mod。例如，把一套挑战规则或一个新玩法放进自己的 Mod。

### Mod 在哪一层

<svg class="ov-svg ov-wide" viewBox="0 0 1000 440" role="img" aria-label="功能模组的层级，自上而下：最上层是功能模组，分内置功能模组（随项目一起打包）、官方外部功能模组（有签名）、玩家外部功能模组（API 黑名单，首次加载需确认）三类；其下依次是 Game Feature 插件、游戏项目、插件（项目插件和引擎插件）、UE 引擎核心模块。上层可以依赖下层，下层不能依赖功能模组。"><defs><marker id="ov3w" viewBox="0 0 8 8" refX="7" refY="4" markerWidth="8" markerHeight="8" orient="auto"><path class="ov-head" d="M0 0L8 4L0 8z"/></marker></defs><text class="ov-layer" x="0" y="40">功能模组</text><rect class="ov-node" x="120" y="10" width="285.333" height="50" rx="9"/><text class="ov-name" x="262.667" y="32" text-anchor="middle">内置功能模组</text><text class="ov-sub" x="262.667" y="50" text-anchor="middle">随项目一起打包</text><rect class="ov-node" x="417.333" y="10" width="285.333" height="50" rx="9"/><text class="ov-name" x="560" y="32" text-anchor="middle">官方外部功能模组</text><text class="ov-sub" x="560" y="50" text-anchor="middle">有签名</text><rect class="ov-node" x="714.667" y="10" width="285.333" height="50" rx="9"/><text class="ov-name" x="857.333" y="32" text-anchor="middle">玩家外部功能模组</text><text class="ov-sub" x="857.333" y="50" text-anchor="middle">API 黑名单，首次加载需确认</text><path class="ov-arrow" d="M560 64V87" marker-end="url(#ov3w)"/><text class="ov-layer" x="0" y="122">Game Feature 插件</text><rect class="ov-node" x="120" y="92" width="880" height="50" rx="9"/><text class="ov-name" x="560" y="114" text-anchor="middle">Game Feature 插件</text><text class="ov-sub" x="560" y="132" text-anchor="middle">可开关的玩法单元，运行时激活</text><path class="ov-arrow" d="M560 146V169" marker-end="url(#ov3w)"/><text class="ov-layer" x="0" y="204">游戏项目</text><rect class="ov-node" x="120" y="174" width="880" height="50" rx="9"/><text class="ov-name" x="560" y="196" text-anchor="middle">游戏项目</text><text class="ov-sub" x="560" y="214" text-anchor="middle">项目的玩法与资源</text><path class="ov-arrow" d="M560 228V251" marker-end="url(#ov3w)"/><text class="ov-layer" x="0" y="286">插件</text><rect class="ov-node" x="120" y="256" width="434" height="50" rx="9"/><text class="ov-name" x="337" y="278" text-anchor="middle">项目插件</text><text class="ov-sub" x="337" y="296" text-anchor="middle">soloAS 插件、其他项目插件</text><rect class="ov-node" x="566" y="256" width="434" height="50" rx="9"/><text class="ov-name" x="783" y="278" text-anchor="middle">引擎插件</text><text class="ov-sub" x="783" y="296" text-anchor="middle">GameplayAbilities、EnhancedInput 等</text><path class="ov-arrow" d="M560 310V333" marker-end="url(#ov3w)"/><text class="ov-layer" x="0" y="368">UE 核心</text><rect class="ov-node base" x="120" y="338" width="880" height="50" rx="9"/><text class="ov-name" x="560" y="360" text-anchor="middle">UE 引擎核心模块</text><text class="ov-sub" x="560" y="378" text-anchor="middle">引擎提供的基础功能</text><text class="ov-sub" x="120" y="428">↓ 上层可以依赖下层</text><text class="ov-sub" x="560" y="428">✕ 下层不能依赖功能模组</text></svg>
<svg class="ov-svg ov-tall" viewBox="0 0 300 688" role="img" aria-label="功能模组的层级，自上而下：最上层是功能模组，分内置功能模组（随项目一起打包）、官方外部功能模组（有签名）、玩家外部功能模组（API 黑名单，首次加载需确认）三类；其下依次是 Game Feature 插件、游戏项目、插件（项目插件和引擎插件）、UE 引擎核心模块。上层可以依赖下层，下层不能依赖功能模组。"><defs><marker id="ov3t" viewBox="0 0 8 8" refX="7" refY="4" markerWidth="8" markerHeight="8" orient="auto"><path class="ov-head" d="M0 0L8 4L0 8z"/></marker></defs><text class="ov-layer" x="10" y="12">功能模组</text><rect class="ov-node" x="10" y="20" width="280" height="46" rx="9"/><text class="ov-name" x="150" y="42" text-anchor="middle">内置功能模组</text><text class="ov-sub" x="150" y="60" text-anchor="middle">随项目一起打包</text><rect class="ov-node" x="10" y="74" width="280" height="46" rx="9"/><text class="ov-name" x="150" y="96" text-anchor="middle">官方外部功能模组</text><text class="ov-sub" x="150" y="114" text-anchor="middle">有签名</text><rect class="ov-node" x="10" y="128" width="280" height="46" rx="9"/><text class="ov-name" x="150" y="150" text-anchor="middle">玩家外部功能模组</text><text class="ov-sub" x="150" y="168" text-anchor="middle">API 黑名单，首次加载需确认</text><text class="ov-layer" x="10" y="220">Game Feature 插件</text><rect class="ov-node" x="10" y="228" width="280" height="46" rx="9"/><text class="ov-name" x="150" y="250" text-anchor="middle">Game Feature 插件</text><text class="ov-sub" x="150" y="268" text-anchor="middle">可开关的玩法单元，运行时激活</text><text class="ov-layer" x="10" y="320">游戏项目</text><rect class="ov-node" x="10" y="328" width="280" height="46" rx="9"/><text class="ov-name" x="150" y="350" text-anchor="middle">游戏项目</text><text class="ov-sub" x="150" y="368" text-anchor="middle">项目的玩法与资源</text><text class="ov-layer" x="10" y="420">插件</text><rect class="ov-node" x="10" y="428" width="280" height="46" rx="9"/><text class="ov-name" x="150" y="450" text-anchor="middle">项目插件</text><text class="ov-sub" x="150" y="468" text-anchor="middle">soloAS 插件、其他项目插件</text><rect class="ov-node" x="10" y="482" width="280" height="46" rx="9"/><text class="ov-name" x="150" y="504" text-anchor="middle">引擎插件</text><text class="ov-sub" x="150" y="522" text-anchor="middle">GameplayAbilities、EnhancedInput 等</text><text class="ov-layer" x="10" y="574">UE 核心</text><rect class="ov-node base" x="10" y="582" width="280" height="46" rx="9"/><text class="ov-name" x="150" y="604" text-anchor="middle">UE 引擎核心模块</text><text class="ov-sub" x="150" y="622" text-anchor="middle">引擎提供的基础功能</text><text class="ov-sub" x="10" y="650">↓ 上层可以依赖下层</text><text class="ov-sub" x="10" y="669">✕ 下层不能依赖功能模组</text><path class="ov-arrow" d="M150 185V204" marker-end="url(#ov3t)"/><path class="ov-arrow" d="M150 285V304" marker-end="url(#ov3t)"/><path class="ov-arrow" d="M150 385V404" marker-end="url(#ov3t)"/><path class="ov-arrow" d="M150 539V558" marker-end="url(#ov3t)"/></svg>


Mod 位于最上层：可以依赖游戏项目、Game Feature Plugin 和其他 Mod，反过来它们都不能依赖 Mod。按信任来源，Mod 分三类：内置模块随项目一起打包，不受玩家 API 黑名单限制；官方外部模块带有项目开发者的签名；玩家外部模块默认可使用未被黑名单禁止的 API。详见下文“模块的三类与信任”。

## 使用方式

启用功能模组后，Mod 就像普通插件一样放置。Mod 分为以下三类：

- **内置模块**：随项目一起打包，是项目自己的 Mod，不受玩家 API 黑名单限制。
- **官方外部模块**：带有项目开发者的签名；权限与内置模块相同。
- **玩家外部模块**：没有签名或签名无法识别，可以直接加载，可以使用未被黑名单禁止的接口；第一次加载时会弹出确认，这个确认可以关掉。

随项目打包的 Mod 放在 `Plugins/FeatureMods/<名字>/`；玩家或第三方安装的 Mod 放在游戏根目录的 `FeatureMods/<名字>/`。随项目打包的内置 Mod 具有内置信任；外部 Mod 按签名确定信任。玩家安装 Mod 就是复制进去，启动游戏。

用 **SoloAS → FeatureMods** 创建 Mod、编辑清单、查看依赖或执行 **One-click check**。目录名与 `.uplugin` 文件名必须相同，作为稳定的 Mod 名字；`.uplugin` 中用 `"FeatureMod": true` 标记它，玩法脚本放在这个 Mod 的 `Script/` 中。

## Mod 配置：FeatureMod.json

配置放在 Mod 根目录的 `FeatureMod.json`。从下面的最小清单开始：

```json
{
  "schemaVersion": 1,
  "version": "1.0.0",
  "dependencies": { "trunkModules": [], "branches": [], "featureMods": [] },
  "BlueprintBindings": {},
  "BlueprintDependencies": []
}
```

| 字段 | 你需要填写什么 |
| --- | --- |
| `version` | 这个 Mod 的发布版本；更新时递增。 |
| `dependencies` | 这个 Mod 直接使用的外部内容，分三类，见下。 |
| `BlueprintBindings` | 给蓝图资产取名字；脚本用名字，不写资产路径。 |
| `BlueprintDependencies` | 脚本要继承的蓝图父类名字。 |

`dependencies` 声明这个 Mod 直接使用了哪些别人提供的东西，三类都没有就留空数组：

- `trunkModules`：用到项目主体就写固定标识 `Project`，用到普通插件里的脚本就写它的稳定插件 ID。不需要填写 C++ 模块名；旧清单里的模块名仍然兼容。
- `branches`：要用的普通 Game Feature Plugin 名字；同时要在 `.uplugin` 的 `Plugins` 中声明它的 UE 依赖。
- `featureMods`：要用的其他 Mod 名字。

用到什么就直接列出什么：间接依赖不会授予引用权限；缺失依赖或循环依赖会让相关 Mod 被拒绝，不影响无关的 Mod。填写的名字必须对应工程中真实存在的插件或 Mod，并且用到的插件要已启用。

## 模块的三类与信任

签名用于标明“官方”；项目也可以只允许官方外部模块。声称是官方签名但验证失败的模块会被拒绝，不会降级当成玩家外部模块加载。

官方外部模块需要作者和项目开发者配合。FeatureMods 窗口的签名按钮提供操作说明，签名由外部工具完成：

1. 作者创建 `FeatureMods/<名字>/`，准备带有 `"FeatureMod": true` 的 `.uplugin`、`FeatureMod.json` 和全部文件。
2. 项目开发者在 `DefaultEngine.ini` 的 ModKit 配置里设置 Ed25519 公钥（`PatchPublicKeyBase64`）和 Key ID（`PatchVerifyKeyId`），Shipping 构建会把这个信任根编进游戏，之后换密钥要重新构建。请使用发布方认可的密钥生成和签名工具。
3. 使用打包操作生成清单草稿和待签名字节，用外部工具签名并填入签名值。发布包需要旁置的 `<名字>.manifest.json`，列出 Mod 目录里每个文件及其 SHA-256，并带有效签名；它和 `FeatureMod.json` 是两份不同的文件。
4. 部署时把 Mod 放到游戏根的 `FeatureMods/<名字>/`，签名清单放在旁边。
5. 游戏启动时会校验签名、公钥 ID、引擎版本、文件哈希和完整文件集合，通过后标为官方外部模块；不匹配的官方模块会被拒绝。

版本下限只对有签名的模块生效：第一次验证成功时自动记录，默认拒绝降级，不需要手动放置下限文件。

玩家外部模块没有签名或签名无法识别，不需要任何签名文件，可以直接加载；玩家安装就是复制进去，启动游戏。第一次加载时会弹出确认，项目可以关掉这个确认。

项目可以开启“只允许官方外部模块”开关（默认关闭），开启后只加载官方外部模块。

部署前可用 `ModKitPatchVerify -Kind=package` 离线验证 Mod 包。

签名说明“谁发布了这些文件”。内置模块和官方外部模块不受玩家 API 黑名单限制。玩家外部模块默认可以调用可用的 API、继承基类和覆盖事件；默认黑名单限制控制台命令、文件读写删除、启动外部程序、打开 URL、退出游戏、按名称修改对象属性、编辑器 API，以及 `QuitGame` 和 `DeleteGameInSlot`。标记为 `internal` 的接口始终拒绝。作者可用项目提供的 `PublicApi.as` 查看可用函数。

项目维护者可以在 `Config/DefaultEngine.ini` 中追加黑名单，例如：

```ini
[/Script/AngelscriptModKit.ModKitSettings]
+DeniedApiPatterns=*FVector::FVector*
+DeniedBaseClassPatterns=APawn
+DeniedOverridePatterns=*AActor::BeginPlay*
```

这三项分别限制调用、继承和事件覆盖。项目规则与默认黑名单共同生效，黑名单优先；如需调整权限，请联系项目维护者。
