from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import qn, nsdecls
from docx.section import Section
from docx.table import _Cell
from docx.text.paragraph import Paragraph

def set_page_borders(section: Section) -> None:
    """Sets a single 4px double #1a1a1a border inset on the page (specs §1)."""
    sectPr = section._sectPr
    # Remove existing borders if any
    for el in sectPr.findall(qn("w:pgBorders")):
        sectPr.remove(el)

    pgBorders = OxmlElement("w:pgBorders")
    pgBorders.set(qn("w:offsetFrom"), "page")
    for side in ("top", "left", "bottom", "right"):
        border = OxmlElement(f"w:{side}")
        border.set(qn("w:val"), "double")
        border.set(qn("w:sz"), "24")  # 3pt
        border.set(qn("w:space"), "24")
        border.set(qn("w:color"), "1A1A1A")
        pgBorders.append(border)

    sectPr.append(pgBorders)

def set_cell_borders(cell: _Cell, top="single", bottom="single", left="single", right="single",
                     color="1A1A1A", sz="8") -> None:
    """Sets borders on an individual table cell."""
    tcPr = cell._tc.get_or_add_tcPr()
    tcBorders = OxmlElement("w:tcBorders")
    
    borders = {"top": top, "bottom": bottom, "left": left, "right": right}
    for side, val in borders.items():
        if val:
            b = OxmlElement(f"w:{side}")
            b.set(qn("w:val"), val)
            b.set(qn("w:sz"), sz)
            b.set(qn("w:space"), "0")
            b.set(qn("w:color"), color)
            tcBorders.append(b)
        else:
            b = OxmlElement(f"w:{side}")
            b.set(qn("w:val"), "nil")
            tcBorders.append(b)

    tcPr.append(tcBorders)

def set_cell_shading(cell: _Cell, fill_hex: str = "F4F2EC", val: str = "pct15", color: str = "CCCCCC") -> None:
    """Sets hatched or solid shading on a cell."""
    tcPr = cell._tc.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:val="{val}" w:color="{color}" w:fill="{fill_hex}"/>')
    tcPr.append(shd)

def set_section_columns(section: Section, num_cols: int = 2, space_twips: int = 720, sep: bool = True) -> None:
    """Sets 2-column layout with vertical separator rule for MCQ booklet (specs §3)."""
    sectPr = section._sectPr
    for el in sectPr.findall(qn("w:cols")):
        sectPr.remove(el)

    cols = OxmlElement("w:cols")
    cols.set(qn("w:num"), str(num_cols))
    cols.set(qn("w:space"), str(space_twips))
    if sep:
        cols.set(qn("w:sep"), "1")
    sectPr.append(cols)

def add_footer_with_page_number(footer_para: Paragraph, prefix_text: str) -> None:
    """
    Inserts footer text:
    <prefix_text> · Page <PAGE> of <NUMPAGES>
    Compatible with Word 2007+.
    """
    footer_para.text = prefix_text + " · Page "
    
    # Page field
    run = footer_para.add_run()
    fldSimple_page = OxmlElement("w:fldSimple")
    fldSimple_page.set(qn("w:instr"), "PAGE")
    run._r.append(fldSimple_page)
    
    run_of = footer_para.add_run(" of ")
    
    # NumPages field
    run_pages = footer_para.add_run()
    fldSimple_numpages = OxmlElement("w:fldSimple")
    fldSimple_numpages.set(qn("w:instr"), "NUMPAGES")
    run_pages._r.append(fldSimple_numpages)

def configure_document_fonts(doc) -> None:
    """Sets default document fonts to Times New Roman, Jameel Noori Nastaleeq, and Noto Sans Devanagari."""
    style = doc.styles["Normal"]
    font = style.font
    font.name = "Times New Roman"
    font.size = None  # Handled per-paragraph

    # OpenXML rFonts configuration
    rPr = style.element.get_or_add_rPr()
    rFonts = rPr.find(qn("w:rFonts"))
    if rFonts is None:
        rFonts = OxmlElement("w:rFonts")
        rPr.append(rFonts)
    rFonts.set(qn("w:ascii"), "Times New Roman")
    rFonts.set(qn("w:hAnsi"), "Times New Roman")
    rFonts.set(qn("w:cs"), "Jameel Noori Nastaleeq")
    rFonts.set(qn("w:eastAsia"), "Noto Sans Devanagari")

def set_paragraph_bidi(para: Paragraph, align: str = "right") -> None:
    """Sets RTL / bidi properties on a paragraph for Urdu / Arabic text in Word 2007."""
    pPr = para._p.get_or_add_pPr()
    bidi = OxmlElement("w:bidi")
    pPr.append(bidi)
    if align:
        jc = OxmlElement("w:jc")
        jc.set(qn("w:val"), align)
        pPr.append(jc)

def set_run_bidi(run, font_name: str = "Jameel Noori Nastaleeq") -> None:
    """Sets RTL and complex script font properties on a run for Word 2007."""
    rPr = run._r.get_or_add_rPr()
    rtl = OxmlElement("w:rtl")
    rPr.append(rtl)
    rFonts = OxmlElement("w:rFonts")
    rFonts.set(qn("w:ascii"), font_name)
    rFonts.set(qn("w:hAnsi"), font_name)
    rFonts.set(qn("w:cs"), font_name)
    rPr.append(rFonts)

