from __future__ import annotations

import html
import os
import queue
import re
import shutil
import subprocess
import sys
import threading
import time
import unicodedata
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable

from .config import Settings
from .ingest import is_graphify_generated_path, is_supported_file

WIKI_LINK_RE = re.compile(r"\[\[([^\]\|]+)(?:\|([^\]]+))?\]\]")
TOGAF_META_RE = re.compile(
    r"^-\s*(Fase ADM|Dominio architetturale|Tipo artefatto|Template di riferimento|Stato contenuto):\s*(.+?)\s*$",
    re.MULTILINE | re.IGNORECASE,
)
FUNCTIONAL_REQUIREMENT_META_RE = re.compile(
    r"^-\s*(Tipo requisito|Epica|Priorita|Stato|Fase|Fonte wiki):\s*(.+?)\s*$",
    re.MULTILINE | re.IGNORECASE,
)


@dataclass(frozen=True)
class WikiPage:
    slug: str
    title: str
    rel_path: str
    updated_at: str
    size: int
    links: int


@dataclass(frozen=True)
class GraphifySource:
    rel_path: str
    size: int
    updated_at: str


@dataclass(frozen=True)
class GraphifyRunResult:
    ok: bool
    mode: str
    returncode: int
    elapsed_seconds: float
    message: str
    stdout: str
    stderr: str
    sources: list[GraphifySource]


GraphifyProgressCallback = Callable[[str, str], None]


@dataclass(frozen=True)
class _StreamingProcessResult:
    returncode: int
    stdout: str
    stderr: str


@dataclass(frozen=True)
class _WikiDocument:
    page: WikiPage
    markdown: str


WIKI_CONFIG_FILE = "_config.md"
TOGAF_WIKI_DIR_NAME = "togaf"
FUNCTIONAL_REQUIREMENTS_WIKI_DIR_NAME = "requisiti-funzionali"
WIKI_LANGUAGE_RE = re.compile(r"^-\s*Codice lingua:\s*([a-z]{2})\s*$", re.MULTILINE)
TOGAF_PHASE_ORDER = [
    "Preliminary Phase",
    "Phase A - Architecture Vision",
    "Phase B - Business Architecture",
    "Phase C - Information Systems Architecture",
    "Phase D - Technology Architecture",
    "Phase E - Opportunities and Solutions",
    "Phase F - Migration Planning",
    "Phase G - Implementation Governance",
    "Phase H - Architecture Change Management",
]

WIKI_LANGUAGE_OPTIONS: dict[str, str] = {
    "it": "Italian",
    "en": "English",
    "es": "Spanish",
    "fr": "French",
    "de": "German",
    "pt": "Portuguese",
    "nl": "Dutch",
    "pl": "Polish",
    "ro": "Romanian",
    "ar": "Arabic",
    "zh": "Simplified Chinese",
    "ja": "Japanese",
}
DEFAULT_WIKI_LANGUAGE = "it"


def normalize_wiki_language(language: str | None) -> str:
    code = (language or DEFAULT_WIKI_LANGUAGE).strip().lower()
    return code if code in WIKI_LANGUAGE_OPTIONS else DEFAULT_WIKI_LANGUAGE


def wiki_language_label(language: str | None) -> str:
    return WIKI_LANGUAGE_OPTIONS[normalize_wiki_language(language)]


def read_wiki_config_markdown(wiki_dir: Path) -> str:
    config_path = wiki_dir / WIKI_CONFIG_FILE
    if not config_path.exists():
        return ""

    try:
        return config_path.read_text(encoding="utf-8")
    except OSError:
        return ""


def _format_wiki_config_markdown(language: str) -> str:
    language = normalize_wiki_language(language)
    return (
        "# Configurazione Wiki\n\n"
        "Questa pagina contiene impostazioni strutturali della wiki locale.\n\n"
        "## Lingua\n\n"
        f"- Codice lingua: {language}\n"
        f"- Nome lingua: {wiki_language_label(language)}\n"
        "- Bloccata: si\n"
        f"- Creata il: {datetime.now(timezone.utc).isoformat()}\n\n"
        "## Note operative\n\n"
        "- La lingua viene scelta alla prima compilazione della wiki.\n"
        "- Dopo il salvataggio, la lingua non viene modificata dalla UI.\n"
    )


def _append_wiki_config_log(wiki_dir: Path, language: str) -> None:
    log_path = wiki_dir / "_log.md"
    if log_path.exists():
        try:
            current_log = log_path.read_text(encoding="utf-8")
        except OSError:
            return
    else:
        current_log = "# Log operativo\n\n"

    timestamp = datetime.now().astimezone().isoformat(timespec="seconds")
    entry = (
        f"\n## {timestamp} - configurazione lingua\n\n"
        "- Pagine create:\n"
        "  - [[_config|Configurazione Wiki]]\n"
        "- Pagine aggiornate:\n"
        "  - [[_log|Log operativo]]\n"
        f"- Lingua wiki bloccata: {wiki_language_label(language)} (`{language}`).\n"
        "- Dubbi aperti:\n"
        "  - Nessuno.\n"
    )

    try:
        log_path.write_text(current_log.rstrip() + entry + "\n", encoding="utf-8")
    except OSError:
        return


def get_configured_wiki_language(wiki_dir: Path) -> str | None:
    markdown = read_wiki_config_markdown(wiki_dir)
    match = WIKI_LANGUAGE_RE.search(markdown)
    if not match:
        return None
    return normalize_wiki_language(match.group(1))


