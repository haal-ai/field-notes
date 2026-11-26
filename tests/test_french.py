"""French site: wording, dates, lang, and the multi-figure article contract (figN.svg + figN.alt.md)."""
import json
import re
import unittest
from datetime import date

import build
import strings_fr
from strings_fr import T
from test_figures_drafts import SVG, TempSite, entry

ENGLISH_CHROME = ['Skip to', 'Theme', 'Review ledger', 'News archive', 'Last updated', 'Published', 'Open the',
                  'Text equivalent', 'Show older', 'First published', 'Last edited', 'Revision history']


def fr_body(n, caption='Une figure'):
    lines = ['# Titre', '', 'Un court texte.', '']
    for i in range(1, n + 1):
        lines += [f'## Partie {i}', '', f'![{caption} {i}](fig{i}.svg)', '']
    return '\n'.join(lines)


def fr_entry(slug='boites', **extra):
    art = entry(slug, lang='fr', section='Inférence',
                formats=['Article'])
    art.pop('visual')
    art.update(extra)
    return art


class FrenchSite(TempSite):
    def add_fr(self, slug='boites', n=3, folder=None, body=None, skip=(), **extra):
        art = fr_entry(slug, **extra)
        folder = self.add(art, body=fr_body(n) if body is None else body, svg=None, alt=None, folder=folder)
        for i in range(1, n + 1):
            if f'fig{i}.svg' not in skip:
                (folder / f'fig{i}.svg').write_text(SVG)
            if f'fig{i}.alt.md' not in skip:
                (folder / f'fig{i}.alt.md').write_text(f'Texte de la figure {i}.\n')
        return art, folder

    def public(self, art):
        self.write_catalogue(art)
        build.build(date(2026, 11, 25))


class WordingAndDates(FrenchSite):
    def test_every_page_is_french_with_lang_fr(self):
        self.write_catalogue()
        build.build(date(2026, 11, 25))
        for page in (self.tmp / '_site').rglob('*.html'):
            self.assertIn('<html lang="fr">', page.read_text(), page)
        for name in ('index.html', 'archive/index.html', 'maintenance/index.html', '404.html', 'publication-trial/index.html'):
            text = (self.tmp / '_site' / name).read_text()
            for word in ENGLISH_CHROME:
                self.assertNotIn(word, text, f'{name}: {word}')

    def test_french_labels_on_catalogue_and_ledger(self):
        self.write_catalogue()
        build.build(date(2026, 11, 25))
        index = (self.tmp / '_site/index.html').read_text()
        for label in ['Aller au contenu', 'Thème : système', 'Suivi des relectures', 'Archives', 'Sections', 'Guides',
                      'Expériences', 'Afficher les anciennes actualités', 'placeholder="Chercher une explication',
                      'Article avec figures', 'Comprendre.', 'À propos de la bibliothèque', 'Évaluation', 'Inférence',
                      'Lire l’explication']:
            self.assertIn(label, index)
        ledger = (self.tmp / '_site/maintenance/index.html').read_text()
        self.assertIn('Échéance', ledger)
        self.assertRegex(ledger, r'\d+ (janv|févr|mars|avr|mai|juin|juil|août|sept|oct|nov|déc)\.? 20')

    def test_dates_in_french_without_os_locale(self):
        self.assertEqual(build.day('2026-11-25'), '25 nov. 2026')
        self.assertEqual(build.day('2026-12-01'), '1er déc. 2026')
        self.assertEqual(build.day('2026-02-05'), '5 févr. 2026')
        self.assertEqual(build.day('2026-08-05'), '5 août 2026')
        self.assertEqual(strings_fr.fr_month_year(date(2026, 11, 25)), 'novembre 2026')
        self.assertEqual(strings_fr.fr_month_year(date(2027, 6, 1)), 'juin 2027')

    def test_status_labels(self):
        guide = next(a for a in self.real['articles'] if a['type'] == 'guide')
        self.assertEqual(build.lifecycle(guide, date(2026, 11, 26))['status'], 'À jour · prochaine relecture mai 2027')
        self.assertEqual(build.lifecycle(guide, date(2027, 6, 1))['status'], 'À relire')
        exp = next(a for a in self.real['articles'] if a['type'] == 'experiment')
        self.assertTrue(build.lifecycle(exp, date(2026, 11, 26))['status'].startswith('Expérience · testée le '))

    def test_article_page_metadata_labels(self):
        art, _ = self.add_fr()
        self.public(art)
        page = self.page('boites')
        for label in ['Première publication', 'Dernière modification', 'Dernière relecture',
                      'Prochaine relecture', 'Historique des révisions']:
            self.assertIn(label, page)
        for gone in ['Auteur', 'Avis individuel', 'Dernière vérification']:
            self.assertNotIn(gone, page)

    def test_script_reads_its_strings_from_the_page(self):
        js = (build.ROOT / 'assets/site.js').read_text()
        self.assertIn("getElementById('i18n')", js)
        self.assertNotRegex(js, r"'(Theme|entry|entries| of )[^']*'")
        self.write_catalogue()
        build.build(date(2026, 11, 25))
        raw = re.search(r'<script type="application/json" id="i18n">(.*?)</script>', (self.tmp / '_site/index.html').read_text()).group(1)
        data = json.loads(raw)
        self.assertEqual(data['of'], 'sur')
        self.assertEqual(data['notes_count']['other'], '{n} notes')


