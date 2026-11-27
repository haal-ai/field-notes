"""Build the public catalogue, static articles, and review ledger. Standard library only."""
import argparse
import calendar
import html
import json
import re
import shutil
import unicodedata
from collections import OrderedDict
from datetime import date
import sys
from pathlib import Path

import glossary
import news
from render import esc, figure_markers, inline_svg, leftovers, markdown
from strings_fr import (ABOUT, JS_KEYS, KIND, SECTION_NAMES, SECTION_NOTE_DEFAULT, SECTION_NOTES, T, fr_day, fr_full_day, fr_month_year)

ROOT = Path(__file__).resolve().parent
OUT = ROOT / '_site'                # public output: the only directory ever deployed
PREVIEW_OUT = ROOT / '_preview'     # private draft preview: never deployed, git-ignored
APPROVED = ['approved-publication-test', 'approved-publication']
PRIVATE_TOKENS = ['teams.microsoft.com', 'sharepoint.com', '/users/', 'file://']
STATE = {'preview': False, 'out': OUT, 'glossary': False, 'news': False}


def plus_months(value, months):
    d = date.fromisoformat(value)
    month = d.year * 12 + d.month - 1 + months
    year, month = divmod(month, 12)
    return date(year, month + 1, min(d.day, calendar.monthrange(year, month + 1)[1]))


def day(value):
    try:
        d = date.fromisoformat(str(value))
    except ValueError:  # only drafts reach here; validate() rejects non-ISO dates in public builds
        return T['undated']
    return fr_day(d)


def when(value):
    if not iso(value):
        return f'<span class="undated">{T["undated"]}</span>'
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


def section_name(article):
    return SECTION_NAMES.get(article['section'], article['section'])


def is_outdated(article, today):
    return lifecycle(article, today)['class'] == 'archived'


def count_label(n):
    return T['notes_count']['one' if n == 1 else 'other'].format(n=n)


def lifecycle(article, today):
    kind = article['type']
    if is_draft(article):
        return {'status': T['status_draft'], 'class': 'draft', 'due': None, 'action': T['action_draft']}
    if kind == 'news':
        due = plus_months(article['published'], 3)
        old = today >= due
        return {'status': T['status_news_old'] if old else T['status_news_current'],
                'class': 'archived' if old else 'current', 'due': due.isoformat(),
                'action': T['action_news_old'] if old else T['action_news_current']}
    if kind == 'guide':
        due = plus_months(article['reviewed'], article['review_months'])
        late = today >= due
        return {'status': T['status_guide_due'] if late else T['status_guide_ok'].format(month=fr_month_year(due)),
                'class': 'due' if late else 'current', 'due': due.isoformat(), 'action': T['action_guide']}
    tested = article.get('tested')
    return {'status': T['status_experiment_dated'].format(date=day(tested)) if iso(tested) else T['status_experiment'],
            'class': 'record', 'due': article['review_due'], 'action': T['action_experiment']}


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
        # Articles with figN.svg markers carry their figures in the folder; others need the single 'visual' entry.
        keys = ['slug', 'title', 'section', 'type', 'summary', 'approval', 'formats', 'history']
        if article_markers(article):
            article.pop('visual', None)  # figN.svg markers replace the single visual
        for key in keys + ([] if article_markers(article) else ['visual']):
            if not article.get(key):
                raise ValueError(f'Missing {key}: {article.get("slug", "unknown article")}')
        slug = article['slug']
        if not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', slug) or slug in slugs:
            raise ValueError('Invalid or duplicate slug')
        slugs.add(slug)
        draft = is_draft(article)
        if draft and not preview:
            raise ValueError(f'Draft or unapproved entry refused in a public build: {slug}')
        if article.get('lang', 'en') not in ('fr', 'en'):
            raise ValueError(f'Unknown lang: {slug}')
        if article['type'] not in ['guide', 'news', 'experiment']:
            raise ValueError('Unknown content type')
        if not article.get('sections') and not body_file(article):
            raise ValueError(f'Missing sections or article.md: {slug}')
        if article.get('visual'):
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


def article_markers(article):
    path = body_file(article)
    return figure_markers(path.read_text()) if path else []


def figure_html(svg, caption, alt):
    return (f'<figure data-learning-visual="svg">{svg}<figcaption>{esc(caption)}</figcaption>'
            f'<details class="fig-text" style="margin-top:12px;padding:10px 14px"><summary>{T["figure_text"]}</summary>{alt}</details></figure>')


def alt_text(alt_file, label, problems):
    """Render a text equivalent file; record placeholders and private references."""
    if not alt_file.is_file():
        problems.append(f'text equivalent {label} not written yet')
        return f'<p>{T["figure_text_missing"]}</p>'
    raw = alt_file.read_text()
    alt, _ = markdown(raw, warnings=problems)
    problems.extend(f'{label}: {l}' for l in leftovers(raw))
    problems.extend(f'{label}: private reference {t}' for t in PRIVATE_TOKENS if t in raw.lower())
    return alt


