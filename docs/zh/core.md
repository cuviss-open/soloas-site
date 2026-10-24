# 插件核心

在未经修改的 Unreal Engine 上提供 AngelScript 核心脚本工作流，并兼容 Hazelight 的 UE 分支（Haze fork）的常见用法，可以直接参考 [Hazelight 文档](https://angelscript.hazelight.se/)。

## 主要区别与改进

- 使用原版 UE，以项目插件提供脚本能力，无需编译引擎。
- 从以 Haze fork 作为引擎的工程带来的资产，若提示保存时的引擎版本为空，可用 **SoloAS → Resave assets with empty engine version** 批量重新保存。
- 修复了垃圾回收或热重载时，同一个脚本对象的析构函数可能执行两次的问题。
- 预编译脚本缓存损坏或被截断时会明确报错，不再读到一半出错。

## 技术限制与不足

- Stock UE 上的 FullReload 约为 Haze fork 的 1.6 到 1.8 倍耗时，这是已知的适配成本。
- 部分编辑器体验优化要在本版本适配的原版引擎上才能完整生效；对运行时和打包后的游戏没有影响。
