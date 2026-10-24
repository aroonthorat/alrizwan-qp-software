import pytest
from fastapi.testclient import TestClient
from server.main import app
from server.figures import generate_timeline_svg, generate_concept_map_svg

client = TestClient(app)

def test_generate_timeline_svg():
    events = [
        {"year": 1914, "text": "WWI begins", "blank": False},
        {"year": 1918, "text": "WWI ends", "blank": True},
        {"year": 1939, "text": "WWII begins", "blank": False}
    ]
    svg = generate_timeline_svg(events)
    assert "<svg" in svg
    assert "1914" in svg
    assert "[ _____ ]" in svg  # Blank placeholder
    assert "</svg>" in svg

def test_generate_concept_map_svg():
    branches = [
        {"text": "Troposphere", "blank": False},
        {"text": "", "blank": True},
        {"text": "Mesosphere", "blank": False}
    ]
    svg = generate_concept_map_svg("Atmosphere", branches)
    assert "<svg" in svg
    assert "Atmosphere" in svg
    assert "[ Complete ]" in svg
    assert "</svg>" in svg

def test_api_figures():
    res_time = client.post("/api/figures/timeline", json={
        "events": [{"year": 2000, "text": "Millennium", "blank": False}],
        "width": 400,
        "height": 120
    })
    assert res_time.status_code == 200
    assert "image/svg+xml" in res_time.headers["content-type"]

    res_map = client.post("/api/figures/concept-map", json={
        "root_title": "Energy",
        "branches": [{"text": "Solar", "blank": False}],
        "width": 400,
        "height": 150
    })
    assert res_map.status_code == 200
    assert "image/svg+xml" in res_map.headers["content-type"]

def test_diagram_list_api():
    res = client.get("/api/diagrams")
    assert res.status_code == 200
    assert isinstance(res.json(), list)
