#!/usr/bin/env python3
"""Render reviewed API differences from the product policy; fail on unknown forms."""
import argparse
from concurrent.futures import ThreadPoolExecutor
import json
import os
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_POLICY = ROOT.parent / 'soloas/project/config/as-api-comparison.json'


def doc_projection(row):
    """Map a database declaration to its documentation spelling when exact."""
    kind, owner = row['kind'], row['owner'] or 'Global'
    if kind == 'type':
        base = row['value'].get('inherits')
        return 'type|' + owner + (' : public ' + base if base else '')
    if kind == 'namespace':
        return 'type|' + owner
    if kind == 'enum':
        return 'enum|' + owner
    if kind == 'enum-value':
        return f"enum-value|{owner}|{row['name']}"
    if kind in ('property', 'global-property'):
        typ = row['type'].replace('@', '').replace('&out', '&').replace('&in', '&')
        prefix = 'static ' if kind == 'global-property' else ''
        member = (owner + '::' if kind == 'global-property' and owner != 'Global' else '') + row['name']
        return f'{kind}|{owner}|{prefix}{typ} {member}'
    if kind in ('method', 'global-function'):
        value = row['value']
        prefix = 'static ' if kind == 'global-function' else ''
        member = (owner + '::' if kind == 'global-function' and owner != 'Global' else '') + value['name']
        args = []
        for arg in value['args']:
            typ = arg['type'].replace('@', '').replace('&inout', '&')
            text = typ + (' ' + arg['name'] if arg.get('name') else '')
            if 'default' in arg:
                text += ' = ' + arg['default']
            args.append(text)
        ret = value['return'].replace('@', '').replace('&inout', '&')
        decl = f'{prefix}{ret} {member}(' + ', '.join(args) + ')'
        if value.get('const'):
            decl += ' const'
        return f'{kind}|{owner}|' + decl
    return None


def examples_by_owner(rows, limit=5):
    """Choose deterministic examples across owners before taking a second from any owner."""
    chosen, owners = [], set()
    for row in sorted(rows):
        owner = row[0].split('::')[0]
        if owner not in owners:
            chosen.append(row)
            owners.add(owner)
        if len(chosen) == limit:
            return chosen
    return (chosen + [row for row in sorted(rows) if row not in chosen])[:limit]


def distribution_examples(rows, limit=5):
    """Prefer different declaration kinds and never repeat a top-level owner."""
    selected, owners = [], set()
    ordered = sorted(rows, key=lambda row: (row[0] == 'type' and row[1].startswith('E'), row))
    for kind in ('enum', 'type', 'global-function', 'method', 'property', 'enum-value'):
        for row_kind, owner, label in ordered:
            if row_kind == kind and owner not in owners:
                selected.append(label)
                owners.add(owner)
                break
        if len(selected) == limit:
            return selected
    for _, owner, label in ordered:
        if owner not in owners:
            selected.append(label)
            owners.add(owner)
        if len(selected) == limit:
            break
    return selected