def ensure_wiki_language_config(wiki_dir: Path, language: str | None) -> str:
    configured_language = get_configured_wiki_language(wiki_dir)
    if configured_language:
        return configured_language

    selected_language = normalize_wiki_language(language)
    wiki_dir.mkdir(parents=True, exist_ok=True)
    (wiki_dir / WIKI_CONFIG_FILE).write_text(_format_wiki_config_markdown(selected_language), encoding="utf-8")
    _append_wiki_config_log(wiki_dir, selected_language)
    return selected_language


def ensure_wiki_layout(settings: Settings) -> None:
    settings.source_dir.mkdir(parents=True, exist_ok=True)
    settings.raw_dir.mkdir(parents=True, exist_ok=True)
    settings.wiki_dir.mkdir(parents=True, exist_ok=True)

    index_path = settings.wiki_dir / "_index.md"
    if not index_path.exists():
        index_path.write_text(
            "# Indice Wiki\n\n"
            "Questa pagina viene aggiornata da Graphify durante la compilazione della knowledge base.\n",
            encoding="utf-8",
        )


def ensure_togaf_layout(settings: Settings) -> None:
    togaf_dir = settings.wiki_dir / TOGAF_WIKI_DIR_NAME
    togaf_dir.mkdir(parents=True, exist_ok=True)

    togaf_index_path = togaf_dir / "_index.md"
    if not togaf_index_path.exists():
        togaf_index_path.write_text(
            "# Indice TOGAF\n\n"
            "Questa wiki alternativa indicizza i contenuti della knowledge base secondo viste e artefatti TOGAF.\n\n"
            "## Artefatti\n\n"
            "- Nessun artefatto TOGAF ancora generato.\n",
            encoding="utf-8",
        )

    togaf_log_path = togaf_dir / "_log.md"
    if not togaf_log_path.exists():
        togaf_log_path.write_text(
            "# Log operativo TOGAF\n\n"
            "Questo log traccia le modifiche alla wiki alternativa TOGAF.\n",
            encoding="utf-8",
        )


def ensure_functional_requirements_layout(settings: Settings) -> None:
    requirements_dir = settings.wiki_dir / FUNCTIONAL_REQUIREMENTS_WIKI_DIR_NAME
    requirements_dir.mkdir(parents=True, exist_ok=True)

    requirements_index_path = requirements_dir / "_index.md"
    if not requirements_index_path.exists():
        requirements_index_path.write_text(
            "# Indice Requisiti Funzionali\n\n"
            "Questa wiki parallela indicizza solo requisiti software funzionali, organizzati in epiche e user story.\n\n"
            "## Epiche\n\n"
            "- Nessun requisito funzionale ancora generato.\n",
            encoding="utf-8",
        )

    requirements_log_path = requirements_dir / "_log.md"
    if not requirements_log_path.exists():
        requirements_log_path.write_text(
            "# Log operativo Requisiti Funzionali\n\n"
            "Questo log traccia le modifiche alla wiki parallela dei requisiti funzionali.\n",
            encoding="utf-8",
        )


def slugify_wiki_title(title: str) -> str:
    normalized = unicodedata.normalize("NFKD", title)
    ascii_text = normalized.encode("ascii", "ignore").decode("ascii")
    slug = re.sub(r"[^a-z0-9]+", "-", ascii_text.lower()).strip("-")
    return slug or "pagina"


def title_from_markdown(path: Path) -> str:
    try:
        return title_from_markdown_text(path.read_text(encoding="utf-8", errors="ignore"), path.stem)
    except OSError:
        return path.stem.replace("-", " ").replace("_", " ").title()


def title_from_markdown_text(markdown: str, fallback_slug: str) -> str:
    for line in markdown.splitlines():
        stripped = line.strip()
        if stripped.startswith("# "):
            return stripped[2:].strip()

    return fallback_slug.replace("-", " ").replace("_", " ").title()


def _load_wiki_documents(wiki_dir: Path) -> list[_WikiDocument]:
    if not wiki_dir.exists():
        return []

    documents: list[_WikiDocument] = []
    for path in sorted(wiki_dir.glob("*.md"), key=lambda item: item.name.lower()):
        markdown = path.read_text(encoding="utf-8", errors="ignore")
        stat = path.stat()
        documents.append(
            _WikiDocument(
                page=WikiPage(
                    slug=path.stem,
                    title=title_from_markdown_text(markdown, path.stem),
                    rel_path=path.name,
                    updated_at=datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M"),
                    size=stat.st_size,
                    links=len(WIKI_LINK_RE.findall(markdown)),
                ),
                markdown=markdown,
            )
        )

    return documents


def list_wiki_pages(wiki_dir: Path) -> list[WikiPage]:
    return [document.page for document in _load_wiki_documents(wiki_dir)]


def _wiki_title_map(wiki_dir: Path) -> dict[str, str]:
    return _wiki_title_map_from_documents(_load_wiki_documents(wiki_dir))


def _wiki_title_map_from_documents(documents: list[_WikiDocument]) -> dict[str, str]:
    mapping: dict[str, str] = {}
    for document in documents:
        mapping[slugify_wiki_title(document.page.title)] = document.page.slug
        mapping[slugify_wiki_title(document.page.slug)] = document.page.slug
    return mapping