def marker_figure(article, name, caption, problems):
    """One figN.svg marker: inline SVG, caption from the marker, text equivalent from figN.alt.md."""
    slug, stem = article['slug'], name[:-4]
    folder = article_dir(article)
    if not caption:
        problems.append(f'{name}: empty figure caption')
    elif leftovers(caption):
        problems.append(f'{name}: figure caption is still a placeholder')
    if not (folder / name).is_file():
        problems.append(f'{name}: figure file missing')
        return f'<p class="fig-missing">{esc(T["figure_missing"].format(name=name))}</p>'
    raw = (folder / name).read_text()
    try:
        svg = inline_svg(raw, f'{slug}-{stem}')
    except ValueError as err:
        problems.append(f'{name}: {err}')
        return f'<p class="fig-missing">{esc(T["figure_missing"].format(name=name))}</p>'
    problems.extend(f'{name}: private reference {t}' for t in PRIVATE_TOKENS if t in svg.lower())
    return figure_html(svg, caption, alt_text(folder / f'{stem}.alt.md', f'{stem}.alt.md', problems))


def figure(article, problems):
    """The page figure: the built-in three-step flow, or the article's own inline SVG with caption and text equivalent."""
    v = article['visual']
    if v['kind'] == 'flow':
        return flow(v['title'], v['nodes'], v['details'], v['caption'])
    folder = article_dir(article)
    svg = inline_svg((folder / v['svg']).read_text(), article['slug'])
    alt = alt_text(folder / v['alt'], v['alt'], problems)
    problems.extend(f'private reference {t} in figure' for t in PRIVATE_TOKENS if t in svg.lower())
    if leftovers(v['caption']):
        problems.append('figure caption is still a placeholder')
    return figure_html(svg, v['caption'], alt)


def prepare(articles, preview):
    """Render each article's figures and body. Public builds raise on any problem; preview collects them."""
    warnings = []
    for a in articles:
        problems = []
        if preview and (a.get('visual') or {}).get('kind') == 'flow' and (article_dir(a) / 'visual.svg').is_file():
            a['visual'] = dict(a['visual'], kind='svg', svg='visual.svg', alt='alt.md')  # preview-only adapter
        a['_figure'] = figure(a, problems) if a.get('visual') else ''
        a['_body'], a['_figure_in_body'] = None, False
        path = body_file(a)
        markers = figure_markers(path.read_text()) if path else []
        names = [n for _, n in markers]
        problems.extend(f'{n}: figure used twice' for n in sorted(set(names)) if names.count(n) > 1)
        if a.get('lang') == 'fr' and len(markers) + bool(a.get('visual')) < 3:
            problems.append(f'a French article needs at least 3 figures (found {len(markers) + bool(a.get("visual"))})')
        if path:
            text = path.read_text()
            problems.extend(f'{path.name}: unfinished text "{l}"' for l in leftovers(text))
            problems.extend(f'{path.name}: private reference {t}' for t in PRIVATE_TOKENS if t in text.lower())
            marker = (a.get('visual') or {}).get('svg')
            a['_body'], a['_figure_in_body'] = markdown(text, marker, a['_figure'], problems,
                                                        figure_fn=lambda n, c, a=a: marker_figure(a, n, c, problems))
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


def js_strings():
    """Strings site.js needs, as JSON safe to embed in a script element."""
    return json.dumps({k: T[k] for k in JS_KEYS}, ensure_ascii=False).replace('</', '<\\/')


