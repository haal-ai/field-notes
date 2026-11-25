"""Build the public catalogue, static articles, and review ledger. Standard library only."""
import argparse
import calendar
import html
import json
import re
import shutil
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUT = ROOT / '_site'


def esc(value):
    return html.escape(str(value), quote=True)


def plus_months(value, months):
    d = date.fromisoformat(value)
    month = d.year * 12 + d.month - 1 + months
    year, month = divmod(month, 12)
    return date(year, month + 1, min(d.day, calendar.monthrange(year, month + 1)[1]))


def day(value):
    d = date.fromisoformat(str(value))
    return f'{d.day} {d.strftime("%b %Y")}'


def when(value):
    return f'<time datetime="{esc(value)}">{day(value)}</time>'


def lifecycle(article, today):
    kind = article['type']
    if kind == 'news':
        due = plus_months(article['published'], 3)
        return {'status': 'Outdated news' if today >= due else 'Current news',
                'class': 'archived' if today >= due else 'current', 'due': due.isoformat(),
                'action': 'Check for a replacement report' if today >= due else 'Archive news at expiry'}
    if kind == 'guide':
        due = plus_months(article['reviewed'], article['review_months'])
        return {'status': 'Review due' if today >= due else 'Within review period',
                'class': 'due' if today >= due else 'current', 'due': due.isoformat(),
                'action': 'Technical review'}
    return {'status': 'Dated experiment', 'class': 'record', 'due': article['review_due'],
            'action': 'Check relevance; preserve the original measurement'}


def validate(catalogue):
    slugs = set()
    for article in catalogue['articles']:
        for key in ['slug', 'title', 'section', 'type', 'summary', 'author', 'perspective',
                    'published', 'edited', 'approval', 'formats', 'visual', 'sections', 'history']:
            if not article.get(key):
                raise ValueError(f'Missing {key}: {article.get("slug", "unknown article")}')
        slug = article['slug']
        if not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', slug) or slug in slugs:
            raise ValueError('Invalid or duplicate slug')
        slugs.add(slug)
        if article['approval'] not in ['approved-publication-test', 'approved-publication']:
            raise ValueError(f'Publication approval missing: {slug}')
        if article['perspective'] not in ['HAAL publication', 'Individual perspective']:
            raise ValueError('Explicit publication perspective required')
        if article['type'] not in ['guide', 'news', 'experiment']:
            raise ValueError('Unknown content type')
        pub, edited = date.fromisoformat(article['published']), date.fromisoformat(article['edited'])
        if edited < pub:
            raise ValueError('Edit date precedes publication')
        v = article['visual']
        if v.get('kind') != 'flow' or len(v.get('nodes', [])) != 3 or len(v.get('details', [])) != 3:
            raise ValueError('An explanatory three-step visual is required for this renderer')
        if not v.get('caption') or not v.get('title'):
            raise ValueError('A useful visual caption and accessible title are required')
        if article['type'] == 'guide':
            reviewed = date.fromisoformat(article['reviewed'])
            if reviewed < pub or reviewed > edited or article['review_months'] not in [3, 6]:
                raise ValueError('Invalid guide review metadata')
        if article['type'] == 'experiment':
            for key in ['tested', 'versions', 'method', 'limitations', 'review_due']:
                if not article.get(key):
                    raise ValueError(f'Experiment requires {key}')
            date.fromisoformat(article['tested'])
            date.fromisoformat(article['review_due'])
    # The public repository is a selected public dataset, never an export of the private inventory.
    payload = json.dumps(catalogue).lower()
    for token in ['teams.microsoft.com', 'sharepoint.com', '/users/', 'file://']:
        if token in payload:
            raise ValueError(f'Private/local source reference in public catalogue: {token}')


def flow(title, nodes, details, caption):
    nodes_svg = []
    for i, (node, detail) in enumerate(zip(nodes, details)):
        y = 37 + i * 85
        nodes_svg.append(f'<rect x="35" y="{y}" width="490" height="58" rx="4" class="flow-box"/>'
                         f'<text x="280" y="{y+24}" text-anchor="middle" class="flow-label">{esc(node)}</text>'
                         f'<text x="280" y="{y+44}" text-anchor="middle" class="flow-detail">{esc(detail)}</text>')
        if i < 2:
            nodes_svg.append(f'<path d="M280 {y+58}v27" class="flow-line"/>')
    return (f'<figure data-learning-visual="flow"><svg role="img" aria-label="{esc(title)}" viewBox="0 0 560 300">'
            f'<title>{esc(title)}</title>'+''.join(nodes_svg)+f'</svg><figcaption>{esc(caption)}</figcaption></figure>')


