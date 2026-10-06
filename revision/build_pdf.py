#!/usr/bin/env python3
"""Typeset a reading PDF of the rewritten Introduction.

No LaTeX distribution is available in this environment (CTAN and GitHub release
downloads are blocked), so the PDF is built with ReportLab for the page layout
and Matplotlib's mathtext renderer for the mathematics: every formula is
rendered from the LaTeX source in revision/NEW_INTRODUCTION.tex into a
high-resolution transparent image that is placed on the text baseline, using the
ink bounding box of the render to get the exact ascent and descent.

Output: revision/Introduction_revised.pdf
"""
import re
import pathlib
import zipfile
import html as htmllib

import matplotlib
matplotlib.use('Agg')
matplotlib.rcParams['mathtext.fontset'] = 'stix'          # Times-like math
from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import FigureCanvasAgg
from PIL import Image

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_JUSTIFY, TA_CENTER
from reportlab.lib.units import mm
from reportlab.platypus import (BaseDocTemplate, PageTemplate, Frame, Paragraph,
                                Spacer, Image as RLImage, KeepTogether, HRFlowable)

ROOT = pathlib.Path(__file__).resolve().parent.parent
INTRO = ROOT / 'revision' / 'NEW_INTRODUCTION.tex'
ZIP = ROOT / 'Audit 3 JOINT_Paper_Source_and_Supplementary_Files.zip'
BBL_MEMBER = 'JOINT_Paper_Package/manuscript/FINAL_SUBMISSION.bbl'
FIG = ROOT / 'revision' / 'figure1_workflow.png'
OUT = ROOT / 'revision' / 'Introduction_revised.pdf'
CACHE = ROOT / 'revision' / '.math_cache'
CACHE.mkdir(exist_ok=True)

BODY_SIZE = 10.5
LEADING = 14.4
DPI = 700                      # render resolution of the formulas
FIG_W, FIG_H, BASELINE_Y = 12.0, 1.6, 0.35   # inches / figure fraction

MATH_NUMBERS = {               # manuscript \ref numbers -> printed numbers
    'eq:compat': '(3.2)',
    'lem:factor-selection': '2.2', 'lem:complete': '2.5', 'lem:global-code': '2.6',
    'prop:dual-translation': '2.7', 'lem:ordinary-reciprocal': '3.4',
    'thm:dual-generator': '3.5', 'thm:hull-support': '3.10', 'prop:boundary': '3.13',
    'prop:transfer-matrix': '4.2', 'prop:closed': '4.4', 'thm:central': '4.6',
    'cor:total': '4.7', 'cor:conditional-variance': '4.14',
    'sec:setting': '2', 'sec:duality': '3', 'sec:enumeration': '4',
    'sec:examples': '5', 'sec:verification': '5.2', 'sec:conclusion': '6',
    'fig:pipeline': '1',
}

# ----------------------------------------------------------------- references
with zipfile.ZipFile(ZIP) as zf:
    bbl_text = zf.read(BBL_MEMBER).decode('utf-8')
bbl_order = re.findall(r'\\bibitem\[[^\]]*\]\{([^}]+)\}', bbl_text)
bbl_blocks = re.split(r'^%%%\s*\d+\s*$', bbl_text, flags=re.M)[1:]
BBL = dict(zip(bbl_order, bbl_blocks))
NUMBER = {k: i + 1 for i, k in enumerate(bbl_order)}

ACCENTS = {'\\\'', '\\`', '\\^', '\\"', '\\~', '\\=', '\\.', '\\u', '\\v', '\\H',
           '\\c', '\\d', '\\b', '\\t', '\\k', '\\r'}


def braced(s, cmd):
    out, start, needle = [], 0, '\\' + cmd + '{'
    while True:
        i = s.find(needle, start)
        if i < 0:
            return out
        j, depth, buf = i + len(needle), 1, []
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


def strip_tex(s):
    for a, b in [(r'\mathbb{Z}', 'Z'), (r'\mathbb{F}', 'F'), (r'\mathbb{Q}', 'Q'),
                 (r'\mathbb{N}', 'N'), (r'\mathbb{R}', 'R'), (r'\mathbb{C}', 'C')]:
        s = s.replace(a, b)
    s = s.replace('\\i', 'i').replace('\\j', 'j').replace('\\ss', 'ss')
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
    return re.sub(r'\.\.', '.', s).strip()


