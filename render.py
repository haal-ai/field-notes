"""Markdown subset and inline-SVG helpers for the field-notes generator. Standard library only."""
import html
import re

LEFTOVERS = re.compile(r'placeholder|\bTBD\b|caption \(draft\)|not approved|status: draft', re.I)


def esc(value):
    return html.escape(str(value), quote=True)


# ---------- markdown subset ----------

def inline(text, warnings):
    """Escape, then apply code spans, links, bare URLs, bold and italic."""
    codes = []

    def stash(m):
        codes.append('<code>' + esc(m.group(1)) + '</code>')
        return f'\x00{len(codes) - 1}\x00'

    text = re.sub(r'`([^`]+)`', stash, text)
    text = esc(text)
    if '![' in text:
        warnings.append('image syntax is only allowed as the figure marker line')

    def link(m):
        label, url = m.group(1), html.unescape(m.group(2))
        if not re.match(r'(https?://|mailto:|#)', url):
            warnings.append(f'link with unsupported target left as text: {url}')
            return m.group(0)
        return f'<a href="{esc(url)}">{label}</a>'

    text = re.sub(r'\[([^\]]+)\]\(([^)\s]+)\)', link, text)
    text = re.sub(r'(?<![">=/\w])(https?://[^\s<)]+[^\s<).,;:])', r'<a href="\1">\1</a>', text)
    text = re.sub(r'\*\*(?=\S)(.+?)(?<=\S)\*\*', r'<strong>\1</strong>', text)
    text = re.sub(r'(?<![\w*])\*(?=[^\s*])(.+?)(?<=[^\s*])\*(?![\w*])', r'<em>\1</em>', text)
    return re.sub(r'\x00(\d+)\x00', lambda m: codes[int(m.group(1))], text)


def markdown(text, figure_file=None, figure_html='', warnings=None, skip_title=True):
    """Render headings, paragraphs, lists, tables, quotes, code, links and one figure marker.

    The first '# ' heading is the page title and is dropped. A line holding only
    ![...](figure_file) marks where the figure goes. Returns (html, figure_used).
    """
    warnings = warnings if warnings is not None else []
    text = re.sub(r'<!--.*?-->', '', text, flags=re.S)
    lines, out, i, used = text.splitlines(), [], 0, False
    title_seen = not skip_title

    def starts_block(line):
        return bool(re.match(r'(#{1,4} |[-*] |\d+\. |> |\||```|!\[)', line))

    while i < len(lines):
        line = lines[i].rstrip()
        if not line.strip():
            i += 1
        elif line.startswith('```'):
            i += 1
            code = []
            while i < len(lines) and not lines[i].startswith('```'):
                code.append(lines[i])
                i += 1
            i += 1
            out.append('<pre><code>' + esc('\n'.join(code)) + '</code></pre>')
        elif re.match(r'#{1,4} ', line):
            level = len(line) - len(line.lstrip('#'))
            body = line[level + 1:].strip()
            i += 1
            if level == 1 and not title_seen:
                title_seen = True
                continue
            level = max(level, 2)
            out.append(f'<h{level}>{inline(body, warnings)}</h{level}>')
        elif figure_file and re.fullmatch(r'!\[[^\]]*\]\(' + re.escape(figure_file) + r'\)', line.strip()):
            if used:
                warnings.append('more than one figure marker')
            else:
                out.append(figure_html)
            used = True
            i += 1
        elif line.startswith('|'):
            rows = []
            while i < len(lines) and lines[i].startswith('|'):
                rows.append([c.strip() for c in lines[i].strip().strip('|').split('|')])
                i += 1
            head, body = rows[0], [r for r in rows[1:] if not all(re.fullmatch(r':?-{3,}:?', c) for c in r)]
            out.append('<table><thead><tr>' + ''.join(f'<th>{inline(c, warnings)}</th>' for c in head) + '</tr></thead><tbody>'
                       + ''.join('<tr>' + ''.join(f'<td>{inline(c, warnings)}</td>' for c in r) + '</tr>' for r in body)
                       + '</tbody></table>')
        elif re.match(r'([-*]|\d+\.) ', line):
            tag = 'ol' if line[0].isdigit() else 'ul'
            items = []
            while i < len(lines) and re.match(r'([-*]|\d+\.) ', lines[i]):
                items.append(re.sub(r'^([-*]|\d+\.) ', '', lines[i]).strip())
                i += 1
            out.append(f'<{tag}>' + ''.join(f'<li>{inline(t, warnings)}</li>' for t in items) + f'</{tag}>')
        elif line.startswith('>'):
            quote = []
            while i < len(lines) and lines[i].startswith('>'):
                quote.append(lines[i].lstrip('>').strip())
                i += 1
            out.append('<blockquote><p>' + inline(' '.join(q for q in quote if q), warnings) + '</p></blockquote>')
        else:
            para = [line.strip()]
            i += 1
            while i < len(lines) and lines[i].strip() and not starts_block(lines[i]):
                para.append(lines[i].strip())
                i += 1
            out.append('<p>' + inline(' '.join(para), warnings) + '</p>')
    return '\n'.join(out), used


