import base64
from pathlib import Path
from typing import List, Dict, Any, Optional
from server.models import ParsedPaper, QuestionGroup, QuestionItem

ASSETS_DIR = Path(__file__).resolve().parent.parent.parent / "assets"
LOGO_PATH = ASSETS_DIR / "logo.jpg"

def get_logo_data_uri() -> str:
    if LOGO_PATH.exists():
        with open(LOGO_PATH, "rb") as f:
            encoded = base64.b64encode(f.read()).decode("utf-8")
            return f"data:image/jpeg;base64,{encoded}"
    return ""

def paginate_paper_3a(paper: ParsedPaper) -> List[Dict[str, Any]]:
    """
    Paginates Template 3a (Theory).
    Target: 85-95% fill, breaks at question-group boundaries.
    For Class 9 Social Science (Q1-Q5):
    Sheet 1: Q1, Q2, Q3 + continuation note
    Sheet 2: Q4, Q5 (with large map placeholder)
    """
    groups = paper.groups
    sheets = []

    if len(groups) <= 3:
        # Fits on 1 sheet
        sheets.append({
            "page_num": 1,
            "total_pages": 1,
            "has_header": True,
            "groups": groups,
            "continuation_note": None
        })
    else:
        # Split into Sheet 1 and Sheet 2 (or more if needed)
        # Class 9 reference splits at Q.3 / Q.4
        sheet1_groups = groups[:3]
        sheet2_groups = groups[3:]

        sheets.append({
            "page_num": 1,
            "total_pages": 2,
            "has_header": True,
            "groups": sheet1_groups,
            "continuation_note": f"{sheet2_groups[0].group_id} and {sheet2_groups[-1].group_id} continue on page 2 →"
        })

        sheets.append({
            "page_num": 2,
            "total_pages": 2,
            "has_header": False,
            "groups": sheet2_groups,
            "continuation_note": None
        })

    return sheets

def paginate_paper_3b(paper: ParsedPaper) -> List[Dict[str, Any]]:
    """
    Paginates Template 3b (MCQ).
    For 40 questions (Sections A+B / C+D):
    Sheet 1: Header + Details + Instructions + Sections A+B (Q1-Q20) + continuation note
    Sheet 2: Sections C+D (Q21-Q40) + Rough work box
    """
    groups = paper.groups
    sheets = []

    total_q = sum(len(g.questions) for g in groups)

    if total_q <= 25:
        # Fits on 1 sheet
        sheets.append({
            "page_num": 1,
            "total_pages": 1,
            "has_header": True,
            "has_instructions": True,
            "groups": groups,
            "has_rough_work": True,
            "continuation_note": None
        })
    else:
        # Split by sections or half questions
        if len(groups) >= 4:
            s1_groups = groups[:2]
            s2_groups = groups[2:]
        else:
            half = len(groups) // 2
            s1_groups = groups[:half]
            s2_groups = groups[half:]

        # Continuation text
        next_sec_names = [g.section_name or g.heading for g in s2_groups]
        cont_text = f"{next_sec_names[0]} continue on page 2 →" if next_sec_names else "Continues on page 2 →"

        sheets.append({
            "page_num": 1,
            "total_pages": 2,
            "has_header": True,
            "has_instructions": True,
            "groups": s1_groups,
            "has_rough_work": False,
            "continuation_note": cont_text
        })

        sheets.append({
            "page_num": 2,
            "total_pages": 2,
            "has_header": False,
            "has_instructions": False,
            "groups": s2_groups,
            "has_rough_work": True,
            "continuation_note": None
        })

    return sheets

def paginate_paper(paper: ParsedPaper) -> List[Dict[str, Any]]:
    if paper.template == "3b":
        return paginate_paper_3b(paper)
    return paginate_paper_3a(paper)
