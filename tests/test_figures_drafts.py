"""Per-page SVG figures, markdown articles, and the draft gate (public refuses, preview allows)."""
import copy
import json
import shutil
import tempfile
import unittest
from datetime import date
from pathlib import Path
from unittest import mock

import build
import render

SVG = ('<svg xmlns="http://www.w3.org/2000/svg" role="img" aria-labelledby="t d" viewBox="0 0 300 120" width="300">'
       '<title id="t">Two boxes</title><desc id="d">A box and a second box</desc>'
       '<style>svg{--_c:var(--text,#111)}.h{fill:var(--_c)}@media(prefers-color-scheme:dark){svg{--_c:var(--text,#eee)}}</style>'
       '<text class="h" x="5" y="20">A</text></svg>')
BODY = ('# Title\n\nIntro with a [link](https://example.org/a) and `code` and **bold** and *italic*.\n\n'
        '## Section\n\n- one\n- two\n\n1. first\n2. second\n\n| A | B |\n|---|---|\n| 1 | 2 |\n\n'
        '![Two boxes](visual.svg)\n\n```\nx = 1 < 2\n```\n\n<!-- hidden note -->\n')


def entry(slug, **extra):
    base = {'slug': slug, 'title': 'T ' + slug, 'section': 'Model internals', 'type': 'guide', 'summary': 'S',
            'author': 'Jean Marin', 'perspective': 'Individual view: independent summary', 'published': '2026-11-25',
            'edited': '2026-11-25', 'reviewed': '2026-11-25', 'review_months': 6, 'approval': 'approved-publication',
            'formats': ['Article'], 'history': [{'date': '2026-11-25', 'note': 'First publication.'}],
            'visual': {'kind': 'svg', 'svg': 'visual.svg', 'alt': 'alt.md', 'title': 'Two boxes',
                       'caption': 'One box leads to another.'}}
    base.update(extra)
    return base


