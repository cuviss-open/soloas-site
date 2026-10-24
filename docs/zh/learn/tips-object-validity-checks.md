---
title: "UE_Angelscript 奇技淫巧3：选 if(Obj) 还是 if(Obj != nullptr)？秒选 if(Obj)"
order: 17
category: tips
---
# UE_Angelscript 奇技淫巧3：选 if(Obj) 还是 if(Obj != nullptr)？秒选 if(Obj)

# 前言

本文是完整的 `if(Obj)`解决方案，直接傻瓜式拷贝粘贴，无需多少 C++经验，无副作用。

本文的`Obj` 都是指代 `UObject` 的一个实例。

UE-Angelscript 脚本里，`Obj` 的判空是经常的事，官方推荐的写法是 `if(Obj != nullptr)`或者需要考虑 GC 时，使用`if(IsValid(Obj))`。

然而，我们在 c++中，经常是`if(Obj)` 的方式，UE 官方大量的代码都用了 UObject 指针相对于对 bool 的隐式转换。

之前的篇章里提到，我们可以通过 mixin 的方式做到这种判空，写起来或许更合口味 `if(Obj.IsNull)` 或者 `if(Obj.IsValid)`。这里的 IsNull 或者 IsValid 看个人喜好了，我会为了区别于其他的 mixin 函数，给加个下划线前缀。我给这种加了下划线前缀的 mixin 一种特殊的含义——可以接受 nullptr 的 mixin 函数。

然后，即使用到了 mixin 函数将书写更改为链式调用的方式，相对于 C++的简洁，也还是逊色了。

最终，在写了大量的 if 后，决定挑个时间，将其简化下来。（虽然我自己决定更改这种隐式转换的限制，但是我认为 HAZE 官方否决隐式转换的选择没错，毕竟各有偏好。）

经过查找相关的代码，我发现要彻底打开 UObject 类型的隐式转换还是有技术上的问题，似乎到修改到 Angelscript 的底层代码，这是我不愿意做的，我顶多修改 UE-Angelscript 这个插件，而不会轻易去修改原始的 Angelscript 第三方库。

那么换其他思路呢？

最终考虑，在预处理阶段开个口子算了，之前有给 UE-Angelscript 增加 Lambda 函数（模拟 ）的经验，所以这次开这个口子就简单了不少。

本文将完整地提供这个简单的修改。

- 修改增加三处修改，让预处理器开个口子（加个委托），可以让外部有机会处理 AS 原始代码。
- 之后增一个一个类，随便放在哪里，这个类绑定刚才开的口子（绑定委托），依靠静态类的实例化，来进行注册。
- 虽然说起来麻烦，但是拷贝代码还是方便的，莫慌。

# 1，修改 AngelscriptPreprocessor

## 声明一个委托

AngelscriptPreprocessor.h 里修改。
放在哪？#include 的下方，有一批类似的，就和他们组队放一起即可，前后无所谓啦。

```cpp
// tart -- add a chance for handle raw files  DECLARE_MULTICAST_DELEGATE_OneParam(FBeforeAngelscriptParseFiles, struct FAngelscriptPreprocessor&);
// end -- add a chance for handle raw files
```

## 声明一个函数

也是在 AngelscriptPreprocessor.h 里修改。

在这个类`struct ANGELSCRIPTCODE_API FAngelscriptPreprocessor`里，随便找个地方放上一个静态函数，我给写上 public 以免你忘了，如果是 public 区域，不加也没问题。

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

为什么封装为函数？一是因为不用的时候，无需初始化占内存，二是因为我后续用了静态初始化来绑定委托，需要杜绝 C++的一个未定义行为，叫做 SIOF，有兴趣的可以去看看。

## 加入钩子

这个要到 AngelscriptPreprocessor.cpp 里修改。
`bool FAngelscriptPreprocessor::Preprocess()`里找到合适的位置，这里将前后代码都加上了，这个钩子的时机是 .as 文件刚被读取完毕，预处理器还没进行处理的时候。

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

至此，钩子已经完成。以后只要你需要在预处理阶段修改原始代码，都可以复用它。至于调用的方式，请看下文。

# 2，随便找个地方放下方的两个文件

虽然说是随便找，但是我建议还是放在 AngelscriptPreprocessor.cpp 所在文件夹。为什么呢，因为这样你就不用考虑 `#include` 的问题了，拷贝了就能用。

这个文件名我取名为 `IfStatementSugar.h`

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

实现文件，自然文件名是 `IfStatementSugar.cpp`
这两个文件放在一起就好了，头文件也放这里，不需要被外部调用。当然，你非要放其他地方，随意啦，反正能编译通过，这个功能一定可以实现。

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
    // match boolean，for example：bool MyFlag; bool MyFlag = true; (bool MyFlag, bool TestFlag)
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

## 简单解析

这个操作的思路就是，获取文件后，一个一个处理文件。

- 收集当前文件里所有声明的 bool 类型的变量名，也是用正则匹配出来（这里留了一个待处理的，如果是注释里的也会匹配到，不过无所谓，反正报错了你自己会知道删掉，最终存入 `TSet<FString> BoolVariables`
- 在文件里用正则表达式来匹配` if (TestObj)` 或者 `if (!TestObj)`，支持有空格，凡是匹配到的，都做了判断，b 开头的不处理，BoolVariables 里收集了的，不处理。
- 分别对` if (TestObj)` 或者 `if (!TestObj)`进行替换，替换之后，再找下一个，循环直到文件结束。

此方案比较简单，就不支持运算符` &&` 和`||`这种了。

另外，虽然做了 bool 类型的变量名的收集处理，但是仅限于当前文件声明的，万一你用到了某个其他文件里的全局 bool 类型全局变量，而且这个变量还不是 b 开头的，那么会报错。（即使如此，报错也是很一目了解，bool 类型不能等于 nullptr，此时就知道命名不规范了。ps. 真有人用全局变量不做命名空间的限制吗？不是好习惯哎。）

# 总结

本文的方案，简单明了，不会有副作用（不会导致内存问题或运行时崩溃），所以随便放出来给大家用吧。如果某一天出现了更好的方式，让 UObject 全面支持隐式转换为 bool，那么，也不用修改代码，只是删掉两个文件的事情而已。

这个内容归入奇技淫巧，实至名归，无则隐忍，有则更佳。

如果用一个单词能清晰地表达一个概念，为什么要用多个呢？UObject 既然可以和 nullptr 比较，就是认为其自带有无的概念，那么隐式转换就可以自然而然，这个理解并不过分抽象，我认为可以给编程经验少的讲清楚。当然，这只是个人的观点。

---
