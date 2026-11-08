# AI 辅助开发

## 人用 VS Code 查看和编写

- 安装 VS Code 和 UE-AS 官方发布的 [Unreal Angelscript 扩展](https://marketplace.visualstudio.com/items?itemName=Hazelight.unreal-angelscript)。
- 在 VS Code 里打开工程的 `Script` 文件夹，或用编辑器菜单 **Tools → Programming → Open Angelscript workspace (VS Code)**。
- 扩展提供补全、签名提示、F12 跳转、诊断和调试，保存后的编译错误回到 Problems 面板；**Angelscript API** 侧栏可搜索、列出和查看 API 详情。
- 扩展通过编辑器的 AS DebugServer 取得类型和编译信息，默认端口 `27099`，自动连接。改过端口时，让 `UnrealAngelscript.unrealConnectionPort` 与工程 Angelscript 设置里的 Connection Port 一致。
- 编辑器没运行，或用 `-NoMessaging`、`-NoASDebugServer` 启动时，实时功能不可用。

## AI 用 MCP 辅助开发

**SoloASMcpHost** 随 SoloASDeveloperTools 提供，位于 `Binaries/ThirdParty/SoloASMcpHost/Win64/`，已经编译好，直接运行，不需要安装 .NET，也不需要自己构建。MCP 服务由开发工具提供。AI 工具通过 stdio 启动 Host，它再连接本机编辑器的 `127.0.0.1:27099`。

在编辑器里点 **SoloAS → AI 辅助开发 → 复制 MCP 配置**，会生成已经填好 Host、引擎目录、`.uproject` 路径和端口的配置，粘贴进 AI 工具即可。

Claude Code 用下面的命令添加，其他 AI 工具把同样的命令和参数配成本地 stdio 的 MCP，或合并进工程根的 `.mcp.json`（尖括号里的值菜单已经填好）：

```text
claude mcp add --transport stdio --scope project soloas-angelscript -- "<SoloASDeveloperTools>/Binaries/ThirdParty/SoloASMcpHost/Win64/SoloASMcpHost.exe" --engine "<UERoot>" --project "<Project.uproject>" --lane stock --debug-host 127.0.0.1 --debug-port 27099
```

```json
{
  "mcpServers": {
    "soloas-angelscript": {
      "type": "stdio",
      "command": "<SoloASDeveloperTools>/Binaries/ThirdParty/SoloASMcpHost/Win64/SoloASMcpHost.exe",
      "args": [
        "--engine", "<UERoot>",
        "--project", "<Project.uproject>",
        "--lane", "stock",
        "--debug-host", "127.0.0.1",
        "--debug-port", "27099"
      ]
    }
  }
}
```

- **在线与离线**：可用的 API 以运行中编辑器的类型表为准，包含已注册的原生绑定和已编译的脚本类型。Host 会保存最近一次的类型表作快照，编辑器没开时读这份快照；第一次离线又没有快照时，API 查询返回 `DebugServer runtime type table is not available yet`。
- **和 UE 官方 MCP 并用**：soloAS 的 Host 负责 AS 的 API、脚本类型、诊断和调试；UE 的 `ModelContextProtocol` 负责编辑器里的资产、场景等操作，端口和协议都与 `27099` 无关，两者互不依赖。

## MCP 能提供什么

- **脚本类型和工程信息，只读**：列出编辑器当前已编译的脚本类型，读取工程、插件、脚本根和连接状态，读取编辑器推送的编译诊断。
- **项目打包工具**：通过 Developer Tools 查询配置、预检并运行打包，也可按工具权限保存打包设置或请求取消任务。
- **调试**：读取暂停时的调用栈和变量；设置和清除断点、继续和单步执行、求值表达式，这些会改变断点或执行状态，求值还可能有副作用，不是只读。
