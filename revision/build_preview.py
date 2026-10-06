#!/usr/bin/env python3
"""Build a reading preview (HTML, MathJax) of the rewritten Introduction.

Inputs (all in the repository):
  revision/NEW_INTRODUCTION.tex          -- the new Introduction, LaTeX
  "Audit 3 ... .zip" -> JOINT_Paper_Package/manuscript/FINAL_SUBMISSION.bbl
                                         -- the reordered bibliography (read from
                                            the package archive, no unzipping)
Output:
  revision/NEW_INTRODUCTION_preview.html
"""
import re
import pathlib
import zipfile
import html as htmllib

ROOT = pathlib.Path(__file__).resolve().parent.parent
INTRO = ROOT / 'revision' / 'NEW_INTRODUCTION.tex'
ZIP = ROOT / 'Audit 3 JOINT_Paper_Source_and_Supplementary_Files.zip'
BBL_MEMBER = 'JOINT_Paper_Package/manuscript/FINAL_SUBMISSION.bbl'
OUT = ROOT / 'revision' / 'NEW_INTRODUCTION_preview.html'

# ---------------------------------------------------------------- bibliography
with zipfile.ZipFile(ZIP) as zf:
    bbl_text = zf.read(BBL_MEMBER).decode('utf-8')
entries = {}
order = re.findall(r'\\bibitem\[[^\]]*\]\{([^}]+)\}', bbl_text)
blocks = re.split(r'^%%%\s*\d+\s*$', bbl_text, flags=re.M)[1:]
for key, block in zip(order, blocks):
    entries[key] = block
number = {k: i + 1 for i, k in enumerate(order)}


def braced(s: str, cmd: str):
    """Contents of all \\cmd{...} occurrences, with balanced braces."""
    out = []
    start = 0
    needle = '\\' + cmd + '{'
    while True:
        i = s.find(needle, start)
        if i < 0:
            return out
        j = i + len(needle)
        depth, buf = 1, []
        while j < len(s) and depth:
            c = s[j]
            if c == '{':
                depth += 1
            elif c == '}':
                depth -= 1
                if depth == 0:
                    break
            buf.append(c)
            j += 1
        out.append(''.join(buf))
        start = j + 1


ACCENTS = {
    "\\'": '', '\\`': '', '\\^': '', '\\"': '', '\\~': '', '\\=': '', '\\.': '',
    '\\u': '', '\\v': '', '\\H': '', '\\c': '', '\\d': '', '\\b': '', '\\t': '',
    '\\k': '', '\\r': '',
}


def strip_tex(s: str) -> str:
    s = s.replace('\\i', 'i').replace('\\j', 'j').replace('\\ss', 'ss')
    # accent groups such as {\'i}, {\u a}, {\c c}
    s = re.sub(r'\{\\([a-zA-Z\'`^~=."ubvHcdtkrs])\s*([a-zA-Z])\}', r'\2', s)
    s = re.sub(r'\{\\[a-zA-Z\'`^~=."]+\}', '', s)
    s = re.sub(r'\\([a-zA-Z\'`^~=."])\s*([a-zA-Z])',
               lambda m: m.group(2) if m.group(1) in ACCENTS or m.group(1) == "'" else m.group(0), s)
    s = re.sub(r'\\bsnm\{([^{}]*)\}', r'\1', s)
    s = re.sub(r'\\binits\{([^{}]*)\}', r'\1', s)
    s = re.sub(r'\\betal\b', 'et al.', s)
    s = re.sub(r'\\[a-zA-Z]+\*?', ' ', s)
    s = re.sub(r'[{}$]', ' ', s)
    s = re.sub(r'\s+([,.;:])', r'\1', s)
    s = re.sub(r'\s+', ' ', s)
    s = s.replace('..', '.')
    return s.strip()


def first(s: str, cmd: str):
    got = braced(s, cmd)
    return got[0] if got else None


def render_entry(key: str) -> str:
    b = entries[key]
    authors = [strip_tex(a) for a in braced(b, 'bauthor')]
    if len(authors) > 3:
        authors = authors[:3] + ['et al.']
    title = first(b, 'batitle')
    journal = first(b, 'bjtitle')
    volume = first(b, 'bvolume')
    issue = first(b, 'bissue')
    fpage = first(b, 'bfpage')
    lpage = first(b, 'blpage')
    year = first(b, 'byear')
    doi = first(b, 'doiurl')
    entity = first(b, 'bpublisher') or first(b, 'bbtitle')
    parts = []
    if authors:
        names = ', '.join(authors)
        parts.append(names if names.endswith('.') else names + '.')
    if title:
        parts.append(strip_tex(title) + '.')
    venue = strip_tex(journal) if journal else (strip_tex(entity) if entity else '')
    if venue:
        venue += ' ' + (volume or '')
        if issue:
            venue += '(' + issue + ')'
        venue = venue.replace('  ', ' ').strip()
        if fpage:
            venue += ', ' + fpage + ('--' + lpage if lpage else '')
        if year:
            venue += ' (' + year + ')'
        parts.append(venue + '.')
    elif year:
        parts.append('(' + year + ').')
    if doi:
        parts.append('doi:' + doi)
    return ' '.join(parts)


