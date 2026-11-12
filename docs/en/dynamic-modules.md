# Feature Mods

## Introduction

Feature Mods let you write a piece of gameplay as a **FeatureMod**, called a Mod for short, that can be loaded, unloaded and updated independently. For example, put a set of challenge rules or a new gameplay mode into your own Mod.

### Where Mods sit

<svg class="ov-svg ov-wide" viewBox="0 0 1000 440" role="img" aria-label="Feature Mod layers, top to bottom: Feature Mods on top in three kinds, built-in Feature Mods (packaged with the project), official external Feature Mods (signed) and player external Feature Mods (API denylist, confirm on first load); below them Game Feature plugins, the game project, plugins (project plugins and engine plugins) and the UE engine core modules. Upper layers may depend on lower layers; lower layers must not depend on Feature Mods."><defs><marker id="ov3w" viewBox="0 0 8 8" refX="7" refY="4" markerWidth="8" markerHeight="8" orient="auto"><path class="ov-head" d="M0 0L8 4L0 8z"/></marker></defs><text class="ov-layer" x="0" y="40">Feature Mods</text><rect class="ov-node" x="120" y="10" width="285.333" height="50" rx="9"/><text class="ov-name sm" x="262.667" y="32" text-anchor="middle">Built-in Feature Mods</text><text class="ov-sub" x="262.667" y="50" text-anchor="middle">Packaged with the project</text><rect class="ov-node" x="417.333" y="10" width="285.333" height="50" rx="9"/><text class="ov-name sm" x="560" y="32" text-anchor="middle">Official external Feature Mods</text><text class="ov-sub" x="560" y="50" text-anchor="middle">Signed</text><rect class="ov-node" x="714.667" y="10" width="285.333" height="50" rx="9"/><text class="ov-name sm" x="857.333" y="32" text-anchor="middle">Player external Feature Mods</text><text class="ov-sub" x="857.333" y="50" text-anchor="middle">API denylist, confirm on first</text><text class="ov-sub" x="857.333" y="65" text-anchor="middle">load</text><path class="ov-arrow" d="M560 64V87" marker-end="url(#ov3w)"/><text class="ov-layer" x="0" y="122">Game Feature plugins</text><rect class="ov-node" x="120" y="92" width="880" height="50" rx="9"/><text class="ov-name sm" x="560" y="114" text-anchor="middle">Game Feature plugins</text><text class="ov-sub" x="560" y="132" text-anchor="middle">Toggleable gameplay units,</text><text class="ov-sub" x="560" y="147" text-anchor="middle">activated at runtime</text><path class="ov-arrow" d="M560 146V169" marker-end="url(#ov3w)"/><text class="ov-layer" x="0" y="204">Game project</text><rect class="ov-node" x="120" y="174" width="880" height="50" rx="9"/><text class="ov-name sm" x="560" y="196" text-anchor="middle">Game project</text><text class="ov-sub" x="560" y="214" text-anchor="middle">Project gameplay and assets</text><path class="ov-arrow" d="M560 228V251" marker-end="url(#ov3w)"/><text class="ov-layer" x="0" y="286">Plugins</text><rect class="ov-node" x="120" y="256" width="434" height="50" rx="9"/><text class="ov-name sm" x="337" y="278" text-anchor="middle">Project plugins</text><text class="ov-sub" x="337" y="296" text-anchor="middle">soloAS plugins, other project</text><text class="ov-sub" x="337" y="311" text-anchor="middle">plugins</text><rect class="ov-node" x="566" y="256" width="434" height="50" rx="9"/><text class="ov-name sm" x="783" y="278" text-anchor="middle">Engine plugins</text><text class="ov-sub" x="783" y="296" text-anchor="middle">GameplayAbilities, EnhancedInput</text><text class="ov-sub" x="783" y="311" text-anchor="middle">and more</text><path class="ov-arrow" d="M560 310V333" marker-end="url(#ov3w)"/><text class="ov-layer" x="0" y="368">UE core</text><rect class="ov-node base" x="120" y="338" width="880" height="50" rx="9"/><text class="ov-name sm" x="560" y="360" text-anchor="middle">UE engine core modules</text><text class="ov-sub" x="560" y="378" text-anchor="middle">Engine foundations</text><text class="ov-sub" x="120" y="428">↓ Upper layers may depend on lower layers</text><text class="ov-sub" x="560" y="428">✕ Lower layers must not depend on Feature Mods</text></svg>
<svg class="ov-svg ov-tall" viewBox="0 0 300 767" role="img" aria-label="Feature Mod layers, top to bottom: Feature Mods on top in three kinds, built-in Feature Mods (packaged with the project), official external Feature Mods (signed) and player external Feature Mods (API denylist, confirm on first load); below them Game Feature plugins, the game project, plugins (project plugins and engine plugins) and the UE engine core modules. Upper layers may depend on lower layers; lower layers must not depend on Feature Mods."><defs><marker id="ov3t" viewBox="0 0 8 8" refX="7" refY="4" markerWidth="8" markerHeight="8" orient="auto"><path class="ov-head" d="M0 0L8 4L0 8z"/></marker></defs><text class="ov-layer" x="10" y="12">Feature Mods</text><rect class="ov-node" x="10" y="20" width="280" height="46" rx="9"/><text class="ov-name sm" x="150" y="42" text-anchor="middle">Built-in Feature Mods</text><text class="ov-sub" x="150" y="60" text-anchor="middle">Packaged with the project</text><rect class="ov-node" x="10" y="74" width="280" height="46" rx="9"/><text class="ov-name sm" x="150" y="96" text-anchor="middle">Official external Feature Mods</text><text class="ov-sub" x="150" y="114" text-anchor="middle">Signed</text><rect class="ov-node" x="10" y="128" width="280" height="62" rx="9"/><text class="ov-name sm" x="150" y="150" text-anchor="middle">Player external Feature Mods</text><text class="ov-sub" x="150" y="168" text-anchor="middle">API denylist, confirm on first</text><text class="ov-sub" x="150" y="183" text-anchor="middle">load</text><text class="ov-layer" x="10" y="236">Game Feature plugins</text><rect class="ov-node" x="10" y="244" width="280" height="62" rx="9"/><text class="ov-name sm" x="150" y="266" text-anchor="middle">Game Feature plugins</text><text class="ov-sub" x="150" y="284" text-anchor="middle">Toggleable gameplay units,</text><text class="ov-sub" x="150" y="299" text-anchor="middle">activated at runtime</text><text class="ov-layer" x="10" y="352">Game project</text><rect class="ov-node" x="10" y="360" width="280" height="46" rx="9"/><text class="ov-name sm" x="150" y="382" text-anchor="middle">Game project</text><text class="ov-sub" x="150" y="400" text-anchor="middle">Project gameplay and assets</text><text class="ov-layer" x="10" y="452">Plugins</text><rect class="ov-node" x="10" y="460" width="280" height="62" rx="9"/><text class="ov-name sm" x="150" y="482" text-anchor="middle">Project plugins</text><text class="ov-sub" x="150" y="500" text-anchor="middle">soloAS plugins, other project</text><text class="ov-sub" x="150" y="515" text-anchor="middle">plugins</text><rect class="ov-node" x="10" y="530" width="280" height="62" rx="9"/><text class="ov-name sm" x="150" y="552" text-anchor="middle">Engine plugins</text><text class="ov-sub" x="150" y="570" text-anchor="middle">GameplayAbilities, EnhancedInput</text><text class="ov-sub" x="150" y="585" text-anchor="middle">and more</text><text class="ov-layer" x="10" y="638">UE core</text><rect class="ov-node base" x="10" y="646" width="280" height="46" rx="9"/><text class="ov-name sm" x="150" y="668" text-anchor="middle">UE engine core modules</text><text class="ov-sub" x="150" y="686" text-anchor="middle">Engine foundations</text><text class="ov-sub" x="10" y="714">↓ Upper layers may depend on lower layers</text><text class="ov-sub" x="10" y="733">✕ Lower layers must not depend on Feature</text><text class="ov-sub" x="10" y="748">Mods</text><path class="ov-arrow" d="M150 201V220" marker-end="url(#ov3t)"/><path class="ov-arrow" d="M150 317V336" marker-end="url(#ov3t)"/><path class="ov-arrow" d="M150 417V436" marker-end="url(#ov3t)"/><path class="ov-arrow" d="M150 603V622" marker-end="url(#ov3t)"/></svg>


