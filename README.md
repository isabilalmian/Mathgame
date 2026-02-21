# Maths and Learning Game

An interactive browser-based learning game for ages 8-99 with curriculum-aware quiz content, guided learning pages, language tools, and a local scoreboard.

This repository is a single-page web app (no build step) focused on age-appropriate learning paths and multilingual support.

## Highlights

- Browser-only app: open and run directly from `index.html`.
- Quiz mode with score, lives, timer, feedback, and end-of-game summary.
- Learn mode with topic explanations and table-of-contents navigation.
- Language-learning modes:
  - Info texts
  - Built-in dictionary lookup
  - Vocabulary lookup/translation
- Curriculum selection based on chosen language/region.
- Age-based grade mapping from Grade 4 to university level.
- Multi-subject support (maths, science, social studies, and languages).
- Local scoreboard with ranking and celebration effects (confetti/fireworks).

## Main Features

### 1) Age and curriculum aware learning

- Enter age to map content difficulty from school grades to advanced levels.
- Select curriculum options after language selection (for example:
  Germany regions, UK nations, US curricula, and other locale-specific options).
- Subject availability adapts by grade level.

### 2) Multiple study modes

- **Quiz mode**: answer generated questions and earn points.
- **Learn mode**: read structured explanations for selected subjects.
- **Language subject extras**:
  - **Info texts search**
  - **Dictionary**
  - **Vocabulary**

### 3) Game loop and scoring

- 10 questions per selected subject.
- Total questions = `10 x number_of_subjects`.
- Lives scale with subject count: `min(2 + subjects, 5)`.
- Max time per question: 3 minutes.
- Correct answer: +1 score.
- Wrong answer: -1 life.
- Results include:
  - final score
  - mistakes count
  - per-question summary
  - ranked scoreboard entry

### 4) Local scoreboard

- Stored in browser `localStorage`.
- Keeps up to 30 entries.
- Entries older than 30 days are removed.
- Ranking prioritizes higher score, then faster average time.

### 5) Multilingual experience

The interface includes support for many languages, including:
German, English (UK/US), French, Spanish, Arabic (with regional variants),
Pashto, Greek, Chinese (Simplified/Traditional), Russian, Turkish, Urdu,
Hindi, Italian, Portuguese, Japanese, Korean, and Bengali.

## Age to grade mapping

- Age 8-9 -> Grade 4
- Age 10-11 -> Grade 5
- Age 11-12 -> Grade 6
- Age 12-13 -> Grade 7
- Age 13-14 -> Grade 8
- Age 14-15 -> Grade 9
- Age 15-16 -> Grade 10
- Age 16-17 -> Grade 11
- Age 17-18 -> Grade 12
- Age 19+ -> University level

## Subjects (examples)

- Core: Maths
- Science: Chemistry, Biology, Physics, Astronomy
- Social studies: Geography, History, Laws and rights
- Languages: German, English, French, Latin, Spanish, Arabic variants,
  Pashto, Greek, Mandarin (Simplified/Traditional), Russian, Turkish, Urdu,
  Hindi, Italian, Portuguese, Japanese, Korean, Bengali, Dutch, Polish,
  Swedish, Vietnamese, Indonesian

## Run locally

No installation required.

1. Clone or download this repository.
2. Open `index.html` in a modern browser.

Optional: if you prefer serving files over HTTP:

```bash
python3 -m http.server 8000
```

Then open `http://localhost:8000`.

## Project structure

- `index.html` - app UI, styles, data, and game logic
- `README.md` - repository documentation

## Notes for maintainers

- Main tuning constants are near the script section in `index.html`:
  - `QUESTIONS_PER_SUBJECT`
  - `STARTING_LIVES`
  - `MAX_SECONDS_PER_QUESTION`
- Scoreboard key:
  - `SCOREBOARD_KEY = "mathsGameScoreboard"`
- Because everything is in one file, prefer small, isolated edits and test in-browser after changes.

---

Created by Isa Mian
