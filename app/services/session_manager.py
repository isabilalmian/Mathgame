from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
import random
import threading
import time
import uuid

from app.config import (
    MAX_LIVES,
    MAX_SECONDS_PER_QUESTION,
    QUESTIONS_PER_SUBJECT,
    SESSION_TTL_HOURS,
    SUPPORTED_SUBJECTS,
)
from app.models import AnswerLogEntry, GameSession, Question
from app.services.engine import GameEngine


@dataclass(slots=True)
class SubmissionResult:
    correct: bool
    timed_out: bool
    correct_answer: str
    explanation: str
    user_answer: str
    finished: bool
    next_question: Question | None


class SessionStore:
    def __init__(self, engine: GameEngine) -> None:
        self._engine = engine
        self._lock = threading.Lock()
        self._sessions: dict[str, GameSession] = {}

    def create_session(self, name: str, age: int, subjects: list[str]) -> GameSession:
        if not subjects:
            raise ValueError("Please choose at least one subject.")
        if not self._engine.is_valid_age(age):
            raise ValueError("Age must be between 8 and 99.")

        cleaned_subjects = self._clean_subjects(subjects)
        if not cleaned_subjects:
            raise ValueError("No supported subjects were provided.")

        rng = random.Random()
        rng.seed(uuid.uuid4().int)
        plan = self._build_plan(cleaned_subjects, rng)
        session_id = uuid.uuid4().hex
        grade = self._engine.get_grade_from_age(age)
        lives = min(2 + len(cleaned_subjects), MAX_LIVES)

        session = GameSession(
            id=session_id,
            name=name.strip()[:30],
            age=age,
            grade=grade,
            subjects=cleaned_subjects,
            question_plan=plan,
            total_questions=len(plan),
            lives=lives,
            rng=rng,
        )
        self._generate_current_question(session)
        with self._lock:
            self._cleanup_locked()
            self._sessions[session.id] = session
        return session

    def get_session(self, session_id: str) -> GameSession | None:
        with self._lock:
            self._cleanup_locked()
            session = self._sessions.get(session_id)
            if session is None:
                return None
            session.updated_at = datetime.now(timezone.utc)
            return session

    def submit_answer(
        self,
        session_id: str,
        question_id: str,
        user_answer: str,
        elapsed_seconds: float | int,
    ) -> tuple[GameSession, SubmissionResult]:
        with self._lock:
            self._cleanup_locked()
            session = self._sessions.get(session_id)
            if session is None:
                raise KeyError("Session not found.")
            if session.finished:
                raise ValueError("This session has already finished.")
            if session.current_question is None:
                raise ValueError("Session has no active question.")
            if session.current_question.id != question_id:
                raise ValueError("Question id does not match the active question.")

            question = session.current_question
            client_elapsed = float(elapsed_seconds) if elapsed_seconds is not None else 0.0
            if client_elapsed < 0:
                client_elapsed = 0.0
            server_elapsed = max(0.0, time.time() - question.created_at)
            elapsed = min(MAX_SECONDS_PER_QUESTION, max(client_elapsed, server_elapsed))
            timed_out = elapsed >= MAX_SECONDS_PER_QUESTION

            correct = (not timed_out) and self._engine.answers_match(user_answer, question.answer)
            if correct:
                session.score += 1
            else:
                session.lives -= 1

            session.elapsed_times.append(elapsed)
            correct_answer = self._engine.format_answer(question.answer)
            session.answer_log.append(
                AnswerLogEntry(
                    question_no=session.current_question_no,
                    question_id=question.id,
                    subject=question.subject,
                    prompt=question.prompt,
                    user_answer=(user_answer or "").strip(),
                    correct_answer=correct_answer,
                    correct=correct,
                    explanation=question.explanation,
                    elapsed_seconds=elapsed,
                    timed_out=timed_out,
                )
            )

            is_last_question = session.question_cursor >= (session.total_questions - 1)
            finished = session.lives <= 0 or is_last_question
            next_question = None

            if finished:
                session.finished = True
                session.current_question = None
            else:
                session.question_cursor += 1
                next_question = self._generate_current_question(session)

            session.updated_at = datetime.now(timezone.utc)
            result = SubmissionResult(
                correct=correct,
                timed_out=timed_out,
                correct_answer=correct_answer,
                explanation=question.explanation,
                user_answer=(user_answer or "").strip(),
                finished=finished,
                next_question=next_question,
            )
            return session, result

    def _generate_current_question(self, session: GameSession) -> Question:
        subject = session.question_plan[session.question_cursor]
        used_prompts = session.used_prompts.setdefault(subject, set())
        question = self._engine.generate_question(
            subject=subject,
            age=session.age,
            rng=session.rng,
            used_prompts=used_prompts,
        )
        session.current_question = question
        session.updated_at = datetime.now(timezone.utc)
        return question

    def _build_plan(self, subjects: list[str], rng: random.Random) -> list[str]:
        plan: list[str] = []
        for subject in subjects:
            for _ in range(QUESTIONS_PER_SUBJECT):
                plan.append(subject)
        rng.shuffle(plan)
        return plan

    def _clean_subjects(self, subjects: list[str]) -> list[str]:
        cleaned: list[str] = []
        seen: set[str] = set()
        for subject in subjects:
            s = (subject or "").strip().lower()
            if not s or s in seen:
                continue
            if s not in SUPPORTED_SUBJECTS:
                continue
            cleaned.append(s)
            seen.add(s)
        return cleaned

    def _cleanup_locked(self) -> None:
        now = datetime.now(timezone.utc)
        ttl = timedelta(hours=SESSION_TTL_HOURS)
        expired = [
            sid
            for sid, session in self._sessions.items()
            if (now - session.updated_at) > ttl
        ]
        for sid in expired:
            self._sessions.pop(sid, None)
