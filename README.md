# Graphify Second Brain

Web app locale per caricare fonti in `knowledge/raw/`, costruire un knowledge graph con Graphify e navigare la wiki Markdown generata.

Il flusso e' volutamente semplice:
- `knowledge/raw/`: fonti originali caricate dall'utente.
- `knowledge/graphify-out/`: output Graphify (`graph.json`, `GRAPH_REPORT.md`, `graph.html`, `wiki/`).
- `knowledge/wiki/`: copia navigabile della wiki Markdown generata da Graphify.
- `knowledge/processed/`: fonti raw archiviate dopo una compilazione riuscita.

Non ci sono piu' prompt custom applicativi o template di generazione locali. Di default l'app invoca la skill Graphify dentro Codex CLI (`GRAPHIFY_RUNNER=cli`), cosi' non serve una API key Graphify separata. La modalita' headless (`GRAPHIFY_RUNNER=headless`) resta disponibile per chi vuole usare direttamente `python -m graphify extract` con una chiave API supportata.

## Funzionalita
- Upload di testo/Markdown, codice, YAML/JSON/CSV/HTML, PDF, immagini e file Office supportati dal runtime locale.
- Esecuzione Graphify via CLI agent: `/graphify "<raw>" --wiki`.
- Navigazione web delle pagine in `knowledge/wiki/`.
- Stato live della build Graphify dalla pagina Sources.
- Archiviazione automatica delle fonti da `raw/` a `processed/` dopo una build riuscita.

## Requisiti
- `uv` oppure Python con le dipendenze di `requirements.txt`.
- Codex CLI installato e autenticato se usi `GRAPHIFY_RUNNER=cli`.
- Solo per `GRAPHIFY_RUNNER=headless`: una chiave API supportata da Graphify, per esempio `GEMINI_API_KEY`, `ANTHROPIC_API_KEY`, `OPENAI_API_KEY`, `DEEPSEEK_API_KEY` o `MOONSHOT_API_KEY`.

Verifica Graphify e Codex CLI:
```powershell
uv run --with-requirements requirements.txt python -m graphify --version
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
2. Scegli la lingua della wiki se non e' gia' configurata. La lingua resta un metadato locale dell'app; Graphify genera i contenuti secondo le proprie regole.
3. Premi **Build Graphify Wiki**.
4. L'app installa/aggiorna la skill Graphify per Codex e avvia Codex CLI con `/graphify "<raw>" --wiki`.
5. L'output Markdown di `knowledge/graphify-out/wiki/` viene sincronizzato in `knowledge/wiki/`, usando `_index.md` come entry point locale.

## Configurazione
Variabili principali in `.env.example`:
- `WIKI_SOURCE_DIR`
- `WIKI_RAW_DIR`
- `WIKI_OUTPUT_DIR`
- `GRAPHIFY_OUTPUT_DIR`: cartella dentro cui Graphify crea `graphify-out/`.
- `GRAPHIFY_RUNNER`: `cli` usa Codex CLI senza API key Graphify; `headless` usa direttamente la CLI Python di Graphify.
- `GRAPHIFY_CLI_COMMAND`: comando CLI agent, default `codex.cmd` su Windows.
- `GRAPHIFY_TIMEOUT_SECONDS`
- `GRAPHIFY_BACKEND`
- `GRAPHIFY_MODEL`
- `GRAPHIFY_MAX_WORKERS`
- `GRAPHIFY_TOKEN_BUDGET`
- `GRAPHIFY_MAX_CONCURRENCY`

## Endpoint
- `GET /`
- `GET /wiki/{slug}`
- `GET /api/sources`
- `GET /api/wiki/pages`
- `GET /api/wiki/status`
- `GET /api/wiki/graph`
- `POST /api/wiki/compile`
- `POST /api/upload`
- `POST /api/upload-text`