Mods sit at the top: a Mod can depend on the game project, Game Feature Plugins and other Mods, and none of those can depend on a Mod. By trust source there are three kinds: built-in modules ship with the project and are not restricted by the player API denylist; official external modules carry the project developer's signature; player external modules can use APIs that are not denied by the denylist. See "The three kinds of modules and trust" below.

## Usage

Once Feature Mods are enabled, place a Mod like an ordinary plugin. There are three kinds:

- **Built-in modules**: ship with the project as the project's own Mods and are not restricted by the player API denylist.
- **Official external modules**: carry the project developer's signature; their permissions are the same as built-in modules.
- **Player external modules**: unsigned, or signed in a way that is not recognized; they load directly and can use APIs that are not denied by the denylist; a confirmation appears on the first load, and the project can turn it off.

Mods that ship with the project go in `Plugins/FeatureMods/<name>/`; Mods that players or third parties install go in `FeatureMods/<name>/` in the game root. Built-in Mods packaged with the project have built-in trust; trust for external Mods is determined by their signature. Installing a Mod is simply copying it in and starting the game.

Use **SoloAS → FeatureMods** to create a Mod, edit its manifest, view dependencies or run **One-click check**. The directory name and the `.uplugin` file name must match and serve as the stable Mod name. Mark the plugin with `"FeatureMod": true` in the `.uplugin`, and put the gameplay scripts in the Mod's `Script/`.

