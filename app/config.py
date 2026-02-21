from pathlib import Path

APP_NAME = "Mathgame Python Platform"
APP_VERSION = "1.0.0"

MIN_AGE = 8
MAX_AGE = 99
QUESTIONS_PER_SUBJECT = 10
MAX_SECONDS_PER_QUESTION = 180
MAX_LIVES = 5

SCOREBOARD_DAYS = 30
MAX_LEADERBOARD = 30

SESSION_TTL_HOURS = 6

SUPPORTED_SUBJECTS = [
    "maths",
    "chemistry",
    "biology",
    "physics",
    "astronomy",
    "geography",
    "history",
]

SUBJECT_LABELS = {
    "maths": "Maths",
    "chemistry": "Chemistry",
    "biology": "Biology",
    "physics": "Physics",
    "astronomy": "Astronomy",
    "geography": "Geography",
    "history": "History",
}

ROOT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT_DIR / "data"
SCOREBOARD_DB_PATH = DATA_DIR / "scoreboard.db"
FRONTEND_DIR = ROOT_DIR / "frontend"
