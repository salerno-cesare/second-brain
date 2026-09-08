from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Sequence

from .config import Settings, get_settings
from .wiki import (
    FUNCTIONAL_REQUIREMENTS_WIKI_DIR_NAME,
    TOGAF_WIKI_DIR_NAME,
    get_configured_wiki_language,
    list_open_wiki_doubts,
    list_wiki_pages,
    normalize_wiki_language,
    read_wiki_page,
    run_codex_wiki_job,
    search_wiki_pages,
    wiki_language_label,
)


JOB_COMMANDS = ("compile", "requirements", "togaf", "lint")
AREA_CHOICES = ("wiki", "requirements", "togaf")


def _add_area_argument(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--area",
        choices=AREA_CHOICES,
        default="wiki",
        help="Area da interrogare (default: wiki).",
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="wiki",
        description="CLI locale per compilare e consultare la LLM Wiki.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    for command in JOB_COMMANDS:
        job_parser = subparsers.add_parser(command, help=f"Esegue il job wiki '{command}'.")
        job_parser.add_argument(
            "--language",
            "-l",
            default="it",
            help="Codice lingua della wiki (default: it; ignorato se la lingua e' gia' bloccata).",
        )

    pages_parser = subparsers.add_parser("pages", help="Elenca le pagine wiki disponibili.")
    _add_area_argument(pages_parser)

    search_parser = subparsers.add_parser("search", help="Cerca testo nelle pagine wiki.")
    search_parser.add_argument("query", help="Testo da cercare.")
    search_parser.add_argument("--limit", type=int, default=30, help="Numero massimo di risultati (default: 30).")
    _add_area_argument(search_parser)

    show_parser = subparsers.add_parser("show", help="Stampa una pagina Markdown.")
    show_parser.add_argument("slug", help="Slug della pagina, con o senza estensione .md.")
    _add_area_argument(show_parser)

    subparsers.add_parser("doubts", help="Elenca i dubbi aperti della wiki.")
    subparsers.add_parser("status", help="Mostra configurazione e lingua della wiki locale.")
    return parser


def _area_dir(settings: Settings, area: str) -> Path:
    if area == "togaf":
        return settings.wiki_dir / TOGAF_WIKI_DIR_NAME
    if area == "requirements":
        return settings.wiki_dir / FUNCTIONAL_REQUIREMENTS_WIKI_DIR_NAME
    return settings.wiki_dir


def _progress(stream: str, text: str) -> None:
    if not text:
        return
    target = sys.stderr if stream == "stderr" else sys.stdout
    prefix = "[wiki] " if stream == "status" else ""
    print(f"{prefix}{text}", file=target, flush=True)


def _run_job(settings: Settings, command: str, language: str) -> int:
    try:
        language = normalize_wiki_language(language)
    except ValueError as exc:
        print(f"Errore: {exc}", file=sys.stderr)
        return 2

    configured_language = get_configured_wiki_language(settings.wiki_dir)
    if configured_language:
        language = configured_language

    print(f"[wiki] Job: {command} | lingua: {wiki_language_label(language)}", flush=True)
    try:
        result = run_codex_wiki_job(
            settings,
            mode=command,
            language=language,
            progress_callback=_progress,
        )
    except (OSError, ValueError) as exc:
        print(f"Errore: {exc}", file=sys.stderr)
        return 1

    print(f"[wiki] {result.message}", flush=True)
    print(f"[wiki] Durata: {result.elapsed_seconds:.2f}s", flush=True)
    return 0 if result.ok else (result.returncode or 1)


def _list_pages(settings: Settings, area: str) -> int:
    pages = list_wiki_pages(_area_dir(settings, area))
    if not pages:
        print(f"Nessuna pagina nell'area '{area}'.")
        return 0
    for page in pages:
        print(f"{page.slug}\t{page.title}")
    return 0


def _search(settings: Settings, area: str, query: str, limit: int) -> int:
    if limit < 1:
        print("Errore: --limit deve essere maggiore di zero.", file=sys.stderr)
        return 2
    results = search_wiki_pages(_area_dir(settings, area), query, limit=limit)
    if not results:
        print("Nessun risultato.")
        return 0
    for result in results:
        print(f"{result['slug']}\t{result['title']}")
    return 0


def _show(settings: Settings, area: str, slug: str) -> int:
    page = read_wiki_page(_area_dir(settings, area), slug.removesuffix(".md"))
    if page is None:
        print(f"Errore: pagina '{slug}' non trovata nell'area '{area}'.", file=sys.stderr)
        return 1
    _, markdown = page
    print(markdown, end="" if markdown.endswith("\n") else "\n")
    return 0


def _list_doubts(settings: Settings) -> int:
    doubts = list_open_wiki_doubts(settings.wiki_dir)
    if not doubts:
        print("Nessun dubbio aperto.")
        return 0
    for doubt in doubts:
        print(f"{doubt.id}\t{doubt.page_title}\t{doubt.text}")
    return 0


def _status(settings: Settings) -> int:
    language = get_configured_wiki_language(settings.wiki_dir)
    print(f"Wiki: {settings.wiki_dir}")
    print(f"Fonti raw: {settings.raw_dir}")
    print(f"Codex: {settings.codex_command} (shell: {settings.codex_shell})")
    print(f"Lingua: {wiki_language_label(language) if language else 'non configurata'}")
    return 0


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    settings = get_settings()

    if args.command in JOB_COMMANDS:
        return _run_job(settings, args.command, args.language)
    if args.command == "pages":
        return _list_pages(settings, args.area)
    if args.command == "search":
        return _search(settings, args.area, args.query, args.limit)
    if args.command == "show":
        return _show(settings, args.area, args.slug)
    if args.command == "doubts":
        return _list_doubts(settings)
    if args.command == "status":
        return _status(settings)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
