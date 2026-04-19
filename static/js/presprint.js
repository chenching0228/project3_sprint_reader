const moduleId = "M001";

async function loadModuleMetadata() {
  try {
    const response = await fetch(`/api/modules/${moduleId}/metadata`);

    if (!response.ok) {
      throw new Error("Failed to load module metadata");
    }

    const data = await response.json();

    document.getElementById("module-title").textContent = data.source_document;
    document.getElementById("module-source").textContent = `來源：${data.source}`;
    document.getElementById("warning-text").textContent = data.warning_text;

    const tagsContainer = document.getElementById("module-tags");
    tagsContainer.innerHTML = "";

    data.domains.forEach(tag => {
      const span = document.createElement("span");
      span.className = "tag";
      span.textContent = `#${tag}`;
      tagsContainer.appendChild(span);
    });
  } catch (error) {
    console.error(error);
    alert("模組資料載入失敗，請稍後再試。");
  }
}

async function startReading() {
  try {
    const response = await fetch("/api/sessions/start", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        agent_id: "demo_user",
        module_id: moduleId
      })
    });

    if (!response.ok) {
      throw new Error("Failed to start session");
    }

    const data = await response.json();

    window.location.href = `/reader?module_id=${moduleId}&sprint_id=${data.sprint_id}`;
  } catch (error) {
    console.error(error);
    alert("無法開始閱讀，請稍後再試。");
  }
}

document.addEventListener("DOMContentLoaded", () => {
  loadModuleMetadata();

  const startButton = document.getElementById("start-button");
  startButton.addEventListener("click", startReading);
});