# ---------------------------------------------------------------- the LaTeX
tex = INTRO.read_text(encoding='utf-8')
tex = tex.replace('\\section{Introduction}\\label{sec:intro}', '')
# the TikZ block is shown as an image instead, so drop it here
tex = re.sub(r'\\begin\{figure\}.*?\\end\{figure\}', '', tex, flags=re.S)
tex = re.sub(r'\\label\{[^}]*\}', '', tex)

MATH_NUMBERS = {
    'eq:compat': '(3.2)',
    'lem:factor-selection': '2.2',
    'lem:complete': '2.5',
    'lem:global-code': '2.6',
    'prop:dual-translation': '2.7',
    'lem:ordinary-reciprocal': '3.4',
    'thm:dual-generator': '3.5',
    'thm:hull-support': '3.10',
    'prop:boundary': '3.13',
    'prop:transfer-matrix': '4.2',
    'prop:closed': '4.4',
    'thm:central': '4.6',
    'cor:total': '4.7',
    'cor:conditional-variance': '4.14',
    'sec:setting': '2',
    'sec:duality': '3',
    'sec:enumeration': '4',
    'sec:examples': '5',
    'sec:verification': '5.2',
    'sec:conclusion': '6',
    'fig:pipeline': '1',
}
used_cites = []


def cite_html(keys: str) -> str:
    nums = []
    for k in keys.split(','):
        k = k.strip()
        if k not in used_cites:
            used_cites.append(k)
        nums.append(number[k])
    nums.sort()
    # compress runs
    out, i = [], 0
    while i < len(nums):
        j = i
        while j + 1 < len(nums) and nums[j + 1] == nums[j] + 1:
            j += 1
        out.append(str(nums[i]) if j == i else f'{nums[i]}\u2013{nums[j]}')
        i = j + 1
    body = ','.join(out)
    return f'<span class="cite">[{body}]</span>'


def text_sub(s: str) -> str:
    s = re.sub(r'\\cite\{([^}]*)\}', lambda m: cite_html(m.group(1)), s)
    s = re.sub(r'\\eqref\{([^}]*)\}', lambda m: MATH_NUMBERS.get(m.group(1), '?'), s)
    s = re.sub(r'\\ref\{([^}]*)\}', lambda m: MATH_NUMBERS.get(m.group(1), '?'), s)
    s = re.sub(r'\\emph\{(.*?)\}', r'<em>\1</em>', s, flags=re.S)
    s = s.replace('\\%', '%').replace('\\&', '&amp;').replace('\\_', '_')
    s = s.replace('~', '&nbsp;')
    s = s.replace('\\\\', ' ')
    s = re.sub(r'\\,|\\;|\\ ', ' ', s)
    s = re.sub(r'---', '\u2014', s)
    s = re.sub(r'--', '\u2013', s)
    s = re.sub(r'\\medskip|\\smallskip|\\noindent|\\bigskip', '', s)
    return s


# split into math and non-math parts, escape HTML only outside math
token = re.compile(r'(\$[^$]*\$|\\\[.*?\\\])', re.S)
chunks = []
for part in token.split(tex):
    if not part:
        continue
    if part.startswith('$') or part.startswith('\\['):
        math = part
        if math.startswith('$'):
            math = '\\(' + math[1:-1] + '\\)'
        chunks.append(('math', math))
    else:
        chunks.append(('text', part))

body_parts = []
for kind, part in chunks:
    if kind == 'math':
        body_parts.append(part)
    else:
        body_parts.append(text_sub(htmllib.escape(part, quote=False)))

converted = ''.join(body_parts)

# pull the display formulas out so that they stay intact while paragraphs split
displays = []


def _stash(m):
    displays.append(m.group(0))
    return f'@@DISPLAY{len(displays) - 1}@@'


converted = re.sub(r'\\\[.*?\\\]', _stash, converted, flags=re.S)

paras = [p.strip() for p in re.split(r'\n\s*\n', converted) if p.strip()]
html_paras = []
for p in paras:
    p = re.sub(r'\n+', ' ', p).strip()
    p = re.sub(r'@@DISPLAY(\d+)@@', lambda m: '\x00<div class="display">'
               + displays[int(m.group(1))].replace('\n', ' ') + '</div>\x00', p)
    for piece in [q.strip() for q in p.split('\x00') if q.strip()]:
        if piece.startswith('<div'):
            html_paras.append(piece)
        else:
            html_paras.append(f'<p>{piece}</p>')

refs = []
for k in used_cites:
    refs.append(f'<li id="ref{number[k]}"><span class="num">[{number[k]}]</span> {render_entry(k)}</li>')

