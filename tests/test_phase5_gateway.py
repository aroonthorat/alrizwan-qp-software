import pytest
from fastapi.testclient import TestClient
from server.main import app
from server.models import PaperHeader
from server.parser import parse_raw_text
from server.ai_gateway import ai_gateway

client = TestClient(app)

def test_ai_gateway_caching():
    task = "test_task"
    payload = {"query": "sample query text"}
    payload_str = '{"query": "sample query text"}'
    
    # Store in cache
    expected_resp = {"status": "ok", "result": "sample result"}
    ai_gateway.store_cache(task, payload_str, expected_resp)

    # Lookup
    cached = ai_gateway.lookup_cache(task, payload_str)
    assert cached == expected_resp

def test_ai_gateway_logging_and_monthly_spend():
    initial_spend = ai_gateway.get_monthly_spend()
    ai_gateway.log_call(
        task="test_logging",
        model="gemini-3.8-flash",
        tokens_in=100,
        tokens_out=50,
        cost_inr=0.05,
        cache_hit=False
    )
    new_spend = ai_gateway.get_monthly_spend()
    assert new_spend >= initial_spend + 0.05

def test_answer_key_generation_and_export():
    header = PaperHeader(
        class_name="Class 9th",
        subject="Social Science",
        paper_name="First Unit Test",
        marks=40
    )
    text = """
Q.1) Answer the following. (2 × 1 = 2)
1. Name the archive situated in New Delhi.
2. Which ocean lies to the south of India?
"""
    paper = parse_raw_text(text, header)
    
    res = client.post("/api/export/answer-key", json={"paper": paper.model_dump()})
    assert res.status_code == 200
    assert "application/vnd.openxmlformats" in res.headers["content-type"]
    assert "Answer" in res.headers["content-disposition"] and "Key.docx" in res.headers["content-disposition"]
