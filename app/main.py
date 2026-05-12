from datetime import datetime
from pathlib import Path
import re
import shutil
import threading
import traceback
from urllib.parse import quote

from fastapi import FastAPI, File, Form, HTTPException, Request, UploadFile
from fastapi import Query
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

from .config import get_settings
from .ingest import is_supported_file, list_source_files
from .wiki import (
    CodexRunResult,
    TOGAF_WIKI_DIR_NAME,
    build_wiki_graph,
    ensure_wiki_layout,
    get_togaf_page_payload,
    get_wiki_page_payload,
    list_togaf_artifacts,
    list_wiki_pages,
    read_wiki_page,
    run_codex_wiki_job,
    search_wiki_pages,
    normalize_wiki_language,
    get_configured_wiki_language,
    wiki_language_label,
    WIKI_LANGUAGE_OPTIONS,
)

settings = get_settings()
app = FastAPI(title="LLM Wiki Codex", version="0.2.0")
templates = Jinja2Templates(directory=str(Path(__file__).parent / "templates"))
app.mount("/static", StaticFiles(directory=str(Path(__file__).parent / "static")), name="static")

codex_lock = threading.Lock()
codex_state: dict = {
    "running": False,
    "mode": None,
    "language": "it",
    "language_label": WIKI_LANGUAGE_OPTIONS["it"],
    "message": "Nessuna compilazione avviata.",
    "ok": None,
    "returncode": None,
    "started_at": None,
    "finished_at": None,
    "elapsed_seconds": None,
    "stdout": "",
    "stderr": "",
    "sources": [],
}


class CodexJobRequest(BaseModel):
    language: str = "it"


@app.on_event("startup")
def startup_event() -> None:
    ensure_wiki_layout(settings)


@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    wiki_pages = list_wiki_pages(settings.wiki_dir)
    initial_slug = "_index" if any(page.slug == "_index" for page in wiki_pages) else (wiki_pages[0].slug if wiki_pages else "")
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "wiki_pages": wiki_pages,
            "initial_slug": initial_slug,
        },
    )


@app.get("/sources", response_class=HTMLResponse)
def sources_page(request: Request):
    processed_dir = settings.raw_dir.parent / "processed"
    configured_language = get_configured_wiki_language(settings.wiki_dir)
    return templates.TemplateResponse(
        "sources.html",
        {
            "request": request,
            "raw_dir": str(settings.raw_dir),
            "processed_dir": str(processed_dir),
            "wiki_dir": str(settings.wiki_dir),
            "source_files": list_source_files(settings.raw_dir, settings.source_dir),
            "processed_files": list_source_files(processed_dir, settings.source_dir),
            "codex_state": codex_state,
            "codex_command": settings.codex_command,
            "codex_shell": settings.codex_shell,
            "wiki_languages": WIKI_LANGUAGE_OPTIONS,
            "selected_wiki_language": configured_language or "it",
            "wiki_language_locked": configured_language is not None,
        },
    )


def _togaf_dir() -> Path:
    return settings.wiki_dir / TOGAF_WIKI_DIR_NAME


@app.get("/togaf", response_class=HTMLResponse)
def togaf_home(request: Request):
    togaf_pages = list_wiki_pages(_togaf_dir())
    initial_slug = "_index" if any(page.slug == "_index" for page in togaf_pages) else (togaf_pages[0].slug if togaf_pages else "")
    return templates.TemplateResponse(
        "togaf.html",
        {
            "request": request,
            "togaf_pages": togaf_pages,
            "togaf_artifacts": list_togaf_artifacts(_togaf_dir()),
            "initial_slug": initial_slug,
        },
    )


@app.get("/wiki/{slug}")
def wiki_detail(slug: str):
    if not read_wiki_page(settings.wiki_dir, slug):
        raise HTTPException(status_code=404, detail="Wiki page not found")
    return RedirectResponse(url=f"/#{quote(slug)}")


@app.get("/togaf/{slug}")
def togaf_detail(slug: str):
    if not read_wiki_page(_togaf_dir(), slug):
        raise HTTPException(status_code=404, detail="TOGAF artifact not found")
    return RedirectResponse(url=f"/togaf#{quote(slug)}")


@app.get("/api/sources")
def api_sources():
    return JSONResponse(
        content={"sources": [source.__dict__ for source in list_source_files(settings.raw_dir, settings.source_dir)]}
    )


@app.get("/api/processed")
def api_processed_sources():
    processed_dir = settings.raw_dir.parent / "processed"
    return JSONResponse(
        content={"sources": [source.__dict__ for source in list_source_files(processed_dir, settings.source_dir)]}
    )


