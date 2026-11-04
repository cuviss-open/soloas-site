# Migrating an existing AS project

## 1. Back up the project

Copy the complete project and migrate the copy; keep `Script/`, `Config/` and `Content/`, and keep the working original for comparison.

## 2. Switch to stock Unreal Engine

In the backup copy, choose a supported stock Unreal Engine patch version and switch the `.uproject` engine association to it (right-click the `.uproject` and choose **Switch Unreal Engine version**, or edit `EngineAssociation`). Pure AS/Blueprint projects only need the engine association changed; C++ projects must also regenerate project files with that engine. Keep the old fork project and engine for comparison.

## 3. Install the plugin

Remove duplicate old UE-AS plugins only from the migration copy and the target stock engine plugin folders; leave the old fork project and engine untouched for comparison. Then install the soloAS plugin into the project or target engine; see the [quick start](requirements.md#quick-start) for how.

## 4. Enable the plugins

Confirm that the `Angelscript` plugin is enabled; its required dependencies are enabled automatically. Enable GAS and Enhanced Input as needed.

## 5. Fix compile problems

1. **Rebuild the project**: a delivery build also needs the cache regenerated.
2. **Fix compile and dependency problems**: if you hit compile problems, fix them as the messages direct.
3. **Fix asset warnings**: for `Asset has been saved with empty engine version`, use [Resave assets with empty engine version in the SoloAS menu](soloas-menu.md), or click **Fix in one click** in the notification. Save the affected assets and check loading again.

## 6. Run the project and test for real

Verify your existing AS scripts, hot reload, and the GAS and Enhanced Input you enable as the project needs, then run in PIE and run a packaged build and test it, going through the full flow.
