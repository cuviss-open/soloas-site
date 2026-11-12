# SoloAS menu

The editor's **SoloAS** menu provides common developer tools:

- **Packaging**: configure profiles, package and inspect the result; see [Packaging](packaging.md).
- **AI-assisted development**: copy the MCP configuration to connect an AI tool that supports MCP; see [AI-assisted development](ai-assisted.md).
- **[C++ Toolchain](requirements.md#c-toolchain)** (Windows only): inspect and select a toolchain, or install or uninstall the managed toolchain.

## Resave assets with empty engine version

Use this when loading an asset shows `Asset has been saved with empty engine version`, which is common after migrating a project from the UE-AS fork; you can also click **Fix in one click** in the notification. The action resaves project assets whose saved engine version is empty. When it finishes, the editor reports how many assets succeeded, failed, or were skipped.

## Fix assets affected by load-time rebinding

Use this when the editor reports `SoloAS deferred a script reload while assets were loading. Reload the affected assets.` The action reloads affected project assets from disk; unsaved assets and assets outside the project are skipped. When it finishes, the editor reports how many assets succeeded, failed, or were skipped.

## About soloAS

This lists the installed soloAS plugin versions. It also tells you whether the current UE version is supported.

## Check for updates

The editor checks online only when you click this action. If a newer version is available, you can start a one-click update; see [Updating soloAS](requirements.md#updating-soloas) for the steps and limitations.
