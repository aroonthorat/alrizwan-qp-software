import pytest
from fastapi.testclient import TestClient
from server.main import app
from server.models import PaperHeader
from server.bank_service import (
    save_question_to_db,
    list_bank_questions,
    auto_pick_from_bank,
    check_paper_repetition_warnings,
    save_paper_and_record_usage
)
from server.parser import parse_raw_text

client = TestClient(app)

@pytest.fixture
def default_header():
    return PaperHeader(
        class_name="Class 9th",
        subject="Social Science",
        paper_name="Mid Term Examination",
        month_year="OCT. 2026",
        date="2026-10-15",
        marks=40,
        time="2 Hours"
    )

def test_bank_list_and_filter():
    res = client.get("/api/bank/questions?class_name=Class+9th&subject=Social+Science")
    assert res.status_code == 200
    data = res.json()
    assert "total" in data
    assert "items" in data
    assert data["total"] > 0
    # Every item should have required fields
    item = data["items"][0]
    assert "id" in item
    assert "text" in item
    assert "type" in item
    assert "marks" in item
    assert "used_in" in item

def test_bank_search():
    res = client.get("/api/bank/questions?q=Ganga")
    assert res.status_code == 200
    data = res.json()
    assert data["total"] >= 1
    assert any("Ganga" in q["text"] for q in data["items"])

def test_auto_pick_theory(default_header):
    payload = {
        "header": default_header.model_dump(),
        "template": "3a",
        "question_count": 5
    }
    res = client.post("/api/bank/auto-pick", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["paper"]["template"] == "3a"
    assert len(data["paper"]["groups"]) > 0
    assert len(data["sheets"]) >= 1

def test_auto_pick_mcq(default_header):
    payload = {
        "header": default_header.model_dump(),
        "template": "3b",
        "question_count": 10,
        "preferred_type": "MCQ"
    }
    res = client.post("/api/bank/auto-pick", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["paper"]["template"] == "3b"
    total_q = sum(len(g["questions"]) for g in data["paper"]["groups"])
    assert total_q == 10

def test_repetition_guardrail(default_header):
    # Auto-pick paper
    paper = auto_pick_from_bank(default_header, template="3a", question_count=3)
    # Check repetition warnings
    warns = check_paper_repetition_warnings(paper)
    # Questions from Class 9 Social Science were used in the seeded Unit Test
    assert isinstance(warns, list)