def first(s, cmd):
    got = braced(s, cmd)
    return got[0] if got else None


def reference_text(key):
    b = BBL[key]
    authors = [strip_tex(a) for a in braced(b, 'bauthor') + braced(b, 'oauthor')]
    if len(authors) > 3:
        authors = authors[:3] + ['et al.']
    parts = []
    if authors:
        names = ', '.join(authors)
        parts.append(names if names.endswith('.') else names + '.')
    title = first(b, 'batitle') or first(b, 'bbtitle')
    if title:
        parts.append(strip_tex(title) + '.')
    edition = first(b, 'bedition')
    if edition:
        parts.append(strip_tex(edition) + ' edn.')
    venue = strip_tex(first(b, 'bjtitle') or '')
    if venue:
        venue += ' ' + (first(b, 'bvolume') or '')
        issue = first(b, 'bissue')
        if issue:
            venue += '(' + issue + ')'
        venue = venue.strip()
        fpage, lpage = first(b, 'bfpage'), first(b, 'blpage')
        if fpage:
            venue += ', ' + fpage + ('--' + lpage if lpage else '')
        year = first(b, 'byear')
        if year:
            venue += ' (' + year + ')'
        parts.append(venue + '.')
    else:
        publisher = first(b, 'bpublisher')
        year = first(b, 'byear')
        tail = []
        if publisher:
            tail.append(strip_tex(publisher))
        if year:
            tail.append('(' + year + ')')
        if tail:
            parts.append(' '.join(tail) + '.')
    doi = first(b, 'doiurl')
    if doi:
        parts.append('doi:' + doi)
    text = htmllib.escape(' '.join(parts))
    # \mathbb{Z}_4 in the .bbl prints as a plain Z here; keep the subscript
    text = re.sub(r'\bZ_(\d+)', r'Z<sub>\1</sub>', text)
    return text


# ----------------------------------------------------------------- mathematics
def convert_math(tex):
    s = tex.strip()
    if s.startswith('\\['):
        s = s[2:-2]
    elif s.startswith('$'):
        s = s[1:-1]
    s = re.sub(r'\s+', ' ', s)
    for a, b in [(r'\operatorname{tr}', r'\mathrm{tr}'), (r'\Epoly', r'\mathcal{E}'),
                 (r'\A', r'\mathcal{A}'), (r'\Os', r'\mathcal{O}_s'),
                 (r'\Fs', r'\mathcal{F}_s'), (r'\Hull', r'\mathrm{Hull}'),
                 (r'\Dk', r'D_k'), (r'\K', r'\mathbb{K}'), (r'\F', r'\mathbb{F}'),
                 (r'\bigl', ''), (r'\bigr', ''), (r'\Bigl', ''), (r'\Bigr', ''),
                 (r'\left', ''), (r'\right', ''), (r'\mathscr{E}', r'\mathcal{E}'),
                 (r'\hspace*', ''), (r'\!', ''), (r'^{\\perp}', r'^{\\bot}')]:
        s = s.replace(a, b)
    return s


_cache_index = {}


def math_image(tex, size=BODY_SIZE):
    """Render one formula; return (path, width_pt, height_pt, depth_pt)."""
    key = (convert_math(tex), round(size, 2))
    if key in _cache_index:
        return _cache_index[key]
    path = CACHE / f'm{abs(hash(key)) % 10**12}.png'
    fig = Figure(figsize=(FIG_W, FIG_H), dpi=DPI)
    FigureCanvasAgg(fig)
    fig.text(0.01, BASELINE_Y, f'${key[0]}$', fontsize=key[1], ha='left',
             va='baseline', color='black')
    fig.savefig(path, dpi=DPI, transparent=True)
    im = Image.open(path)
    bbox = im.getchannel('A').getbbox()
    if bbox is None:                                  # empty formula
        return None
    pad = 2
    x0, y0, x1, y1 = (max(0, bbox[0] - pad), max(0, bbox[1] - pad),
                      min(im.width, bbox[2] + pad), min(im.height, bbox[3] + pad))
    im.crop((x0, y0, x1, y1)).save(path)
    baseline_px = (1.0 - BASELINE_Y) * FIG_H * DPI     # from the top of the figure
    res = (path,
           (x1 - x0) / DPI * 72,                       # width  in points
           (y1 - y0) / DPI * 72,                       # height in points
           max(0.0, (y1 - baseline_px) / DPI * 72))    # descent below baseline
    _cache_index[key] = res
    return res


