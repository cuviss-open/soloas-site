#!/usr/bin/env python3
"""Compose public version-difference pages using the product generator."""
import argparse
import importlib.util
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def compose(current, legacy, language):
    def content(document, section=0):
        parts = document.split('\n', 6)
        body = parts[6]  # Skip the generated marker, title and release sentence.
        suffix = (('（0.2.x）' if language == 'zh' else ' (0.2.x)') if section == 1 else ('（0.1.x）' if language == 'zh' else ' (0.1.x)') if section == 2 else '')
        return '\n'.join('#' + line + suffix if line.startswith('## ') else line
                         for line in body.split('\n')).strip()

    title = current.split('\n')[2]
    if language == 'zh':
        intro = '本页按 soloAS 版本分节。'
        headings = ('0.3.x（当前版本 · 支持 UE 5.7、5.8）', '0.2.x（历史版本 · 支持 UE 5.7、5.8）', '0.1.x（支持 UE 5.4–5.8）')
        labels = ('0.3.x（当前，支持 UE 5.7、5.8）', headings[1], headings[2])
    else:
        intro = 'This page is organized by soloAS version.'
        headings = ('0.3.x (current version · supports UE 5.7, 5.8)', '0.2.x (historical version · supports UE 5.7, 5.8)', '0.1.x (supports UE 5.4–5.8)')
        labels = ('0.3.x (current, supports UE 5.7, 5.8)', headings[1], headings[2])
    def anchor(heading):
        return re.sub(r'\s+', '-', re.sub(r'[^\w\s-]', '', heading.lower()).strip())
    links = '\n'.join(f'- [{label}](#{anchor(heading)})' for label, heading in zip(labels, headings))
    return (current.split('\n')[0] + '\n\n' + title + '\n\n' + intro + '\n\n' + links +
            '\n\n' + '\n\n'.join('## ' + heading + '\n\n' + content(document, section)
                                      for section, (heading, document) in enumerate(zip(headings, (current, current, legacy)))) + '\n')



def run(product, check=False):
    product = product.resolve()
    spec = importlib.util.spec_from_file_location('engine_support', product / 'project/tools/Runner/engine-support.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    data = json.loads((product / 'project/config/engine-version-test-coverage.json').read_text(encoding='utf-8'))
    _, profile = module.locked_engine_profile(product)
    supported = {minor for minor, row in profile['epic']['support'].items() if row.get('supported', True)}
    for language in ('zh', 'en'):
        current = module.public_documents(data, language, '0.2.0', supported)
        legacy = module.public_documents(data, language, '0.1.3', supported)
        output = compose(current, legacy, language)
        path = ROOT / 'docs' / language / 'ue-version-differences.md'
        if check:
            if path.read_text(encoding='utf-8') != output:
                raise ValueError(f'Generated version differences are out of date: {path}')
        else:
            path.write_text(output, encoding='utf-8')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--product', type=Path, required=True)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    run(args.product, args.check)


if __name__ == '__main__':
    main()
