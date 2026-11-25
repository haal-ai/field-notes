import copy
import json
import unittest
from datetime import date
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit
import build


class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links=[]
        self.visual=False

    def handle_starttag(self, tag, attrs):
        attrs=dict(attrs)
        if tag=='figure' and attrs.get('data-learning-visual'):
            self.visual=True
        for field in ['src','href']:
            if field in attrs:
                self.links.append(attrs[field])


class PublicationChecks(unittest.TestCase):
    def setUp(self):
        self.data=json.loads((build.ROOT/'content/catalogue.json').read_text())

    def test_calendar_expiry_and_edit(self):
        self.assertEqual(str(build.plus_months('2027-11-30',3)),'2028-02-29')
        news=copy.deepcopy(next(a for a in self.data['articles'] if a['type']=='guide'))
        news.update(type='news')
        news['edited']='2027-02-24'
        self.assertEqual(build.lifecycle(news,date(2027,2,24))['status'],'Current news')
        self.assertEqual(build.lifecycle(news,date(2027,2,25))['status'],'Outdated news')

    def test_publication_and_visual_gates(self):
        for field,value in [('approval','draft'),('visual',{})]:
            data=copy.deepcopy(self.data)
            data['articles'][0][field]=value
            with self.assertRaises(ValueError):
                build.validate(data)

    def test_review_due_does_not_mean_wrong(self):
        guide=next(a for a in self.data['articles'] if a['type']=='guide')
        self.assertEqual(build.lifecycle(guide,date(2027,5,25))['status'],'Due for a check')

    def test_all_generated_pages_have_visuals_and_valid_local_links(self):
        pages=list(build.OUT.rglob('*.html'))
        self.assertGreaterEqual(len(pages),5)
        for page in pages:
            parser=Links()
            parser.feed(page.read_text())
            self.assertTrue(parser.visual,page)
            for value in parser.links:
                url=urlsplit(value)
                if url.scheme or value.startswith('#'):
                    continue
                target=(page.parent/url.path).resolve()
                self.assertTrue(target.is_relative_to(build.OUT.resolve()),value)
                self.assertTrue(target.exists(),f'{page}: {value}')

    def test_catalogue_has_filters_featured_and_real_counts(self):
        page=(build.OUT/'index.html').read_text()
        n=len(self.data['articles'])
        self.assertEqual(page.count('class="entry"'),n)
        self.assertIn('class="featured',page)
        self.assertEqual(page.count('class="type-button'),3)
        self.assertNotIn('data-kind="news" aria-pressed',page)  # no news yet: the filter is hidden
        self.assertEqual(page.count('<a class="side-section'),1+len({a['section'] for a in self.data['articles']}))
        self.assertIn('id="archive"',page)
        self.assertIn('data-outdated="false"',page)
        for private in ['Agent Commander','Huawei']:
            self.assertNotIn(private,page)


if __name__=='__main__':
    unittest.main()
