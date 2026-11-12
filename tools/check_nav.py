#!/usr/bin/env python3
"""Check that the release navigation lists every page of the full docs (dev) in the same order.

Pages that are not in the release must be shown with the "coming soon" suffix, must not be
links, must be marked noindex and must not be linked from anywhere. Release-only pages are
allowed as extras. Local pre-release gate; needs the dev branch in the same repository.
"""
import argparse
import ast
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SUFFIX = {"zh": "（待发布）", "en": " (coming soon)"}
INTENTIONAL_RELEASE_OMISSIONS = {}


def literal_block(text, name):
    i = text.index(name + " = [")
    j = text.index("\n]\n", i) + 2
    return ast.literal_eval(text[i + len(name) + 3:j])


def entries(html_text, lang):
    label = "使用文档" if lang == "zh" else "Documentation"
    m = re.search(r'<nav aria-label="%s">(.*?)</nav></details>' % re.escape(label), html_text, flags=re.S)
    assert m, "documentation navigation not found"
    out = []
    for tag in re.finditer(r'<a href="([^"]+)"[^>]*>([^<]*)</a>|<span class="nav-pending"[^>]*>([^<]*)</span>', m.group(1)):
        if tag.group(1):
            out.append(("link", tag.group(2), tag.group(1)))
        else:
            out.append(("pending", tag.group(3), None))
    return out


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dev-ref", default="ctrl/site013-dev")
    parser.add_argument("--site", type=Path, default=ROOT / "site")
    args = parser.parse_args()

    dev_text = subprocess.run(["git", "show", f"{args.dev_ref}:tools/build_docs.py"], cwd=ROOT, capture_output=True, text=True, check=True).stdout
    dev_nav = literal_block(dev_text, "DOC_NAV")
    cur_nav = literal_block((ROOT / "tools/build_docs.py").read_text(), "DOC_NAV")
    pending_keys = [item[1] for item in cur_nav if item[0] == "pending"]
    problems = []

    for lang in ("zh", "en"):
        idx = 3 if lang == "zh" else 2
        dev_labels = [item[idx] for item in dev_nav if item[0] == "page"]
        page = (args.site / "docs" / lang / "core.html").read_text()
        found = entries(page, lang)
        # label of an entry without the coming-soon suffix
        shown = [(kind, text[: -len(SUFFIX[lang])] if kind == "pending" and text.endswith(SUFFIX[lang]) else text, href) for kind, text, href in found]
        positions = []
        for label in dev_labels:
            hits = [i for i, (_, text, _) in enumerate(shown) if text == label]
            if not hits:
                if label in INTENTIONAL_RELEASE_OMISSIONS:
                    print(f"[{lang}] intentional structural difference: {label} — {INTENTIONAL_RELEASE_OMISSIONS[label]}")
                    continue
                problems.append(f"[{lang}] full-docs page missing from the release navigation: {label}")
            else:
                positions.append(hits[0])
        if positions != sorted(positions):
            problems.append(f"[{lang}] order differs from the full docs: {dev_labels}")
        for kind, text, href in found:
            if kind == "pending" and not text.endswith(SUFFIX[lang]):
                problems.append(f"[{lang}] pending entry without the suffix: {text}")
            if kind == "link" and text.endswith(SUFFIX[lang]):
                problems.append(f"[{lang}] suffix on a clickable entry: {text}")
        extras = [text for kind, text, _ in shown if text not in dev_labels]
        print(f"[{lang}] full-docs pages: {len(dev_labels)}; release entries: {len(found)} "
              f"(pending {sum(k == 'pending' for k, _, _ in found)}); release-only extras: {extras}")

    # pending pages: noindex, and no link to them anywhere
    for key in pending_keys:
        for lang in ("zh", "en"):
            f = args.site / "docs" / lang / f"{key}.html"
            if not f.exists():
                problems.append(f"missing stub page: {lang}/{key}.html")
            elif 'name="robots" content="noindex"' not in f.read_text():
                problems.append(f"stub page without noindex: {lang}/{key}.html")
    for page in args.site.rglob("*.html"):
        text = page.read_text()
        own = page.stem if page.parent.parent.name == "docs" else None  # a stub's language switcher points at its own twin
        anchors = re.findall(r'<a\s[^>]*href="([^"]+)"', text)
        for key in pending_keys:
            if key == own:
                continue
            if any(re.search(r'(?:^|/)%s\.html(?:#|$)' % re.escape(key), href) for href in anchors):
                problems.append(f"{page.relative_to(args.site)} links to the pending page {key}")
    print("pending pages:", ", ".join(pending_keys))
    print(f"problems: {len(problems)}")
    for p in problems:
        print(" -", p)
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
