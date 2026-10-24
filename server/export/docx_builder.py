import os
from pathlib import Path
from typing import Optional, List
import docx
from docx import Document
from docx.shared import Inches, Pt, RGBColor, Mm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import qn, nsdecls

from server.models import ParsedPaper, QuestionGroup, QuestionItem, DiagramPlaceholder
from server.export.xml_helpers import (
    set_page_borders,
    set_cell_borders,
    set_cell_shading,
    set_section_columns,
    add_footer_with_page_number,
    configure_document_fonts
)

ASSETS_DIR = Path(__file__).resolve().parent.parent.parent / "assets"
LOGO_PATH = ASSETS_DIR / "logo.jpg"
WATERMARK_PATH = ASSETS_DIR / "logo_watermark.png"

def create_watermark_if_needed():
    if not WATERMARK_PATH.exists() and LOGO_PATH.exists():
        from PIL import Image
        img = Image.open(LOGO_PATH).convert("RGBA")
        gray = img.convert("L")
        alpha = int(255 * 0.07)  # 7% opacity
        wm = Image.new("RGBA", img.size, (255, 255, 255, 0))
        for x in range(img.size[0]):
            for y in range(img.size[1]):
                lum = gray.getpixel((x, y))
                wm.putpixel((x, y), (lum, lum, lum, alpha))
        wm.save(WATERMARK_PATH)

def format_clean_class(class_name: str) -> str:
    cleaned = class_name.strip()
    if not cleaned.lower().startswith("class"):
        cleaned = f"Class {cleaned}"
    return cleaned

def generate_export_filename(paper: ParsedPaper) -> str:
    cls_name = format_clean_class(paper.header.class_name)
    sub = paper.header.subject.strip()
    suffix = "MCQ Paper.docx" if paper.template == "3b" else "Theory Paper.docx"
    return f"{cls_name} {sub} - {suffix}"

def add_header_masthead(doc: Document, paper: ParsedPaper, is_3a: bool) -> None:
    """Renders the top masthead: Logo | School name & Exam | Roll No. boxes"""
    table = doc.add_table(rows=1, cols=3)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False

    # Widths: Left ~1.2 in, Center ~4.0 in, Right ~1.6 in
    widths = [Inches(1.2), Inches(4.2), Inches(1.6)]
    for i, w in enumerate(widths):
        table.rows[0].cells[i].width = w

    # Left cell: Logo
    left_cell = table.cell(0, 0)
    left_cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
    lp = left_cell.paragraphs[0]
    lp.alignment = WD_ALIGN_PARAGRAPH.LEFT
    if LOGO_PATH.exists():
        l_run = lp.add_run()
        l_run.add_picture(str(LOGO_PATH), width=Inches(1.0 if is_3a else 0.94))

    # Center cell: School info
    center_cell = table.cell(0, 1)
    center_cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
    cp = center_cell.paragraphs[0]
    cp.alignment = WD_ALIGN_PARAGRAPH.CENTER
    cp.paragraph_format.space_before = Pt(0)
    cp.paragraph_format.space_after = Pt(2)

    r_school = cp.add_run(paper.header.school + "\n")
    r_school.bold = True
    r_school.font.size = Pt(20 if is_3a else 18)
    r_school.font.color.rgb = RGBColor(0x11, 0x11, 0x11)

    r_addr = cp.add_run(paper.header.address + "\n")
    r_addr.font.size = Pt(9.5 if is_3a else 9.0)
    r_addr.font.color.rgb = RGBColor(0x22, 0x22, 0x22)

    paper_title = paper.header.paper_name.upper()
    if paper.header.month_year:
        paper_title += f" — {paper.header.month_year.upper()}"
    r_title = cp.add_run(paper_title)
    r_title.bold = True
    r_title.font.size = Pt(10.5 if is_3a else 10.0)
    r_title.font.color.rgb = RGBColor(0x11, 0x11, 0x11)

    # Right cell: Roll No. boxes
    right_cell = table.cell(0, 2)
    right_cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
    rp = right_cell.paragraphs[0]
    rp.alignment = WD_ALIGN_PARAGRAPH.CENTER
    rp.paragraph_format.space_after = Pt(3)
    r_roll_lbl = rp.add_run("Roll No.\n")
    r_roll_lbl.font.size = Pt(9.5)
    r_roll_lbl.bold = True

    # 4 empty square boxes
    roll_tbl = right_cell.add_table(rows=1, cols=paper.header.roll_no_boxes)
    roll_tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    for c in roll_tbl.rows[0].cells:
        c.width = Inches(0.24)
        set_cell_borders(c, top="single", bottom="single", left="single", right="single", sz="8")
        # Empty space in cell
        p = c.paragraphs[0]
        p.paragraph_format.space_before = Pt(2)
        p.paragraph_format.space_after = Pt(4)

    # Bottom rule across masthead
    for cell in table.rows[0].cells:
        set_cell_borders(cell, top=None, bottom="single", left=None, right=None, color="1A1A1A", sz="16")

