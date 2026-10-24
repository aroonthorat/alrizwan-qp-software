import pytest
from pathlib import Path
from fastapi.testclient import TestClient

from server.main import app
from server.models import PaperHeader, ParsedPaper, QuestionGroup, QuestionItem
from server.parser import parse_raw_text, parse_paper_parts
from server.export import export_paper_to_docx, generate_export_filename

client = TestClient(app)

BASE_DIR = Path(__file__).resolve().parent.parent

@pytest.fixture
def default_header():
    return PaperHeader(
        class_name="Class 9th",
        subject="Social Science",
        paper_name="FIRST UNIT TEST",
        month_year="AUG. 2026",
        date="2026-08-12",
        marks=40,
        time="2 Hours"
    )

def test_health():
    res = client.get("/api/health")
    assert res.status_code == 200
    assert res.json()["status"] == "ok"

def test_config():
    res = client.get("/api/config")
    assert res.status_code == 200
    assert "Al-Rizwan English School" in res.json()["name"]

def test_samples_api():
    res = client.get("/api/samples")
    assert res.status_code == 200
    samples = res.json()
    assert len(samples) >= 3

def test_theory_paper_parsing(default_header):
    sample_path = BASE_DIR / "samples" / "class9-social-science-theory.txt"
    with open(sample_path, "r", encoding="utf-8") as f:
        text = f.read()

    paper = parse_raw_text(text, default_header)
    assert paper.template == "3a"
    assert paper.total_marks_calculated == 40.0
    assert paper.is_valid is True
    assert len(paper.validation_errors) == 0
    assert len(paper.groups) == 5

def test_mcq_paper_parsing(default_header):
    sample_path = BASE_DIR / "samples" / "class9-social-science-mcq.txt"
    with open(sample_path, "r", encoding="utf-8") as f:
        text = f.read()

    paper = parse_raw_text(text, default_header)
    assert paper.template == "3b"
    assert paper.total_marks_calculated == 40.0
    assert paper.is_valid is True
    assert len(paper.validation_errors) == 0
    total_q = sum(len(g.questions) for g in paper.groups)
    assert total_q == 40

def test_marks_mismatch_blocks_export(default_header):
    # Header says 50 marks, but paper has 40 marks
    bad_header = default_header.model_copy(update={"marks": 50})
    sample_path = BASE_DIR / "samples" / "class9-social-science-theory.txt"
    with open(sample_path, "r", encoding="utf-8") as f:
        text = f.read()

    paper = parse_raw_text(text, bad_header)
    assert paper.is_valid is False
    assert len(paper.validation_errors) > 0
    assert "Marks mismatch" in paper.validation_errors[0]

    # Attempt to export via API
    res = client.post("/api/export", json={"paper": paper.model_dump()})
    assert res.status_code == 400
    assert "Export blocked due to validation errors" in res.json()["detail"]

def test_mcq_invalid_options_count(default_header):
    bad_mcq_text = """
1. What is the capital of India?
(1) New Delhi (2) Mumbai (3) Kolkata
"""
    paper = parse_raw_text(bad_mcq_text, default_header)
    # Only 3 options instead of 4
    assert paper.is_valid is False
    assert any("exactly 4 required" in err for err in paper.validation_errors)

def test_docx_export_both_papers(default_header, tmp_path):
    theory_path = BASE_DIR / "samples" / "class9-social-science-theory.txt"
    with open(theory_path, "r", encoding="utf-8") as f:
        theory_paper = parse_raw_text(f.read(), default_header)
    
    out_theory = export_paper_to_docx(theory_paper, tmp_path)
    assert out_theory.exists()
    assert out_theory.name == "Class 9th Social Science - Theory Paper.docx"
    assert out_theory.stat().st_size > 10000

    mcq_path = BASE_DIR / "samples" / "class9-social-science-mcq.txt"
    with open(mcq_path, "r", encoding="utf-8") as f:
        mcq_paper = parse_raw_text(f.read(), default_header)

    out_mcq = export_paper_to_docx(mcq_paper, tmp_path)
    assert out_mcq.exists()
    assert out_mcq.name == "Class 9th Social Science - MCQ Paper.docx"
    assert out_mcq.stat().st_size > 10000
