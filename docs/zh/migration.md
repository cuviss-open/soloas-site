# 迁移已有 AS 项目

## 1. 备份项目

复制一份完整项目，在副本中迁移；保留 `Script/`、`Config/` 和 `Content/`，并留着可运行的旧工程用于对照。

## 2. 安装插件

移除旧的 Haze 引擎插件，再安装 soloAS 插件，安装到项目或引擎均可，安装方式见[快速上手](requirements.md#快速上手)。

## 3. 启用插件

确认 `Angelscript`（Runtime）已启用；它会通过依赖自动启用 `SoloASBridge`。GAS 和 Enhanced Input 按需启用。

## 4. 修理编译问题

1. **重新构建项目**：交付构建还要重新生成缓存。
2. **修编译依赖问题**：如果遇到编译问题，按照提示修理。
3. **修资产提示警告**：遇到 `Asset has been saved with empty engine version`，使用 SoloAS → Resave assets with empty engine version，或通知中的 Fix in one click，保存受影响资产后再检查加载结果。

## 5. 运行项目，真实测试

验证原有 AS 脚本、热重载、按项目需要启用的 GAS 和 Enhanced Input，再用 PIE 运行、打包运行测试，走完整个流程。
