---
title: "UE_Angelscript — Source 2: how AS classes are bound to UE"
order: 41
category: internals
---
# UE_Angelscript — Source 2: how AS classes are bound to UE

Continuing from the previous article.

Prerequisites: C++, UE and Angelscript knowledge.

# Compiling AS classes into UE classes

## How can UE recognize an AS class?

More precisely, binding AS classes to UE means generating reflection information from AS code for UE’s reflection system. UE reflection can provide class information dynamically at runtime; that is what “binding to UE” means here.

### Preprocessing

AS scripts accept U++-style UCLASS, USTRUCT, UENUM, UPROPERTY and UFUNCTION macros. These do not participate in compilation by the AS engine; they provide reflection information.

The plugin reads AS files from C++, extracts reflection information from macros and keywords, then dynamically generates reflected types such as UClass. It also transforms the original AS source into code for the VM, generally deleting those macros.

So the AS source you write is not the code the VM ultimately runs. The plugin preprocesses it, removing macros and converting special constructs such as delegate declarations. This is metaprogramming: code generating code.

Here are two snippets for comparison.
The original AS:

```C++
UCLASS(Abstract)
class UGameplayAbility_Test : UGameplayAbility
{
    UPROPERTY(Category = "Test")
    float32 TestFloat = 1;
   
	UFUNCTION(BlueprintOverride)
	void ActivateAbility()
	{
		// skip
	}
}
```

The generated code:

```C++
class UGameplayAbility_Test : UGameplayAbility
{

    float32 TestFloat = 1;

    void ActivateAbility_Implementation()
    {
        // skip
    }
}

const TSubclassOf<UObject> __StaticType_UGameplayAbility_Test;

namespace UGameplayAbility_Test {
    UClass StaticClass() __generated
        {
            return __StaticType_UGameplayAbility_Test;
        }
    }
```

All macros have disappeared, and extra code is appended to add functions to the type.

Let us look a little deeper at preprocessing.

The main process is in void FAngelscriptManager::InitialCompile(). It can load precompiled data under certain conditions, but development normally uses AS source, which is the focus here.

The overall flow is:

Create a preprocessor. Its constructor reads AS settings, the options in project settings.
This is FAngelscriptPreprocessor Preprocessor, with an important function:
bool FAngelscriptPreprocessor::Preprocess(), which details the source transformation.

The core flow:

---

1. **Load script contents asynchronously**
   - If loads are pending, call `PerformAsynchronousLoads()` so all contents are in memory.
2. **Parse into chunks: ParseIntoChunks**
   - Call `ParseIntoChunks(File)` for each file. Each chunk represents a class, struct, global section or enum.
3. **Detect classes, structs and enums: DetectClasses/DetectEnum**
   - Traverse chunks and record descriptions such as `FAngelscriptClassDesc` and `FAngelscriptEnumDesc`.
4. **Analyze classes and structs: AnalyzeClasses/AnalyzeStructs**
   - Analyze inheritance, static members and generated static functions.
5. **Process macros: ProcessMacros**
   - Process UPROPERTY/UFUNCTION/UCLASS and generate property and method descriptions.
6. **Process delegates: ProcessDelegates**
   - Process delegate/event declarations.
7. **Broadcast the OnProcessChunks hook**
   - Let external listeners customize each preprocessor instance.
8. **Process default values: ProcessDefaults**
   - Convert default statements into default-value code.
9. **Condense chunks: CondenseFromChunks**
   - Combine chunks into final preprocessed source, `File.ProcessedCode`, then append generated code.
10. **Postprocess: PostProcessRangeBasedFor/PostProcessLiteralAssets**
    - Handle range-based loops, asset syntax and other syntax sugar.
11. **Broadcast the OnPostProcessCode hook**
    - Let external listeners further process the final code.
12. **Generate module code sections**
    - Add `File.ProcessedCode` as an `FCodeSection` in `File.Module->Code` for compilation.
---

That is a lot, but it falls into two jobs:

- Generate final preprocessed Angelscript code.
- Generate descriptions of reflection information.

The first compiles to VM bytecode. The second generates reflection types such as UClass and UScriptStruct.

### Compilation

After preprocessing comes compilation, implemented in ECompileResult FAngelscriptManager::CompileModules.

The simplified flow:

```
   ├─► recursively collect all modules to compile, with their dependencies
   │
   ├─► Stage 1: generate type information (CompileModule_Types_Stage1)
   │
   ├─► parse the script sources in parallel (BuildParallelParseScripts)
   │
   ├─► generate type metadata (BuildGenerateTypes)
   │
   ├─► Stage 2: generate function metadata (CompileModule_Functions_Stage2)
   │
   ├─► handle dependencies and type reference replacement
   │
   ├─► class layout and global variable allocation
   │
   ├─► Stage 3: compile the script code (CompileModule_Code_Stage3)
   │
   ├─► Stage 4: initialize global variables (CompileModule_Globals_Stage4)
   │
   ├─► module swap and hot reload (SwapInModules)
   │
   ├─► cleanup, post-processing, register tests
   │
   └─► return the compile result (ECompileResult)
```

There are four main stages plus N helper stages. The details are complicated, but focus on where the two preprocessing results go.

Final Angelscript code:

The script compiles to bytecode and runs through Angelscript’s own language machinery. I will not explain the VM here.

Reflection descriptions:

This deserves more attention. UClass describes a UObject in UE reflection. The plugin derives UASClass from UClass and adds more information. This is the stage that creates it.

One question makes the rest easier to understand: how is UASClass generated?

The call chain is:
InitialCompile()
   └─► CompileModules()
         └─► FAngelscriptClassGenerator::AddModule()
               └─► FAngelscriptClassGenerator::Setup()
                     └─► FAngelscriptClassGenerator::PerformSoftReload()/PerformFullReload()
                           └─► Generate and register UASClass

This happens during SwapInModules, near the end. The point is to ensure Angelscript compilation succeeds first: after Stage 4 runs without errors, update UE reflection. Sensible enough.

UASClass adds members and methods to connect UE and AS conveniently and make AS-type information available to C++.

For example, AS can declare DefaultComponent through UPROPERTY, a very comfortable feature!

Its data lives in UASClass’s `TArray<FDefaultComponent> DefaultComponents`. `FDefaultComponent` describes the reflected member. `OverrideComponents` works similarly.

```C++
	struct FDefaultComponent
	{
		UClass* ComponentClass;
		FName ComponentName;
		SIZE_T VariableOffset;
		bool bIsRoot;
		bool bEditorOnly;
		FName Attach;
		FName AttachSocket;
	};
```

The main bridges include UASStruct and UASFunction as well as UASClass. UASFunction has several variants.

Those bridges cover most scripting needs.

What about UEnum and delegate? Do they not need reflection?

They do, but UEnum is simple and has no dedicated subclass. There are no plans here to add more descriptive information. That makes some introspection harder, though still possible.

AS delegate/event declarations are actually preprocessed into structs.

The official FExampleEventSignature example becomes this large block:

```C++
struct FExampleEventSignature {_FMulticastScriptDelegate _Inner;FExampleEventSignature() __generated no_discard {}FExampleEventSignature(const FExampleEventSignature& Other) __generated no_discard { this = Other; }FExampleEventSignature& opAssign(const FExampleEventSignature& Other) __generated { _Inner = Other._Inner; return this; }void Broadcast(UObject Object, float Value) const __generated {if (!_Inner.IsBound()) return; __Evt_PushArgument__UObject(Object); __Evt_PushArgument__float(Value); __Evt_ExecuteDelegate(_Inner);}void AddUFunction(const UObject Object, const FName& FunctionName) __generated { _Inner.AddUFunction(Object, FunctionName, __DelegateSignature(this)); }void Unbind(UObject Object, const FName& FunctionName) __generated { _Inner.Unbind(Object, FunctionName); }void UnbindObject(UObject Object) __generated { _Inner.UnbindObject(Object); }bool IsBound() const __generated { return _Inner.IsBound(); }void Clear() __generated { _Inner.Clear(); }};
```

It looks messy, but is just a struct plus functions. It is generated in batches during preprocessing, not for people to read, so formatting is unnecessary.

Like UASClass, UASFunction adds descriptions. Different return values and other features lead to derived UASFunction variants overriding RuntimeCallFunction and RuntimeCallEvent.

That covers the types we commonly write in AS, in varying detail, enough for a broad picture.

For details, read the source — headache-inducing as it is. A friendly tip: do not immediately drown in the C++ implementation, particularly preprocessing code that manipulates characters to generate code. My reaction on opening it was: just browsing, sorry to disturb you, goodbye!

---