# ----------------------------------------------------------------- text -> html
def cite_html(keys):
    nums = sorted(NUMBER[k.strip()] for k in keys.split(','))
    out, i = [], 0
    while i < len(nums):
        j = i
        while j + 1 < len(nums) and nums[j + 1] == nums[j] + 1:
            j += 1
        out.append(str(nums[i]) if j == i else f'{nums[i]}&#8211;{nums[j]}')
        i = j + 1
    return '<font color="#14509b">[' + ','.join(out) + ']</font>'


def text_html(s, strip=True):
    s = htmllib.escape(s, quote=False)
    s = re.sub(r'\\cite\{([^}]*)\}', lambda m: cite_html(m.group(1)), s)
    s = re.sub(r'\\eqref\{([^}]*)\}', lambda m: MATH_NUMBERS.get(m.group(1), '?'), s)
    s = re.sub(r'\\ref\{([^}]*)\}', lambda m: MATH_NUMBERS.get(m.group(1), '?'), s)
    s = re.sub(r'\\emph\{(.*?)\}', r'<i>\1</i>', s, flags=re.S)
    s = s.replace('\\%', '%').replace('\\&', '&amp;').replace('\\_', '_')
    s = s.replace('~', '&#160;').replace('\\\\', ' ')
    s = re.sub(r'\\,|\\;|\\ ', ' ', s)
    s = s.replace('---', '&#8212;').replace('--', '&#8211;')
    s = re.sub(r'\s+', ' ', s)
    return s.strip() if strip else s


def inline_html(fragment):
    out = []
    for piece in re.split(r'(\$[^$]*\$)', fragment):
        if not piece:
            continue
        if piece.startswith('$') and piece.endswith('$') and len(piece) > 2:
            img = math_image(piece)
            if img:
                path, w, h, d = img
                valign = -round(d, 2)
                out.append(f'<img src="{path}" width="{w:.2f}" height="{h:.2f}" '
                           f'valign="{valign}"/>')
            else:
                out.append(htmllib.escape(piece.strip('$')))
        else:
            out.append(text_html(piece, strip=False))
    joined = ''.join(out)
    return re.sub(r' +', ' ', joined).strip()


