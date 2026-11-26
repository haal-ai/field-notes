"""Market news: load content/news/news.json, check it, and render the /nouvelles/ page, its
day-grouped list, the home 'Dernières nouvelles' block, a small bar chart, and the by-month archive.

Record schema (public fields only, see scripts/merge_news.py): id, date, vendor, theme, title_fr,
text_fr, urls. Standard library only.
"""
import re
from collections import OrderedDict
from datetime import date, timedelta
from urllib.parse import urlsplit

from render import esc

PRIVATE_HOSTS = ('teams.microsoft.com', 'sharepoint.com', 'localhost', '127.0.0.1')
FORBIDDEN_NAMES = ('/users/', 'file://')
WINDOW_DAYS = 28  # four weeks

THEME_COLORS = {
    'Sécurité': '#c0604a', 'Outils et agents': '#146b5c', 'Modèles': '#555084', 'Business': '#785413',
    'Infrastructure et inférence': '#2f6fa6', 'Cloud et plateformes': '#5a7a2e', 'Recherche et benchmarks': '#8a4b8f',
}
THEME_ORDER = list(THEME_COLORS)


def check(records):
    """Problems with this record list: missing field, no public https URL, a private host, or a forbidden-name hit.
    Does not raise; the caller decides what to do with a non-empty list."""
    problems = []
    seen = set()
    for r in records:
        rid = r.get('id', '?')
        for field in ('id', 'date', 'vendor', 'theme', 'title_fr', 'text_fr', 'urls'):
            if not r.get(field):
                problems.append(f'{rid}: missing {field}')
        if rid in seen:
            problems.append(f'{rid}: duplicate id')
        seen.add(rid)
        urls = r.get('urls') or []
        if not urls:
            problems.append(f'{rid}: no public URL')
        for url in urls:
            if not url.startswith('https://'):
                problems.append(f'{rid}: URL is not https: {url}')
                continue
            host = urlsplit(url).hostname or ''
            if host.lower() in PRIVATE_HOSTS or re.fullmatch(r'(\d{1,3}\.){3}\d{1,3}', host):
                problems.append(f'{rid}: private or local host in URL')
        haystack = ' '.join([str(r.get(k, '')) for k in ('title_fr', 'text_fr', 'vendor', 'theme')] + urls).lower()
        for token in FORBIDDEN_NAMES:
            if token in haystack:
                problems.append(f'{rid}: forbidden-name scan hit')
    return problems


def domain(url):
    host = urlsplit(url).hostname or url
    return host[4:] if host.startswith('www.') else host


def source_url(record):
    return record['urls'][0]


def in_window(record, today):
    d = date.fromisoformat(record['date'])
    return (today - d).days < WINDOW_DAYS and d <= today


def sorted_desc(records):
    return sorted(records, key=lambda r: (r['date'], r['id']), reverse=True)


def by_day(records):
    """OrderedDict of ISO date -> records, newest day first, records within a day in the given order."""
    out = OrderedDict()
    for r in records:
        out.setdefault(r['date'], []).append(r)
    return out


def card(record, prefix=''):
    url = source_url(record)
    note = (f'<p class="news-source-note">{esc(record["source_note"])}</p>' if record.get('source_note') else '')
    return (f'<article class="news-card" data-theme="{esc(_slug(record["theme"]))}">'
            f'<div class="news-card-head"><span class="news-theme news-theme-{esc(_slug(record["theme"]))}">{esc(record["theme"])}</span>'
            f'<span class="news-vendor">{esc(record["vendor"])}</span></div>'
            f'<h3><a href="{esc(url)}">{esc(record["title_fr"])}</a></h3>'
            f'<p class="news-text">{esc(record["text_fr"])}</p>{note}'
            f'<p class="news-meta"><span class="news-domain">{esc(domain(url))}</span> · <span>Nouvelle partagée</span></p></article>')


def _slug(text):
    import unicodedata
    plain = unicodedata.normalize('NFKD', text.lower()).encode('ascii', 'ignore').decode()
    return re.sub(r'[^a-z0-9]+', '-', plain).strip('-')


def day_section(iso_date, day_label, records, prefix=''):
    return (f'<section class="news-day" aria-labelledby="day-{iso_date}"><h2 id="day-{iso_date}" class="news-day-heading">{esc(day_label)}</h2>'
            f'{"".join(card(r, prefix) for r in records)}</section>')


