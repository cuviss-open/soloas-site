#!/usr/bin/env python3
"""Build the soloAS Pages artifact offline with Python 3's standard library.

Supported Markdown: headings/anchors, paragraphs, fenced code, tables, ordered
and unordered lists, blockquotes, links, emphasis, inline code and rules.
Raw HTML is escaped. Relative .md links become .html in the web output.
"""
from pathlib import Path
import html
import os
import re
import shutil
import json
import subprocess
from collections import Counter
from datetime import datetime
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
CONFIG = json.loads((ROOT / 'tools/site_config.json').read_text())
LANGUAGES = CONFIG['languages']
CHROME_CSS = (ROOT / 'tools/site-chrome.css').read_text()
VERSION_HIGHLIGHT_CSS = (
    '.ver{color:inherit;font-weight:700;font-style:italic}\n'
)
PAGES = [
    ('overview', 'About soloAS', '项目介绍'),
    ('requirements', 'Environment setup and quick start', '环境配置与快速上手'),
    ('soloas-menu', 'The SoloAS menu', 'SoloAS 菜单'),
    ('changelog', 'Changelog', '更新日志'),
    ('migration', 'Migrating an existing AS project', '迁移已有 AS 项目'),
    ('features', 'Feature overview', '功能一览'),
    ('core', 'Plugin core', '插件核心'),
    ('ue-version-differences', 'Adaptation Differences Across Unreal Engine Versions', '不同 UE 版本的适配差异'),
    ('api-differences', 'API differences between the latest soloAS and the UE-AS fork', 'soloAS 最新版与 UE-AS fork 的 API 差异'),
    ('manual-binding-packs', 'Manual binding packs', '手工绑定包'),
    ('packaging', 'Packaging', '项目打包'),
    ('license', 'Community', '社区贡献'),
    ('extensions', 'Core extensions', '核心扩展'),
    ('dynamic-modules', 'Feature Mods', '功能模组'),
    ('core-manual-bindings', 'Manual binding core', '手工绑定核心'),
    ('auto-binding', 'Auto binding', '自动绑定'),
    ('ai-assisted', 'AI-assisted development', 'AI 辅助开发'),
]


def secure_external_links(page):
    page = page.replace("https://github.com/cuviss-open/soloAS", CONFIG["links"]["repository"])
    page = page.replace("https://discord.gg/D8W94mvMMU", CONFIG["links"]["discord"])
    def update(match):
        tag = match.group(0)
        href = re.search(r'\bhref="([^"]*)"', tag, re.I)
        if not href:
            return tag
        parsed = urlsplit(html.unescape(href.group(1)))
        if parsed.scheme not in {'', 'http', 'https'} or not parsed.netloc or (parsed.hostname or '').lower() == 'soloas.cuviss.com':
            return re.sub(r'\s+target="[^"]*"', '', tag)
        target = re.search(r'\s+target="[^"]*"', tag, re.I)
        if target:
            tag = tag[:target.start()] + ' target="_blank"' + tag[target.end():]
        else:
            tag = tag[:-1] + ' target="_blank">'
        rel = re.search(r'\s+rel="([^"]*)"', tag, re.I)
        tokens = set(rel.group(1).lower().split()) if rel else set()
        tokens.update({'noopener', 'noreferrer'})
        value = ' '.join(sorted(tokens))
        if rel:
            tag = tag[:rel.start()] + f' rel="{value}"' + tag[rel.end():]
        else:
            tag = tag[:-1] + f' rel="{value}">'
        return tag
    return re.sub(r'<a\b[^>]*>', update, page, flags=re.I)
DOC_NAV = [
    ('page', 'overview', 'About soloAS', '项目介绍'),
    ('page', 'requirements', 'Environment setup and quick start', '环境配置与快速上手'),
    ('page', 'soloas-menu', 'The SoloAS menu', 'SoloAS 菜单'),
    ('page', 'changelog', 'Changelog', '更新日志'),
    ('page', 'migration', 'Migrating an existing AS project', '迁移已有 AS 项目'),
    ('page', 'features', 'Feature overview', '功能一览'),
    ('page', 'core', 'Plugin core', '插件核心'),
    ('page', 'ue-version-differences', 'Adaptation Differences Across Unreal Engine Versions', '不同 UE 版本的适配差异'),
    ('page', 'api-differences', 'API differences between the latest soloAS and the UE-AS fork', 'soloAS 最新版与 UE-AS fork 的 API 差异'),
    ('page', 'extensions', 'Core extensions', '核心扩展'),
    ('page', 'dynamic-modules', 'Feature Mods', '功能模组'),
    ('pending', 'core-manual-bindings', 'Manual binding core', '手工绑定核心'),
    ('pending', 'auto-binding', 'Auto binding', '自动绑定'),
    ('page', 'manual-binding-packs', 'Manual binding packs', '手工绑定包'),
    ('page', 'packaging', 'Packaging', '项目打包'),
    ('page', 'ai-assisted', 'AI-assisted development', 'AI 辅助开发'),
]
PENDING_PAGES = {item[1] for item in DOC_NAV if item[0] == 'pending'}
CATEGORY_ORDER = ('getting-started', 'concepts', 'tips', 'essays', 'practice', 'internals', 'binding')
CATEGORY_LABELS = {
    'en': {
        'getting-started': 'Getting started',
        'concepts': 'Concepts',
        'tips': 'Tips',
        'essays': 'Essays',
        'practice': 'Practice',
        'internals': 'Internals',
        'binding': 'Binding',
    },
    'zh': {
        'getting-started': '入门',
        'concepts': '概念',
        'tips': '技巧',
        'essays': '思考',
        'practice': '实践',
        'internals': '内部机制',
        'binding': '绑定',
    },
}