html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Joint Code-Dimension and k-Galois-Hull Enumerators — Introduction (revised)</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<script>
window.MathJax = {{
  tex: {{
    inlineMath: [['$','$'],['\\\\(','\\\\)']],
    displayMath: [['\\\\[','\\\\]'],['$$','$$']],
    macros: {{
      A: '\\\\mathcal{{A}}', K: '\\\\mathbb{{K}}', F: '\\\\mathbb{{F}}',
      Fs: '\\\\mathcal{{F}}_s', Os: '\\\\mathcal{{O}}_s', Epoly: '\\\\mathscr{{E}}',
      Hull: '\\\\operatorname{{Hull}}', perpE: '{{\\\\perp_E}}', Dk: 'D_k',
      rank: '\\\\operatorname{{rank}}', wt: '\\\\operatorname{{wt}}',
      texorpdfstring: ['#1', 2]
    }}
  }},
  chtml: {{ scale: 1.0 }}
}};
</script>
<script id="mj" src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js" async></script>
<script>
// fallback CDN if jsDelivr is unreachable
setTimeout(function () {{
  if (!window.MathJax || !window.MathJax.startup) {{
    var s = document.createElement('script');
    s.src = 'https://unpkg.com/mathjax@3/es5/tex-mml-chtml.js';
    s.async = true;
    document.head.appendChild(s);
  }}
}}, 4000);
</script>
<style>
  :root {{ --ink:#1a1a1a; --muted:#5b6470; --rule:#d8dde3; --link:#1a4f9c; }}
  html {{ background:#f4f5f7; }}
  body {{ margin:0; padding:28px 12px 60px; font-family:"Latin Modern Roman",Georgia,"Times New Roman",serif;
         color:var(--ink); line-height:1.52; }}
  main {{ max-width:760px; margin:0 auto; background:#fff; padding:44px 52px 56px; border:1px solid var(--rule);
          box-shadow:0 1px 3px rgba(20,30,50,.08); }}
  .kicker {{ font-family:ui-sans-serif,system-ui,"Segoe UI",Helvetica,Arial,sans-serif; font-size:12.5px;
             letter-spacing:.09em; text-transform:uppercase; color:var(--muted); margin:0 0 6px; }}
  h1 {{ font-size:1.55rem; margin:0 0 4px; font-weight:700; }}
  .subtitle {{ font-family:ui-sans-serif,system-ui,"Segoe UI",Helvetica,Arial,sans-serif; font-size:13px;
               color:var(--muted); margin:0 0 22px; }}
  h2 {{ font-size:1.05rem; margin:34px 0 10px; }}
  p {{ margin:0 0 13px; text-align:justify; hyphens:auto; }}
  .display {{ margin:14px 0 16px; overflow-x:auto; text-align:center; }}
  .cite {{ color:var(--link); font-size:.85em; vertical-align:.12em; white-space:nowrap; }}
  figure {{ margin:22px 0 6px; }}
  figure img {{ width:100%; border:1px solid var(--rule); padding:10px; background:#fff; }}
  figcaption {{ font-size:.9rem; color:var(--muted); margin-top:8px; }}
  ol.refs {{ list-style:none; margin:0; padding:0; font-size:.92rem; }}
  ol.refs li {{ margin:0 0 9px; padding-left:2.6em; text-indent:-2.6em; line-height:1.45; }}
  .num {{ color:var(--link); }}
  .note {{ font-family:ui-sans-serif,system-ui,"Segoe UI",Helvetica,Arial,sans-serif; font-size:12.5px;
           color:var(--muted); background:#f7f9fb; border:1px solid var(--rule); border-radius:6px;
           padding:10px 13px; margin:0 0 26px; }}
  .note b {{ color:var(--ink); }}
  hr {{ border:0; border-top:1px solid var(--rule); margin:34px 0 22px; }}
</style>
</head>
<body>
<main>
  <p class="kicker">Joint Code-Dimension and k-Galois-Hull Enumerators for Simple-Root Constacyclic Codes over Square-Free Affine Algebras</p>
  <h1>Introduction &mdash; revised version</h1>
  <p class="subtitle">Reading preview of the rewritten Section&nbsp;1. Mathematics rendered by MathJax; cross-reference numbers are
     those of the current build (unchanged by the revision).</p>

  <p class="note"><b>What this is.</b> The LaTeX source of the paper is
     <code>manuscript/FINAL_SUBMISSION.tex</code>; this page is only a convenient way to read the new Introduction without
     compiling. The display formula and the (i)&ndash;(iv) list are typeset here as separate blocks for legibility; in the
     compiled paper they follow the manuscript layout. Figure&nbsp;1 is the unchanged TikZ figure, taken from the existing
     PDF build.</p>

  {''.join(html_paras)}

  <figure>
    <img src="figure1_workflow.png" alt="Workflow of the paper">
    <figcaption><b>Fig. 1.</b> The workflow of the paper: from the CRT decomposition of the affine algebra to the one-orbit
    polynomial and the global joint enumerator, with the consequences and the validation at the end. (Figure text as in the
    manuscript; unaltered by this revision.)</figcaption>
  </figure>

  <hr>
  <h2>References cited in the Introduction</h2>
  <ol class="refs">
    {''.join(refs)}
  </ol>
</main>
</body>
</html>
"""
OUT.write_text(html, encoding='utf-8')
print('written', OUT, len(html.encode()), 'bytes')
print('citations used in the intro:', len(used_cites))
missing = [k for k in used_cites if k not in entries]
print('missing bbl entries:', missing)
