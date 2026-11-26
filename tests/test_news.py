import copy
import json
import shutil
import sys
import tempfile
import unittest
from datetime import date
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import build
import merge_news
import news


def rec(id_='a1b2c3d4e5f6a1b2', date_='2026-11-20', vendor='Acme', theme='Modèles',
        title='Titre', text='Texte', urls='__default__'):
    return {'id': id_, 'date': date_, 'vendor': vendor, 'theme': theme, 'title_fr': title,
            'text_fr': text, 'urls': ['https://example.test/a'] if urls == '__default__' else urls}


class SchemaAndPrivacyChecks(unittest.TestCase):
    def test_valid_record_has_no_problems(self):
        self.assertEqual(merge_news.check_all([rec()]), [])

    def test_missing_field_is_refused(self):
        bad = rec()
        del bad['vendor']
        self.assertTrue(merge_news.check_all([bad]))

    def test_record_with_no_url_is_refused(self):
        bad = rec(urls=[])
        self.assertTrue(merge_news.check_all([bad]))

    def test_non_https_url_is_refused(self):
        bad = rec(urls=['http://example.test/a'])
        self.assertTrue(any('https' in p for p in merge_news.check_all([bad])))

    def test_private_host_is_refused(self):
        for host in ('https://teams.microsoft.com/x', 'https://sharepoint.com/x', 'https://localhost/x', 'https://127.0.0.1/x'):
            with self.subTest(host=host):
                self.assertTrue(merge_news.check_all([rec(urls=[host])]))

    def test_forbidden_name_in_text_is_refused(self):
        bad = rec(text='Un lien interne /Users/quelquun/dossier')
        self.assertTrue(merge_news.check_all([bad]))

    def test_duplicate_id_in_same_file_is_refused(self):
        problems = merge_news.check_all([rec(), rec()])
        self.assertTrue(any('duplicate' in p for p in problems))

    def test_bad_date_format_is_refused(self):
        bad = rec(date_='20-11-2026')
        self.assertTrue(any('date' in p for p in merge_news.check_all([bad])))


class MergeLogic(unittest.TestCase):
    def test_new_id_is_appended(self):
        existing = [rec(id_='a1b2c3d4e5f6a1b2', date_='2026-11-20')]
        incoming = [rec(id_='1111222233334444', date_='2026-11-25')]
        merged = merge_news.merge(existing, incoming)
        self.assertEqual({r['id'] for r in merged}, {'a1b2c3d4e5f6a1b2', '1111222233334444'})

    def test_merged_list_is_newest_first(self):
        existing = [rec(id_='a1b2c3d4e5f6a1b2', date_='2026-11-10')]
        incoming = [rec(id_='1111222233334444', date_='2026-11-25')]
        merged = merge_news.merge(existing, incoming)
        self.assertEqual([r['id'] for r in merged], ['1111222233334444', 'a1b2c3d4e5f6a1b2'])

    def test_same_id_adds_urls_without_touching_title_or_text(self):
        existing = [rec(id_='a1b2c3d4e5f6a1b2', title='Titre original', text='Texte original', urls=['https://example.test/a'])]
        incoming = [rec(id_='a1b2c3d4e5f6a1b2', title='Titre modifié par erreur', text='Texte modifié par erreur',
                        urls=['https://example.test/a', 'https://example.test/b'])]
        merged = merge_news.merge(existing, incoming)
        self.assertEqual(len(merged), 1)
        self.assertEqual(merged[0]['title_fr'], 'Titre original')
        self.assertEqual(merged[0]['text_fr'], 'Texte original')
        self.assertEqual(merged[0]['urls'], ['https://example.test/a', 'https://example.test/b'])

    def test_same_id_does_not_duplicate_an_existing_url(self):
        existing = [rec(urls=['https://example.test/a'])]
        incoming = [rec(urls=['https://example.test/a'])]
        merged = merge_news.merge(existing, incoming)
        self.assertEqual(merged[0]['urls'], ['https://example.test/a'])

    def test_main_refuses_a_bad_incoming_file_without_touching_news_json(self):
        tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, tmp)
        news_path = tmp / 'news.json'
        news_path.write_text(json.dumps([rec()]))
        bad_path = tmp / 'incoming.json'
        bad = rec(id_='1111222233334444')
        del bad['vendor']
        bad_path.write_text(json.dumps([bad]))
        before = news_path.read_text()
        with mock.patch.object(sys, 'argv', ['merge_news.py', str(bad_path), str(news_path)]):
            rc = merge_news.main()
        self.assertEqual(rc, 1)
        self.assertEqual(news_path.read_text(), before)

    def test_main_merges_a_good_incoming_file(self):
        tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, tmp)
        news_path = tmp / 'news.json'
        news_path.write_text(json.dumps([rec(id_='a1b2c3d4e5f6a1b2', date_='2026-11-10')]))
        incoming_path = tmp / 'incoming.json'
        incoming_path.write_text(json.dumps([rec(id_='1111222233334444', date_='2026-11-25')]))
        with mock.patch.object(sys, 'argv', ['merge_news.py', str(incoming_path), str(news_path)]):
            rc = merge_news.main()
        self.assertEqual(rc, 0)
        merged = json.loads(news_path.read_text())
        self.assertEqual(len(merged), 2)
        self.assertEqual(merged[0]['id'], '1111222233334444')  # newest first


