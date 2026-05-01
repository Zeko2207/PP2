"""PostgreSQL persistence layer for the Snake leaderboard."""

from __future__ import annotations

from datetime import datetime
from typing import Any

import psycopg2
from psycopg2.extras import RealDictCursor

from config import DB_CONFIG


class DatabaseError(RuntimeError):
    """Custom error used when the database is not available."""


def get_connection():
    """Create and return a PostgreSQL connection."""
    try:
        return psycopg2.connect(**DB_CONFIG)
    except psycopg2.Error as error:
        raise DatabaseError(str(error)) from error


def init_db() -> tuple[bool, str]:
    """Create required tables if they do not already exist."""
    sql = """
    CREATE TABLE IF NOT EXISTS players (
        id       SERIAL PRIMARY KEY,
        username VARCHAR(50) UNIQUE NOT NULL
    );

    CREATE TABLE IF NOT EXISTS game_sessions (
        id            SERIAL PRIMARY KEY,
        player_id     INTEGER REFERENCES players(id),
        score         INTEGER NOT NULL,
        level_reached INTEGER NOT NULL,
        played_at     TIMESTAMP DEFAULT NOW()
    );
    """

    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(sql)
        return True, "Database connected"
    except DatabaseError as error:
        return False, str(error)


def get_or_create_player(username: str) -> int:
    """Return player id; create a new player if the username is new."""
    username = username.strip()[:50] or "Player"

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO players (username)
                VALUES (%s)
                ON CONFLICT (username) DO NOTHING;
                """,
                (username,),
            )
            cur.execute("SELECT id FROM players WHERE username = %s;", (username,))
            row = cur.fetchone()
            if row is None:
                raise DatabaseError("Could not create or find player")
            return int(row[0])


def save_game_session(username: str, score: int, level_reached: int) -> tuple[bool, str]:
    """Save one finished game session to PostgreSQL."""
    try:
        player_id = get_or_create_player(username)
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO game_sessions (player_id, score, level_reached)
                    VALUES (%s, %s, %s);
                    """,
                    (player_id, int(score), int(level_reached)),
                )
        return True, "Saved"
    except DatabaseError as error:
        return False, str(error)


def get_personal_best(username: str) -> int:
    """Return the best score for one username. Return 0 if no result exists."""
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT COALESCE(MAX(gs.score), 0)
                    FROM game_sessions gs
                    JOIN players p ON p.id = gs.player_id
                    WHERE p.username = %s;
                    """,
                    (username.strip()[:50] or "Player",),
                )
                row = cur.fetchone()
                return int(row[0]) if row else 0
    except DatabaseError:
        return 0


def get_top_scores(limit: int = 10) -> list[dict[str, Any]]:
    """Fetch Top 10 scores from PostgreSQL."""
    try:
        with get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    """
                    SELECT
                        p.username,
                        gs.score,
                        gs.level_reached,
                        gs.played_at
                    FROM game_sessions gs
                    JOIN players p ON p.id = gs.player_id
                    ORDER BY gs.score DESC, gs.level_reached DESC, gs.played_at ASC
                    LIMIT %s;
                    """,
                    (limit,),
                )
                rows = cur.fetchall()
    except DatabaseError:
        return []

    result: list[dict[str, Any]] = []
    for row in rows:
        played_at = row["played_at"]
        if isinstance(played_at, datetime):
            date_text = played_at.strftime("%Y-%m-%d %H:%M")
        else:
            date_text = str(played_at)

        result.append(
            {
                "username": row["username"],
                "score": int(row["score"]),
                "level": int(row["level_reached"]),
                "date": date_text,
            }
        )
    return result
