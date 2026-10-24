from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class PaperHeader(BaseModel):
    school: str = "Al-Rizwan English School"
    address: str = "Chaitaniya Nagar Road, Nanded"
    class_name: str = "Class 9th"
    subject: str = "Social Science"
    paper_name: str = "FIRST UNIT TEST"
    month_year: str = "AUG. 2026"
    date: Optional[str] = "2026-08-12"
    marks: int = 40
    time: str = "2 Hours"
    roll_no_boxes: int = 4

class DiagramPlaceholder(BaseModel):
    kind: str = "figure"  # "figure" or "map"
    caption: str = ""
    width_px: int = 280
    height_px: int = 175
    placement: str = "side"  # "side" for figure, "below" for map

class QuestionItem(BaseModel):
    id: Optional[str] = None
    q_num: str
    text: str
    type: str = "SHORT"
    marks: float = 1.0
    options: Optional[List[str]] = None
    diagram: Optional[DiagramPlaceholder] = None
    sub_questions: Optional[List["QuestionItem"]] = None

class QuestionGroup(BaseModel):
    group_id: str  # e.g., "Q.1", "SECTION A"
    heading: str   # e.g., "Answer the following." or "SECTION A — HISTORY"
    marks_display: Optional[str] = None  # e.g., "(10 × 1 = 10)"
    any_n: Optional[int] = None          # e.g., 5
    count: int = 0
    marks_per_q: float = 1.0
    total_marks: float = 0.0
    questions: List[QuestionItem] = Field(default_factory=list)
    is_section: bool = False
    section_name: Optional[str] = None

class ParsedPaper(BaseModel):
    header: PaperHeader
    template: str = "3a"  # "3a" (Theory) or "3b" (MCQ)
    groups: List[QuestionGroup] = Field(default_factory=list)
    total_marks_calculated: float = 0.0
    is_valid: bool = True
    validation_errors: List[str] = Field(default_factory=list)
    validation_warnings: List[str] = Field(default_factory=list)

class ParseRequest(BaseModel):
    header: PaperHeader
    content: str
    template_override: Optional[str] = None

class ValidationResult(BaseModel):
    is_valid: bool
    template: str
    header_marks: int
    calculated_marks: float
    errors: List[str]
    warnings: List[str]

class ExportRequest(BaseModel):
    paper: ParsedPaper
