"""Build the public catalogue, static articles, and review ledger. Standard library only."""
import argparse
import calendar
import html
import json
import re
import shutil
from datetime import date
import sys
from pathlib import Path

from render import esc, inline_svg, leftovers, markdown

ROOT = Path(__file__).resolve().parent
OUT = ROOT / '_site'                # public output: the only directory ever deployed
PREVIEW_OUT = ROOT / '_preview'     # private draft preview: never deployed, git-ignored
APPROVED = ['approved-publication-test', 'approved-publication']
PRIVATE_TOKENS = ['teams.microsoft.com', 'sharepoint.com', '/users/', 'file://']
ABOUT = 'About this library'
SECTION_NOTES = {
    'Inference': 'How models run: prompts, memory, serving.',
    'Evaluation': 'Small tests with their setup and limits.',
    ABOUT: 'How to read these notes.',
}
STATE = {'preview': False, 'out': OUT}


def plus_months(value, months):
    d = date.fromisoformat(value)
    month = d.year * 12 + d.month - 1 + months
    year, month = divmod(month, 12)
    return date(year, month + 1, min(d.day, calendar.monthrange(year, month + 1)[1]))


def day(value):
    try:
        d = date.fromisoformat(str(value))
    except ValueError:  # only drafts reach here; validate() rejects non-ISO dates in public builds
        return 'Set at publication'
    return f'{d.day} {d.strftime("%b %Y")}'


def when(value):
    if not iso(value):
        return '<span class="undated">Set at publication</span>'
    return f'<time datetime="{esc(value)}">{day(value)}</time>'


def iso(value):
    try:
        return isinstance(value, str) and bool(date.fromisoformat(value))
    except ValueError:
        return False


def is_draft(article):
    return article.get('status') == 'draft' or article.get('approval') not in APPROVED


def article_dir(article):
    return Path(article.get('_dir') or ROOT / 'content' / 'articles' / article['slug'])


def body_file(article):
    return next((p for p in (article_dir(article) / n for n in ('article.md', 'draft.md')) if p.is_file()), None)


def perspective_label(article):
    return 'Individual view' if article['perspective'] == 'Individual perspective' else article['perspective']


def lifecycle(article, today):
    kind = article['type']
    if is_draft(article):
        return {'status': 'Draft (not published)', 'class': 'draft', 'due': None,
                'action': 'Technical review, rights review and approval before publication'}
    if kind == 'news':
        due = plus_months(article['published'], 3)
        return {'status': 'Outdated news' if today >= due else 'Current news',
                'class': 'archived' if today >= due else 'current', 'due': due.isoformat(),
                'action': 'Check for a replacement report' if today >= due else 'Archive news at expiry'}
    if kind == 'guide':
        due = plus_months(article['reviewed'], article['review_months'])
        return {'status': 'Due for a check' if today >= due else f'Up to date · next check {due.strftime("%B %Y")}',
                'class': 'due' if today >= due else 'current', 'due': due.isoformat(),
                'action': 'Technical review'}
    tested = article.get('tested')
    return {'status': f'Experiment · tested {day(tested)}' if iso(tested) else 'Experiment', 'class': 'record', 'due': article['review_due'],
            'action': 'Check relevance; preserve the original measurement'}


def validate_visual(article, preview):
    slug, v = article['slug'], article['visual']
    if not v.get('caption') or not v.get('title'):
        raise ValueError('A useful visual caption and accessible title are required')
    if v.get('kind') == 'flow':
        if len(v.get('nodes', [])) != 3 or len(v.get('details', [])) != 3:
            raise ValueError('An explanatory three-step visual is required for this renderer')
    elif v.get('kind') == 'svg':
        for key in ('svg', 'alt'):
            if not re.fullmatch(r'[A-Za-z0-9_-]+\.(svg|md)', str(v.get(key, ''))):
                raise ValueError(f'Figure {key} must be a plain file name in the article folder: {slug}')
        if not (article_dir(article) / v['svg']).is_file():
            raise ValueError(f'Figure file missing: {slug}/{v["svg"]}')
        if not preview and not (article_dir(article) / v['alt']).is_file():
            raise ValueError(f'Text equivalent missing: {slug}/{v["alt"]}')
    else:
        raise ValueError('Unknown visual kind')
    if not preview and (leftovers(v['caption']) or leftovers(v['title'])):
        raise ValueError(f'Placeholder figure caption: {slug}')


