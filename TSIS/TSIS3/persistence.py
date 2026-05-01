"""Persistence helpers for settings and leaderboard JSON files."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

BASE_DIR = Path(__file__).resolve().parent
SETTINGS_FILE = BASE_DIR / "settings.json"
LEADERBOARD_FILE = BASE_DIR / "leaderboard.json"

DEFAULT_SETTINGS: dict[str, Any] = {
    "sound": True,
    "car_color": "blue",
    "difficulty": "normal",
}

DEFAULT_LEADERBOARD: list[dict[str, Any]] = []

VALID_COLORS = ["blue", "red", "green", "yellow", "purple"]
VALID_DIFFICULTIES = ["easy", "normal", "hard"]


def _read_json(path: Path, default: Any) -> Any:
    """Read JSON from disk. If the file is missing or broken, return default."""
    if not path.exists():
        return default

    try:
        with path.open("r", encoding="utf-8") as file:
            return json.load(file)
    except (json.JSONDecodeError, OSError):
        return default


def _write_json(path: Path, data: Any) -> None:
    """Write JSON to disk in a readable format."""
    with path.open("w", encoding="utf-8") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)


def load_settings() -> dict[str, Any]:
    """Load settings and fix invalid/missing values."""
    settings = DEFAULT_SETTINGS.copy()
    loaded = _read_json(SETTINGS_FILE, DEFAULT_SETTINGS.copy())

    if isinstance(loaded, dict):
        settings.update(loaded)

    if settings["car_color"] not in VALID_COLORS:
        settings["car_color"] = DEFAULT_SETTINGS["car_color"]

    if settings["difficulty"] not in VALID_DIFFICULTIES:
        settings["difficulty"] = DEFAULT_SETTINGS["difficulty"]

    settings["sound"] = bool(settings.get("sound", True))
    return settings


def save_settings(settings: dict[str, Any]) -> None:
    """Save settings to settings.json."""
    _write_json(SETTINGS_FILE, settings)


def load_leaderboard() -> list[dict[str, Any]]:
    """Load leaderboard entries from leaderboard.json."""
    data = _read_json(LEADERBOARD_FILE, DEFAULT_LEADERBOARD.copy())
    if not isinstance(data, list):
        return []

    clean_entries: list[dict[str, Any]] = []
    for entry in data:
        if not isinstance(entry, dict):
            continue
        clean_entries.append(
            {
                "name": str(entry.get("name", "Player"))[:12],
                "score": int(entry.get("score", 0)),
                "distance": int(entry.get("distance", 0)),
                "coins": int(entry.get("coins", 0)),
            }
        )

    clean_entries.sort(key=lambda item: item["score"], reverse=True)
    return clean_entries[:10]


def save_leaderboard(entries: list[dict[str, Any]]) -> None:
    """Save only top 10 leaderboard entries."""
    entries.sort(key=lambda item: item["score"], reverse=True)
    _write_json(LEADERBOARD_FILE, entries[:10])


def add_score(entry: dict[str, Any]) -> list[dict[str, Any]]:
    """Add one result to the leaderboard and save it."""
    entries = load_leaderboard()
    entries.append(
        {
            "name": str(entry.get("name", "Player"))[:12],
            "score": int(entry.get("score", 0)),
            "distance": int(entry.get("distance", 0)),
            "coins": int(entry.get("coins", 0)),
        }
    )
    save_leaderboard(entries)
    return load_leaderboard()