## Mod configuration: FeatureMod.json

The configuration lives in `FeatureMod.json` at the Mod root. Start from this minimal manifest:

```json
{
  "schemaVersion": 1,
  "version": "1.0.0",
  "dependencies": { "trunkModules": [], "branches": [], "featureMods": [] },
  "BlueprintBindings": {},
  "BlueprintDependencies": []
}
```

| Field | What to fill in |
| --- | --- |
| `version` | The release version of this Mod; increase it on each update. |
| `dependencies` | What this Mod uses directly from elsewhere, in three kinds; see below. |
| `BlueprintBindings` | Give Blueprint assets names; scripts use the name, not the asset path. |
| `BlueprintDependencies` | Names of the Blueprint parents the scripts inherit. |

`dependencies` declares which things provided by others this Mod uses directly; leave an array empty when there is nothing of that kind:

- `trunkModules`: write the fixed identifier `Project` to use the project itself, or a plugin's stable ID to use scripts in an ordinary plugin. You do not need to write C++ module names; module names in older manifests still work.
- `branches`: ordinary Game Feature Plugins to use; also declare its UE dependency in the `.uplugin` `Plugins` list.
- `featureMods`: other Mods to use.

List exactly what you use directly: indirect dependencies do not grant a right to reference them; a missing or circular dependency makes the affected Mods rejected without affecting unrelated ones. Each name must match a plugin or Mod that really exists in the project, and any plugin you use must be enabled.

## The three kinds of modules and trust

A signature marks a module as official; a project can also allow only official external modules. A module that claims an official signature but fails verification is rejected; it is not downgraded to a player external module.

Official external modules need the author and the project developer to work together. The Sign button in the FeatureMods window provides instructions; signing is performed with an external tool:

1. The author creates `FeatureMods/<name>/` with a `.uplugin` marked `"FeatureMod": true`, a `FeatureMod.json` and all the files.
2. The project developer sets the Ed25519 public key (`PatchPublicKeyBase64`) and the Key ID (`PatchVerifyKeyId`) in the ModKit settings in `DefaultEngine.ini`. A Shipping build compiles this trust root into the game, so changing the key later needs a new build. Use a key generation and signing tool approved by the publisher.
3. Use the packaging action to generate a draft manifest and bytes to sign, sign them with an external tool and fill in the signature value. The release package needs a `<name>.manifest.json` beside it, listing every file in the Mod directory with its SHA-256 and carrying a valid signature; it is a different file from `FeatureMod.json`.
4. When deploying, put the Mod in the game root's `FeatureMods/<name>/` and put the signed manifest beside it.
5. At startup the game checks the signature, the public key ID, the engine version, the file hashes and the complete file set; a module that passes is marked as an official external module, and an official module that does not match is rejected.

The version floor applies only to signed modules: it is recorded automatically the first time verification succeeds, after which a rollback is rejected by default; no floor file has to be placed by hand.

A player external module is unsigned, or signed in a way that is not recognized; it needs no signature files and loads directly. Installing it is simply copying it in and starting the game. A confirmation appears on the first load, and the project can turn it off.

The project can turn on the "official external modules only" switch (off by default); once on, only official external modules load.

Before deployment, verify a Mod package offline with `ModKitPatchVerify -Kind=package`.

A signature says who published the files. Built-in and official external modules are not restricted by the player API denylist. Player external modules can call available APIs, inherit base classes and override events by default; the default denylist restricts console commands, file reading, writing and deletion, launching external programs, opening URLs, exiting the game, changing object properties by name, editor APIs, `QuitGame` and `DeleteGameInSlot`. Interfaces marked `internal` are always denied. Authors can look up available functions in the `PublicApi.as` provided by the project.

The project maintainer can append denylist rules in `Config/DefaultEngine.ini`, for example:

```ini
[/Script/AngelscriptModKit.ModKitSettings]
+DeniedApiPatterns=*FVector::FVector*
+DeniedBaseClassPatterns=APawn
+DeniedOverridePatterns=*AActor::BeginPlay*
```

These fields restrict calls, inheritance and event overrides respectively. Project rules apply alongside the default denylist, and deny rules take precedence. Contact the project maintainer to adjust permissions.
