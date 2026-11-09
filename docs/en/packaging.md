# Packaging

## Packaging entry points

1. Set maps, cooking, Pak/IoStore, targets and other options in **SoloAS → UE Packaging Settings**, which opens Unreal Engine's **Project Settings → Project → Packaging** page.
2. **SoloAS → Package Project…** opens UE's Project Launcher for native UE packaging. Scripts are included as source.
3. For bytecode or semi-AOT, choose the delivery form and output directory in **SoloAS → soloAS Packaging Settings**, then package with the command line or AI assistance described below.

## Bytecode packaging

Do not ship the main AS source, and cut startup preprocessing and compiling. Functions still run as bytecode in the VM, so this is not a native speedup, and the program data in the cache can be analyzed, so it is not encryption or reverse-engineering protection.

Choose **Bytecode** in soloAS Packaging Settings, or set `deliveryMode` to `bytecode` in a CLI profile. Run the soloAS packaging CLI. The tool generates matching precompiled caches, collects them into `Script/` in the release copy and checks the package. The base caches are `Binds.Cache`, `Binds.Cache.Headers` and `PrecompiledScript.Cache`; the package should not contain project `.as` source.

- **Cache and exe do not match**: a package without source reports `ASR-PRECOMPILED-NO-SOURCE: No compatible precompiled script cache and no script source files are available.`, and the maintainer must publish a matching cache. `Loaded angelscript precompiled data was for a different build configuration. Discarding all precompiled data.` means the cache was generated with another configuration.

## Semi-AOT packaging (static JIT)

Turn the AS functions that can be generated into C++ compiled into the Game, reducing the VM overhead of those functions; the AS runtime, reflection and bytecode entry points remain. The cost is longer C++ build time and a larger executable, and not every function gets faster.

Choose **Semi-AOT** in soloAS Packaging Settings, or set `deliveryMode` to `semi_aot` in a CLI profile. Run the soloAS packaging CLI. The same run that generates the precompiled data outputs the JIT C++ files, and the `sync-jit` command puts them into the C++ consumer module; when the consumer module does not exist it is generated and registered with the Game target automatically, and every later generation syncs and rebuilds the Game automatically. The order is fixed: generate, rebuild the Game, package; cooking again alone does not link the C++ into the exe. The `check-package` command should decide "semi-AOT package": the JIT consumer module is linked into the exe and the package has the matching cache.

- **How it gets into the package**: the JIT C++ enters the exe through the normal build, not by being placed in the Pak; the cache is packaged by the rules of bytecode packaging.
- **Cache and the exe's JIT do not match**: you see `Loaded angelscript precompiled data does not match the transpiled C++ in the game binary. Transpiled code will not be used!` and the bytecode in the cache is used instead, which mainly affects performance. When a module cache set does not match, the whole set may be invalidated.

## Packaging from scripts and CI

The `soloas_package.py` that ships with the plugin reads the same project settings as the native settings page. Use it to read or change configuration, manage profiles, run checks, package and query results from scripts or CI. The soloAS CLI pipeline currently supports Win64. `<Tool>` is `Build/PackagingTool/soloas_package.py` in the installed plugin:

```text
python <Tool> --project <Game.uproject> profiles list --json
python <Tool> --project <Game.uproject> config read --platform Win64 --json
python <Tool> --project <Game.uproject> precheck --json
python <Tool> --project <Game.uproject> run --json
python <Tool> --project <Game.uproject> status --job <id> --json
```

Without `--profile`, the CLI uses project defaults. To repeat a named combination, create the profile first:

```text
python <Tool> --project <Game.uproject> profiles save --name Shipping-bytecode --overrides '{"configuration":"Shipping","deliveryMode":"bytecode"}' --json
python <Tool> --project <Game.uproject> run --profile Shipping-bytecode --json
```

`precheck` reports configuration, optional toolchain probing and pending checks; `run` performs the full checks before building. The script returns structured progress and results that CI can read. A configuration write returns the diff of what changed; every run records its profile and input version so it can be reviewed and rebuilt.

## Let AI prepare and run packaging

After connecting in **SoloAS → AI-assisted development**, tell the AI your delivery goal, for example "create a Windows Shipping bytecode profile, check the configuration and package". The AI reads the current project settings, gives the changes needed and their diff, saves the profile and starts packaging; you can keep asking about progress, find the failing stage and see the final result. AI assistance and the command line use the same packaging flow and read the project defaults written by the native settings page.

After connecting MCP, use `soloas_package_config`, `soloas_package_config_write`, `soloas_package_profiles_save`, `soloas_package_precheck`, `soloas_package_run`, `soloas_package_status` and `soloas_package_cancel` for the same workflow.