VERSION_NUMBER = r"\d+\.\d+(?:\.\d+)?"
VERSION_DELIMITER = r"(?:[–—-]|\b(?:to|through|and|or)\b|[,，、和])"
UE_VERSION_RE = re.compile(
    rf"(?<![\w])(?:UE|Unreal Engine)\s+{VERSION_NUMBER}"
    rf"(?:\s*{VERSION_DELIMITER}\s*(?:(?:UE|Unreal Engine)\s+)?{VERSION_NUMBER})*"
    r"(?![\w]|\.\d)",
    re.I,
)
SOLOAS_VERSION_RE = re.compile(
    rf"(?<![\w])soloAS\s+v?{VERSION_NUMBER}(?![\w]|\.\d)", re.I
)
VERSION_BRANCH_RE = re.compile(r"(?<![\w.])0\.\d+\.x(?![\w.])", re.I)
VERSION_TAG_RE = re.compile(r"(?<![\w.])v0\.3\.0(?![\w]|\.\d)", re.I)
CHANGELOG_VERSION_RE = re.compile(
    rf"(?<![\w.]){VERSION_NUMBER}\s+·\s+(?:UE|Unreal Engine)\s+{VERSION_NUMBER}"
    rf"(?:\s*(?:[–—-]|\b(?:to|through|and|or)\b|[,，、])\s*{VERSION_NUMBER})*"
    r"(?![\w]|\.\d)",
    re.I,
)
VERSION_TABLE_CELL_RE = re.compile(
    r"\s*5\.[4-8](?:\.\d+)?"
    r"(?:\s*(?:[–—-]|\b(?:to|through|and|or)\b|[,，、])\s*5\.[4-8](?:\.\d+)?)*\s*",
    re.I,
)
URL_RE = re.compile(r"(?i)\b(?:https?|ftp|mailto):[^\s<>()]+")
VERSION_SPAN_RE = re.compile(r'<span class="ver">.*?</span>')
RAW_HTML_TAG_RE = re.compile(r"(?s)<!--.*?-->|<![^>]*>|</?[A-Za-z][^>]*>")
RAW_HTML_CODE_RE = re.compile(r"(?is)<(pre|code|title|script|style)\b[^>]*>.*?</\1\s*>")
HTML_PROTECTED_TAGS = {"code", "pre", "title", "script", "style"}
HTML_VOID_TAGS = {
    "area", "base", "br", "col", "embed", "hr", "img", "input", "link",
    "meta", "param", "source", "track", "wbr",
}


def slug(text):
    text = re.sub(r'[`*_]', '', text).lower()
    text = re.sub(r'[^\w\s-]', '', text)
    return re.sub(r'\s+', '-', text.strip())


def mark_versions(source, version_cell=False):
    """Wrap only known SoloAS/Unreal version forms in visible source text."""
    candidates = []
    for priority, pattern in enumerate((
        UE_VERSION_RE,
        SOLOAS_VERSION_RE,
        VERSION_BRANCH_RE,
        VERSION_TAG_RE,
        CHANGELOG_VERSION_RE,
    )):
        candidates.extend((match.start(), match.end(), priority) for match in pattern.finditer(source))
    if version_cell and VERSION_TABLE_CELL_RE.fullmatch(source):
        candidates.append((0, len(source), 10))

    urls = [match.span() for match in URL_RE.finditer(source)]
    chosen = []
    for start, end, priority in sorted(candidates, key=lambda item: (-(item[1] - item[0]), -item[2], item[0])):
        if any(start < url_end and end > url_start for url_start, url_end in urls):
            continue
        if any(start < chosen_end and end > chosen_start for chosen_start, chosen_end in chosen):
            continue
        chosen.append((start, end))
    if not chosen:
        return source

    parts = []
    cursor = 0
    for start, end in sorted(chosen):
        parts.append(source[cursor:start])
        parts.append('<span class="ver">' + source[start:end] + '</span>')
        cursor = end
    parts.append(source[cursor:])
    return ''.join(parts)


def mark_html_text(source):
    """Apply version spans to HTML text nodes while preserving markup verbatim."""
    parts, protected = [], []
    cursor = 0
    for match in RAW_HTML_TAG_RE.finditer(source):
        text = source[cursor:match.start()]
        parts.append(text if any(tag in HTML_PROTECTED_TAGS for tag in protected) else mark_versions(text))
        tag = match.group(0)
        parts.append(tag)
        tag_match = re.match(r"<\s*(/?)\s*([A-Za-z][\w:-]*)", tag)
        if tag_match:
            closing, name = tag_match.groups()
            name = name.lower()
            if closing:
                for index in range(len(protected) - 1, -1, -1):
                    if protected[index] == name:
                        del protected[index:]
                        break
            elif name not in HTML_VOID_TAGS and not tag.rstrip().endswith('/>'):
                protected.append(name)
        cursor = match.end()
    text = source[cursor:]
    parts.append(text if any(tag in HTML_PROTECTED_TAGS for tag in protected) else mark_versions(text))
    return ''.join(parts)