def leftovers(text):
    """Return lines that look like unfinished draft text."""
    visible = re.sub(r'<!--.*?-->', '', text, flags=re.S)  # comments are never rendered
    return [l.strip()[:80] for l in visible.splitlines() if LEFTOVERS.search(l)]


# ---------- inline SVG ----------

def _scope_selector(sel, scope):
    sel = sel.strip()
    if re.match(r'svg(?![\w-])', sel):
        return '#' + scope + sel[3:]
    if re.match(r'\.fig(?![\w-])', sel):
        return '#' + scope + sel[4:]
    return f'#{scope} {sel}'


def scope_css(css, scope):
    """Prefix every selector so a figure's styles cannot leak onto the page (or the reverse)."""
    css = re.sub(r'/\*.*?\*/', '', css, flags=re.S)
    out, i = [], 0
    while True:
        j = css.find('{', i)
        if j < 0:
            return ''.join(out)
        head = css[i:j].strip()
        if head.startswith('@'):
            depth, k = 1, j + 1
            while depth:
                depth += (css[k] == '{') - (css[k] == '}')
                k += 1
            out.append(f'{head}{{{scope_css(css[j + 1:k - 1], scope)}}}')
        else:
            k = css.index('}', j) + 1
            out.append(','.join(_scope_selector(s, scope) for s in head.split(',')) + css[j:k])
        i = k


def inline_svg(raw, slug):
    """Validate an authored SVG and return markup safe to embed inline, with scoped styles and ids."""
    svg = re.sub(r'<\?xml.*?\?>|<!DOCTYPE[^>]*>|<!--.*?-->', '', raw, flags=re.S).strip()
    root = re.match(r'<svg\b[^>]*>', svg)
    if not root or not svg.endswith('</svg>'):
        raise ValueError(f'{slug}: figure must be a single <svg> element')
    banned = [r'<script', r'<foreignObject', r'<image', r'<iframe', r'\son\w+\s*=', r'javascript:', r'@import',
              r'(?:xlink:)?href\s*=\s*["\'](?!#)', r'url\(\s*["\']?(?!#)']
    for pattern in banned:
        if re.search(pattern, svg, re.I):
            raise ValueError(f'{slug}: figure contains disallowed content ({pattern})')
    head = root.group(0)
    if 'role="img"' not in head or '<title' not in svg:
        raise ValueError(f'{slug}: figure needs role="img" and a <title>')
    box = re.search(r'viewBox="\s*[-\d.]+[ ,]+[-\d.]+[ ,]+([\d.]+)[ ,]+([\d.]+)\s*"', head)
    if not box:
        raise ValueError(f'{slug}: figure needs a viewBox')
    scope = f'fig-{slug}'
    css = ''.join(scope_css(m.group(1), scope) for m in re.finditer(r'<style[^>]*>(.*?)</style>', svg, re.S))
    svg = re.sub(r'<style[^>]*>.*?</style>', '', svg, flags=re.S)
    ids = set(re.findall(r'\sid="([^"]+)"', svg))
    for name in ids:
        svg = svg.replace(f' id="{name}"', f' id="{scope}-{name}"').replace(f'url(#{name})', f'url(#{scope}-{name})')
        svg = svg.replace(f'href="#{name}"', f'href="#{scope}-{name}"')
    svg = re.sub(r'aria-labelledby="([^"]+)"', lambda m: 'aria-labelledby="' + ' '.join(f'{scope}-{t}' for t in m.group(1).split()) + '"', svg)
    head = re.match(r'<svg\b[^>]*>', svg).group(0)
    new_head = head[:-1] + f' id="{scope}" style="max-width:{float(box.group(1)):g}px;margin:0 auto">'
    svg = new_head + (f'<style>{css}</style>' if css else '') + svg[len(head):]
    return svg
