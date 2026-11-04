# SoloAS 菜单

在关卡编辑器主菜单的 **Tools** 旁边打开 **SoloAS**。

## Resave assets with empty engine version（重新保存引擎版本为空的资产）

加载资产时出现 `Asset has been saved with empty engine version` 警告，可使用此项处理；从 UE-AS fork 迁移的项目较常遇到此问题，也可以直接点击通知中的 **Fix in one click**。此操作会重新保存项目内已保存引擎版本为空的资产。完成后，编辑器会报告成功、失败和跳过的数量。

## Fix assets affected by load-time rebinding（修复加载时重新绑定影响的资产）

编辑器提示 `SoloAS deferred a script reload while assets were loading. Reload the affected assets.` 时，可使用此项。此操作会从磁盘重新加载受影响的项目资产；未保存的资产和项目之外的资产会跳过。完成后，编辑器会报告成功、失败和跳过的数量。

## About soloAS（关于 soloAS）

此项列出已安装的 soloAS 插件版本。也会显示当前 UE 版本是否受支持。

## Check for updates（检查更新）

只有点击此项时，编辑器才会联网检查更新。发现新版本时，可选择 **Update (restart editor to finish)**（更新，重启编辑器后完成）；步骤和限制见[更新 soloAS](requirements.md#更新-soloas)。
