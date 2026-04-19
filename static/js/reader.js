const urlParams = new URLSearchParams(window.location.search);
const moduleId = urlParams.get("module_id");
const sprintId = urlParams.get("sprint_id");

const appState = {
  currentCardIndex: 0,
  totalCards: 0,
  remainingTime: 420,
  isPaused: false,
  tabSwitchCount: 0,
  sessionId: sprintId,
  completionStatus: "in_progress",
  isLocked: false,
  flashcards: [],
  timerInterval: null,
  progressSyncInterval: null
};

let touchStartX = 0;
let touchEndX = 0;

async function loadFlashcards() {
  try {
    const response = await fetch(`/api/modules/${moduleId}/flashcards`);

    if (!response.ok) {
      throw new Error("Failed to load flashcards");
    }

    const data = await response.json();

    appState.flashcards = data.pages;
    appState.totalCards = data.pages.length;

    renderCard();
  } catch (error) {
    console.error(error);
    alert("卡片資料載入失敗。");
  }
}

function updateStoryProgress() {
  const container = document.getElementById("story-progress");
  if (!container) return;

  container.innerHTML = "";
  for (let i = 0; i < appState.totalCards; i++) {
    const seg = document.createElement("div");
    seg.className = "story-progress-segment" + (i <= appState.currentCardIndex ? " filled" : "");
    container.appendChild(seg);
  }
}

function renderCard() {
  const card = appState.flashcards[appState.currentCardIndex];
  if (!card) return;

  document.getElementById("progress-text").textContent =
    `第 ${appState.currentCardIndex + 1} 張 / 共 ${appState.totalCards} 張`;

  updateStoryProgress();

  document.getElementById("domain-tag").textContent = card.domain_tag;
  document.getElementById("card-title").textContent = card.title;

  const contentContainer = document.getElementById("card-content");
  contentContainer.innerHTML = "";

  if (Array.isArray(card.page_content_json.text)) {
    const ul = document.createElement("ul");

    card.page_content_json.text.forEach(line => {
      const li = document.createElement("li");
      li.textContent = line;
      ul.appendChild(li);
    });

    contentContainer.appendChild(ul);
  } else {
    contentContainer.textContent = card.page_content_json.text || "";
  }

  updateControlButtons();
}

function goToNextCard() {
  if (appState.isLocked) return;

  if (appState.currentCardIndex < appState.totalCards - 1) {
    appState.currentCardIndex += 1;
    renderCard();
  } else {
    finishReadingEarly();
  }
}

function goToPrevCard() {
  if (appState.isLocked) return;

  if (appState.currentCardIndex > 0) {
    appState.currentCardIndex -= 1;
    renderCard();
  }
}

function updateControlButtons() {
  const prevButton = document.getElementById("prev-button");
  const nextButton = document.getElementById("next-button");

  prevButton.disabled = appState.currentCardIndex === 0 || appState.isLocked;

  if (appState.currentCardIndex === appState.totalCards - 1) {
    nextButton.textContent = "完成閱讀";
  } else {
    nextButton.textContent = "下一張";
  }

  nextButton.disabled = appState.isLocked;
}

function formatTime(seconds) {
  const minutes = Math.floor(seconds / 60);
  const secs = seconds % 60;

  return `${String(minutes).padStart(2, "0")}:${String(secs).padStart(2, "0")}`;
}

function updateTimerDisplay() {
  document.getElementById("timer").textContent = formatTime(appState.remainingTime);
}

function startTimer() {
  if (appState.timerInterval) {
    clearInterval(appState.timerInterval);
    appState.timerInterval = null;
  }

  updateTimerDisplay();
  console.log("[Timer] startTimer() called, interval starting");

  appState.timerInterval = setInterval(() => {
    if (appState.isPaused || appState.isLocked) return;

    appState.remainingTime -= 1;
    console.log("[Timer] tick, remainingTime =", appState.remainingTime);
    updateTimerDisplay();

    if (appState.remainingTime <= 0) {
      appState.remainingTime = 0;
      updateTimerDisplay();
      timeOutReading();
    }
  }, 1000);
}