def _wiki_documents_by_slug(documents: list[_WikiDocument]) -> dict[str, _WikiDocument]:
    return {document.page.slug: document for document in documents}


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
        title=title_from_markdown_text(content, target.stem),
        rel_path=target.name,
        updated_at=datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M"),
        size=stat.st_size,
        links=len(WIKI_LINK_RE.findall(content)),
    )
    return page, content


def _resolve_wiki_link(
    target_title: str,
    label: str,
    title_map: dict[str, str],
    pages_by_slug: dict[str, _WikiDocument],
    link_base_path: str,
    fallback_title_map: dict[str, str] | None = None,
    fallback_pages_by_slug: dict[str, _WikiDocument] | None = None,
    fallback_link_base_path: str = "/wiki",
) -> dict:
    title_key = slugify_wiki_title(target_title)
    slug = title_map.get(title_key, title_key)
    target = pages_by_slug.get(slug)
    base_path = link_base_path

    if not target and fallback_title_map is not None and fallback_pages_by_slug is not None:
        fallback_slug = fallback_title_map.get(title_key, title_key)
        fallback_target = fallback_pages_by_slug.get(fallback_slug)
        if fallback_target:
            slug = fallback_slug
            target = fallback_target
            base_path = fallback_link_base_path

    exists = target is not None
    title = target.page.title if target else target_title
    return {
        "slug": slug,
        "title": title,
        "label": label,
        "exists": exists,
        "base_path": base_path,
        "href": f"{base_path}/{slug}",
    }


def extract_wiki_links(
    markdown: str,
    wiki_dir: Path,
    title_map: dict[str, str] | None = None,
    pages_by_slug: dict[str, _WikiDocument] | None = None,
    fallback_title_map: dict[str, str] | None = None,
    fallback_pages_by_slug: dict[str, _WikiDocument] | None = None,
    link_base_path: str = "/wiki",
    fallback_link_base_path: str = "/wiki",
) -> list[dict]:
    title_map = title_map or _wiki_title_map(wiki_dir)
    pages_by_slug = pages_by_slug or _wiki_documents_by_slug(_load_wiki_documents(wiki_dir))
    links: list[dict] = []
    seen: set[tuple[str, str, str]] = set()

    for match in WIKI_LINK_RE.finditer(markdown):
        target_title = match.group(1).strip()
        label = (match.group(2) or target_title).strip()
        resolved = _resolve_wiki_link(
            target_title,
            label,
            title_map,
            pages_by_slug,
            link_base_path,
            fallback_title_map,
            fallback_pages_by_slug,
            fallback_link_base_path,
        )
        key = (resolved["base_path"], resolved["slug"], label)
        if key in seen:
            continue
        seen.add(key)
        links.append(resolved)

    return links


