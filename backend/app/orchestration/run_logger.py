"""Append-only run logger for multi-agent execution traces in JSONL format."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

class RunLogger:
    """Thread-safe append-only logger for multi-agent traces."""

    def __init__(self, log_path: Optional[Path | str] = None):
        if log_path:
            self.log_file = Path(log_path)
        else:
            root_dir = Path(__file__).resolve().parent.parent.parent
            self.log_file = root_dir / "logs" / "run_log.jsonl"
        self.log_file.parent.mkdir(parents=True, exist_ok=True)

    def log_event(
        self,
        session_id: str,
        agent: str,
        step: str,
        action: str,
        input_summary: Any,
        output_summary: Any,
        duration_ms: float = 0.0,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        """Append a single structured JSON log entry."""
        entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "session_id": session_id,
            "agent": agent,
            "step": step,
            "action": action,
            "input_summary": input_summary,
            "output_summary": output_summary,
            "duration_ms": round(duration_ms, 2),
            "metadata": metadata or {},
        }
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")

run_logger = RunLogger()
