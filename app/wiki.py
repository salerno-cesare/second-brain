from __future__ import annotations

import html
import json
import re
import shutil
import subprocess
import time
import unicodedata
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from .config import Settings
from .ingest import is_supported_file, normalize_text, read_text_from_file

WIKI_LINK_RE = re.compile(r"\[\[([^\]\|]+)(?:\|([^\]]+))?\]\]")


@dataclass(frozen=True)
class WikiPage:
    slug: str
    title: str
    rel_path: str
    updated_at: str
    size: int
    links: int


@dataclass(frozen=True)
class PreparedSource:
    rel_path: str
    extracted_path: str
    chars: int
    truncated: bool


@dataclass(frozen=True)
class CodexRunResult:
    ok: bool
    mode: str
    returncode: int
    elapsed_seconds: float
    message: str
    stdout: str
    stderr: str
    sources: list[PreparedSource]


def ensure_wiki_layout(settings: Settings) -> None:
    settings.source_dir.mkdir(parents=True, exist_ok=True)
    settings.raw_dir.mkdir(parents=True, exist_ok=True)
    settings.wiki_dir.mkdir(parents=True, exist_ok=True)

    index_path = settings.wiki_dir / "_index.md"
    if not index_path.exists():
        index_path.write_text(
            "# Indice Wiki\n\n"
            "Questa pagina viene aggiornata da Codex durante la compilazione della knowledge base.\n",
            encoding="utf-8",
        )


def slugify_wiki_title(title: str) -> str:
    normalized = unicodedata.normalize("NFKD", title)
    ascii_text = normalized.encode("ascii", "ignore").decode("ascii")
    slug = re.sub(r"[^a-z0-9]+", "-", ascii_text.lower()).strip("-")
    return slug or "pagina"


def title_from_markdown(path: Path) -> str:
    try:
        for line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
            stripped = line.strip()
            if stripped.startswith("# "):
                return stripped[2:].strip()
    except OSError:
        pass

    return path.stem.replace("-", " ").replace("_", " ").title()


def list_wiki_pages(wiki_dir: Path) -> list[WikiPage]:
    if not wiki_dir.exists():
        return []

    pages: list[WikiPage] = []
    for path in sorted(wiki_dir.glob("*.md"), key=lambda item: item.name.lower()):
        content = path.read_text(encoding="utf-8", errors="ignore")
        stat = path.stat()
        pages.append(
            WikiPage(
                slug=path.stem,
                title=title_from_markdown(path),
                rel_path=path.name,
                updated_at=datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M"),
                size=stat.st_size,
                links=len(WIKI_LINK_RE.findall(content)),
            )
        )

    return pages


def _wiki_title_map(wiki_dir: Path) -> dict[str, str]:
    mapping: dict[str, str] = {}
    for page in list_wiki_pages(wiki_dir):
        mapping[slugify_wiki_title(page.title)] = page.slug
        mapping[slugify_wiki_title(page.slug)] = page.slug
    return mapping


def read_wiki_page(wiki_dir: Path, slug: str) -> tuple[WikiPage, str] | None:
    safe_slug = Path(slug).name
    target = (wiki_dir / f"{safe_slug}.md").resolve()
    try:
        if target.parent != wiki_dir.resolve():
            return None
    except OSError:
        return None

    if not target.exists() or not target.is_file():
        return None

    content = target.read_text(encoding="utf-8", errors="ignore")
    stat = target.stat()
    page = WikiPage(
        slug=target.stem,
        title=title_from_markdown(target),
        rel_path=target.name,
        updated_at=datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M"),
        size=stat.st_size,
        links=len(WIKI_LINK_RE.findall(content)),
    )
    return page, content


def extract_wiki_links(markdown: str, wiki_dir: Path) -> list[dict]:
    title_map = _wiki_title_map(wiki_dir)
    links: list[dict] = []
    seen: set[tuple[str, str]] = set()

    for match in WIKI_LINK_RE.finditer(markdown):
        target_title = match.group(1).strip()
        label = (match.group(2) or target_title).strip()
        slug = title_map.get(slugify_wiki_title(target_title), slugify_wiki_title(target_title))
        target = read_wiki_page(wiki_dir, slug)
        exists = target is not None
        title = target[0].title if target else target_title
        key = (slug, label)
        if key in seen:
            continue
        seen.add(key)
        links.append(
            {
                "slug": slug,
                "title": title,
                "label": label,
                "exists": exists,
            }
        )

    return links