def add_details_table_3a(doc: Document, paper: ParsedPaper) -> None:
    """Header details table for 3a (Theory)"""
    table = doc.add_table(rows=3, cols=3)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False

    # Row 1: Class · Subject · Date
    r1 = table.rows[0]
    _set_cell_text(r1.cells[0], "Class: ", paper.header.class_name)
    _set_cell_text(r1.cells[1], "Subject: ", paper.header.subject)
    _set_cell_text(r1.cells[2], "Date: ", paper.header.date or "")

    # Row 2: Marks · Unit Test · Time
    r2 = table.rows[1]
    _set_cell_text(r2.cells[0], "Marks: ", str(paper.header.marks))
    _set_cell_text(r2.cells[1], "Exam: ", paper.header.paper_name)
    _set_cell_text(r2.cells[2], "Time: ", paper.header.time)

    # Row 3: Name of the Student (spans 3 columns)
    r3 = table.rows[2]
    # Merge cells
    cell_student = r3.cells[0]
    cell_student.merge(r3.cells[1]).merge(r3.cells[2])
    _set_cell_text(cell_student, "Name of the Student: ", "................................................................................................")

    for row in table.rows:
        for cell in row.cells:
            cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
            set_cell_borders(cell, top="single", bottom="single", left="single", right="single", color="1A1A1A", sz="8")

def add_details_table_3b(doc: Document, paper: ParsedPaper) -> None:
    """Header details table for 3b (MCQ, 4 columns)"""
    table = doc.add_table(rows=3, cols=4)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False

    # Row 1: Class · Subject · Unit Test · Date
    r1 = table.rows[0]
    _set_cell_text(r1.cells[0], "Class: ", paper.header.class_name)
    _set_cell_text(r1.cells[1], "Subject: ", paper.header.subject)
    _set_cell_text(r1.cells[2], "Exam: ", paper.header.paper_name)
    _set_cell_text(r1.cells[3], "Date: ", paper.header.date or "")

    # Row 2: Questions · Max. Marks · Time (spans 2)
    r2 = table.rows[1]
    total_q = sum(len(g.questions) for g in paper.groups)
    _set_cell_text(r2.cells[0], "Questions: ", str(total_q))
    _set_cell_text(r2.cells[1], "Max. Marks: ", str(paper.header.marks))
    r2.cells[2].merge(r2.cells[3])
    _set_cell_text(r2.cells[2], "Time: ", paper.header.time)

    # Row 3: Name of the Student (spans 3) · Roll No.
    r3 = table.rows[2]
    r3.cells[0].merge(r3.cells[1]).merge(r3.cells[2])
    _set_cell_text(r3.cells[0], "Name of the Student: ", "....................................................................................")
    _set_cell_text(r3.cells[3], "Roll No.: ", "")

    for row in table.rows:
        for cell in row.cells:
            cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
            set_cell_borders(cell, top="single", bottom="single", left="single", right="single", color="1A1A1A", sz="8")

def _set_cell_text(cell, label: str, value: str):
    p = cell.paragraphs[0]
    p.paragraph_format.space_before = Pt(3)
    p.paragraph_format.space_after = Pt(3)
    r_lbl = p.add_run(label)
    r_lbl.font.size = Pt(9.5)
    r_val = p.add_run(value)
    r_val.bold = True
    r_val.font.size = Pt(9.5)