def shell(title, content, prefix='', description=None, sidebar=''):
    description = description or T['description']
    main_open, main_close = (f'<div class="site-layout">{sidebar}', '</div>') if sidebar else ('', '')
    preview = STATE['preview']
    gloss_nav = f'<a href="{prefix}glossaire/index.html">{T["nav_glossary"]}</a>' if STATE['glossary'] else ''
    gloss_foot = f'<a href="{prefix}glossaire/index.html">{T["nav_glossary"]}</a>' if STATE['glossary'] else ''
    news_nav = f'<a href="{prefix}nouvelles/index.html">{T["nav_news"]}</a>' if STATE['news'] else ''
    extra_head = ('<meta name="robots" content="noindex,nofollow"><style>.status-draft{border:1px dashed var(--due);color:var(--due)}'
                  '.undated{color:var(--muted)}.fig-missing{border:1px dashed var(--due);color:var(--due);padding:12px}'
                  '.preview-banner{background:var(--due-bg);color:var(--due);border-bottom:1px solid var(--due);'
                  'padding:10px 20px;font-size:.875rem;text-align:center}</style>') if preview else ''
    banner = f'<div class="preview-banner" role="note" data-preview="true">{T["preview_banner"]}</div>' if preview else ''
    title = T['preview_title'].format(title=title) if preview else title
    return f'''<!doctype html><html lang="{T['lang']}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="color-scheme" content="dark light">{extra_head}<meta name="description" content="{esc(description)}"><title>{esc(title)} — {T['site_name']}</title>
<link rel="stylesheet" href="{prefix}assets/styles.css"><link rel="stylesheet" href="{prefix}assets/publication.css"><script type="application/json" id="i18n">{js_strings()}</script><script defer src="{prefix}assets/site.js"></script><noscript><style>.js-only{{display:none!important}}</style></noscript></head>
<body>{banner}<a class="skip-link" href="#main">{T['skip']}</a><header class="site-header"><a class="brand" href="{prefix}index.html"><span class="brand-mark" aria-hidden="true">h/</span><strong>{T['site_name']}<span class="brand-sub">{T['brand_sub']}</span></strong></a><nav class="header-nav" aria-label="{T['nav_aria']}"><a href="{prefix}index.html">{T['nav_catalogue']}</a>{news_nav}{gloss_nav}<a href="{prefix}archive/index.html">{T['nav_archive']}</a><a href="{prefix}maintenance/index.html">{T['nav_ledger']}</a></nav><button id="theme" type="button" class="theme-control">{T['theme']} : {T['theme_system']}</button></header>{main_open}<main id="main" class="publication-main">{content}<footer><a href="{prefix}index.html" class="footer-brand">{T['footer_brand']}</a><span>{T['footer_tagline']}</span><a href="{prefix}how-these-notes-age/index.html">{T['footer_dates']}</a>{gloss_foot}</footer></main>{main_close}</body></html>'''


def slugify(text):
    """ASCII anchor id: accents are dropped so 'Inférence' becomes 'inference'."""
    plain = unicodedata.normalize('NFKD', text.lower()).encode('ascii', 'ignore').decode()
    return re.sub(r'[^a-z0-9]+', '-', plain).strip('-')


def entry(article, today, prefix=''):
    status = lifecycle(article, today)
    kind = article['type']
    return f'''<article class="entry" data-slug="{esc(article['slug'])}" data-kind="{esc(kind)}" data-topic="{esc(slugify(section_name(article)))}" data-outdated="{'true' if status['class']=='archived' else 'false'}"><div class="entry-kind"><span class="kind kind-{esc(kind)}">{KIND[kind]}</span></div><div><a class="entry-title" href="{prefix}{article['slug']}/index.html">{esc(article['title'])}</a><p class="entry-description">{esc(article['summary'])}</p><div class="entry-formats">{T['article_with_figures']}</div></div><div class="entry-date">{T['published_label']}<strong>{when(article.get('published'))}</strong><span class="status status-{status['class']}">{status['status']}</span></div></article>'''


def section_slug(article):
    return slugify(section_name(article))


def sections_of(articles, today):
    """Group articles under their displayed section heading: largest first, the library's own section last."""
    groups = {}
    for a in articles:
        groups.setdefault(section_name(a), []).append(a)
    order = sorted(groups, key=lambda name: (name == ABOUT, -len(groups[name]), name))
    return [(name, groups[name], sum(not is_outdated(a, today) for a in groups[name])) for name in order]


SECTION_PAGE_SIZE = 20


def section_card(name, items, today, slug):
    """A home-page card for one section: description, count, three most recent notes, a link to its page."""
    note = SECTION_NOTES.get(name) or SECTION_NOTE_DEFAULT.format(name=name)
    current = [a for a in items if not is_outdated(a, today)]
    recent = ''.join(
        f'<li><span class="kind kind-{esc(a["type"])}">{KIND[a["type"]]}</span><a href="{esc(a["slug"])}/index.html">{esc(a["title"])}</a></li>'
        for a in current[:3])
    return (f'<article class="section-card"><h3><a href="sections/{slug}/index.html">{esc(name)}</a>'
            f'<span class="section-count">{len(current):02d}</span></h3><p class="section-note">{esc(note)}</p>'
            f'<p class="section-recent-label">{T["section_recent"]}</p><ul class="section-recent">{recent}</ul>'
            f'<a class="section-view-all" href="sections/{slug}/index.html">{T["section_view_all"].format(n=len(current))}</a></article>')


