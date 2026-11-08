# AI-assisted development

## Humans: view and write in VS Code

- Install VS Code and the [Unreal Angelscript extension](https://marketplace.visualstudio.com/items?itemName=Hazelight.unreal-angelscript) published by UE-AS.
- Open the project's `Script` folder in VS Code, or use the editor menu **Tools → Programming → Open Angelscript workspace (VS Code)**.
- The extension provides completion, signature help, F12 navigation, diagnostics and debugging, and compile errors after a save return to the Problems panel; the **Angelscript API** sidebar lets you search, list and view API details.
- The extension gets types and compile information from the editor's AS DebugServer, on port `27099` by default, and connects by itself. If you changed the port, make `UnrealAngelscript.unrealConnectionPort` match the Connection Port in the project's Angelscript settings.
- When the editor is not running, or was started with `-NoMessaging` or `-NoASDebugServer`, the live features are unavailable.

## AI: assist development through MCP

**SoloASMcpHost** ships with SoloASDeveloperTools in `Binaries/ThirdParty/SoloASMcpHost/Win64/`, already built; it runs directly, needs no .NET installed and needs no building. Developer Tools provides the MCP service. The AI tool starts the Host over stdio, and it connects to the local editor at `127.0.0.1:27099`.

In the editor choose **SoloAS → AI-assisted development → Copy MCP configuration**; it generates a configuration with the Host, the engine directory, the `.uproject` path and the port already filled in, ready to paste into the AI tool.

Claude Code adds it with the command below; for other AI tools, configure the same command and arguments as a local stdio MCP, or merge them into the project root's `.mcp.json` (the editor menu has already filled in the values in angle brackets):

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

- **Online and offline**: the available APIs are those in the running editor's type table, covering registered native bindings and compiled script types. The Host saves the last type table as a snapshot and reads it when the editor is not open; the first time offline with no snapshot, API queries return `DebugServer runtime type table is not available yet`.
- **Using it with UE's official MCP**: the soloAS Host covers AS APIs, script types, diagnostics and debugging; UE's `ModelContextProtocol` covers assets, scenes and other operations in the editor. Their ports and protocols have nothing to do with `27099`, and neither depends on the other.

## What MCP provides

- **Script types and project information, read only**: list the script types the editor has compiled, read the project, plugins, script roots and connection state, and read the compile diagnostics the editor pushes.
- **Project packaging tools**: use Developer Tools to read settings, precheck and run packaging, and, according to tool permissions, save packaging settings or request job cancellation.
- **Debugging**: read the call stack and variables while paused; set and clear breakpoints, continue and step, and evaluate expressions. These change breakpoints or execution state, and evaluation may have side effects, so it is not read only.
