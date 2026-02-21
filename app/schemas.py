from __future__ import annotations

from pydantic import BaseModel, Field, field_validator


class QuestionView(BaseModel):
    id: str
    subject: str
    prompt: str
    diagram_html: str | None = None


class SessionStatsView(BaseModel):
    score: int
    lives: int
    current_question: int
    total_questions: int
    mistakes: int
    average_time_seconds: float


class ScoreboardEntryView(BaseModel):
    rank: int
    name: str
    age: int
    grade: str
    score: int
    total_questions: int
    avg_time_seconds: float
    subjects: str


class StartSessionRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=30)
    age: int
    subjects: list[str]

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("Name is required.")
        return cleaned

    @field_validator("subjects")
    @classmethod
    def validate_subjects(cls, value: list[str]) -> list[str]:
        if not value:
            raise ValueError("Select at least one subject.")
        return value


class StartSessionResponse(BaseModel):
    session_id: str
    player_name: str
    age: int
    grade: str
    subjects: list[str]
    total_questions: int
    stats: SessionStatsView
    question: QuestionView


class AnswerRequest(BaseModel):
    question_id: str = Field(..., min_length=1)
    answer: str = ""
    elapsed_seconds: float = 0


class AnswerOutcomeView(BaseModel):
    correct: bool
    timed_out: bool
    your_answer: str
    correct_answer: str
    explanation: str


class AnswerLogItemView(BaseModel):
    question_no: int
    subject: str
    prompt: str
    your_answer: str
    correct_answer: str
    correct: bool
    explanation: str
    elapsed_seconds: float
    timed_out: bool


class GameSummaryView(BaseModel):
    score: int
    total_questions: int
    mistakes: int
    average_time_seconds: float
    answers: list[AnswerLogItemView]
    leaderboard: list[ScoreboardEntryView]


class AnswerResponse(BaseModel):
    finished: bool
    outcome: AnswerOutcomeView
    stats: SessionStatsView
    next_question: QuestionView | None = None
    summary: GameSummaryView | None = None
