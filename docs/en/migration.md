# Migrating an existing AS project

## 1. Back up the project

Copy the complete project and migrate the copy; keep `Script/`, `Config/` and `Content/`, and keep the working original for comparison.

## 2. Install the plugin

Remove the old Haze engine plugin, then install the soloAS plugin, into the project or into the engine; see the [quick start](requirements.md#quick-start) for how.

## 3. Enable the plugins

Confirm that `Angelscript` (the Runtime) is enabled; it enables `SoloASBridge` through its dependency. Enable GAS and Enhanced Input as needed.

## 4. Fix compile problems

1. **Rebuild the project**: a delivery build also needs the cache regenerated.
2. **Fix compile and dependency problems**: if you hit compile problems, fix them as the messages direct.
3. **Fix asset warnings**: for `Asset has been saved with empty engine version`, use SoloAS → Resave assets with empty engine version, or Fix in one click in the notification. Save the affected assets and check loading again.

## 5. Run the project and test for real

Verify your existing AS scripts, hot reload, and the GAS and Enhanced Input you enable as the project needs, then run in PIE and run a packaged build and test it, going through the full flow.