def inline(source, tokens=None, mark_version_text=True, version_cell=False):
    if tokens is None:
        tokens = []

    def keep(value):
        tokens.append(value)
        return f'\x00{len(tokens) - 1}\x00'

    source = re.sub(r'`([^`]+)`', lambda m: keep('<code>' + html.escape(m[1]) + '</code>'), source)

    def picture(match):
        label, url = match[1], match[2]
        if re.match(r'(?i)(?:javascript|data|vbscript):', url):
            raise ValueError('Unsafe Markdown image URL')
        return keep(f'<img src="{html.escape(url, quote=True)}" alt="{html.escape(label, quote=True)}" loading="lazy">')

    source = re.sub(r'!\[([^\]]*)\]\(([^\s)]+)\)', picture, source)

    def link(match):
        label, url = match[1], match[2]
        if re.match(r'(?i)(?:javascript|data|vbscript):', url):
            raise ValueError('Unsafe Markdown URL')
        url = re.sub(r'\.md(?=#|$)', '.html', url)
        return keep(f'<a href="{html.escape(url, quote=True)}">{inline(label, tokens, mark_version_text, version_cell)}</a>')

    source = re.sub(r'\[([^\]]+)\]\(([^\s)]+)\)', link, source)
    source = RAW_HTML_CODE_RE.sub(lambda m: keep(html.escape(m[0])), source)
    source = RAW_HTML_TAG_RE.sub(lambda m: keep(html.escape(m[0])), source)
    source = URL_RE.sub(lambda m: keep(html.escape(m[0])), source)
    if mark_version_text:
        source = mark_versions(source, version_cell=version_cell)
        source = VERSION_SPAN_RE.sub(lambda m: keep(m[0]), source)
    source = html.escape(source)
    source = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', source)
    source = re.sub(r'(?<!\*)\*([^*]+)\*(?!\*)', r'<em>\1</em>', source)
    return re.sub(r'\x00(\d+)\x00', lambda m: tokens[int(m[1])], source)


def render(source, mark_version_text=True, version_table=False):
    # HTML comments are source metadata and never appear in the built pages.
    source = re.sub(r'<!--[\s\S]*?-->', '', source)
    lines = source.splitlines()
    output, toc, anchors = [], [], {}
    i = 0
    while i < len(lines):
        line = lines[i]
        if not line.strip():
            i += 1
            continue
        if line.strip().startswith('<svg') and line.strip().endswith('</svg>'):
            output.append(line.strip())
            i += 1
            continue
        if line.strip() == '<picture>':
            picture = [line]
            i += 1
            while i < len(lines):
                picture.append(lines[i])
                if lines[i].strip() == '</picture>':
                    break
                i += 1
            if picture[-1].strip() != '</picture>':
                raise ValueError('Unclosed picture element')
            output.append('\n'.join(picture))
        elif re.match(r'^ {0,3}```', line):
            language = line.lstrip()[3:].strip()
            code = []
            i += 1
            while i < len(lines) and not re.match(r'^ {0,3}```', lines[i]):
                code.append(lines[i])
                i += 1
            if i == len(lines):
                raise ValueError('Unclosed code fence')
            output.append(f'<pre tabindex="0"><code class="language-{html.escape(language, quote=True)}">' + html.escape('\n'.join(code)) + '</code></pre>')
        elif match := re.match(r'^(#{1,6})\s+(.+)$', line):
            level, label = len(match[1]), match[2]
            anchor = slug(label)
            count = anchors.get(anchor, 0)
            anchors[anchor] = count + 1
            if count:
                anchor += f'-{count}'
            output.append(f'<h{level} id="{anchor}">{inline(label, mark_version_text=mark_version_text)}<a class="anchor" href="#{anchor}" aria-label="Permalink">#</a></h{level}>')
            if level in (2, 3):
                toc.append(f'<a class="toc-h{level}" href="#{anchor}">{inline(label, mark_version_text=mark_version_text)}</a>')
        elif i + 1 < len(lines) and '|' in line and re.match(r'^\s*\|?\s*:?-{3,}', lines[i + 1]):
            def cells(row):
                return [inline(c.strip(), mark_version_text=mark_version_text, version_cell=version_table)
                        for c in row.strip().strip('|').split('|')]
            heads = cells(line)
            output.append('<div class="table-wrap"><table><thead><tr>' + ''.join('<th scope="col">' + c + '</th>' for c in heads) + '</tr></thead><tbody>')
            i += 2
            while i < len(lines) and '|' in lines[i] and lines[i].strip():
                output.append('<tr>' + ''.join('<td>' + c + '</td>' for c in cells(lines[i])) + '</tr>')
                i += 1
            output.append('</tbody></table></div>')
            continue
        elif match := re.match(r'^\s*(?:([-+*])|\d+\.)\s+(.+)$', line):
            ordered = match[1] is None
            tag = 'ol' if ordered else 'ul'
            start = re.match(r'^\s*(\d+)\.', line) if ordered else None
            start_attr = f' start="{start[1]}"' if start and start[1] != '1' else ''
            output.append(f'<{tag}{start_attr}>')
            while i < len(lines):
                item = re.match(r'^\s*(?:([-+*])|\d+\.)\s+(.+)$', lines[i])
                if not item or (item[1] is None) != ordered:
                    break
                text = [item[2]]
                i += 1
                while i < len(lines) and lines[i].startswith('  ') and lines[i].strip() and not re.match(r'^\s*(?:[-+*]|\d+\.)\s', lines[i]) and not re.match(r'^ {0,3}```', lines[i]):
                    text.append(lines[i].strip())
                    i += 1
                output.append('<li>' + inline(' '.join(text), mark_version_text=mark_version_text) + '</li>')
            output.append(f'</{tag}>')
            continue
        elif line.startswith('> 注：') or line.startswith('> Note: '):
            output.append('<p class="doc-aside">' + inline(line[2:], mark_version_text=mark_version_text) + '</p>')
            i += 1
        elif line in ('> **soloAS 注**', '> **soloAS note**'):
            label = line[4:-2]
            note = []
            i += 1
            while i < len(lines) and lines[i].startswith('> '):
                note.append(lines[i][2:])
                i += 1
            output.append('<aside class="soloas-note" aria-label="' + html.escape(label) + '"><span class="soloas-note-label">' + html.escape(label) + '</span><p>' + inline(' '.join(note), mark_version_text=mark_version_text) + '</p></aside>')
            continue
        elif line.startswith('> '):
            output.append('<blockquote><p>' + inline(line[2:], mark_version_text=mark_version_text) + '</p></blockquote>')
        elif re.match(r'^\s*(?:---+|\*\*\*+)\s*$', line):
            output.append('<hr>')
        else:
            paragraph = [line]
            i += 1
            while i < len(lines) and lines[i].strip() and not re.match(r'^(?:#|```|>|\s*[-+*]\s|\s*\d+\.\s)', lines[i]):
                paragraph.append(lines[i])
                i += 1
            output.append('<p>' + inline(' '.join(paragraph), mark_version_text=mark_version_text) + '</p>')
            continue
        i += 1
    return '\n'.join(output), '\n'.join(toc)


