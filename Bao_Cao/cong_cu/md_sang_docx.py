"""Convert Bao_Cao/BaoCao.md to Bao_Cao/BaoCao.docx with python-docx (cover, TOC field, page numbers, tables, figures)."""
import re
import sys
from pathlib import Path

from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.opc.constants import RELATIONSHIP_TYPE as RT
from docx.shared import Cm, Pt, RGBColor

sys.stdout.reconfigure(encoding="utf8")
# latex2mathml may be installed beside the scripts rather than in the environment.
sys.path.append(str(Path(__file__).resolve().parent.parent / "pylib"))
BASE = Path(__file__).resolve().parent.parent
SRC, DST = BASE / "BaoCao.md", BASE / "BaoCao.docx"
FONT, CODE_FONT = "Times New Roman", "Consolas"
BLUE = RGBColor(0x1F, 0x4E, 0x8C)


def set_font(run, name=FONT, size=None, bold=None, italic=None, color=None):
    run.font.name = name
    rpr = run._element.get_or_add_rPr()
    fonts = rpr.find(qn("w:rFonts"))
    if fonts is None:
        fonts = OxmlElement("w:rFonts")
        rpr.insert(0, fonts)
    for attr in ("w:ascii", "w:hAnsi", "w:eastAsia", "w:cs"):
        fonts.set(qn(attr), name)
    if size:
        run.font.size = Pt(size)
    if bold is not None:
        run.bold = bold
    if italic is not None:
        run.italic = italic
    if color is not None:
        run.font.color.rgb = color


def shade(element_pr, fill):
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), fill)
    element_pr.append(shd)


def para_border(p, color="2F6DB5", side="left", size=18):
    ppr = p._p.get_or_add_pPr()
    borders = OxmlElement("w:pBdr")
    b = OxmlElement(f"w:{side}")
    b.set(qn("w:val"), "single")
    b.set(qn("w:sz"), str(size))
    b.set(qn("w:space"), "6")
    b.set(qn("w:color"), color)
    borders.append(b)
    ppr.append(borders)


def add_field(paragraph, instr, placeholder=""):
    run = paragraph.add_run()
    fld = OxmlElement("w:fldChar"); fld.set(qn("w:fldCharType"), "begin"); run._r.append(fld)
    run = paragraph.add_run()
    it = OxmlElement("w:instrText"); it.set(qn("xml:space"), "preserve"); it.text = instr; run._r.append(it)
    run = paragraph.add_run()
    fld = OxmlElement("w:fldChar"); fld.set(qn("w:fldCharType"), "separate"); run._r.append(fld)
    run = paragraph.add_run(placeholder)
    set_font(run, size=12)
    run = paragraph.add_run()
    fld = OxmlElement("w:fldChar"); fld.set(qn("w:fldCharType"), "end"); run._r.append(fld)


def add_hyperlink(paragraph, text, url, size=None, bold=False):
    rid = paragraph.part.relate_to(url, RT.HYPERLINK, is_external=True)
    link = OxmlElement("w:hyperlink")
    link.set(qn("r:id"), rid)
    run = OxmlElement("w:r")
    rpr = OxmlElement("w:rPr")
    fonts = OxmlElement("w:rFonts")
    for attr in ("w:ascii", "w:hAnsi", "w:eastAsia", "w:cs"):
        fonts.set(qn(attr), FONT)
    rpr.append(fonts)
    if bold:
        rpr.append(OxmlElement("w:b"))
    color = OxmlElement("w:color"); color.set(qn("w:val"), "1F4E8C"); rpr.append(color)
    u = OxmlElement("w:u"); u.set(qn("w:val"), "single"); rpr.append(u)
    if size:
        sz = OxmlElement("w:sz"); sz.set(qn("w:val"), str(int(size * 2))); rpr.append(sz)
    run.append(rpr)
    t = OxmlElement("w:t"); t.set(qn("xml:space"), "preserve"); t.text = text
    run.append(t)
    link.append(run)
    paragraph._p.append(link)


INLINE = re.compile(r"\*\*(.+?)\*\*|`([^`]+)`|\[([^\]]+)\]\(([^)]+)\)|\*([^*]+)\*")


