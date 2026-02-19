from __future__ import annotations

import random

from app.services.engine import GameEngine


def test_grade_from_age_boundaries() -> None:
    engine = GameEngine()
    assert engine.get_grade_from_age(8) == 4
    assert engine.get_grade_from_age(10) == 5
    assert engine.get_grade_from_age(12) == 7
    assert engine.get_grade_from_age(18) == 12
    assert engine.get_grade_from_age(25) == "university"


def test_answers_match_numeric_and_text() -> None:
    engine = GameEngine()
    assert engine.answers_match("1.5000001", 1.5)
    assert engine.answers_match("Berlin", "berlin")
    assert not engine.answers_match("berlin", "paris")


def test_generate_question_for_each_subject() -> None:
    engine = GameEngine()
    rng = random.Random(1234)
    subjects = [
        "maths",
        "chemistry",
        "biology",
        "physics",
        "astronomy",
        "geography",
        "history",
    ]
    for subject in subjects:
        question = engine.generate_question(subject, age=13, rng=rng, used_prompts=set())
        assert question.subject == subject
        assert isinstance(question.prompt, str)
        assert question.prompt
