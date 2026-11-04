# Environment setup and quick start

## Environment setup

### Engine version

<!-- generated-engine-support:start -->
- Current adaptations: stock Unreal Engine 5.4.4, 5.5.4, 5.6.1, 5.7.4, and 5.8.4.
- The most recent supported version has the broadest validation coverage. Unlisted patches are not guaranteed to work.
<!-- generated-engine-support:end -->
- See [Adaptation Differences Across Unreal Engine Versions](ue-version-differences.md) for behavior that varies by engine version.
- A source-built engine (the same adapted tag) is expected to be functionally equivalent in theory but is not guaranteed.

### Operating systems

- Windows 11 x64 is the primary supported and validated platform; Windows 10 is expected to work in theory but is not guaranteed.
- macOS 15 or later is weakly supported: limited compile verification only, with no behavior guarantee.

### C++ toolchain

- With the prebuilt package, a Blueprint-only project can use it directly in the editor; see the release notes for packaging requirements.
- On Windows, the source package needs a C++ project and the Visual Studio toolchain, and the project must be compiled after installing. On macOS, use the Xcode toolchain required by the corresponding UE version; verification is limited to compilation.
- Use only English letters, numbers and common symbols in project paths. Avoid Chinese and other non-English characters, or Unreal Engine may fail to find files when compiling C++; this is an Unreal Engine and Visual Studio compiler limitation, unrelated to soloAS.

### Code editor

- VS Code, with Hazelight's Unreal Angelscript extension installed; see the [Hazelight documentation site](https://angelscript.hazelight.se).
- Set the workspace to the project's `Script` folder; completion, diagnostics, navigation, breakpoints, variables and continue are all available.
- Start the editor normally, without `-NoMessaging` or `-NoASDebugServer`, which turn off the DebugServer the extension uses.

## Quick start