def build_docx_3a(paper: ParsedPaper, output_path: Path) -> Path:
    """Builds Template 3a (Theory) .docx"""
    create_watermark_if_needed()
    doc = Document()
    configure_document_fonts(doc)

    section = doc.sections[0]
    section.page_width = Mm(210)
    section.page_height = Mm(297)
    section.top_margin = Mm(12)
    section.bottom_margin = Mm(12)
    section.left_margin = Mm(12)
    section.right_margin = Mm(12)
    set_page_borders(section)

    # Watermark in Header
    if WATERMARK_PATH.exists():
        hp = section.header.paragraphs[0]
        hp.alignment = WD_ALIGN_PARAGRAPH.CENTER
        hrun = hp.add_run()
        hrun.add_picture(str(WATERMARK_PATH), width=Inches(4.5))

    # Footer
    footer_text = f"{paper.header.school} · {paper.header.class_name} · {paper.header.subject} · {paper.header.paper_name}"
    fp = section.footer.paragraphs[0]
    fp.alignment = WD_ALIGN_PARAGRAPH.CENTER
    fp.paragraph_format.space_before = Pt(4)
    add_footer_with_page_number(fp, footer_text)

    # 1. Masthead
    add_header_masthead(doc, paper, is_3a=True)

    # Spacer
    p_sp = doc.add_paragraph()
    p_sp.paragraph_format.space_before = Pt(4)
    p_sp.paragraph_format.space_after = Pt(4)

    # 2. Details table
    add_details_table_3a(doc, paper)

    # 3. Question Groups
    # Paginate: Group boundary break between Q.3 and Q.4 for 2 sheets
    split_index = 3 if len(paper.groups) >= 4 else len(paper.groups)

    for i, group in enumerate(paper.groups):
        if i == split_index:
            # Continuation note before page break
            cp = doc.add_paragraph()
            cp.paragraph_format.space_before = Pt(12)
            cp.paragraph_format.space_after = Pt(8)
            cp.alignment = WD_ALIGN_PARAGRAPH.RIGHT
            c_run = cp.add_run(f"{paper.groups[split_index].group_id} and {paper.groups[-1].group_id} continue on page 2 →")
            c_run.font.italic = True
            c_run.font.size = Pt(10.5)
            c_run.font.color.rgb = RGBColor(0x55, 0x55, 0x55)

            # Insert page break
            doc.add_page_break()

        # Group Heading
        gp = doc.add_paragraph()
        gp.paragraph_format.space_before = Pt(12)
        gp.paragraph_format.space_after = Pt(6)
        gp.paragraph_format.keep_with_next = True

        heading_full = f"{group.group_id}) {group.heading}"
        if group.marks_display:
            heading_full += f"   {group.marks_display}"
        r_gh = gp.add_run(heading_full)
        r_gh.bold = True
        r_gh.font.size = Pt(13)  # ~17.5px

        # Sub-questions
        for q in group.questions:
            # If question has a diagram placeholder
            if q.diagram and q.diagram.placement == "side":
                # Side-by-side flex layout in docx using a 2-cell table
                tbl = doc.add_table(rows=1, cols=2)
                tbl.autofit = False
                tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
                cell_fig = tbl.cell(0, 0)
                cell_text = tbl.cell(0, 1)
                cell_fig.width = Inches(2.8)
                cell_text.width = Inches(4.2)

                # Figure box with hatched fill
                set_cell_borders(cell_fig, top="single", bottom="single", left="single", right="single", color="1A1A1A", sz="8")
                set_cell_shading(cell_fig, fill_hex="F4F2EC", val="pct15")
                fig_p = cell_fig.paragraphs[0]
                fig_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                fig_p.paragraph_format.space_before = Pt(20)
                fig_p.paragraph_format.space_after = Pt(20)
                r_cap = fig_p.add_run(q.diagram.caption)
                r_cap.font.name = "Consolas"
                r_cap.font.size = Pt(8.5)
                r_cap.font.color.rgb = RGBColor(0x55, 0x55, 0x55)

                # Question text in right cell
                set_cell_borders(cell_text, top=None, bottom=None, left=None, right=None)
                qp = cell_text.paragraphs[0]
                qp.paragraph_format.space_before = Pt(6)
                qp.paragraph_format.space_after = Pt(6)
                qp.paragraph_format.line_spacing = 1.4
                r_q = qp.add_run(f"{q.q_num}. {q.text}")
                r_q.font.size = Pt(12)  # 16px locked scale
            elif q.diagram and q.diagram.placement == "below":
                # Instruction text then map box below
                qp = doc.add_paragraph()
                qp.paragraph_format.space_before = Pt(6)
                qp.paragraph_format.space_after = Pt(4)
                qp.paragraph_format.line_spacing = 1.4
                r_q = qp.add_run(f"{q.q_num}. {q.text}")
                r_q.font.size = Pt(12)

                # Map box table
                map_tbl = doc.add_table(rows=1, cols=1)
                map_tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
                map_cell = map_tbl.cell(0, 0)
                map_cell.width = Inches(6.5)
                set_cell_borders(map_cell, top="single", bottom="single", left="single", right="single", color="1A1A1A", sz="8")
                set_cell_shading(map_cell, fill_hex="F4F2EC", val="pct12")
                mp = map_cell.paragraphs[0]
                mp.alignment = WD_ALIGN_PARAGRAPH.CENTER
                mp.paragraph_format.space_before = Pt(110)
                mp.paragraph_format.space_after = Pt(110)
                r_map = mp.add_run(q.diagram.caption)
                r_map.font.name = "Consolas"
                r_map.font.size = Pt(10)
                r_map.font.color.rgb = RGBColor(0x55, 0x55, 0x55)
            else:
                # Normal question
                qp = doc.add_paragraph()
                qp.paragraph_format.space_before = Pt(3)
                qp.paragraph_format.space_after = Pt(3)
                qp.paragraph_format.line_spacing = 1.4
                r_q = qp.add_run(f"{q.q_num}. {q.text}")
                r_q.font.size = Pt(12)  # 16px locked scale

    doc.save(str(output_path))
    return output_path