def get_wiki_backlinks(
    wiki_dir: Path,
    target_slug: str,
    documents: list[_WikiDocument] | None = None,
    title_map: dict[str, str] | None = None,
    pages_by_slug: dict[str, _WikiDocument] | None = None,
) -> list[dict]:
    documents = documents or _load_wiki_documents(wiki_dir)
    title_map = title_map or _wiki_title_map_from_documents(documents)
    pages_by_slug = pages_by_slug or _wiki_documents_by_slug(documents)
    backlinks: list[dict] = []
    safe_target_slug = Path(target_slug).name

    for document in documents:
        page = document.page
        if page.slug == safe_target_slug:
            continue

        matching_links = [
            link
            for link in extract_wiki_links(document.markdown, wiki_dir, title_map, pages_by_slug)
            if link["slug"] == safe_target_slug
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


def get_wiki_page_payload(
    wiki_dir: Path,
    slug: str,
    link_base_path: str = "/wiki",
    fallback_wiki_dir: Path | None = None,
    fallback_link_base_path: str = "/wiki",
) -> dict | None:
    documents = _load_wiki_documents(wiki_dir)
    pages_by_slug = _wiki_documents_by_slug(documents)
    safe_slug = Path(slug).name
    document = pages_by_slug.get(safe_slug)
    if not document:
        return None

    title_map = _wiki_title_map_from_documents(documents)
    fallback_documents = _load_wiki_documents(fallback_wiki_dir) if fallback_wiki_dir else []
    fallback_title_map = _wiki_title_map_from_documents(fallback_documents) if fallback_documents else None
    fallback_pages_by_slug = _wiki_documents_by_slug(fallback_documents) if fallback_documents else None
    return {
        "page": document.page.__dict__,
        "markdown": document.markdown,
        "html": render_wiki_markdown(
            document.markdown,
            wiki_dir,
            title_map,
            pages_by_slug,
            link_base_path,
            fallback_title_map=fallback_title_map,
            fallback_pages_by_slug=fallback_pages_by_slug,
            fallback_link_base_path=fallback_link_base_path,
        ),
        "outgoing": extract_wiki_links(
            document.markdown,
            wiki_dir,
            title_map,
            pages_by_slug,
            fallback_title_map=fallback_title_map,
            fallback_pages_by_slug=fallback_pages_by_slug,
            link_base_path=link_base_path,
            fallback_link_base_path=fallback_link_base_path,
        ),
        "backlinks": get_wiki_backlinks(wiki_dir, document.page.slug, documents, title_map, pages_by_slug),
    }


def get_togaf_page_payload(wiki_dir: Path, slug: str) -> dict | None:
    payload = get_wiki_page_payload(
        wiki_dir,
        slug,
        link_base_path="/togaf",
        fallback_wiki_dir=wiki_dir.parent,
        fallback_link_base_path="/wiki",
    )
    if not payload:
        return None
    payload["togaf"] = extract_togaf_metadata(payload["markdown"], payload["page"])
    return payload


def get_functional_requirements_page_payload(wiki_dir: Path, slug: str) -> dict | None:
    payload = get_wiki_page_payload(
        wiki_dir,
        slug,
        link_base_path="/requirements",
        fallback_wiki_dir=wiki_dir.parent,
        fallback_link_base_path="/wiki",
    )
    if not payload:
        return None
    payload["requirement"] = extract_functional_requirement_metadata(payload["markdown"], payload["page"])
    return payload


def search_wiki_pages(wiki_dir: Path, query: str, limit: int = 30) -> list[dict]:
    normalized_query = query.strip().lower()
    if not normalized_query:
        return []

    matches: list[dict] = []
    for document in _load_wiki_documents(wiki_dir):
        page = document.page
        haystack = f"{page.title}\n{document.markdown}".lower()
        index = haystack.find(normalized_query)
        if index < 0:
            continue

        snippet_start = max(index - 80, 0)
        snippet_end = min(index + len(normalized_query) + 160, len(document.markdown))
        snippet = re.sub(r"\s+", " ", document.markdown[snippet_start:snippet_end]).strip()
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
    documents = _load_wiki_documents(wiki_dir)
    pages = [document.page for document in documents]
    known_slugs = {page.slug for page in pages}
    title_map = _wiki_title_map_from_documents(documents)
    pages_by_slug = _wiki_documents_by_slug(documents)
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

    for document in documents:
        page = document.page
        for link in extract_wiki_links(document.markdown, wiki_dir, title_map, pages_by_slug):
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


def extract_togaf_metadata(markdown: str, page: dict | WikiPage) -> dict:
    metadata = {
        "adm_phase": "Unclassified",
        "domain": "Unclassified",
        "artifact_type": "Artifact",
        "template_reference": "Not specified",
        "status": "To verify",
    }
    label_map = {
        "fase adm": "adm_phase",
        "dominio architetturale": "domain",
        "tipo artefatto": "artifact_type",
        "template di riferimento": "template_reference",
        "stato contenuto": "status",
    }
    for match in TOGAF_META_RE.finditer(markdown):
        key = label_map.get(match.group(1).strip().lower())
        if key:
            metadata[key] = match.group(2).strip()

    if isinstance(page, WikiPage):
        metadata["slug"] = page.slug
        metadata["title"] = page.title
        metadata["rel_path"] = page.rel_path
        metadata["links"] = page.links
    else:
        metadata["slug"] = page.get("slug", "")
        metadata["title"] = page.get("title", "")
        metadata["rel_path"] = page.get("rel_path", "")
        metadata["links"] = page.get("links", 0)
    return metadata


def extract_functional_requirement_metadata(markdown: str, page: dict | WikiPage) -> dict:
    metadata = {
        "requirement_type": "Requirement",
        "epic": "Unclassified",
        "priority": "Not specified",
        "status": "To verify",
        "phase": "Not specified",
        "wiki_source": "Not specified",
    }
    label_map = {
        "tipo requisito": "requirement_type",
        "epica": "epic",
        "priorita": "priority",
        "stato": "status",
        "fase": "phase",
        "fonte wiki": "wiki_source",
    }
    for match in FUNCTIONAL_REQUIREMENT_META_RE.finditer(markdown):
        key = label_map.get(match.group(1).strip().lower())
        if key:
            metadata[key] = match.group(2).strip()

    if isinstance(page, WikiPage):
        metadata["slug"] = page.slug
        metadata["title"] = page.title
        metadata["rel_path"] = page.rel_path
        metadata["links"] = page.links
    else:
        metadata["slug"] = page.get("slug", "")
        metadata["title"] = page.get("title", "")
        metadata["rel_path"] = page.get("rel_path", "")
        metadata["links"] = page.get("links", 0)
    return metadata


def list_togaf_artifacts(togaf_dir: Path) -> dict:
    documents = _load_wiki_documents(togaf_dir)
    artifacts = [
        extract_togaf_metadata(document.markdown, document.page)
        for document in documents
        if not document.page.slug.startswith("_")
    ]
    groups: dict[str, list[dict]] = {}
    phases: dict[str, list[dict]] = {}
    types: dict[str, list[dict]] = {}

    for artifact in artifacts:
        groups.setdefault(artifact["domain"], []).append(artifact)
        phases.setdefault(artifact["adm_phase"], []).append(artifact)
        types.setdefault(artifact["artifact_type"], []).append(artifact)

    def ordered(mapping: dict[str, list[dict]], preferred_order: list[str] | None = None) -> list[dict]:
        order = {name: index for index, name in enumerate(preferred_order or [])}
        return [
            {"name": name, "artifacts": sorted(items, key=lambda item: item["title"].lower())}
            for name, items in sorted(mapping.items(), key=lambda item: (order.get(item[0], 999), item[0].lower()))
        ]

    return {
        "artifacts": sorted(artifacts, key=lambda item: item["title"].lower()),
        "domains": ordered(groups),
        "phases": ordered(phases, TOGAF_PHASE_ORDER),
        "types": ordered(types),
    }


def list_functional_requirements(requirements_dir: Path) -> dict:
    documents = _load_wiki_documents(requirements_dir)
    requirements = [
        extract_functional_requirement_metadata(document.markdown, document.page)
        for document in documents
        if not document.page.slug.startswith("_")
    ]
    epics: dict[str, list[dict]] = {}
    types: dict[str, list[dict]] = {}
    statuses: dict[str, list[dict]] = {}

    for requirement in requirements:
        epics.setdefault(requirement["epic"], []).append(requirement)
        types.setdefault(requirement["requirement_type"], []).append(requirement)
        statuses.setdefault(requirement["status"], []).append(requirement)

    def ordered(mapping: dict[str, list[dict]]) -> list[dict]:
        return [
            {"name": name, "requirements": sorted(items, key=lambda item: item["title"].lower())}
            for name, items in sorted(mapping.items(), key=lambda item: item[0].lower())
        ]

    return {
        "requirements": sorted(requirements, key=lambda item: item["title"].lower()),
        "epics": ordered(epics),
        "types": ordered(types),
        "statuses": ordered(statuses),
    }


def render_wiki_markdown(
    markdown: str,
    wiki_dir: Path,
    title_map: dict[str, str] | None = None,
    pages_by_slug: dict[str, _WikiDocument] | None = None,
    link_base_path: str = "/wiki",
    fallback_title_map: dict[str, str] | None = None,
    fallback_pages_by_slug: dict[str, _WikiDocument] | None = None,
    fallback_link_base_path: str = "/wiki",
) -> str:
    title_map = title_map or _wiki_title_map(wiki_dir)
    pages_by_slug = pages_by_slug or _wiki_documents_by_slug(_load_wiki_documents(wiki_dir))

    def replace_wiki_link(match: re.Match[str]) -> str:
        target_title = match.group(1).strip()
        label = (match.group(2) or target_title).strip()
        resolved = _resolve_wiki_link(
            target_title,
            label,
            title_map,
            pages_by_slug,
            link_base_path,
            fallback_title_map,
            fallback_pages_by_slug,
            fallback_link_base_path,
        )
        exists = resolved["exists"]
        css_class = "wiki-link" if exists else "wiki-link missing"
        href = html.escape(resolved["href"])
        return f'<a class="{css_class}" href="{href}">{html.escape(label)}</a>'

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
        if not path.is_file() or is_graphify_generated_path(path) or not is_supported_file(path):
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


def list_graphify_sources(settings: Settings) -> list[GraphifySource]:
    if not settings.raw_dir.exists():
        return []

    source_root = settings.source_dir.resolve()
    sources: list[GraphifySource] = []
    for path in sorted(settings.raw_dir.rglob("*"), key=lambda item: str(item).lower()):
        if not path.is_file() or is_graphify_generated_path(path) or not is_supported_file(path):
            continue

        stat = path.stat()
        sources.append(
            GraphifySource(
                rel_path=str(path.resolve().relative_to(source_root)).replace("\\", "/"),
                size=stat.st_size,
                updated_at=datetime.fromtimestamp(stat.st_mtime).isoformat(timespec="seconds"),
            )
        )
    return sources


def _emit_graphify_progress(callback: GraphifyProgressCallback | None, stream: str, text: str) -> None:
    if callback:
        callback(stream, text)


def _read_process_stream(stream, stream_name: str, events: queue.Queue[tuple[str, str]]) -> None:
    try:
        for line in iter(stream.readline, ""):
            events.put((stream_name, line))
    finally:
        try:
            stream.close()
        except OSError:
            pass


def _run_graphify_command(
    settings: Settings,
    args: list[str],
    progress_callback: GraphifyProgressCallback | None,
) -> _StreamingProcessResult:
    command = [sys.executable, "-m", "graphify", *args]
    env = os.environ.copy()
    env.setdefault("PYTHONIOENCODING", "utf-8")

    process = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        errors="replace",
        bufsize=1,
        cwd=str(settings.source_dir),
        env=env,
    )

    events: queue.Queue[tuple[str, str]] = queue.Queue()
    stdout_parts: list[str] = []
    stderr_parts: list[str] = []
    readers = [
        threading.Thread(target=_read_process_stream, args=(process.stdout, "stdout", events), daemon=True),
        threading.Thread(target=_read_process_stream, args=(process.stderr, "stderr", events), daemon=True),
    ]
    for reader in readers:
        reader.start()

    started = time.monotonic()
    timed_out = False
    while True:
        try:
            stream, line = events.get(timeout=0.1)
        except queue.Empty:
            pass
        else:
            if stream == "stdout":
                stdout_parts.append(line)
            else:
                stderr_parts.append(line)
            _emit_graphify_progress(progress_callback, stream, line.rstrip("\r\n"))

        process_finished = process.poll() is not None
        readers_finished = all(not reader.is_alive() for reader in readers)
        if process_finished and readers_finished and events.empty():
            break

        if time.monotonic() - started > settings.graphify_timeout_seconds:
            timed_out = True
            process.kill()
            try:
                process.wait(timeout=2)
            except subprocess.TimeoutExpired:
                pass
            _emit_graphify_progress(
                progress_callback,
                "stderr",
                f"Graphify exceeded the {settings.graphify_timeout_seconds}-second timeout.",
            )
            break

    for reader in readers:
        reader.join(timeout=1)

    while not events.empty():
        stream, line = events.get_nowait()
        if stream == "stdout":
            stdout_parts.append(line)
        else:
            stderr_parts.append(line)
        _emit_graphify_progress(progress_callback, stream, line.rstrip("\r\n"))

    stdout = "".join(stdout_parts)
    stderr = "".join(stderr_parts)
    if timed_out:
        raise subprocess.TimeoutExpired(command, settings.graphify_timeout_seconds, output=stdout, stderr=stderr)

    return _StreamingProcessResult(process.returncode or 0, stdout, stderr)


