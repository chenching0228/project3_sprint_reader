document.addEventListener("DOMContentLoaded", () => {
  const urlParams = new URLSearchParams(window.location.search);
  const sessionId = urlParams.get("session_id");
  const moduleId = urlParams.get("module_id");

  setTimeout(() => {
    window.location.href = `/quiz?session_id=${sessionId}&module_id=${moduleId}`;
  }, 2000);
});