# Environment setup and quick start

## Environment setup

### Engine version

- Currently adapted to UE 5.8.4; the official Launcher build is recommended.
- A source-built engine (the same adapted tag) is expected to be functionally equivalent in theory but is not guaranteed.

### Operating systems

- Windows 11 x64 is the primary supported and validated platform; Windows 10 is expected to work in theory but is not guaranteed.
- macOS 15 or later is weakly supported: limited compile verification only, with no behavior guarantee.

### C++ toolchain

- With the prebuilt package, a Blueprint-only project can use it directly in the editor; see the release notes for packaging requirements.
- The source package needs a C++ project and the Visual Studio toolchain, and the project must be compiled after installing.

### Code editor

- VS Code, with Hazelight's Unreal Angelscript extension installed; see the [Hazelight documentation site](https://angelscript.hazelight.se).
- Set the workspace to the project's `Script` folder; completion, diagnostics, navigation, breakpoints, variables and continue are all available.
- Start the editor normally, without `-NoMessaging` or `-NoASDebugServer`, which turn off the DebugServer the extension uses.

## Quick start

1. **Create a project**: create a project with stock Unreal Engine.
2. **Copy the plugins**: x.x.x is the soloAS version and uex.x.x the supported UE version; download the latest from the [Releases](https://github.com/cuviss-open/soloAS/releases/latest) page, choosing one:
   - Prebuilt package (recommended): `soloAS-x.x.x-uex.x.x-win64.7z`; extract it into the project's `Plugins/` and it is ready to use. Windows 11 can extract it directly; Windows 10 needs 7-Zip installed first.
   - Source package: `soloAS-x.x.x-uex.x.x-source.zip` needs a C++ project and the Visual Studio toolchain; put it under `<Project>/Plugins/` as the "Plugin folders and dependencies" section below maps out.
   - Debug symbols: `soloAS-x.x.x-uex.x.x-win64-symbols.7z` is needed only to debug or read a crash stack; extract it over the same location.
3. **Generate and build** (when using the source package): close the editor, right-click the `.uproject` and choose **Generate Visual Studio project files**, open the `.sln`, build `<ProjectName>Editor` for Win64 Development, then open the `.uproject`.
4. **Enable the plugins**: `Angelscript` is enabled by default and enables `SoloASBridge` with it; when you use the GAS or Enhanced Input bindings, enable `AngelscriptGAS` or `AngelscriptEnhancedInput` in the editor's Plugins window and restart the editor when prompted.
5. **Write code**: you can then write AngelScript (`.as`) code under `<Project>/Script/`; changing a script does not need an editor restart. Your first script follows.

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

## Plugin folders and dependencies

The source package contains four plugins; put them under `<Project>/Plugins/` as this table shows, and extract the prebuilt package into `Plugins/` to use it directly:

| Folder in the source bundle | Folder under `<Project>/Plugins/` |
| --- | --- |
| `AngelscriptRuntime/` | `soloAS/AngelscriptRuntime/` |
| `SoloASBridge/` | `soloAS/SoloASBridge/` |
| `AngelscriptManualBindPlugins/AngelscriptGAS/` | `soloAS/AngelscriptManualBindPlugins/AngelscriptGAS/` |
| `AngelscriptManualBindPlugins/AngelscriptEnhancedInput/` | `soloAS/AngelscriptManualBindPlugins/AngelscriptEnhancedInput/` |

`soloAS/` is only a parent folder that keeps the plugins together; it is not a plugin. The Runtime source folder is `AngelscriptRuntime`; its descriptor is `Angelscript.uplugin`, so Unreal identifies it as `Angelscript`. You can keep the folder name or choose a custom one. The plugins can also go under `<UE>/Engine/Plugins/` to serve several projects of that engine, but a project-level install lets a project pin its own version. Do not install a plugin of the same name in both the engine and the project, and do not leave two copies in the project.

| Plugin | Plugins it depends on | Default state |
| --- | --- | --- |
| `Angelscript` (Runtime) | `SoloASBridge` | Enabled by default, and it enables the Bridge |
| `SoloASBridge` | `DataValidation`, `StateTree` | Off by default, enabled by the Runtime dependency |
| `AngelscriptGAS` | `GameplayAbilities`, `Angelscript` | Off by default; enable it when you use the GAS bindings |
| `AngelscriptEnhancedInput` | `EnhancedInput`, `Angelscript` | Off by default; enable it when you use the input bindings |

When you use the source package, or after changing a plugin's C++, close the editor, regenerate the project files and rebuild the Editor target, then start the editor. The equivalent command-line build:

```bat
"<UE>\Engine\Build\BatchFiles\Build.bat" <ProjectName>Editor Win64 Development -Project="<Project>\<ProjectName>.uproject" -NoUBA -NoMessaging
```

Common messages:

- Duplicate install: `The same version (v1) of plugin 'Angelscript' exists at '<first path>' and '<second path>' - second location will be ignored.`; remove the extra copy.
- Missing dependency: `This project requires the 'Angelscript' plugin, which has a missing dependency on the 'SoloASBridge' plugin.` followed by two more paragraphs, `Would you like to disable it?` and `If you do, you will no longer be able to open any assets created with it. If not, the application will close.`; check that the `SoloASBridge` folder is in the right place.
- Missing module: `Plugin 'Angelscript' failed to load because module 'AngelscriptCode' could not be found.  Please ensure the plugin is properly installed, otherwise consider disabling the plugin for this project.`; regenerate the project files and build the Editor.
- Mismatched version: `Plugin 'Angelscript' failed to load because module 'AngelscriptCode' does not appear to be compatible with the current version of the engine.  The plugin may need to be recompiled.`; recompile with the current engine.