def _run_streaming_process(
    command: list[str],
    cwd: Path,
    timeout_seconds: int,
    progress_callback: GraphifyProgressCallback | None,
    stdin_text: str | None = None,
) -> _StreamingProcessResult:
    env = os.environ.copy()
    env.setdefault("PYTHONIOENCODING", "utf-8")
    process = subprocess.Popen(
        command,
        stdin=subprocess.PIPE if stdin_text is not None else None,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        errors="replace",
        bufsize=1,
        cwd=str(cwd),
        env=env,
    )

    if stdin_text is not None:
        assert process.stdin is not None
        process.stdin.write(stdin_text)
        process.stdin.close()

    events: queue.Queue[tuple[str, str]] = queue.Queue()
    stdout_parts: list[str] = []
    stderr_parts: list[str] = []
    readers = [
        threading.Thread(target=_read_process_stream, args=(process.stdout, "stdout", events), daemon=True),
        threading.Thread(target=_read_process_stream, args=(process.stderr, "stderr", events), daemon=True),
    ]
    for reader in readers:
        reader.start()

    started = time.monotonic()
    timed_out = False
    while True:
        try:
            stream, line = events.get(timeout=0.1)
        except queue.Empty:
            pass
        else:
            if stream == "stdout":
                stdout_parts.append(line)
            else:
                stderr_parts.append(line)
            _emit_graphify_progress(progress_callback, stream, line.rstrip("\r\n"))

        process_finished = process.poll() is not None
        readers_finished = all(not reader.is_alive() for reader in readers)
        if process_finished and readers_finished and events.empty():
            break

        if time.monotonic() - started > timeout_seconds:
            timed_out = True
            process.kill()
            try:
                process.wait(timeout=2)
            except subprocess.TimeoutExpired:
                pass
            _emit_graphify_progress(progress_callback, "stderr", f"Process exceeded the {timeout_seconds}-second timeout.")
            break

    for reader in readers:
        reader.join(timeout=1)

    while not events.empty():
        stream, line = events.get_nowait()
        if stream == "stdout":
            stdout_parts.append(line)
        else:
            stderr_parts.append(line)
        _emit_graphify_progress(progress_callback, stream, line.rstrip("\r\n"))

    stdout = "".join(stdout_parts)
    stderr = "".join(stderr_parts)
    if timed_out:
        raise subprocess.TimeoutExpired(command, timeout_seconds, output=stdout, stderr=stderr)

    return _StreamingProcessResult(process.returncode or 0, stdout, stderr)


