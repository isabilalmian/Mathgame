from __future__ import annotations

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.config import (
    APP_NAME,
    APP_VERSION,
    DATA_DIR,
    FRONTEND_DIR,
    SUBJECT_LABELS,
    SUPPORTED_SUBJECTS,
)
from app.models import GameSession, Question, ScoreboardEntry
from app.schemas import (
    AnswerLogItemView,
    AnswerRequest,
    AnswerResponse,
    AnswerOutcomeView,
    GameSummaryView,
    QuestionView,
    ScoreboardEntryView,
    SessionStatsView,
    StartSessionRequest,
    StartSessionResponse,
)
from app.services.engine import GameEngine
from app.services.scoreboard import ScoreboardStore
from app.services.session_manager import SessionStore

DATA_DIR.mkdir(parents=True, exist_ok=True)
FRONTEND_DIR.mkdir(parents=True, exist_ok=True)

engine = GameEngine()
sessions = SessionStore(engine)
scoreboard = ScoreboardStore()

app = FastAPI(title=APP_NAME, version=APP_VERSION)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR)), name="static")


def _grade_to_string(grade: int | str) -> str:
    return str(grade)


def _question_view(question: Question) -> QuestionView:
    return QuestionView(
        id=question.id,
        subject=question.subject,
        prompt=question.prompt,
        diagram_html=question.diagram_html,
    )


def _stats_view(session: GameSession) -> SessionStatsView:
    current = session.current_question_no
    if session.finished:
        current = session.total_questions
    return SessionStatsView(
        score=session.score,
        lives=session.lives,
        current_question=current,
        total_questions=session.total_questions,
        mistakes=session.mistakes,
        average_time_seconds=round(session.average_time, 2),
    )


def _scoreboard_entry_view(entry: ScoreboardEntry) -> ScoreboardEntryView:
    return ScoreboardEntryView(
        rank=entry.rank or 0,
        name=entry.name,
        age=entry.age,
        grade=entry.grade,
        score=entry.score,
        total_questions=entry.total_questions,
        avg_time_seconds=round(entry.avg_time, 2),
        subjects=entry.subjects,
    )


def _summary_view(session: GameSession) -> GameSummaryView:
    leaderboard = [_scoreboard_entry_view(row) for row in scoreboard.get_leaderboard()]
    answers = [
        AnswerLogItemView(
            question_no=row.question_no,
            subject=row.subject,
            prompt=row.prompt,
            your_answer=row.user_answer,
            correct_answer=row.correct_answer,
            correct=row.correct,
            explanation=row.explanation,
            elapsed_seconds=round(row.elapsed_seconds, 2),
            timed_out=row.timed_out,
        )
        for row in session.answer_log
    ]
    return GameSummaryView(
        score=session.score,
        total_questions=session.total_questions,
        mistakes=session.mistakes,
        average_time_seconds=round(session.average_time, 2),
        answers=answers,
        leaderboard=leaderboard,
    )


@app.get("/api/v1/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/v1/subjects")
def list_subjects() -> dict[str, list[dict[str, str]]]:
    items = [
        {"key": key, "label": SUBJECT_LABELS.get(key, key.title())}
        for key in SUPPORTED_SUBJECTS
    ]
    return {"subjects": items}


@app.get("/api/v1/scoreboard", response_model=list[ScoreboardEntryView])
def get_scoreboard(limit: int = Query(default=30, ge=1, le=30)) -> list[ScoreboardEntryView]:
    rows = scoreboard.get_leaderboard(limit=limit)
    return [_scoreboard_entry_view(row) for row in rows]


@app.post("/api/v1/sessions", response_model=StartSessionResponse)
def start_session(payload: StartSessionRequest) -> StartSessionResponse:
    if not engine.is_valid_age(payload.age):
        raise HTTPException(status_code=422, detail="Age must be between 8 and 99.")

    try:
        session = sessions.create_session(
            name=payload.name,
            age=payload.age,
            subjects=payload.subjects,
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    if session.current_question is None:
        raise HTTPException(status_code=500, detail="Could not generate first question.")

    return StartSessionResponse(
        session_id=session.id,
        player_name=session.name,
        age=session.age,
        grade=_grade_to_string(session.grade),
        subjects=session.subjects,
        total_questions=session.total_questions,
        stats=_stats_view(session),
        question=_question_view(session.current_question),
    )


@app.post("/api/v1/sessions/{session_id}/answer", response_model=AnswerResponse)
def answer_question(session_id: str, payload: AnswerRequest) -> AnswerResponse:
    try:
        session, result = sessions.submit_answer(
            session_id=session_id,
            question_id=payload.question_id,
            user_answer=payload.answer,
            elapsed_seconds=payload.elapsed_seconds,
        )
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    summary = None
    if result.finished:
        scoreboard.add_entry(
            name=session.name,
            age=session.age,
            grade=_grade_to_string(session.grade),
            score=session.score,
            total_questions=session.total_questions,
            avg_time=session.average_time,
            subjects=", ".join(session.subjects),
        )
        summary = _summary_view(session)

    return AnswerResponse(
        finished=result.finished,
        outcome=AnswerOutcomeView(
            correct=result.correct,
            timed_out=result.timed_out,
            your_answer=result.user_answer,
            correct_answer=result.correct_answer,
            explanation=result.explanation,
        ),
        stats=_stats_view(session),
        next_question=_question_view(result.next_question) if result.next_question else None,
        summary=summary,
    )


@app.get("/", include_in_schema=False)
def index() -> FileResponse:
    path = FRONTEND_DIR / "index.html"
    if not path.exists():
        raise HTTPException(status_code=404, detail="Frontend index.html not found.")
    return FileResponse(path)


@app.get("/favicon.ico", include_in_schema=False)
def favicon() -> FileResponse:
    icon_path = FRONTEND_DIR / "favicon.ico"
    if icon_path.exists():
        return FileResponse(icon_path)
    raise HTTPException(status_code=404, detail="No favicon configured.")
