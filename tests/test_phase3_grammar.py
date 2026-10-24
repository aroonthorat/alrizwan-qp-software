import pytest
from fastapi.testclient import TestClient
from server.main import app
from server.models import PaperHeader
from server.parser import parse_raw_text
from server.checker import check_question_grammar, audit_paper_grammar

client = TestClient(app)

def test_auto_rules_spacing_and_blanks():
    text = "Fill in the blank:  The capital is   ____ ."
    cleaned, logs, suggs = check_question_grammar("Q1", text, lang="en")
    assert "  " not in cleaned
    assert "____________" in cleaned
    assert any(l["rule"] == "U-01" for l in logs)
    assert any(l["rule"] == "U-03" for l in logs)

def test_english_grammar_rules():
    # Wh-question without question mark
    text1 = "What is the capital of France"
    _, _, suggs1 = check_question_grammar("Q1", text1, lang="en")
    assert any(s["rule"] == "EN-03" for s in suggs1)

    # US to UK spelling
    text2 = "Describe the color and center of the cell."
    _, _, suggs2 = check_question_grammar("Q2", text2, lang="en")
    assert any(s["rule"] == "EN-08" and s["original"] == "color" for s in suggs2)
    assert any(s["rule"] == "EN-08" and s["original"] == "center" for s in suggs2)

def test_hindi_grammar_rules():
    # Standard form: गयी -> गई
    text = "वह बाज़ार गयी."
    cleaned, logs, suggs = check_question_grammar("Q1", text, lang="hi")
    assert cleaned.endswith("।")  # HI-01 Purna Viram
    assert any(s["rule"] == "HI-03" and s["suggestion"] == "गई" for s in suggs)

def test_marathi_grammar_rules():
    # Standard form: आणी -> आणि
    text = "राम आणी शाम मित्र आहेत।"
    cleaned, logs, suggs = check_question_grammar("Q1", text, lang="mr")
    assert cleaned.endswith(".")  # MR-01 modern Marathi uses .
    assert any(s["rule"] == "MR-03" and s["suggestion"] == "आणि" for s in suggs)

def test_urdu_unicode_rules():
    # Arabic Yeh \u064A -> Urdu Yeh \u06CC
    arabic_text = "ہندوستان کی راجدھانی" # with arabic yeh
    cleaned, logs, suggs = check_question_grammar("Q1", "ہندوستان کي", lang="ur")
    # Arabic kaf \u0643 converted to Urdu \u06A9
    assert any(l["rule"] == "UR-01" for l in logs)

def test_api_grammar_check_and_dictionary():
    header = PaperHeader()
    paper = parse_raw_text("1. What is the color of the sky?\n2. Explain the process.", header)
    res = client.post("/api/grammar/check", json={"paper": paper.model_dump()})
    assert res.status_code == 200
    data = res.json()
    assert "auto_logs" in data
    assert "suggestions" in data
    assert any(s["original"] == "color" for s in data["suggestions"])

    # Test add to dictionary whitelist
    res_dict = client.post("/api/grammar/dictionary/add", json={"lang": "en", "word": "Chlorophyll"})
    assert res_dict.status_code == 200
    assert res_dict.json()["status"] == "ok"