def theme_chips(records, filter_aria):
    counts = OrderedDict()
    for r in records:
        counts[r['theme']] = counts.get(r['theme'], 0) + 1
    chips = ''.join(
        f'<button type="button" class="type-button news-chip" data-theme="{esc(_slug(t))}" aria-pressed="false">{esc(t)} <span class="mono">{n:02d}</span></button>'
        for t, n in counts.items())
    return (f'<div class="filter-row js-only" role="group" aria-label="{esc(filter_aria)}">'
            f'<button type="button" class="type-button news-chip active" data-theme="all" aria-pressed="true">Tous les thèmes</button>{chips}</div>')


def chart_svg(records, today, caption_fn):
    """A stacked weekly bar chart (4 weeks, newest week on the right), one bar segment per theme, with a title/desc
    and a caption built by caption_fn(weeks) where weeks is [(label, {theme: count})], oldest week first."""
    weeks = []
    for w in range(3, -1, -1):
        start = today - timedelta(days=today.weekday() + 7 * w)
        end = start + timedelta(days=6)
        counts = OrderedDict()
        for r in records:
            d = date.fromisoformat(r['date'])
            if start <= d <= end:
                counts[r['theme']] = counts.get(r['theme'], 0) + 1
        label = f'{start.day:02d}/{start.month:02d}'
        weeks.append((label, counts))
    total_max = max((sum(c.values()) for _, c in weeks), default=1) or 1
    width, height, bar_w, gap, top_pad = 390, 220, 64, 22, 20
    chart_h = height - 60
    svg = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" role="img" '
           f'aria-labelledby="news-chart-title news-chart-desc" font-family="Inter,ui-sans-serif,system-ui,sans-serif">']
    svg.append('<title id="news-chart-title">Nouvelles par semaine, quatre dernières semaines</title>')
    desc_bits = '; '.join(f'{lbl} : {sum(c.values())}' for lbl, c in weeks)
    svg.append(f'<desc id="news-chart-desc">Nombre de nouvelles par semaine, empilées par thème. {esc(desc_bits)}.</desc>')
    svg.append(f'<rect width="{width}" height="{height}" fill="var(--bg,#f7f9fa)"/>')
    for i, (label, counts) in enumerate(weeks):
        x = 20 + i * (bar_w + gap)
        y = top_pad
        for theme in THEME_ORDER:
            n = counts.get(theme, 0)
            if not n:
                continue
            seg_h = (n / total_max) * chart_h
            svg.append(f'<rect x="{x}" y="{y}" width="{bar_w}" height="{seg_h:.1f}" fill="{THEME_COLORS[theme]}"/>')
            y += seg_h
        total = sum(counts.values())
        svg.append(f'<text x="{x + bar_w / 2}" y="{top_pad + chart_h + 18}" text-anchor="middle" fill="var(--text,#152a34)" font-size="12">{esc(label)}</text>')
        svg.append(f'<text x="{x + bar_w / 2}" y="{top_pad - 6}" text-anchor="middle" fill="var(--muted,#506571)" font-size="12">{total}</text>')
    legend_x = 20
    for theme in THEME_ORDER:
        if not any(theme in c for _, c in weeks):
            continue
        svg.append(f'<rect x="{legend_x}" y="{height - 16}" width="9" height="9" fill="{THEME_COLORS[theme]}"/>')
        legend_x += 11
    svg.append('</svg>')
    caption = caption_fn(weeks)
    return ''.join(svg), caption


def chart_caption(weeks):
    total = sum(sum(c.values()) for _, c in weeks)
    return (f'Nombre de nouvelles par semaine sur les quatre dernières semaines (semaine du lundi indiqué), '
            f'empilées par thème. {total} nouvelles au total sur la période.')


def chart_text_equivalent(weeks):
    lines = ['<ul>']
    for label, counts in weeks:
        parts = ', '.join(f'{t} : {n}' for t, n in counts.items())
        total = sum(counts.values())
        noun = 'nouvelle' if total == 1 else 'nouvelles'
        lines.append(f'<li>Semaine du {esc(label)} : {total} {noun} ({esc(parts)}).</li>' if parts
                      else f'<li>Semaine du {esc(label)} : aucune nouvelle.</li>')
    lines.append('</ul>')
    return ''.join(lines)


def month_key(iso_date):
    return iso_date[:7]  # YYYY-MM


def month_label(key):
    from strings_fr import MONTHS
    y, m = key.split('-')
    return f'{MONTHS[int(m) - 1]} {y}'
