import io
import pytest
from pathlib import Path
from fastapi.testclient import TestClient
from server.main import app
import docx

client = TestClient(app)

SAMPLE_THEORY_TEXT = """
Q.1) Answer the following. (2 × 1 = 2)
1. What is the unit of electric current?
2. Define photosynthesis.
"""

def test_ocr_upload():
    # Create mock 1x1 png image
    img_bytes = (
        b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01"
        b"\x08\x06\x00\x00\x00\x1f\x15c4\x00\x00\x00\nIDATx\x9cc\x00\x01"
        b"\x00\x00\x05\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82"
    )
    files = {"file": ("handwritten_paper.png", io.BytesIO(img_bytes), "image/png")}
    res = client.post("/api/ocr/upload", files=files)
    assert res.status_code == 200
    data = res.json()
    assert "text" in data
    assert "Q.1)" in data["text"]
    assert "powerhouse" in data["text"] or "electric current" in data["text"] or "photosynthesis" in data["text"]

def test_bilingual_translation_and_export():
    # 1. Parse sample paper first
    parse_res = client.post("/api/parse", json={
        "header": {
            "school": "Al-Rizwan English School",
            "class_name": "Class 9th",
            "subject": "Social Science",
            "paper_name": "First Unit Test",
            "month_year": "AUG. 2026",
            "date": "2026-08-12",
            "marks": 2,
            "time": "1 Hour"
        },
        "content": SAMPLE_THEORY_TEXT
    })
    assert parse_res.status_code == 200
    paper_data = parse_res.json()["parts"]["theory"]["paper"]

    # 2. Test Bilingual Translation API
    trans_res = client.post("/api/bilingual/translate", json={"paper": paper_data})
    assert trans_res.status_code == 200
    bilingual_paper = trans_res.json()["bilingual_paper"]
    assert bilingual_paper.get("is_bilingual") is True
    assert "urdu_title" in bilingual_paper["groups"][0]
    assert "urdu_text" in bilingual_paper["groups"][0]["questions"][0]

    # 3. Test Bilingual .docx Export
    export_res = client.post("/api/export/bilingual", json={"paper": paper_data})
    assert export_res.status_code == 200
    assert "application/vnd.openxmlformats" in export_res.headers["content-type"]
    assert "Bilingual" in export_res.headers["content-disposition"]

    # Open docx and verify text content and fonts
    doc_stream = io.BytesIO(export_res.content)
    doc = docx.Document(doc_stream)
    full_text = "\n".join([p.text for p in doc.paragraphs] + [c.text for t in doc.tables for r in t.rows for c in r.cells])
    assert "Al-Rizwan English School" in full_text
    assert "What is the unit of electric current?" in full_text
    # Urdu Nastaleeq text should be present
    assert any(c in full_text for c in ["مندرجہ", "جوابات", "برقی", "سوال"])

def test_diagram_auto_tag():
    res = client.post("/api/diagrams/auto-tag", json={
        "filename": "atmosphere_layers.jpg",
        "subject": "Social Science",
        "chapter": "Atmosphere"
    })
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "success"
    assert "Atmosphere" in data["tags"]
    assert "Layers" in data["tags"] or "Geography" in data["tags"]