function stopTimer() {
  if (appState.timerInterval) {
    clearInterval(appState.timerInterval);
    appState.timerInterval = null;
  }
}

function startProgressSync() {
  appState.progressSyncInterval = setInterval(async () => {
    if (appState.isPaused || appState.isLocked) return;

    try {
      await fetch(`/api/sessions/${appState.sessionId}/progress`, {
        method: "PATCH",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({
          remaining_time: appState.remainingTime
        })
      });
    } catch (error) {
      console.error("Progress sync failed:", error);
    }
  }, 10000);
}

function stopProgressSync() {
  if (appState.progressSyncInterval) {
    clearInterval(appState.progressSyncInterval);
    appState.progressSyncInterval = null;
  }
}

async function notifyPause() {
  try {
    const response = await fetch(`/api/sessions/${appState.sessionId}/pause`, {
      method: "PATCH",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        remaining_time: appState.remainingTime
      })
    });

    const data = await response.json();
    appState.isPaused = data.is_paused;
    appState.tabSwitchCount = data.tab_switch_count;
  } catch (error) {
    console.error("Pause failed:", error);
  }
}

async function notifyResume() {
  try {
    const response = await fetch(`/api/sessions/${appState.sessionId}/resume`, {
      method: "PATCH",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        remaining_time: appState.remainingTime
      })
    });

    const data = await response.json();
    appState.isPaused = data.is_paused;
    appState.tabSwitchCount = data.tab_switch_count;
  } catch (error) {
    console.error("Resume failed:", error);
  }
}

document.addEventListener("visibilitychange", async () => {
  if (appState.isLocked) return;

  if (document.hidden) {
    appState.isPaused = true;
    notifyPause(); // fire-and-forget: do NOT await, so isPaused stays true
  } else {
    appState.isPaused = false;
    notifyResume(); // fire-and-forget: do NOT await, so isPaused is already false
  }
});


async function completeSession(status) {
  if (appState.isLocked) return;

  appState.isLocked = true;
  appState.completionStatus = status;

  clearInterval(appState.timerInterval);
  clearInterval(appState.progressSyncInterval);

  try {
    const response = await fetch(`/api/sessions/${appState.sessionId}/complete`, {
      method: "PATCH",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        completion_status: status,
        remaining_time: appState.remainingTime
      })
    });

    const data = await response.json();

    window.location.href =
      `/handoff?session_id=${data.session_id}&module_id=${moduleId}&status=${data.completion_status}`;
  } catch (error) {
    console.error("Complete failed:", error);
    alert("完成流程失敗，請稍後再試。");
  }
}

function finishReadingEarly() {
  completeSession("finished_early");
}

function timeOutReading() {
  completeSession("timed_out");
}

function handleSwipe() {
  if (appState.isLocked) return;

  const swipeDistance = touchEndX - touchStartX;
  const threshold = 50;

  if (swipeDistance < -threshold) {
    goToNextCard();
  } else if (swipeDistance > threshold) {
    goToPrevCard();
  }
}

document.addEventListener("DOMContentLoaded", async () => {
  console.log("[Init] DOMContentLoaded fired");
  document.getElementById("prev-button").addEventListener("click", goToPrevCard);
  document.getElementById("next-button").addEventListener("click", goToNextCard);

  await loadFlashcards();
  updateTimerDisplay();
  startTimer();
  startProgressSync();

  const readerCard = document.querySelector(".reader-card");

  readerCard.addEventListener("touchstart", (event) => {
    touchStartX = event.changedTouches[0].screenX;
  });

  readerCard.addEventListener("touchend", (event) => {
    touchEndX = event.changedTouches[0].screenX;
    handleSwipe();
  });
});