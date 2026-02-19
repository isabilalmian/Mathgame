from __future__ import annotations

from datetime import datetime, timedelta, timezone
import sqlite3
import threading

from app.config import MAX_LEADERBOARD, SCOREBOARD_DAYS, SCOREBOARD_DB_PATH
from app.models import ScoreboardEntry


class ScoreboardStore:
    def __init__(self, db_path: str | None = None) -> None:
        self._db_path = str(db_path or SCOREBOARD_DB_PATH)
        self._lock = threading.Lock()
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self._db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        with self._lock, self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS scoreboard_entries (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    age INTEGER NOT NULL,
                    grade TEXT NOT NULL,
                    score INTEGER NOT NULL,
                    total_questions INTEGER NOT NULL,
                    avg_time REAL NOT NULL,
                    subjects TEXT NOT NULL,
                    created_at_ms INTEGER NOT NULL
                )
                """
            )
            conn.commit()

    def add_entry(
        self,
        *,
        name: str,
        age: int,
        grade: str,
        score: int,
        total_questions: int,
        avg_time: float,
        subjects: str,
    ) -> None:
        created_at_ms = int(datetime.now(timezone.utc).timestamp() * 1000)
        with self._lock, self._connect() as conn:
            conn.execute(
                """
                INSERT INTO scoreboard_entries (
                    name, age, grade, score, total_questions, avg_time, subjects, created_at_ms
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (name, age, grade, score, total_questions, avg_time, subjects, created_at_ms),
            )
            conn.commit()

    def get_leaderboard(
        self,
        *,
        limit: int = MAX_LEADERBOARD,
        max_days: int = SCOREBOARD_DAYS,
    ) -> list[ScoreboardEntry]:
        safe_limit = max(1, min(limit, MAX_LEADERBOARD))
        cutoff_dt = datetime.now(timezone.utc) - timedelta(days=max_days)
        cutoff_ms = int(cutoff_dt.timestamp() * 1000)
        with self._lock, self._connect() as conn:
            rows = conn.execute(
                """
                SELECT name, age, grade, score, total_questions, avg_time, subjects, created_at_ms
                FROM scoreboard_entries
                WHERE created_at_ms >= ?
                ORDER BY score DESC, avg_time ASC, created_at_ms DESC
                LIMIT ?
                """,
                (cutoff_ms, safe_limit),
            ).fetchall()

        entries = [
            ScoreboardEntry(
                name=row["name"],
                age=int(row["age"]),
                grade=str(row["grade"]),
                score=int(row["score"]),
                total_questions=int(row["total_questions"]),
                avg_time=float(row["avg_time"]),
                subjects=str(row["subjects"]),
                created_at_ms=int(row["created_at_ms"]),
            )
            for row in rows
        ]
        for idx, entry in enumerate(entries, start=1):
            entry.rank = idx
        return entries