class NoticeAndNoByline(FrenchSite):
    BANNED = ['Jean Marin', 'Avis individuel', 'Point de vue individuel', 'position de HAAL', 'Publications HAAL',
              'publications HAAL', 'avis personnels', 'Auteur']

    def test_built_site_has_no_byline_or_organisation_wording_and_every_article_has_the_notice(self):
        art, _ = self.add_fr()
        self.write_catalogue(art)
        build.build(date(2026, 11, 25))
        pages = list((self.tmp / '_site').rglob('*.html')) + list((self.tmp / '_site').rglob('*.json'))
        for page in pages:
            text = page.read_text()
            for word in self.BANNED:
                self.assertNotIn(word, text, f'{page.name}: {word}')
        for a in json.loads((self.tmp / '_site/catalogue.json').read_text())['articles']:
            self.assertIn(T['notice_all'].replace("'", '&#x27;'), (self.tmp / '_site' / a['slug'] / 'index.html').read_text())
        self.assertEqual(T['notice_all'], "Cet article n'a pas de valeur scientifique et n'est pas la copie d'une autre publication. "
                         "Il n'est pas contre-vérifié : c'est un simple partage, sans ambition.")

    def test_review_labels_say_relecture(self):
        for old in ['Dernière vérification', 'Prochaine vérification', 'prochaine vérification', 'À vérifier']:
            self.assertNotIn(old, ' '.join(str(v) for v in T.values()))


class MultiFigureArticles(FrenchSite):
    def test_three_markers_render_three_inline_figures(self):
        art, _ = self.add_fr()
        self.public(art)
        page = self.page('boites')
        self.assertEqual(page.count('<figure data-learning-visual="svg">'), 3)
        for i in (1, 2, 3):
            self.assertIn(f'<figcaption>Une figure {i}</figcaption>', page)
            self.assertIn(f'Texte de la figure {i}.', page)
            self.assertIn(f'id="fig-boites-fig{i}"', page)           # scoped per figure
            self.assertIn(f'aria-labelledby="fig-boites-fig{i}-t fig-boites-fig{i}-d"', page)
        self.assertEqual(page.count('<summary>Équivalent textuel de la figure</summary>'), 3)
        self.assertNotIn('<img', page)
        self.assertIn('var(--text,#111)', page)                      # theme variables kept
        self.assertNotIn('lang="en"', page)                          # French article: no English language mark
        # figures sit in the body at their marker, in order
        order = [page.index(f'Une figure {i}</figcaption>') for i in (1, 2, 3)]
        self.assertEqual(order, sorted(order))
        self.assertLess(page.index('Partie 1'), order[0])
        self.assertLess(order[0], page.index('Partie 2'))

    def test_public_build_refuses_a_marker_without_svg(self):
        art, _ = self.add_fr(skip=('fig2.svg',))
        with self.assertRaisesRegex(ValueError, 'fig2.svg: figure file missing'):
            self.public(art)

    def test_public_build_refuses_a_marker_without_alt_md(self):
        art, _ = self.add_fr(skip=('fig3.alt.md',))
        with self.assertRaisesRegex(ValueError, 'fig3.alt.md'):
            self.public(art)

    def test_public_build_refuses_an_empty_caption(self):
        art, _ = self.add_fr(body=fr_body(3).replace('![Une figure 2](fig2.svg)', '![](fig2.svg)'))
        with self.assertRaisesRegex(ValueError, 'empty figure caption'):
            self.public(art)

    def test_public_build_refuses_svg_without_role_img_and_title(self):
        for bad in (SVG.replace(' role="img"', ''), SVG.replace('<title id="t">Two boxes</title>', '')):
            art, folder = self.add_fr()
            (folder / 'fig2.svg').write_text(bad)
            with self.assertRaisesRegex(ValueError, 'role="img"'):
                self.public(art)

    def test_public_build_refuses_a_french_article_with_fewer_than_three_figures(self):
        art, _ = self.add_fr(n=2)
        with self.assertRaisesRegex(ValueError, 'at least 3 figures'):
            self.public(art)

    def test_french_article_with_only_the_legacy_single_visual_is_refused(self):
        art = entry('ancien', lang='fr', section='Inférence')
        self.add(art)
        with self.assertRaisesRegex(ValueError, 'at least 3 figures'):
            self.public(art)

    def test_english_single_visual_entries_still_build(self):
        art = entry('legacy')
        self.add(art)
        self.public(art)
        self.assertEqual(self.page('legacy').count('<figure data-learning-visual="svg">'), 1)
        self.assertIn('lang="en"', self.page('legacy'))              # marked as English text inside the French site

    def test_a_marker_may_not_repeat_a_figure(self):
        art, _ = self.add_fr(body=fr_body(3) + '\n![Encore](fig1.svg)\n')
        with self.assertRaisesRegex(ValueError, 'used twice'):
            self.public(art)

    def test_unknown_lang_is_refused(self):
        art, _ = self.add_fr(lang='de')
        with self.assertRaisesRegex(ValueError, 'lang'):
            self.public(art)