def add_inline(paragraph, text, size=13, bold=False, italic=False):
    pos = 0
    for m in INLINE.finditer(text):
        if m.start() > pos:
            set_font(paragraph.add_run(text[pos:m.start()]), size=size, bold=bold, italic=italic)
        if m.group(1) is not None:
            add_inline(paragraph, m.group(1), size, True, italic)
        elif m.group(2) is not None:
            set_font(paragraph.add_run(m.group(2)), CODE_FONT, size - 2, bold=bold, color=RGBColor(0x8A, 0x2B, 0x2B))
        elif m.group(3) is not None:
            add_hyperlink(paragraph, m.group(3), m.group(4), size, bold)
        else:
            add_inline(paragraph, m.group(5), size, bold, True)
        pos = m.end()
    if pos < len(text):
        set_font(paragraph.add_run(text[pos:]), size=size, bold=bold, italic=italic)


def fmt(p, align=None, before=0, after=6, line=1.3, left=None, first=None, keep=False):
    pf = p.paragraph_format
    if align is not None:
        p.alignment = align
    pf.space_before, pf.space_after, pf.line_spacing = Pt(before), Pt(after), line
    if left is not None:
        pf.left_indent = Cm(left)
    if first is not None:
        pf.first_line_indent = Cm(first)
    if keep:
        pf.keep_with_next = True
    return p


def setup(doc):
    sec = doc.sections[0]
    sec.page_height, sec.page_width = Cm(29.7), Cm(21.0)
    sec.top_margin, sec.bottom_margin, sec.left_margin, sec.right_margin = Cm(2), Cm(2), Cm(3), Cm(2)
    st = doc.styles["Normal"]
    st.font.name, st.font.size = FONT, Pt(13)
    st.element.rPr.rFonts.set(qn("w:eastAsia"), FONT)
    for name, size, bold, italic, color in (("Heading 1", 16, True, False, BLUE), ("Heading 2", 14, True, False, BLUE),
                                            ("Heading 3", 13, True, False, RGBColor(0x22, 0x22, 0x22)), ("Heading 4", 13, True, True, RGBColor(0x22, 0x22, 0x22))):
        hs = doc.styles[name]
        hs.font.name, hs.font.size, hs.font.bold, hs.font.italic = FONT, Pt(size), bold, italic
        hs.font.color.rgb = color
        rpr = hs.element.get_or_add_rPr()
        fonts = rpr.find(qn("w:rFonts"))
        if fonts is None:
            fonts = OxmlElement("w:rFonts"); rpr.insert(0, fonts)
        for attr in ("w:ascii", "w:hAnsi", "w:eastAsia", "w:cs"):
            fonts.set(qn(attr), FONT)
        for a in ("w:asciiTheme", "w:hAnsiTheme", "w:eastAsiaTheme", "w:cstheme"):
            if fonts.get(qn(a)) is not None:
                del fonts.attrib[qn(a)]
        pf = hs.paragraph_format
        pf.space_before, pf.space_after, pf.keep_with_next = Pt(18 if name == "Heading 1" else 12), Pt(8), True
        pf.line_spacing = 1.2
    footer = sec.footer.paragraphs[0]
    footer.alignment = WD_ALIGN_PARAGRAPH.CENTER
    add_field(footer, "PAGE", "1")


def cover(doc, lines):
    lines = [l.strip() for l in lines]
    for i, l in enumerate(lines):
        if not l:
            fmt(doc.add_paragraph(), after=10)
            continue
        p = fmt(doc.add_paragraph(), WD_ALIGN_PARAGRAPH.CENTER, after=4, line=1.2)
        if l.startswith(("TRƯỜNG", "KHOA")):
            set_font(p.add_run(l), size=14, bold=True)
        elif l == "BÁO CÁO MÔN HỌC":
            fmt(p, WD_ALIGN_PARAGRAPH.CENTER, before=70, after=4)
            set_font(p.add_run(l), size=18, bold=True)
        elif l.startswith("KHO DỮ LIỆU"):
            set_font(p.add_run(l), size=20, bold=True, color=BLUE)
        elif l == "ĐỀ TÀI:":
            fmt(p, WD_ALIGN_PARAGRAPH.CENTER, before=40, after=4)
            set_font(p.add_run(l), size=14, bold=True)
        elif l.isupper():
            set_font(p.add_run(l), size=15, bold=True)
        elif ":" in l and not l.startswith("Năm"):
            fmt(p, WD_ALIGN_PARAGRAPH.LEFT, after=4, left=4.0)
            k, v = l.split(":", 1)
            set_font(p.add_run(k + ":"), size=14, bold=True)
            set_font(p.add_run(v), size=14)
        else:
            fmt(p, WD_ALIGN_PARAGRAPH.CENTER, before=120)
            set_font(p.add_run(l), size=14, bold=True)
    doc.add_paragraph().add_run().add_break(WD_BREAK.PAGE)