def validate(catalogue, preview=False):
    """Public mode (default) refuses drafts. Preview mode accepts them for the private preview build."""
    slugs = set()
    for article in catalogue['articles']:
        for key in ['slug', 'title', 'section', 'type', 'summary', 'author', 'perspective',
                    'approval', 'formats', 'visual', 'history']:
            if not article.get(key):
                raise ValueError(f'Missing {key}: {article.get("slug", "unknown article")}')
        slug = article['slug']
        if not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', slug) or slug in slugs:
            raise ValueError('Invalid or duplicate slug')
        slugs.add(slug)
        draft = is_draft(article)
        if draft and not preview:
            raise ValueError(f'Draft or unapproved entry refused in a public build: {slug}')
        if article['perspective'] != 'HAAL publication' and not article['perspective'].startswith('Individual'):
            raise ValueError('Explicit publication perspective required')
        if article['type'] not in ['guide', 'news', 'experiment']:
            raise ValueError('Unknown content type')
        if not article.get('sections') and not body_file(article):
            raise ValueError(f'Missing sections or article.md: {slug}')
        validate_visual(article, preview)
        if draft:
            continue
        for key in ('published', 'edited'):
            if not iso(article.get(key)):
                raise ValueError(f'A real ISO {key} date is required for publication: {slug}')
        pub, edited = date.fromisoformat(article['published']), date.fromisoformat(article['edited'])
        if edited < pub:
            raise ValueError('Edit date precedes publication')
        if not all(iso(r.get('date')) for r in article['history']):
            raise ValueError(f'History dates must be ISO dates: {slug}')
        if article['type'] == 'guide':
            if not iso(article.get('reviewed')) or article['review_months'] not in [3, 6]:
                raise ValueError('Invalid guide review metadata')
            reviewed = date.fromisoformat(article['reviewed'])
            if reviewed < pub or reviewed > edited:
                raise ValueError('Invalid guide review metadata')
        if article['type'] == 'experiment':
            for key in ['tested', 'versions', 'method', 'limitations', 'review_due']:
                if not article.get(key):
                    raise ValueError(f'Experiment requires {key}')
            date.fromisoformat(article['tested'])
            date.fromisoformat(article['review_due'])
    for gone in catalogue.get('retired', []):
        if not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', gone.get('slug', '')) or gone['slug'] in slugs or not gone.get('note'):
            raise ValueError('Invalid retired page entry')
    # The public repository is a selected public dataset, never an export of the private inventory.
    payload = json.dumps([{k: v for k, v in a.items() if not k.startswith('_')} for a in catalogue['articles']]).lower()
    for token in PRIVATE_TOKENS:
        if token in payload:
            raise ValueError(f'Private/local source reference in public catalogue: {token}')


def figure(article, problems):
    """The page figure: the built-in three-step flow, or the article's own inline SVG with caption and text equivalent."""
    v = article['visual']
    if v['kind'] == 'flow':
        return flow(v['title'], v['nodes'], v['details'], v['caption'])
    folder = article_dir(article)
    svg = inline_svg((folder / v['svg']).read_text(), article['slug'])
    alt_file = folder / v['alt']
    if alt_file.is_file():
        alt, _ = markdown(alt_file.read_text(), warnings=problems)
        problems.extend(f'{v["alt"]}: {l}' for l in leftovers(alt_file.read_text()))
        problems.extend(f'{v["alt"]}: private reference {t}' for t in PRIVATE_TOKENS if t in alt_file.read_text().lower())
    else:
        problems.append(f'text equivalent {v["alt"]} not written yet')
        alt = '<p>The text equivalent of this figure is not written yet.</p>'
    problems.extend(f'private reference {t} in figure' for t in PRIVATE_TOKENS if t in svg.lower())
    caption = v['caption']
    if leftovers(caption):
        problems.append(f'figure caption is still a placeholder')
    return (f'<figure data-learning-visual="svg">{svg}<figcaption>{esc(caption)}</figcaption>'
            f'<details class="fig-text" style="margin-top:12px;padding:10px 14px"><summary>Text equivalent of this figure</summary>{alt}</details></figure>')


