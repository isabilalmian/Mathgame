from __future__ import annotations

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_health_and_subjects() -> None:
    health = client.get("/api/v1/health")
    assert health.status_code == 200
    assert health.json()["status"] == "ok"

    subjects = client.get("/api/v1/subjects")
    assert subjects.status_code == 200
    payload = subjects.json()
    assert "subjects" in payload
    assert any(row["key"] == "maths" for row in payload["subjects"])


def test_start_session_and_answer_once() -> None:
    start = client.post(
        "/api/v1/sessions",
        json={
            "name": "Tester",
            "age": 12,
            "subjects": ["maths"],
        },
    )
    assert start.status_code == 200
    started = start.json()
    session_id = started["session_id"]
    question = started["question"]

    answer = client.post(
        f"/api/v1/sessions/{session_id}/answer",
        json={
            "question_id": question["id"],
            "answer": "",
            "elapsed_seconds": 5,
        },
    )
    assert answer.status_code == 200
    payload = answer.json()
    assert "finished" in payload
    assert "outcome" in payload
    assert "stats" in payload
