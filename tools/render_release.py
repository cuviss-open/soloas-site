#!/usr/bin/env python3
"""Render release heading and license tables from the frozen release and site data."""
import argparse
from concurrent.futures import ThreadPoolExecutor
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]

def replace_block(text, name, body, occurrence=0):
    start, end = f'<!-- generated-{name}:start -->', f'<!-- generated-{name}:end -->'
    before = ''
    for _ in range(occurrence):
        part, marker, text = text.partition(end)
        if not marker:
            raise ValueError(f'Missing {name} markers')
        before += part + marker
    prefix, marker, tail = text.partition(start)
    before += prefix
    _, marker2, after = tail.partition(end)
    if not marker or not marker2:
        raise ValueError(f'Missing {name} markers')
    return before + start + '\n' + body + '\n' + end + after

def release_data():
    data = json.loads((ROOT / 'tools/data/releases.json').read_text())
    version = json.loads((ROOT / 'tools/data/site013-release-input.json').read_text())['release']
    release = next(r for r in data['releases'] if r['version'] == version)
    assets = release['assets']
    versions = [v.strip() for v in release['engineVersion'].split(',')]
    from render_support import load_snapshot, supported_versions
    if versions != supported_versions(load_snapshot()['support']):
        raise ValueError('release and supported engine versions differ')
    if len(assets) != 1 + 2 * len(versions) or len({a['name'] for a in assets}) != len(assets):
        raise ValueError('release asset list is incomplete')
    for a in assets:
        if not re.fullmatch(r'[0-9a-f]{64}', a['sha256']) or not isinstance(a['bytes'], int) or a['bytes'] <= 0:
            raise ValueError('invalid asset metadata')
        if not a['ueVersions'] or not set(a['ueVersions']) <= set(versions) or not a['platforms']:
            raise ValueError('invalid asset applicability')
    return release

def run(check=False):
    release = release_data()
    releases = json.loads((ROOT / 'tools/data/releases.json').read_text())['releases']
    next_release = next(r for r in releases if r['version'] == '0.2.0')
    tables = json.loads((ROOT / 'tools/site_config.json').read_text())['licenseTables']
    def language(lang):
        results=[]
        versions = [v.strip() for v in release['engineVersion'].split(',')]
        heading = f"## {release['version']} · UE {versions[0]}–{versions[-1]}"
        next_versions = [v.strip() for v in next_release['engineVersion'].split(',')]
        next_heading = f"## {next_release['version']} · UE {next_versions[0]}–{next_versions[-1]}"
        for page, name, body, occurrence in [('license', 'license', '\n'.join(tables[lang]), 0), ('changelog', 'release-heading', next_heading, 0), ('changelog', 'release-heading', heading, 1)]:
            path=ROOT / 'docs' / lang / f'{page}.md'
            current=path.read_text(encoding='utf-8')
            expected=replace_block(current,name,body,occurrence)
            if current != expected:
                if check: results.append(f'{path.relative_to(ROOT)}: generated {name} differs')
                else: path.write_text(expected,encoding='utf-8')
        return results
    with ThreadPoolExecutor() as pool:
        errors = [e for group in pool.map(language, ('en','zh')) for e in group]
    if errors: raise ValueError('; '.join(errors))

if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check',action='store_true')
    args=parser.parse_args()
    run(args.check)
    print('Release heading and license tables match.' if args.check else 'Rendered release heading and license tables.')