def render(policy, language):
    entries = policy['partitions']['fork']
    presentation = policy['publicPresentation']
    groups = {}
    for entry in entries:
        category = entry['category']
        if category not in ('upstream-bug-fix', 'non-api-engine-distribution', 'non-api-loading-timing'):
            raise ValueError(f'Unreviewed public difference category: {category}')
        if category not in presentation:
            raise ValueError(f'No public presentation for {category}')
        if category == 'upstream-bug-fix' and entry['reason'] != presentation[category]['reason']:
            raise ValueError('New bug-fix difference needs reviewed public wording')
        groups.setdefault(category, []).append(entry)
    if language == 'zh':
        lines = ['# soloAS 最新版与 UE-AS fork 的 API 差异', '',
                 '本页概述 soloAS 最新版与 UE-AS fork 的 API 差异，并列出代表性例子。未提及的差异类别与 UE-AS fork 一致。', '',
                 '## 默认参数', '']
    else:
        lines = ['# API differences between the latest soloAS and the UE-AS fork', '',
                 'This page summarizes API differences between the latest soloAS and the UE-AS fork with representative examples. Areas not mentioned match the UE-AS fork.', '',
                 '## Default arguments', '']
    fixes = groups.get('upstream-bug-fix', [])
    # Each collector must have the exact inverse record, not just matching counts.
    for entry in fixes:
        opposite = 'removed' if entry['direction'] == 'added' else 'added'
        if not any(other['collector'] == entry['collector'] and other['direction'] == opposite
                   and other['record'] == entry.get('counterpart')
                   and other.get('counterpart') == entry['record'] for other in fixes):
            raise ValueError('Unpaired default difference requires review')
    if len(fixes) != 4 * sum(e['collector'] == 'docs' and e['direction'] == 'added' for e in fixes):
        raise ValueError('Unpaired default differences require review')
    rows = set()
    for entry in (e for e in fixes if e['collector'] == 'docs' and e['direction'] == 'added'):
        kind, owner, declaration = entry['record'].split('|', 2)
        function = re.search(r'\b([A-Za-z_]\w*(?:::\w+)?)\(', declaration)
        defaults = re.findall(r'FName (\w+) = FName \( "([^"]+)" \)', declaration)
        if kind not in ('method', 'global-function') or not function or not defaults:
            raise ValueError('New default difference requires review')
        expected = entry['record']
        for name, value in defaults:
            expected = expected.replace(f'FName {name} = FName ( "{value}" )', f'FName {name} = FName ( "" )')
            rows.add((function.group(1) if '::' in function.group(1) else owner + '::' + function.group(1), name, value))
        if expected != entry['counterpart']:
            raise ValueError('New default difference requires review')
    if fixes and ('VisualLogger::LogArrow', 'CategoryName', 'VisLogBP') not in rows:
        raise ValueError('Default argument example requires review')
    lines += [
        ('**有什么不同：**省略下表中的参数时，soloAS 传入表中列出的值；UE-AS fork 传入空名称（`NAME_None`）。' if language == 'zh' else
         '**Difference:** When a parameter below is omitted, soloAS passes the value listed in the table; the UE-AS fork passes an empty name (`NAME_None`).'),
        '',
        ('**为什么：有意改进。**UE-AS fork 对这些默认值的处理有缺陷；soloAS 按原生声明的默认值传参。' if language == 'zh' else
         '**Why: Intentional improvement.** The UE-AS fork handles these defaults incorrectly; soloAS passes the defaults from the native declarations.'),
        '',
        ('**需要注意：**要让两边行为一致，请显式传入参数。' if language == 'zh' else
         '**What to do:** Pass the argument explicitly for consistent behavior across both implementations.'),
        '', (f'共 {len({row[0] for row in rows})} 个函数；以下为例子。' if language == 'zh' else f'{len({row[0] for row in rows})} functions in total; examples are shown below.'), '', '```angelscript',
        'VisualLogger::LogArrow(WorldContextObject, SegmentStart, SegmentEnd, Text);',
        ('// soloAS 收到的 CategoryName: FName("VisLogBP")' if language == 'zh' else '// soloAS receives CategoryName: FName("VisLogBP")'),
        ('// UE-AS fork 收到的 CategoryName: NAME_None' if language == 'zh' else '// UE-AS fork receives CategoryName: NAME_None'),
        '```', '',
        ('| 函数 | 参数名 | soloAS 默认值 |' if language == 'zh' else '| Function | Parameter | soloAS default |'),
        '| --- | --- | --- |']
    for function, name, value in examples_by_owner(rows):
        lines.append(f'| `{function}` | `{name}` | `FName("{value}")` |')
    lines += ['', '## 引擎插件提供的接口' if language == 'zh' else '## Interfaces supplied by engine plugins', '',
              ('原版 UE 默认安装包含更多配套插件，其接口可在 soloAS 中使用；所比较的 UE-AS fork 安装中没有这些插件，因此不算 API 差异。实际可用性取决于引擎安装及插件是否启用。' if language == 'zh' else
               'A standard UE installation includes more bundled plugins whose APIs are available in soloAS; these plugins are absent from the compared UE-AS fork installation, so they are not API differences. Availability depends on the engine installation and whether the plugins are enabled.'), '']
    distribution = groups.get('non-api-engine-distribution', [])
    documented = {entry['record'] for entry in distribution if entry['collector'] == 'docs'}
    distribution_rows = {}
    examples = []
    for entry in distribution:
        source = entry['proof']['presentSource']['path'].split('/')
        if len(source) < 4 or source[:2] != ['Engine', 'Plugins'] or entry['direction'] != 'added':
            raise ValueError('New engine-distribution difference requires review')
        if entry['collector'] == 'docs':
            parts = entry['record'].split('|', 2)
            label = parts[1] if len(parts) == 2 else parts[1] + ' · ' + parts[2]
        elif entry['collector'] == 'db':
            row = entry['record']
            if doc_projection(row) in documented:
                continue
            value = row.get('value', {})
            name = row.get('name') or value.get('name') or ''
            label = row.get('owner', '') + ('::' if row.get('owner') and name else '') + name
            if 'args' in value:
                label += '(' + ', '.join(arg['type'] + (' ' + arg['name'] if arg.get('name') else '') + (' = ' + arg['default'] if 'default' in arg else '') for arg in value['args']) + ')'
            if row.get('type'):
                label += ' : ' + row['type']
            if not label:
                raise ValueError('Unrenderable API difference')
        else:
            raise ValueError('Unknown collector')
        distribution_rows[entry['record'] if entry['collector'] == 'docs' else doc_projection(row) or label] = label
        kind, owner = (parts[:2] if entry['collector'] == 'docs' else (row['kind'], row.get('owner') or 'Global'))
        examples.append((kind, owner.split('::')[0], label))
    if distribution_rows:
        lines += [(f'共 {len(distribution_rows)} 项接口；以下为例子。' if language == 'zh' else f'{len(distribution_rows)} interfaces in total; examples are shown below.'), '']
        lines.extend(f'- `{label}`' for label in distribution_examples(examples))
        lines.append('')
    timing = groups.get('non-api-loading-timing', [])
    if timing:
        expected_reason = ('Identical native declarations become visible before AS binding in the project-plugin discovery slot; '
                           'the engine-plugin fork initializes AS before this PostDefault owner module. Signature changes are excluded.')
        modules = set()
        for entry in timing:
            if entry['direction'] != 'added' or entry['reason'] != expected_reason:
                raise ValueError('Unreviewed loading-timing difference')
            if entry['collector'] not in ('docs', 'db'):
                raise ValueError('Unknown collector')
            module = entry['proof']['module']
            if not isinstance(module, str) or not module.strip():
                raise ValueError('Loading-timing difference needs a module')
            modules.add(module)
        lines += ['## 加载时机（非 API 差异）' if language == 'zh' else '## Loading timing (not an API difference)', '',
                  ('以下模块中的部分原生声明在两端完全相同，但 soloAS 作为项目插件初始化时这些模块已加载，因此可供脚本使用；UE-AS fork 在这些模块加载前就已初始化脚本绑定，所以用不到。声明和签名本身没有差异。' if language == 'zh' else
                   'Some native declarations in the following modules are identical on both sides. These modules are already loaded when soloAS initializes as a project plugin, so the declarations are available to scripts; UE-AS fork initializes script bindings before these modules load, so they are unavailable there. The declarations and signatures themselves do not differ.'), '',
                  (f'共 {len(modules)} 个模块；以下为例子。' if language == 'zh' else f'{len(modules)} modules in total; examples are shown below.'), '']
        lines.extend(f'- `{module}`' for module in sorted(modules)[:5])
        lines.append('')
    residuals = [item for item in policy.get('nativeCallResiduals', [])
                 if policy.get('engineVersion', '5.8.4') in item['ueVersions']]
    if residuals:
        lines += ['## 原生调用行为' if language == 'zh' else '## Native call behavior', '']
        seen = set()
        if len(residuals) > 5:
            lines += [(f'共 {len(residuals)} 项；以下为例子。' if language == 'zh' else f'{len(residuals)} differences in total; examples are shown below.'), '']
        for index, item in enumerate(sorted(residuals, key=lambda row: row['id'])):
            if item['id'] in seen:
                raise ValueError('Duplicate native call difference ID')
            seen.add(item['id'])
            wording = item['text']
            categories = {'technical': ('技术限制：', 'Technical limitation:'),
                          'improvement': ('有意改进：', 'Intentional improvement:')}
            matches = [prefixes for prefixes in categories.values()
                       if all(wording[lang]['why'].startswith(prefix)
                              for lang, prefix in zip(('zh', 'en'), prefixes))]
            reviewed_plain_reasons = {
                'avalanche.get-parametric-material.invalid-index-default': ('安装版引擎没有导出原函数，无法取得它的默认对象地址。', 'The installed engine does not export the original function, so its default object address is unavailable.'),
                'texturegraph.render-texture-graph.return-copy': ('安装版引擎没有导出能取得原数组引用的函数入口。', 'The installed engine does not export the function entry needed to obtain the original array reference.'),
                'usertoolbox.get-brush-by-id.unexported-reference': ('安装版引擎没有导出 GetBrushById、所属类和静态 DefaultBrush；原函数也不是内联函数。公开接口无法取得该函数返回的私有默认对象地址。', 'The installed engine exports neither GetBrushById, its owning class, nor the static DefaultBrush, and the function is not inline. Public interfaces cannot obtain the private default object address returned by this function.'),
                'usertoolbox.get-brush-by-style-and-id.unexported-reference': ('安装版引擎没有导出 GetBrushByStyleAndId、所属类和静态 DefaultBrush；原函数也不是内联函数。公开接口无法取得该函数返回的私有默认对象地址。', 'The installed engine exports neither GetBrushByStyleAndId, its owning class, nor the static DefaultBrush, and the function is not inline. Public interfaces cannot obtain the private default object address returned by this function.'),
            }
            plain_reason = (wording['zh']['why'], wording['en']['why'])
            if len(matches) != 1 and reviewed_plain_reasons.get(item['id']) != plain_reason:
                raise ValueError('Native call difference needs matching reviewed reason categories')
            signatures = all(isinstance(item.get(key), str) and item[key].strip()
                             for key in ('cppSignature', 'asSignature'))
            source_only = (item['id'] in reviewed_plain_reasons and
                           'cppSignature' not in item and 'asSignature' not in item and
                           isinstance(item.get('signature'), str) and item['signature'].strip())
            if not signatures and not source_only:
                raise ValueError('Native call difference needs C++ and AS signatures')
            if any(not isinstance(wording.get(lang, {}).get(key), str) or not wording[lang][key].strip()
                   for lang in ('zh', 'en') for key in ('what', 'why', 'impact')):
                raise ValueError('Native call difference needs complete bilingual wording')
            if index >= 5:
                continue
            text = wording[language]
            labels = ('**有什么不同：**', '**为什么：**', '**需要注意：**') if language == 'zh' else (
                '**Difference:** ', '**Why:** ', '**Impact:** ')
            lines += ['### ' + item['owner'] + '::' + item['function'], '']
            if signatures:
                lines += ['```angelscript', '// C++', item['cppSignature'],
                          '// AngelScript', item['asSignature'], '```', '']
            else:
                lines += ['```cpp', item['signature'], '```', '']
            lines += [labels[0] + text['what'], '', labels[1] + text['why'], '', labels[2] + text['impact'], '']
    if any(e['collector'] not in ('docs', 'db') for e in entries):
        raise ValueError('Unknown collector')
    lines += [('[不同 UE 版本的适配差异](ue-version-differences.md)' if language == 'zh' else
               '[Adaptation differences across UE versions](ue-version-differences.md)'), '']
    return '\n'.join(lines)


def run(policy_path, check=False):
    policy = json.loads(policy_path.read_text(encoding='utf-8'))
    # The two languages are independent and must have identical source entries.
    languages = ('zh', 'en')
    with ThreadPoolExecutor(max_workers=min(len(languages), os.cpu_count() or 1)) as executor:
        rendered = dict(zip(languages, executor.map(lambda lang: render(policy, lang), languages)))
    for language, content in rendered.items():
        path = ROOT / 'docs' / language / 'api-differences.md'
        if check:
            if not path.is_file() or path.read_text(encoding='utf-8') != content:
                raise ValueError(f'Generated API differences are out of date: {path}')
        else:
            path.write_text(content, encoding='utf-8')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--policy', type=Path, default=Path(os.environ.get('SOLOAS_API_POLICY', DEFAULT_POLICY)))
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    run(args.policy, args.check)
    print('API differences match.' if args.check else 'API differences rendered.')


if __name__ == '__main__':
    main()
