import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import render_api_differences as renderer


class RenderApiDifferencesTest(unittest.TestCase):
    def policy(self):
        return {'publicPresentation': {
            'upstream-bug-fix': {'reason': 'fix', 'zh': '修复', 'en': 'Fixed'},
            'non-api-engine-distribution': {'zh': '插件', 'en': 'Plugin'}},
            'partitions': {'fork': []}}

    def test_check_detects_policy_and_page_drift(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            for language in ('zh', 'en'):
                (root / 'docs' / language).mkdir(parents=True)
            policy = root / 'policy.json'
            policy.write_text(json.dumps(self.policy()))
            with patch.object(renderer, 'ROOT', root):
                renderer.run(policy)
                for language in ('zh', 'en'):
                    self.assertEqual((root / 'docs' / language / 'api-differences.md').read_text(),
                                     renderer.render(self.policy(), language))
                renderer.run(policy, check=True)
                (root / 'docs/zh/api-differences.md').write_text('changed')
                with self.assertRaises(ValueError):
                    renderer.run(policy, check=True)
                renderer.run(policy)
                changed = self.policy()
                changed['partitions']['fork'].append({'category': 'upstream-bug-fix', 'reason': 'unknown'})
                policy.write_text(json.dumps(changed))
                with self.assertRaises(ValueError):
                    renderer.run(policy, check=True)

    def test_loading_timing_lists_policy_modules_without_declaration_details(self):
        policy = self.policy()
        policy['publicPresentation']['non-api-loading-timing'] = {'zh': '加载时机', 'en': 'Loading timing'}
        reason = ('Identical native declarations become visible before AS binding in the project-plugin discovery slot; '
                  'the engine-plugin fork initializes AS before this PostDefault owner module. Signature changes are excluded.')
        base = {'category': 'non-api-loading-timing', 'direction': 'added', 'reason': reason,
                'proof': {'module': 'ExampleEditor'}}
        policy['partitions']['fork'] = [
            {**base, 'collector': 'docs', 'record': 'property|UExample|int Count'},
            {**base, 'collector': 'db', 'record': {'kind': 'property', 'owner': 'UExample', 'name': 'Count', 'type': 'int'}}]
        for language in ('zh', 'en'):
            page = renderer.render(policy, language)
            section = page.split('## 加载时机（非 API 差异）' if language == 'zh' else
                                 '## Loading timing (not an API difference)', 1)[1]
            self.assertIn('- `ExampleEditor`', page)
            self.assertNotIn('UExample', page)
            self.assertIn('共 1 个模块' if language == 'zh' else '1 modules in total', page)
        self.assertIn('以下模块中的部分原生声明在两端完全相同，但 soloAS 作为项目插件初始化时这些模块已加载，因此可供脚本使用；UE-AS fork 在这些模块加载前就已初始化脚本绑定，所以用不到。声明和签名本身没有差异。',
                      renderer.render(policy, 'zh'))
        self.assertIn('Some native declarations in the following modules are identical on both sides.',
                      renderer.render(policy, 'en'))
        policy['partitions']['fork'][0]['proof']['module'] = 'ExtraModule'
        page = renderer.render(policy, 'en')
        self.assertIn('- `ExtraModule`', page)
        self.assertNotIn('- `ExampleEditor`', page)
        policy['partitions']['fork'][0]['reason'] = 'unreviewed'
        with self.assertRaisesRegex(ValueError, 'Unreviewed loading-timing'):
            renderer.render(policy, 'en')

    def test_engine_distribution_is_summarized_and_still_validated(self):
        policy = self.policy()
        common = {'category': 'non-api-engine-distribution', 'direction': 'added',
                  'proof': {'presentSource': {'path': 'Engine/Plugins/Example/Source/Test.h'}}}
        policy['partitions']['fork'] = [
            {**common, 'collector': 'docs', 'record': 'enum-value|EExample|Value'},
            {**common, 'collector': 'db', 'record': {'kind': 'enum-value', 'owner': 'EExample', 'name': 'Value'}}]
        self.assertIn('EExample · Value', renderer.render(policy, 'en'))
        self.assertIn('1 interfaces in total', renderer.render(policy, 'en'))
        self.assertNotIn('EExample::Value', renderer.render(policy, 'en'))
        policy['partitions']['fork'][0]['direction'] = 'removed'
        with self.assertRaisesRegex(ValueError, 'engine-distribution'):
            renderer.render(policy, 'en')
        policy['partitions']['fork'][0]['direction'] = 'added'
        policy['partitions']['fork'][0]['proof'] = {'presentSource': {'path': 'Engine/Source/Test.h'}}
        with self.assertRaisesRegex(ValueError, 'engine-distribution'):
            renderer.render(policy, 'en')

    def test_default_table_and_counterpart_validation(self):
        policy = self.policy()
        new = 'global-function|VisualLogger|static void VisualLogger::LogArrow(FName CategoryName = FName ( "VisLogBP" ))'
        old = new.replace('"VisLogBP"', '""')
        db_new = {'default': 'VisLogBP'}
        db_old = {'default': ''}
        for collector, added, removed in [('docs', new, old), ('db', db_new, db_old)]:
            for direction, record, counterpart in [('added', added, removed), ('removed', removed, added)]:
                policy['partitions']['fork'].append({'category': 'upstream-bug-fix', 'reason': 'fix',
                    'collector': collector, 'direction': direction, 'record': record, 'counterpart': counterpart})
        for language in ('zh', 'en'):
            page = renderer.render(policy, language)
            self.assertIn('```angelscript\nVisualLogger::LogArrow(', page)
            self.assertIn('| `VisualLogger::LogArrow` | `CategoryName` | `FName("VisLogBP")` |', page)
            self.assertNotIn('static void VisualLogger::LogArrow', page)
            self.assertIn('有意改进' if language == 'zh' else 'Intentional improvement', page)
        policy['partitions']['fork'][0]['counterpart'] = 'wrong'
        with self.assertRaisesRegex(ValueError, 'Unpaired'):
            renderer.render(policy, 'en')

    def test_examples_are_limited_and_span_owners(self):
        rows = {(f'Owner{i}::Function', 'Arg', str(i)) for i in range(8)}
        examples = renderer.examples_by_owner(rows)
        self.assertEqual(len(examples), 5)
        self.assertTrue(set(examples) <= rows)
        self.assertEqual(len({row[0].split('::')[0] for row in examples}), 5)

    def test_distribution_examples_are_deterministic_and_distinct(self):
        rows = [('enum', 'EOne', 'EOne'), ('enum-value', 'EOne', 'EOne · A'),
                ('type', 'EOne', 'EOne type'), ('type', 'FData', 'FData'),
                ('global-function', 'UClass', 'UClass::Call()'),
                ('method', 'FOther', 'FOther::Call()'), ('property', 'USettings', 'USettings::Value')]
        expected = ['EOne', 'FData', 'UClass::Call()', 'FOther::Call()', 'USettings::Value']
        self.assertEqual(renderer.distribution_examples(rows), expected)
        self.assertEqual(renderer.distribution_examples(list(reversed(rows))), expected)
        self.assertEqual(renderer.distribution_examples(rows[:3]), ['EOne'])

    def test_native_call_residuals_use_reviewed_bilingual_text(self):
        policy = self.policy()
        policy['nativeCallResiduals'] = [{
            'id': 'example.copy', 'module': 'Example', 'owner': 'Example', 'function': 'Call',
            'signature': 'int Call()', 'cppSignature': 'int Call();', 'asSignature': 'int Example::Call()', 'kind': 'return-copy', 'scope': 'always',
            'matrixCell': 'cell-1', 'ueVersions': ['5.8.4'],
            'decision': {'by': 'user', 'date': '2026-10-31'}, 'evidence': ['private/path'],
            'text': {'zh': {'what': '返回副本。', 'why': '技术限制：调用方式不同。', 'impact': '修改副本不影响原值。'},
                     'en': {'what': 'Returns a copy.', 'why': 'Technical limitation: the call route differs.', 'impact': 'Changes affect only the copy.'}}}]
        for language, phrase in [('zh', '返回副本。'), ('en', 'Returns a copy.')]:
            page = renderer.render(policy, language)
            self.assertIn(phrase, page)
            self.assertIn('Example::Call', page)
            self.assertIn('```angelscript\n// C++\nint Call();\n// AngelScript\nint Example::Call()\n```', page)
            self.assertIn('技术限制' if language == 'zh' else 'Technical limitation', page)
            self.assertNotIn('5.8.4', page)
            self.assertNotIn('private/path', page)
            self.assertNotIn('cell-1', page)
        policy['nativeCallResiduals'][0]['text']['zh']['impact'] = ' '
        with self.assertRaisesRegex(ValueError, 'complete bilingual wording'):
            renderer.render(policy, 'en')
        policy['nativeCallResiduals'][0]['text']['zh']['impact'] = '修改副本不影响原值。'
        for key in ('cppSignature', 'asSignature'):
            for invalid in (None, '', '  '):
                incomplete = json.loads(json.dumps(policy))
                if invalid is None:
                    del incomplete['nativeCallResiduals'][0][key]
                else:
                    incomplete['nativeCallResiduals'][0][key] = invalid
                with self.assertRaisesRegex(ValueError, r'C\+\+ and AS signatures'):
                    renderer.render(incomplete, 'en')
        policy['nativeCallResiduals'][0]['text']['en']['why'] = 'Intentional improvement: mismatched.'
        with self.assertRaisesRegex(ValueError, 'matching reviewed reason categories'):
            renderer.render(policy, 'en')
        policy['nativeCallResiduals'][0]['text']['en']['why'] = 'Technical limitation: the call route differs.'
        policy['nativeCallResiduals'].append(policy['nativeCallResiduals'][0])
        with self.assertRaisesRegex(ValueError, 'Duplicate'):
            renderer.render(policy, 'en')

    def test_old_version_residuals_are_not_published(self):
        policy = self.policy()
        policy['nativeCallResiduals'] = [{'id': 'old', 'ueVersions': ['5.6.1']}]
        for language in ('zh', 'en'):
            self.assertNotIn('old', renderer.render(policy, language))

    def test_unpaired_records_fail(self):
        policy = self.policy()
        policy['partitions']['fork'].append({'category': 'upstream-bug-fix', 'reason': 'fix',
            'collector': 'docs', 'direction': 'added', 'record': 'method|Thing|Call()', 'counterpart': 'old'})
        with self.assertRaisesRegex(ValueError, 'Unpaired'):
            renderer.render(policy, 'en')


if __name__ == '__main__':
    unittest.main()
