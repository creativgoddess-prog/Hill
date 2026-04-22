"""
Saves and loads session data so you never lose your research or plan.
"""
import json
import os
from datetime import datetime
from pathlib import Path

DATA_DIR = Path.home() / ".ai_income_bot"


def ensure_data_dir():
    DATA_DIR.mkdir(exist_ok=True)


def save_session(data: dict, filename: str = None) -> str:
    ensure_data_dir()
    if not filename:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"session_{timestamp}.json"
    path = DATA_DIR / filename
    with open(path, "w") as f:
        json.dump(data, f, indent=2)
    return str(path)


def load_latest_session() -> dict | None:
    ensure_data_dir()
    sessions = sorted(DATA_DIR.glob("session_*.json"), reverse=True)
    if not sessions:
        return None
    with open(sessions[0]) as f:
        return json.load(f)


def save_plan_as_text(plan_text: str) -> str:
    ensure_data_dir()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = DATA_DIR / f"business_plan_{timestamp}.txt"
    path.write_text(plan_text)
    return str(path)


def list_sessions() -> list[str]:
    ensure_data_dir()
    return [str(p) for p in sorted(DATA_DIR.glob("session_*.json"), reverse=True)]