1. **Create a project**: create a project with stock Unreal Engine.
2. **Copy the plugins**: download the latest package for your UE version from [Releases](https://github.com/cuviss-open/soloAS/releases/latest). Extract either the prebuilt package or the source package under the project's `Plugins/`; each produces `Plugins/soloAS/`. The debug symbols package is only needed to debug or read a crash stack; extract it to the same location, replacing files. Windows 11 can extract packages directly; Windows 10 needs 7-Zip installed first.
3. **Generate and build** (when using the source package on Windows): close the editor, right-click the `.uproject` and choose **Generate Visual Studio project files**, open the `.sln`, build `<ProjectName>Editor` for Win64 Development, then open the `.uproject`.
4. **Enable the plugins**: core scripting support and its required dependencies are enabled automatically; when you use the GAS or Enhanced Input bindings, enable `AngelscriptGAS` or `AngelscriptEnhancedInput` in the editor's Plugins window and restart the editor when prompted.
5. **Write code**: you can then write AngelScript (`.as`) code under `<Project>/Script/`; `<Project>` stands for your project folder, such as `MyProject/Script/`. Changing a script does not need an editor restart. Your first script follows.

<!-- generated-release-assets:start -->
### 0.1.3 release files

Verify files with `SHA256SUMS` from the release page. macOS uses the source package and has limited validation.

| File | UE versions | Platform | Size |
| --- | --- | --- | ---: |
| `soloAS-0.1.3-source.zip` | 5.4.4, 5.5.4, 5.6.1, 5.7.4, 5.8.4 | Win64, macOS | About 3.4 MB |
| `soloAS-0.1.3-ue5.4.4-win64-symbols.7z` | 5.4.4 | Win64 | About 418.5 MB |
| `soloAS-0.1.3-ue5.4.4-win64.7z` | 5.4.4 | Win64 | About 102.9 MB |
| `soloAS-0.1.3-ue5.5.4-win64-symbols.7z` | 5.5.4 | Win64 | About 463.6 MB |
| `soloAS-0.1.3-ue5.5.4-win64.7z` | 5.5.4 | Win64 | About 197.4 MB |
| `soloAS-0.1.3-ue5.6.1-win64-symbols.7z` | 5.6.1 | Win64 | About 499.6 MB |
| `soloAS-0.1.3-ue5.6.1-win64.7z` | 5.6.1 | Win64 | About 205.3 MB |
| `soloAS-0.1.3-ue5.7.4-win64-symbols.7z` | 5.7.4 | Win64 | About 522.9 MB |
| `soloAS-0.1.3-ue5.7.4-win64.7z` | 5.7.4 | Win64 | About 202.7 MB |
| `soloAS-0.1.3-ue5.8.4-win64-symbols.7z` | 5.8.4 | Win64 | About 567.6 MB |
| `soloAS-0.1.3-ue5.8.4-win64.7z` | 5.8.4 | Win64 | About 205.3 MB |
<!-- generated-release-assets:end -->

Save a script class that inherits `AActor` and prints text in `BeginPlay`. Once you place it in a level or spawn it from game logic, the game viewport shows "Hello from soloAS!" for a few seconds and the Output Log records the same text:

```angelscript
class AFirstScriptActor : AActor
{
    bool bHelloWorldShown = false;

    UFUNCTION(BlueprintOverride)
    void BeginPlay()
    {
        Print("Hello from soloAS!");
        bHelloWorldShown = true;
    }
}
```

## Updating soloAS

**Method 1: Update from the soloAS menu (Windows official release packages, from 0.1.3)**

On Windows, complete installations from an official prebuilt or source release package support menu updates. Keep the project open and retain the release manifest, which contains the checksum URL. A repository checkout, incomplete directory, or installation without the manifest must first be replaced manually with an official package. In the editor's [**SoloAS** menu](soloas-menu.md), choose **Check for updates**. When an update is available, click **Update (restart editor to finish)**. soloAS downloads and verifies the files automatically. Follow the prompt to restart the editor; the updater will replace the files and reopen the project. Configuration files you modified or added in the plugin folder are kept, and any conflicts are listed for you to resolve. If the update fails, the previous version is restored automatically. Installing to the engine folder may require administrator authorization; if you decline, update manually using Method 2. On macOS, use Method 2.

**Method 2: Replace the installation (for all versions)**

1. Close the editor. Read the [changelog](changelog.md) and the entry for your UE version in [Adaptation Differences Across Unreal Engine Versions](ue-version-differences.md).
2. Confirm whether the actual installation root is the project's `Plugins/soloAS/` or the target engine's `<UE>/Engine/Plugins/soloAS/`, and back up custom or added files in that directory. Replace the installation in the same location: remove the existing `soloAS/` directory, then download the new package from [Releases](https://github.com/cuviss-open/soloAS/releases/latest) and extract it under the same `Plugins/` directory. Do not overwrite old files, so files removed in the new version are not left behind. If the plugins sit directly under `Plugins/`, delete the `AngelscriptRuntime/`, `SoloASBridge/`, `AngelscriptGAS/`, and `AngelscriptEnhancedInput/` folders under `Plugins/` (or `<UE>/Engine/Plugins/`) before extracting the new package. Merge backed-up custom configuration with the new defaults. If the editor log reports duplicate installations, remove the extra copy as described under “Plugin folders and dependencies” below.
3. If you use the source package, rebuild your C++ project.
4. Open the editor, let scripts recompile automatically, and check the output log.

Your project's own configuration is stored in its `Config/` folder and is unaffected by plugin updates.

## Plugin folders and dependencies

Extracted under the project's `Plugins/`, both the prebuilt and source packages produce `Plugins/soloAS/`, with this directory structure:

| Directory | Plugin identity | Purpose |
| --- | --- | --- |
| `AngelscriptRuntime/` | `Angelscript` (Runtime) | AngelScript runtime and scripting support |
| `SoloASBridge/` | `SoloASBridge` | Integrates soloAS with Unreal Engine |
| `AngelscriptManualBindPlugins/AngelscriptGAS/` | `AngelscriptGAS` | GAS bindings |
| `AngelscriptManualBindPlugins/AngelscriptEnhancedInput/` | `AngelscriptEnhancedInput` | Enhanced Input bindings |

`soloAS/` is the release folder containing these plugins; it is not itself a plugin. The Runtime directory is `AngelscriptRuntime`; its descriptor is `Angelscript.uplugin`, so Unreal identifies it as `Angelscript`. `<UE>` in a path means the engine installation folder, such as `C:/Program Files/Epic Games/UE_5.8`. The plugins can also go under `<UE>/Engine/Plugins/` to serve several projects of that engine, but a project-level install lets a project pin its own version. Do not install a plugin of the same name in both the engine and the project, and do not leave two copies in the project.

The core scripting plugins enable their required dependencies automatically. GAS and Enhanced Input bindings are off by default; enable `AngelscriptGAS` or `AngelscriptEnhancedInput` in the Plugins window only when the project uses those features. `StateTree` is optional and only needs to be enabled when the project uses related functionality.

When you use the source package, or after changing a plugin's C++, close the editor, regenerate the project files and rebuild the Editor target, then start the editor. In the command, replace `<UE>`, `<ProjectName>` and `<Project>` with the engine folder, project name and project folder, such as `C:/UE_5.8`, `MyGame` and `D:/MyGame`. The equivalent command-line build:

```bat
"<UE>\Engine\Build\BatchFiles\Build.bat" <ProjectName>Editor Win64 Development -Project="<Project>\<ProjectName>.uproject" -NoUBA -NoMessaging
```

Common messages:

- Duplicate install: `The same version (v1) of plugin 'Angelscript' exists at '<first path>' and '<second path>' - second location will be ignored.`; remove the extra copy.
- Missing dependency: `This project requires the 'Angelscript' plugin, which has a missing dependency on the 'SoloASBridge' plugin.` followed by two more paragraphs, `Would you like to disable it?` and `If you do, you will no longer be able to open any assets created with it. If not, the application will close.`; check that the `SoloASBridge` folder is in the right place.
- Missing module: `Plugin 'Angelscript' failed to load because module 'AngelscriptCode' could not be found.  Please ensure the plugin is properly installed, otherwise consider disabling the plugin for this project.`; regenerate the project files and build the Editor.
- Mismatched version: `Plugin 'Angelscript' failed to load because module 'AngelscriptCode' does not appear to be compatible with the current version of the engine.  The plugin may need to be recompiled.`; recompile with the current engine.