def get_wiki_backlinks(wiki_dir: Path, target_slug: str) -> list[dict]:
    backlinks: list[dict] = []
    safe_target_slug = Path(target_slug).name

    for page in list_wiki_pages(wiki_dir):
        if page.slug == safe_target_slug:
            continue

        page_data = read_wiki_page(wiki_dir, page.slug)
        if not page_data:
            continue

        _, markdown = page_data
        matching_links = [
            link for link in extract_wiki_links(markdown, wiki_dir) if link["slug"] == safe_target_slug
        ]
        if matching_links:
            backlinks.append(
                {
                    "slug": page.slug,
                    "title": page.title,
                    "rel_path": page.rel_path,
                    "count": len(matching_links),
                }
            )

    return backlinks


def get_wiki_page_payload(wiki_dir: Path, slug: str) -> dict | None:
    page_data = read_wiki_page(wiki_dir, slug)
    if not page_data:
        return None

    page, markdown = page_data
    return {
        "page": page.__dict__,
        "markdown": markdown,
        "html": render_wiki_markdown(markdown, wiki_dir),
        "outgoing": extract_wiki_links(markdown, wiki_dir),
        "backlinks": get_wiki_backlinks(wiki_dir, page.slug),
    }


def search_wiki_pages(wiki_dir: Path, query: str, limit: int = 30) -> list[dict]:
    normalized_query = query.strip().lower()
    if not normalized_query:
        return []

    matches: list[dict] = []
    for page in list_wiki_pages(wiki_dir):
        page_data = read_wiki_page(wiki_dir, page.slug)
        if not page_data:
            continue

        _, markdown = page_data
        haystack = f"{page.title}\n{markdown}".lower()
        index = haystack.find(normalized_query)
        if index < 0:
            continue

        snippet_start = max(index - 80, 0)
        snippet_end = min(index + len(normalized_query) + 160, len(markdown))
        snippet = re.sub(r"\s+", " ", markdown[snippet_start:snippet_end]).strip()
        matches.append(
            {
                "slug": page.slug,
                "title": page.title,
                "rel_path": page.rel_path,
                "snippet": snippet,
            }
        )

        if len(matches) >= limit:
            break

    return matches


def build_wiki_graph(wiki_dir: Path) -> dict:
    pages = list_wiki_pages(wiki_dir)
    known_slugs = {page.slug for page in pages}
    nodes = [
        {
            "slug": page.slug,
            "title": page.title,
            "links": page.links,
            "missing": False,
        }
        for page in pages
    ]
    missing_nodes: dict[str, dict] = {}
    edges: list[dict] = []
    seen_edges: set[tuple[str, str]] = set()

    for page in pages:
        page_data = read_wiki_page(wiki_dir, page.slug)
        if not page_data:
            continue

        _, markdown = page_data
        for link in extract_wiki_links(markdown, wiki_dir):
            target_slug = link["slug"]
            key = (page.slug, target_slug)
            if key in seen_edges:
                continue
            seen_edges.add(key)

            if target_slug not in known_slugs and target_slug not in missing_nodes:
                missing_nodes[target_slug] = {
                    "slug": target_slug,
                    "title": link["title"],
                    "links": 0,
                    "missing": True,
                }

            edges.append(
                {
                    "source": page.slug,
                    "target": target_slug,
                    "label": link["label"],
                    "missing": target_slug not in known_slugs,
                }
            )

    return {"nodes": nodes + list(missing_nodes.values()), "edges": edges}


