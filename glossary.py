"""Public glossary: parse content/glossaire.md, link the first use of each term in an article, check coverage.

File format (one block per key term, the heading is the English term shown to readers):

    ## KV cache
    match: KV caches?            (optional regex; default: the heading plus an optional final s)
    Two or three plain French sentences.

Standard library only.
"""
import re

from render import esc, inline

# Key terms that stay in English on the site (sample spellings). Any of them used in an article needs an entry.
KEY_TERMS = ['KV cache', 'token', 'tokenizer', 'prompt', 'prefill', 'decoding', 'batching', 'attention', 'query', 'key',
             'value', 'KV head', 'embedding', 'logits', 'weights', 'activations', 'quantization', 'dequantization',
             'scale', 'zero-point', 'fine-tuning', 'throughput', 'latency', 'memory bandwidth', 'speculative decoding',
             'code graph', 'agent', 'GPU', 'LLM', 'FP16', 'FP8', 'int4', 'int8', 'bf16']
SKIP_TAGS = {'a', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'code', 'pre', 'figure', 'details', 'summary', 'script', 'style', 'svg'}
VOID = {'br', 'hr', 'img', 'input', 'meta', 'link'}


def slugify(text):
    import unicodedata
    plain = unicodedata.normalize('NFKD', text.lower()).encode('ascii', 'ignore').decode()
    return re.sub(r'[^a-z0-9]+', '-', plain).strip('-')


def term_regex(pattern):
    return re.compile(r'(?<![\w])(?:' + pattern + r')(?![\w])', re.I)


def parse(text):
    """Return a list of {term, slug, pattern, regex, definition}. Raises ValueError on a malformed block."""
    entries, seen = [], set()
    for block in re.split(r'(?m)^## ', text)[1:]:
        head, _, rest = block.partition('\n')
        term = head.strip()
        pattern, lines = None, []
        for line in rest.splitlines():
            m = re.match(r'match:\s*(.+)$', line.strip())
            if m and pattern is None and not lines:
                pattern = m.group(1).strip()
            elif line.strip():
                lines.append(line.strip())
        definition = ' '.join(lines)
        slug = slugify(term)
        if not term or not definition or slug in seen:
            raise ValueError(f'Glossary entry needs a unique term and a definition: {term!r}')
        seen.add(slug)
        pattern = pattern or re.escape(term) + 's?'
        entries.append({'term': term, 'slug': slug, 'pattern': pattern, 'regex': term_regex(pattern), 'definition': definition})
    return entries


def plain(md):
    """Text a reader could meet: markdown with link targets and bare URLs removed."""
    md = re.sub(r'\]\([^)]*\)', ']', md)
    return re.sub(r'https?://\S+', ' ', md)


def link_terms(html_text, entries, href):
    """Link the first use of every entry in this article body. Headings, links, code, figures and details are left alone."""
    linked, depth, out = set(), 0, []
    for part in re.split(r'(<[^>]+>)', html_text):
        if part.startswith('<') and part.endswith('>'):
            name = re.match(r'</?\s*([a-zA-Z0-9]+)', part)
            name = name.group(1).lower() if name else ''
            if name in SKIP_TAGS:
                depth += -1 if part.startswith('</') else 1
            out.append(part)
            continue
        if depth > 0 or not part.strip():
            out.append(part)
            continue
        cands = sorted(((m.start(), m.end(), e) for e in entries if e['slug'] not in linked for m in e['regex'].finditer(part)),
                       key=lambda h: (h[0], -(h[1] - h[0])))
        pos, text = 0, []
        for start, end, e in cands:
            if start < pos or e['slug'] in linked:
                continue  # inside a longer term already linked here (or already linked): this term waits for a later mention
            text.append(part[pos:start])
            text.append(f'<a class="gloss" href="{href}#{e["slug"]}">{part[start:end]}</a>')
            linked.add(e['slug'])
            pos = end
        text.append(part[pos:])
        out.append(''.join(text))
    return ''.join(out)


def used_terms(texts):
    """Which KEY_TERMS appear in these texts (a dict slug -> text)."""
    return [t for t in KEY_TERMS if any(term_regex(re.escape(t) + ('s?' if t[-1].isalpha() else '')).search(x) for x in texts)]


def render_entries(entries, uses, prefix=''):
    """HTML for the glossary page. uses maps entry slug -> list of (slug, title) of articles that use the term."""
    out = []
    for e in entries:
        links = ' · '.join(f'<a href="{prefix}{s}/index.html">{esc(t)}</a>' for s, t in uses.get(e['slug'], []))
        out.append(f'<section class="gloss-entry" id="{e["slug"]}"><h2><a href="#{e["slug"]}">{esc(e["term"])}</a></h2>'
                   f'<p>{inline(e["definition"], [])}</p>' + (f'<p class="gloss-used">Utilisé dans : {links}</p>' if links else '') + '</section>')
    return ''.join(out)


def check_links(pages, anchors):
    """pages: {name: html}. Every link to the glossary must reach an existing entry anchor."""
    for name, page in pages.items():
        for target in re.findall(r'href="[^"#]*glossaire/index\.html#([^"]*)"', page):
            if target not in anchors:
                raise ValueError(f'Broken glossary link in {name}: #{target}')
