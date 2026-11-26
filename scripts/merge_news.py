"""Merge market-news records into content/news/news.json. Standard library only, no LLM.

Public record schema (the only fields ever written to news.json):
    id, date (ISO), vendor, theme, title_fr, text_fr, urls (list of public https URLs)
    source_note (optional): a short, source-attributed note added by editorial review (e.g. the
    source later gave a different explanation); the shared title_fr/text_fr are never edited for this.

Merge rule (same as the French field renaming in inventory.md's daily-update section):
a record with an id already present in news.json is merged by adding any new urls (deduplicated,
order preserved) without touching title_fr/text_fr/date/vendor/theme; a new id is appended. The
file is always rewritten sorted by date descending (newest first), id as the tiebreaker so the
order is stable.

Privacy checks (refuse the whole merge if any record fails):
- every record has every required field, and at least one url;
- every url starts with https:// and is not a private host (PRIVATE_HOSTS below) or a bare IP/
  localhost-style address;
- the forbidden-name scan (same denylist as build.py's PRIVATE_TOKENS) finds nothing in any
  title_fr/text_fr/vendor/theme/url.

--- Daily prep-mate export (merge_prep_mate) ---
prep-mate produces work/news/from-prep-mate.json: {"news": [...], "summary": {...}}, each news item:
    date, title, text (English, verbatim as shared), source_urls, vendor, shared_on (list of dates), status
status is 'shared' (a public link exists, ready to translate and publish) or 'prepared' (no public
link yet, or editorially held back) -- a 'prepared' record is NEVER published; it stays in the
French source file only, for a later export to pick up once it has a public link.

Stable id = first 16 hex chars of SHA-256 of the normalized canonical URL (scheme and 'www.'
stripped, no trailing slash). If the URL's path is a generic platform-wide page (a changelog or
release-notes root with no specific article path), the id basis is 'normalized_url|slugified title'
instead, so two different items sharing a changelog root get different ids.

Matching an export item against the existing French dataset (news-fr.json) is done by URL overlap
(any of its source_urls, normalized, equal to any URL already recorded on an existing item), which
is robust even if the stable id of an older entry was computed by a slightly different historical
rule. A match means the record is already covered: its shared_on dates are added to the existing
entry, and its French title/text are left untouched (an independent review already covers them).
A 'shared' item with no match is new: its title_fr/text_fr must be supplied already translated
(translation happens upstream of this script -- the daily job's own translation step, following the
same no-rewrite, key-terms-in-English rule as the reviewed set) and the record is marked
translated_by_daily_rule=true so a later manual review can sample it.
"""
import hashlib
import json
import re
import sys
from pathlib import Path
from urllib.parse import urlsplit

REQUIRED_FIELDS = ('id', 'date', 'vendor', 'theme', 'title_fr', 'text_fr', 'urls')
PRIVATE_HOSTS = ('teams.microsoft.com', 'sharepoint.com', 'localhost', '127.0.0.1')
FORBIDDEN_NAMES = ('/users/', 'file://')  # case-insensitive; extend here, never in the data itself
ID_RE = re.compile(r'^[0-9a-f]{8,64}$')
DATE_RE = re.compile(r'^\d{4}-\d{2}-\d{2}$')
GENERIC_PATH_NAMES = ('changelog', 'release-notes', 'release-notes/overview', 'releases', 'news', 'blog')


def check_record(record, problems):
    """Append every problem found with this record to problems; does not raise."""
    rid = record.get('id', '?')
    for field in REQUIRED_FIELDS:
        if not record.get(field):
            problems.append(f'{rid}: missing {field}')
    if 'id' in record and not ID_RE.fullmatch(str(record['id'])):
        problems.append(f'{rid}: id must be a lowercase hex string')
    if 'date' in record and record['date'] and not DATE_RE.fullmatch(str(record['date'])):
        problems.append(f'{rid}: date must be ISO (YYYY-MM-DD)')
    urls = record.get('urls') or []
    if not urls:
        problems.append(f'{rid}: no public URL')
    for url in urls:
        if not url.startswith('https://'):
            problems.append(f'{rid}: URL is not https: {url}')
            continue
        host = url[len('https://'):].split('/', 1)[0].split('@')[-1].split(':')[0].lower()
        if host in PRIVATE_HOSTS or re.fullmatch(r'(\d{1,3}\.){3}\d{1,3}', host):
            problems.append(f'{rid}: private or local host in URL')
    haystack = ' '.join([str(record.get(k, '')) for k in ('title_fr', 'text_fr', 'vendor', 'theme')] + urls).lower()
    for token in FORBIDDEN_NAMES:
        if token in haystack:
            problems.append(f'{rid}: forbidden-name scan hit')


def check_all(records):
    problems = []
    seen_ids = set()
    for record in records:
        check_record(record, problems)
        rid = record.get('id')
        if rid in seen_ids:
            problems.append(f'{rid}: duplicate id in the same file')
        seen_ids.add(rid)
    return problems