def render_wiki_markdown(markdown: str, wiki_dir: Path) -> str:
    title_map = _wiki_title_map(wiki_dir)

    def replace_wiki_link(match: re.Match[str]) -> str:
        target_title = match.group(1).strip()
        label = (match.group(2) or target_title).strip()
        slug = title_map.get(slugify_wiki_title(target_title), slugify_wiki_title(target_title))
        exists = (wiki_dir / f"{slug}.md").exists()
        css_class = "wiki-link" if exists else "wiki-link missing"
        return f'<a class="{css_class}" href="/wiki/{html.escape(slug)}">{html.escape(label)}</a>'

    rendered_lines: list[str] = []
    in_list = False
    in_code = False
    code_lines: list[str] = []

    for raw_line in markdown.splitlines():
        line = raw_line.rstrip()
        stripped = line.strip()

        if stripped.startswith("```"):
            if in_code:
                rendered_lines.append("<pre><code>" + html.escape("\n".join(code_lines)) + "</code></pre>")
                code_lines = []
                in_code = False
            else:
                if in_list:
                    rendered_lines.append("</ul>")
                    in_list = False
                in_code = True
            continue

        if in_code:
            code_lines.append(line)
            continue

        if not stripped:
            if in_list:
                rendered_lines.append("</ul>")
                in_list = False
            continue

        heading = re.match(r"^(#{1,4})\s+(.+)$", stripped)
        if heading:
            if in_list:
                rendered_lines.append("</ul>")
                in_list = False
            level = len(heading.group(1))
            text = WIKI_LINK_RE.sub(replace_wiki_link, html.escape(heading.group(2), quote=False))
            rendered_lines.append(f"<h{level}>{text}</h{level}>")
            continue

        bullet = re.match(r"^[-*]\s+(.+)$", stripped)
        if bullet:
            if not in_list:
                rendered_lines.append("<ul>")
                in_list = True
            text = WIKI_LINK_RE.sub(replace_wiki_link, html.escape(bullet.group(1), quote=False))
            rendered_lines.append(f"<li>{text}</li>")
            continue

        if in_list:
            rendered_lines.append("</ul>")
            in_list = False

        text = WIKI_LINK_RE.sub(replace_wiki_link, html.escape(stripped, quote=False))
        rendered_lines.append(f"<p>{text}</p>")

    if in_code:
        rendered_lines.append("<pre><code>" + html.escape("\n".join(code_lines)) + "</code></pre>")
    if in_list:
        rendered_lines.append("</ul>")

    return "\n".join(rendered_lines)


def _source_text_dir(settings: Settings) -> Path:
    return settings.source_dir / ".codex_sources"


def _clear_prepared_source_files(source_text_dir: Path) -> None:
    if not source_text_dir.exists():
        return

    for child in source_text_dir.iterdir():
        for attempt in range(3):
            try:
                if child.is_dir():
                    shutil.rmtree(child)
                else:
                    child.unlink()
                break
            except FileNotFoundError:
                break
            except PermissionError:
                if attempt == 2:
                    break
                time.sleep(0.15)
            except OSError:
                break


