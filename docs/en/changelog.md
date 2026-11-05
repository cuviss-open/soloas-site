# Changelog

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
