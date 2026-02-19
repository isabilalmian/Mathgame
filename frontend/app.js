const MAX_SECONDS_PER_QUESTION = 180;

const state = {
  sessionId: null,
  currentQuestion: null,
  nextQuestion: null,
  timerId: null,
  questionStartedAtMs: null,
  awaitingNext: false,
  submitting: false,
};

const el = {
  startScreen: document.getElementById("start-screen"),
  gameScreen: document.getElementById("game-screen"),
  resultsScreen: document.getElementById("results-screen"),
  startForm: document.getElementById("start-form"),
  answerForm: document.getElementById("answer-form"),
  subjectGrid: document.getElementById("subject-grid"),
  startError: document.getElementById("start-error"),
  statQuestion: document.getElementById("stat-question"),
  statScore: document.getElementById("stat-score"),
  statLives: document.getElementById("stat-lives"),
  statTimer: document.getElementById("stat-timer"),
  statAvg: document.getElementById("stat-avg"),
  questionSubject: document.getElementById("question-subject"),
  questionText: document.getElementById("question-text"),
  diagramContainer: document.getElementById("diagram-container"),
  answerInput: document.getElementById("answer-input"),
  feedback: document.getElementById("feedback"),
  nextBtn: document.getElementById("next-btn"),
  resultsHeadline: document.getElementById("results-headline"),
  resultsMeta: document.getElementById("results-meta"),
  answerReview: document.getElementById("answer-review"),
  resultsScoreboard: document.getElementById("results-scoreboard"),
  startScoreboard: document.getElementById("start-scoreboard"),
  playAgainBtn: document.getElementById("play-again-btn"),
};

function formatTime(seconds) {
  const safe = Math.max(0, Math.floor(seconds || 0));
  const m = Math.floor(safe / 60);
  const s = safe % 60;
  return `${m}:${s < 10 ? "0" : ""}${s}`;
}

function htmlEscape(raw) {
  return String(raw)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;");
}

async function api(path, options = {}) {
  const res = await fetch(path, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!res.ok) {
    let detail = "Request failed.";
    try {
      const data = await res.json();
      if (typeof data.detail === "string") {
        detail = data.detail;
      } else if (Array.isArray(data.detail) && data.detail.length > 0) {
        detail = data.detail[0].msg || detail;
      }
    } catch (_err) {
      // Ignore parsing errors and use default message.
    }
    throw new Error(detail);
  }
  return res.json();
}

function showScreen(screen) {
  el.startScreen.classList.add("hidden");
  el.gameScreen.classList.add("hidden");
  el.resultsScreen.classList.add("hidden");
  screen.classList.remove("hidden");
}

function setFeedback(kind, text) {
  el.feedback.classList.remove("hidden", "good", "bad");
  el.feedback.classList.add(kind === "good" ? "good" : "bad");
  el.feedback.innerHTML = text;
}

function clearFeedback() {
  el.feedback.classList.add("hidden");
  el.feedback.classList.remove("good", "bad");
  el.feedback.textContent = "";
}

function updateStats(stats) {
  el.statQuestion.textContent = `${stats.current_question}/${stats.total_questions}`;
  el.statScore.textContent = String(stats.score);
  el.statLives.textContent = String(stats.lives);
  el.statAvg.textContent = formatTime(stats.average_time_seconds);
}

function stopTimer() {
  if (state.timerId) {
    clearInterval(state.timerId);
    state.timerId = null;
  }
}

function elapsedSecondsForQuestion() {
  if (!state.questionStartedAtMs) {
    return 0;
  }
  return Math.floor((Date.now() - state.questionStartedAtMs) / 1000);
}

function startTimer() {
  stopTimer();
  state.questionStartedAtMs = Date.now();
  el.statTimer.textContent = "0:00";
  state.timerId = setInterval(() => {
    const elapsed = elapsedSecondsForQuestion();
    el.statTimer.textContent = formatTime(elapsed);
    if (elapsed >= MAX_SECONDS_PER_QUESTION) {
      stopTimer();
      if (!state.awaitingNext && !state.submitting) {
        submitCurrentAnswer("", true);
      }
    }
  }, 1000);
}

function renderQuestion(question) {
  state.currentQuestion = question;
  state.nextQuestion = null;
  state.awaitingNext = false;
  clearFeedback();
  el.nextBtn.classList.add("hidden");
  el.answerInput.disabled = false;
  el.answerInput.value = "";
  el.questionSubject.textContent = question.subject.toUpperCase();
  el.questionText.textContent = question.prompt;
  if (question.diagram_html) {
    el.diagramContainer.innerHTML = question.diagram_html;
  } else {
    el.diagramContainer.innerHTML = "";
  }
  startTimer();
  el.answerInput.focus();
}

function renderScoreboard(target, rows) {
  if (!rows || rows.length === 0) {
    target.innerHTML = "<p class='muted'>No scores yet.</p>";
    return;
  }
  const head =
    "<table><thead><tr><th>#</th><th>Name</th><th>Age</th><th>Grade</th><th>Score</th><th>Avg</th><th>Subjects</th></tr></thead><tbody>";
  const body = rows
    .map(
      (row) =>
        `<tr><td>${row.rank}</td><td>${htmlEscape(row.name)}</td><td>${row.age}</td><td>${htmlEscape(
          row.grade
        )}</td><td>${row.score}/${row.total_questions}</td><td>${formatTime(
          row.avg_time_seconds
        )}</td><td>${htmlEscape(row.subjects)}</td></tr>`
    )
    .join("");
  target.innerHTML = `${head}${body}</tbody></table>`;
}

async function loadScoreboard() {
  const rows = await api("/api/v1/scoreboard");
  renderScoreboard(el.startScoreboard, rows);
}