def article(source):
    """Read the Learn category and order front matter without a YAML dependency."""
    order = 10000
    category = None
    if source.startswith('---\n'):
        _, metadata, source = source.split('---', 2)
        match = re.search(r'^order:\s*(\d+)\s*$', metadata, re.MULTILINE)
        if match:
            order = int(match[1])
        match = re.search(r'^category:\s*([a-z-]+)\s*$', metadata, re.MULTILINE)
        if match:
            category = match[1]
    if category not in CATEGORY_ORDER:
        raise ValueError(f'Learn article has missing or unknown category: {category!r}')
    heading = re.search(r'^#\s+(.+)$', source, re.MULTILINE)
    if not heading:
        raise ValueError('Article is missing an H1 title')
    return category, order, heading[1], source


def link(key, label, current, prefix):
    selected = ' aria-current="page"' if key == current else ''
    return f'<a href="{prefix}{key}.html"{selected}>{html.escape(label)}</a>'


def navigation(lang, current, learning):
    learning_page = current.startswith('learn/')
    docs_label = 'Documentation' if lang == 'en' else '使用文档'
    learn_label = 'Articles' if lang == 'en' else '相关文章'
    docs_name = 'Documentation' if lang == 'en' else '使用文档'
    learn_name = learn_label
    prefix = '../' if current.startswith('learn/') else ''

    docs = []
    for item in DOC_NAV:
        kind = item[0]
        if kind == 'page':
            _, key, en, zh = item
            docs.append(link(key, en if lang == 'en' else zh, current, prefix))
            continue
        if kind == 'pending':
            _, key, en, zh = item
            suffix = ' (coming soon)' if lang == 'en' else '（待发布）'
            docs.append(f'<span class="nav-pending" aria-disabled="true">{html.escape(en if lang == "en" else zh)}{suffix}</span>')
            continue
        _, en_label, zh_label, pages = item
        expanded = ' open' if any(page[0] == current for page in pages) else ''
        items = ''.join(link(page_key, page_en if lang == 'en' else page_zh, current, prefix)
                        for page_key, page_en, page_zh in pages)
        label = en_label if lang == 'en' else zh_label
        docs.append(
            f'<details class="nav-category"{expanded}><summary>{html.escape(label)}</summary>'
            f'<nav aria-label="{html.escape(label)}">{items}</nav></details>'
        )
    docs = ''.join(docs)
    learn = [link('learn/index', 'Contents' if lang == 'en' else '文章目录', current, prefix)]
    active_category = next((category for category, _, key, _, _ in learning[lang]
                            if current == 'learn/' + key), None)
    for category in CATEGORY_ORDER:
        articles = [(key, title) for article_category, _, key, title, _ in learning[lang]
                    if article_category == category]
        if not articles:
            continue
        label = CATEGORY_LABELS[lang][category]
        expanded = ' open' if category == active_category else ''
        items = ''.join(link('learn/' + key, title, current, prefix) for key, title in articles)
        learn.append(
            f'<details class="nav-category"{expanded}><summary>{html.escape(label)}</summary>'
            f'<nav aria-label="{html.escape(label)}">{items}</nav></details>'
        )

    if learning_page:
        return (
            f'<details class="nav-group" open>'
            f'<summary>{learn_label}</summary><nav aria-label="{learn_name}">{"".join(learn)}</nav></details>'
        )
    return (
        f'<details class="nav-group" open>'
        f'<summary>{docs_label}</summary><nav aria-label="{docs_name}">{docs}</nav></details>'
    )


