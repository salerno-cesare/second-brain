# LLM Wiki Codex

Web app locale per creare una knowledge base Markdown usando Codex CLI come LLM.

Il flusso e' volutamente semplice:
- `knowledge/raw/`: fonti originali caricate dall'utente.
- `knowledge/.codex_sources/`: estratti testuali temporanei preparati per Codex.
- `knowledge/wiki/`: pagine Markdown generate e mantenute da Codex.

Non ci sono piu' SQLite, FTS5, indicizzazione o retrieval API: l'app serve solo a caricare fonti, avviare Codex CLI dalla shell locale e navigare la wiki generata.

## Funzionalita
- Upload di `.txt`, `.md`, `.rst`, `.log`, `.csv`, `.json`, `.html`, `.pdf`, `.docx`, `.pptx`, `.xlsx`.
- Estrazione testo dalle fonti raw per facilitare il lavoro di Codex.
- Esecuzione locale di `codex exec` tramite PowerShell.
- Compilazione wiki con pagine Markdown, `_index.md`, `_log.md` e link `[[wiki-style]]`.
- Lint/manutenzione della wiki esistente.
- Navigazione web delle pagine in `knowledge/wiki/`.

## Requisiti
- `uv` oppure Python con le dipendenze di `requirements.txt`.
- Codex CLI installato e autenticato sulla macchina locale.
- Su Windows, usa `codex.cmd` (evita i blocchi ExecutionPolicy sul file `codex.ps1`).

Verifica Codex:
```powershell
Get-Command codex.cmd
codex.cmd --version
```

## Avvio Locale
```powershell
uv run --with-requirements requirements.txt uvicorn app.main:app --reload
```

Apri: http://127.0.0.1:8000

In VS Code usa il profilo **LLM Wiki: locale FastAPI** oppure il task **App: run local**.

## Uso
1. Carica un file dalla UI o copialo in `knowledge/raw/`.
2. Premi **Compila**.
3. L'app prepara gli estratti in `knowledge/.codex_sources/`.
4. Codex CLI viene avviato via PowerShell locale e scrive solo in `knowledge/wiki/`.
5. Apri le pagine generate dalla sezione **Pagine Wiki**.

Usa **Lint** per far controllare a Codex link mancanti, duplicati, pagine orfane, contraddizioni e struttura delle pagine.

## Configurazione
Variabili principali in `.env.example`:
- `WIKI_SOURCE_DIR`
- `WIKI_RAW_DIR`
- `WIKI_OUTPUT_DIR`
- `CODEX_COMMAND`
- `CODEX_SHELL`
- `CODEX_MODEL`
- `CODEX_TIMEOUT_SECONDS`
- `CODEX_SOURCE_CHAR_LIMIT`: `0` disabilita il taglio degli estratti in `knowledge/.codex_sources/`; un valore positivo impone un limite massimo di caratteri per fonte.

## Endpoint
- `GET /`
- `GET /wiki/{slug}`
- `GET /api/sources`
- `GET /api/wiki/pages`
- `GET /api/wiki/status`
- `POST /api/wiki/compile`
- `POST /api/wiki/lint`
- `POST /api/upload`
- `POST /api/upload-text`
