#!/usr/bin/env python3
"""Render the supported engine versions from a frozen product lock."""
import argparse
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT = ROOT / 'tools/data/site013-release-input.json'
START = '<!-- generated-engine-support:start -->'
END = '<!-- generated-engine-support:end -->'


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def sync_product(product_root):
    product_root = product_root.resolve()
    lock_path = product_root / 'Upstream.lock.json'
    coverage_path = product_root / 'project/config/engine-version-test-coverage.json'
    lock = json.loads(lock_path.read_text(encoding='utf-8'))
    coverage = json.loads(coverage_path.read_text(encoding='utf-8'))
    profiles = lock.get('compatibilityProfiles', {})
    profile = next((item for item in profiles.values() if item.get('epic', {}).get('support')), None)
    if profile is None:
        raise ValueError('No Unreal Engine support policy found in product lock')
    commit = subprocess.check_output(['git', '-C', str(product_root), 'rev-parse', 'HEAD'], text=True).strip()
    snapshot = {'source': {'repository': str(product_root), 'commit': commit,
                           'lockPath': 'Upstream.lock.json', 'lockSha256': sha256(lock_path),
                           'coveragePath': 'project/config/engine-version-test-coverage.json',
                           'coverageSha256': sha256(coverage_path)},
                'release': coverage.get('release'), 'support': profile['epic']['support']}
    SNAPSHOT.write_text(json.dumps(snapshot, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    return snapshot


def load_snapshot():
    return json.loads(SNAPSHOT.read_text(encoding='utf-8'))


def supported_versions(support):
    versions = []
    for minor, details in support.items():
        if not minor.startswith('5.') or not isinstance(details, dict):
            continue
        for patch, result in details.get('patches', {}).items():
            if str(patch).isdigit() and result.get('validated') is True:
                versions.append((tuple(map(int, minor.split('.'))) + (int(patch),), f'{minor}.{patch}'))
    return [label for _, label in sorted(versions)]


def render_support(snapshot, language):
    versions = supported_versions(snapshot.get('support', {}))
    if not versions:
        raise ValueError('No supported Unreal Engine versions found in the synchronized product lock')
    levels = [snapshot['support'][version.rsplit('.', 1)[0]].get('verificationLevel') for version in versions]
    if levels[-1] != 'full' or any(level != 'core' for level in levels[:-1]):
        raise ValueError('Verification levels changed; revise the support wording before rendering')
    if language == 'en':
        labels = ', '.join(versions[:-1]) + (', and ' if len(versions) > 2 else ' and ' if len(versions) > 1 else '') + versions[-1]
        lines = [f'Current adaptations: stock Unreal Engine {labels}.',
                 'The most recent supported version has the broadest validation coverage. Unlisted patches are not guaranteed to work.']
    else:
        lines = [f"当前适配：原版 UE {'、'.join(versions)}。",
                 '最新已适配版本的验证范围最完整。未列出的补丁版本不保证可用。']
    return '\n'.join(f'- {line}' for line in lines)


def render(snapshot, check=False):
    errors = []
    for language in ('en', 'zh'):
        path = ROOT / 'docs' / language / 'requirements.md'
        current = path.read_text(encoding='utf-8')
        before, marker, rest = current.partition(START)
        _, marker2, after = rest.partition(END)
        if not marker or not marker2:
            raise ValueError(f'Missing generated support markers: {path}')
        expected = before + START + '\n' + render_support(snapshot, language) + '\n' + END + after
        if check and expected != current:
            errors.append(f'Support text differs from synchronized lock: {path.relative_to(ROOT)}')
        elif not check:
            path.write_text(expected, encoding='utf-8')
    if errors:
        raise SystemExit('\n'.join(errors))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--sync-from-product', type=Path)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    snapshot = sync_product(args.sync_from_product) if args.sync_from_product else load_snapshot()
    render(snapshot, check=args.check)
    print('Generated support matches.' if args.check else 'Rendered support from product lock.')


if __name__ == '__main__':
    main()
