# Feature overview

## Core

Use AngelScript with stock Unreal Engine, write script classes and components, hot reload in the editor, and use GAS and Enhanced Input. See [Plugin core](core.md) and [Manual binding packs](manual-binding-packs.md).

## Core extensions

These features are on by default; each can be turned off individually. See [Core extensions](extensions.md).

- **UE interfaces**: scripts can implement C++, AS and Blueprint interfaces, and editor scripts can declare new interfaces for Blueprints to implement.
- **Blueprint inheritance**: script classes can inherit directly from Blueprint parent classes.
- **Blueprint structs**: use structs defined in Blueprints from script.
- **Native event parent implementations**: when overriding a native event, call the original Unreal parent implementation to keep its default behavior.
- **Lambdas**: write lambdas for delegates and container algorithms, with explicit captures.

## Developer tools

See [Packaging](packaging.md) and [AI-assisted development](ai-assisted.md).

- **Bytecode packaging**: ship without AS source and skip script preprocessing and compilation at startup.
- **Semi-AOT packaging (static JIT)**: compile eligible AS functions to C++ in the game binary to reduce VM overhead.
- **Command-line and CI packaging**: check and run packaging with the bundled script, using the same project settings as the editor.
- **AI-assisted development via MCP**: AI can read script types and project information, help with packaging, and debug scripts through MCP.

## Upcoming features

Feature Mods, the manual binding core, auto binding and additional manual binding packs are coming soon; see the [roadmap](/#roadmap).
