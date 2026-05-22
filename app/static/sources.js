const form = document.getElementById("upload-form");
const output = document.getElementById("upload-result");
const textForm = document.getElementById("text-upload-form");
const textOutput = document.getElementById("text-upload-result");
const compileButton = document.getElementById("compile-wiki");
const compileTogafButton = document.getElementById("compile-togaf");
const lintButton = document.getElementById("lint-wiki");
const codexStatus = document.getElementById("codex-status");
const codexLivePanel = document.getElementById("codex-live-panel");
const codexLiveDot = document.getElementById("codex-live-dot");
const codexLiveState = document.getElementById("codex-live-state");
const codexLiveMode = document.getElementById("codex-live-mode");
const codexLiveStarted = document.getElementById("codex-live-started");
const codexLiveFinished = document.getElementById("codex-live-finished");
const codexLiveReturncode = document.getElementById("codex-live-returncode");
const codexLiveOutput = document.getElementById("codex-live-output");
const wikiLanguage = document.getElementById("wiki-language");
const sourceList = document.getElementById("source-list");
const sourceCount = document.getElementById("source-count");
const processedList = document.getElementById("processed-list");
const processedCount = document.getElementById("processed-count");

let codexWasRunning = false;
const storedWikiLanguage = window.localStorage.getItem("wiki-language");
if (wikiLanguage && storedWikiLanguage && !wikiLanguage.disabled) {
  wikiLanguage.value = storedWikiLanguage;
}

function updateSourceCount() {
  if (!sourceList || !sourceCount) {
    return;
  }
  sourceCount.textContent = String(sourceList.querySelectorAll("li[data-rel-path]").length);
}

function updateProcessedCount() {
  if (!processedList || !processedCount) {
    return;
  }
  processedCount.textContent = String(processedList.querySelectorAll("li[data-rel-path]").length);
}

function shortTime(value) {
  if (!value) {
    return "-";
  }
  return String(value).replace("T", " ");
}

function renderCodexLive(data) {
  if (!codexLivePanel) {
    return;
  }

  const isRunning = Boolean(data.running);
  const ok = data.ok;
  codexLivePanel.classList.toggle("is-running", isRunning);
  codexLivePanel.classList.toggle("is-ok", !isRunning && ok === true);
  codexLivePanel.classList.toggle("is-error", !isRunning && ok === false);

  if (codexLiveDot) {
    codexLiveDot.className = "codex-live-dot";
    if (isRunning) {
      codexLiveDot.classList.add("running");
    } else if (ok === true) {
      codexLiveDot.classList.add("ok");
    } else if (ok === false) {
      codexLiveDot.classList.add("error");
    }
  }

  if (codexLiveState) {
    if (isRunning) {
      codexLiveState.textContent = "Running";
    } else if (ok === true) {
      codexLiveState.textContent = "Completed";
    } else if (ok === false) {
      codexLiveState.textContent = "Failed";
    } else {
      codexLiveState.textContent = "Idle";
    }
  }

  if (codexLiveMode) {
    codexLiveMode.textContent = data.mode || "-";
  }
  if (codexLiveStarted) {
    codexLiveStarted.textContent = shortTime(data.started_at);
  }
  if (codexLiveFinished) {
    codexLiveFinished.textContent = shortTime(data.finished_at || data.last_output_at);
  }
  if (codexLiveReturncode) {
    codexLiveReturncode.textContent = data.returncode === null || data.returncode === undefined ? "-" : String(data.returncode);
  }

  if (codexLiveOutput) {
    const events = Array.isArray(data.events) ? data.events : [];
    if (events.length === 0) {
      codexLiveOutput.textContent = data.stdout || data.stderr || "No Codex run yet.";
      return;
    }
    codexLiveOutput.textContent = events
      .map((event) => {
        const time = shortTime(event.time).slice(11) || "--:--:--";
        const stream = (event.stream || "status").toUpperCase().padEnd(6, " ");
        return `${time} ${stream} ${event.text || ""}`;
      })
      .join("\n");
    if (isRunning) {
      codexLiveOutput.scrollTop = codexLiveOutput.scrollHeight;
    }
  }
}

async function refreshCodexStatus() {
  if (!codexStatus) {
    return;
  }

  const resp = await fetch("/api/wiki/status");
  const data = await resp.json();
  let message = data.message || "Status unavailable.";
  if (data.running) {
    message = `${message} Started: ${data.started_at || ""}`;
  } else if (data.finished_at) {
    message = `${message} Finished: ${data.finished_at}.`;
  }
  if (data.language_label) {
    message = `${message} Language: ${data.language_label}.`;
  }
  codexStatus.textContent = message;
  renderCodexLive(data);

  if (wikiLanguage && data.language_locked) {
    wikiLanguage.value = data.configured_language || wikiLanguage.value;
    wikiLanguage.disabled = true;
  }

  if (compileButton) {
    compileButton.disabled = Boolean(data.running);
  }
  if (compileTogafButton) {
    compileTogafButton.disabled = Boolean(data.running);
  }
  if (lintButton) {
    lintButton.disabled = Boolean(data.running);
  }

  if (data.running) {
    codexWasRunning = true;
    setTimeout(refreshCodexStatus, 1800);
  } else if (codexWasRunning) {
    codexWasRunning = false;
    setTimeout(() => window.location.reload(), 700);
  }
}