def shell(title, content, prefix='', description='AI and software engineering explanations, with dates, evidence, and useful visuals.', sidebar=''):
    main_open, main_close = (f'<div class="site-layout">{sidebar}', '</div>') if sidebar else ('', '')
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="color-scheme" content="dark light"><meta name="description" content="{esc(description)}"><title>{esc(title)} — HAAL</title>
<link rel="stylesheet" href="{prefix}assets/styles.css"><link rel="stylesheet" href="{prefix}assets/publication.css"><script defer src="{prefix}assets/site.js"></script><noscript><style>.js-only{{display:none!important}}</style></noscript></head>
<body><a class="skip-link" href="#main">Skip to content</a><header class="site-header"><a class="brand" href="{prefix}index.html"><span class="brand-mark" aria-hidden="true">h/</span><strong>HAAL<span class="brand-sub">ENGINEERING FIELD NOTES</span></strong></a><nav class="header-nav" aria-label="Main navigation"><a href="{prefix}index.html">Catalogue</a><a href="{prefix}archive/index.html">Archive</a><a href="{prefix}maintenance/index.html">Review ledger</a></nav><button id="theme" type="button" class="theme-control">Theme: system</button></header>{main_open}<main id="main" class="publication-main">{content}<footer><a href="{prefix}index.html" class="footer-brand">HAAL / FIELD NOTES</a><span>Publication-process trial · two test pages</span><a href="{prefix}how-these-notes-age/index.html">Dates and content lifetime</a></footer></main>{main_close}</body></html>'''


def slugify(text):
    return re.sub(r'[^a-z0-9]+', '-', text.lower()).strip('-')


def entry(article, today, prefix=''):
    status = lifecycle(article, today)
    return f'''<article class="entry" data-kind="{esc(article['type'])}" data-topic="{esc(slugify(article['section']))}" data-outdated="{'true' if status['status']=='Outdated news' else 'false'}"><div class="entry-kind"><span class="kind kind-{esc(article['type'])}">{esc(article['type'].upper())}</span></div><div><a class="entry-title" href="{prefix}{article['slug']}/index.html">{esc(article['title'])}</a><p class="entry-description">{esc(article['summary'])}</p><div class="entry-formats">{esc(article['section'])} / {esc(' · '.join(article['formats']))}</div></div><div class="entry-date">Published<strong>{when(article['published'])}</strong><span class="status status-{status['class']}">{status['status']}</span></div></article>'''


def write(path, content):
    dest = OUT / path
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(content)


def build(today=None):
    today = today or date.today()
    catalogue = json.loads((ROOT / 'content/catalogue.json').read_text())
    validate(catalogue)
    # Delete only stale files in our dedicated generated output directory.
    if OUT.exists():
        for stale in sorted(OUT.rglob('*'), key=lambda p: len(p.parts), reverse=True):
            if stale.is_file() or stale.is_symlink():
                stale.unlink()
            elif stale.is_dir():
                stale.rmdir()
    OUT.mkdir(exist_ok=True)
    shutil.copytree(ROOT / 'assets', OUT / 'assets', dirs_exist_ok=True)
    articles = sorted(catalogue['articles'], key=lambda a: (a['published'], a['slug']), reverse=True)
    entries = [a for a in articles if lifecycle(a, today)['status'] != 'Outdated news']
    summary_visual = flow('Choose a reading path', ['News', 'Guides', 'Experiments'],
                          ['Dated observations · three months', 'Longer-lived explanations · review dates', 'Recorded tests · versions and limits'],
                          'Choose news for a dated update, a guide for an explanation, or an experiment for evidence from a specific setup.')
    listing = sorted(articles, key=lambda a: a['published'], reverse=True)
    topics = {}
    for a in articles:
        topics.setdefault(a['section'], []).append(a)
    featured = next((a for a in articles if a['type'] == 'guide'), articles[0])
    fs = lifecycle(featured, today)
    fv = featured['visual']
    sidebar = (f'<aside class="sidebar" aria-label="Library filters"><div class="side-label">EXPLORE THE LIBRARY</div>'
               f'<div class="js-only"><button type="button" class="topic-button active" data-topic="all" aria-pressed="true">All topics<span>{len(entries):02d}</span></button><div id="topics">'
               + ''.join(f'<button type="button" class="topic-button" data-topic="{esc(slugify(t))}" aria-pressed="false">{esc(t)}<span>{len(v):02d}</span></button>' for t, v in topics.items())
               + '</div></div><noscript><p class="format-note">Topic filters need JavaScript. All entries are listed.</p></noscript>'
               '<div class="side-divider"></div><div class="side-label">READING FORMATS</div>'
               + ''.join(f'<div class="format-note">{esc(f)}</div>' for f in sorted({f for a in articles for f in a['formats']}))
               + '<a href="maintenance/index.html" class="sidebar-note">A date on every page.<br>A clear limit on every claim.</a></aside>')
    home = f'''<section id="library"><div class="eyebrow">OPEN SOURCE · OPEN WEIGHTS · PRACTICAL ENGINEERING</div><div class="intro-row"><div><h1>Understand it.<br><span>Try it. Document it.</span></h1><p class="intro">AI and software engineering, with useful visuals.<br>Publication-process trial: these pages test the website.</p></div><div class="index-stamp"><span>THE WORKING INDEX</span><strong>{len(articles):02d}</strong><span>{esc(catalogue['release_marker'])}</span></div></div>