@app.delete("/api/sources")
def api_delete_source(path: str = Query(..., min_length=1, max_length=260)):
    requested = Path(path)
    if requested.is_absolute():
        raise HTTPException(status_code=400, detail="Percorso non valido")

    target = (settings.source_dir / requested).resolve()
    try:
        raw_root = settings.raw_dir.resolve()
    except OSError:
        raise HTTPException(status_code=500, detail="Directory raw non disponibile")

    if raw_root not in target.parents:
        raise HTTPException(status_code=400, detail="Percorso fuori da raw/")
    if not target.exists() or not target.is_file():
        raise HTTPException(status_code=404, detail="File non trovato")

    target.unlink()
    return JSONResponse(content={"status": "ok", "deleted": str(target.relative_to(raw_root)).replace("\\", "/")})


def _unique_destination(target: Path) -> Path:
    if not target.exists():
        return target

    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    candidate = target.with_name(f"{target.stem}-{stamp}{target.suffix}")
    counter = 1
    while candidate.exists():
        candidate = target.with_name(f"{target.stem}-{stamp}-{counter}{target.suffix}")
        counter += 1
    return candidate


@app.post("/api/processed/restore")
def api_restore_processed_source(path: str = Query(..., min_length=1, max_length=260)):
    requested = Path(path)
    if requested.is_absolute():
        raise HTTPException(status_code=400, detail="Percorso non valido")

    source_path = (settings.source_dir / requested).resolve()
    processed_root = (settings.raw_dir.parent / "processed").resolve()
    raw_root = settings.raw_dir.resolve()

    if processed_root not in source_path.parents:
        raise HTTPException(status_code=400, detail="Percorso fuori da processed/")
    if not source_path.exists() or not source_path.is_file():
        raise HTTPException(status_code=404, detail="File non trovato")

    rel_in_processed = source_path.relative_to(processed_root)
    destination = _unique_destination(raw_root / rel_in_processed)
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.move(str(source_path), str(destination))

    restored_rel = str(destination.relative_to(raw_root)).replace("\\", "/")
    return JSONResponse(content={"status": "ok", "restored": restored_rel})


@app.get("/api/wiki/pages")
def api_wiki_pages():
    return JSONResponse(content={"pages": [page.__dict__ for page in list_wiki_pages(settings.wiki_dir)]})


@app.get("/api/wiki/page/{slug}")
def api_wiki_page(slug: str):
    payload = get_wiki_page_payload(settings.wiki_dir, slug)
    if not payload:
        raise HTTPException(status_code=404, detail="Wiki page not found")
    return JSONResponse(content=payload)


@app.get("/api/wiki/search")
def api_wiki_search(q: str = Query(default="", max_length=120)):
    return JSONResponse(content={"query": q, "results": search_wiki_pages(settings.wiki_dir, q)})


@app.get("/api/wiki/graph")
def api_wiki_graph():
    return JSONResponse(content=build_wiki_graph(settings.wiki_dir))


@app.get("/api/togaf/pages")
def api_togaf_pages():
    return JSONResponse(content={"pages": [page.__dict__ for page in list_wiki_pages(_togaf_dir())]})


@app.get("/api/togaf/page/{slug}")
def api_togaf_page(slug: str):
    payload = get_togaf_page_payload(_togaf_dir(), slug)
    if not payload:
        raise HTTPException(status_code=404, detail="TOGAF artifact not found")
    return JSONResponse(content=payload)


@app.get("/api/togaf/search")
def api_togaf_search(q: str = Query(default="", max_length=120)):
    return JSONResponse(content={"query": q, "results": search_wiki_pages(_togaf_dir(), q)})


@app.get("/api/togaf/graph")
def api_togaf_graph():
    return JSONResponse(content=build_wiki_graph(_togaf_dir()))


@app.get("/api/togaf/artifacts")
def api_togaf_artifacts():
    return JSONResponse(content=list_togaf_artifacts(_togaf_dir()))


@app.get("/api/wiki/status")
def api_wiki_status():
    configured_language = get_configured_wiki_language(settings.wiki_dir)
    state = dict(codex_state)
    state["configured_language"] = configured_language
    state["configured_language_label"] = wiki_language_label(configured_language) if configured_language else None
    state["language_locked"] = configured_language is not None
    return JSONResponse(content=state)


def _set_codex_state(**values) -> None:
    with codex_lock:
        codex_state.update(values)