def alternates(paths):
    items = [f'<link rel="alternate" hreflang="{item["tag"]}" href="https://soloas.cuviss.com{paths[item["key"]]}">' for item in LANGUAGES]
    items.append(f'<link rel="alternate" hreflang="x-default" href="https://soloas.cuviss.com{paths[LANGUAGES[0]["key"]]}">')
    return '\n'.join(items)


def header(lang, paths, is_home=False):
    current = next(item for item in LANGUAGES if item['key'] == lang)
    names = ('Home', 'Docs', 'Community', 'GitHub', 'Discord', 'Articles') if lang == 'en' else ('首页', '使用文档', '社区贡献', 'GitHub', 'Discord', '相关文章')
    destinations = (current['home'], f'/docs/{lang}/overview.html', f'/docs/{lang}/license.html', 'https://github.com/cuviss-open/soloAS', CONFIG['links']['discord'], f'/docs/{lang}/learn/index.html')
    links = ''.join(f'<a href="{url}"' + (' aria-current="page"' if is_home and index == 0 else '') + f'>{name}</a>' for index, (name, url) in enumerate(zip(names, destinations)))
    languages = ''.join(f'<li><a href="{paths[item["key"]]}" lang="{item["tag"]}" hreflang="{item["tag"]}"' + (' aria-current="page"' if item['key'] == lang else '') + f'>{item["name"]}' + (' <span aria-hidden="true">✓</span>' if item['key'] == lang else '') + '</a></li>' for item in LANGUAGES)
    return f'<header class="site-header"><div class="site-nav"><div class="site-brand-row"><a class="wordmark" href="{current["home"]}" aria-label="soloAS">solo<em>AS</em></a><details class="language-menu"><summary aria-label="{("Language" if lang == "en" else "语言")}">{current["name"]}</summary><ul>{languages}</ul></details></div><nav aria-label="{("Main navigation" if lang == "en" else "主导航")}">{links}</nav></div></header>'