# ----------------------------------------------------------------- the document
def main():
    intro_tex = INTRO.read_text(encoding='utf-8')
    intro_tex = intro_tex.split('\n\n', 1)[1]            # drop the header comment
    intro_tex = re.sub(r'\\section\{Introduction\}\s*(\\label\{[^}]*\})?', '', intro_tex)
    intro_tex = re.sub(r'\\label\{[^}]*\}', '', intro_tex)

    display_tex = None
    m = re.search(r'\\\[(.*?)\\\]', intro_tex, re.S)
    if m:
        display_tex = m.group(0)
        intro_tex = intro_tex.replace(display_tex, '\x00D\x00')

    paragraphs = [p.strip() for p in re.split(r'\n\s*\n', intro_tex) if p.strip()]

    sty = {
        'title': ParagraphStyle('title', fontName='Times-Bold', fontSize=14.5,
                                leading=17.5, alignment=TA_CENTER, spaceAfter=5),
        'author': ParagraphStyle('author', fontName='Times-Roman', fontSize=10.2,
                                 leading=13, alignment=TA_CENTER, spaceAfter=13),
        'h1': ParagraphStyle('h1', fontName='Times-Bold', fontSize=12.4, leading=15,
                             spaceAfter=8),
        'sub': ParagraphStyle('sub', fontName='Times-Italic', fontSize=9.4, leading=12,
                              textColor='#555555', spaceAfter=10),
        'body': ParagraphStyle('body', fontName='Times-Roman', fontSize=BODY_SIZE,
                               leading=LEADING, alignment=TA_JUSTIFY, spaceAfter=8),
        'cap': ParagraphStyle('cap', fontName='Times-Roman', fontSize=9.2, leading=11.8,
                              alignment=TA_JUSTIFY),
        'ref': ParagraphStyle('ref', fontName='Times-Roman', fontSize=9.4, leading=12.2,
                              leftIndent=20, firstLineIndent=-20, spaceAfter=3.6),
        'note': ParagraphStyle('note', fontName='Times-Italic', fontSize=8.8,
                               leading=11.2, textColor='#555555', alignment=TA_JUSTIFY),
    }
    try:                                     # optional, nicer justification
        import pyphen                        # noqa: F401
        sty['body'].hyphenationLang = 'en_GB'
        sty['cap'].hyphenationLang = 'en_GB'
    except Exception:
        pass

    story = [
        Paragraph('Joint Code-Dimension and <i>k</i>-Galois-Hull Enumerators for '
                  'Simple-Root Constacyclic Codes over Square-Free Affine Algebras',
                  sty['title']),
        Paragraph('Arun Kumar Yadav &#183; School of Basic and Applied Sciences, '
                  'K.R. Mangalam University, Gurugram, Haryana, India', sty['author']),
        HRFlowable(width='100%', thickness=0.7, color='#777777', spaceAfter=12),
        Paragraph('1. Introduction', sty['h1']),
        Paragraph('Revised version of Section 1 (Phase 3). The mathematics, the citations and '
                  'the cross-references are those of the manuscript source.', sty['sub']),
    ]

    for para in paragraphs:
        if '\x00D\x00' in para:
            before, after = para.split('\x00D\x00')
            if before.strip():
                story.append(Paragraph(inline_html(before), sty['body']))
            img = math_image(display_tex, size=12)
            if img:
                path, w, h, _ = img
                avail = 155 * mm
                if w > avail:
                    h *= avail / w
                    w = avail
                story += [Spacer(1, 6), RLImage(str(path), width=w, height=h,
                                                hAlign='CENTER'), Spacer(1, 8)]
            if after.strip():
                story.append(Paragraph(inline_html(after), sty['body']))
        else:
            story.append(Paragraph(inline_html(para), sty['body']))

    if FIG.exists():
        iw, ih = Image.open(FIG).size
        width = 148 * mm
        story.append(KeepTogether([
            Spacer(1, 8),
            RLImage(str(FIG), width=width, height=width * ih / iw, hAlign='CENTER'),
            Spacer(1, 6),
            Paragraph('<b>Fig. 1.</b> The workflow of the paper: from the CRT decomposition of '
                      'the affine algebra to the one-orbit polynomial and the global joint '
                      'enumerator, with the consequences of the enumeration and the validation '
                      'at the end.', sty['cap']),
        ]))

    story += [Spacer(1, 16),
              Paragraph('References cited in the Introduction', sty['h1'])]
    body_for_keys = intro_tex.replace('\x00D\x00', '')
    for key in bbl_order:
        if f'{{{key}}}' not in body_for_keys:
            continue
        story.append(Paragraph(f'<font color="#14509b">[{NUMBER[key]}]</font> '
                               f'{reference_text(key)}', sty['ref']))

    story += [Spacer(1, 12),
              HRFlowable(width='100%', thickness=0.5, color='#aaaaaa', spaceAfter=7),
              Paragraph('About this file: a reading copy of the revised Introduction. No LaTeX '
                        'distribution was available where it was produced, so it was typeset '
                        'with ReportLab and Matplotlib (mathtext); the formulas are rendered '
                        'from the LaTeX of the manuscript. The authoritative source remains '
                        'FINAL_SUBMISSION.tex together with references.bib and '
                        'sn-mathphys-num-local.bst.', sty['note'])]

    def footer(canvas, doc):
        canvas.saveState()
        canvas.setFont('Times-Roman', 8.5)
        canvas.setFillColor('#666666')
        canvas.drawCentredString(A4[0] / 2, 12 * mm, str(doc.page))
        canvas.restoreState()

    doc = BaseDocTemplate(
        str(OUT), pagesize=A4, leftMargin=25 * mm, rightMargin=25 * mm,
        topMargin=22 * mm, bottomMargin=20 * mm,
        title='Introduction (revised) — Joint Code-Dimension and k-Galois-Hull '
              'Enumerators for Simple-Root Constacyclic Codes over Square-Free '
              'Affine Algebras',
        author='Arun Kumar Yadav')
    doc.addPageTemplates([PageTemplate(id='all',
                                       frames=[Frame(doc.leftMargin, doc.bottomMargin,
                                                     doc.width, doc.height, id='main')],
                                       onPage=footer)])
    doc.build(story)
    print('written', OUT)


if __name__ == '__main__':
    main()