def section_page(name, slug, items, today, summary_visual):
    """Write /sections/<slug>/ and its static pagination pages: newest first, 20 per page, a type filter, a per-section search box."""
    current = sorted((a for a in items if not is_outdated(a, today)),
                      key=lambda a: a.get('published') if iso(a.get('published')) else '0000', reverse=True)
    pages = max(1, -(-len(current) // SECTION_PAGE_SIZE))
    note = SECTION_NOTES.get(name) or SECTION_NOTE_DEFAULT.format(name=name)
    news_button = (f'<button type="button" class="type-button" data-kind="news" aria-pressed="false">{T["filter_news"]}</button>'
                   if any(a['type'] == 'news' for a in current) else '')
    for page_num in range(1, pages + 1):
        chunk = current[(page_num - 1) * SECTION_PAGE_SIZE: page_num * SECTION_PAGE_SIZE]
        depth_prefix = '../../' if page_num == 1 else '../../../../'
        rows = ''.join(entry(a, today, depth_prefix) for a in chunk)
        crumb = f'<p class="breadcrumb"><a href="{depth_prefix}index.html">{T["crumb_catalogue"]}</a> › {esc(name)}</p>'
        nav_links = []
        if page_num > 1:
            target = 'index.html' if page_num == 2 else f'../{page_num - 1}/index.html'
            nav_links.append(f'<a href="{target}" rel="prev">{T["section_prev"]}</a>')
        if page_num < pages:
            nav_links.append(f'<a href="../{page_num + 1}/index.html" rel="next">{T["section_next"]}</a>')
        pagination = (f'<nav class="pagination" aria-label="{T["section_page_of"].format(page=page_num, total=pages)}">'
                      f'<span class="mono muted">{T["section_page_of"].format(page=page_num, total=pages)}</span>{"".join(nav_links)}</nav>') if pages > 1 else ''
        body = f'''{crumb}<div class="eyebrow">{T['side_title']}</div><h1>{esc(name)}</h1><p class="intro">{esc(note)}</p>{summary_visual if page_num == 1 else ''}
<div class="search-row"><label class="search-box js-only"><span class="sr-only">{T['section_search_placeholder']}</span><input id="section-search" type="search" placeholder="{esc(T['section_search_placeholder'])}" autocomplete="off"></label></div>
<div class="filter-row js-only" role="group" aria-label="{T['section_type_filter_aria']}"><button type="button" class="type-button active" data-kind="all" aria-pressed="true">{T['filter_all']}</button><button type="button" class="type-button" data-kind="guide" aria-pressed="false">{T['filter_guide']}</button><button type="button" class="type-button" data-kind="experiment" aria-pressed="false">{T['filter_experiment']}</button>{news_button}</div>
<div id="entries" class="entries">{rows}</div><div id="empty" class="empty" hidden>{T['empty']}</div>{pagination}'''
        path = f'sections/{slug}/index.html' if page_num == 1 else f'sections/{slug}/page/{page_num}/index.html'
        write(path, shell(name, body, '../../' if page_num == 1 else '../../../../', note))


def load_news():
    """Load content/news/news.json; [] if the file is missing. Raises ValueError on any privacy/schema problem."""
    path = ROOT / 'content/news/news.json'
    if not path.is_file():
        return []
    records = json.loads(path.read_text())
    problems = news.check(records)
    if problems:
        raise ValueError('News: ' + '; '.join(problems))
    return news.sorted_desc(records)


def news_home_block(records, today):
    """The home page's small 'Dernières nouvelles' block: the 5 newest, a link to the full page."""
    current = [r for r in records if news.in_window(r, today)]
    if not current:
        return ''
    top5 = current[:5]
    rows = ''.join(
        f'<li><span class="news-theme news-theme-{esc(news._slug(r["theme"]))}">{esc(r["theme"])}</span>'
        f'<a href="{esc(news.source_url(r))}">{esc(r["title_fr"])}</a></li>' for r in top5)
    return (f'<section id="news-home" class="news-home"><div class="library-topline"><div><h2>{T["news_home_title"]}</h2></div></div>'
            f'<ul class="news-home-list">{rows}</ul><a href="nouvelles/index.html">{T["news_home_more"]}</a></section>')


def news_notice():
    return f'<div class="article-notice news-notice"><p>{esc(T["news_notice"])}</p><p>{esc(T["notice_all"])}</p></div>'


def news_page(records, today):
    """Write /nouvelles/: figure, theme chips + search, newest-first list grouped by day. Records older than
    WINDOW_DAYS go to the archive instead and are not written here."""
    current = [r for r in records if news.in_window(r, today)]
    chips = news.theme_chips(current, T['news_filter_aria'])
    by_day = news.by_day(current)
    days_html = ''.join(news.day_section(iso_date, fr_full_day(date.fromisoformat(iso_date)), recs)
                        for iso_date, recs in by_day.items())
    body = f'''<div class="eyebrow">{T['side_title']}</div><h1>{esc(T['news_title'])}</h1><p class="intro">{esc(T['news_intro'])}</p>
{news_notice()}
<div class="search-row"><label class="search-box js-only"><span class="sr-only">{T['news_search_placeholder']}</span><input id="news-search" type="search" placeholder="{esc(T['news_search_placeholder'])}" autocomplete="off"></label></div>
{chips}
<div id="news-list" class="news-list">{days_html}</div><div id="empty" class="empty" hidden>{T['news_empty']}</div>
<p><a href="archives/index.html">{T['news_open_archives']}</a></p>'''
    write('nouvelles/index.html', shell(T['news_title_short'], body, '../', T['news_intro']))


def news_archive(records, today):
    """Write /nouvelles/archives/ and one page per month for every record outside the 4-week window, oldest months first link, newest first within a month."""
    older = [r for r in records if not news.in_window(r, today)]
    months = OrderedDict()
    for r in sorted(older, key=lambda r: (r['date'], r['id']), reverse=True):
        months.setdefault(news.month_key(r['date']), []).append(r)
    archive_visual = flow(T['archive_visual_title'], T['archive_visual_nodes'], T['archive_visual_details'], T['archive_visual_caption'])
    index_rows = ''.join(
        f'<li><a href="{key}/index.html">{esc(news.month_label(key))}</a> <span class="mono muted">{len(recs):02d}</span></li>'
        for key, recs in months.items())
    index_body = f'''<p class="breadcrumb"><a href="../../index.html">{T['crumb_catalogue']}</a> › <a href="../index.html">{T['news_title_short']}</a> › {T['news_archive_title']}</p>
<div class="eyebrow">{T['side_title']}</div><h1>{esc(T['news_archive_title'])}</h1><p class="intro">{esc(T['news_archive_intro'])}</p>{archive_visual}
<ul class="archive-month-list">{index_rows}</ul>''' if months else f'''<p class="breadcrumb"><a href="../../index.html">{T['crumb_catalogue']}</a> › <a href="../index.html">{T['news_title_short']}</a> › {T['news_archive_title']}</p>
<div class="eyebrow">{T['side_title']}</div><h1>{esc(T['news_archive_title'])}</h1><p class="intro">{esc(T['news_archive_intro'])}</p>{archive_visual}<p>{esc(T['news_archive_month_empty'])}</p>'''
    write('nouvelles/archives/index.html', shell(T['news_archive_title'], index_body, '../../'))
    for key, recs in months.items():
        by_day_recs = news.by_day(recs)
        days_html = ''.join(news.day_section(iso_date, fr_full_day(date.fromisoformat(iso_date)), day_recs)
                            for iso_date, day_recs in by_day_recs.items())
        crumb = f'<p class="breadcrumb"><a href="../../../index.html">{T["crumb_catalogue"]}</a> › <a href="../../index.html">{T["news_title_short"]}</a> › <a href="../index.html">{T["news_archive_title"]}</a> › {esc(news.month_label(key))}</p>'
        body = f'{crumb}<div class="eyebrow">{T["side_title"]}</div><h1>{esc(news.month_label(key))}</h1>{archive_visual}{news_notice()}<div class="news-list">{days_html}</div>'
        write(f'nouvelles/archives/{key}/index.html', shell(news.month_label(key), body, '../../../../'))


def write(path, content):
    dest = STATE['out'] / path
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(content)


def load_drafts(folders):
    """Read <folder>/<slug>/entry-fr.json (preferred) or entry.json staging entries (preview only). Folder names must equal slugs."""
    found = []
    for folder in folders:
        for slug_dir in sorted(p for p in Path(folder).iterdir() if p.is_dir()):
            entry_file = next((slug_dir / n for n in ('entry-fr.json', 'entry.json') if (slug_dir / n).is_file()), None)
            if not entry_file:
                continue
            article = json.loads(entry_file.read_text())
            if article.get('slug') != entry_file.parent.name:
                raise ValueError(f'Folder name must equal slug: {entry_file.parent}')
            article['_dir'] = str(entry_file.parent)
            found.append(article)
    return found


def article_texts(article):
    """Every text a reader could meet in an article: body, captions, text equivalents and figure labels."""
    folder, texts = article_dir(article), []
    path = body_file(article)
    if path:
        texts.append(glossary.plain(path.read_text()))
    for f in sorted(folder.glob('fig*.alt.md')) + sorted(folder.glob('fig*.svg')) + sorted(folder.glob('visual.svg')) + sorted(folder.glob('alt.md')):
        raw = f.read_text()
        texts.append(glossary.plain(re.sub(r'<[^>]+>', ' ', raw) if f.suffix == '.svg' else raw))
    return texts


def check_glossary(entries, texts):
    """Problems: a key term used in an article without an entry, or an entry no article uses."""
    problems = []
    everything = [x for t in texts.values() for x in t]
    for term in glossary.used_terms(everything):
        if not any(e['regex'].search(term) for e in entries):
            problems.append(f'key term used but not defined: {term}')
    for e in entries:
        if not any(e['regex'].search(x) for x in everything):
            problems.append(f'entry not used by any article: {e["term"]}')
    return problems


def build(today=None, preview=False, drafts=()):
    """Public build -> _site (refuses drafts). Preview build -> _preview (accepts drafts, never deployed)."""
    if drafts and not preview:
        raise ValueError('Draft folders need preview mode')
    today = today or date.today()
    out = PREVIEW_OUT if preview else OUT
    STATE.update(preview=preview, out=out)
    catalogue = json.loads((ROOT / 'content/catalogue.json').read_text())
    staged = load_drafts(drafts)
    staged_slugs = {a['slug'] for a in staged}  # a staged entry replaces the catalogue entry with the same slug
    catalogue['articles'] = [a for a in catalogue['articles'] if a['slug'] not in staged_slugs] + staged
    validate(catalogue, preview)
    warnings = prepare(catalogue['articles'], preview)
    gloss_file = next((Path(d) / 'glossaire.md' for d in drafts if (Path(d) / 'glossaire.md').is_file()), ROOT / 'content/glossaire.md')
    gloss = glossary.parse(gloss_file.read_text()) if gloss_file.is_file() else []
    STATE['glossary'] = bool(gloss)
    news_records = load_news()
    STATE['news'] = bool(news_records)
    texts = {a['slug']: article_texts(a) for a in catalogue['articles']}
    if news_records:
        texts['__news__'] = [r['title_fr'] + ' ' + r['text_fr'] for r in news_records]
    gloss_problems = check_glossary(gloss, texts) if gloss else []
    if gloss_problems and not preview:
        raise ValueError('Glossary: ' + '; '.join(gloss_problems))
    warnings.extend(f'glossaire: {p}' for p in gloss_problems)
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
    entries = [a for a in articles if not is_outdated(a, today)]
    summary_visual = flow(T['choose_visual_title'], T['choose_visual_nodes'], T['choose_visual_details'], T['choose_visual_caption'])
    listing = sorted(articles, key=lambda a: a.get('published') if iso(a.get('published')) else '0000', reverse=True)
    groups = sections_of(listing, today)
    candidates = [a for a in articles if not is_draft(a)] or articles
    # Feature a content article, never the library's own "about" page; the catalogue may name one.
    named = catalogue.get('featured')
    featured = next((a for a in candidates if a['slug'] == named), None) or next(
        (a for a in candidates if section_name(a) != ABOUT and a['type'] == 'guide'), candidates[0])
    fs = lifecycle(featured, today)
    fv = featured.get('visual') or {}
    # Only the built-in three-step flow fits the card; tall article figures stay on the article page.
    featured_visual = flow(fv['title'], fv['nodes'], fv['details'], fv['caption']) if fv.get('nodes') else ''
    published = [a for a in articles if not is_draft(a)]
    stats = (f'<div class="library-stats"><strong>{count_label(len(published))}</strong>'
             f'<span>{T["updated"].format(date=day(max(a["edited"] for a in published)))}</span></div>') if published else ''
    side_items = ''.join(
        f'<li><a class="side-section" href="sections/{slugify(t)}/index.html">{esc(t)}<span class="side-count">{n:02d}</span></a></li>'
        for t, v, n in groups if n)
    sidebar = (f'<aside class="sidebar" aria-label="{T["side_aria"]}"><details class="side-sections" open><summary class="side-summary">{T["side_title"]}</summary>'
               f'<ul class="side-list"><li><a class="side-section side-all" href="#browse">{T["side_all"]}<span class="side-count">{len(entries):02d}</span></a></li>{side_items}</ul></details></aside>')
    news_button = (f'<button type="button" class="type-button" data-kind="news" aria-pressed="false">{T["filter_news"]}</button>'
                   if any(a['type'] == 'news' for a in articles) else '')
    cards = ''.join(section_card(name, items, today, slugify(name)) for name, items, n in groups if n)

    def search_entry(a):
        # entry() already renders kind, title, summary, date and status; add data-topic and a section tag for the flat results list.
        html = entry(a, today).replace('<article class="entry"', f'<article class="entry" data-topic="{esc(slugify(section_name(a)))}"', 1)
        return html.replace('</div><div class="entry-date">', f'<p class="entry-section-tag">{esc(section_name(a))}</p></div><div class="entry-date">')

    search_index = ''.join(search_entry(a) for a in listing)
    home = f'''<section id="library"><div class="eyebrow">{T['eyebrow']}</div><div class="intro-row"><div><h1>{T['hero']}</h1><p class="intro">{T['intro']}</p></div>{stats}</div>
<div class="library-topline"><div><span class="section-number">01 /</span> <h2>{T['start_title']}</h2></div><span class="mono muted">{T['start_hint']}</span></div>
<a class="featured{"" if featured_visual else " featured-single"}" href="{featured['slug']}/index.html"><div class="featured-copy"><div class="entry-kicker"><span class="kind kind-{esc(featured['type'])}">{KIND[featured['type']]}</span><span>{esc(section_name(featured).upper())}</span></div><h3>{esc(featured['title'])}</h3><p>{esc(featured['summary'])}</p><div class="featured-footer"><span>{T['featured_read']}</span><span class="mono">{T['featured_tag']}</span></div><div class="featured-dates">{T['published_on']} {when(featured.get('published'))} · {T['edited_on']} {when(featured.get('edited'))} <span class="status status-{fs['class']}">{fs['status']}</span></div></div>{f'<div class="featured-visual">{featured_visual}</div>' if featured_visual else ''}</a>
<section id="browse" class="browse" aria-labelledby="browse-title"><div class="library-topline"><div><span class="section-number">02 /</span> <h2 id="browse-title">{T['browse_sections_title']}</h2></div><span id="result-count" class="mono muted" aria-live="polite" hidden></span></div>
<div class="search-row"><label class="search-box js-only"><span class="sr-only">{T['search_label']}</span><input id="search" type="search" placeholder="{T['search_placeholder']}" autocomplete="off"></label><label class="archive-control js-only"><input id="archive" type="checkbox"> {T['show_old_news']}</label></div>
<div class="filter-row js-only" role="group" aria-label="{T['filter_aria']}" hidden id="search-filters"><button type="button" class="type-button active" data-kind="all" aria-pressed="true">{T['filter_all']}</button><button type="button" class="type-button" data-kind="guide" aria-pressed="false">{T['filter_guide']}</button><button type="button" class="type-button" data-kind="experiment" aria-pressed="false">{T['filter_experiment']}</button>{news_button}</div>
<div id="section-cards" class="section-cards">{cards}</div>
<div id="search-results" class="entries" hidden aria-live="polite"></div>
<div id="search-index" hidden>{search_index}</div>
<div id="empty" class="empty" hidden>{T['empty']}</div><p><a href="archive/index.html">{T['open_archive']}</a></p></section>
<section id="principles" class="principles"><div class="library-topline"><div><span class="section-number">03 /</span> <h2>{T['principles_title']}</h2></div></div><div class="principle-grid"><div><span class="kind kind-news">{KIND['news']}</span><h3>{T['principle_news_title']}</h3><p>{T['principle_news']}</p></div><div><span class="kind kind-guide">{KIND['guide']}</span><h3>{T['principle_guide_title']}</h3><p>{T['principle_guide']}</p></div><div><span class="kind kind-experiment">{KIND['experiment']}</span><h3>{T['principle_experiment_title']}</h3><p>{T['principle_experiment']}</p></div></div>{summary_visual}</section>
{news_home_block(news_records, today) if news_records else ''}
<section id="about" class="about"><div><span class="side-label">{T['about_label']}</span><h2>{T['about_title']}</h2></div><div><p>{T['about_1']}</p><p class="muted">{T['about_2']}</p><p class="muted">{T['about_3']}</p></div></section></section>'''
    write('index.html', shell(T['nav_catalogue'], home, sidebar=sidebar))
    for name, items, n in groups:
        if n:
            section_page(name, slugify(name), items, today, summary_visual)
    if news_records:
        news_page(news_records, today)
        news_archive(news_records, today)
    ledger = []
    for a in articles:
        status = lifecycle(a, today)
        visual = a['_figure']
        review_meta = f'<div>{T["meta_reviewed"]}<strong>{when(a.get("reviewed"))}</strong></div>' if a['type']=='guide' else ''
        metadata = f'''<div class="article-metadata"><div>{T['meta_published']}<strong>{when(a.get('published'))}</strong></div><div>{T['meta_edited']}<strong>{when(a.get('edited'))}</strong></div>{review_meta}<div>{T['meta_expires'] if a['type']=='news' else T['meta_next']}<strong>{when(status['due'])}</strong></div></div>'''
        paragraphs = glossary.link_terms(a['_body'], gloss, '../glossaire/index.html') if (gloss and a['_body'] is not None) else a['_body'] if a['_body'] is not None else ''.join('<section><h2>'+esc(s['title'])+'</h2>'+''.join('<p>'+esc(p)+'</p>' for p in s['paragraphs'])+'</section>' for s in a['sections'])
        if a['_figure_in_body']:
            visual = ''
        notice = T['notice_' + a['type']]
        if is_draft(a):
            notice = T['notice_draft']
        notice += '</p><p>' + esc(T['notice_all'])  # on every article, drafts included
        history = f'<details><summary>{T["history"]}</summary><ul>'+''.join('<li>'+day(r['date'])+' — '+esc(r['note'])+'</li>' for r in a['history'])+'</ul></details>'
        lang_attr = '' if a.get('lang') == 'fr' else ' lang="en"'  # entries not yet rewritten are still English text
        body = f'''<article class="public-article"{lang_attr}><a href="../index.html">{T['crumb_catalogue']}</a><div class="entry-kicker"><span class="kind kind-{a['type']}">{KIND[a['type']]}</span><a href="../sections/{section_slug(a)}/index.html">{esc(section_name(a))}</a></div><h1>{esc(a['title'])}</h1><p class="article-deck">{esc(a['summary'])}</p>{metadata}<div class="article-notice"><span class="status status-{status['class']}">{status['status']}</span><p>{notice}</p></div>{visual}<div class="reader-body">{paragraphs}{history}</div></article>'''
        write(a['slug']+'/index.html', shell(a['title'], body, '../', a['summary']))
        ledger.append({'slug':a['slug'],'title':a['title'],'content_type':a['type'],
                       'published':a.get('published'),'last_reviewed':a.get('reviewed'),'tested':a.get('tested'),
                       'action':status['action'],'due':status['due'],'status':status['status'],
                       'path':'../'+a['slug']+'/index.html'})
    review_visual = flow(T['ledger_visual_title'], T['ledger_visual_nodes'], T['ledger_visual_details'], T['ledger_visual_caption'])
    rows=''.join(f'<li><a href="{esc(r["path"])}">{esc(r["title"])}</a><p>{T["ledger_row"].format(action=esc(r["action"]), due=when(r["due"]), status=esc(r["status"]))}</p></li>' for r in sorted(ledger,key=lambda r:r['due'] or '9999'))
    ledger_page = f'<div class="eyebrow">{T["ledger_eyebrow"]}</div><h1>{T["ledger_title"]}</h1><p class="intro">{esc(T["ledger_intro"].format(date=day(today)))}</p>{review_visual}<h2>{T["ledger_queue"]}</h2><ol class="review-queue">{rows}</ol><p><a href="ledger.json">{T["ledger_download"]}</a></p>'
    write('maintenance/index.html',shell(T['ledger_title_short'],ledger_page,'../'))
    write('maintenance/ledger.json',json.dumps({'computed_on':today.isoformat(),'items':ledger},indent=2,ensure_ascii=False)+'\n')
    archive=[a for a in articles if is_outdated(a,today)]
    archive_visual=flow(T['archive_visual_title'],T['archive_visual_nodes'],T['archive_visual_details'],T['archive_visual_caption'])
    archive_body=f'<h1>{T["archive_title"]}</h1><p class="intro">{T["archive_intro"]}</p>'+archive_visual
    archive_body+=''.join(entry(a,today,'../') for a in archive) if archive else f'<h2>{T["archive_policy"]}</h2><p>'+T['archive_none'].format(date=day(plus_months('2026-11-25',3)))+'</p>'
    write('archive/index.html',shell(T['archive_title'],archive_body,'../'))
    write('catalogue.json',json.dumps({'as_of':today.isoformat(),'release_marker':catalogue['release_marker'],'articles':[{k:a.get(k) for k in ['slug','title','section','type','published','summary','formats']} for a in articles]},indent=2,ensure_ascii=False)+'\n')
    write('404.html',shell(T['notfound_title'],f'<h1>{T["notfound_h1"]}</h1>'+summary_visual+f'<p><a href="./index.html">{T["open_catalogue"]}</a></p>'))
    for gone in catalogue.get('retired', []):
        write(gone['slug']+'/index.html', shell(T['retired_title'], f'<h1>{T["retired_h1"]}</h1><p>{esc(gone["note"])}</p>'+summary_visual+f'<p><a href="../index.html">{T["open_catalogue"]}</a></p>', '../'))
    if gloss:
        uses = {e['slug']: [(a['slug'], a['title']) for a in articles if any(e['regex'].search(x) for x in texts[a['slug']])] for e in gloss}
        if news_records:
            for e in gloss:
                if any(e['regex'].search(x) for x in texts['__news__']):
                    uses[e['slug']].append(('nouvelles', T['news_title_short']))
        gloss_visual = flow(T['glossary_visual_title'], T['glossary_visual_nodes'], T['glossary_visual_details'], T['glossary_visual_caption'])
        gloss_body = f'<h1>{T["glossary_title"]}</h1><p class="intro">{T["glossary_intro"]}</p>{gloss_visual}' + glossary.render_entries(gloss, uses, '../')
        write('glossaire/index.html', shell(T['glossary_title'], gloss_body, '../'))
        glossary.check_links({str(p): p.read_text() for p in out.rglob('*.html')}, {e['slug'] for e in gloss})
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