async function startCodexJob(kind) {
  if (!codexStatus) {
    return;
  }
  codexStatus.textContent = "Starting Codex...";
  renderCodexLive({
    running: true,
    mode: kind,
    ok: null,
    started_at: new Date().toISOString().slice(0, 19),
    finished_at: null,
    last_output_at: null,
    returncode: null,
    events: [{ time: new Date().toISOString().slice(0, 19), stream: "status", text: "Starting Codex..." }],
  });
  const endpoints = {
    compile: "/api/wiki/compile",
    togaf: "/api/wiki/togaf",
    lint: "/api/wiki/lint",
  };
  const endpoint = endpoints[kind] || endpoints.compile;
  const language = wikiLanguage?.value || "it";
  if (wikiLanguage && !wikiLanguage.disabled) {
    window.localStorage.setItem("wiki-language", language);
  }

  try {
    const resp = await fetch(endpoint, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ language }),
    });
    const data = await resp.json();
    if (!resp.ok) {
      codexStatus.textContent = `Error: ${data.detail || "operation not started"}`;
      return;
    }
    refreshCodexStatus();
  } catch (err) {
    codexStatus.textContent = `Network error: ${err}`;
  }
}

if (compileButton) {
  compileButton.addEventListener("click", () => startCodexJob("compile"));
}

if (compileTogafButton) {
  compileTogafButton.addEventListener("click", () => startCodexJob("togaf"));
}

if (lintButton) {
  lintButton.addEventListener("click", () => startCodexJob("lint"));
}

if (form && output) {
  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    const formData = new FormData(form);

    output.textContent = "Uploading...";

    try {
      const resp = await fetch("/api/upload", {
        method: "POST",
        body: formData,
      });

      const data = await resp.json();
      if (!resp.ok) {
        output.textContent = `Error: ${data.detail || "upload failed"}`;
        return;
      }

      output.textContent = `File uploaded: ${data.file}`;
      setTimeout(() => window.location.reload(), 500);
    } catch (err) {
      output.textContent = `Network error: ${err}`;
    }
  });
}

if (textForm && textOutput) {
  textForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    const formData = new FormData(textForm);

    textOutput.textContent = "Uploading text...";

    try {
      const resp = await fetch("/api/upload-text", {
        method: "POST",
        body: formData,
      });

      const data = await resp.json();
      if (!resp.ok) {
        textOutput.textContent = `Error: ${data.detail || "upload failed"}`;
        return;
      }

      textOutput.textContent = `Text uploaded: ${data.file}`;
      setTimeout(() => window.location.reload(), 500);
    } catch (err) {
      textOutput.textContent = `Network error: ${err}`;
    }
  });
}

if (sourceList && output) {
  sourceList.addEventListener("click", async (event) => {
    const target = event.target;
    if (!(target instanceof HTMLButtonElement) || !target.classList.contains("js-delete-source")) {
      return;
    }

    const row = target.closest("li");
    if (!row) {
      return;
    }
    const relPath = row.getAttribute("data-rel-path") || "";
    if (!relPath) {
      return;
    }

    const confirmed = window.confirm(`Delete ${relPath}?`);
    if (!confirmed) {
      return;
    }

    target.disabled = true;
    output.textContent = `Deleting ${relPath}...`;

    try {
      const resp = await fetch(`/api/sources?path=${encodeURIComponent(relPath)}`, {
        method: "DELETE",
      });
      const data = await resp.json();

      if (!resp.ok) {
        output.textContent = `Error: ${data.detail || "deletion failed"}`;
        target.disabled = false;
        return;
      }

      row.remove();
      updateSourceCount();
      output.textContent = `File deleted: ${data.deleted || relPath}`;
    } catch (err) {
      output.textContent = `Network error: ${err}`;
      target.disabled = false;
    }
  });
}

if (processedList && output) {
  processedList.addEventListener("click", async (event) => {
    const target = event.target;
    if (!(target instanceof HTMLButtonElement) || !target.classList.contains("js-restore-source")) {
      return;
    }

    const row = target.closest("li");
    if (!row) {
      return;
    }
    const relPath = row.getAttribute("data-rel-path") || "";
    if (!relPath) {
      return;
    }

    const confirmed = window.confirm(`Restore ${relPath} to raw/?`);
    if (!confirmed) {
      return;
    }

    target.disabled = true;
    output.textContent = `Restoring ${relPath}...`;

    try {
      const resp = await fetch(`/api/processed/restore?path=${encodeURIComponent(relPath)}`, {
        method: "POST",
      });
      const data = await resp.json();

      if (!resp.ok) {
        output.textContent = `Error: ${data.detail || "restore failed"}`;
        target.disabled = false;
        return;
      }

      row.remove();
      updateProcessedCount();
      output.textContent = `File restored to raw/: ${data.restored || relPath}`;
      setTimeout(() => window.location.reload(), 500);
    } catch (err) {
      output.textContent = `Network error: ${err}`;
      target.disabled = false;
    }
  });
}

updateSourceCount();
updateProcessedCount();
refreshCodexStatus();
