# API differences between the latest soloAS and the UE-AS fork

This page lists all API differences between the latest soloAS and the UE-AS fork. Areas not listed match the UE-AS fork.

## Default arguments

**Difference:** When a parameter below is omitted, soloAS passes the value listed in the table; the UE-AS fork passes an empty name (`NAME_None`).

**Why: Intentional improvement.** The UE-AS fork handles these defaults incorrectly; soloAS passes the defaults from the native declarations.

**What to do:** Pass the argument explicitly for consistent behavior across both implementations.

```angelscript
VisualLogger::LogArrow(WorldContextObject, SegmentStart, SegmentEnd, Text);
// soloAS receives CategoryName: FName("VisLogBP")
// UE-AS fork receives CategoryName: NAME_None
```

| Function | Parameter | soloAS default |
| --- | --- | --- |
| `AnimDatabaseFrameAttribute::FrameAttributeBoneSpeed` | `BoneName` | `FName("foot_l")` |
| `AnimDatabaseFrameAttribute::FrameAttributeContactCurve` | `BoneName` | `FName("ball_l")` |
| `AnimDatabaseFrameAttribute::FrameAttributeContactFrames` | `BoneName` | `FName("ball_l")` |
| `AnimDatabaseFrameAttribute::FrameAttributeContactRanges` | `BoneName` | `FName("ball_l")` |
| `AnimDatabaseFrameAttribute::FrameAttributeGaussianSmoothedRootTransform` | `RootLocationProjectionBoneName` | `FName("spine_02")` |
| `AnimDatabaseFrameAttribute::FrameAttributeGaussianSmoothedRootTransform` | `RootRotationProjectionBoneName` | `FName("pelvis")` |
| `AnimDatabaseFrameAttribute::FrameAttributeSavGolSmoothedRootTransform` | `RootLocationProjectionBoneName` | `FName("spine_02")` |
| `AnimDatabaseFrameAttribute::FrameAttributeSavGolSmoothedRootTransform` | `RootRotationProjectionBoneName` | `FName("pelvis")` |
| `DrawDebug::MakeVisualLoggerDebugDrawer` | `Category` | `FName("LogDrawDebugLibrary")` |
| `DrawDebug::MakeVisualLoggerDebugDrawerFromObject` | `Category` | `FName("LogDrawDebugLibrary")` |
| `LevelSnapshots::TakeLevelSnapshot` | `NewSnapshotName` | `FName("NewLevelSnapshot")` |
| `MusicClockComponent::CreateMetasoundDrivenMusicClock` | `MetasoundOuputPinName` | `FName("MIDI Clock")` |
| `UAnimGenControls::DrawDebugAngularVelocityControl` | `Tag` | `FName("AngularVelocityControl")` |
| `UAnimGenControls::DrawDebugDirectionControl` | `Tag` | `FName("DirectionControl")` |
| `UAnimGenControls::DrawDebugLinearVelocityControl` | `Tag` | `FName("LinearVelocityControl")` |
| `UAnimGenControls::DrawDebugLocationControl` | `Tag` | `FName("LocationControl")` |
| `UAnimGenControls::DrawDebugLocationTrajectoryControl` | `Tag` | `FName("LocationTrajectoryControl")` |
| `UAnimGenControls::DrawDebugNamedExclusiveDiscreteControl` | `Tag` | `FName("NamedExclusiveDiscreteControl")` |
| `UAnimGenControls::DrawDebugNamedInclusiveDiscreteControl` | `Tag` | `FName("NamedInclusiveDiscreteControl")` |
| `UAnimGenControls::DrawDebugNamedSparseControl` | `Tag` | `FName("NamedSparseControl")` |
| `UAnimGenControls::DrawDebugPoseControlFromPoseState` | `Tag` | `FName("PoseControl")` |
| `UAnimGenControls::DrawDebugRotationControl` | `Tag` | `FName("RotationControl")` |
| `UAnimGenControls::DrawDebugTrajectoryControl` | `Tag` | `FName("TrajectoryControl")` |
| `UAnimGenControls::FindInclusiveUnionControlElement` | `Tag` | `FName("InclusiveUnionControl")` |
| `UAnimGenControls::FrameAttributeDirectionDistanceFromControl` | `Tag` | `FName("DirectionControl")` |
| `UAnimGenControls::FrameAttributeEventDistanceFromControl` | `Tag` | `FName("EventControl")` |
| `UAnimGenControls::FrameAttributeLocationDistanceFromControl` | `Tag` | `FName("LocationControl")` |
| `UAnimGenControls::FrameAttributePoseDistanceFromControl` | `Tag` | `FName("PoseControl")` |
| `UAnimGenControls::FrameAttributeRotationDistanceFromControl` | `Tag` | `FName("RotationControl")` |
| `UAnimGenControls::FrameAttributeTrajectoryDistanceFromControl` | `Tag` | `FName("TrajectoryControl")` |
| `UAnimGenControls::FrameAttributeVelocityDistanceFromControl` | `Tag` | `FName("LinearVelocityControl")` |
| `UAnimGenControls::GetAngleControl` | `Tag` | `FName("AngleControl")` |
| `UAnimGenControls::GetAngleControlRadians` | `Tag` | `FName("AngleControl")` |
| `UAnimGenControls::GetAngularVelocityControl` | `Tag` | `FName("AngularVelocityControl")` |
| `UAnimGenControls::GetArrayControl` | `Tag` | `FName("ArrayControl")` |
| `UAnimGenControls::GetArrayControlNum` | `Tag` | `FName("ArrayControl")` |
| `UAnimGenControls::GetBitmaskControl` | `Tag` | `FName("BitmaskControl")` |
| `UAnimGenControls::GetBoolControl` | `Tag` | `FName("BoolControl")` |
| `UAnimGenControls::GetContinuousControl` | `Tag` | `FName("ContinuousControl")` |
| `UAnimGenControls::GetContinuousControlNum` | `Tag` | `FName("ContinuousControl")` |
| `UAnimGenControls::GetCountControl` | `Tag` | `FName("CountControl")` |
| `UAnimGenControls::GetDirectionControl` | `Tag` | `FName("DirectionControl")` |
| `UAnimGenControls::GetDirectionsStaticArrayControl` | `Tag` | `FName("DirectionsStaticArrayControl")` |
| `UAnimGenControls::GetDirectionsStaticArrayControlNum` | `Tag` | `FName("DirectionsStaticArrayControl")` |
| `UAnimGenControls::GetEitherControl` | `Tag` | `FName("EitherControl")` |
| `UAnimGenControls::GetEncodingControl` | `Tag` | `FName("EncodingControl")` |
| `UAnimGenControls::GetEnumControl` | `Tag` | `FName("EnumControl")` |
| `UAnimGenControls::GetEventControl` | `Tag` | `FName("EventControl")` |
| `UAnimGenControls::GetExclusiveDiscreteControl` | `Tag` | `FName("ExclusiveDiscreteControl")` |
| `UAnimGenControls::GetExclusiveUnionControl` | `Tag` | `FName("ExclusiveUnionControl")` |
| `UAnimGenControls::GetFloatControl` | `Tag` | `FName("FloatControl")` |
| `UAnimGenControls::GetInclusiveDiscreteControl` | `Tag` | `FName("InclusiveDiscreteControl")` |
| `UAnimGenControls::GetInclusiveDiscreteControlNum` | `Tag` | `FName("InclusiveDiscreteControl")` |
| `UAnimGenControls::GetInclusiveUnionControl` | `Tag` | `FName("InclusiveUnionControl")` |
| `UAnimGenControls::GetInclusiveUnionControlNum` | `Tag` | `FName("InclusiveUnionControl")` |
| `UAnimGenControls::GetInclusiveUnionControlToArrays` | `Tag` | `FName("InclusiveUnionControl")` |
| `UAnimGenControls::GetLinearVelocitiesStaticArrayControl` | `Tag` | `FName("LinearVelocitiesStaticArrayControl")` |
| `UAnimGenControls::GetLinearVelocitiesStaticArrayControlNum` | `Tag` | `FName("LinearVelocitiesStaticArrayControl")` |
| `UAnimGenControls::GetLinearVelocityControl` | `Tag` | `FName("LinearVelocityControl")` |
| `UAnimGenControls::GetLocationControl` | `Tag` | `FName("LocationControl")` |
| `UAnimGenControls::GetLocationTrajectoryControl` | `Tag` | `FName("LocationTrajectoryControl")` |
| `UAnimGenControls::GetLocationTrajectoryControlNum` | `Tag` | `FName("LocationTrajectoryControl")` |
| `UAnimGenControls::GetLocationsStaticArrayControl` | `Tag` | `FName("LocationsStaticArrayControl")` |
| `UAnimGenControls::GetLocationsStaticArrayControlNum` | `Tag` | `FName("LocationsStaticArrayControl")` |
| `UAnimGenControls::GetMapControl` | `Tag` | `FName("MapControl")` |
| `UAnimGenControls::GetMapControlNum` | `Tag` | `FName("MapControl")` |
| `UAnimGenControls::GetMapControlToArrays` | `Tag` | `FName("MapControl")` |
| `UAnimGenControls::GetNamedExclusiveDiscreteControl` | `Tag` | `FName("NamedExclusiveDiscreteControl")` |
| `UAnimGenControls::GetNamedInclusiveDiscreteControl` | `Tag` | `FName("NamedInclusiveDiscreteControl")` |
| `UAnimGenControls::GetNamedInclusiveDiscreteControlNum` | `Tag` | `FName("NamedInclusiveDiscreteControl")` |
| `UAnimGenControls::GetNamedSparseControl` | `Tag` | `FName("NamedSparseControl")` |
| `UAnimGenControls::GetNamedSparseControlNum` | `Tag` | `FName("NamedSparseControl")` |
| `UAnimGenControls::GetNullControl` | `Tag` | `FName("NullControl")` |
| `UAnimGenControls::GetOptionalControl` | `Tag` | `FName("OptionalControl")` |
| `UAnimGenControls::GetPairControl` | `Tag` | `FName("PairControl")` |
| `UAnimGenControls::GetPoseControl` | `Tag` | `FName("PoseControl")` |
| `UAnimGenControls::GetPoseControlNum` | `Tag` | `FName("PoseControl")` |
| `UAnimGenControls::GetRotationControl` | `Tag` | `FName("RotationControl")` |
| `UAnimGenControls::GetRotationControlAsQuat` | `Tag` | `FName("RotationControl")` |
| `UAnimGenControls::GetScaleControl` | `Tag` | `FName("ScaleControl")` |
| `UAnimGenControls::GetSetControl` | `Tag` | `FName("SetControl")` |
| `UAnimGenControls::GetSetControlNum` | `Tag` | `FName("SetControl")` |
| `UAnimGenControls::GetSetControlToArray` | `Tag` | `FName("SetControl")` |
| `UAnimGenControls::GetSparseControl` | `Tag` | `FName("SparseControl")` |
| `UAnimGenControls::GetSparseControlNum` | `Tag` | `FName("SparseControl")` |
| `UAnimGenControls::GetStaticArrayControl` | `Tag` | `FName("StaticArrayControl")` |
| `UAnimGenControls::GetStaticArrayControlNum` | `Tag` | `FName("StaticArrayControl")` |
| `UAnimGenControls::GetStructControl` | `Tag` | `FName("StructControl")` |
| `UAnimGenControls::GetStructControlElement` | `Tag` | `FName("StructControl")` |
| `UAnimGenControls::GetStructControlNum` | `Tag` | `FName("StructControl")` |
| `UAnimGenControls::GetStructControlToArrays` | `Tag` | `FName("StructControl")` |
| `UAnimGenControls::GetTimeControl` | `Tag` | `FName("TimeControl")` |
| `UAnimGenControls::GetTrajectoryControl` | `Tag` | `FName("TrajectoryControl")` |
| `UAnimGenControls::GetTrajectoryControlNum` | `Tag` | `FName("TrajectoryControl")` |
| `UAnimGenControls::GetTransformControl` | `Tag` | `FName("TransformControl")` |
| `UAnimGenControls::MakeAngleControl` | `Tag` | `FName("AngleControl")` |
| `UAnimGenControls::MakeAngleControlRadians` | `Tag` | `FName("AngleControl")` |
| `UAnimGenControls::MakeAngularVelocityControl` | `Tag` | `FName("AngularVelocityControl")` |
| `UAnimGenControls::MakeAngularVelocityControlSet` | `Tag` | `FName("AngularVelocityControl")` |
| `UAnimGenControls::MakeArrayControl` | `Tag` | `FName("ArrayControl")` |
| `UAnimGenControls::MakeBitmaskControl` | `Tag` | `FName("BitmaskControl")` |
| `UAnimGenControls::MakeBoneGlobalDirectionAtNearestFramesControlSetFromDatabase` | `Tag` | `FName("DirectionControl")` |
| `UAnimGenControls::MakeBoneGlobalDirectionAtNearestFramesControlSetFromDatabaseBoneName` | `Tag` | `FName("DirectionControl")` |
| `UAnimGenControls::MakeBoneGlobalDirectionControlSet` | `Tag` | `FName("DirectionControl")` |
| `UAnimGenControls::MakeBoneGlobalDirectionControlSetFromName` | `Tag` | `FName("DirectionControl")` |
| `UAnimGenControls::MakeBoneGlobalLocationAtNearestFramesControlSetFromDatabase` | `Tag` | `FName("LocationControl")` |
| `UAnimGenControls::MakeBoneGlobalLocationAtNearestFramesControlSetFromDatabaseBoneName` | `Tag` | `FName("LocationControl")` |
| `UAnimGenControls::MakeBoneGlobalLocationControlSet` | `Tag` | `FName("LocationControl")` |
| `UAnimGenControls::MakeBoneGlobalLocationControlSetFromName` | `Tag` | `FName("LocationControl")` |
| `UAnimGenControls::MakeBoolControl` | `Tag` | `FName("BoolControl")` |
| `UAnimGenControls::MakeBoolControlSet` | `Tag` | `FName("BoolControl")` |
| `UAnimGenControls::MakeBoolControlSetFromActiveRanges` | `Tag` | `FName("BoolControl")` |
| `UAnimGenControls::MakeBoolControlSetFromAnimNotifyState` | `Tag` | `FName("BoolControl")` |
| `UAnimGenControls::MakeBoolControlSetFromConstant` | `Tag` | `FName("BoolControl")` |
| `UAnimGenControls::MakeBoolControlSetFromMirrored` | `Tag` | `FName("BoolControl")` |
| `UAnimGenControls::MakeBoolControlSetFromNotMirrored` | `Tag` | `FName("BoolControl")` |
| `UAnimGenControls::MakeContinuousControl` | `Tag` | `FName("ContinuousControl")` |
| `UAnimGenControls::MakeCountControl` | `Tag` | `FName("CountControl")` |
| `UAnimGenControls::MakeDirectionControl` | `Tag` | `FName("DirectionControl")` |
| `UAnimGenControls::MakeDirectionControlSet` | `Tag` | `FName("DirectionControl")` |
| `UAnimGenControls::MakeDirectionsStaticArrayControl` | `Tag` | `FName("DirectionsStaticArrayControl")` |
| `UAnimGenControls::MakeEitherAControl` | `Tag` | `FName("EitherControl")` |
| `UAnimGenControls::MakeEitherBControl` | `Tag` | `FName("EitherControl")` |
| `UAnimGenControls::MakeEitherControl` | `Tag` | `FName("EitherControl")` |
| `UAnimGenControls::MakeEmptyInclusiveUnionControlSet` | `Tag` | `FName("InclusiveUnionControl")` |
| `UAnimGenControls::MakeEncodingControl` | `Tag` | `FName("EncodingControl")` |
| `UAnimGenControls::MakeEncodingControlSet` | `Tag` | `FName("EncodingControl")` |
| `UAnimGenControls::MakeEnumControl` | `Tag` | `FName("EnumControl")` |
| `UAnimGenControls::MakeEnumControlSet` | `Tag` | `FName("EnumControl")` |
| `UAnimGenControls::MakeEventControl` | `Tag` | `FName("EventControl")` |
| `UAnimGenControls::MakeEventControlFromPoseState` | `Tag` | `FName("EventControl")` |
| `UAnimGenControls::MakeEventControlSet` | `Tag` | `FName("EventControl")` |
| `UAnimGenControls::MakeExclusiveDiscreteControl` | `Tag` | `FName("ExclusiveDiscreteControl")` |
| `UAnimGenControls::MakeExclusiveDiscreteControlSetFromConstant` | `Tag` | `FName("ExclusiveDiscreteControl")` |
| `UAnimGenControls::MakeExclusiveUnionControl` | `Tag` | `FName("ExclusiveUnionControl")` |
| `UAnimGenControls::MakeExclusiveUnionControlSet` | `Tag` | `FName("ExclusiveUnionControl")` |
| `UAnimGenControls::MakeFloatControl` | `Tag` | `FName("FloatControl")` |
| `UAnimGenControls::MakeFloatControlSet` | `Tag` | `FName("FloatControl")` |
| `UAnimGenControls::MakeFutureRootDirectionControlSetFromDatabase` | `Tag` | `FName("DirectionControl")` |
| `UAnimGenControls::MakeFutureRootLinearVelocityControlSetFromDatabase` | `Tag` | `FName("LinearVelocityControl")` |
| `UAnimGenControls::MakeInclusiveDiscreteControl` | `Tag` | `FName("InclusiveDiscreteControl")` |
| `UAnimGenControls::MakeInclusiveUnionControl` | `Tag` | `FName("InclusiveUnionControl")` |
| `UAnimGenControls::MakeInclusiveUnionControlFromArrays` | `Tag` | `FName("InclusiveUnionControl")` |
| `UAnimGenControls::MakeInclusiveUnionControlSet` | `Tag` | `FName("InclusiveUnionControl")` |
| `UAnimGenControls::MakeLinearVelocitiesStaticArrayControl` | `Tag` | `FName("LinearVelocitiesStaticArrayControl")` |
| `UAnimGenControls::MakeLinearVelocityControl` | `Tag` | `FName("LinearVelocityControl")` |
| `UAnimGenControls::MakeLinearVelocityControlSet` | `Tag` | `FName("LinearVelocityControl")` |
| `UAnimGenControls::MakeLocationControl` | `Tag` | `FName("LocationControl")` |
| `UAnimGenControls::MakeLocationControlSet` | `Tag` | `FName("LocationControl")` |
| `UAnimGenControls::MakeLocationTrajectoryControl` | `Tag` | `FName("LocationTrajectoryControl")` |
| `UAnimGenControls::MakeLocationTrajectoryControlFromTransformTrajectory` | `Tag` | `FName("LocationTrajectoryControl")` |
| `UAnimGenControls::MakeLocationTrajectoryControlSet` | `Tag` | `FName("LocationTrajectoryControl")` |
| `UAnimGenControls::MakeLocationTrajectoryControlSetFromDatabase` | `Tag` | `FName("LocationTrajectoryControl")` |
| `UAnimGenControls::MakeLocationsStaticArrayControl` | `Tag` | `FName("LocationsStaticArrayControl")` |
| `UAnimGenControls::MakeLookAtTrajectoryControlSetFromDatabase` | `Tag` | `FName("TrajectoryControl")` |
| `UAnimGenControls::MakeMapControl` | `Tag` | `FName("MapControl")` |
| `UAnimGenControls::MakeMapControlFromArrays` | `Tag` | `FName("MapControl")` |
| `UAnimGenControls::MakeNamedExclusiveDiscreteControl` | `Tag` | `FName("NamedExclusiveDiscreteControl")` |
| `UAnimGenControls::MakeNamedExclusiveDiscreteControlSetFromAnimNotifyStates` | `Tag` | `FName("NamedExclusiveDiscreteControl")` |
| `UAnimGenControls::MakeNamedExclusiveDiscreteControlSetFromFrameRanges` | `Tag` | `FName("NamedExclusiveDiscreteControl")` |
| `UAnimGenControls::MakeNamedInclusiveDiscreteControl` | `Tag` | `FName("NamedInclusiveDiscreteControl")` |
| `UAnimGenControls::MakeNamedInclusiveDiscreteControlSetFromAnimNotifyStates` | `Tag` | `FName("NamedInclusiveDiscreteControl")` |
| `UAnimGenControls::MakeNamedInclusiveDiscreteControlSetFromFrameRanges` | `Tag` | `FName("NamedInclusiveDiscreteControl")` |
| `UAnimGenControls::MakeNamedSparseControl` | `Tag` | `FName("NamedSparseControl")` |
| `UAnimGenControls::MakeNamedSparseControlSetFromFrameRanges` | `Tag` | `FName("NamedSparseControl")` |
| `UAnimGenControls::MakeNullControl` | `Tag` | `FName("NullControl")` |
| `UAnimGenControls::MakeNullControlSet` | `Tag` | `FName("NullControl")` |
| `UAnimGenControls::MakeOptionalControl` | `Tag` | `FName("OptionalControl")` |
| `UAnimGenControls::MakeOptionalControlOnCondition` | `Tag` | `FName("OptionalControl")` |
| `UAnimGenControls::MakeOptionalControlSet` | `Tag` | `FName("OptionalControl")` |
| `UAnimGenControls::MakeOptionalNullControl` | `Tag` | `FName("OptionalControl")` |
| `UAnimGenControls::MakeOptionalNullControlSet` | `Tag` | `FName("OptionalControl")` |
| `UAnimGenControls::MakeOptionalValidControl` | `Tag` | `FName("OptionalControl")` |
| `UAnimGenControls::MakeOptionalValidControlSet` | `Tag` | `FName("OptionalControl")` |
| `UAnimGenControls::MakePairControl` | `Tag` | `FName("PairControl")` |
| `UAnimGenControls::MakePoseControl` | `Tag` | `FName("PoseControl")` |
| `UAnimGenControls::MakePoseControlFromPoseState` | `Tag` | `FName("PoseControl")` |
| `UAnimGenControls::MakePoseControlSet` | `Tag` | `FName("PoseControl")` |
| `UAnimGenControls::MakePoseControlSetFromDatabase` | `Tag` | `FName("PoseControl")` |
| `UAnimGenControls::MakeRootAngularVelocityControlSetFromDatabase` | `Tag` | `FName("AngularVelocityControl")` |
| `UAnimGenControls::MakeRootDirectionAtRangeEndControlSetFromDatabase` | `Tag` | `FName("DirectionControl")` |
| `UAnimGenControls::MakeRootLinearVelocityControlSetFromDatabase` | `Tag` | `FName("LinearVelocityControl")` |
| `UAnimGenControls::MakeRootLocationAtRangeEndControlSetFromDatabase` | `Tag` | `FName("LocationControl")` |
| `UAnimGenControls::MakeRotationControl` | `Tag` | `FName("RotationControl")` |
| `UAnimGenControls::MakeRotationControlFromQuat` | `Tag` | `FName("RotationControl")` |
| `UAnimGenControls::MakeRotationControlSet` | `Tag` | `FName("RotationControl")` |
| `UAnimGenControls::MakeScaleControl` | `Tag` | `FName("ScaleControl")` |
| `UAnimGenControls::MakeSetControl` | `Tag` | `FName("SetControl")` |
| `UAnimGenControls::MakeSetControlFromArray` | `Tag` | `FName("SetControl")` |
| `UAnimGenControls::MakeSetControlSetFromArray` | `Tag` | `FName("SetControl")` |
| `UAnimGenControls::MakeSparseControl` | `Tag` | `FName("SparseControl")` |
| `UAnimGenControls::MakeStaticArrayControl` | `Tag` | `FName("StaticArrayControl")` |
| `UAnimGenControls::MakeStructControl` | `Tag` | `FName("StructControl")` |
| `UAnimGenControls::MakeStructControlFromArrays` | `Tag` | `FName("StructControl")` |
| `UAnimGenControls::MakeStructControlSet` | `Tag` | `FName("StructControl")` |
| `UAnimGenControls::MakeTimeControl` | `Tag` | `FName("TimeControl")` |
| `UAnimGenControls::MakeTimeControlSet` | `Tag` | `FName("TimeControl")` |
| `UAnimGenControls::MakeTimeUntilNearestAnimNotifyControlSet` | `Tag` | `FName("TimeControl")` |
| `UAnimGenControls::MakeTrajectoryControl` | `Tag` | `FName("TrajectoryControl")` |
| `UAnimGenControls::MakeTrajectoryControlFromTransformTrajectory` | `Tag` | `FName("TrajectoryControl")` |
| `UAnimGenControls::MakeTrajectoryControlSet` | `Tag` | `FName("TrajectoryControl")` |
| `UAnimGenControls::MakeTrajectoryControlSetFromDatabase` | `Tag` | `FName("TrajectoryControl")` |
| `UAnimGenControls::MakeTransformControl` | `Tag` | `FName("TransformControl")` |
| `UAnimGenControls::SpecifyAngleControl` | `Tag` | `FName("AngleControl")` |
| `UAnimGenControls::SpecifyAngularVelocityControl` | `Tag` | `FName("AngularVelocityControl")` |
| `UAnimGenControls::SpecifyArrayControl` | `Tag` | `FName("ArrayControl")` |
| `UAnimGenControls::SpecifyBitmaskControl` | `Tag` | `FName("BitmaskControl")` |
| `UAnimGenControls::SpecifyBoolControl` | `Tag` | `FName("BoolControl")` |
| `UAnimGenControls::SpecifyContinuousControl` | `Tag` | `FName("ContinuousControl")` |
| `UAnimGenControls::SpecifyCountControl` | `Tag` | `FName("CountControl")` |
| `UAnimGenControls::SpecifyDirectionControl` | `Tag` | `FName("DirectionControl")` |
| `UAnimGenControls::SpecifyDirectionsStaticArrayControl` | `Tag` | `FName("DirectionsStaticArrayControl")` |
| `UAnimGenControls::SpecifyEitherControl` | `Tag` | `FName("EitherControl")` |
| `UAnimGenControls::SpecifyEncodingControl` | `Tag` | `FName("EncodingControl")` |
| `UAnimGenControls::SpecifyEnumControl` | `Tag` | `FName("EnumControl")` |
| `UAnimGenControls::SpecifyEventControl` | `Tag` | `FName("EventControl")` |
| `UAnimGenControls::SpecifyExclusiveDiscreteControl` | `Tag` | `FName("ExclusiveDiscreteControl")` |
| `UAnimGenControls::SpecifyExclusiveUnionControl` | `Tag` | `FName("ExclusiveUnionControl")` |
| `UAnimGenControls::SpecifyExclusiveUnionControlFromArrays` | `Tag` | `FName("ExclusiveUnionControl")` |
| `UAnimGenControls::SpecifyFloatControl` | `Tag` | `FName("FloatControl")` |
| `UAnimGenControls::SpecifyInclusiveDiscreteControl` | `Tag` | `FName("InclusiveDiscreteControl")` |
| `UAnimGenControls::SpecifyInclusiveUnionControl` | `Tag` | `FName("InclusiveUnionControl")` |
| `UAnimGenControls::SpecifyInclusiveUnionControlFromArrays` | `Tag` | `FName("InclusiveUnionControl")` |
| `UAnimGenControls::SpecifyLinearVelocitiesStaticArrayControl` | `Tag` | `FName("LinearVelocitiesStaticArrayControl")` |
| `UAnimGenControls::SpecifyLinearVelocityControl` | `Tag` | `FName("LinearVelocityControl")` |
| `UAnimGenControls::SpecifyLocationControl` | `Tag` | `FName("LocationControl")` |
| `UAnimGenControls::SpecifyLocationTrajectoryControl` | `Tag` | `FName("LocationTrajectoryControl")` |
| `UAnimGenControls::SpecifyLocationsStaticArrayControl` | `Tag` | `FName("LocationsStaticArrayControl")` |
| `UAnimGenControls::SpecifyMapControl` | `Tag` | `FName("MapControl")` |
| `UAnimGenControls::SpecifyNamedExclusiveDiscreteControl` | `Tag` | `FName("NamedExclusiveDiscreteControl")` |
| `UAnimGenControls::SpecifyNamedInclusiveDiscreteControl` | `Tag` | `FName("NamedInclusiveDiscreteControl")` |
| `UAnimGenControls::SpecifyNamedSparseControl` | `Tag` | `FName("NamedSparseControl")` |
| `UAnimGenControls::SpecifyNullControl` | `Tag` | `FName("NullControl")` |
| `UAnimGenControls::SpecifyOptionalControl` | `Tag` | `FName("OptionalControl")` |
| `UAnimGenControls::SpecifyPairControl` | `Tag` | `FName("PairControl")` |
| `UAnimGenControls::SpecifyPoseControl` | `Tag` | `FName("PoseControl")` |
| `UAnimGenControls::SpecifyRotationControl` | `Tag` | `FName("RotationControl")` |
| `UAnimGenControls::SpecifyScaleControl` | `Tag` | `FName("ScaleControl")` |
| `UAnimGenControls::SpecifySetControl` | `Tag` | `FName("SetControl")` |
| `UAnimGenControls::SpecifySparseControl` | `Tag` | `FName("SparseControl")` |
| `UAnimGenControls::SpecifyStaticArrayControl` | `Tag` | `FName("StaticArrayControl")` |
| `UAnimGenControls::SpecifyStructControl` | `Tag` | `FName("StructControl")` |
| `UAnimGenControls::SpecifyStructControlFromArrays` | `Tag` | `FName("StructControl")` |
| `UAnimGenControls::SpecifyTimeControl` | `Tag` | `FName("TimeControl")` |
| `UAnimGenControls::SpecifyTrajectoryControl` | `Tag` | `FName("TrajectoryControl")` |
| `UAnimGenControls::SpecifyTransformControl` | `Tag` | `FName("TransformControl")` |
| `UAnimGenControls::SwitchOnHasInclusiveUnionControlElement` | `Tag` | `FName("InclusiveUnionControl")` |
| `ULearningAgentsActions::GetContinuousActionNum` | `Tag` | `FName("ContinuousAction")` |
| `ULearningAgentsActions::GetEitherAction` | `Tag` | `FName("EitherAction")` |
| `ULearningAgentsActions::GetEncodingAction` | `Tag` | `FName("EncodingAction")` |
| `ULearningAgentsActions::GetExclusiveUnionAction` | `Tag` | `FName("ExclusiveUnionAction")` |
| `ULearningAgentsActions::GetInclusiveDiscreteActionNum` | `Tag` | `FName("DiscreteInclusiveAction")` |
| `ULearningAgentsActions::GetInclusiveUnionAction` | `Tag` | `FName("InclusiveUnionAction")` |
| `ULearningAgentsActions::GetInclusiveUnionActionNum` | `Tag` | `FName("InclusiveUnionAction")` |
| `ULearningAgentsActions::GetInclusiveUnionActionToArrays` | `Tag` | `FName("InclusiveUnionAction")` |
| `ULearningAgentsActions::GetNamedInclusiveDiscreteActionNum` | `Tag` | `FName("NamedDiscreteInclusiveAction")` |
| `ULearningAgentsActions::GetNullAction` | `Tag` | `FName("NullAction")` |
| `ULearningAgentsActions::GetOptionalAction` | `Tag` | `FName("OptionalAction")` |
| `ULearningAgentsActions::GetPairAction` | `Tag` | `FName("PairAction")` |
| `ULearningAgentsActions::GetStaticArrayAction` | `Tag` | `FName("StaticArrayAction")` |
| `ULearningAgentsActions::GetStaticArrayActionNum` | `Tag` | `FName("StaticArrayAction")` |
| `ULearningAgentsActions::GetStructAction` | `Tag` | `FName("StructAction")` |
| `ULearningAgentsActions::GetStructActionElement` | `Tag` | `FName("StructAction")` |
| `ULearningAgentsActions::GetStructActionNum` | `Tag` | `FName("StructAction")` |
| `ULearningAgentsActions::GetStructActionToArrays` | `Tag` | `FName("StructAction")` |
| `ULearningAgentsActions::MakeAngleActionModifier` | `Tag` | `FName("AngleAction")` |
| `ULearningAgentsActions::MakeAngleActionModifierRadians` | `Tag` | `FName("AngleAction")` |
| `ULearningAgentsActions::MakeBitmaskActionModifier` | `Tag` | `FName("BitmaskAction")` |
| `ULearningAgentsActions::MakeBoolActionModifier` | `Tag` | `FName("BoolAction")` |
| `ULearningAgentsActions::MakeContinuousActionModifier` | `Tag` | `FName("ContinuousAction")` |
| `ULearningAgentsActions::MakeDirectionActionModifier` | `Tag` | `FName("DirectionAction")` |
| `ULearningAgentsActions::MakeEitherAAction` | `Tag` | `FName("EitherAction")` |
| `ULearningAgentsActions::MakeEitherAction` | `Tag` | `FName("EitherAction")` |
| `ULearningAgentsActions::MakeEitherActionModifier` | `Tag` | `FName("EitherAction")` |
| `ULearningAgentsActions::MakeEitherBAction` | `Tag` | `FName("EitherAction")` |
| `ULearningAgentsActions::MakeEncodingAction` | `Tag` | `FName("EncodingAction")` |
| `ULearningAgentsActions::MakeEncodingActionModifier` | `Tag` | `FName("EncodingAction")` |
| `ULearningAgentsActions::MakeEnumActionModifier` | `Tag` | `FName("EnumAction")` |
| `ULearningAgentsActions::MakeExclusiveDiscreteActionModifier` | `Tag` | `FName("DiscreteExclusiveAction")` |
| `ULearningAgentsActions::MakeExclusiveUnionAction` | `Tag` | `FName("ExclusiveUnionAction")` |
| `ULearningAgentsActions::MakeExclusiveUnionActionModifier` | `Tag` | `FName("ExclusiveUnionAction")` |
| `ULearningAgentsActions::MakeExclusiveUnionActionModifierFromArrays` | `Tag` | `FName("ExclusiveUnionAction")` |
| `ULearningAgentsActions::MakeFloatActionModifier` | `Tag` | `FName("FloatAction")` |
| `ULearningAgentsActions::MakeInclusiveDiscreteActionModifier` | `Tag` | `FName("DiscreteInclusiveAction")` |
| `ULearningAgentsActions::MakeInclusiveUnionAction` | `Tag` | `FName("InclusiveUnionAction")` |
| `ULearningAgentsActions::MakeInclusiveUnionActionFromArrays` | `Tag` | `FName("InclusiveUnionAction")` |
| `ULearningAgentsActions::MakeInclusiveUnionActionModifier` | `Tag` | `FName("InclusiveUnionAction")` |
| `ULearningAgentsActions::MakeInclusiveUnionActionModifierFromArrays` | `Tag` | `FName("InclusiveUnionAction")` |
| `ULearningAgentsActions::MakeLocationActionModifier` | `Tag` | `FName("LocationAction")` |
| `ULearningAgentsActions::MakeNamedExclusiveDiscreteActionModifier` | `Tag` | `FName("NamedDiscreteExclusiveAction")` |
| `ULearningAgentsActions::MakeNamedInclusiveDiscreteActionModifier` | `Tag` | `FName("NamedDiscreteInclusiveAction")` |
| `ULearningAgentsActions::MakeNullAction` | `Tag` | `FName("NullAction")` |
| `ULearningAgentsActions::MakeNullActionModifier` | `Tag` | `FName("NullAction")` |
| `ULearningAgentsActions::MakeOptionalAction` | `Tag` | `FName("OptionalAction")` |
| `ULearningAgentsActions::MakeOptionalActionModifier` | `Tag` | `FName("OptionalAction")` |
| `ULearningAgentsActions::MakeOptionalNullAction` | `Tag` | `FName("OptionalAction")` |
| `ULearningAgentsActions::MakeOptionalValidAction` | `Tag` | `FName("OptionalAction")` |
| `ULearningAgentsActions::MakePairAction` | `Tag` | `FName("PairAction")` |
| `ULearningAgentsActions::MakePairActionModifier` | `Tag` | `FName("PairAction")` |
| `ULearningAgentsActions::MakeScaleActionModifier` | `Tag` | `FName("ScaleAction")` |
| `ULearningAgentsActions::MakeStaticArrayAction` | `Tag` | `FName("StaticArrayAction")` |
| `ULearningAgentsActions::MakeStaticArrayActionModifier` | `Tag` | `FName("StaticArrayAction")` |
| `ULearningAgentsActions::MakeStructAction` | `Tag` | `FName("StructAction")` |
| `ULearningAgentsActions::MakeStructActionFromArrays` | `Tag` | `FName("StructAction")` |
| `ULearningAgentsActions::MakeStructActionModifier` | `Tag` | `FName("StructAction")` |
| `ULearningAgentsActions::MakeStructActionModifierFromArrays` | `Tag` | `FName("StructAction")` |
| `ULearningAgentsActions::MakeVelocityActionModifier` | `Tag` | `FName("VelocityAction")` |
| `ULearningAgentsActions::SpecifyAngleAction` | `Tag` | `FName("AngleAction")` |
| `ULearningAgentsActions::SpecifyBitmaskAction` | `Tag` | `FName("BitmaskAction")` |
| `ULearningAgentsActions::SpecifyBitmaskActionFromArray` | `Tag` | `FName("BitmaskAction")` |
| `ULearningAgentsActions::SpecifyBoolAction` | `Tag` | `FName("BoolAction")` |
| `ULearningAgentsActions::SpecifyContinuousAction` | `Tag` | `FName("ContinuousAction")` |
| `ULearningAgentsActions::SpecifyDirectionAction` | `Tag` | `FName("DirectionAction")` |
| `ULearningAgentsActions::SpecifyEitherAction` | `Tag` | `FName("EitherAction")` |
| `ULearningAgentsActions::SpecifyEncodingAction` | `Tag` | `FName("EncodingAction")` |
| `ULearningAgentsActions::SpecifyEnumAction` | `Tag` | `FName("EnumAction")` |
| `ULearningAgentsActions::SpecifyEnumActionFromArray` | `Tag` | `FName("EnumAction")` |
| `ULearningAgentsActions::SpecifyExclusiveDiscreteAction` | `Tag` | `FName("DiscreteExclusiveAction")` |
| `ULearningAgentsActions::SpecifyExclusiveUnionAction` | `Tag` | `FName("ExclusiveUnionAction")` |
| `ULearningAgentsActions::SpecifyExclusiveUnionActionFromArrays` | `Tag` | `FName("ExclusiveUnionAction")` |
| `ULearningAgentsActions::SpecifyFloatAction` | `Tag` | `FName("FloatAction")` |
| `ULearningAgentsActions::SpecifyInclusiveDiscreteAction` | `Tag` | `FName("DiscreteInclusiveAction")` |
| `ULearningAgentsActions::SpecifyInclusiveUnionAction` | `Tag` | `FName("InclusiveUnionAction")` |
| `ULearningAgentsActions::SpecifyInclusiveUnionActionFromArrays` | `Tag` | `FName("InclusiveUnionAction")` |
| `ULearningAgentsActions::SpecifyLocationAction` | `Tag` | `FName("LocationAction")` |
| `ULearningAgentsActions::SpecifyNamedExclusiveDiscreteAction` | `Tag` | `FName("NamedDiscreteExclusiveAction")` |
| `ULearningAgentsActions::SpecifyNamedInclusiveDiscreteAction` | `Tag` | `FName("NamedDiscreteInclusiveAction")` |
| `ULearningAgentsActions::SpecifyNullAction` | `Tag` | `FName("NullAction")` |
| `ULearningAgentsActions::SpecifyOptionalAction` | `Tag` | `FName("OptionalAction")` |
| `ULearningAgentsActions::SpecifyPairAction` | `Tag` | `FName("PairAction")` |
| `ULearningAgentsActions::SpecifyRotationAction` | `Tag` | `FName("RotationAction")` |
| `ULearningAgentsActions::SpecifyScaleAction` | `Tag` | `FName("ScaleAction")` |
| `ULearningAgentsActions::SpecifyStaticArrayAction` | `Tag` | `FName("StaticArrayAction")` |
| `ULearningAgentsActions::SpecifyStructAction` | `Tag` | `FName("StructAction")` |
| `ULearningAgentsActions::SpecifyStructActionFromArrays` | `Tag` | `FName("StructAction")` |
| `ULearningAgentsActions::SpecifyTransformAction` | `Tag` | `FName("TransformAction")` |
| `ULearningAgentsActions::SpecifyVelocityAction` | `Tag` | `FName("VelocityAction")` |
| `ULearningAgentsCompletions::MakeCompletion` | `Tag` | `FName("Completion")` |
| `ULearningAgentsCompletions::MakeCompletionOnCondition` | `Tag` | `FName("ConditionCompletion")` |
| `ULearningAgentsCompletions::MakeCompletionOnEpisodeStepsRecorded` | `Tag` | `FName("EpisodeStepsRecordedCompletion")` |
| `ULearningAgentsCompletions::MakeCompletionOnLocationDifferenceAboveThreshold` | `Tag` | `FName("LocationDifferenceAboveThresholdCompletion")` |
| `ULearningAgentsCompletions::MakeCompletionOnLocationDifferenceBelowThreshold` | `Tag` | `FName("LocationDifferenceBelowThresholdCompletion")` |
| `ULearningAgentsCompletions::MakeCompletionOnLocationOutsideBounds` | `Tag` | `FName("LocationOutsideBoundsCompletion")` |
| `ULearningAgentsCompletions::MakeCompletionOnTimeElapsed` | `Tag` | `FName("TimeElapsedCompletion")` |
| `ULearningAgentsController::MakeController` | `Name` | `FName("Controller")` |
| `ULearningAgentsFlowMatchingTrainer::MakeFlowMatchingTrainer` | `Name` | `FName("FlowMatchingTrainer")` |
| `ULearningAgentsImitationTrainer::MakeImitationTrainer` | `Name` | `FName("ImitationTrainer")` |
| `ULearningAgentsInteractor::MakeInteractor` | `Name` | `FName("Interactor")` |
| `ULearningAgentsObservations::GetAngleObservation` | `Tag` | `FName("AngleObservation")` |
| `ULearningAgentsObservations::GetAngleObservationRadians` | `Tag` | `FName("AngleObservation")` |
| `ULearningAgentsObservations::GetArrayObservation` | `Tag` | `FName("ArrayObservation")` |
| `ULearningAgentsObservations::GetArrayObservationNum` | `Tag` | `FName("ArrayObservation")` |
| `ULearningAgentsObservations::GetBitmaskObservation` | `Tag` | `FName("BitmaskObservation")` |
| `ULearningAgentsObservations::GetBoolObservation` | `Tag` | `FName("BoolObservation")` |
| `ULearningAgentsObservations::GetContinuousObservation` | `Tag` | `FName("ContinuousObservation")` |
| `ULearningAgentsObservations::GetContinuousObservationNum` | `Tag` | `FName("ContinuousObservation")` |
| `ULearningAgentsObservations::GetConv1dObservation` | `Tag` | `FName("Conv1dObservation")` |
| `ULearningAgentsObservations::GetConv2dObservation` | `Tag` | `FName("Conv2dObservation")` |
| `ULearningAgentsObservations::GetCountObservation` | `Tag` | `FName("CountObservation")` |
| `ULearningAgentsObservations::GetDirectionAlongSplineObservation` | `Tag` | `FName("DirectionAlongSplineObservation")` |
| `ULearningAgentsObservations::GetDirectionObservation` | `Tag` | `FName("DirectionObservation")` |
| `ULearningAgentsObservations::GetEitherObservation` | `Tag` | `FName("EitherObservation")` |
| `ULearningAgentsObservations::GetEncodingObservation` | `Tag` | `FName("EncodingObservation")` |
| `ULearningAgentsObservations::GetEnumObservation` | `Tag` | `FName("EnumObservation")` |
| `ULearningAgentsObservations::GetExclusiveDiscreteObservation` | `Tag` | `FName("ExclusiveDiscreteObservation")` |
| `ULearningAgentsObservations::GetExclusiveUnionObservation` | `Tag` | `FName("ExclusiveUnionObservation")` |
| `ULearningAgentsObservations::GetFloatObservation` | `Tag` | `FName("FloatObservation")` |
| `ULearningAgentsObservations::GetInclusiveDiscreteObservation` | `Tag` | `FName("InclusiveDiscreteObservation")` |
| `ULearningAgentsObservations::GetInclusiveDiscreteObservationNum` | `Tag` | `FName("InclusiveDiscreteObservation")` |
| `ULearningAgentsObservations::GetInclusiveUnionObservation` | `Tag` | `FName("InclusiveUnionObservation")` |
| `ULearningAgentsObservations::GetInclusiveUnionObservationNum` | `Tag` | `FName("InclusiveUnionObservation")` |
| `ULearningAgentsObservations::GetInclusiveUnionObservationToArrays` | `Tag` | `FName("InclusiveUnionObservation")` |
| `ULearningAgentsObservations::GetLocationAlongSplineObservation` | `Tag` | `FName("LocationAlongSplineObservation")` |
| `ULearningAgentsObservations::GetLocationObservation` | `Tag` | `FName("LocationObservation")` |
| `ULearningAgentsObservations::GetMapObservation` | `Tag` | `FName("MapObservation")` |
| `ULearningAgentsObservations::GetMapObservationNum` | `Tag` | `FName("MapObservation")` |
| `ULearningAgentsObservations::GetMapObservationToArrays` | `Tag` | `FName("MapObservation")` |
| `ULearningAgentsObservations::GetNamedExclusiveDiscreteObservation` | `Tag` | `FName("ExclusiveDiscreteObservation")` |
| `ULearningAgentsObservations::GetNamedInclusiveDiscreteObservation` | `Tag` | `FName("InclusiveDiscreteObservation")` |
| `ULearningAgentsObservations::GetNamedInclusiveDiscreteObservationNum` | `Tag` | `FName("InclusiveDiscreteObservation")` |
| `ULearningAgentsObservations::GetNullObservation` | `Tag` | `FName("NullObservation")` |
| `ULearningAgentsObservations::GetOptionalObservation` | `Tag` | `FName("OptionalObservation")` |
| `ULearningAgentsObservations::GetPairObservation` | `Tag` | `FName("PairObservation")` |
| `ULearningAgentsObservations::GetProportionAlongRayObservation` | `Tag` | `FName("ProportionAlongRayObservation")` |
| `ULearningAgentsObservations::GetProportionAlongSplineObservation` | `Tag` | `FName("ProportionAlongSplineObservation")` |
| `ULearningAgentsObservations::GetRotationObservation` | `Tag` | `FName("RotationObservation")` |
| `ULearningAgentsObservations::GetRotationObservationAsQuat` | `Tag` | `FName("RotationObservation")` |
| `ULearningAgentsObservations::GetScaleObservation` | `Tag` | `FName("ScaleObservation")` |
| `ULearningAgentsObservations::GetSetObservation` | `Tag` | `FName("SetObservation")` |
| `ULearningAgentsObservations::GetSetObservationNum` | `Tag` | `FName("SetObservation")` |
| `ULearningAgentsObservations::GetSetObservationToArray` | `Tag` | `FName("SetObservation")` |
| `ULearningAgentsObservations::GetStaticArrayObservation` | `Tag` | `FName("StaticArrayObservation")` |
| `ULearningAgentsObservations::GetStaticArrayObservationNum` | `Tag` | `FName("StaticArrayObservation")` |
| `ULearningAgentsObservations::GetStructObservation` | `Tag` | `FName("StructObservation")` |
| `ULearningAgentsObservations::GetStructObservationElement` | `Tag` | `FName("StructObservation")` |
| `ULearningAgentsObservations::GetStructObservationNum` | `Tag` | `FName("StructObservation")` |
| `ULearningAgentsObservations::GetStructObservationToArrays` | `Tag` | `FName("StructObservation")` |
| `ULearningAgentsObservations::GetTransformObservation` | `Tag` | `FName("TransformObservation")` |
| `ULearningAgentsObservations::GetVelocityObservation` | `Tag` | `FName("VelocityObservation")` |
| `ULearningAgentsObservations::MakeArrayObservation` | `Tag` | `FName("ArrayObservation")` |
| `ULearningAgentsObservations::MakeConv1dObservation` | `Tag` | `FName("Conv1dObservation")` |
| `ULearningAgentsObservations::MakeConv2dObservation` | `Tag` | `FName("Conv2dObservation")` |
| `ULearningAgentsObservations::MakeEitherAObservation` | `Tag` | `FName("EitherObservation")` |
| `ULearningAgentsObservations::MakeEitherBObservation` | `Tag` | `FName("EitherObservation")` |
| `ULearningAgentsObservations::MakeEitherObservation` | `Tag` | `FName("EitherObservation")` |
| `ULearningAgentsObservations::MakeEncodingObservation` | `Tag` | `FName("EncodingObservation")` |
| `ULearningAgentsObservations::MakeExclusiveUnionObservation` | `Tag` | `FName("ExclusiveUnionObservation")` |
| `ULearningAgentsObservations::MakeInclusiveUnionObservation` | `Tag` | `FName("InclusiveUnionObservation")` |
| `ULearningAgentsObservations::MakeInclusiveUnionObservationFromArrays` | `Tag` | `FName("InclusiveUnionObservation")` |
| `ULearningAgentsObservations::MakeMapObservation` | `Tag` | `FName("MapObservation")` |
| `ULearningAgentsObservations::MakeMapObservationFromArrays` | `Tag` | `FName("MapObservation")` |
| `ULearningAgentsObservations::MakeNullObservation` | `Tag` | `FName("NullObservation")` |
| `ULearningAgentsObservations::MakeOptionalNullObservation` | `Tag` | `FName("OptionalObservation")` |
| `ULearningAgentsObservations::MakeOptionalObservation` | `Tag` | `FName("OptionalObservation")` |
| `ULearningAgentsObservations::MakeOptionalValidObservation` | `Tag` | `FName("OptionalObservation")` |
| `ULearningAgentsObservations::MakePairObservation` | `Tag` | `FName("PairObservation")` |
| `ULearningAgentsObservations::MakeSetObservation` | `Tag` | `FName("SetObservation")` |
| `ULearningAgentsObservations::MakeSetObservationFromArray` | `Tag` | `FName("SetObservation")` |
| `ULearningAgentsObservations::MakeStaticArrayObservation` | `Tag` | `FName("StaticArrayObservation")` |
| `ULearningAgentsObservations::MakeStructObservation` | `Tag` | `FName("StructObservation")` |
| `ULearningAgentsObservations::MakeStructObservationFromArrays` | `Tag` | `FName("StructObservation")` |
| `ULearningAgentsObservations::SpecifyAngleObservation` | `Tag` | `FName("AngleObservation")` |
| `ULearningAgentsObservations::SpecifyArrayObservation` | `Tag` | `FName("ArrayObservation")` |
| `ULearningAgentsObservations::SpecifyBitmaskObservation` | `Tag` | `FName("BitmaskObservation")` |
| `ULearningAgentsObservations::SpecifyBoolObservation` | `Tag` | `FName("BoolObservation")` |
| `ULearningAgentsObservations::SpecifyContinuousObservation` | `Tag` | `FName("ContinuousObservation")` |
| `ULearningAgentsObservations::SpecifyConv1dObservation` | `Tag` | `FName("Conv1dObservation")` |
| `ULearningAgentsObservations::SpecifyConv2dObservation` | `Tag` | `FName("Conv2dObservation")` |
| `ULearningAgentsObservations::SpecifyCountObservation` | `Tag` | `FName("CountObservation")` |
| `ULearningAgentsObservations::SpecifyDirectionAlongSplineObservation` | `Tag` | `FName("DirectionAlongSplineObservation")` |
| `ULearningAgentsObservations::SpecifyDirectionObservation` | `Tag` | `FName("DirectionObservation")` |
| `ULearningAgentsObservations::SpecifyEitherObservation` | `Tag` | `FName("EitherObservation")` |
| `ULearningAgentsObservations::SpecifyEncodingObservation` | `Tag` | `FName("EncodingObservation")` |
| `ULearningAgentsObservations::SpecifyEnumObservation` | `Tag` | `FName("EnumObservation")` |
| `ULearningAgentsObservations::SpecifyExclusiveDiscreteObservation` | `Tag` | `FName("ExclusiveDiscreteObservation")` |
| `ULearningAgentsObservations::SpecifyExclusiveUnionObservation` | `Tag` | `FName("ExclusiveUnionObservation")` |
| `ULearningAgentsObservations::SpecifyExclusiveUnionObservationFromArrays` | `Tag` | `FName("ExclusiveUnionObservation")` |
| `ULearningAgentsObservations::SpecifyFloatObservation` | `Tag` | `FName("FloatObservation")` |
| `ULearningAgentsObservations::SpecifyInclusiveDiscreteObservation` | `Tag` | `FName("InclusiveDiscreteObservation")` |
| `ULearningAgentsObservations::SpecifyInclusiveUnionObservation` | `Tag` | `FName("InclusiveUnionObservation")` |
| `ULearningAgentsObservations::SpecifyInclusiveUnionObservationFromArrays` | `Tag` | `FName("InclusiveUnionObservation")` |
| `ULearningAgentsObservations::SpecifyLidarObservation` | `Tag` | `FName("LidarObservation")` |
| `ULearningAgentsObservations::SpecifyLocationAlongSplineObservation` | `Tag` | `FName("LocationAlongSplineObservation")` |
| `ULearningAgentsObservations::SpecifyLocationObservation` | `Tag` | `FName("LocationObservation")` |
| `ULearningAgentsObservations::SpecifyMapObservation` | `Tag` | `FName("MapObservation")` |
| `ULearningAgentsObservations::SpecifyNamedExclusiveDiscreteObservation` | `Tag` | `FName("NamedExclusiveDiscreteObservation")` |
| `ULearningAgentsObservations::SpecifyNamedInclusiveDiscreteObservation` | `Tag` | `FName("NamedInclusiveDiscreteObservation")` |
| `ULearningAgentsObservations::SpecifyNullObservation` | `Tag` | `FName("NullObservation")` |
| `ULearningAgentsObservations::SpecifyOptionalObservation` | `Tag` | `FName("OptionalObservation")` |
| `ULearningAgentsObservations::SpecifyPairObservation` | `Tag` | `FName("PairObservation")` |
| `ULearningAgentsObservations::SpecifyProportionAlongRayObservation` | `Tag` | `FName("ProportionAlongRayObservation")` |
| `ULearningAgentsObservations::SpecifyProportionAlongSplineObservation` | `Tag` | `FName("ProportionAlongSplineObservation")` |
| `ULearningAgentsObservations::SpecifyRotationObservation` | `Tag` | `FName("RotationObservation")` |
| `ULearningAgentsObservations::SpecifyScaleObservation` | `Tag` | `FName("ScaleObservation")` |
| `ULearningAgentsObservations::SpecifySetObservation` | `Tag` | `FName("SetObservation")` |
| `ULearningAgentsObservations::SpecifyStaticArrayObservation` | `Tag` | `FName("StaticArrayObservation")` |
| `ULearningAgentsObservations::SpecifyStructObservation` | `Tag` | `FName("StructObservation")` |
| `ULearningAgentsObservations::SpecifyStructObservationFromArrays` | `Tag` | `FName("StructObservation")` |
| `ULearningAgentsObservations::SpecifyTransformObservation` | `Tag` | `FName("TransformObservation")` |
| `ULearningAgentsObservations::SpecifyVelocityObservation` | `Tag` | `FName("VelocityObservation")` |
| `ULearningAgentsRewards::MakeReward` | `Tag` | `FName("Reward")` |
| `ULearningAgentsRewards::MakeRewardFromAngleSimilarity` | `Tag` | `FName("AngleSimilarityReward")` |
| `ULearningAgentsRewards::MakeRewardFromDirectionSimilarity` | `Tag` | `FName("DirectionSimilarityReward")` |
| `ULearningAgentsRewards::MakeRewardFromLocationDifference` | `Tag` | `FName("LocationDifferenceReward")` |
| `ULearningAgentsRewards::MakeRewardFromLocationSimilarity` | `Tag` | `FName("LocationSimilarityReward")` |
| `ULearningAgentsRewards::MakeRewardFromRotationSimilarity` | `Tag` | `FName("RotationSimilarityReward")` |
| `ULearningAgentsRewards::MakeRewardFromRotationSimilarityAsQuats` | `Tag` | `FName("RotationSimilarityReward")` |
| `ULearningAgentsRewards::MakeRewardFromVelocityAlongSpline` | `Tag` | `FName("VelocityAlongSplineReward")` |
| `ULearningAgentsRewards::MakeRewardOnCondition` | `Tag` | `FName("ConditionReward")` |
| `ULearningAgentsRewards::MakeRewardOnLocationDifferenceAboveThreshold` | `Tag` | `FName("LocationDifferenceAboveThresholdReward")` |
| `ULearningAgentsRewards::MakeRewardOnLocationDifferenceBelowThreshold` | `Tag` | `FName("LocationDifferenceBelowThresholdReward")` |
| `ULearningAgentsTrainingEnvironment::MakeTrainingEnvironment` | `Name` | `FName("TrainingEnvironment")` |
| `UNiagaraSimCache::ReadColorAttribute` | `AttributeName` | `FName("Color")` |
| `UNiagaraSimCache::ReadPositionAttribute` | `AttributeName` | `FName("Position")` |
| `UNiagaraSimCache::ReadPositionAttributeWithRebase` | `AttributeName` | `FName("Position")` |
| `UNiagaraSimCache::ReadQuatAttribute` | `AttributeName` | `FName("MeshOrientation")` |
| `UNiagaraSimCache::ReadQuatAttributeWithRebase` | `AttributeName` | `FName("MeshOrientation")` |
| `UPyTestTypeHint::CheckNameTypeHints` | `Param2` | `FName("Hi")` |
| `URigVMController::AddUnitNode` | `InMethodName` | `FName("Execute")` |
| `URigVMController::AddUnitNodeFromStructPath` | `InMethodName` | `FName("Execute")` |
| `URigVMController::AddUnitNodeWithDefaults` | `InMethodName` | `FName("Execute")` |
| `VisualLogger::LogArrow` | `CategoryName` | `FName("VisLogBP")` |
| `VisualLogger::LogBox` | `LogCategory` | `FName("VisLogBP")` |
| `VisualLogger::LogCapsule` | `LogCategory` | `FName("VisLogBP")` |
| `VisualLogger::LogCircle` | `CategoryName` | `FName("VisLogBP")` |
| `VisualLogger::LogCone` | `LogCategory` | `FName("VisLogBP")` |
| `VisualLogger::LogCylinder` | `LogCategory` | `FName("VisLogBP")` |
| `VisualLogger::LogLocation` | `LogCategory` | `FName("VisLogBP")` |
| `VisualLogger::LogOrientedBox` | `LogCategory` | `FName("VisLogBP")` |
| `VisualLogger::LogSegment` | `CategoryName` | `FName("VisLogBP")` |
| `VisualLogger::LogSphere` | `LogCategory` | `FName("VisLogBP")` |
| `VisualLogger::LogText` | `LogCategory` | `FName("VisLogBP")` |
| `Widget::DrawTextFormatted` | `FontTypeFace` | `FName("Regular")` |

## Interfaces supplied by engine plugins

A standard UE installation includes more bundled plugins whose APIs are available in soloAS; these plugins are absent from the compared UE-AS fork installation, so they are not API differences. Availability depends on the engine installation and whether the plugins are enabled.

## Loading timing (not an API difference)

Some native declarations in the following modules are identical on both sides. These modules are already loaded when soloAS initializes as a project plugin, so the declarations are available to scripts; UE-AS fork initializes script bindings before these modules load, so they are unavailable there. The declarations and signatures themselves do not differ.

The following modules are involved:

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

**Difference:** RenderTextureGraph preserves all original side effects. Its const& declaration matches UE-AS fork; the reference points to a Bridge-owned array copy.

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