def footer(lang):
    item = next(item for item in LANGUAGES if item['key'] == lang)
    text = item['footer']
    label = text['navLabel']
    date = CONFIG['legalUpdated']

    def paragraphs(values):
        return ''.join(f'<p>{inline(value.replace("{date}", date))}</p>' for value in values)

    terms = paragraphs(text['termsParagraphs']) + f'<p>{html.escape(text["updated"].format(date=date))}</p>'
    privacy = paragraphs(text['privacyParagraphs']) + f'<p>{html.escape(text["updated"].format(date=date))}</p>'
    copyright = paragraphs(text['copyrightParagraphs'])
    return f'''<footer class="site-footer" id="site-footer"><div class="site-footer-inner"><span>© {datetime.now().year} soloAS by Cuviss Studio · {html.escape(text['copyrightShort'])}</span><nav aria-label="{label}"><a href="#contact" aria-haspopup="dialog" aria-controls="contact">{html.escape(text['contact'])}</a><span aria-hidden="true">·</span><a href="#about" aria-haspopup="dialog" aria-controls="about">{html.escape(text['about'])}</a></nav></div></footer>
<div class="site-dialog-root">
<dialog class="site-dialog" id="contact" aria-modal="true" aria-labelledby="contact-title" tabindex="-1" data-site-dialog>
  <div class="site-dialog-panel">
    <a class="site-dialog-close-fallback" href="#site-footer" aria-label="{html.escape(text['close'], quote=True)}" data-dialog-close-link>×</a>
    <button class="site-dialog-close-button" type="button" aria-label="{html.escape(text['close'], quote=True)}" data-dialog-close hidden>×</button>
    <h2 id="contact-title">{html.escape(text['contact'])}</h2>
    <section class="site-dialog-section"><h3>{html.escape(text['feedback'])}</h3><p>{html.escape(text['feedbackText'])} <a href="https://github.com/cuviss-open/soloAS/issues">{html.escape(text['feedbackLink'])}</a>{html.escape(text['sentenceEnd'])}</p></section>
    <section class="site-dialog-section"><h3>{html.escape(text['cooperation'])}</h3><p>{html.escape(text['cooperationText'])} <a href="mailto:contact@cuviss.com">contact@cuviss.com</a>{html.escape(text['sentenceEnd'])}</p></section>
  </div>
</dialog>
<dialog class="site-dialog" id="about" aria-modal="true" aria-labelledby="about-title" tabindex="-1" data-site-dialog>
  <div class="site-dialog-panel">
    <a class="site-dialog-close-fallback" href="#site-footer" aria-label="{html.escape(text['close'], quote=True)}" data-dialog-close-link>×</a>
    <button class="site-dialog-close-button" type="button" aria-label="{html.escape(text['close'], quote=True)}" data-dialog-close hidden>×</button>
    <h2 id="about-title">{html.escape(text['about'])}</h2>
    <section class="site-dialog-section" aria-labelledby="copyright-title"><h3 id="copyright-title">{html.escape(text['copyright'])}</h3>{copyright}</section>
    <section class="site-dialog-section" aria-labelledby="terms-title"><h3 id="terms-title">{html.escape(text['terms'])}</h3>{terms}</section>
    <section class="site-dialog-section" aria-labelledby="privacy-title"><h3 id="privacy-title">{html.escape(text['privacy'])}</h3>{privacy}</section>
  </div>
</dialog>
<script>
(() => {{
  const dialogs = Array.from(document.querySelectorAll('[data-site-dialog]'));
  if (!dialogs.length) return;
  dialogs.forEach(dialog => {{
    dialog.querySelector('[data-dialog-close-link]').hidden = true;
    dialog.querySelector('[data-dialog-close]').hidden = false;
  }});
  const returnFocus = new WeakMap();
  let backgroundState = null;
  const focusableSelector = 'a[href], button:not([disabled]), input:not([disabled]), select:not([disabled]), textarea:not([disabled]), [tabindex]:not([tabindex="-1"])';
  function lockBackground() {{
    if (backgroundState) return;
    backgroundState = Array.from(document.body.children)
      .filter(element => !element.classList.contains('site-dialog-root'))
      .map(element => [element, element.inert]);
    backgroundState.forEach(([element]) => element.inert = true);
  }}
  function unlockBackground() {{
    if (!backgroundState) return;
    backgroundState.forEach(([element, inert]) => element.inert = inert);
    backgroundState = null;
  }}
  function matchingTrigger(dialog) {{
    return document.querySelector(`.site-footer a[href="#${{dialog.id}}"]`);
  }}
  function openDialog(dialog, trigger) {{
    if (dialog.open) return;
    returnFocus.set(dialog, trigger || matchingTrigger(dialog));
    lockBackground();
    dialog.classList.add('is-modal');
    dialog.showModal();
    dialog.querySelector('[data-dialog-close]').focus({{preventScroll:true}});
  }}
  function syncHash() {{
    const target = dialogs.find(dialog => dialog.id === location.hash.slice(1));
    dialogs.forEach(dialog => {{
      if (dialog.open && dialog !== target) dialog.close();
    }});
    if (target && !target.open) openDialog(target, matchingTrigger(target));
  }}
  dialogs.forEach(dialog => {{
    dialog.addEventListener('click', event => {{
      if (event.target === dialog) dialog.close();
    }});
    dialog.addEventListener('click', event => {{
      if (event.target.closest('[data-dialog-close]')) dialog.close();
      if (event.target.closest('[data-dialog-close-link]')) {{
        event.preventDefault();
        dialog.close();
      }}
    }});
    dialog.addEventListener('keydown', event => {{
      if (event.key !== 'Tab') return;
      const focusable = Array.from(dialog.querySelectorAll(focusableSelector))
        .filter(element => !element.hidden && element.getAttribute('aria-hidden') !== 'true');
      if (!focusable.length) {{
        event.preventDefault();
        dialog.focus({{preventScroll:true}});
      }} else if (event.shiftKey && (document.activeElement === focusable[0] || !dialog.contains(document.activeElement))) {{
        event.preventDefault();
        focusable[focusable.length - 1].focus({{preventScroll:true}});
      }} else if (!event.shiftKey && (document.activeElement === focusable[focusable.length - 1] || !dialog.contains(document.activeElement))) {{
        event.preventDefault();
        focusable[0].focus({{preventScroll:true}});
      }}
    }});
    dialog.addEventListener('close', () => {{
      dialog.classList.remove('is-modal');
      unlockBackground();
      if (location.hash === `#${{dialog.id}}`) {{
        if (history.state && history.state.siteDialog === dialog.id) history.back();
        else history.replaceState(history.state, '', location.pathname + location.search);
      }}
      const focusTarget = returnFocus.get(dialog);
      returnFocus.delete(dialog);
      if (focusTarget) focusTarget.focus({{preventScroll:true}});
    }});
  }});
  document.addEventListener('click', event => {{
    const trigger = event.target.closest('.site-footer a[aria-haspopup="dialog"]');
    if (!trigger) return;
    const dialog = document.getElementById(trigger.hash.slice(1));
    if (!dialog) return;
    event.preventDefault();
    if (location.hash !== `#${{dialog.id}}`) history.pushState({{ siteDialog: dialog.id }}, '', `#${{dialog.id}}`);
    openDialog(dialog, trigger);
  }});
  window.addEventListener('popstate', syncHash);
  window.addEventListener('hashchange', syncHash);
  syncHash();
}})();
</script>
</div>'''


