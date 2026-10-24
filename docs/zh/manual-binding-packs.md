# 手工绑定包

项目用到对应玩法系统时，再启用相应绑定包。

## GAS：用脚本写技能和属性

使用 Gameplay Ability System 时启用 `AngelscriptGAS`。源自 Haze fork 的同名插件，仅为适配做了少量修改，脚本用法与 Haze fork 一致。

## Enhanced Input：在脚本里响应输入

使用 Input Action 和 Input Mapping Context 时启用 `AngelscriptEnhancedInput`。源自 Haze fork 的同名插件，仅为适配做了少量修改，脚本用法与 Haze fork 一致。

## SoloASPacks：补充你正在用的功能（待发布）

`SoloASPacks` 下各包按需启用，不必全开（仅列出部分包）：

| 你要控制的内容 | 绑定插件 |
| --- | --- |
| PCG 生成 | `AngelscriptPCGBindings` |
| Niagara 特效 | `AngelscriptNiagaraBindings` |
| Game Features | `AngelscriptGameFeaturesBindings` |
| Common UI 界面 | `AngelscriptCommonUIBindings` |
| Gameplay Graph | `AngelscriptGameplayGraphBindings` |
