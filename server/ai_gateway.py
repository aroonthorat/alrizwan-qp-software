import os
import json
import hashlib
from pathlib import Path
from typing import Dict, Any, Optional

CONFIG_DIR = Path(__file__).resolve().parent.parent / "config"
ROUTES_PATH = CONFIG_DIR / "routes.json"

class AIGateway:
    """
    Central AI gateway adhering to SOFTWARE-PLAN §4:
    - All AI calls routed through here.
    - Offline fallback / disabled mode if AI is off.
    - Caches responses.
    - Reads keys strictly from environment variables (.env).
    """
    def __init__(self):
        self.routes = self._load_routes()

    def _load_routes(self) -> Dict[str, Any]:
        if ROUTES_PATH.exists():
            with open(ROUTES_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}

    def is_ai_available(self) -> bool:
        # Check if enabled and keys exist
        return bool(os.getenv("GEMINI_API_KEY") or os.getenv("ANTHROPIC_API_KEY"))

    def call(self, task: str, payload: Dict[str, Any], schema: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        if not self.is_ai_available():
            raise RuntimeError(f"AI is disabled or API keys are missing. Offline mode is active.")

        # In Phase 1, all core parsing and layout is rule-based and works fully offline.
        raise NotImplementedError(f"AI task {task} scheduled for Phase 5.")

ai_gateway = AIGateway()