def prepare(articles, preview):
    """Render each article's figure and body. Public builds raise on any problem; preview collects them."""
    warnings = []
    for a in articles:
        problems = []
        if preview and a['visual']['kind'] == 'flow' and (article_dir(a) / 'visual.svg').is_file():
            a['visual'] = dict(a['visual'], kind='svg', svg='visual.svg', alt='alt.md')  # preview-only adapter
        a['_figure'] = figure(a, problems)
        a['_body'], a['_figure_in_body'] = None, False
        path = body_file(a)
        if path:
            text = path.read_text()
            problems.extend(f'{path.name}: unfinished text "{l}"' for l in leftovers(text))
            problems.extend(f'{path.name}: private reference {t}' for t in PRIVATE_TOKENS if t in text.lower())
            marker = a['visual'].get('svg')
            a['_body'], a['_figure_in_body'] = markdown(text, marker, a['_figure'], problems)
        if problems and not preview:
            raise ValueError(f'{a["slug"]}: ' + '; '.join(problems))
        warnings.extend(f'{a["slug"]}: {p}' for p in problems)
    return warnings


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
    preview = STATE['preview']
    extra_head = ('<meta name="robots" content="noindex,nofollow"><style>.status-draft{border:1px dashed var(--due);color:var(--due)}'
                  '.undated{color:var(--muted)}.preview-banner{background:var(--due-bg);color:var(--due);border-bottom:1px solid var(--due);'
                  'padding:10px 20px;font-size:.875rem;text-align:center}</style>') if preview else ''
    banner = ('<div class="preview-banner" role="note" data-preview="true">PRIVATE PREVIEW. Contains drafts that are not published or approved. Never deploy this build.</div>'
              if preview else '')
    title = f'[Preview] {title}' if preview else title
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="color-scheme" content="dark light">{extra_head}<meta name="description" content="{esc(description)}"><title>{esc(title)} — HAAL</title>
<link rel="stylesheet" href="{prefix}assets/styles.css"><link rel="stylesheet" href="{prefix}assets/publication.css"><script defer src="{prefix}assets/site.js"></script><noscript><style>.js-only{{display:none!important}}</style></noscript></head>
<body>{banner}<a class="skip-link" href="#main">Skip to content</a><header class="site-header"><a class="brand" href="{prefix}index.html"><span class="brand-mark" aria-hidden="true">h/</span><strong>HAAL<span class="brand-sub">ENGINEERING FIELD NOTES</span></strong></a><nav class="header-nav" aria-label="Main navigation"><a href="{prefix}index.html">Catalogue</a><a href="{prefix}archive/index.html">Archive</a><a href="{prefix}maintenance/index.html">Review ledger</a></nav><button id="theme" type="button" class="theme-control">Theme: system</button></header>{main_open}<main id="main" class="publication-main">{content}<footer><a href="{prefix}index.html" class="footer-brand">HAAL / FIELD NOTES</a><span>Practical AI and software engineering notes, with dates</span><a href="{prefix}how-these-notes-age/index.html">Dates and content lifetime</a></footer></main>{main_close}</body></html>'''


def slugify(text):
    return re.sub(r'[^a-z0-9]+', '-', text.lower()).strip('-')


def entry(article, today, prefix=''):
    status = lifecycle(article, today)
    return f'''<article class="entry" data-slug="{esc(article['slug'])}" data-kind="{esc(article['type'])}" data-topic="{esc(slugify(article['section']))}" data-outdated="{'true' if status['status']=='Outdated news' else 'false'}"><div class="entry-kind"><span class="kind kind-{esc(article['type'])}">{esc(article['type'].upper())}</span></div><div><a class="entry-title" href="{prefix}{article['slug']}/index.html">{esc(article['title'])}</a><p class="entry-description">{esc(article['summary'])}</p>{'<div class="entry-formats">Article with figure</div>' if any('visual' in f.lower() for f in article['formats']) else ''}</div><div class="entry-date">Published<strong>{when(article.get('published'))}</strong><span class="status status-{status['class']}">{status['status']}</span></div></article>'''


def sections_of(articles, today):
    """Group articles under their section heading: largest section first, 'About this library' last."""
    groups = {}
    for a in articles:
        groups.setdefault(a['section'], []).append(a)
    order = sorted(groups, key=lambda name: (name == ABOUT, -len(groups[name]), name))
    return [(name, groups[name], sum(lifecycle(a, today)['status'] != 'Outdated news' for a in groups[name])) for name in order]


def section_block(name, items, today):
    sid = 'section-' + slugify(name)
    return (f'<section class="entry-section" data-section="{esc(slugify(name))}" aria-labelledby="{sid}"><h3 id="{sid}" class="section-heading">{esc(name)}'
            f'<span class="section-count">{len(items):02d}</span></h3><p class="section-note">{esc(SECTION_NOTES.get(name) or f"Notes on {name.lower()}.")}</p>'
            f'{"".join(entry(a, today) for a in items)}</section>')


def write(path, content):
    dest = STATE['out'] / path
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(content)


def load_drafts(folders):
    """Read <folder>/<slug>/entry.json staging entries (preview only). Folder names must equal slugs."""
    found = []
    for folder in folders:
        for entry_file in sorted(Path(folder).glob('*/entry.json')):
            article = json.loads(entry_file.read_text())
            if article.get('slug') != entry_file.parent.name:
                raise ValueError(f'Folder name must equal slug: {entry_file.parent}')
            article['_dir'] = str(entry_file.parent)
            found.append(article)
    return found


def build(today=None, preview=False, drafts=()):
    """Public build -> _site (refuses drafts). Preview build -> _preview (accepts drafts, never deployed)."""
    if drafts and not preview:
        raise ValueError('Draft folders need preview mode')
    today = today or date.today()
    out = PREVIEW_OUT if preview else OUT
    STATE.update(preview=preview, out=out)
    catalogue = json.loads((ROOT / 'content/catalogue.json').read_text())
    catalogue['articles'] += load_drafts(drafts)
    validate(catalogue, preview)
    warnings = prepare(catalogue['articles'], preview)
    # Delete only stale files in our dedicated generated output directory.
    if out.exists():
        for stale in sorted(out.rglob('*'), key=lambda p: len(p.parts), reverse=True):
            if stale.is_file() or stale.is_symlink():
                stale.unlink()
            elif stale.is_dir():
                stale.rmdir()
    out.mkdir(exist_ok=True)
    shutil.copytree(ROOT / 'assets', out / 'assets', dirs_exist_ok=True)
    pub_key = lambda a: (a.get('published') if iso(a.get('published')) else '0000', a['slug'])
    articles = sorted(catalogue['articles'], key=pub_key, reverse=True)
    entries = [a for a in articles if lifecycle(a, today)['status'] != 'Outdated news']
    summary_visual = flow('Choose a reading path', ['News', 'Guides', 'Experiments'],
                          ['Dated observations · three months', 'Longer-lived explanations · review dates', 'Recorded tests · versions and limits'],
                          'Choose news for a dated update, a guide for an explanation, or an experiment for evidence from a specific setup.')
    listing = sorted(articles, key=lambda a: a.get('published') if iso(a.get('published')) else '0000', reverse=True)
    groups = sections_of(listing, today)
    candidates = [a for a in articles if not is_draft(a)] or articles
    # Feature a content article, never the library's own "about" page; the catalogue may name one.
    named = catalogue.get('featured')
    featured = next((a for a in candidates if a['slug'] == named), None) or next(
        (a for a in candidates if a['section'] != ABOUT and a['type'] == 'guide'), candidates[0])
    fs = lifecycle(featured, today)
    fv = featured['visual']
    # Only the built-in three-step flow fits the card; tall article figures stay on the article page.
    featured_visual = flow(fv['title'], fv['nodes'], fv['details'], fv['caption']) if fv.get('nodes') else ''
    published = [a for a in articles if not is_draft(a)]
    stats = (f'<div class="library-stats"><strong>{len(published)} {"note" if len(published) == 1 else "notes"}</strong>'
             f'<span>Last updated {day(max(a["edited"] for a in published))}</span></div>') if published else ''
    side_groups = ''.join(
        f'<li class="side-group" data-section="{esc(slugify(t))}"><a class="side-section" href="#section-{esc(slugify(t))}">{esc(t)}<span class="side-count">{n:02d}</span></a><ul class="side-articles">'
        + ''.join(f'<li data-slug="{esc(a["slug"])}"><a href="{esc(a["slug"])}/index.html">{esc(a["title"])}</a></li>'
                  for a in v if lifecycle(a, today)['status'] != 'Outdated news') + '</ul></li>'
        for t, v, n in groups if n)
    sidebar = (f'<aside class="sidebar" aria-label="Sections and articles"><details class="side-sections" open><summary class="side-summary">Sections</summary>'
               f'<ul class="side-list"><li><a class="side-section side-all" href="#browse">All sections<span class="side-count">{len(entries):02d}</span></a></li>{side_groups}</ul></details>'
               '<a href="maintenance/index.html" class="sidebar-note">A date on every page.<br>A clear limit on every claim.</a></aside>')
    news_button = ('<button type="button" class="type-button" data-kind="news" aria-pressed="false">News &amp; magazine</button>'
                   if any(a['type'] == 'news' for a in articles) else '')
    home = f'''<section id="library"><div class="eyebrow">OPEN SOURCE · OPEN WEIGHTS · PRACTICAL ENGINEERING</div><div class="intro-row"><div><h1>Understand it.<br><span>Try it. Document it.</span></h1><p class="intro">AI and software engineering, with useful visuals.<br>Each page shows its author, dates and review status.</p></div>{stats}</div>
