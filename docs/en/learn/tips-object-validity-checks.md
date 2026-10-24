---
title: "UE_Angelscript — Tricks 3: if(Obj) or if(Obj != nullptr)? I pick if(Obj)"
order: 17
category: tips
---
# UE_Angelscript — Tricks 3: if(Obj) or if(Obj != nullptr)? I pick if(Obj)

# Preface

This is a complete `if(Obj)` solution: copy and paste it, with little C++ experience needed and no side effects.

Here, `Obj` means an instance of `UObject`.

Null checks are common in UE-Angelscript. The official recommendation is `if(Obj != nullptr)`, or `if(IsValid(Obj))` when GC matters.

In C++, however, we often write `if(Obj)`. UE’s own code frequently uses the implicit conversion of UObject pointers to bool.

Earlier articles showed using mixins for checks such as `if(Obj.IsNull)` or `if(Obj.IsValid)`. Pick whichever name you prefer. I add an underscore prefix to distinguish these from other mixins, giving that prefix a special meaning: a mixin that accepts nullptr.

Even with fluent, chained mixin calls, it is still less concise than C++.

After writing enough ifs, I decided to find time to simplify them. Although I am changing this restriction myself, I do not think HAZE’s decision to reject implicit conversion is wrong. Preferences differ.

Looking through the code, fully enabling implicit conversion for UObject appeared technically difficult and seemed to require changes in Angelscript’s internals. I am unwilling to go that far. I might edit the UE-Angelscript plugin, but not casually change the original third-party Angelscript library.

What about another approach?

I settled on a hook in preprocessing. Having previously added simulated lambdas to UE-Angelscript made this much easier.

This article gives the complete small change.

- Make three changes to open a preprocessor hook — a delegate — so external code can process raw AS source.
- Add a class anywhere, bind it to that delegate and register through static instantiation.
- It sounds involved, but copying the code is easy. Do not panic.

# 1. Modify AngelscriptPreprocessor

## Declare a delegate

Edit AngelscriptPreprocessor.h.
Where? Below the includes, among the similar declarations. Put it with them; exact order does not matter.

```cpp
// tart -- add a chance for handle raw files  DECLARE_MULTICAST_DELEGATE_OneParam(FBeforeAngelscriptParseFiles, struct FAngelscriptPreprocessor&);
// end -- add a chance for handle raw files
```

## Declare a function

Still in AngelscriptPreprocessor.h.

Inside `struct ANGELSCRIPTCODE_API FAngelscriptPreprocessor`, put a static function wherever convenient. I included public in case you forget; omit it if already in a public section.

```cpp
// start -- add a chance for handle raw files  static
public:
FBeforeAngelscriptParseFiles& BeforeAngelscriptParseFiles()
{
    static FBeforeAngelscriptParseFiles Instance;
    return Instance;
}
// end -- add a chance for handle raw files
```

Why wrap it in a function? First, unused code need not initialize and occupy memory. Second, I bind the delegate through static initialization later and need to avoid C++’s SIOF undefined behavior. Look it up if interested.

## Add the hook

Now edit AngelscriptPreprocessor.cpp.
Find the right place in `bool FAngelscriptPreprocessor::Preprocess()`. I included the surrounding code. The hook runs just after reading the .as file, before preprocessing starts.

```cpp
// Do asynchronous loads if we queued them
if (bLoadingAnyFilesAsynchronous)
    PerformAsynchronousLoads();

// start -- add a chance for handle raw files  BeforeAngelscriptParseFiles().Broadcast(*this);
// end -- add a chance for handle raw files

// First step, parse into chunks
for (FFile& File : Files)
    ParseIntoChunks(File);
```

The hook is now ready. Reuse it whenever raw code needs changing during preprocessing. Calling it is explained below.

# 2. Put these two files somewhere

Anywhere works, but I recommend the same folder as AngelscriptPreprocessor.cpp. That avoids include-path worries: copy them in and use them.

I named this file `IfStatementSugar.h`:

```cpp
#pragma once

#include "CoreMinimal.h"
#include "Preprocessor/AngelscriptPreprocessor.h"

/**
 * if (TestObj) --> if (TestObj != nullptr)
 * if (!TestObj) --> if (TestObj == nullptr)
 *
 * Only support simple if statement, such as if (!TestObj) or if (TestObj)
 * to keep it simple, there is a simple rule:
 * can not bind function "bool opImplConv() const" to any value type!
 * All your bool variables must begin with "b", we will skip these variables, otherwise maybe error
 * (we catch all bool variable names use patten "bool Var", and skip them)
 * From "if" to ")", can have white space or line feed, but can not have anything else such as comments!
 */
class FIfStatementSugar
{
public:
	FIfStatementSugar();
public:
	// Main entry: process all files, search for If Statement Sugar and expand them
	static void ProcessIfStatementSugar(TArray<FAngelscriptPreprocessor::FFile>& Files);

private:
	// Search for If Statement Sugar in a single file and expand them
	static void ProcessFile(FAngelscriptPreprocessor::FFile& File);
};
```

