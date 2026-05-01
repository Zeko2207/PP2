"""Configuration and JSON settings helpers for TSIS 4 Snake Game."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

# -----------------------------
# Window and grid settings
# -----------------------------
SCREEN_WIDTH = 820
SCREEN_HEIGHT = 620
CELL_SIZE = 20
BOARD_COLS = 30
BOARD_ROWS = 30
BOARD_LEFT = 10
BOARD_TOP = 10
BOARD_WIDTH = BOARD_COLS * CELL_SIZE
BOARD_HEIGHT = BOARD_ROWS * CELL_SIZE
PANEL_LEFT = BOARD_LEFT + BOARD_WIDTH + 20
FPS = 60

# -----------------------------
# Gameplay settings
# -----------------------------
FOODS_PER_LEVEL = 5
FOOD_LIFETIME_MS = 7000
POWERUP_LIFETIME_MS = 8000
POWERUP_DURATION_MS = 5000
POWERUP_SPAWN_MIN_MS = 5000
POWERUP_SPAWN_MAX_MS = 10000

# -----------------------------
# Colors
# -----------------------------
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (120, 120, 120)
LIGHT_GRAY = (210, 210, 210)
DARK_GRAY = (45, 45, 45)
GREEN = (40, 200, 90)
DARK_GREEN = (20, 120, 50)
RED = (220, 40, 40)
DARK_RED = (120, 0, 0)
YELLOW = (240, 210, 60)
BLUE = (70, 130, 240)
PURPLE = (150, 80, 230)
ORANGE = (240, 150, 40)
CYAN = (30, 210, 220)

BASE_DIR = Path(__file__).resolve().parent
SETTINGS_FILE = BASE_DIR / "settings.json"

DEFAULT_SETTINGS: dict[str, Any] = {
    "snake_color": [40, 200, 90],
    "grid_overlay": True,
    "sound": True,
}

# PostgreSQL connection settings.
# You can change these here or set environment variables in Terminal.
DB_CONFIG = {
    "dbname": os.getenv("PGDATABASE", "snake_db"),
    "user": os.getenv("PGUSER", "postgres"),
    "password": os.getenv("PGPASSWORD", "23816"),
    "host": os.getenv("PGHOST", "localhost"),
    "port": os.getenv("PGPORT", "5432"),
}


def load_settings() -> dict[str, Any]:
    """Load settings from settings.json. If the file is missing, use defaults."""
    if not SETTINGS_FILE.exists():
        save_settings(DEFAULT_SETTINGS.copy())
        return DEFAULT_SETTINGS.copy()

    try:
        with SETTINGS_FILE.open("r", encoding="utf-8") as file:
            data = json.load(file)
    except (json.JSONDecodeError, OSError):
        data = {}

    settings = DEFAULT_SETTINGS.copy()
    settings.update(data)
    return settings


def save_settings(settings: dict[str, Any]) -> None:
    """Save settings to settings.json."""
    with SETTINGS_FILE.open("w", encoding="utf-8") as file:
        json.dump(settings, file, indent=4)


def tuple_color(value: Any) -> tuple[int, int, int]:
    """Convert a stored RGB list into a safe tuple for pygame."""
    if isinstance(value, list) and len(value) == 3:
        return tuple(max(0, min(255, int(c))) for c in value)  # type: ignore[return-value]
    return tuple(DEFAULT_SETTINGS["snake_color"])  # type: ignore[return-value]