<div class="library-topline"><div><span class="section-number">01 /</span> <h2>Start with an explanation</h2></div><span class="mono muted">TEXT FIRST. VISUAL WHEN USEFUL.</span></div>
<a class="featured{"" if featured_visual else " featured-single"}" href="{featured['slug']}/index.html"><div class="featured-copy"><div class="entry-kicker"><span class="kind kind-{esc(featured['type'])}">{esc(featured['type'].upper())}</span><span>{esc(featured['section'].upper())}</span></div><h3>{esc(featured['title'])}</h3><p>{esc(featured['summary'])}</p><div class="featured-footer"><span>Read the explanation</span><span class="mono">ARTICLE + VISUAL</span></div><div class="featured-dates">Published {when(featured.get('published'))} · Edited {when(featured.get('edited'))} <span class="status status-{fs['class']}">{fs['status']}</span></div></div>{f'<div class="featured-visual">{featured_visual}</div>' if featured_visual else ''}</a>
<section id="browse" class="browse" aria-labelledby="browse-title"><div class="library-topline"><div><span class="section-number">02 /</span> <h2 id="browse-title">Browse the field notes</h2></div><span id="result-count" class="mono muted" aria-live="polite">{len(listing)} entries</span></div>
<div class="search-row"><label class="search-box js-only"><span class="sr-only">Search titles and descriptions</span><input id="search" type="search" placeholder="Find an explanation, experiment, or subject…" autocomplete="off"></label><label class="archive-control js-only"><input id="archive" type="checkbox"> Show older news</label></div>
<div class="filter-row js-only" role="group" aria-label="Content type"><button type="button" class="type-button active" data-kind="all" aria-pressed="true">All entries</button><button type="button" class="type-button" data-kind="guide" aria-pressed="false">Guides</button><button type="button" class="type-button" data-kind="experiment" aria-pressed="false">Experiments</button>{news_button}</div>
<div id="entries" class="entries">{''.join(section_block(name, items, today) for name, items, n in groups)}</div><div id="empty" class="empty" hidden>No matching entries. Try another filter or clear the search.</div><p><a href="archive/index.html">Open the news archive</a></p></section>
<section id="principles" class="principles"><div class="library-topline"><div><span class="section-number">03 /</span> <h2>Useful today. Honest about time.</h2></div></div><div class="principle-grid"><div><span class="kind kind-news">NEWS</span><h3>A three-month window</h3><p>A dated observation. After three calendar months, it moves to the archive and shows an outdated notice. Editing it does not restart the clock.</p></div><div><span class="kind kind-guide">GUIDE</span><h3>Knowledge worth revisiting</h3><p>A longer-lived explanation. It shows its last technical review and next review date. A missed review means due for a check, not no longer valid.</p></div><div><span class="kind kind-experiment">EXPERIMENT</span><h3>Results from a known setup</h3><p>The test date, versions, method, and limits stay with the result. An old measurement remains historical evidence; it does not describe a newer release.</p></div></div>{summary_visual}</section>
<section id="about" class="about"><div><span class="side-label">ABOUT THIS LIBRARY</span><h2>Practical work,<br>with its context attached.</h2></div><div><p>HAAL publications share explanations and experiments about AI and software engineering. Each article identifies its author, scope, sources, and limits. Personal views are labelled separately.</p><p class="muted">No account required. No engagement counters. Every page is written for this library and cites public sources.</p></div></section></section>'''
    write('index.html', shell('Catalogue', home, sidebar=sidebar))
    ledger = []
    for a in articles:
        status = lifecycle(a, today)
        visual = a['_figure']
        review_meta = f'<div>Last technical review<strong>{when(a.get("reviewed"))}</strong></div>' if a['type']=='guide' else ''
        metadata = f'''<div class="article-metadata"><div>Author / perspective<strong>{esc(a['author'])} · {esc(perspective_label(a))}</strong></div><div>First published<strong>{when(a.get('published'))}</strong></div><div>Last edited<strong>{when(a.get('edited'))}</strong></div>{review_meta}<div>{'News expires' if a['type']=='news' else 'Next review'}<strong>{when(status['due'])}</strong></div></div>'''
        paragraphs = a['_body'] if a['_body'] is not None else ''.join('<section><h2>'+esc(s['title'])+'</h2>'+''.join('<p>'+esc(p)+'</p>' for p in s['paragraphs'])+'</section>' for s in a['sections'])
        if a['_figure_in_body']:
            visual = ''
        notice = {'news':'A dated report. It moves to the archive after three calendar months.', 'guide':'A missed review date means the guide is due for a check. It does not establish that the content is wrong.', 'experiment':'These results apply to the recorded setup. Check the versions and test date.'}[a['type']]
        if is_draft(a):
            notice = 'Draft preview. Not published and not approved. Dates are set at release.'
        if a['perspective'].startswith('Individual'):
            notice += f'</p><p>Individual view: the analysis of {esc(a["author"])}. It is not a HAAL publication or position.'
        history = '<details><summary>Revision history</summary><ul>'+''.join('<li>'+day(r['date'])+' — '+esc(r['note'])+'</li>' for r in a['history'])+'</ul></details>'
        body = f'''<article class="public-article"><a href="../index.html">Catalogue</a><div class="entry-kicker"><span class="kind kind-{a['type']}">{a['type'].upper()}</span><span>{esc(a['section'])}</span></div><h1>{esc(a['title'])}</h1><p class="article-deck">{esc(a['summary'])}</p>{metadata}<div class="article-notice"><span class="status status-{status['class']}">{status['status']}</span><p>{notice}</p></div>{visual}<div class="reader-body">{paragraphs}{history}</div></article>'''
        write(a['slug']+'/index.html', shell(a['title'], body, '../', a['summary']))
        ledger.append({'slug':a['slug'],'title':a['title'],'content_type':a['type'],'perspective':a['perspective'],
                       'published':a.get('published'),'last_reviewed':a.get('reviewed'),'tested':a.get('tested'),
                       'action':status['action'],'due':status['due'],'status':status['status'],
                       'owner':'HAAL Publisher','path':'../'+a['slug']+'/index.html'})
    review_visual = flow('Review decisions', ['Check the due date', 'Inspect content and sources', 'Record the result'],
                         ['A timer identifies work', 'A person or assisted review checks accuracy', 'Keep dates and revision evidence'],
                         'The daily build refreshes date labels. It does not perform a technical review or approve new content.')
    rows=''.join(f'<li><a href="{esc(r["path"])}">{esc(r["title"])}</a><p>{esc(r["action"])} · Due {when(r["due"])} · {esc(r["status"])}</p></li>' for r in sorted(ledger,key=lambda r:r['due'] or '9999'))
    ledger_page = f'<div class="eyebrow">PUBLICATION MAINTENANCE</div><h1>What needs review,<br><span>and when.</span></h1><p class="intro">Computed on {day(today)} (UTC in the scheduled build). Dates come from the publication catalogue.</p>{review_visual}<h2>Review queue</h2><ol class="review-queue">{rows}</ol><p><a href="ledger.json">Download the maintenance ledger (JSON)</a></p>'
    write('maintenance/index.html',shell('Review ledger',ledger_page,'../'))
    write('maintenance/ledger.json',json.dumps({'computed_on':today.isoformat(),'items':ledger},indent=2)+'\n')
    archive=[a for a in articles if lifecycle(a,today)['status']=='Outdated news']
    archive_visual=flow('The news archive',['Original report','Three-month boundary','Historical reference'],['First publication stays fixed','News becomes outdated','Read with its original context'],'Archiving changes how news is presented. It preserves the original report and publication date.')
    archive_body='<h1>News archive</h1><p class="intro">Dated reports remain accessible after their current-news window ends.</p>'+archive_visual
    archive_body+=''.join(entry(a,today,'../') for a in archive) if archive else '<h2>Archive policy</h2><p>No news report has reached its three-month boundary yet. The first news entry expires on '+day(plus_months('2026-11-25',3))+'.</p>'
    write('archive/index.html',shell('News archive',archive_body,'../'))
    write('catalogue.json',json.dumps({'as_of':today.isoformat(),'release_marker':catalogue['release_marker'],'articles':[{k:a[k] for k in ['slug','title','section','type','published','summary','formats','perspective']} for a in articles]},indent=2)+'\n')
    write('404.html',shell('Page not found','<h1>This page is not in the catalogue.</h1>'+summary_visual+'<p><a href="./index.html">Open the catalogue</a></p>'))
    for gone in catalogue.get('retired', []):
        write(gone['slug']+'/index.html', shell('Page retired', f'<h1>This page has been retired.</h1><p>{esc(gone["note"])}</p>'+summary_visual+'<p><a href="../index.html">Open the catalogue</a></p>', '../'))
    write('.nojekyll','')
    for w in warnings:
        print('PREVIEW WARNING:', w, file=sys.stderr)
    print(json.dumps({'articles':len(articles),'generated_pages':len(list(out.rglob('*.html'))),'as_of':today.isoformat(),'release':catalogue['release_marker'],
                      **({'mode':'preview','output':str(out),'warnings':len(warnings)} if preview else {})}))
    return warnings


if __name__ == '__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--as-of',type=date.fromisoformat)
    parser.add_argument('--preview',action='store_true',help='private draft preview into _preview/ (never deployed)')
    parser.add_argument('--drafts',action='append',default=[],metavar='DIR',help='folder of <slug>/entry.json staging entries; implies --preview')
    args=parser.parse_args()
    build(args.as_of,preview=args.preview or bool(args.drafts),drafts=args.drafts)
