from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
import random
import time
from typing import Any

Grade = int | str
AnswerValue = int | float | str


@dataclass(slots=True)
class Question:
    id: str
    subject: str
    prompt: str
    answer: AnswerValue
    explanation: str
    diagram_html: str | None = None
    created_at: float = field(default_factory=time.time)


@dataclass(slots=True)
class AnswerLogEntry:
    question_no: int
    question_id: str
    subject: str
    prompt: str
    user_answer: str
    correct_answer: str
    correct: bool
    explanation: str
    elapsed_seconds: float
    timed_out: bool


@dataclass(slots=True)
class GameSession:
    id: str
    name: str
    age: int
    grade: Grade
    subjects: list[str]
    question_plan: list[str]
    total_questions: int
    lives: int
    rng: random.Random
    score: int = 0
    question_cursor: int = 0
    current_question: Question | None = None
    answer_log: list[AnswerLogEntry] = field(default_factory=list)
    elapsed_times: list[float] = field(default_factory=list)
    used_prompts: dict[str, set[str]] = field(default_factory=dict)
    finished: bool = False
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    @property
    def mistakes(self) -> int:
        return sum(1 for row in self.answer_log if not row.correct)

    @property
    def average_time(self) -> float:
        if not self.elapsed_times:
            return 0.0
        return sum(self.elapsed_times) / len(self.elapsed_times)

    @property
    def questions_answered(self) -> int:
        return len(self.answer_log)

    @property
    def current_question_no(self) -> int:
        return self.question_cursor + 1


@dataclass(slots=True)
class ScoreboardEntry:
    name: str
    age: int
    grade: str
    score: int
    total_questions: int
    avg_time: float
    subjects: str
    created_at_ms: int
    rank: int | None = None