def load(path):
    p = Path(path)
    return json.loads(p.read_text()) if p.is_file() else []


def normalize_url(url):
    """Scheme and 'www.' stripped, no trailing slash: the canonical form the stable id and the URL-overlap
    match are both computed from."""
    p = urlsplit(url)
    host = (p.hostname or '').lower()
    if host.startswith('www.'):
        host = host[4:]
    return host + p.path.rstrip('/')


def slugify_title(title):
    return re.sub(r'[^a-z0-9]+', '-', title.lower()).strip('-')


def _is_generic_path(url):
    path = urlsplit(url).path.strip('/').lower()
    return path in GENERIC_PATH_NAMES


def stable_id(url, title):
    """16-hex-char id: hash of the normalized URL, or of 'url|slug(title)' when the URL is a generic,
    platform-wide page (so two different announcements sharing one changelog root get different ids)."""
    basis = normalize_url(url) + ('|' + slugify_title(title) if _is_generic_path(url) else '')
    return hashlib.sha256(basis.encode()).hexdigest()[:16]


def find_existing(record_urls, existing):
    """The first existing record (from news-fr.json or news.json) sharing any normalized URL with record_urls, or None."""
    wanted = {normalize_url(u) for u in record_urls}
    for r in existing:
        if wanted & {normalize_url(u) for u in r.get('urls', [])}:
            return r
    return None


def merge_prep_mate(export, existing_fr, translate):
    """export: the {"news": [...]} dict from from-prep-mate.json. existing_fr: news-fr.json's record
    list (title_fr/text_fr already reviewed). translate(item) -> (title_fr, text_fr) for a NEW 'shared'
    item with no match; called only for those. Returns (updated_fr, held_back_prepared, stats) where
    updated_fr is existing_fr plus any new shared records (with shared_on merged into matches), and
    held_back_prepared lists every 'prepared' item that is not already covered by an existing record
    (never published; the caller keeps them in the private file only)."""
    by_id = {r['id']: r for r in existing_fr}
    stats = {'from_export': len(export['news']), 'matched_existing': 0, 'new_shared_translated': 0, 'prepared_held_back': 0}
    held_back = []
    for item in export['news']:
        hit = find_existing(item['source_urls'], existing_fr)
        if hit:
            stats['matched_existing'] += 1
            seen = set(hit.get('shared_on', [hit.get('shared_date', hit.get('date'))]))
            hit['shared_on'] = sorted(seen | set(item.get('shared_on', [])))
            continue
        if item['status'] != 'shared':
            stats['prepared_held_back'] += 1
            held_back.append(item)
            continue
        title_fr, text_fr = translate(item)
        new_id = stable_id(item['source_urls'][0], item['title'])
        by_id[new_id] = {
            'id': new_id, 'date': item['date'], 'shared_date': item.get('shared_on', [item['date']])[0],
            'vendor': item['vendor'], 'theme': item.get('theme', ''), 'theme_original': item.get('theme', ''),
            'title_fr': title_fr, 'text_fr': text_fr, 'title_en': item['title'], 'text_en': item['text'],
            'urls': item['source_urls'], 'shared_on': item.get('shared_on', []), 'date_outside_window': False,
            'translated_by_daily_rule': True,
        }
        stats['new_shared_translated'] += 1
    return list(by_id.values()), held_back, stats


def merge(existing, incoming):
    """Merge incoming records into existing by id (urls deduplicated and extended; other fields untouched
    for an id already present); return the merged list, newest first."""
    by_id = {r['id']: dict(r) for r in existing}
    for record in incoming:
        rid = record['id']
        if rid in by_id:
            seen = list(by_id[rid]['urls'])
            for url in record['urls']:
                if url not in seen:
                    seen.append(url)
            by_id[rid]['urls'] = seen
        else:
            by_id[rid] = dict(record)
    return sorted(by_id.values(), key=lambda r: (r['date'], r['id']), reverse=True)


def main():
    if len(sys.argv) != 3:
        print('usage: merge_news.py <incoming.json> <content/news/news.json>', file=sys.stderr)
        return 2
    incoming_path, news_path = sys.argv[1], sys.argv[2]
    incoming = load(incoming_path)
    problems = check_all(incoming)
    if problems:
        print('Refused: ' + '; '.join(problems), file=sys.stderr)
        return 1
    existing = load(news_path)
    merged = merge(existing, incoming)
    problems = check_all(merged)
    if problems:
        print('Refused (post-merge): ' + '; '.join(problems), file=sys.stderr)
        return 1
    Path(news_path).parent.mkdir(parents=True, exist_ok=True)
    Path(news_path).write_text(json.dumps(merged, indent=2, ensure_ascii=False) + '\n')
    print(f'{news_path}: {len(merged)} records ({len(incoming)} merged in)')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