class TempSite(unittest.TestCase):
    """A throwaway site root: the real catalogue plus content/articles/<slug>/ folders."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp)
        (self.tmp / 'content/articles').mkdir(parents=True)
        if (build.ROOT / 'content/articles').is_dir():
            shutil.copytree(build.ROOT / 'content/articles', self.tmp / 'content/articles', dirs_exist_ok=True)
        shutil.copytree(build.ROOT / 'assets', self.tmp / 'assets')
        for patch in [mock.patch.object(build, 'ROOT', self.tmp), mock.patch.object(build, 'OUT', self.tmp / '_site'),
                      mock.patch.object(build, 'PREVIEW_OUT', self.tmp / '_preview')]:
            patch.start()
            self.addCleanup(patch.stop)
        self.real = json.loads((Path(__file__).resolve().parents[1] / 'content/catalogue.json').read_text())

    def add(self, article, body=BODY, svg=SVG, alt='Box A leads to box B.\n', folder=None):
        folder = Path(folder) if folder else self.tmp / 'content/articles' / article['slug']
        folder.mkdir(parents=True, exist_ok=True)
        if body is not None:
            (folder / 'article.md').write_text(body)
        if svg is not None:
            (folder / 'visual.svg').write_text(svg)
        if alt is not None:
            (folder / 'alt.md').write_text(alt)
        return folder

    def write_catalogue(self, *articles, keep_real=True):
        data = copy.deepcopy(self.real)
        data['articles'] = (data['articles'] if keep_real else []) + list(articles)
        (self.tmp / 'content/catalogue.json').write_text(json.dumps(data))

    def page(self, slug, preview=False):
        return ((self.tmp / ('_preview' if preview else '_site')) / slug / 'index.html').read_text()


class SvgFigureTests(TempSite):
    def test_svg_is_embedded_inline_with_caption_and_text_equivalent(self):
        self.add(entry('boxes'))
        self.write_catalogue(entry('boxes'))
        build.build(date(2026, 11, 25))
        page = self.page('boxes')
        self.assertIn('<figure data-learning-visual="svg"><svg', page)
        self.assertIn('<figcaption>One box leads to another.</figcaption>', page)
        self.assertIn('Box A leads to box B.', page)       # alt.md rendered as the text equivalent
        self.assertNotIn('<img', page)                     # inline, no external file: works without JavaScript
        self.assertIn('var(--text,#111)', page)            # theme variables kept, so light and dark follow the site
        self.assertEqual(page.count('<figure'), 1)         # figure placed at the marker, not repeated

    def test_svg_styles_and_ids_are_scoped_to_the_page_figure(self):
        scoped = render.inline_svg(SVG, 'boxes')
        self.assertIn('#fig-boxes .h{', scoped)
        self.assertIn('#fig-boxes{--_c:', scoped)
        self.assertIn('aria-labelledby="fig-boxes-t fig-boxes-d"', scoped)
        self.assertNotIn('\nsvg{', scoped)

    def test_unsafe_svg_is_refused(self):
        for bad in ['<script>1</script>', '<image href="https://x.test/a.png"/>', '<a href="https://x.test">x</a>']:
            with self.assertRaises(ValueError):
                render.inline_svg(SVG.replace('<text', bad + '<text'), 'boxes')

    def test_public_build_requires_text_equivalent_and_real_caption(self):
        self.add(entry('boxes'), alt=None)
        self.write_catalogue(entry('boxes'))
        with self.assertRaises(ValueError):
            build.build(date(2026, 11, 25))
        self.add(entry('boxes'))
        placeholder = entry('boxes')
        placeholder['visual']['caption'] = 'PLACEHOLDER for the flow renderer'
        self.write_catalogue(placeholder)
        with self.assertRaises(ValueError):
            build.build(date(2026, 11, 25))

    def test_existing_three_step_flow_still_works(self):
        self.write_catalogue()
        build.build(date(2026, 11, 25))
        page = self.page('how-these-notes-age')
        self.assertIn('data-learning-visual="flow"', page)
        self.assertNotIn('data-learning-visual="svg"', page)


class MarkdownTests(unittest.TestCase):
    def test_subset_renders(self):
        warnings = []
        html, used = render.markdown(BODY, 'visual.svg', '<figure>F</figure>', warnings)
        self.assertTrue(used)
        self.assertNotIn('<h1>', html)                       # title comes from the entry
        for fragment in ['<h2>Section</h2>', '<ul><li>one</li>', '<ol><li>first</li>', '<table>', '<th>A</th>',
                         '<a href="https://example.org/a">link</a>', '<code>code</code>', '<strong>bold</strong>',
                         '<em>italic</em>', '<figure>F</figure>', '<pre><code>x = 1 &lt; 2']:
            self.assertIn(fragment, html)
        self.assertNotIn('hidden note', html)
        self.assertEqual(warnings, [])

    def test_html_is_escaped_and_unsafe_links_are_text(self):
        warnings = []
        html, _ = render.markdown('<script>alert(1)</script> [x](javascript:alert(1))', warnings=warnings)
        self.assertNotIn('<script>', html)
        self.assertNotIn('href="javascript', html)
        self.assertTrue(warnings)


class DraftWorkflowTests(TempSite):
    def draft(self, slug='draft-page', **extra):
        art = entry(slug, published=None, edited=None, reviewed=None, approval='draft', status='draft', **extra)
        art['history'] = [{'date': 'TBD at release', 'note': 'First publication.'}]
        return art

    def test_public_build_refuses_drafts_and_keeps_site_clean(self):
        self.add(self.draft())
        self.write_catalogue(self.draft())
        with self.assertRaisesRegex(ValueError, 'refused in a public build'):
            build.build(date(2026, 11, 25))
        self.assertFalse((self.tmp / '_site/draft-page').exists())

    def test_public_build_refuses_unapproved_or_undated_entries(self):
        self.add(entry('boxes'))
        for change in [{'approval': 'pending'}, {'status': 'draft'}, {'published': 'TBD at release'},
                       {'published': None}, {'edited': '2026-13-45'}]:
            self.write_catalogue(entry('boxes', **change))
            with self.assertRaises(ValueError, msg=str(change)):
                build.build(date(2026, 11, 25))

    def test_public_build_refuses_unfinished_text_in_the_article(self):
        self.add(entry('boxes'), body=BODY + '\n*[Visual placeholder: add the figure]*\n')
        self.write_catalogue(entry('boxes'))
        with self.assertRaisesRegex(ValueError, 'unfinished'):
            build.build(date(2026, 11, 25))

    def test_drafts_folder_needs_preview_mode(self):
        with self.assertRaises(ValueError):
            build.build(date(2026, 11, 25), drafts=[self.tmp])

    def test_preview_builds_draft_into_preview_only(self):
        self.write_catalogue()
        staging = self.tmp / 'staging'
        self.add(self.draft(), folder=staging / 'draft-page')
        (staging / 'draft-page/entry.json').write_text(json.dumps(self.draft()))
        build.build(date(2026, 11, 25), preview=True, drafts=[staging])
        page = self.page('draft-page', preview=True)
        self.assertIn('PRIVATE PREVIEW', page)
        self.assertIn('noindex', page)
        self.assertIn('Draft (not published)', page)
        self.assertIn('Set at publication', page)            # no invented date
        self.assertIn('Individual view', page)               # perspective label
        self.assertIn('not a HAAL publication or position', page)
        self.assertIn('<h2>Section</h2>', page)              # full article from the markdown file
        self.assertFalse((self.tmp / '_site').exists())      # nothing reaches the deployable directory

    def test_preview_reports_unfinished_text_instead_of_failing(self):
        self.write_catalogue()
        staging = self.tmp / 'staging'
        self.add(self.draft(), body=BODY + '\n*[Visual placeholder]*\n', alt=None, folder=staging / 'draft-page')
        (staging / 'draft-page/entry.json').write_text(json.dumps(self.draft()))
        warnings = build.build(date(2026, 11, 25), preview=True, drafts=[staging])
        self.assertTrue(any('unfinished' in w for w in warnings))
        self.assertTrue(any('text equivalent' in w for w in warnings))

    def test_public_build_after_preview_has_no_preview_marker(self):
        self.write_catalogue()
        build.build(date(2026, 11, 25), preview=True)
        build.build(date(2026, 11, 25))
        for page in (self.tmp / '_site').rglob('*.html'):
            self.assertNotIn('PRIVATE PREVIEW', page.read_text())
            self.assertNotIn('noindex', page.read_text())


class CatalogueNavigationTests(TempSite):
    def build_index(self, *extra):
        self.write_catalogue(*extra)
        build.build(date(2026, 11, 25))
        return (self.tmp / '_site/index.html').read_text()

    def test_whole_entry_is_one_link_target_named_by_its_title(self):
        index = self.build_index()
        rows = index.split('<article class="entry"')[1:]
        self.assertEqual(len(rows), len(self.real['articles']))
        for row in rows:
            row = row.split('</article>')[0]
            self.assertEqual(row.count('<a '), 1)  # one link per entry; its stretched area covers the row
            self.assertIn('class="entry-title" href="', row)
        css = (build.ROOT / 'assets/publication.css').read_text()
        self.assertRegex(css, r'\.entry-title::after\{content:"";position:absolute;inset:0')
        self.assertIn('.entry-title:focus-visible::after{outline', css)
        self.assertIn('<a class="featured" href=', index)

    def test_entries_are_grouped_under_section_headings(self):
        index = self.build_index()
        sections = {a['slug']: a['section'] for a in self.real['articles']}
        self.assertEqual({sections[s] for s in ('vllm-and-sglang', 'quantization-explained', 'how-llms-process-a-prompt')}, {'Inference'})
        self.assertEqual(sections['code-graph-pilot'], 'Evaluation')
        self.assertEqual(sections['how-these-notes-age'], 'About this library')
        for name in set(sections.values()):
            block = index.split(f'<h3 id="section-{build.slugify(name)}"')[1].split('</section>')[0]
            self.assertIn(f'>{name}<span class="section-count">', '>' + block.split('>', 1)[1])
            for slug, sec in sections.items():
                self.assertEqual(f'href="{slug}/index.html"' in block, sec == name, slug)
        for retired in ('Inference servers', 'Model internals'):
            self.assertNotIn(retired, index)
        self.assertEqual(index.count('class="topic-button'), 1 + len(set(sections.values())))
        self.assertIn('Inference<span>03</span>', index)

    def test_empty_sections_are_omitted(self):
        index = self.build_index()
        self.assertNotIn('section-publication-process', index)
        self.assertEqual(index.count('class="entry-section"'), len({a['section'] for a in self.real['articles']}))

    def test_script_hides_sections_left_empty_by_a_filter(self):
        self.assertIn('.entry-section', (build.ROOT / 'assets/site.js').read_text())

    def test_trial_page_removed_and_old_url_points_to_catalogue(self):
        self.write_catalogue()
        build.build(date(2026, 11, 25))
        site = self.tmp / '_site'
        self.assertNotIn('publication-trial', [a['slug'] for a in self.real['articles']])
        self.assertFalse(any('trial' in p.read_text().lower() for p in site.rglob('*.html')))
        old = (site / 'publication-trial/index.html').read_text()
        self.assertIn('href="../index.html"', old)
        self.assertNotIn('Publication trial', (site / 'index.html').read_text())
        self.assertNotIn('publication-trial', (site / 'catalogue.json').read_text())
        self.assertNotIn('publication-trial', (site / 'maintenance/ledger.json').read_text())

    def test_outdated_news_flagged_for_archive_control(self):
        news = entry('sample-news', type='news', section='Inference')
        news.pop('reviewed'), news.pop('review_months')
        self.add(news)
        self.write_catalogue(news)
        build.build(date(2027, 3, 1))
        index = (self.tmp / '_site/index.html').read_text()
        self.assertIn('data-outdated="true"', index)
        self.assertIn('data-kind="news" aria-pressed', index)  # the News filter returns with the first news entry
        self.assertIn('id="archive"', index)
        self.assertIn('Inference<span>03</span>', index)  # outdated news is not counted as current


class ExistingPagesUnchanged(TempSite):
    def test_public_output_of_current_pages_has_no_preview_state(self):
        self.write_catalogue()
        build.build(date(2026, 11, 25))
        index = (self.tmp / '_site/index.html').read_text()
        self.assertGreaterEqual(index.count('class="entry"'), 1)
        self.assertNotIn('status-draft', index)
        ledger = json.loads((self.tmp / '_site/maintenance/ledger.json').read_text())
        self.assertLessEqual({'how-these-notes-age'}, {i['slug'] for i in ledger['items']})


if __name__ == '__main__':
    unittest.main()