def _graphify_out_dir(settings: Settings) -> Path:
    return settings.graphify_out_dir / "graphify-out"


def _build_graphify_extract_args(settings: Settings) -> list[str]:
    args = [
        "extract",
        str(settings.raw_dir),
        "--out",
        str(settings.graphify_out_dir),
    ]
    if settings.graphify_backend:
        args.extend(["--backend", settings.graphify_backend])
    if settings.graphify_model:
        args.extend(["--model", settings.graphify_model])
    if settings.graphify_max_workers is not None:
        args.extend(["--max-workers", str(settings.graphify_max_workers)])
    if settings.graphify_token_budget is not None:
        args.extend(["--token-budget", str(settings.graphify_token_budget)])
    if settings.graphify_max_concurrency is not None:
        args.extend(["--max-concurrency", str(settings.graphify_max_concurrency)])
    return args


def _graphify_agent_prompt(settings: Settings) -> str:
    raw_path = str(settings.raw_dir.resolve()).replace('"', '\\"')
    return (
        f'/graphify "{raw_path}" --wiki\n\n'
        "Use the Graphify skill workflow. Build the knowledge graph and the wiki in graphify-out/. "
        "Do not use external Graphify API-key mode; use the CLI agent model for semantic extraction."
    )


def _ensure_graphify_codex_skill(settings: Settings, progress_callback: GraphifyProgressCallback | None) -> str:
    _emit_graphify_progress(progress_callback, "status", "Ensuring Graphify skill is installed for Codex CLI...")
    completed = _run_graphify_command(
        settings,
        ["install", "--platform", "codex"],
        progress_callback,
    )
    if completed.returncode != 0:
        error = completed.stderr.strip().splitlines()[-1] if completed.stderr.strip() else "Graphify Codex skill install failed."
        raise RuntimeError(error)
    return (completed.stdout or "") + (completed.stderr or "")


