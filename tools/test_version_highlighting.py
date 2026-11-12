import unittest

from tools.build_docs import inline, mark_html_text, render
from tools.qa_pages import ENGINE_VERSION_RE, TreeParser, allowed_version, version_context


class VersionHighlightingTest(unittest.TestCase):
    def test_explicit_engine_and_soloas_versions_are_marked(self):
        source = (
            'UE 5.7.4; UE 5.8; UE 5.4–5.8; UE 5.7.4–5.8.4; '
            'Unreal Engine 5.8.4; soloAS 0.3.0; v0.3.0; 0.2.x; 0.1.x; 0.3.x'
        )
        result = inline(source)
        self.assertEqual(result.count('class="ver"'), 10)
        for text in ('UE 5.7.4', 'UE 5.8', 'UE 5.4–5.8', 'UE 5.7.4–5.8.4',
                     'Unreal Engine 5.8.4', 'soloAS 0.3.0', 'v0.3.0', '0.2.x', '0.1.x', '0.3.x'):
            self.assertIn(f'<span class="ver">{text}</span>', result)

    def test_page_outline_contains_h2_and_h3_only(self):
        _, toc = render('# Title\n\n## Section\n\n### Detail\n\n#### Minor')
        self.assertIn('class="toc-h2" href="#section"', toc)
        self.assertIn('class="toc-h3" href="#detail"', toc)
        self.assertNotIn('#minor', toc)

    def test_connected_engine_versions_are_marked(self):
        for delimiter in ('和', ' and ', '、', ', '):
            text = f'UE 5.7.4{delimiter}5.8.4'
            self.assertEqual(inline(text), f'<span class="ver">{text}</span>')

    def test_changelog_heading_marks_the_whole_release_version(self):
        result = inline('0.3.0 · UE 5.7.4–5.8.4')
        self.assertEqual(result, '<span class="ver">0.3.0 · UE 5.7.4–5.8.4</span>')

    def test_plain_engine_versions_are_marked_only_in_version_tables(self):
        source = '| Engine |\n| --- |\n| 5.7.4 |'
        regular_body, _ = render(source)
        version_body, _ = render(source, version_table=True)
        self.assertNotIn('class="ver"', regular_body)
        self.assertIn('<td><span class="ver">5.7.4</span></td>', version_body)
        list_body, _ = render('| Engine versions |\n| --- |\n| 5.4、5.5、5.6 |', version_table=True)
        self.assertIn('<td><span class="ver">5.4、5.5、5.6</span></td>', list_body)

    def test_codes_urls_attributes_metrics_and_other_versions_are_not_marked(self):
        source = (
            '1.5×; Windows 11; VS 2022; SDK 10.0.22621.0; 2026-11-12; '
            'https://example.com/UE-5.7.4/v0.3.0; `UE 5.7.4`; '
            '![UE 5.7.4](https://example.com/0.3.0.png); '
            '<img alt="UE 5.7.4" src="https://example.com/v0.3.0.png">'
        )
        result = inline(source)
        self.assertNotIn('class="ver"', result)

    def test_raw_html_text_skips_title_code_pre_and_attributes(self):
        source = (
            '<title>UE 5.7.4</title><p>UE 5.8; 1.5×</p>'
            '<a href="https://example.com/UE-5.7.4">soloAS 0.3.0</a>'
            '<pre>UE 5.7.4</pre><code>v0.3.0</code>'
        )
        result = mark_html_text(source)
        self.assertIn('<title>UE 5.7.4</title>', result)
        self.assertIn('<p><span class="ver">UE 5.8</span>; 1.5×</p>', result)
        self.assertIn('href="https://example.com/UE-5.7.4">', result)
        self.assertIn('<span class="ver">soloAS 0.3.0</span>', result)
        self.assertIn('<pre>UE 5.7.4</pre><code>v0.3.0</code>', result)

    def test_learn_page_rendering_can_skip_version_marks(self):
        body, _ = render('# Learning article\n\nUE 5.7.4 and soloAS 0.3.0', mark_version_text=False)
        self.assertNotIn('class="ver"', body)
        self.assertIn('UE 5.7.4 and soloAS 0.3.0', body)

    def test_qa_keeps_support_context_across_version_spans(self):
        parser = TreeParser()
        parser.feed('<p>All soloAS 0.2.1 plugins support stock <span class="ver">Unreal Engine 5.7.4 and 5.8.4</span>.</p>')
        version_node = next(node for node in parser.root.walk()
                            if node.tag == '#text' and 'Unreal Engine' in node.data)
        match = ENGINE_VERSION_RE.search(version_node.data)
        context = version_context(version_node, match)
        self.assertIn('support stock', context)
        self.assertTrue(allowed_version('docs/en/requirements.html', context, match))

    def test_qa_still_rejects_an_unrelated_engine_version(self):
        parser = TreeParser()
        parser.feed('<p>Support stock Unreal Engine 5.7.4; Unreal Engine 5.6.1 remains unsupported.</p>')
        version_node = next(node for node in parser.root.walk()
                            if node.tag == '#text' and 'Unreal Engine 5.6.1' in node.data)
        match = list(ENGINE_VERSION_RE.finditer(version_node.data))[1]
        context = version_context(version_node, match)
        self.assertFalse(allowed_version('docs/en/overview.html', context, match))


if __name__ == '__main__':
    unittest.main()