Naturally, the implementation is `IfStatementSugar.cpp`.
Keep the two together. The header need not be called externally. If you prefer another location, fine; as long as it compiles, this feature will work.

```cpp
#include "IfStatementSugar.h"

// only use to trigger to bind hook in Preprocessor
static FIfStatementSugar IfStatementSugar;

FIfStatementSugar::FIfStatementSugar()
{
    FAngelscriptPreprocessor::BeforeAngelscriptParseFiles().AddLambda([](FAngelscriptPreprocessor& Preprocessor)
    {
       ProcessIfStatementSugar(Preprocessor.Files);
    });
}

void FIfStatementSugar::ProcessIfStatementSugar(TArray<FAngelscriptPreprocessor::FFile>& Files)
{
    for (FAngelscriptPreprocessor::FFile& File : Files)
    {
       ProcessFile(File);
    }
}

void FIfStatementSugar::ProcessFile(FAngelscriptPreprocessor::FFile& File)
{
    FString& RawCode = File.RawCode;
    int32 SearchPos = 0;

    // 1. scan the file, search all the boolean declarations.
    TSet<FString> BoolVariables;

    //  R"( … )" is raw string literal
    // match boolean, for example: bool MyFlag; bool MyFlag = true; (bool MyFlag, bool TestFlag)
    static const FRegexPattern BoolPattern(TEXT(R"(\bbool\s+([A-Za-z_][A-Za-z0-9_]*)\s*(?:=.+?)?(?:;|,|\)))"));
    FRegexMatcher BoolMatcher(BoolPattern, RawCode);
    while (BoolMatcher.FindNext())
    {
       FString VarName = BoolMatcher.GetCaptureGroup(1).TrimStartAndEnd();
       if (!VarName.IsEmpty())
       {
          BoolVariables.Add(VarName);
       }
    }

    // 2. match if (VarName) or if (!VarName)
    static const FRegexPattern IfPattern(TEXT(R"(\bif\s*\(\s*(!)?\s*([A-Za-z_][A-Za-z0-9_]*)\s*\))"));

    while (true)
    {
       FRegexMatcher Matcher(IfPattern, RawCode.Mid(SearchPos));
       if (!Matcher.FindNext())
       {
          break;
       }

       int32 MatchBegin = SearchPos + Matcher.GetMatchBeginning();
       int32 MatchEnd = SearchPos + Matcher.GetMatchEnding();

       bool bNegated = !Matcher.GetCaptureGroup(1).IsEmpty(); // '!' captured
       FString VarName = Matcher.GetCaptureGroup(2);

       // Skip if variable is bool or starts with 'b'
       if (!VarName.StartsWith(TEXT("b")) && !BoolVariables.Contains(VarName))
       {
          FString Replacement;
          if (bNegated)
          {
             Replacement = FString::Printf(TEXT("if (%s == nullptr)"), *VarName);
          }
          else
          {
             Replacement = FString::Printf(TEXT("if (%s != nullptr)"), *VarName);
          }

          RawCode.RemoveAt(MatchBegin, MatchEnd - MatchBegin);
          RawCode.InsertAt(MatchBegin, Replacement);

          SearchPos = MatchBegin + Replacement.Len();
       }
       else
       {
          // Skip this match
          SearchPos = MatchEnd;
       }

       // Safety guard
       if (SearchPos >= RawCode.Len())
          break;
    }
}
```

## A short explanation

The idea is to receive the files and process them one at a time.

- Collect the names of bool variables declared in the current file with a regex. One unfinished detail: declarations inside comments match too. It hardly matters; if they produce an error, you will know to remove them. Store the results in `TSet<FString> BoolVariables`.
- Match `if (TestObj)` or `if (!TestObj)` with optional spaces. Ignore names starting with b and names collected in BoolVariables.
- Replace each match, then continue to the next until the end of the file.

This simple solution does not support operators such as `&&` or `||`.

The bool-name collection only covers declarations in the current file. A global bool from another file whose name does not start with b will cause an error. At least the error is obvious: bool cannot be compared with nullptr, telling you the naming convention is wrong. Do people really leave globals outside namespaces? Not a good habit.

# Summary

The approach is simple and has no side effects — no memory trouble or runtime crashes — so here it is for everyone. If a better way to support UObject-to-bool conversion arrives, no script changes are needed; just delete the two files.

This belongs among the tricks of the trade: bear with the language without it, enjoy it with it.

If one word clearly expresses a concept, why use several? A UObject that can compare with nullptr already has an existence/nonexistence concept. Implicit conversion follows naturally. That does not seem too abstract to explain even to less experienced programmers. That is just my view.

---