class StableIdAndPrepMateMatching(unittest.TestCase):
    def test_normalize_url_strips_scheme_www_and_trailing_slash(self):
        self.assertEqual(merge_news.normalize_url('https://www.example.test/a/b/'), 'example.test/a/b')
        self.assertEqual(merge_news.normalize_url('https://example.test/a/b'), 'example.test/a/b')

    def test_stable_id_is_deterministic_and_url_based(self):
        a = merge_news.stable_id('https://example.test/releases/tag/v1.0', 'Title A')
        b = merge_news.stable_id('https://example.test/releases/tag/v1.0', 'Title B')
        self.assertEqual(a, b)  # specific article URL: title does not change the id

    def test_stable_id_uses_title_for_a_generic_changelog_root(self):
        a = merge_news.stable_id('https://example.test/changelog', 'Release A')
        b = merge_news.stable_id('https://example.test/changelog', 'Release B')
        self.assertNotEqual(a, b)  # same generic root, different announcements -> different ids

    def test_find_existing_matches_by_normalized_url_overlap(self):
        existing = [rec(id_='a1b2c3d4e5f6a1b2', urls=['https://example.test/a'])]
        hit = merge_news.find_existing(['https://www.example.test/a/'], existing)
        self.assertIsNotNone(hit)
        self.assertEqual(hit['id'], 'a1b2c3d4e5f6a1b2')

    def test_find_existing_returns_none_without_overlap(self):
        existing = [rec(id_='a1b2c3d4e5f6a1b2', urls=['https://example.test/a'])]
        self.assertIsNone(merge_news.find_existing(['https://example.test/b'], existing))

    def test_merge_prep_mate_matches_existing_and_adds_shared_on(self):
        existing_fr = [rec(id_='a1b2c3d4e5f6a1b2', urls=['https://example.test/a'])]
        export = {'news': [{'date': '2026-11-20', 'title': 'T', 'text': 'Txt', 'source_urls': ['https://example.test/a'],
                             'vendor': 'Acme', 'shared_on': ['2026-11-26'], 'status': 'shared'}]}
        updated, held_back, stats = merge_news.merge_prep_mate(export, existing_fr, translate=lambda i: ('x', 'y'))
        self.assertEqual(stats['matched_existing'], 1)
        self.assertEqual(stats['new_shared_translated'], 0)
        self.assertEqual(held_back, [])
        self.assertEqual(updated[0]['shared_on'], ['2026-11-20', '2026-11-26'])  # the record's own date is kept as its first known share, union'd with the new one
        self.assertEqual(updated[0]['title_fr'], 'Titre')  # untouched: the review's own wording stays

    def test_merge_prep_mate_translates_a_genuinely_new_shared_item(self):
        existing_fr = [rec(id_='a1b2c3d4e5f6a1b2', urls=['https://example.test/a'])]
        export = {'news': [{'date': '2026-11-26', 'title': 'New thing', 'text': 'A new announcement.',
                             'source_urls': ['https://example.test/new'], 'vendor': 'Acme',
                             'shared_on': ['2026-11-26'], 'status': 'shared'}]}
        calls = []

        def translate(item):
            calls.append(item)
            return ('Nouvelle chose', 'Une nouvelle annonce.')
        updated, held_back, stats = merge_news.merge_prep_mate(export, existing_fr, translate)
        self.assertEqual(stats['new_shared_translated'], 1)
        self.assertEqual(len(calls), 1)
        new_rec = next(r for r in updated if r['title_fr'] == 'Nouvelle chose')
        self.assertTrue(new_rec['translated_by_daily_rule'])
        self.assertEqual(new_rec['text_fr'], 'Une nouvelle annonce.')

    def test_merge_prep_mate_never_translates_a_prepared_item(self):
        existing_fr = []
        export = {'news': [{'date': '2026-11-26', 'title': 'No public link yet', 'text': 'T',
                             'source_urls': ['https://example.test/x'], 'vendor': 'Acme',
                             'shared_on': [], 'status': 'prepared'}]}

        def must_not_be_called(item):
            raise AssertionError('a prepared item must never be translated or published')
        updated, held_back, stats = merge_news.merge_prep_mate(export, existing_fr, must_not_be_called)
        self.assertEqual(stats['prepared_held_back'], 1)
        self.assertEqual(len(held_back), 1)
        self.assertEqual(updated, [])  # nothing published for a prepared-only export

    def test_merge_prep_mate_prepared_item_already_covered_counts_as_matched_not_held_back(self):
        existing_fr = [rec(id_='a1b2c3d4e5f6a1b2', urls=['https://example.test/covered'])]
        export = {'news': [{'date': '2026-11-20', 'title': 'T', 'text': 'Txt', 'source_urls': ['https://example.test/covered'],
                             'vendor': 'Acme', 'shared_on': ['2026-11-26'], 'status': 'prepared'}]}

        def must_not_be_called(item):
            raise AssertionError('already-covered item must never be translated')
        updated, held_back, stats = merge_news.merge_prep_mate(export, existing_fr, must_not_be_called)
        self.assertEqual(stats['matched_existing'], 1)
        self.assertEqual(stats['prepared_held_back'], 0)
        self.assertEqual(held_back, [])