def prepare_sources_for_codex(settings: Settings) -> list[PreparedSource]:
    ensure_wiki_layout(settings)
    source_text_dir = _source_text_dir(settings).resolve()
    source_root = settings.source_dir.resolve()
    if source_root not in source_text_dir.parents:
        raise ValueError("Prepared source directory must stay inside the wiki source directory")

    source_text_dir.mkdir(parents=True, exist_ok=True)
    _clear_prepared_source_files(source_text_dir)

    prepared: list[PreparedSource] = []
    for idx, path in enumerate(sorted(settings.raw_dir.rglob("*")), start=1):
        if not path.is_file() or not is_supported_file(path):
            continue

        rel_path = str(path.resolve().relative_to(source_root)).replace("\\", "/")
        try:
            text = normalize_text(read_text_from_file(path))
        except Exception as exc:
            text = f"Extraction failed for {rel_path}: {exc}"

        truncated = settings.codex_source_char_limit > 0 and len(text) > settings.codex_source_char_limit
        if truncated:
            text = text[: settings.codex_source_char_limit] + "\n\n[TRUNCATED]"

        safe_name = f"{idx:03d}-{slugify_wiki_title(path.stem)}.txt"
        extracted_path = source_text_dir / safe_name
        extracted_path.write_text(
            f"Source: {rel_path}\n"
            f"Extracted at: {datetime.now(timezone.utc).isoformat()}\n"
            f"Truncated: {str(truncated).lower()}\n\n"
            f"{text}\n",
            encoding="utf-8",
        )
        prepared.append(
            PreparedSource(
                rel_path=rel_path,
                extracted_path=str(extracted_path.resolve().relative_to(source_root)).replace("\\", "/"),
                chars=len(text),
                truncated=truncated,
            )
        )

    manifest = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source_count": len(prepared),
        "sources": [source.__dict__ for source in prepared],
    }
    (source_text_dir / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return prepared


def _processed_target_path(source_path: Path, raw_root: Path, processed_root: Path) -> Path:
    rel_path = source_path.resolve().relative_to(raw_root.resolve())
    target = processed_root / rel_path
    if not target.exists():
        return target

    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    candidate = target.with_name(f"{target.stem}-{stamp}{target.suffix}")
    counter = 1
    while candidate.exists():
        candidate = target.with_name(f"{target.stem}-{stamp}-{counter}{target.suffix}")
        counter += 1
    return candidate


def move_raw_sources_to_processed(raw_dir: Path) -> tuple[int, list[str]]:
    if not raw_dir.exists():
        return 0, []

    processed_dir = raw_dir.parent / "processed"
    processed_dir.mkdir(parents=True, exist_ok=True)

    moved_count = 0
    errors: list[str] = []
    for path in sorted(raw_dir.rglob("*"), key=lambda item: str(item).lower()):
        if not path.is_file() or not is_supported_file(path):
            continue

        rel = str(path.resolve().relative_to(raw_dir.resolve())).replace("\\", "/")
        target = _processed_target_path(path, raw_dir, processed_dir)
        target.parent.mkdir(parents=True, exist_ok=True)
        try:
            shutil.move(str(path), str(target))
            moved_count += 1
        except Exception as exc:
            errors.append(f"{rel}: {exc}")

    for folder in sorted((item for item in raw_dir.rglob("*") if item.is_dir()), reverse=True):
        try:
            folder.rmdir()
        except OSError:
            continue

    return moved_count, errors


def build_codex_prompt(settings: Settings, mode: str, sources: list[PreparedSource]) -> str:
    source_list = "\n".join(
        f"- {source.extracted_path} (origine: {source.rel_path}, chars: {source.chars}, truncated: {source.truncated})"
        for source in sources
    )
    if not source_list:
        source_list = "- Nessuna fonte disponibile in raw/."

    if mode == "lint":
        task = (
            "Esegui una manutenzione della wiki esistente: controlla pagine orfane, link mancanti, "
            "concetti troppo larghi da dividere, duplicati, contraddizioni non annotate e aggiorna "
            "solo i file Markdown necessari in wiki/."
        )
    else:
        task = (
            "Compila o aggiorna la wiki persistente partendo dalle fonti estratte. Crea nuove pagine "
            "per concetti non presenti, aggiorna quelle esistenti con nuove informazioni, aggiungi "
            "[[wiki-links]] e annota contraddizioni o incertezze."
        )

    return f"""Sei Codex usato come LLM manutentore di una LLM Wiki locale.

Obiettivo:
{task}

Cartelle, relative alla working directory:
- raw/: fonti originali caricate dall'utente. Non modificarle.
- .codex_sources/: testo estratto dalle fonti per facilitare la lettura. Non modificarlo.
- wiki/: knowledge base Markdown da creare e mantenere. Scrivi solo qui.

Fonti preparate:
{source_list}

Best practice obbligatorie per la LLM Wiki:
1. La wiki e' incrementale: prima preserva e migliora la struttura esistente, poi aggiungi nuove pagine solo se servono davvero.
2. Ogni pagina deve essere atomica: un solo concetto, processo, entita, decisione, progetto o persona. Se una pagina copre piu' temi distinti, dividila.
3. Evita duplicati semantici: se due pagine parlano della stessa cosa con titoli diversi, convergile in una pagina canonica e aggiorna i link.
4. Non inventare fatti. Scrivi solo informazioni supportate dalle fonti o gia' presenti nella wiki. Se un'inferenza e' utile ma non certa, etichettala come dubbio o ipotesi.
5. Mantieni chiara separazione tra fatti, interpretazioni e incertezze.
6. Preferisci testo denso ma leggibile: frasi brevi, sezioni stabili, niente marketing, niente ripetizioni inutili.
7. Usa nomi file in kebab-case ASCII, stabili e descrittivi, per esempio transformer-architecture.md.
8. Il titolo H1 puo' essere piu' naturale del file name, ma deve identificare chiaramente il concetto canonico della pagina.
9. Ogni pagina deve avere almeno questa struttura minima:
   # Titolo
   ## Sintesi
   ## Dettagli
   ## Collegamenti
   ## Contraddizioni o dubbi
   ## Fonti
10. In ## Sintesi scrivi 2-5 bullet o un paragrafo breve che permetta di capire subito perche' la pagina esiste.
11. In ## Dettagli organizza l'informazione in sottosezioni brevi e orientate al recupero: contesto, responsabilita, flusso, decisioni, dati chiave, esempi.
12. In ## Collegamenti usa link wiki in stile Obsidian come [[Nome Concetto]] e crea collegamenti espliciti verso pagine correlate, prerequisiti, componenti dipendenti e concetti superiori/inferiori.
13. Ogni pagina nuova o sostanzialmente aggiornata deve avere almeno un link uscente sensato; quando possibile evita pagine orfane anche in ingresso.
14. Se un concetto citato ricorre piu' volte o ha valore autonomo, crea o aggiorna una pagina dedicata invece di lasciarlo sepolto in una pagina piu' ampia.
15. Se una pagina e' troppo breve e senza autonomia semantica, integrala in una pagina piu' adatta invece di moltiplicare note deboli.
16. Mantieni wiki/_index.md come indice curatoriale della knowledge base: raggruppa le pagine per aree tematiche e aggiungi una descrizione breve e utile per ciascuna voce o gruppo.
17. Mantieni wiki/_log.md come log operativo append-only con data/ora, modalita' del run, fonti considerate, pagine create, pagine aggiornate, pagine unite/divise e dubbi aperti.
18. Nella sezione ## Fonti cita sempre i file sorgente rilevanti usando percorsi o nomi espliciti; se una pagina deriva anche da wiki preesistente, indicalo brevemente.
19. Se una fonte contraddice contenuto esistente, non cancellare il conflitto: registralo in ## Contraddizioni o dubbi, specificando quali fonti o pagine sono in tensione.
20. Se le fonti non bastano per una conclusione affidabile, conserva una pagina minima ma utile, dichiarando il gap informativo invece di riempirlo con testo speculativo.
21. Mantieni coerenza lessicale: scegli un nome canonico per entita, ruoli, progetti e acronimi; usa varianti e alias nel testo solo se aiutano il recupero.
22. Quando utile, aggiungi cross-link anche per persone, clienti, progetti, capability, deliverable, strumenti, metriche e dipendenze tecniche.
23. Non riscrivere l'intera wiki senza motivo: modifica solo i file Markdown necessari per ottenere un miglioramento netto e verificabile.
24. Non modificare codice applicativo, database, raw/ o .codex_sources/.

Procedura di lavoro obbligatoria:
1. Leggi prima .codex_sources/manifest.json, poi le fonti in .codex_sources/, poi le pagine gia' presenti in wiki/ rilevanti per i concetti trovati.
2. Identifica i concetti canonici, le entita nominate, le relazioni e gli eventuali conflitti o sovrapposizioni.
3. Decidi per ogni concetto se creare, aggiornare, unire, dividere o lasciare invariata una pagina esistente.
4. Aggiorna sempre anche _index.md e _log.md se il contenuto della wiki cambia.
5. Prima di concludere, controlla: naming coerente, sezioni minime presenti, link sensati, fonti esplicite, nessuna affermazione importante senza supporto.

Criteri specifici per questa esecuzione:
- Se mode = compile: privilegia copertura incrementale, nuove pagine utili e consolidamento della rete di link.
- Se mode = lint: privilegia qualita' editoriale e strutturale, senza introdurre contenuto non supportato dalle fonti.

Output finale richiesto:
- Rispondi con un riepilogo breve ma concreto di pagine create, aggiornate, unite o divise.
- Elenca i dubbi residui, le contraddizioni aperte e le aree che richiedono ulteriori fonti.
"""


def _ps_quote(value: str | Path) -> str:
    return "'" + str(value).replace("'", "''") + "'"


def _build_codex_powershell_script(settings: Settings, prompt_path: Path, output_path: Path) -> str:
    codex_args = [
        "exec",
        "--skip-git-repo-check",
        "--full-auto",
        "--ephemeral",
        "-C",
        str(settings.source_dir),
        "-o",
        str(output_path),
        "-",
    ]
    if settings.codex_model:
        codex_args[1:1] = ["--model", settings.codex_model]

    quoted_args = " ".join(_ps_quote(arg) for arg in codex_args)
    return f"""
$ErrorActionPreference = 'Stop'
$codexCommand = {_ps_quote(settings.codex_command)}
$commandInfo = Get-Command $codexCommand -ErrorAction SilentlyContinue
if (-not $commandInfo -and -not (Test-Path -LiteralPath $codexCommand)) {{
    throw "Codex CLI non trovato nel PATH della shell locale: $codexCommand"
}}
Get-Content -LiteralPath {_ps_quote(prompt_path)} -Raw | & $codexCommand {quoted_args}
exit $LASTEXITCODE
""".strip()


def run_codex_wiki_job(settings: Settings, mode: str = "compile") -> CodexRunResult:
    started = time.monotonic()
    sources = prepare_sources_for_codex(settings)

    if mode == "compile" and not sources:
        return CodexRunResult(
            ok=False,
            mode=mode,
            returncode=2,
            elapsed_seconds=0,
            message="Nessuna fonte trovata in raw/. Carica almeno un file supportato.",
            stdout="",
            stderr="",
            sources=sources,
        )

    prompt = build_codex_prompt(settings, mode, sources)
    source_text_dir = _source_text_dir(settings)
    prompt_path = source_text_dir / "codex-prompt.txt"
    output_path = source_text_dir / "codex-last-message.txt"
    prompt_path.write_text(prompt, encoding="utf-8")
    script = _build_codex_powershell_script(settings, prompt_path, output_path)

    try:
        completed = subprocess.run(
            [
                settings.codex_shell,
                "-NoLogo",
                "-NoProfile",
                "-ExecutionPolicy",
                "Bypass",
                "-Command",
                script,
            ],
            capture_output=True,
            text=True,
            timeout=settings.codex_timeout_seconds,
            cwd=str(settings.source_dir),
        )
    except FileNotFoundError:
        elapsed = time.monotonic() - started
        return CodexRunResult(
            ok=False,
            mode=mode,
            returncode=127,
            elapsed_seconds=elapsed,
            message=f"Shell locale non trovata: {settings.codex_shell}",
            stdout="",
            stderr="",
            sources=sources,
        )
    except subprocess.TimeoutExpired as exc:
        elapsed = time.monotonic() - started
        return CodexRunResult(
            ok=False,
            mode=mode,
            returncode=124,
            elapsed_seconds=elapsed,
            message=f"Codex ha superato il timeout di {settings.codex_timeout_seconds} secondi.",
            stdout=exc.stdout or "",
            stderr=exc.stderr or "",
            sources=sources,
        )

    elapsed = time.monotonic() - started
    stdout = completed.stdout or ""
    stderr = completed.stderr or ""
    ok = completed.returncode == 0
    returncode = completed.returncode
    error_message = stderr.strip().splitlines()[-1] if stderr.strip() else ""

    if ok and mode == "compile":
        moved_count, move_errors = move_raw_sources_to_processed(settings.raw_dir)
        if move_errors:
            ok = False
            returncode = 3
            message = (
                "Codex ha aggiornato la wiki, ma lo spostamento in processed/ e' incompleto. "
                f"File spostati: {moved_count}, errori: {len(move_errors)}."
            )
            details = "\n".join(move_errors)
            stderr = (stderr + "\n\n" if stderr else "") + f"Errori spostamento in processed/:\n{details}"
        else:
            message = f"Codex ha aggiornato la wiki e spostato {moved_count} file in processed/."
    else:
        message = "Codex ha aggiornato la wiki." if ok else error_message or "Codex non ha completato la compilazione."

    return CodexRunResult(
        ok=ok,
        mode=mode,
        returncode=returncode,
        elapsed_seconds=elapsed,
        message=message,
        stdout=stdout,
        stderr=stderr,
        sources=sources,
    )
