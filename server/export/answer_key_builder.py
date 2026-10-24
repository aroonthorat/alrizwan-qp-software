from pathlib import Path
from docx import Document
from docx.shared import Inches, Pt, RGBColor, Mm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL

from server.models import ParsedPaper
from server.export.xml_helpers import (
    set_page_borders,
    set_cell_borders,
    configure_document_fonts,
    add_footer_with_page_number
)

def build_answer_key_docx(paper: ParsedPaper, answers_data: list, output_path: Path) -> Path:
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

    # Footer
    fp = section.footer.paragraphs[0]
    fp.alignment = WD_ALIGN_PARAGRAPH.CENTER
    footer_text = f"{paper.header.school} · {paper.header.class_name} · {paper.header.subject} · ANSWER KEY"
    add_footer_with_page_number(fp, footer_text)

    # Title Masthead
    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_title.paragraph_format.space_before = Pt(6)
    p_title.paragraph_format.space_after = Pt(2)
    r_sch = p_title.add_run(paper.header.school + "\n")
    r_sch.bold = True
    r_sch.font.size = Pt(18)

    r_sub = p_title.add_run(f"MODEL ANSWER KEY & EVALUATION SCHEME\n")
    r_sub.bold = True
    r_sub.font.size = Pt(13)
    r_sub.font.color.rgb = RGBColor(0x33, 0x33, 0x88)

    r_meta = p_title.add_run(f"{paper.header.class_name} — {paper.header.subject} | {paper.header.paper_name}\nMax Marks: {paper.header.marks}")
    r_meta.font.size = Pt(10)

    # Horizontal rule
    p_hr = doc.add_paragraph()
    p_hr.paragraph_format.space_after = Pt(10)

    # Answer Key Table
    table = doc.add_table(rows=1, cols=4)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False

    # Header Row
    headers = ["Q. No.", "Type", "Marks", "Model Answer / Key Points"]
    widths = [Inches(0.8), Inches(1.2), Inches(0.8), Inches(4.2)]
    for i, h in enumerate(headers):
        cell = table.cell(0, i)
        cell.width = widths[i]
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = p.add_run(h)
        r.bold = True
        r.font.size = Pt(10)
        set_cell_borders(cell, top="single", bottom="single", left="single", right="single", color="1A1A1A", sz="12")

    # Rows
    for ans in answers_data:
        row = table.add_row()
        q_num = ans.get("q_num", "")
        q_type = ans.get("type", "SHORT")
        marks = ans.get("marks", 1.0)
        ans_text = ans.get("answer", "")

        vals = [str(q_num), str(q_type), f"{marks}M", str(ans_text)]
        for i, val in enumerate(vals):
            c = row.cells[i]
            c.width = widths[i]
            p = c.paragraphs[0]
            if i < 3:
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            else:
                p.alignment = WD_ALIGN_PARAGRAPH.LEFT
            r = p.add_run(val)
            r.font.size = Pt(9.5)
            set_cell_borders(c, top="single", bottom="single", left="single", right="single", color="1A1A1A", sz="8")

    doc.save(str(output_path))
    return output_path
