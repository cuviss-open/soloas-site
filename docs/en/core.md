# Plugin core

On an unmodified Unreal Engine, soloAS provides the core AngelScript scripting workflow and is compatible with common usage of UE-AS fork; you can follow the [Hazelight documentation](https://angelscript.hazelight.se/).

## Key differences and improvements

- Scripting runs on stock UE as project plugins, without building the engine.
- If assets brought over from projects that use UE-AS fork as their engine report an empty saved engine version, use **SoloAS → Resave assets with empty engine version** to resave them in bulk.
- Fixed a case where a script object's destructor could run twice during garbage collection or hot reload.
- A truncated or corrupted precompiled script cache is now rejected with a clear error instead of failing partway through loading.
- The plugin modules cannot be unloaded or reloaded while the editor is running; Live Coding and script hot reload work as usual.

## Technical limitations

- FullReload on stock UE can take longer than on the UE-AS fork; the difference depends on the project.
- Some editor experience improvements take full effect only on the stock engine version this release supports; runtime and packaged games are not affected.

[API differences between the latest soloAS and the UE-AS fork](api-differences.md)
