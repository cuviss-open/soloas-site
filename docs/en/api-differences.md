# API differences between the latest soloAS and the UE-AS fork

This page summarizes API differences between the latest soloAS and the UE-AS fork with representative examples. Areas not mentioned match the UE-AS fork.

## Default arguments

**Difference:** When a parameter below is omitted, soloAS passes the value listed in the table; the UE-AS fork passes an empty name (`NAME_None`).

**Why: Intentional improvement.** The UE-AS fork handles these defaults incorrectly; soloAS passes the defaults from the native declarations.

**What to do:** Pass the argument explicitly for consistent behavior across both implementations.

491 functions in total; examples are shown below.

```angelscript
VisualLogger::LogArrow(WorldContextObject, SegmentStart, SegmentEnd, Text);
// soloAS receives CategoryName: FName("VisLogBP")
// UE-AS fork receives CategoryName: NAME_None
```

| Function | Parameter | soloAS default |
| --- | --- | --- |
| `AnimDatabaseFrameAttribute::FrameAttributeBoneSpeed` | `BoneName` | `FName("foot_l")` |
| `DrawDebug::MakeVisualLoggerDebugDrawer` | `Category` | `FName("LogDrawDebugLibrary")` |
| `LevelSnapshots::TakeLevelSnapshot` | `NewSnapshotName` | `FName("NewLevelSnapshot")` |
| `MusicClockComponent::CreateMetasoundDrivenMusicClock` | `MetasoundOuputPinName` | `FName("MIDI Clock")` |
| `UAnimGenControls::DrawDebugAngularVelocityControl` | `Tag` | `FName("AngularVelocityControl")` |

## Interfaces supplied by engine plugins

A standard UE installation includes more bundled plugins whose APIs are available in soloAS; these plugins are absent from the compared UE-AS fork installation, so they are not API differences. Availability depends on the engine installation and whether the plugins are enabled.

173 interfaces in total; examples are shown below.

- `EFabEnvironment`
- `FBifrostNodeInfo`
- `UBrowserBinding · static UClass UBrowserBinding::StaticClass()`
- `FMegascanMaterialPair · FMegascanMaterialPair& opAssign(FMegascanMaterialPair Other)`
- `UFabSettings · EFabEnvironment Environment`

## Loading timing (not an API difference)

Some native declarations in the following modules are identical on both sides. These modules are already loaded when soloAS initializes as a project plugin, so the declarations are available to scripts; UE-AS fork initializes script bindings before these modules load, so they are unavailable there. The declarations and signatures themselves do not differ.

5 modules in total; examples are shown below.

- `AudioSynesthesiaEditor`
- `SoundCueTemplatesEditor`
- `TakeRecorderEditor`
- `TakeRecorderNamingTokens`
- `TakeRecorderSources`

## Native call behavior

### UAvaShapeDynamicMeshBase::GetParametricMaterial

```cpp
const FAvaShapeParametricMaterial& UAvaShapeDynamicMeshBase::GetParametricMaterial(int32 InMeshIndex) const
```

**Difference:** For an invalid index, GetParametricMaterial returns an equal-valued default object at a different address from UE-AS fork.

**Why:** The installed engine does not export the original function, so its default object address is unavailable.

**Impact:** Valid indices retain the original address; avoid comparing invalid-index result addresses across implementations.

### UTG_BlueprintFunctionLibrary::RenderTextureGraph

```cpp
static const TArray<UTextureRenderTarget2D*>& UTG_BlueprintFunctionLibrary::RenderTextureGraph(UObject* WorldContextObject, UTextureGraphBase* InTextureGraph)
```

**Difference:** RenderTextureGraph preserves all original side effects. Its const& declaration matches UE-AS fork; the reference points to a copy of the array held by soloAS.

**Why:** The installed engine does not export the function entry needed to obtain the original array reference.

**Impact:** Each call owns a separate copy containing the same objects. The reference lasts until the end of the ordinary editor frame, or until the next call in commandlets or before the engine loop starts. Copy the array for use across frames; modifying that copy does not affect the original array.

### UUserToolBoxFunctionLibrary::GetBrushById

```cpp
static const FSlateBrush& UUserToolBoxFunctionLibrary::GetBrushById(FString Name)
```

**Difference:** GetBrushById returns a const FSlateBrush& to a registered style brush or the class-static DefaultBrush in UE-AS fork. soloAS currently exports no AS declaration for this function.

**Why:** The installed engine exports neither GetBrushById, its owning class, nor the static DefaultBrush, and the function is not inline. Public interfaces cannot obtain the private default object address returned by this function.

**Impact:** GetBrushById is unavailable in soloAS AngelScript; UE-AS fork scripts containing this call cannot compile.

### UUserToolBoxFunctionLibrary::GetBrushByStyleAndId

```cpp
static const FSlateBrush& UUserToolBoxFunctionLibrary::GetBrushByStyleAndId(FName StyleName, FName Id)
```

**Difference:** GetBrushByStyleAndId returns a const FSlateBrush& to a registered style brush or the class-static DefaultBrush in UE-AS fork. soloAS currently exports no AS declaration for this function.

**Why:** The installed engine exports neither GetBrushByStyleAndId, its owning class, nor the static DefaultBrush, and the function is not inline. Public interfaces cannot obtain the private default object address returned by this function.

**Impact:** GetBrushByStyleAndId is unavailable in soloAS AngelScript; UE-AS fork scripts containing this call cannot compile.

[Adaptation differences across UE versions](ue-version-differences.md)