def table(doc, rows):
    cells = [[c.strip() for c in re.split(r"(?<!\\)\|", r.strip()[1:-1])] for r in rows]
    header, body = cells[0], [r for r in cells[2:]]
    ncol = len(header)
    t = doc.add_table(rows=1 + len(body), cols=ncol)
    t.style = "Table Grid"
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    weights = [max(6, min(60, max(len(re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", r[i] if i < len(r) else "")) for r in cells if r is not cells[1]))) for i in range(ncol)]
    total_w = 16.0
    widths = [total_w * w / sum(weights) for w in weights]
    for ri, row in enumerate([header] + body):
        for ci in range(ncol):
            cell = t.cell(ri, ci)
            cell.width = Cm(widths[ci])
            text = row[ci] if ci < len(row) else ""
            p = cell.paragraphs[0]
            fmt(p, WD_ALIGN_PARAGRAPH.CENTER if ri == 0 else WD_ALIGN_PARAGRAPH.LEFT, after=2, line=1.1)
            add_inline(p, text.replace("\\|", "|"), size=11, bold=(ri == 0))
            if ri == 0:
                shade(cell._tc.get_or_add_tcPr(), "DCE6F2")
    trpr = t.rows[0]._tr.get_or_add_trPr()
    h = OxmlElement("w:tblHeader"); h.set(qn("w:val"), "true"); trpr.append(h)
    # A row never breaks across pages; a short table stays on one page with its caption.
    for ri, row in enumerate(t.rows):
        row._tr.get_or_add_trPr().append(OxmlElement("w:cantSplit"))
        if len(t.rows) <= 15 and ri < len(t.rows) - 1:
            for cell in row.cells:
                for p in cell.paragraphs:
                    p.paragraph_format.keep_with_next = True
    fmt(doc.add_paragraph(), after=4)


def box_border(p, color="9AA3AE"):
    # Same border on every line of a block: Word draws one frame around the consecutive paragraphs.
    ppr = p._p.get_or_add_pPr()
    borders = OxmlElement("w:pBdr")
    for side in ("top", "left", "bottom", "right"):
        b = OxmlElement(f"w:{side}")
        b.set(qn("w:val"), "single"); b.set(qn("w:sz"), "6"); b.set(qn("w:space"), "4"); b.set(qn("w:color"), color)
        borders.append(b)
    ppr.append(borders)


def code(doc, lines):
    size = 8.5 if max(len(l) for l in lines) > 80 else 9.5
    for i, l in enumerate(lines):
        p = fmt(doc.add_paragraph(), WD_ALIGN_PARAGRAPH.LEFT, after=0, line=1.0, left=0.5, keep=i < len(lines) - 1)
        box_border(p)
        shade(p._p.get_or_add_pPr(), "F3F4F6")
        set_font(p.add_run(l if l else " "), CODE_FONT, size)
    fmt(doc.add_paragraph(), after=2)


MML2OMML = r"C:\Program Files\Microsoft Office\root\Office16\MML2OMML.XSL"
_xslt = None


def math(doc, lines):
    """One Word equation (OMML) per LaTeX line: LaTeX -> MathML (latex2mathml) -> OMML (Office's own XSLT)."""
    global _xslt
    from lxml import etree
    from latex2mathml.converter import convert
    if _xslt is None:
        _xslt = etree.XSLT(etree.parse(MML2OMML))
    for i, latex in enumerate(l for l in lines if l.strip()):
        omath = _xslt(etree.fromstring(convert(latex.strip()))).getroot()
        para = etree.SubElement(etree.Element("dummy"), qn("m:oMathPara"))
        para.append(omath)
        p = fmt(doc.add_paragraph(), WD_ALIGN_PARAGRAPH.CENTER, before=2, after=4, line=1.0, keep=True)
        p._p.append(para)
    fmt(doc.add_paragraph(), after=2)


def callout(doc, text):
    p = fmt(doc.add_paragraph(), WD_ALIGN_PARAGRAPH.JUSTIFY, before=4, after=10, line=1.25, left=0.4)
    ppr = p._p.get_or_add_pPr()
    para_border(p)
    shade(ppr, "EEF4FB")
    add_inline(p, text, size=12)


def figure(doc, caption, path):
    p = fmt(doc.add_paragraph(), WD_ALIGN_PARAGRAPH.CENTER, before=6, after=2, keep=True)
    from PIL import Image
    with Image.open(BASE / path) as im:
        w, h = im.size
    width = 16.0 if w / h > 1.3 else 13.0
    if w / h < 1.05:
        width = 15.0
    p.add_run().add_picture(str(BASE / path), width=Cm(width))
    c = fmt(doc.add_paragraph(), WD_ALIGN_PARAGRAPH.CENTER, after=10)
    set_font(c.add_run(caption), size=12, italic=True, bold=False)


def main():
    lines = SRC.read_text(encoding="utf8").splitlines()
    doc = Document()
    setup(doc)
    i = 0
    first_h1 = True
    while i < len(lines):
        line = lines[i]
        s = line.strip()
        if s == "<!-- trang-bia -->":
            j = lines.index("<!-- het-trang-bia -->", i)
            cover(doc, lines[i + 1:j]); i = j + 1; continue
        if s == "<!-- muc-luc -->":
            j = lines.index("<!-- het-muc-luc -->", i)
            add_field(fmt(doc.add_paragraph(), after=0), 'TOC \\o "1-2" \\h \\z \\u', "Mở file bằng Word và nhấn F9 để cập nhật mục lục.")
            i = j + 1; continue
        if s.startswith("<!--"):
            i += 1; continue
        if s.startswith("# "):
            title_text = s[2:]
            if title_text == "MỤC LỤC":
                p = fmt(doc.add_paragraph(), WD_ALIGN_PARAGRAPH.CENTER, after=12)
                set_font(p.add_run(title_text), size=16, bold=True, color=BLUE)
            else:
                if not first_h1:
                    doc.add_paragraph().add_run().add_break(WD_BREAK.PAGE)
                h = doc.add_heading(level=1)
                h.alignment = WD_ALIGN_PARAGRAPH.CENTER
                add_inline(h, title_text, size=16, bold=True)
                for r in h.runs:
                    r.font.color.rgb = BLUE
            first_h1 = False
            i += 1; continue
        m = re.match(r"^(#{2,4}) (.+)$", s)
        if m:
            level = len(m.group(1))
            h = doc.add_heading(level=level)
            add_inline(h, m.group(2), size={2: 14, 3: 13, 4: 13}[level], bold=True, italic=(level == 4))
            for r in h.runs:
                r.font.color.rgb = BLUE if level == 2 else RGBColor(0x22, 0x22, 0x22)
            i += 1; continue
        if s.startswith("```"):
            j = i + 1
            while not lines[j].strip().startswith("```"):
                j += 1
            (math if s == "```math" else code)(doc, lines[i + 1:j]); i = j + 1; continue
        if s.startswith("|"):
            j = i
            while j < len(lines) and lines[j].strip().startswith("|"):
                j += 1
            table(doc, lines[i:j]); i = j; continue
        fm = re.match(r"^!\[(.+)\]\((.+)\)$", s)
        if fm:
            figure(doc, fm.group(1), fm.group(2)); i += 1; continue
        if s.startswith("> "):
            callout(doc, s[2:]); i += 1; continue
        if re.match(r"^\*(Bảng [^*]+)\*$", s):
            p = fmt(doc.add_paragraph(), WD_ALIGN_PARAGRAPH.CENTER, before=6, after=4, keep=True)
            set_font(p.add_run(s.strip("*")), size=12, bold=True, italic=True)
            i += 1; continue
        lm = re.match(r"^(\s*)([-*]|\d+\.) (.+)$", line)
        if lm:
            depth = len(lm.group(1)) // 2
            marker = lm.group(2)
            p = fmt(doc.add_paragraph(), WD_ALIGN_PARAGRAPH.JUSTIFY, after=3, line=1.3, left=0.75 + 0.7 * depth, first=-0.5)
            label = ("•" if depth == 0 else "–") if marker in "-*" else marker
            set_font(p.add_run(label + "\t"), size=13, bold=(marker not in "-*"))
            p.paragraph_format.tab_stops.add_tab_stop(Cm(0.75 + 0.7 * depth))
            add_inline(p, lm.group(3))
            i += 1; continue
        if not s:
            i += 1; continue
        p = fmt(doc.add_paragraph(), WD_ALIGN_PARAGRAPH.JUSTIFY, after=6, first=0)
        if re.match(r"^\[\d+\] ", s):
            p.paragraph_format.left_indent, p.paragraph_format.first_line_indent = Cm(1.0), Cm(-1.0)
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT
            add_inline(p, s, size=12)
        else:
            add_inline(p, s)
        i += 1
    doc.save(DST)
    print("saved", DST, DST.stat().st_size)


main()
