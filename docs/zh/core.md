# 插件核心

在未经修改的 Unreal Engine 上提供 AngelScript 核心脚本工作流，并兼容 UE-AS fork 的常见用法，可以直接参考 [Hazelight 文档](https://angelscript.hazelight.se/)。

## 主要区别与改进

- 使用原版 UE，以项目插件提供脚本能力，无需编译引擎。
- 从以 UE-AS fork 作为引擎的工程带来的资产，若提示保存时的引擎版本为空，可用 **SoloAS → Resave assets with empty engine version（重新保存引擎版本为空的资产）** 批量重新保存。
- 修复了垃圾回收或热重载时，同一个脚本对象的析构函数可能执行两次的问题。
- 预编译脚本缓存损坏或被截断时会明确报错，不再读到一半出错。
- 插件模块不支持在编辑器运行中卸载或重新加载；Live Coding 和脚本热重载照常可用。

## 技术限制与不足

- 原版 UE 上的 FullReload 可能比 UE-AS fork 耗时更长，差距取决于项目。
- 部分编辑器体验优化要在本版本适配的原版引擎上才能完整生效；对运行时和打包后的游戏没有影响。

[soloAS 最新版与 UE-AS fork 的 API 差异](api-differences.md)