class PreviewOfFrenchDrafts(FrenchSite):
    def stage(self, **kw):
        art, folder = self.add_fr('brouillon', folder=self.tmp / 'work/brouillon', approval='draft', status='draft',
                                  published=None, edited=None, reviewed=None, **kw)
        art['history'] = [{'date': 'à la publication', 'note': 'Première publication.'}]
        (folder / 'entry.json').write_text(json.dumps(art))
        return folder

    def test_complete_draft_previews_without_warning(self):
        self.write_catalogue()
        self.stage()
        warnings = build.build(date(2026, 11, 25), preview=True, drafts=[self.tmp / 'work'])
        self.assertEqual(warnings, [])
        self.assertEqual(self.page('brouillon', preview=True).count('<figure data-learning-visual="svg">'), 3)

    def test_missing_figures_are_warnings_in_preview(self):
        self.write_catalogue()
        folder = self.stage(skip=('fig2.svg', 'fig3.alt.md'))
        warnings = build.build(date(2026, 11, 25), preview=True, drafts=[self.tmp / 'work'])
        text = ' | '.join(warnings)
        self.assertIn('fig2.svg: figure file missing', text)
        self.assertIn('fig3.alt.md', text)
        page = self.page('brouillon', preview=True)
        self.assertIn('Figure manquante : fig2.svg', page)
        self.assertEqual(page.count('<figure data-learning-visual="svg">'), 2)

    def test_too_few_figures_and_bad_svg_are_warnings_in_preview(self):
        self.write_catalogue()
        folder = self.stage()
        (folder / 'article.md').write_text(fr_body(2))
        (folder / 'fig1.svg').write_text(SVG.replace(' role="img"', ''))
        warnings = build.build(date(2026, 11, 25), preview=True, drafts=[self.tmp / 'work'])
        self.assertTrue(any('at least 3 figures' in w for w in warnings))
        self.assertTrue(any('role="img"' in w for w in warnings))

    def test_entry_fr_json_is_preferred_and_replaces_the_english_entry(self):
        self.write_catalogue()
        slug = self.real['articles'][0]['slug']
        art, folder = self.add_fr(slug, folder=self.tmp / 'work' / slug, title='Titre français')
        art['visual'] = {'kind': 'flow', 'title': 'x', 'nodes': list('abcd'), 'details': list('abcd'), 'caption': 'y'}
        (folder / 'entry-fr.json').write_text(json.dumps(art))
        (folder / 'entry.json').write_text(json.dumps(dict(art, title='Ignoré')))
        warnings = build.build(date(2026, 11, 25), preview=True, drafts=[self.tmp / 'work'])
        self.assertEqual(warnings, [])
        page = self.page(slug, preview=True)
        self.assertIn('Titre français', page)
        self.assertNotIn('Ignoré', page)
        self.assertEqual(page.count('<figure data-learning-visual="svg">'), 3)   # 4-node 'visual' ignored beside markers
        index = (self.tmp / '_preview/index.html').read_text()
        self.assertEqual(index.count('class="entry"'), len(self.real['articles']))  # replaced, not added


if __name__ == '__main__':
    unittest.main()
