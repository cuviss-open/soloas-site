# Changelog

## 0.2.1 · UE 5.7.4–5.8.4

- Supports UE 5.7.4 and 5.8.4.

### Fixes

- Fixed breakpoints inside lambda callbacks failing to stop in the corresponding callback frame.
- Fixed a possible editor crash when hot reloading a Blueprint parent. As documented, a Blueprint parent can be used without an explicit `import`.
- Fixed implementation classes not receiving updated default methods after changing a parent interface's default method and hot reloading within the same module.
- Fixed builds failing on name collisions when compiling the plugins from source on Windows with default Unity builds.

### Improvements

- MCP supports batch editing and explicit compile requests. If an AI assistant is interrupted, compilation can resume; it can also be resumed from **SoloAS → AI-assisted development** in the editor.

### VS Code extension

- The **soloAS** extension on the Visual Studio Code Marketplace is releasing alongside soloAS 0.2.1.
- Adds interface and lambda syntax support.
- With soloAS 0.2.1, VS Code can complete Blueprint parent members and interface methods and show their hover information.
- Diagnostics refresh after type information loads or a document is reopened; breakpoints in lambda callbacks stop in the correct call frame.

<!-- generated-release-heading:start -->
## 0.2.0 · UE 5.7.4–5.8.4
<!-- generated-release-heading:end -->

- Supports UE 5.7.4 and 5.8.4.

### Added

- Scripts can implement C++, AS and Blueprint interfaces; editor scripts can also declare interfaces for Blueprints to call and implement; packaging and precompilation of newly declared script interfaces are not yet supported.
- Script classes can inherit Blueprint parents and call functions or read and write properties on existing Blueprint objects; while a script class inherits a Blueprint, structural edits to that Blueprint are protected.
- Scripts can use Blueprint structs registered in project configuration.
- Scripts overriding native events can call the original parent implementation.
- Delegates and container algorithms support lambdas with explicit variable captures.
- Configure script delivery and output in Project Settings → Plugins → soloAS Packaging, and use the SoloAS menu to open those settings, UE packaging settings and the Project Launcher.
- Bytecode packaging can omit AS source and reduce startup compilation; semi-AOT can compile eligible script functions into the game to reduce virtual machine overhead.
- The command line and CI can use project settings and packaging profiles to check, run and inspect packaging; soloAS command-line packaging supports Win64.
- MCP lets AI query script types and project information and assist with debugging and packaging; the project connection configuration can be copied from the SoloAS menu.
- C++ toolchain tools can detect and select an available toolchain to help prepare C++ builds.
- The SoloAS menu supports Chinese and English.

### Upgrade note

- 0.2.0 supports UE 5.7.4 and 5.8.4. Users of UE 5.4.4, 5.5.4 or 5.6.1 should continue using 0.1.x, which will continue to receive fixes.

<!-- generated-release-heading:start -->
## 0.1.3 · UE 5.4.4–5.8.4
<!-- generated-release-heading:end -->

- Supports UE 5.4.4–5.8.4 so projects using these versions can use soloAS.
- Expanded script access to native UE plugin APIs, including TextureGraph and ChaosCloth, and aligned reference arguments and return values (matches UE-AS fork).
- StateTree can now be enabled as needed by the project instead of being required.
- The soloAS menu adds About soloAS, Check for updates, and one-click updating for easier version checks and updates.

### Fixes

- Fixed native function calls not passing reference and output arguments at the caller’s address and losing input values for non-const bare references, which could cause crashes.
- Fixed a possible editor crash on exit after exporting script documentation.
- Fixed Blueprint subclass overrides of native properties being replaced by script defaults when the script base class sets the same property in a default statement.
- Fixed old script modules accumulating when script files are deleted or restored and hot reload is repeated in the editor. Creating an object of a Blueprint subclass after its parent class is deleted no longer crashes and now applies defaults from remaining script ancestors.
- Fixed Blueprint subclass edits to inherited components and properties not appearing correctly on placed and spawned instances when a script Actor class sets components or properties with default. This now matches the UE-AS fork. Levels saved before the fix may contain old values; please recheck these properties in the level.
- Fixed possible loss of the Blueprint Designer or animation graph when scripting classes inherit from Widget or animation Blueprints.
- Fixed script class redirect recognition in the macOS editor (macOS only).
- Fixed project test settings failing to override plugin defaults.
- Fixed how script sources are placed during packaging to match the UE-AS fork.
- Fixed omitted non-empty FName default arguments on native functions being passed as empty names.
- Fixed native enum constants outside the signed 8-bit range not being exposed to scripts.
- Fixed output parameters, const references, default parameters, and reference returns of some native functions differing from their native declarations.
- Fixed some native interfaces, wildcard functions, and delegate parameters not being correctly available to scripts.
- Fixed some editor types not being discovered and bound.
- Fixed issues when recreating a deleted script class with the same name.
- Fixed new objects potentially being mistaken for old ones during hot reload.
- Fixed possible debug server crashes when querying function information after hot reload.
- Fixed StateTree script nodes potentially disappearing from the node list after compiling Blueprints or loading assets.

### Changes
- Plugin script roots are collected only from enabled plugins declaring `CanContainContent`; `Script` directories in plugins without that declaration are no longer loaded, matching the UE-AS fork.
- `System::SetTimer` now requires an explicit `bLooping` argument; add `true` or `false` to existing scripts, matching the UE-AS fork.
- Collision object query masks now use `int32` and the `ObjectTypesToQuery` field; scripts using the old `int64` constructor or Get/Set methods need adjustment, matching the UE-AS fork.
- `FInputActionValue` `*=` still modifies the original value, but the expression now returns a copy instead of a reference, matching the UE-AS fork.
- `InputModifier.ModifyRaw` is no longer declared const; scripts using the interface need adjustment, matching the UE-AS fork.

### Removed features
- Removed Blueprint quick call scanning, Full reload scripts, and Open log from the menu (extension feature, not kept for now).
- Assets with an empty engine version no longer trigger an automatic startup notice (redundant, not kept for now).
- Removed script unit isolation, automatic namespaces, and unit dependency rules (extension feature, not kept for now).
- Removed the old Blueprint import configuration (extension feature, not kept for now). Ordinary script Lambdas are unaffected.
- Removed the optional native property preservation configuration (extension feature, not kept for now).
- Removed the `Editor::ImportObjectText` editor scripting interface (redundant, not kept for now).
- Removed several internal interfaces for extension developers. Ordinary scripts are unaffected (extension feature, not kept for now).
- When a script class implements a C++ interface but does not override a function, calling that function through the interface now reports an error instead of running the C++ default implementation, matching the UE-AS fork.

## 0.1.2 · UE 5.8.4

2026-10-25

- Supports UE 5.8.4.
- Includes the latest UE-AS fork updates, including new math functions such as 64-bit integer rounding.
- Fixed editor settings for hiding functions.

## 0.1.1 · UE 5.8.3

2026-10-24

- First precompiled release: includes a Win64 package ready to use in Blueprint projects.
- Also includes source and debugging symbols packages, with SHA256SUMS verification.
- Packaging Win64 projects requires MSVC 14.44 and Windows SDK 10.0.22621.0.
