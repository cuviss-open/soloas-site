# Plugin core

On an unmodified Unreal Engine it provides the core AngelScript scripting workflow and is compatible with common usage of Hazelight's UE fork (the Haze fork); you can follow the [Hazelight documentation](https://angelscript.hazelight.se/).

## Key differences and improvements

- Scripting runs on stock UE as project plugins, without building the engine.
- If assets brought over from projects that use the Haze fork as their engine report an empty saved engine version, use **SoloAS → Resave assets with empty engine version** to resave them in bulk.
- Fixed a case where a script object's destructor could run twice during garbage collection or hot reload.
- A truncated or corrupted precompiled script cache is now rejected with a clear error instead of failing partway through loading.

## Technical limitations

- FullReload on stock UE takes about 1.6 to 1.8 times as long as on the Haze fork. This is a known cost of the adaptation.
- Some editor experience improvements take full effect only on the stock engine version this release supports; runtime and packaged games are not affected.