def _run_graphify_agent_cli(
    settings: Settings,
    progress_callback: GraphifyProgressCallback | None,
) -> _StreamingProcessResult:
    _ensure_graphify_codex_skill(settings, progress_callback)
    output_path = _graphify_out_dir(settings) / "codex-last-message.txt"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    command = [
        settings.graphify_cli_command,
        "exec",
        "--skip-git-repo-check",
        "--full-auto",
        "-C",
        str(settings.graphify_out_dir),
        "-o",
        str(output_path),
        "-",
    ]
    _emit_graphify_progress(progress_callback, "status", f"Starting Graphify through {settings.graphify_cli_command}...")
    return _run_streaming_process(
        command=command,
        cwd=settings.graphify_out_dir,
        timeout_seconds=settings.graphify_timeout_seconds,
        progress_callback=progress_callback,
        stdin_text=_graphify_agent_prompt(settings),
    )


def _graphify_error_message(stderr: str, fallback: str) -> str:
    lines = [line.strip() for line in (stderr or "").splitlines() if line.strip()]
    for line in reversed(lines):
        if line.upper().startswith("ERROR:"):
            return line

    ignored = {"tokens used"}
    for line in reversed(lines):
        if line.lower() in ignored:
            continue
        if re.fullmatch(r"[\d,]+", line):
            continue
        if line.startswith("202") and " WARN " in line:
            continue
        return line
    return fallback


def _append_graphify_log(settings: Settings, page_count: int, source_count: int) -> None:
    log_path = settings.wiki_dir / "_log.md"
    if log_path.exists():
        try:
            current_log = log_path.read_text(encoding="utf-8")
        except OSError:
            current_log = "# Log operativo\n\n"
    else:
        current_log = "# Log operativo\n\n"

    timestamp = datetime.now().astimezone().isoformat(timespec="seconds")
    entry = (
        f"\n## {timestamp} - compilazione graphify\n\n"
        "- Fonti considerate:\n"
        "  - `raw/` tramite Graphify.\n"
        "- Output Graphify:\n"
        "  - `graphify-out/graph.json`\n"
        "  - `graphify-out/GRAPH_REPORT.md`\n"
        "  - `graphify-out/wiki/`\n"
        "- Pagine aggiornate:\n"
        "  - [[_index|Indice Wiki]]\n"
        f"  - {page_count} pagine Markdown generate da Graphify.\n"
        "- Pagine unite o divise:\n"
        "  - Gestione demandata al clustering del knowledge graph Graphify.\n"
        "- Dubbi aperti:\n"
        f"  - Verificare manualmente titoli e community generati da Graphify sui {source_count} file sorgente.\n"
    )
    log_path.write_text(current_log.rstrip() + entry + "\n", encoding="utf-8")


def _sync_graphify_wiki(settings: Settings, source_count: int) -> int:
    generated_wiki_dir = _graphify_out_dir(settings) / "wiki"
    generated_index = generated_wiki_dir / "index.md"
    if not generated_index.exists():
        raise FileNotFoundError(f"Graphify wiki not found: {generated_index}")

    settings.wiki_dir.mkdir(parents=True, exist_ok=True)
    for old_page in settings.wiki_dir.glob("*.md"):
        if old_page.name in {WIKI_CONFIG_FILE, "_log.md"}:
            continue
        old_page.unlink()

    page_count = 0
    for source_page in sorted(generated_wiki_dir.glob("*.md"), key=lambda item: item.name.lower()):
        target_name = "_index.md" if source_page.name.lower() == "index.md" else source_page.name
        shutil.copy2(source_page, settings.wiki_dir / target_name)
        page_count += 1

    _append_graphify_log(settings, page_count, source_count)
    return page_count


def _enrich_graphify_content(progress_callback: GraphifyProgressCallback | None = None) -> None:
    script_path = Path(__file__).resolve().parents[1] / "scripts" / "enrich_graphify_content.py"
    if not script_path.exists():
        return

    _emit_graphify_progress(progress_callback, "status", "Enriching Graphify nodes with source content excerpts...")
    completed = subprocess.run(
        [sys.executable, str(script_path)],
        cwd=script_path.parents[1],
        capture_output=True,
        text=True,
        timeout=120,
        check=False,
    )
    if completed.stdout.strip():
        _emit_graphify_progress(progress_callback, "stdout", completed.stdout.strip())
    if completed.stderr.strip():
        _emit_graphify_progress(progress_callback, "stderr", completed.stderr.strip())
    if completed.returncode != 0:
        _emit_graphify_progress(
            progress_callback,
            "status",
            "Graphify content enrichment failed; continuing with the generated graph/wiki.",
        )