function resetLocalState() {
  stopTimer();
  state.sessionId = null;
  state.currentQuestion = null;
  state.nextQuestion = null;
  state.questionStartedAtMs = null;
  state.awaitingNext = false;
  state.submitting = false;
  el.statTimer.textContent = "0:00";
}

async function submitCurrentAnswer(answerValue, forcedByTimeout = false) {
  if (!state.sessionId || !state.currentQuestion || state.awaitingNext || state.submitting) {
    return;
  }
  state.submitting = true;
  stopTimer();
  const elapsed = forcedByTimeout ? MAX_SECONDS_PER_QUESTION : elapsedSecondsForQuestion();
  try {
    const response = await api(`/api/v1/sessions/${state.sessionId}/answer`, {
      method: "POST",
      body: JSON.stringify({
        question_id: state.currentQuestion.id,
        answer: answerValue,
        elapsed_seconds: elapsed,
      }),
    });

    updateStats(response.stats);
    const message = response.outcome.correct
      ? `<strong>Correct.</strong> ${htmlEscape(response.outcome.explanation)}`
      : response.outcome.timed_out
      ? `<strong>Time up.</strong> Correct answer: <strong>${htmlEscape(
          response.outcome.correct_answer
        )}</strong>. ${htmlEscape(response.outcome.explanation)}`
      : `<strong>Wrong.</strong> Correct answer: <strong>${htmlEscape(
          response.outcome.correct_answer
        )}</strong>. ${htmlEscape(response.outcome.explanation)}`;
    setFeedback(response.outcome.correct ? "good" : "bad", message);

    if (response.finished) {
      state.awaitingNext = true;
      el.answerInput.disabled = true;
      showResults(response.summary);
      return;
    }

    state.nextQuestion = response.next_question;
    state.awaitingNext = true;
    el.answerInput.disabled = true;
    el.nextBtn.classList.remove("hidden");
    el.nextBtn.focus();
  } catch (err) {
    setFeedback("bad", htmlEscape(err.message || "Failed to submit answer."));
  } finally {
    state.submitting = false;
  }
}

function showResults(summary) {
  stopTimer();
  showScreen(el.resultsScreen);
  const scoreLine = `${summary.score} / ${summary.total_questions}`;
  el.resultsHeadline.textContent = `Final score: ${scoreLine}`;
  el.resultsMeta.textContent = `Mistakes: ${summary.mistakes}, average time: ${formatTime(
    summary.average_time_seconds
  )}`;

  if (!summary.answers || summary.answers.length === 0) {
    el.answerReview.innerHTML = "<p class='muted'>No answers recorded.</p>";
  } else {
    el.answerReview.innerHTML = summary.answers
      .map((row) => {
        const klass = row.correct ? "good" : "bad";
        return `
          <div class="answer-row ${klass}">
            <div><strong>${row.question_no}. [${htmlEscape(row.subject)}]</strong> ${htmlEscape(
          row.prompt
        )}</div>
            <div>Your answer: ${htmlEscape(row.your_answer || "-")} | Correct: <strong>${htmlEscape(
          row.correct_answer
        )}</strong></div>
            <div>${row.timed_out ? "Timed out. " : ""}${htmlEscape(row.explanation)}</div>
          </div>
        `;
      })
      .join("");
  }
  renderScoreboard(el.resultsScoreboard, summary.leaderboard || []);
  loadScoreboard().catch(() => {});
}

async function loadSubjects() {
  const payload = await api("/api/v1/subjects");
  const rows = payload.subjects || [];
  el.subjectGrid.innerHTML = rows
    .map((subject, idx) => {
      const checked = subject.key === "maths" || idx === 0;
      return `
      <label class="subject-item">
        <input type="checkbox" name="subject" value="${htmlEscape(subject.key)}" ${
        checked ? "checked" : ""
      } />
        <span>${htmlEscape(subject.label)}</span>
      </label>`;
    })
    .join("");
}

el.startForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  el.startError.textContent = "";
  const name = document.getElementById("player-name").value.trim();
  const age = Number.parseInt(document.getElementById("player-age").value, 10);
  const checked = Array.from(document.querySelectorAll('input[name="subject"]:checked')).map(
    (node) => node.value
  );

  if (!name) {
    el.startError.textContent = "Please enter a name.";
    return;
  }
  if (!Number.isFinite(age)) {
    el.startError.textContent = "Please enter a valid age.";
    return;
  }
  if (checked.length === 0) {
    el.startError.textContent = "Please select at least one subject.";
    return;
  }

  try {
    const response = await api("/api/v1/sessions", {
      method: "POST",
      body: JSON.stringify({
        name,
        age,
        subjects: checked,
      }),
    });
    resetLocalState();
    state.sessionId = response.session_id;
    showScreen(el.gameScreen);
    updateStats(response.stats);
    renderQuestion(response.question);
  } catch (err) {
    el.startError.textContent = err.message || "Could not start game.";
  }
});

el.answerForm.addEventListener("submit", (event) => {
  event.preventDefault();
  submitCurrentAnswer(el.answerInput.value.trim(), false);
});

el.nextBtn.addEventListener("click", () => {
  if (!state.nextQuestion) {
    return;
  }
  el.nextBtn.classList.add("hidden");
  renderQuestion(state.nextQuestion);
});

el.playAgainBtn.addEventListener("click", () => {
  resetLocalState();
  showScreen(el.startScreen);
  clearFeedback();
});

async function boot() {
  try {
    await loadSubjects();
    await loadScoreboard();
  } catch (err) {
    el.startError.textContent = err.message || "Could not load game resources.";
  }
}

boot();
