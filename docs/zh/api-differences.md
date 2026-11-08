# soloAS 最新版与 UE-AS fork 的 API 差异

本页概述 soloAS 最新版与 UE-AS fork 的 API 差异，并列出代表性例子。未提及的差异类别与 UE-AS fork 一致。

## 默认参数

**有什么不同：**省略下表中的参数时，soloAS 传入表中列出的值；UE-AS fork 传入空名称（`NAME_None`）。

**为什么：有意改进。**UE-AS fork 对这些默认值的处理有缺陷；soloAS 按原生声明的默认值传参。

**需要注意：**要让两边行为一致，请显式传入参数。

共 491 个函数；以下为例子。

```angelscript
VisualLogger::LogArrow(WorldContextObject, SegmentStart, SegmentEnd, Text);
// soloAS 收到的 CategoryName: FName("VisLogBP")
// UE-AS fork 收到的 CategoryName: NAME_None
```

| 函数 | 参数名 | soloAS 默认值 |
| --- | --- | --- |
| `AnimDatabaseFrameAttribute::FrameAttributeBoneSpeed` | `BoneName` | `FName("foot_l")` |
| `DrawDebug::MakeVisualLoggerDebugDrawer` | `Category` | `FName("LogDrawDebugLibrary")` |
| `LevelSnapshots::TakeLevelSnapshot` | `NewSnapshotName` | `FName("NewLevelSnapshot")` |
| `MusicClockComponent::CreateMetasoundDrivenMusicClock` | `MetasoundOuputPinName` | `FName("MIDI Clock")` |
| `UAnimGenControls::DrawDebugAngularVelocityControl` | `Tag` | `FName("AngularVelocityControl")` |

## 引擎插件提供的接口

原版 UE 默认安装包含更多配套插件，其接口可在 soloAS 中使用；所比较的 UE-AS fork 安装中没有这些插件，因此不算 API 差异。实际可用性取决于引擎安装及插件是否启用。

共 173 项接口；以下为例子。

- `EFabEnvironment`
- `FBifrostNodeInfo`
- `UBrowserBinding · static UClass UBrowserBinding::StaticClass()`
- `FMegascanMaterialPair · FMegascanMaterialPair& opAssign(FMegascanMaterialPair Other)`
- `UFabSettings · EFabEnvironment Environment`

## 加载时机（非 API 差异）

以下模块中的部分原生声明在两端完全相同，但 soloAS 作为项目插件初始化时这些模块已加载，因此可供脚本使用；UE-AS fork 在这些模块加载前就已初始化脚本绑定，所以用不到。声明和签名本身没有差异。

共 5 个模块；以下为例子。

- `AudioSynesthesiaEditor`
- `SoundCueTemplatesEditor`
- `TakeRecorderEditor`
- `TakeRecorderNamingTokens`
- `TakeRecorderSources`

## 原生调用行为

### UAvaShapeDynamicMeshBase::GetParametricMaterial

```cpp
const FAvaShapeParametricMaterial& UAvaShapeDynamicMeshBase::GetParametricMaterial(int32 InMeshIndex) const
```

**有什么不同：**GetParametricMaterial 在索引无效时返回值相同的默认对象，地址与 UE-AS fork 不同。

**为什么：**安装版引擎没有导出原函数，无法取得它的默认对象地址。

**需要注意：**有效索引保持原对象地址；无效索引的结果不适合用于跨实现的地址比较。

### UTG_BlueprintFunctionLibrary::RenderTextureGraph

```cpp
static const TArray<UTextureRenderTarget2D*>& UTG_BlueprintFunctionLibrary::RenderTextureGraph(UObject* WorldContextObject, UTextureGraphBase* InTextureGraph)
```

**有什么不同：**RenderTextureGraph 保留原函数的全部副作用；const& 声明与 UE-AS fork 一致，引用指向 soloAS 内部持有的数组副本。

**为什么：**安装版引擎没有导出能取得原数组引用的函数入口。

**需要注意：**每次调用各有独立副本，数组元素仍指向相同对象。普通编辑器帧结束前引用有效；commandlet 或引擎循环启动前仅保留至下一次调用。需要跨帧使用时应复制数组，复制后修改不影响原数组。

### UUserToolBoxFunctionLibrary::GetBrushById

```cpp
static const FSlateBrush& UUserToolBoxFunctionLibrary::GetBrushById(FString Name)
```

**有什么不同：**GetBrushById 在 UE-AS fork 中返回样式注册表内的 brush，或该类静态 DefaultBrush 的 const FSlateBrush&；soloAS 当前未导出该 AS 函数，声明也未对齐。

**为什么：**安装版引擎没有导出 GetBrushById、所属类和静态 DefaultBrush；原函数也不是内联函数。公开接口无法取得该函数返回的私有默认对象地址。

**需要注意：**GetBrushById 在 soloAS 的 AngelScript 中不可用；使用此调用的 UE-AS fork 脚本无法通过编译。

### UUserToolBoxFunctionLibrary::GetBrushByStyleAndId

```cpp
static const FSlateBrush& UUserToolBoxFunctionLibrary::GetBrushByStyleAndId(FName StyleName, FName Id)
```

**有什么不同：**GetBrushByStyleAndId 在 UE-AS fork 中返回样式注册表内的 brush，或该类静态 DefaultBrush 的 const FSlateBrush&；soloAS 当前未导出该 AS 函数，声明也未对齐。

**为什么：**安装版引擎没有导出 GetBrushByStyleAndId、所属类和静态 DefaultBrush；原函数也不是内联函数。公开接口无法取得该函数返回的私有默认对象地址。

**需要注意：**GetBrushByStyleAndId 在 soloAS 的 AngelScript 中不可用；使用此调用的 UE-AS fork 脚本无法通过编译。

[不同 UE 版本的适配差异](ue-version-differences.md)