def build_docx_3b(paper: ParsedPaper, output_path: Path) -> Path:
    """Builds Template 3b (MCQ Booklet) .docx"""
    create_watermark_if_needed()
    doc = Document()
    configure_document_fonts(doc)

    section = doc.sections[0]
    section.page_width = Mm(210)
    section.page_height = Mm(297)
    section.top_margin = Mm(12)
    section.bottom_margin = Mm(12)
    section.left_margin = Mm(12)
    section.right_margin = Mm(12)
    set_page_borders(section)

    # Watermark in Header
    if WATERMARK_PATH.exists():
        hp = section.header.paragraphs[0]
        hp.alignment = WD_ALIGN_PARAGRAPH.CENTER
        hrun = hp.add_run()
        hrun.add_picture(str(WATERMARK_PATH), width=Inches(4.5))

    # Footer
    footer_text = f"{paper.header.school} · {paper.header.class_name} · {paper.header.subject} · {paper.header.paper_name}"
    fp = section.footer.paragraphs[0]
    fp.alignment = WD_ALIGN_PARAGRAPH.CENTER
    fp.paragraph_format.space_before = Pt(4)
    add_footer_with_page_number(fp, footer_text)

    # 1. Masthead
    add_header_masthead(doc, paper, is_3a=False)

    # Spacer
    p_sp = doc.add_paragraph()
    p_sp.paragraph_format.space_before = Pt(2)
    p_sp.paragraph_format.space_after = Pt(2)

    # 2. Details table (4 columns)
    add_details_table_3b(doc, paper)

    # 3. Important Instructions Box
    total_q = sum(len(g.questions) for g in paper.groups)
    num_secs = len(paper.groups)
    inst_tbl = doc.add_table(rows=1, cols=1)
    inst_tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    inst_cell = inst_tbl.cell(0, 0)
    inst_cell.width = Inches(7.0)
    set_cell_borders(inst_cell, top="single", bottom="single", left="single", right="single", color="1A1A1A", sz="8")

    ip = inst_cell.paragraphs[0]
    ip.paragraph_format.space_before = Pt(4)
    ip.paragraph_format.space_after = Pt(4)
    r_ih = ip.add_run("IMPORTANT INSTRUCTIONS\n")
    r_ih.bold = True
    r_ih.font.size = Pt(9.5)

    inst_text = (
        f"1. This paper contains {total_q} questions (in {num_secs} sections), all compulsory.\n"
        f"2. Each question carries 1 mark, only ONE of (1)–(4) is correct.\n"
        f"3. Darken the OMR circle with blue/black ball pen; rough work in the space provided."
    )
    r_ib = ip.add_run(inst_text)
    r_ib.font.size = Pt(8.5)

    # 4. Multi-column Section for Questions
    # In Word, we can add a new section for the 2-column layout
    col_section = doc.add_section()
    col_section.page_width = Mm(210)
    col_section.page_height = Mm(297)
    col_section.top_margin = Mm(12)
    col_section.bottom_margin = Mm(12)
    col_section.left_margin = Mm(12)
    col_section.right_margin = Mm(12)
    set_page_borders(col_section)
    set_section_columns(col_section, num_cols=2, space_twips=720, sep=True)

    # Add questions across sections
    for g_idx, group in enumerate(paper.groups):
        # Section Header
        sp = doc.add_paragraph()
        sp.paragraph_format.space_before = Pt(8)
        sp.paragraph_format.space_after = Pt(4)
        sp.paragraph_format.keep_with_next = True
        sp.alignment = WD_ALIGN_PARAGRAPH.CENTER

        sec_title = group.section_name or group.heading
        r_sec = sp.add_run(sec_title.upper())
        r_sec.bold = True
        r_sec.font.size = Pt(10)

        # Questions
        for q in group.questions:
            qp = doc.add_paragraph()
            qp.paragraph_format.space_before = Pt(4)
            qp.paragraph_format.space_after = Pt(1)
            qp.paragraph_format.keep_with_next = True
            r_stem = qp.add_run(f"{q.q_num}. {q.text}")
            r_stem.font.size = Pt(10.5)  # 14px locked scale

            # 2x2 Options
            if q.options and len(q.options) == 4:
                # Option row 1: (1) and (2)
                op1 = doc.add_paragraph()
                op1.paragraph_format.space_before = Pt(0)
                op1.paragraph_format.space_after = Pt(0)
                r_o1 = op1.add_run(f"  (1) {q.options[0]}       (2) {q.options[1]}")
                r_o1.font.size = Pt(9.5)

                # Option row 2: (3) and (4)
                op2 = doc.add_paragraph()
                op2.paragraph_format.space_before = Pt(0)
                op2.paragraph_format.space_after = Pt(3)
                r_o2 = op2.add_run(f"  (3) {q.options[2]}       (4) {q.options[3]}")
                r_o2.font.size = Pt(9.5)

    # Rough Work Box
    rw_tbl = doc.add_table(rows=1, cols=1)
    rw_tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    rw_cell = rw_tbl.cell(0, 0)
    rw_cell.width = Inches(3.2)
    set_cell_borders(rw_cell, top="single", bottom="single", left="single", right="single", color="1A1A1A", sz="8")
    rwp = rw_cell.paragraphs[0]
    rwp.paragraph_format.space_before = Pt(4)
    rwp.paragraph_format.space_after = Pt(30)
    r_rw = rwp.add_run("Space for rough work")
    r_rw.font.italic = True
    r_rw.font.size = Pt(8.5)
    r_rw.font.color.rgb = RGBColor(0x66, 0x66, 0x66)

    doc.save(str(output_path))
    return output_path

def export_paper_to_docx(paper: ParsedPaper, target_dir: Optional[Path] = None) -> Path:
    """Exports ParsedPaper to .docx according to locked template rules."""
    if not target_dir:
        target_dir = Path(__file__).resolve().parent.parent.parent / "data"
    target_dir.mkdir(parents=True, exist_ok=True)

    filename = generate_export_filename(paper)
    output_path = target_dir / filename

    if paper.template == "3b":
        return build_docx_3b(paper, output_path)
    else:
        return build_docx_3a(paper, output_path)
