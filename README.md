# Mathgame Python Platform

This project is a migration of the original HTML-only game into a proper backend + frontend architecture:

- **Backend:** Python + FastAPI (`app/`)
- **Frontend:** HTML/CSS/JS (`frontend/`)
- **Persistence:** SQLite scoreboard (`data/scoreboard.db`)

The old single-file implementation still exists as `index.html` for reference.

---

## Why this migration was needed (review of old implementation)

The original game worked, but it had architecture limits:

1. **Monolithic file size**
   - One huge `index.html` contained UI, game logic, translations, and question banks.
   - This increased initial page load and memory pressure in the browser.

2. **Tight coupling**
   - UI state management and game engine logic were interleaved in one script.
   - Hard to test and hard to extend safely.

3. **Client-only trust**
   - Scoreboard and correctness logic were browser-side.
   - Easy to tamper with and difficult to run centralized analytics/ranking.

4. **Maintainability bottleneck**
   - Adding subjects and balancing difficulty required editing one giant file.
   - No clear service boundaries.

---

## New architecture

```text
app/
  config.py                # global constants and paths
  main.py                  # FastAPI app + API endpoints + static frontend serving
  models.py                # dataclasses (session, question, answer logs)
  schemas.py               # request/response schemas
  services/
    engine.py              # question generation + answer matching
    session_manager.py     # in-memory active sessions
    scoreboard.py          # SQLite leaderboard storage
    question_bank.py       # static subject facts/banks

frontend/
  index.html               # web UI
  styles.css               # styling
  app.js                   # API-driven gameplay loop

data/
  scoreboard.db            # runtime database (gitignored)
```

### Core behavior preserved

- Age-based grade mapping
- Multi-subject quiz sessions
- Lives + score + per-question timer
- Feedback with explanation
- End-of-game summary
- Leaderboard ranking by score, then average answer time

---

## Run locally

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Open:
- `http://localhost:8000/`

---

## API quick reference

- `GET /api/v1/health`
- `GET /api/v1/subjects`
- `GET /api/v1/scoreboard`
- `POST /api/v1/sessions`
- `POST /api/v1/sessions/{session_id}/answer`

---

## Deployment notes

This repository is ready for deployment on platforms such as Render, Railway, Fly.io, or a VPS:

- Start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- Serve static frontend from the same FastAPI app.

---

Created by Isa Mian (original game), architecture migration by AI assistant.