def run_graphify_wiki_job(
    settings: Settings,
    mode: str = "compile",
    language: str = DEFAULT_WIKI_LANGUAGE,
    progress_callback: GraphifyProgressCallback | None = None,
) -> GraphifyRunResult:
    started = time.monotonic()
    language = normalize_wiki_language(language)
    ensure_wiki_layout(settings)
    ensure_wiki_language_config(settings.wiki_dir, language)

    sources = list_graphify_sources(settings)
    _emit_graphify_progress(progress_callback, "status", f"Found {len(sources)} source file(s) in raw/.")

    if not sources:
        _emit_graphify_progress(progress_callback, "status", "No source found in raw/.")
        return GraphifyRunResult(
            ok=False,
            mode=mode,
            returncode=2,
            elapsed_seconds=0,
            message="No source found in raw/. Upload at least one supported file.",
            stdout="",
            stderr="",
            sources=sources,
        )

    stdout_parts: list[str] = []
    stderr_parts: list[str] = []
    try:
        if settings.graphify_runner == "cli":
            cli_completed = _run_graphify_agent_cli(settings, progress_callback)
            stdout_parts.append(cli_completed.stdout or "")
            stderr_parts.append(cli_completed.stderr or "")
            if cli_completed.returncode != 0:
                elapsed = time.monotonic() - started
                error_message = _graphify_error_message(cli_completed.stderr, "Graphify CLI run failed.")
                return GraphifyRunResult(
                    ok=False,
                    mode=mode,
                    returncode=cli_completed.returncode,
                    elapsed_seconds=elapsed,
                    message=error_message or "Graphify CLI run failed.",
                    stdout="".join(stdout_parts),
                    stderr="".join(stderr_parts),
                    sources=sources,
                )
        elif settings.graphify_runner == "headless":
            _emit_graphify_progress(progress_callback, "status", "Starting Graphify extraction...")
            extract_completed = _run_graphify_command(settings, _build_graphify_extract_args(settings), progress_callback)
            stdout_parts.append(extract_completed.stdout or "")
            stderr_parts.append(extract_completed.stderr or "")
            if extract_completed.returncode != 0:
                elapsed = time.monotonic() - started
                error_message = _graphify_error_message(extract_completed.stderr, "Graphify extraction failed.")
                return GraphifyRunResult(
                    ok=False,
                    mode=mode,
                    returncode=extract_completed.returncode,
                    elapsed_seconds=elapsed,
                    message=error_message or "Graphify extraction failed.",
                    stdout="".join(stdout_parts),
                    stderr="".join(stderr_parts),
                    sources=sources,
                )

            graph_path = _graphify_out_dir(settings) / "graph.json"
            _emit_graphify_progress(progress_callback, "status", "Exporting Graphify wiki...")
            export_completed = _run_graphify_command(
                settings,
                ["export", "wiki", "--graph", str(graph_path)],
                progress_callback,
            )
            stdout_parts.append(export_completed.stdout or "")
            stderr_parts.append(export_completed.stderr or "")
            if export_completed.returncode != 0:
                elapsed = time.monotonic() - started
                error_message = _graphify_error_message(export_completed.stderr, "Graphify wiki export failed.")
                return GraphifyRunResult(
                    ok=False,
                    mode=mode,
                    returncode=export_completed.returncode,
                    elapsed_seconds=elapsed,
                    message=error_message or "Graphify wiki export failed.",
                    stdout="".join(stdout_parts),
                    stderr="".join(stderr_parts),
                    sources=sources,
                )
        else:
            elapsed = time.monotonic() - started
            return GraphifyRunResult(
                ok=False,
                mode=mode,
                returncode=2,
                elapsed_seconds=elapsed,
                message=f"Unsupported GRAPHIFY_RUNNER={settings.graphify_runner}. Use cli or headless.",
                stdout="".join(stdout_parts),
                stderr="".join(stderr_parts),
                sources=sources,
            )

        _enrich_graphify_content(progress_callback)
        _emit_graphify_progress(progress_callback, "status", "Syncing Graphify wiki into knowledge/wiki/...")
        page_count = _sync_graphify_wiki(settings, len(sources))
    except FileNotFoundError:
        elapsed = time.monotonic() - started
        _emit_graphify_progress(
            progress_callback,
            "stderr",
            "Graphify or the configured CLI command is not available.",
        )
        return GraphifyRunResult(
            ok=False,
            mode=mode,
            returncode=127,
            elapsed_seconds=elapsed,
            message="Graphify or the configured CLI command is not available. Install dependencies and verify GRAPHIFY_CLI_COMMAND.",
            stdout="".join(stdout_parts),
            stderr="".join(stderr_parts),
            sources=sources,
        )
    except subprocess.TimeoutExpired as exc:
        elapsed = time.monotonic() - started
        return GraphifyRunResult(
            ok=False,
            mode=mode,
            returncode=124,
            elapsed_seconds=elapsed,
            message=f"Graphify exceeded the {settings.graphify_timeout_seconds}-second timeout.",
            stdout=exc.stdout or "",
            stderr=exc.stderr or "",
            sources=sources,
        )

    elapsed = time.monotonic() - started
    stdout = "".join(stdout_parts)
    stderr = "".join(stderr_parts)
    _emit_graphify_progress(progress_callback, "status", "Graphify completed. Moving compiled sources to processed/...")
    moved_count, move_errors = move_raw_sources_to_processed(settings.raw_dir)
    if move_errors:
        message = (
            "Graphify updated the wiki, but the move to processed/ is incomplete. "
            f"Files moved: {moved_count}, errors: {len(move_errors)}."
        )
        details = "\n".join(move_errors)
        stderr = (stderr + "\n\n" if stderr else "") + f"Errors moving files to processed/:\n{details}"
        _emit_graphify_progress(progress_callback, "status", message)
        return GraphifyRunResult(
            ok=False,
            mode=mode,
            returncode=3,
            elapsed_seconds=elapsed,
            message=message,
            stdout=stdout,
            stderr=stderr,
            sources=sources,
        )

    message = f"Graphify updated {page_count} wiki page(s) and moved {moved_count} file(s) to processed/."
    _emit_graphify_progress(progress_callback, "status", message)
    return GraphifyRunResult(
        ok=True,
        mode=mode,
        returncode=0,
        elapsed_seconds=elapsed,
        message=message,
        stdout=stdout,
        stderr=stderr,
        sources=sources,
    )