def _run_codex_background(mode: str, language: str) -> None:
    configured_language = get_configured_wiki_language(settings.wiki_dir)
    if configured_language:
        language = configured_language
    language = normalize_wiki_language(language)
    _set_codex_state(
        running=True,
        mode=mode,
        language=language,
        language_label=WIKI_LANGUAGE_OPTIONS[language],
        message="Codex sta compilando la wiki dalla shell locale...",
        ok=None,
        returncode=None,
        started_at=datetime.now().isoformat(timespec="seconds"),
        finished_at=None,
        elapsed_seconds=None,
        stdout="",
        stderr="",
        sources=[],
    )
    try:
        result: CodexRunResult = run_codex_wiki_job(settings, mode=mode, language=language)
        _set_codex_state(
            running=False,
            message=result.message,
            ok=result.ok,
            returncode=result.returncode,
            finished_at=datetime.now().isoformat(timespec="seconds"),
            elapsed_seconds=round(result.elapsed_seconds, 2),
            stdout=result.stdout[-6000:],
            stderr=result.stderr[-6000:],
            sources=[source.__dict__ for source in result.sources],
        )
    except Exception as exc:
        _set_codex_state(
            running=False,
            message=f"Errore durante la compilazione Codex: {exc}",
            ok=False,
            returncode=1,
            finished_at=datetime.now().isoformat(timespec="seconds"),
            elapsed_seconds=None,
            stdout="",
            stderr=traceback.format_exc(),
            sources=[],
        )


def _start_codex_job(mode: str, language: str = "it") -> JSONResponse:
    configured_language = get_configured_wiki_language(settings.wiki_dir)
    if configured_language:
        language = configured_language
    language = normalize_wiki_language(language)
    with codex_lock:
        if codex_state["running"]:
            raise HTTPException(status_code=409, detail="Una compilazione Codex e' gia' in corso.")
        codex_state.update(
            {
                "running": True,
                "mode": mode,
                "language": language,
                "language_label": WIKI_LANGUAGE_OPTIONS[language],
                "message": "Codex sta compilando la wiki dalla shell locale...",
                "ok": None,
                "returncode": None,
                "started_at": datetime.now().isoformat(timespec="seconds"),
                "finished_at": None,
                "elapsed_seconds": None,
                "stdout": "",
                "stderr": "",
                "sources": [],
            }
        )

    thread = threading.Thread(target=_run_codex_background, args=(mode, language), daemon=True)
    thread.start()
    return JSONResponse(content={"status": "accepted", "mode": mode, "language": language}, status_code=202)


def _source_text_path(title: str) -> Path:
    clean_title = Path(title.strip()).name if title.strip() else ""
    if not clean_title:
        clean_title = f"testo-libero-{datetime.now().strftime('%Y%m%d-%H%M%S')}.txt"

    clean_title = re.sub(r"[^\w.-]+", "-", clean_title, flags=re.ASCII).strip(".-")
    if not clean_title:
        clean_title = f"testo-libero-{datetime.now().strftime('%Y%m%d-%H%M%S')}.txt"

    target_path = settings.raw_dir / clean_title
    if not target_path.suffix:
        target_path = target_path.with_suffix(".txt")

    if target_path.suffix.lower() not in {".txt", ".md", ".rst", ".log"}:
        raise HTTPException(status_code=400, detail="Estensione testo non supportata")

    return target_path


@app.post("/api/wiki/compile")
def api_wiki_compile(payload: CodexJobRequest | None = None):
    return _start_codex_job("compile", payload.language if payload else "it")


@app.post("/api/wiki/lint")
def api_wiki_lint(payload: CodexJobRequest | None = None):
    return _start_codex_job("lint", payload.language if payload else "it")


@app.post("/api/upload")
async def api_upload(file: UploadFile = File(...)):
    if not file.filename:
        raise HTTPException(status_code=400, detail="Missing filename")

    target_path = settings.raw_dir / Path(file.filename).name
    target_path.parent.mkdir(parents=True, exist_ok=True)

    if not is_supported_file(target_path):
        raise HTTPException(status_code=400, detail="Unsupported file type")

    content = await file.read()
    target_path.write_bytes(content)

    return JSONResponse(content={"status": "ok", "file": target_path.name})


@app.post("/api/upload-text")
async def api_upload_text(title: str = Form(default="", max_length=120), text: str = Form(..., max_length=500000)):
    content = text.strip()
    if not content:
        raise HTTPException(status_code=400, detail="Testo mancante")

    target_path = _source_text_path(title)
    target_path.parent.mkdir(parents=True, exist_ok=True)
    target_path.write_text(content + "\n", encoding="utf-8")

    return JSONResponse(content={"status": "ok", "file": target_path.name})
