import os
import json
import httpx
from typing import Dict, Any, Optional

from server.ai_gateway import ai_gateway

WORKER_URL = os.getenv("CLOUDFLARE_WORKER_URL", "")

class AIClient:
    """
    AI Client adhering to specs/SOFTWARE-PLAN.md §7 & specs/STORAGE-AND-RAG.md §2:
    - School PC holds NO secret API keys.
    - Online: Calls the Cloudflare Worker's /api/ai/call endpoint.
    - Offline / Disconnected: Falls back seamlessly to local rule-based engine.
    """
    def __init__(self, worker_url: Optional[str] = None):
        self.worker_url = worker_url or os.getenv("CLOUDFLARE_WORKER_URL", "").rstrip("/")

    def is_cloud_connected(self) -> bool:
        if not self.worker_url:
            return False
        try:
            with httpx.Client(timeout=2.0) as client:
                r = client.get(f"{self.worker_url}/api/health")
                return r.status_code == 200
        except Exception:
            return False

    def call(self, task: str, payload: Dict[str, Any], schema: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Routes through Cloudflare Worker if connected, else falls back to local engine."""
        if self.worker_url:
            try:
                with httpx.Client(timeout=30.0) as client:
                    resp = client.post(
                        f"{self.worker_url}/api/ai/call",
                        json={"task": task, "payload": payload, "schema": schema}
                    )
                    if resp.status_code == 200:
                        return resp.json()
                    elif resp.status_code == 429:
                        # Monthly cap reached on Worker, use local offline fallback
                        err_data = resp.json()
                        print(f"Worker monthly cap notice: {err_data.get('error')}")
            except Exception as e:
                # Fallback to local offline engine if worker unreachable
                print(f"Cloudflare Worker unreachable, switching to local mode: {e}")

        # Local offline gateway execution
        return ai_gateway.call(task=task, payload=payload, schema=schema)

ai_client = AIClient()