<div class="library-topline"><div><span class="section-number">01 /</span> <h2>Start with an explanation</h2></div><span class="mono muted">TEXT FIRST. VISUAL WHEN USEFUL.</span></div>
<a class="featured" href="{featured['slug']}/index.html"><div class="featured-copy"><div class="entry-kicker"><span class="kind kind-{esc(featured['type'])}">{esc(featured['type'].upper())}</span><span>{esc(featured['section'].upper())}</span></div><h3>{esc(featured['title'])}</h3><p>{esc(featured['summary'])}</p><div class="featured-footer"><span>Read the explanation</span><span class="mono">ARTICLE + VISUAL</span></div><div class="featured-dates">Published {when(featured['published'])} · Edited {when(featured['edited'])} <span class="status status-{fs['class']}">{fs['status']}</span></div></div><div class="featured-visual">{flow(fv['title'], fv['nodes'], fv['details'], fv['caption'])}</div></a>
<section class="browse" aria-labelledby="browse-title"><div class="library-topline"><div><span class="section-number">02 /</span> <h2 id="browse-title">Browse the field notes</h2></div><span id="result-count" class="mono muted" aria-live="polite">{len(listing)} entries</span></div>
<div class="search-row"><label class="search-box js-only"><span class="sr-only">Search titles and descriptions</span><input id="search" type="search" placeholder="Find an explanation, experiment, or subject…" autocomplete="off"></label><label class="archive-control js-only"><input id="archive" type="checkbox"> Include outdated news</label></div>
<div class="filter-row js-only" role="group" aria-label="Content type"><button type="button" class="type-button active" data-kind="all" aria-pressed="true">All entries</button><button type="button" class="type-button" data-kind="guide" aria-pressed="false">Guides</button><button type="button" class="type-button" data-kind="experiment" aria-pressed="false">Experiments</button><button type="button" class="type-button" data-kind="news" aria-pressed="false">News &amp; magazine</button></div>
<div id="entries" class="entries">{''.join(entry(a,today) for a in listing)}</div><div id="empty" class="empty" hidden>No matching entries. Try another topic or clear the search.</div><p><a href="archive/index.html">Open the news archive</a></p></section>
<section id="principles" class="principles"><div class="library-topline"><div><span class="section-number">03 /</span> <h2>Useful today. Honest about time.</h2></div></div><div class="principle-grid"><div><span class="kind kind-news">NEWS</span><h3>A three-month window</h3><p>A dated observation. After three calendar months, it moves to the archive and shows an outdated notice. Editing it does not restart the clock.</p></div><div><span class="kind kind-guide">GUIDE</span><h3>Knowledge worth revisiting</h3><p>A longer-lived explanation. It shows its last technical review and next review date. A missed review means Review due, not No longer valid.</p></div><div><span class="kind kind-experiment">EXPERIMENT</span><h3>Results from a known setup</h3><p>The test date, versions, method, and limits stay with the result. An old measurement remains historical evidence; it does not describe a newer release.</p></div></div></section>
<section id="about" class="about"><div><span class="side-label">ABOUT THIS LIBRARY</span><h2>Practical work,<br>with its context attached.</h2></div><div><p>HAAL publications share explanations and experiments about AI and software engineering. Each article identifies its author, scope, sources, and limits. Personal views are labelled separately.</p><p class="muted">No account required. No engagement counters. This trial contains no imported private research.</p></div></section></section>'''
    write('index.html', shell('Catalogue', home, sidebar=sidebar))
    ledger = []
    for a in articles:
        status = lifecycle(a, today)
        visual = flow(a['visual']['title'], a['visual']['nodes'], a['visual']['details'], a['visual']['caption'])
        review_meta = f'<div>Last technical review<strong>{when(a["reviewed"])}</strong></div>' if a['type']=='guide' else ''
        metadata = f'''<div class="article-metadata"><div>Author / perspective<strong>{esc(a['author'])} · {esc(a['perspective'])}</strong></div><div>First published<strong>{when(a['published'])}</strong></div><div>Last edited<strong>{when(a['edited'])}</strong></div>{review_meta}<div>{'News expires' if a['type']=='news' else 'Next review'}<strong>{when(status['due'])}</strong></div></div>'''
        paragraphs = ''.join('<section><h2>'+esc(s['title'])+'</h2>'+''.join('<p>'+esc(p)+'</p>' for p in s['paragraphs'])+'</section>' for s in a['sections'])
        notice = {'news':'A dated report. It moves to the archive after three calendar months.', 'guide':'A missed review date means Review due. It does not establish that the content is wrong.', 'experiment':'These results apply to the recorded setup. Check the versions and test date.'}[a['type']]
        history = '<details><summary>Revision history</summary><ul>'+''.join('<li>'+day(r['date'])+' — '+esc(r['note'])+'</li>' for r in a['history'])+'</ul></details>'
        body = f'''<article class="public-article"><a href="../index.html">Catalogue</a><div class="entry-kicker"><span class="kind kind-{a['type']}">{a['type'].upper()}</span><span>{esc(a['section'])}</span></div><h1>{esc(a['title'])}</h1><p class="article-deck">{esc(a['summary'])}</p>{metadata}<div class="article-notice"><span class="status status-{status['class']}">{status['status']}</span><p>{notice}</p></div>{visual}<div class="reader-body">{paragraphs}{history}</div></article>'''
        write(a['slug']+'/index.html', shell(a['title'], body, '../', a['summary']))
        ledger.append({'slug':a['slug'],'title':a['title'],'content_type':a['type'],'perspective':a['perspective'],
                       'published':a['published'],'last_reviewed':a.get('reviewed'),'tested':a.get('tested'),
                       'action':status['action'],'due':status['due'],'status':status['status'],
                       'owner':'HAAL Publisher','path':'../'+a['slug']+'/index.html'})
    review_visual = flow('Review decisions', ['Check the due date', 'Inspect content and sources', 'Record the result'],
                         ['A timer identifies work', 'A person or assisted review checks accuracy', 'Keep dates and revision evidence'],
                         'The daily build refreshes date labels. It does not perform a technical review or approve new content.')
    rows=''.join(f'<li><a href="{esc(r["path"])}">{esc(r["title"])}</a><p>{esc(r["action"])} · Due {when(r["due"])} · {esc(r["status"])}</p></li>' for r in sorted(ledger,key=lambda r:r['due']))
    ledger_page = f'<div class="eyebrow">PUBLICATION MAINTENANCE</div><h1>What needs review,<br><span>and when.</span></h1><p class="intro">Computed on {day(today)} (UTC in the scheduled build). Dates come from the publication catalogue.</p>{review_visual}<h2>Review queue</h2><ol class="review-queue">{rows}</ol><p><a href="ledger.json">Download the maintenance ledger (JSON)</a></p>'
    write('maintenance/index.html',shell('Review ledger',ledger_page,'../'))
    write('maintenance/ledger.json',json.dumps({'computed_on':today.isoformat(),'items':ledger},indent=2)+'\n')
    archive=[a for a in articles if lifecycle(a,today)['status']=='Outdated news']
    archive_visual=flow('The news archive',['Original report','Three-month boundary','Historical reference'],['First publication stays fixed','News becomes outdated','Read with its original context'],'Archiving changes how news is presented. It preserves the original report and publication date.')
    archive_body='<h1>News archive</h1><p class="intro">Dated reports remain accessible after their current-news window ends.</p>'+archive_visual
    archive_body+=''.join(entry(a,today,'../') for a in archive) if archive else '<h2>Archive policy</h2><p>The publication trial has not yet reached its three-month boundary. The first news entry expires on '+day(plus_months('2026-11-25',3))+'.</p>'
    write('archive/index.html',shell('News archive',archive_body,'../'))
    write('catalogue.json',json.dumps({'as_of':today.isoformat(),'release_marker':catalogue['release_marker'],'articles':[{k:a[k] for k in ['slug','title','section','type','published','summary','formats','perspective']} for a in articles]},indent=2)+'\n')
    write('404.html',shell('Page not found','<h1>This page is not in the catalogue.</h1>'+summary_visual+'<p><a href="./index.html">Open the catalogue</a></p>'))
    write('.nojekyll','')
    print(json.dumps({'articles':len(articles),'generated_pages':len(list(OUT.rglob('*.html'))),'as_of':today.isoformat(),'release':catalogue['release_marker']}))


if __name__ == '__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--as-of',type=date.fromisoformat)
    build(parser.parse_args().as_of)
