import pytest
from fastapi.testclient import TestClient
from server.main import app
from server.storage_sync import queue_sync_action, get_pending_queue_count

client = TestClient(app)

def test_sync_status_offline_mode():
    res = client.get("/api/sync/status")
    assert res.status_code == 200
    data = res.json()
    assert "pending_sync_items" in data
    assert "mode" in data
    assert "last_sync" in data

def test_sync_queueing_and_flush():
    initial_count = get_pending_queue_count()
    queue_sync_action("save_question", {
        "text": "What is the boiling point of water?",
        "class": "9",
        "subject": "Science",
        "marks": 1
    })
    new_count = get_pending_queue_count()
    assert new_count == initial_count + 1

    # Flush queue (skips or completes safely in local offline mode)
    flush_res = client.post("/api/sync/flush")
    assert flush_res.status_code == 200
    flush_data = flush_res.json()
    assert flush_data["status"] in ("skipped", "completed", "synced")

def test_ai_admin_stats_and_budget_cap():
    # 1. Fetch AI stats
    stats_res = client.get("/api/admin/ai-stats")
    assert stats_res.status_code == 200
    stats = stats_res.json()
    assert "monthly_spend" in stats
    assert "monthly_cap" in stats
    assert "total_calls" in stats
    assert "cache_hit_rate" in stats

    # 2. Update monthly budget cap
    cap_res = client.post("/api/admin/set-budget-cap", json={"monthly_cap": 750.0})
    assert cap_res.status_code == 200
    assert cap_res.json()["monthly_cap"] == 750.0

    # 3. Verify updated cap in stats
    stats_res2 = client.get("/api/admin/ai-stats")
    assert stats_res2.json()["monthly_cap"] == 750.0

def test_admin_dictionary_crud():
    # Add word via existing dictionary add endpoint
    add_res = client.post("/api/grammar/dictionary/add", json={"word": "Nandedkar", "lang": "mr"})
    assert add_res.status_code == 200

    # Get dictionary list
    list_res = client.get("/api/admin/dictionary")
    assert list_res.status_code == 200
    words = [item["word"] for item in list_res.json()["dictionary"]]
    assert "Nandedkar" in words

    # Remove word
    del_res = client.request("DELETE", "/api/admin/dictionary", json={"word": "Nandedkar", "lang": "mr"})
    assert del_res.status_code == 200
    assert del_res.json()["status"] == "removed"

    # Confirm removed
    list_res2 = client.get("/api/admin/dictionary")
    words2 = [item["word"] for item in list_res2.json()["dictionary"]]
    assert "Nandedkar" not in words2
