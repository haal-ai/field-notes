"""Public glossary: built from content/glossaire.md, first-use links, coverage checks."""
import re
import unittest
from datetime import date

import build
import glossary
from test_figures_drafts import SVG
from test_french import FrenchSite, fr_entry

GLOSSARY = """# Glossaire

## token
Un token est un morceau de texte.

## KV cache
match: KV caches?
Le KV cache garde les keys et les values déjà calculées.

## prefill
Le prefill lit le prompt d'un coup.

## prompt
Le prompt est le texte donné au modèle.
"""
BODY = ('# Titre\\n\\n## Le prompt\\n\\nUn prompt devient des tokens. Le KV cache grandit. Encore un token et un autre prompt.\\n\\n'
        '![Un token dans un figure](fig1.svg)\\n\\n![Le prefill](fig2.svg)\\n\\n![Le KV cache](fig3.svg)\\n').replace('\\n', '\n')


class GlossaryTests(FrenchSite):
    def setup_site(self, gloss=GLOSSARY, body=BODY):
        art, folder = self.add_fr(body=body)
        for i in (1, 2, 3):
            (folder / f'fig{i}.alt.md').write_text('Le prefill, le prompt, le token et le KV cache.\n')
        if gloss is not None:
            (self.tmp / 'content/glossaire.md').write_text(gloss)
        self.write_catalogue(art, keep_real=False)
        return art

    def build(self):
        build.build(date(2026, 11, 25))
        return (self.tmp / '_site/glossaire/index.html').read_text()

    def test_glossary_page_has_an_anchor_definition_and_users_per_term_and_a_figure(self):
        self.setup_site()
        page = self.build()
        for slug in ('token', 'kv-cache', 'prefill', 'prompt'):
            self.assertIn(f'id="{slug}"', page)
        self.assertIn('Un token est un morceau de texte.', page)
        self.assertIn('href="../boites/index.html"', page)          # the entry links to the article that uses the term
        self.assertIn('data-learning-visual', page)                  # every page carries an explanatory visual
        self.assertEqual(page.count('class="gloss-entry"'), 4)

    def test_header_and_footer_link_to_the_glossary_on_every_page(self):
        self.setup_site()
        self.build()
        for p in (self.tmp / '_site').rglob('*.html'):
            text = p.read_text()
            self.assertEqual(text.count('>Glossaire</a>'), 2, p)   # header nav + footer
        self.assertIn('Glossaire', (self.tmp / '_site/index.html').read_text())

    def test_only_the_first_use_in_the_body_is_linked_and_it_resolves(self):
        self.setup_site()
        self.build()
        page = self.page('boites')
        anchors = set(re.findall(r'id="([^"]+)"', (self.tmp / '_site/glossaire/index.html').read_text()))
        links = re.findall(r'<a class="gloss" href="\.\./glossaire/index\.html#([^"]+)">([^<]+)</a>', page)
        self.assertEqual(sorted(s for s, _ in links), ['kv-cache', 'prompt', 'token'])   # one link per term, none twice
        for slug, _ in links:
            self.assertIn(slug, anchors)
        self.assertEqual(page.count('Un <a class="gloss"'), 1)
        self.assertNotIn('<h2>Le <a', page)                          # headings are not linked
        self.assertNotIn('figcaption><a', page)                      # figure captions are not linked

    def test_a_key_term_used_without_an_entry_fails_the_build(self):
        self.setup_site(gloss=GLOSSARY.replace('## prompt\nLe prompt est le texte donné au modèle.\n', ''))
        with self.assertRaisesRegex(ValueError, 'key term used but not defined: prompt'):
            self.build()

    def test_an_entry_no_article_uses_fails_the_build(self):
        self.setup_site(gloss=GLOSSARY + '\n## quantization\nUne définition.\n')
        with self.assertRaisesRegex(ValueError, 'entry not used by any article: quantization'):
            self.build()

    def test_preview_reports_glossary_problems_as_warnings(self):
        self.setup_site(gloss=GLOSSARY + '\n## quantization\nUne définition.\n')
        warnings = build.build(date(2026, 11, 25), preview=True)
        self.assertTrue(any('quantization' in w for w in warnings))

    def test_a_broken_glossary_link_is_refused(self):
        good = '<a class="gloss" href="../glossaire/index.html#token">token</a>'
        glossary.check_links({'ok': good}, {'token'})
        with self.assertRaisesRegex(ValueError, 'Broken glossary link'):
            glossary.check_links({'page': good.replace('#token', '#nope')}, {'token'})

    def test_without_a_glossary_file_there_is_no_glossary_page_or_link(self):
        self.write_catalogue()
        build.build(date(2026, 11, 25))
        self.assertFalse((self.tmp / '_site/glossaire').exists())
        self.assertNotIn('glossaire', (self.tmp / '_site/index.html').read_text())

    def test_draft_folder_glossary_overrides_the_site_one(self):
        self.write_catalogue()
        staging = self.tmp / 'staging'
        staging.mkdir()
        (staging / 'glossaire.md').write_text(GLOSSARY)
        warnings = build.build(date(2026, 11, 25), preview=True, drafts=[staging])
        self.assertTrue((self.tmp / '_preview/glossaire/index.html').is_file())
        self.assertTrue(any('key term used but not defined' in w for w in warnings))   # the English fixture articles use terms this glossary lacks

    def test_parse_rejects_an_entry_without_definition(self):
        with self.assertRaises(ValueError):
            glossary.parse('## token\n')

    def test_overlapping_terms_link_the_longer_one(self):
        entries = glossary.parse('## decoding\nA.\n\n## speculative decoding\nB.\n')
        out = glossary.link_terms('<p>Le speculative decoding puis le decoding.</p>', entries, 'g.html')
        self.assertIn('>speculative decoding</a>', out)
        self.assertIn('>decoding</a>', out)
        self.assertEqual(out.count('<a '), 2)


if __name__ == '__main__':
    unittest.main()
