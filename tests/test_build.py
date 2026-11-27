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
        self.data['articles']=[a for a in self.data['articles'] if not build.is_draft(a)]  # staged drafts are not public

    def test_calendar_expiry_and_edit(self):
        self.assertEqual(str(build.plus_months('2027-11-30',3)),'2028-02-29')
        news=copy.deepcopy(next(a for a in self.data['articles'] if a['type']=='guide'))
        news.update(type='news')
        news['edited']='2027-02-24'
        self.assertEqual(build.lifecycle(news,date(2027,2,24))['status'],'Actualité en cours')
        self.assertEqual(build.lifecycle(news,date(2027,2,25))['status'],'Actualité ancienne')

    def test_publication_and_visual_gates(self):
        data=copy.deepcopy(self.data)
        data['articles'][0]['approval']='draft'
        with self.assertRaises(ValueError):
            build.validate(data)
        # a sections-only article (no article.md, so no figN.svg markers) still needs its single 'visual' entry
        no_markers={'slug':'no-markers-fixture','title':'T','section':'Inference','type':'guide','summary':'S',
                    'approval':'approved-publication','formats':['Article'],'history':[],
                    'sections':[{'title':'T','paragraphs':['P']}],'visual':{}}
        with self.assertRaises(ValueError):
            build.validate({'articles':[no_markers]})

    def test_review_due_does_not_mean_wrong(self):
        guide=next(a for a in self.data['articles'] if a['type']=='guide')
        self.assertEqual(build.lifecycle(guide,date(2027,5,25))['status'],'À relire')

    def test_all_generated_pages_have_visuals_and_valid_local_links(self):
        pages=list(build.OUT.rglob('*.html'))
        self.assertGreaterEqual(len(pages),5)
        for page in pages:
            parser=Links()
            parser.feed(page.read_text())
            if page.relative_to(build.OUT).as_posix()!='nouvelles/index.html':  # news page: chart removed at the user's request
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
        self.assertEqual(page.count('<a class="side-section'),2+len({a['section'] for a in self.data['articles']}))
        self.assertIn('id="archive"',page)
        self.assertIn('data-outdated="false"',page)
        for private in ['Agent Commander','Huawei']:
            self.assertNotIn(private,page)


class NavNewChecks(unittest.TestCase):
    TODAY=date(2026,11,27)

    def art(self,slug,pub,edited=None,title=None,section='Agents'):
        return {'slug':slug,'title':title or slug,'section':section,'type':'guide','approval':'approved-publication','published':pub,'edited':edited or pub}

    def test_badge_window_13_vs_15_days(self):
        self.assertTrue(build.is_new(self.art('a','2026-11-14'),self.TODAY))   # 13 days
        self.assertTrue(build.is_new(self.art('a','2026-11-27'),self.TODAY))   # today
        self.assertFalse(build.is_new(self.art('a','2026-11-12'),self.TODAY))  # 15 days
        self.assertFalse(build.is_new(self.art('a','2026-11-30'),self.TODAY))  # future
        old=self.art('a','2026-10-01','2026-11-26')
        self.assertFalse(build.is_new(old,self.TODAY))                         # editing never makes a note new
        self.assertIn('badge-new',build.new_badge(self.art('a','2026-11-14'),self.TODAY))
        self.assertEqual(build.new_badge(self.art('a','2026-11-12'),self.TODAY),'')

    def test_ordering_published_edited_title(self):
        arts=[self.art('s1','2026-11-01','2026-11-02',title='Zeta'),self.art('s2','2026-11-01','2026-11-02',title='Alpha'),
              self.art('s3','2026-11-01','2026-11-05',title='Mid'),self.art('s4','2026-11-10',title='Newest')]
        self.assertEqual([a['slug'] for a in build.newest_first(arts)],['s4','s3','s2','s1'])

    def test_latest_block_is_exactly_ten_newest(self):
        arts=[self.art(f'n{i:02d}',f'2026-11-{i:02d}') for i in range(1,16)]
        html=build.latest_list(arts,self.TODAY)
        self.assertEqual(html.count('<li>'),10)
        slugs=[x.split('/')[0] for x in html.split('href="{p}')[1:]]
        self.assertEqual(slugs,[f'n{i:02d}' for i in range(15,5,-1)])
        self.assertEqual(build.latest_list(arts[:3],self.TODAY).count('<li>'),3)
        self.assertEqual(build.latest_list([],self.TODAY),'')

    def test_built_site_latest_page_and_sidebar(self):
        build.build(self.TODAY)
        home=(build.OUT/'index.html').read_text()
        page=(build.OUT/'derniers/index.html').read_text()
        n=len(json.loads((build.ROOT/'content/catalogue.json').read_text())['articles'])
        self.assertEqual(page.count('<li><span class="kind'),min(10,n))
        self.assertEqual(home.split('id="derniers"')[1].split('</section>')[0].count('<li><span class="kind'),min(10,n))
        self.assertLess(home.index('id="derniers"'),home.index('class="featured'))
        self.assertLess(home.index('id="derniers"'),home.index('id="section-cards"'))
        a_section=next((build.OUT/'sections').glob('*/index.html'))
        a_article=next(p for p in build.OUT.glob('*/index.html') if p.parent.name not in ('sections','derniers','archive','maintenance','glossaire','nouvelles'))
        for p in (build.OUT/'index.html',a_section,a_article,build.OUT/'derniers/index.html'):
            self.assertIn('class="side-section side-latest"',p.read_text(),p)


if __name__=='__main__':
    unittest.main()
