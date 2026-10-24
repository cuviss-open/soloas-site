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

ROOT = Path(__file__).resolve().parents[1]
CONFIG = json.loads((ROOT / 'tools/site_config.json').read_text())
LANGUAGES = CONFIG['languages']
CHROME_CSS = (ROOT / 'tools/site-chrome.css').read_text()
PAGES = [
    ('overview', 'About soloAS', '项目介绍'),
    ('requirements', 'Environment setup and quick start', '环境配置与快速上手'),
    ('migration', 'Migrating an existing AS project', '迁移已有 AS 项目'),
    ('core', 'Plugin core', '插件核心'),
    ('manual-binding-packs', 'Manual binding packs', '手工绑定包'),
    ('packaging', 'Packaging', '项目打包'),
    ('license', 'Community', '社区贡献'),
    ('extensions', 'Core extensions', '核心扩展'),
    ('dynamic-modules', 'Feature Mods', '功能模组'),
    ('core-manual-bindings', 'Manual binding core', '手工绑定核心'),
    ('auto-binding', 'Auto binding', '自动绑定'),
    ('ai-assisted', 'AI-assisted development', 'AI 辅助开发'),
]
DOC_NAV = [
    ('page', 'overview', 'About soloAS', '项目介绍'),
    ('page', 'requirements', 'Environment setup and quick start', '环境配置与快速上手'),
    ('page', 'migration', 'Migrating an existing AS project', '迁移已有 AS 项目'),
    ('page', 'core', 'Plugin core', '插件核心'),
    ('pending', 'extensions', 'Core extensions', '核心扩展'),
    ('pending', 'dynamic-modules', 'Feature Mods', '功能模组'),
    ('pending', 'core-manual-bindings', 'Manual binding core', '手工绑定核心'),
    ('pending', 'auto-binding', 'Auto binding', '自动绑定'),
    ('page', 'manual-binding-packs', 'Manual binding packs', '手工绑定包'),
    ('page', 'packaging', 'Packaging', '项目打包'),
    ('pending', 'ai-assisted', 'AI-assisted development', 'AI 辅助开发'),
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


def slug(text):
    text = re.sub(r'[`*_]', '', text).lower()
    text = re.sub(r'[^\w\s-]', '', text)
    return re.sub(r'\s+', '-', text.strip())


def inline(source, tokens=None):
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
        return keep(f'<a href="{html.escape(url, quote=True)}">{inline(label, tokens)}</a>')

    source = re.sub(r'\[([^\]]+)\]\(([^\s)]+)\)', link, source)
    source = html.escape(source)
    source = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', source)
    source = re.sub(r'(?<!\*)\*([^*]+)\*(?!\*)', r'<em>\1</em>', source)
    return re.sub(r'\x00(\d+)\x00', lambda m: tokens[int(m[1])], source)


def render(source):
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
            output.append(f'<h{level} id="{anchor}">{inline(label)}<a class="anchor" href="#{anchor}" aria-label="Permalink">#</a></h{level}>')
            if level == 2 or (level == 1 and len(anchors) > 1):
                toc.append(f'<a href="#{anchor}">{inline(label)}</a>')
        elif i + 1 < len(lines) and '|' in line and re.match(r'^\s*\|?\s*:?-{3,}', lines[i + 1]):
            def cells(row):
                return [inline(c.strip()) for c in row.strip().strip('|').split('|')]
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
                output.append('<li>' + inline(' '.join(text)) + '</li>')
            output.append(f'</{tag}>')
            continue
        elif line.startswith('> 注：') or line.startswith('> Note: '):
            output.append('<p class="doc-aside">' + inline(line[2:]) + '</p>')
            i += 1
        elif line in ('> **soloAS 注**', '> **soloAS note**'):
            label = line[4:-2]
            note = []
            i += 1
            while i < len(lines) and lines[i].startswith('> '):
                note.append(lines[i][2:])
                i += 1
            output.append('<aside class="soloas-note" aria-label="' + html.escape(label) + '"><span class="soloas-note-label">' + html.escape(label) + '</span><p>' + inline(' '.join(note)) + '</p></aside>')
            continue
        elif line.startswith('> '):
            output.append('<blockquote><p>' + inline(line[2:]) + '</p></blockquote>')
        elif re.match(r'^\s*(?:---+|\*\*\*+)\s*$', line):
            output.append('<hr>')
        else:
            paragraph = [line]
            i += 1
            while i < len(lines) and lines[i].strip() and not re.match(r'^(?:#|```|>|\s*[-+*]\s|\s*\d+\.\s)', lines[i]):
                paragraph.append(lines[i])
                i += 1
            output.append('<p>' + inline(' '.join(paragraph)) + '</p>')
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
    names = ('Home', 'Docs', 'Community', 'GitHub', 'Articles') if lang == 'en' else ('首页', '使用文档', '社区贡献', 'GitHub', '相关文章')
    destinations = (current['home'], f'/docs/{lang}/overview.html', f'/docs/{lang}/license.html', 'https://github.com/cuviss-open/soloAS', f'/docs/{lang}/learn/index.html')
    links = ''.join(f'<a href="{url}"' + (' aria-current="page"' if is_home and index == 0 else '') + f'>{name}</a>' for index, (name, url) in enumerate(zip(names, destinations)))
    languages = ''.join(f'<li><a href="{paths[item["key"]]}" lang="{item["tag"]}" hreflang="{item["tag"]}"' + (' aria-current="page"' if item['key'] == lang else '') + f'>{item["name"]}' + (' <span aria-hidden="true">✓</span>' if item['key'] == lang else '') + '</a></li>' for item in LANGUAGES)
    return f'<header class="site-header"><div class="site-nav"><div class="site-brand-row"><a class="wordmark" href="{current["home"]}" aria-label="soloAS">solo<em>AS</em></a><details class="language-menu"><summary aria-label="{("Language" if lang == "en" else "语言")}">{current["name"]}</summary><ul>{languages}</ul></details></div><nav aria-label="{("Main navigation" if lang == "en" else "主导航")}">{links}</nav></div></header>'


def footer(lang):
    item = next(item for item in LANGUAGES if item['key'] == lang)
    text = item['footer']
    label = text['navLabel']
    date = datetime.now().date().isoformat()

    def paragraphs(values):
        return ''.join(f'<p>{inline(value.replace("{date}", date))}</p>' for value in values)

    terms = paragraphs(text['termsParagraphs']) + f'<p>{html.escape(text["updated"].format(date=date))}</p>'
    privacy = paragraphs(text['privacyParagraphs']) + f'<p>{html.escape(text["updated"].format(date=date))}</p>'
    return f'''<footer class="site-footer" id="site-footer"><div class="site-footer-inner"><span>© {datetime.now().year} soloAS by Cuviss Studio</span><nav aria-label="{label}"><a href="#contact" aria-haspopup="dialog" aria-controls="contact">{html.escape(text['contact'])}</a><span aria-hidden="true">·</span><a href="#about" aria-haspopup="dialog" aria-controls="about">{html.escape(text['about'])}</a></nav></div></footer>
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
        intro = ('This part is learning notes based on the original Haze fork. It is time-sensitive: soloAS has extended or reworked some of these areas, but some of the project practice here is still worth referring to. If you use only the two core plugins (Runtime and Bridge), you need these articles even more. For what soloAS adds, see the [documentation](../overview.md).' if lang == 'en' else '这部分是基于原始 Haze fork 的学习心得，具有时效性：soloAS 在部分问题上已经做了拓展处理，但有些项目实践的内容仍然值得参考。如果只使用核心两个插件（Runtime 与 Bridge），就更需要这些文章。soloAS 新增的能力见[使用文档](../overview.md)。')
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
            body, toc = render(source)
            body += pager_html(lang, name, seq_of, titles)
            depth = len(Path(name).parts) - 1
            prefix = '../' * depth
            nav = navigation(lang, name, learning)
            values = dict(suffix='soloAS docs' if lang == 'en' else 'soloAS 文档', tokens=tokens[1], lang=next(item['tag'] for item in LANGUAGES if item['key'] == lang), title=html.escape(title), nav_desktop=nav, nav_mobile=nav, content=body, toc=toc, navigation='Documentation' if lang == 'en' else '使用文档', menu='Contents' if lang == 'en' else '目录', close='Close' if lang == 'en' else '关闭', page_list='Pages' if lang == 'en' else '页面列表', on_page='On this page' if lang == 'en' else '本页目录', skip='Skip to content' if lang == 'en' else '跳至正文', home=prefix + ('../../index.html' if lang == 'en' else '../../zh/index.html'), favicon=prefix + '../../favicon.svg')
            paths = {item['key']: f'/docs/{item["key"]}/{name}.html' for item in LANGUAGES}
            for item in LANGUAGES:
                if name.startswith('learn/') and name != 'learn/index' and not (ROOT / 'docs' / item['key'] / (name + '.md')).exists():
                    paths[item['key']] = f'/docs/{item["key"]}/learn/index.html'
            values.update(header=header(lang, paths), footer=footer(lang), alternates=alternates(paths), chrome_css=CHROME_CSS)
            page = re.sub(r'\{\{(\w+)\}\}', lambda m: values[m[1]], template)
            if name == 'license':
                page = page.replace('class="layout"', 'class="layout" style="display:block;max-width:1000px"')
                page = re.sub(r'<aside class="sidebar">.*?</aside>', '', page, flags=re.S)
                page = re.sub(r'<nav class="toc".*?</nav>', '', page, flags=re.S)
                page = re.sub(r'<button class="contents-button".*?</script>', '', page, flags=re.S)
            if name in PENDING_PAGES:
                page = page.replace('</head>', '<meta name="robots" content="noindex">\n</head>', 1)
            target.write_text(page)
            built += 1
    if (ROOT / 'docs/assets').is_dir():
        shutil.copytree(ROOT / 'docs/assets', ROOT / 'site/docs/assets', dirs_exist_ok=True)
    home_paths = {item['key']: item['home'] for item in LANGUAGES}
    for item in LANGUAGES:
        lang = item['key']
        source = ROOT / ('' if lang == 'en' else lang) / 'index.html'
        values = dict(header=header(lang, home_paths, is_home=True), footer=footer(lang), alternates=alternates(home_paths), chrome_css=CHROME_CSS)
        page = re.sub(r'\{\{(\w+)\}\}', lambda m: values[m[1]], source.read_text())
        target = ROOT / 'site' / item['home'].lstrip('/') / 'index.html'
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(page)
    for name in ('favicon.svg', 'CNAME'):
        shutil.copyfile(ROOT / name, ROOT / 'site' / name)
    print(f'Built {built} documentation pages and homepage assets in site/')


if __name__ == '__main__':
    main()
