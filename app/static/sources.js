const form = document.getElementById("upload-form");
const output = document.getElementById("upload-result");
const textForm = document.getElementById("text-upload-form");
const textOutput = document.getElementById("text-upload-result");
const compileButton = document.getElementById("compile-wiki");
const lintButton = document.getElementById("lint-wiki");
const codexStatus = document.getElementById("codex-status");
const sourceList = document.getElementById("source-list");
const sourceCount = document.getElementById("source-count");
const processedList = document.getElementById("processed-list");
const processedCount = document.getElementById("processed-count");

let codexWasRunning = false;

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

async function refreshCodexStatus() {
  if (!codexStatus) {
    return;
  }

  const resp = await fetch("/api/wiki/status");
  const data = await resp.json();
  let message = data.message || "Stato non disponibile.";
  if (data.running) {
    message = `${message} Avviata: ${data.started_at || ""}`;
  } else if (data.finished_at) {
    message = `${message} Fine: ${data.finished_at}.`;
  }
  codexStatus.textContent = message;

  if (compileButton) {
    compileButton.disabled = Boolean(data.running);
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
  codexStatus.textContent = "Avvio Codex...";
  const endpoint = kind === "lint" ? "/api/wiki/lint" : "/api/wiki/compile";

  try {
    const resp = await fetch(endpoint, { method: "POST" });
    const data = await resp.json();
    if (!resp.ok) {
      codexStatus.textContent = `Errore: ${data.detail || "operazione non avviata"}`;
      return;
    }
    refreshCodexStatus();
  } catch (err) {
    codexStatus.textContent = `Errore rete: ${err}`;
  }
}

if (compileButton) {
  compileButton.addEventListener("click", () => startCodexJob("compile"));
}

if (lintButton) {
  lintButton.addEventListener("click", () => startCodexJob("lint"));
}

if (form && output) {
  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    const formData = new FormData(form);

    output.textContent = "Upload in corso...";

    try {
      const resp = await fetch("/api/upload", {
        method: "POST",
        body: formData,
      });

      const data = await resp.json();
      if (!resp.ok) {
        output.textContent = `Errore: ${data.detail || "upload fallito"}`;
        return;
      }

      output.textContent = `File caricato: ${data.file}`;
      setTimeout(() => window.location.reload(), 500);
    } catch (err) {
      output.textContent = `Errore rete: ${err}`;
    }
  });
}

if (textForm && textOutput) {
  textForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    const formData = new FormData(textForm);

    textOutput.textContent = "Caricamento testo...";

    try {
      const resp = await fetch("/api/upload-text", {
        method: "POST",
        body: formData,
      });

      const data = await resp.json();
      if (!resp.ok) {
        textOutput.textContent = `Errore: ${data.detail || "caricamento fallito"}`;
        return;
      }

      textOutput.textContent = `Testo caricato: ${data.file}`;
      setTimeout(() => window.location.reload(), 500);
    } catch (err) {
      textOutput.textContent = `Errore rete: ${err}`;
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

    const confirmed = window.confirm(`Vuoi cancellare ${relPath}?`);
    if (!confirmed) {
      return;
    }

    target.disabled = true;
    output.textContent = `Cancellazione ${relPath}...`;

    try {
      const resp = await fetch(`/api/sources?path=${encodeURIComponent(relPath)}`, {
        method: "DELETE",
      });
      const data = await resp.json();

      if (!resp.ok) {
        output.textContent = `Errore: ${data.detail || "cancellazione non riuscita"}`;
        target.disabled = false;
        return;
      }

      row.remove();
      updateSourceCount();
      output.textContent = `File cancellato: ${data.deleted || relPath}`;
    } catch (err) {
      output.textContent = `Errore rete: ${err}`;
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

    const confirmed = window.confirm(`Vuoi riportare ${relPath} in raw/?`);
    if (!confirmed) {
      return;
    }

    target.disabled = true;
    output.textContent = `Ripristino ${relPath}...`;

    try {
      const resp = await fetch(`/api/processed/restore?path=${encodeURIComponent(relPath)}`, {
        method: "POST",
      });
      const data = await resp.json();

      if (!resp.ok) {
        output.textContent = `Errore: ${data.detail || "ripristino non riuscito"}`;
        target.disabled = false;
        return;
      }

      row.remove();
      updateProcessedCount();
      output.textContent = `File ripristinato in raw/: ${data.restored || relPath}`;
      setTimeout(() => window.location.reload(), 500);
    } catch (err) {
      output.textContent = `Errore rete: ${err}`;
      target.disabled = false;
    }
  });
}

updateSourceCount();
updateProcessedCount();
refreshCodexStatus();
