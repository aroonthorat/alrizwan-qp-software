import os
import sqlite3
import json
import zipfile
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional
import httpx

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
BACKUP_DIR = Path(__file__).resolve().parent.parent / "backups"
QUEUE_DB_PATH = DATA_DIR / "offline-queue.sqlite"

def init_queue_db():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(QUEUE_DB_PATH)
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS sync_queue (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        action_type TEXT NOT NULL,
        payload_json TEXT NOT NULL,
        created_at TEXT NOT NULL,
        status TEXT DEFAULT 'pending',
        retry_count INTEGER DEFAULT 0
    )
    """)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS sync_meta (
        key TEXT PRIMARY KEY,
        value TEXT
    )
    """)
    conn.commit()
    conn.close()

def queue_sync_action(action_type: str, payload: Dict[str, Any]) -> int:
    """Enqueues an action to be synced with Cloudflare D1 when online."""
    init_queue_db()
    conn = sqlite3.connect(QUEUE_DB_PATH)
    cur = conn.cursor()
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cur.execute("""
    INSERT INTO sync_queue (action_type, payload_json, created_at, status)
    VALUES (?, ?, ?, 'pending')
    """, (action_type, json.dumps(payload), now_str))
    action_id = cur.lastrowid
    conn.commit()
    conn.close()
    return action_id

def get_pending_queue_count() -> int:
    init_queue_db()
    conn = sqlite3.connect(QUEUE_DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM sync_queue WHERE status = 'pending'")
    cnt = cur.fetchone()[0]
    conn.close()
    return cnt

def get_sync_status(worker_url: Optional[str] = None) -> Dict[str, Any]:
    url = worker_url or os.getenv("CLOUDFLARE_WORKER_URL", "")
    pending = get_pending_queue_count()
    connected = False
    
    if url:
        try:
            with httpx.Client(timeout=2.0) as client:
                r = client.get(f"{url.rstrip('/')}/api/health")
                if r.status_code == 200:
                    connected = True
        except Exception:
            connected = False

    init_queue_db()
    conn = sqlite3.connect(QUEUE_DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT value FROM sync_meta WHERE key = 'last_sync'")
    row = cur.fetchone()
    last_sync = row[0] if row else "Never"
    conn.close()

    return {
        "cloud_connected": connected,
        "worker_url": url or "Not configured (Local Offline Mode)",
        "pending_sync_items": pending,
        "last_sync": last_sync,
        "mode": "Cloudflare D1 + Vectorize" if connected else "Local Offline SQLite Queue"
    }

def flush_queue_to_worker(worker_url: Optional[str] = None) -> Dict[str, Any]:
    """Flushes local pending actions to Cloudflare D1."""
    url = worker_url or os.getenv("CLOUDFLARE_WORKER_URL", "")
    if not url:
        return {"status": "skipped", "message": "Worker URL not configured. Operating in local offline mode."}

    init_queue_db()
    conn = sqlite3.connect(QUEUE_DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT id, action_type, payload_json FROM sync_queue WHERE status = 'pending' ORDER BY id ASC")
    items = cur.fetchall()

    if not items:
        conn.close()
        return {"status": "synced", "count": 0, "message": "Queue is empty."}

    success_count = 0
    failed_count = 0

    with httpx.Client(timeout=10.0) as client:
        for item_id, action_type, payload_json in items:
            payload = json.loads(payload_json)
            try:
                if action_type == "save_question":
                    r = client.post(f"{url.rstrip('/')}/api/bank/questions", json=payload)
                elif action_type == "save_paper":
                    r = client.post(f"{url.rstrip('/')}/api/papers", json=payload)
                else:
                    r = None

                if r and r.status_code in (200, 201):
                    cur.execute("UPDATE sync_queue SET status = 'synced' WHERE id = ?", (item_id,))
                    success_count += 1
                else:
                    cur.execute("UPDATE sync_queue SET retry_count = retry_count + 1 WHERE id = ?", (item_id,))
                    failed_count += 1
            except Exception as e:
                print(f"Error syncing item {item_id}: {e}")
                cur.execute("UPDATE sync_queue SET retry_count = retry_count + 1 WHERE id = ?", (item_id,))
                failed_count += 1

    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cur.execute("INSERT OR REPLACE INTO sync_meta (key, value) VALUES ('last_sync', ?)", (now_str,))
    conn.commit()
    conn.close()

    return {
        "status": "completed",
        "synced": success_count,
        "failed": failed_count,
        "last_sync": now_str
    }

def create_nightly_backup() -> Path:
    """
    Creates a zip backup of the data folder per specs/SOFTWARE-PLAN.md §9.
    Excludes journal and temporary files.
    """
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    zip_path = BACKUP_DIR / f"alrizwan_backup_{timestamp}.zip"

    with zipfile.ZipFile(str(zip_path), "w", zipfile.ZIP_DEFLATED) as zf:
        for root, _, files in os.walk(DATA_DIR):
            for file in files:
                if file.endswith((".docx", "-journal", ".tmp")):
                    continue
                file_full = Path(root) / file
                arcname = file_full.relative_to(DATA_DIR)
                zf.write(file_full, arcname=str(arcname))

    return zip_path
