# 迁移已有 AS 项目

## 1. 备份项目

复制一份完整项目，在副本中迁移；保留 `Script/`、`Config/` 和 `Content/`，并留着可运行的旧工程用于对照。

## 2. 切换到原版 UE

在备份副本中选择受支持的原版 UE 补丁版本，将 `.uproject` 的引擎关联切换到该版本（右键 `.uproject` → **Switch Unreal Engine version**，或编辑 `EngineAssociation`）。纯 AS/蓝图工程只需切换引擎关联；C++ 工程还需用该引擎重新生成项目文件。保留旧 fork 工程与引擎，供对照使用。

## 3. 安装插件

只在迁移副本和目标原版 UE 的插件目录中清理重复的旧 UE-AS 插件，不要改动作为对照保留的旧 fork 工程和引擎。然后安装 soloAS 插件，安装到项目或目标引擎均可，安装方式见[快速上手](requirements.md#快速上手)。

## 4. 启用插件

确认 `Angelscript` 主插件已启用；所需依赖会自动启用。GAS 和 Enhanced Input 按需启用。

## 5. 修理编译问题

1. **重新构建项目**：交付构建还要重新生成缓存。
2. **修编译依赖问题**：如果遇到编译问题，按照提示修理。
3. **修资产提示警告**：遇到 `Asset has been saved with empty engine version`，使用 [SoloAS 菜单中的 “Resave assets with empty engine version”（重新保存引擎版本为空的资产）](soloas-menu.md)，或点击通知中的 **Fix in one click**。保存受影响资产后再检查加载结果。

## 6. 运行项目，真实测试

验证原有 AS 脚本、热重载、按项目需要启用的 GAS 和 Enhanced Input，再用 PIE 运行、打包运行测试，走完整个流程。