def pager_html(lang, name, seq_of, titles):
    seq = seq_of.get(name)
    if not seq:
        return ''
    index = seq.index(name)
    previous_label, next_label = ('Previous', 'Next') if lang == 'en' else ('上一篇', '下一篇')
    parts = []
    if index > 0:
        target = seq[index - 1]
        parts.append(f'<a class="pager-prev" rel="prev" href="/docs/{lang}/{target}.html"><span>← {previous_label}</span><strong>{html.escape(titles[target])}</strong></a>')
    if index + 1 < len(seq):
        target = seq[index + 1]
        parts.append(f'<a class="pager-next" rel="next" href="/docs/{lang}/{target}.html"><span>{next_label} →</span><strong>{html.escape(titles[target])}</strong></a>')
    if not parts:
        return ''
    label = 'Previous and next pages' if lang == 'en' else '上一篇与下一篇'
    return f'<nav class="pager" aria-label="{label}">{"".join(parts)}</nav>'


def main():
    template = (ROOT / 'docs/template.html').read_text()
    template = template.replace('<aside class="sidebar">{{nav_desktop}}<nav class="page-toc" aria-label="{{on_page}}"><div class="nav-title">{{on_page}}</div>{{toc}}</nav></aside><main class="document" id="main" tabindex="-1">{{content}}</main>', '<main class="document" id="main" tabindex="-1">{{content}}</main><nav class="page-toc" aria-label="{{on_page}}"><div class="nav-title">{{on_page}}</div>{{toc}}</nav>')
    template = template.replace('{{menu}} <span aria-hidden="true">≡</span>', '<span class="menu-narrow">{{menu}}</span><span class="menu-wide">{{all_docs}}</span> <span aria-hidden="true">≡</span>')
    template = template.replace('<h3>{{page_list}}</h3><div>{{nav_mobile}}</div>\n<h3>{{on_page}}</h3><nav class="contents-sections" aria-label="{{on_page}}">{{toc}}</nav>', '<section class="contents-page"><h3>{{on_page}}</h3><nav class="contents-sections" aria-label="{{on_page}}">{{toc}}</nav></section>\n<h3>{{all_docs}}</h3><div>{{nav_mobile}}</div>')
    template = template.replace("  narrow.addEventListener('change', () => { if (dialog.open && !narrow.matches) dialog.close(); });", "")
    template = template.replace('</body>', """<script>
(() => {
  const links = Array.from(document.querySelectorAll('.layout .page-toc a'));
  const headings = links.map(link => document.getElementById(decodeURIComponent(link.hash.slice(1))));
  if (!links.length) return;
  function update() {
    let active = 0;
    headings.forEach((heading, i) => { if (heading && heading.getBoundingClientRect().top <= 140) active = i; });
    links.forEach((link, i) => { if (i === active) link.setAttribute('aria-current', 'location'); else link.removeAttribute('aria-current'); });
  }
  window.addEventListener('scroll', update, {passive:true});
  update();
})();
</script></body>""")
    homepage = (ROOT / 'index.html').read_text()
    # Keep visual tokens in sync with the homepage, without copying its layout.
    tokens = re.search(r':root\{([^}]+)\}', homepage)
    if not tokens:
        raise ValueError('Homepage CSS tokens missing')
    expected = {name + '.md' for name, _, _ in PAGES}
    for lang in (item['key'] for item in LANGUAGES):
        actual = {p.name for p in (ROOT / 'docs' / lang).glob('*.md')}
        if actual != expected:
            raise ValueError(f'{lang}: missing {expected - actual}; unexpected {actual - expected}')
    learning = {}
    for lang in (item['key'] for item in LANGUAGES):
        learning[lang] = []
        for path in (ROOT / 'docs' / lang / 'learn').glob('*.md'):
            if path.stem != 'index':
                category, order, title, source = article(path.read_text())
                learning[lang].append((category, order, path.stem, title, source))
        learning[lang].sort(key=lambda item: (CATEGORY_ORDER.index(item[0]), item[1], item[2]))
    built = 0
    for lang in (item['key'] for item in LANGUAGES):
        learn_title = 'Articles' if lang == 'en' else '相关文章'
        intro = ('These time-sensitive learning notes use the UE-AS fork as their reference. SoloAS has extended or reworked some areas, while other project practices remain useful. If you use only the two core plugins (Runtime and Bridge), these articles are especially useful. For what soloAS adds, see the [documentation](../overview.md).' if lang == 'en' else '这部分学习心得以 UE-AS fork 为参照，内容具有时效性：soloAS 在部分问题上已经做了拓展处理，但有些项目实践仍然值得参考。如果只使用核心两个插件（Runtime 与 Bridge），这些文章会更有帮助。soloAS 新增的能力见[使用文档](../overview.md)。')
        index = f'# {learn_title}\n\n> {"Note: " if lang == "en" else "注："}{intro}\n\n'
        if learning[lang]:
            for category in CATEGORY_ORDER:
                articles = [(key, title) for article_category, _, key, title, _ in learning[lang]
                            if article_category == category]
                if articles:
                    index += f'## {CATEGORY_LABELS[lang][category]}\n\n'
                    index += '\n'.join(f'- [{title}]({key}.md)' for key, title in articles) + '\n\n'
        else:
            index += 'Articles are being prepared.' if lang == 'en' else '文章正在编写中。'
        entries = [(key, en if lang == 'en' else zh,
                    (ROOT / 'docs' / lang / (key + '.md')).read_text())
                   for key, en, zh in PAGES]
        entries += [('learn/index', learn_title, index)]
        entries += [('learn/' + key, title, source) for _, _, key, title, source in learning[lang]]
        docs_seq = []
        for item in DOC_NAV:
            if item[0] == 'page':
                docs_seq.append(item[1])
            elif item[0] == 'group':
                docs_seq.extend(page[0] for page in item[3])
        learn_seq = ['learn/index'] + ['learn/' + key for _, _, key, _, _ in learning[lang]]
        titles = {entry_name: entry_title for entry_name, entry_title, _ in entries}
        seq_of = {entry_name: seq for seq in (docs_seq, learn_seq) for entry_name in seq}
        for stale in (ROOT / 'site/docs' / lang).glob('*.html'):
            stale.unlink()
        for name, title, source in entries:
            target = ROOT / 'site/docs' / lang / (name + '.html')
            target.parent.mkdir(parents=True, exist_ok=True)
            body, toc = render(
                source,
                mark_version_text=not name.startswith('learn/'),
                version_table=name in {'requirements', 'ue-version-differences'},
            )
            if name == 'ue-version-differences':
                body = re.sub(r'(<h2 id="[^"]+">.*?)(?=<h2 id=|$)',
                              r'<section class="version-section">\1</section>', body, flags=re.S)
            body += pager_html(lang, name, seq_of, titles)
            depth = len(Path(name).parts) - 1
            prefix = '../' * depth
            nav = navigation(lang, name, learning)
            values = dict(suffix='soloAS docs' if lang == 'en' else 'soloAS 文档', tokens=tokens[1], lang=next(item['tag'] for item in LANGUAGES if item['key'] == lang), title=html.escape(title), nav_desktop=nav, nav_mobile=nav, content=body, toc=toc, navigation='Documentation' if lang == 'en' else '使用文档', menu='Contents' if lang == 'en' else '目录', close='Close' if lang == 'en' else '关闭', page_list='Pages' if lang == 'en' else '页面列表', all_docs='All docs' if lang == 'en' else '全部文档', on_page='On this page' if lang == 'en' else '本页目录', skip='Skip to content' if lang == 'en' else '跳至正文', home=prefix + ('../../index.html' if lang == 'en' else '../../zh/index.html'), favicon=prefix + '../../favicon.svg', favicon_ico=prefix + '../../favicon.ico', apple_touch_icon=prefix + '../../apple-touch-icon.png')
            paths = {item['key']: f'/docs/{item["key"]}/{name}.html' for item in LANGUAGES}
            for item in LANGUAGES:
                if name.startswith('learn/') and name != 'learn/index' and not (ROOT / 'docs' / item['key'] / (name + '.md')).exists():
                    paths[item['key']] = f'/docs/{item["key"]}/learn/index.html'
            values.update(header=header(lang, paths), footer=footer(lang), alternates=alternates(paths), chrome_css=CHROME_CSS)
            page = re.sub(r'\{\{(\w+)\}\}', lambda m: values[m[1]], template)
            if not toc:
                page = re.sub(r'<nav class="page-toc".*?</nav>', '', page, flags=re.S)
                page = re.sub(r'<section class="contents-page">.*?</section>', '', page, flags=re.S)
            if name == 'ue-version-differences':
                page = page.replace('</style>', '.version-section{border-left:4px solid var(--paper-line);background:var(--paper);color:var(--ink);padding:1px 20px 20px;margin:32px 0}.version-section h2{margin-top:20px}</style>', 1)
            if name in PENDING_PAGES:
                page = page.replace('</head>', '<meta name="robots" content="noindex">\n</head>', 1)
            if 'class="ver"' not in body or name.startswith('learn/'):
                page = page.replace(VERSION_HIGHLIGHT_CSS, '', 1)
            target.write_text(secure_external_links(page))
            built += 1
    if (ROOT / 'docs/assets').is_dir():
        shutil.copytree(ROOT / 'docs/assets', ROOT / 'site/docs/assets', dirs_exist_ok=True)
    home_paths = {item['key']: item['home'] for item in LANGUAGES}
    for item in LANGUAGES:
        lang = item['key']
        source = ROOT / ('' if lang == 'en' else lang) / 'index.html'
        values = dict(header=header(lang, home_paths, is_home=True), footer=footer(lang), alternates=alternates(home_paths), chrome_css=CHROME_CSS)
        template = source.read_text()
        template = re.sub(r'<p class="start-note">.*?</p>', ('<p class="start-note">支持的版本见<a href="/docs/zh/requirements.html">环境配置</a>。</p>' if lang == 'zh' else '<p class="start-note">See <a href="/docs/en/requirements.html">environment setup</a> for supported versions.</p>'), template, count=1)
        page = re.sub(r'\{\{(\w+)\}\}', lambda m: values[m[1]], template)
        page = mark_html_text(page)
        if 'class="ver"' not in page:
            page = page.replace(VERSION_HIGHLIGHT_CSS, '', 1)
        target = ROOT / 'site' / item['home'].lstrip('/') / 'index.html'
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(secure_external_links(page))
    for name in ('favicon.svg', 'favicon.ico', 'apple-touch-icon.png', 'CNAME'):
        shutil.copyfile(ROOT / name, ROOT / 'site' / name)
    print(f'Built {built} documentation pages and homepage assets in site/')


if __name__ == '__main__':
    main()
