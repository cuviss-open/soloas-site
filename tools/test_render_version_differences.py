import unittest

import render_version_differences as renderer


class VersionDifferencesTest(unittest.TestCase):
    def test_composition_preserves_current_and_legacy_content(self):
        current = '<!-- marker -->\n\n# Current\n\nFor 0.2.0.\n\n## Current section\n'
        legacy = '<!-- marker -->\n\n# Title\n\nFor 0.1.3.\n\n## Core\n\n| 5.4 | Legacy |\n'
        for language in ('zh', 'en'):
            result = renderer.compose(current, legacy, language)
            self.assertIn('### Current section', result)
            self.assertIn('### Core', result)
            self.assertIn('| 5.4 | Legacy |', result)
            self.assertNotIn('For 0.1.3.', result)
            self.assertNotIn('For 0.2.0.', result)
            self.assertEqual(result.count('\n## '), 3)
            from build_docs import render
            body, _ = render(result)
            import re
            for anchor in re.findall(r'href="(#.*?)"', body):
                self.assertIn('id="' + anchor[1:] + '"', body)



if __name__ == '__main__':
    unittest.main()