class NewsHelpers(unittest.TestCase):
    def test_in_window_true_within_28_days(self):
        self.assertTrue(news.in_window(rec(date_='2026-11-01'), date(2026, 11, 26)))

    def test_in_window_false_past_28_days(self):
        self.assertFalse(news.in_window(rec(date_='2026-10-01'), date(2026, 11, 26)))

    def test_domain_strips_www(self):
        self.assertEqual(news.domain('https://www.example.test/a/b'), 'example.test')

    def test_by_day_groups_and_preserves_order(self):
        records = [rec(id_='a1b2c3d4e5f6a1b2', date_='2026-11-20'), rec(id_='1111222233334444', date_='2026-11-20'),
                    rec(id_='2222333344445555', date_='2026-11-19')]
        grouped = news.by_day(records)
        self.assertEqual(list(grouped.keys()), ['2026-11-20', '2026-11-19'])
        self.assertEqual(len(grouped['2026-11-20']), 2)

    def test_month_key_and_label(self):
        self.assertEqual(news.month_key('2026-11-20'), '2026-11')
        self.assertEqual(news.month_label('2026-11'), 'novembre 2026')


class NewsPageBuild(unittest.TestCase):
    """Builds the real site with a small synthetic news.json swapped in, restoring the real file after."""

    def setUp(self):
        self.real_path = build.ROOT / 'content/news/news.json'
        self.had_real = self.real_path.is_file()
        self.backup = self.real_path.read_text() if self.had_real else None
        self.gloss_path = build.ROOT / 'content/glossaire.md'
        self.had_gloss = self.gloss_path.is_file()
        self.gloss_backup = self.gloss_path.read_text() if self.had_gloss else None
        self.cat_path = build.ROOT / 'content/catalogue.json'
        self.cat_backup = self.cat_path.read_text()
        catalogue = json.loads(self.cat_backup)
        catalogue['articles'] = [a for a in catalogue['articles'] if not build.is_draft(a)]  # staged drafts are not public
        self.cat_path.write_text(json.dumps(catalogue, ensure_ascii=False))
        self.tmp_out = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp_out)
        self.addCleanup(self._restore)

    def _restore(self):
        self.cat_path.write_text(self.cat_backup)
        if self.had_real:
            self.real_path.write_text(self.backup)
        elif self.real_path.is_file():
            self.real_path.unlink()
        if self.had_gloss:
            self.gloss_path.write_text(self.gloss_backup)
        elif self.gloss_path.is_file():
            self.gloss_path.unlink()

    def write_news(self, records):
        self.real_path.parent.mkdir(parents=True, exist_ok=True)
        self.real_path.write_text(json.dumps(records, ensure_ascii=False))

    def build(self, as_of):
        patches = [mock.patch.object(build, 'OUT', self.tmp_out), mock.patch.object(build, 'PREVIEW_OUT', self.tmp_out)]
        for p in patches:
            p.start()
            self.addCleanup(p.stop)
        build.STATE['out'] = self.tmp_out
        if self.gloss_path.is_file():
            self.gloss_path.unlink()  # a tiny synthetic news fixture won't use any real key term; skip glossary coverage for these tests
        build.build(as_of)

    def test_news_page_lists_cards_newest_first_grouped_by_day(self):
        self.write_news([
            rec(id_='a1b2c3d4e5f6a1b2', date_='2026-11-20', title='Plus ancienne'),
            rec(id_='1111222233334444', date_='2026-11-25', title='Plus récente'),
        ])
        self.build(date(2026, 11, 26))
        page = (self.tmp_out / 'nouvelles/index.html').read_text()
        self.assertLess(page.index('Plus récente'), page.index('Plus ancienne'))
        self.assertIn('data-learning-visual', page)  # the weekly chart figure
        self.assertIn('news-notice', page)

    def test_record_with_no_public_url_breaks_the_public_build(self):
        bad = rec()
        bad['urls'] = []
        self.write_news([bad])
        with self.assertRaises(ValueError):
            self.build(date(2026, 11, 26))

    def test_items_past_four_weeks_move_to_the_month_archive(self):
        self.write_news([rec(id_='a1b2c3d4e5f6a1b2', date_='2026-10-01', title='Vieille nouvelle')])
        self.build(date(2026, 11, 26))
        page = (self.tmp_out / 'nouvelles/index.html').read_text()
        self.assertNotIn('Vieille nouvelle', page)
        archive = (self.tmp_out / 'nouvelles/archives/2026-10/index.html').read_text()
        self.assertIn('Vieille nouvelle', archive)
        self.assertIn('data-learning-visual', archive)

    def test_home_page_shows_five_newest_with_a_link_to_the_full_page(self):
        self.write_news([rec(id_=f'{i:016x}', date_='2026-11-20', title=f'Nouvelle {i}') for i in range(8)])
        self.build(date(2026, 11, 26))
        home = (self.tmp_out / 'index.html').read_text()
        self.assertIn('news-home', home)
        self.assertEqual(home.count('news-home-list'), 1)
        self.assertIn('href="nouvelles/index.html"', home)

    def test_nav_item_appears_only_when_news_exists(self):
        self.write_news([rec()])
        self.build(date(2026, 11, 26))
        home = (self.tmp_out / 'index.html').read_text()
        self.assertIn('nouvelles/index.html">Nouvelles<', home)


if __name__ == '__main__':
    unittest.main()
