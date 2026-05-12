# LLM Wiki Codex

Web app locale per creare una knowledge base Markdown usando Codex CLI come LLM.

Il flusso e' volutamente semplice:
- `knowledge/raw/`: fonti originali caricate dall'utente.
- `knowledge/.codex_sources/`: estratti testuali temporanei preparati per Codex.
- `knowledge/wiki/`: pagine Markdown generate e mantenute da Codex.
- `knowledge/wiki/togaf/`: wiki alternativa con indice e artefatti TOGAF derivati dalla wiki principale.

Non ci sono piu' SQLite, FTS5, indicizzazione o retrieval API: l'app serve solo a caricare fonti, avviare Codex CLI dalla shell locale e navigare la wiki generata.

## Funzionalita
- Upload di `.txt`, `.md`, `.rst`, `.log`, `.csv`, `.json`, `.html`, `.pdf`, `.docx`, `.pptx`, `.xlsx`.
- Estrazione testo dalle fonti raw per facilitare il lavoro di Codex.
- Esecuzione locale di `codex exec` tramite PowerShell.
- Compilazione wiki con pagine Markdown, `_index.md`, `_log.md` e link `[[wiki-style]]`.
- Compilazione di una vista TOGAF alternativa con artefatti navigabili per fase ADM, dominio e tipo.
- Lint/manutenzione della wiki esistente.
- Navigazione web delle pagine in `knowledge/wiki/`.
- Navigazione web degli artefatti TOGAF da `/togaf`.

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
2. Scegli la lingua della wiki, se non e' gia' configurata. Il default e' **Italiano**.
3. Premi **Compila**.
4. L'app prepara gli estratti in `knowledge/.codex_sources/`.
5. Codex CLI viene avviato via PowerShell locale e scrive solo in `knowledge/wiki/`.
6. Apri le pagine generate dalla sezione **Pagine Wiki** oppure gli artefatti dalla sezione **TOGAF**.

La prima compilazione salva la lingua in `knowledge/wiki/_config.md`; dopo il salvataggio non e' piu' modificabile dalla UI per evitare wiki multilingua accidentali.

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
- `CODEX_PROMPT_TEMPLATE`: percorso del prompt principale usato da Codex, con placeholder `{mode}`, `{task}` e `{source_list}`.
- `CODEX_TASK_PROMPTS`: obiettivi per le modalita' `compile` e `lint`.
- `CODEX_SOURCE_EXTRACT_TEMPLATE`: template dei file estratti in `knowledge/.codex_sources/`.
- `CODEX_SOURCE_LIST_ITEM_TEMPLATE`: template di ogni voce fonte nel prompt principale.
- `CODEX_SOURCE_LIST_EMPTY_TEMPLATE`: testo usato quando non ci sono fonti raw.

## Endpoint
- `GET /`
- `GET /wiki/{slug}`
- `GET /togaf`
- `GET /togaf/{slug}`
- `GET /api/sources`
- `GET /api/wiki/pages`
- `GET /api/wiki/status`
- `GET /api/togaf/pages`
- `GET /api/togaf/page/{slug}`
- `GET /api/togaf/search`
- `GET /api/togaf/graph`
- `GET /api/togaf/artifacts`
- `POST /api/wiki/compile`
- `POST /api/wiki/lint`
- `POST /api/upload`
- `POST /api/upload-text`
