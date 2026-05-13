from __future__ import annotations

import html
import json
import re
import shutil
import subprocess
import time
import unicodedata
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from datetime import datetime, timezone
from hashlib import sha1
from os import cpu_count
from pathlib import Path

from .config import Settings
from .ingest import is_supported_file, normalize_text, read_text_from_file

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


@dataclass(frozen=True)
class _WikiDocument:
    page: WikiPage
    markdown: str


SOURCE_CACHE_VERSION = 1
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
    "it": "Italiano",
    "en": "English",
    "es": "Espanol",
    "fr": "Francais",
    "de": "Deutsch",
    "pt": "Portugues",
    "nl": "Nederlands",
    "pl": "Polski",
    "ro": "Romana",
    "ar": "Arabo",
    "zh": "Cinese semplificato",
    "ja": "Giapponese",
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
            "Questa pagina viene aggiornata da Codex durante la compilazione della knowledge base.\n",
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
        "adm_phase": "Non classificata",
        "domain": "Non classificato",
        "artifact_type": "Artefatto",
        "template_reference": "Non indicato",
        "status": "Da verificare",
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
        "requirement_type": "Requisito",
        "epic": "Non classificata",
        "priority": "Non indicata",
        "status": "Da verificare",
        "phase": "Non indicata",
        "wiki_source": "Non indicata",
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


def _source_text_dir(settings: Settings) -> Path:
    return settings.source_dir / ".codex_sources"


def _remove_source_cache_entry(child: Path) -> None:
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


def _clear_stale_prepared_source_files(source_text_dir: Path, current_files: set[Path]) -> None:
    if not source_text_dir.exists():
        return

    reserved_names = {"codex-prompt.txt", "codex-last-message.txt", "manifest.json"}
    current_resolved = {path.resolve() for path in current_files}
    for child in source_text_dir.iterdir():
        if child.name in reserved_names:
            continue
        if child.is_file() and child.resolve() in current_resolved:
            continue
        if child.is_file() and child.suffix.lower() != ".txt":
            continue
        _remove_source_cache_entry(child)


def _load_source_manifest(source_text_dir: Path) -> dict:
    manifest_path = source_text_dir / "manifest.json"
    if not manifest_path.exists():
        return {}

    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}

    if manifest.get("cache_version") != SOURCE_CACHE_VERSION:
        return {}

    return {
        source.get("rel_path"): source
        for source in manifest.get("sources", [])
        if isinstance(source, dict) and source.get("rel_path")
    }


def _safe_source_extract_path(source_text_dir: Path, rel_path: str, source_path: Path) -> Path:
    digest = sha1(rel_path.encode("utf-8")).hexdigest()[:10]
    slug = slugify_wiki_title(source_path.stem)[:80]
    return source_text_dir / f"source-{slug}-{digest}.txt"


def _read_config_text(path: Path, label: str) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except OSError as exc:
        raise FileNotFoundError(f"{label} non trovato o non leggibile: {path}") from exc


def _format_config_template(template: str, values: dict, template_path: Path) -> str:
    try:
        return template.format(**values)
    except KeyError as exc:
        raise ValueError(f"Placeholder non supportato nel template {template_path}: {exc}") from exc


def _source_cache_matches(cache_entry: dict, path: Path, extracted_path: Path, char_limit: int) -> bool:
    if not extracted_path.exists() or not extracted_path.is_file():
        return False

    try:
        stat = path.stat()
    except OSError:
        return False

    return (
        cache_entry.get("cache_version") == SOURCE_CACHE_VERSION
        and cache_entry.get("source_size") == stat.st_size
        and cache_entry.get("source_mtime_ns") == stat.st_mtime_ns
        and cache_entry.get("char_limit") == char_limit
        and Path(str(cache_entry.get("extracted_path", ""))).name == extracted_path.name
    )


def _prepare_single_source(
    path: Path,
    rel_path: str,
    source_text_dir: Path,
    char_limit: int,
    source_extract_template: str,
    source_extract_template_path: Path,
    cache_entry: dict | None,
) -> tuple[PreparedSource, dict, Path]:
    extracted_path = _safe_source_extract_path(source_text_dir, rel_path, path)
    if cache_entry and _source_cache_matches(cache_entry, path, extracted_path, char_limit):
        chars = int(cache_entry.get("chars") or 0)
        truncated = bool(cache_entry.get("truncated"))
        return (
            PreparedSource(
                rel_path=rel_path,
                extracted_path=extracted_path.name,
                chars=chars,
                truncated=truncated,
            ),
            cache_entry,
            extracted_path,
        )

    try:
        text = normalize_text(read_text_from_file(path))
    except Exception as exc:
        text = f"Extraction failed for {rel_path}: {exc}"

    truncated = char_limit > 0 and len(text) > char_limit
    if truncated:
        text = text[:char_limit] + "\n\n[TRUNCATED]"

    extracted_content = _format_config_template(
        source_extract_template,
        {
            "rel_path": rel_path,
            "extracted_at": datetime.now(timezone.utc).isoformat(),
            "truncated": str(truncated).lower(),
            "text": text,
        },
        source_extract_template_path,
    )
    extracted_path.write_text(extracted_content.rstrip() + "\n", encoding="utf-8")

    stat = path.stat()
    cache_data = {
        "cache_version": SOURCE_CACHE_VERSION,
        "rel_path": rel_path,
        "extracted_path": extracted_path.name,
        "chars": len(text),
        "truncated": truncated,
        "source_size": stat.st_size,
        "source_mtime_ns": stat.st_mtime_ns,
        "source_ext": path.suffix.lower(),
        "char_limit": char_limit,
    }
    return (
        PreparedSource(
            rel_path=rel_path,
            extracted_path=extracted_path.name,
            chars=len(text),
            truncated=truncated,
        ),
        cache_data,
        extracted_path,
    )


def _source_worker_count(source_count: int) -> int:
    if source_count <= 1:
        return 1

    return min(source_count, max(2, min(cpu_count() or 2, 6)))


def _prepare_source_job(args: tuple[Path, str, Path, int, str, Path, dict | None]) -> tuple[PreparedSource, dict, Path]:
    return _prepare_single_source(*args)


def _prepared_source_with_relative_path(source: PreparedSource, source_root: Path, extracted_path: Path) -> PreparedSource:
    return PreparedSource(
        rel_path=source.rel_path,
        extracted_path=str(extracted_path.resolve().relative_to(source_root)).replace("\\", "/"),
        chars=source.chars,
        truncated=source.truncated,
    )


def prepare_sources_for_codex(settings: Settings) -> list[PreparedSource]:
    ensure_wiki_layout(settings)
    source_text_dir = _source_text_dir(settings).resolve()
    source_root = settings.source_dir.resolve()
    if source_root not in source_text_dir.parents:
        raise ValueError("Prepared source directory must stay inside the wiki source directory")

    source_text_dir.mkdir(parents=True, exist_ok=True)
    cached_sources = _load_source_manifest(source_text_dir)
    source_extract_template = _read_config_text(
        settings.codex_source_extract_template_path,
        "Template estrazione fonti Codex",
    )

    source_paths = [
        path
        for path in sorted(settings.raw_dir.rglob("*"), key=lambda item: str(item).lower())
        if path.is_file() and is_supported_file(path)
    ]
    jobs: list[tuple[Path, str, Path, int, str, Path, dict | None]] = []
    for path in source_paths:
        rel_path = str(path.resolve().relative_to(source_root)).replace("\\", "/")
        jobs.append(
            (
                path,
                rel_path,
                source_text_dir,
                settings.codex_source_char_limit,
                source_extract_template,
                settings.codex_source_extract_template_path,
                cached_sources.get(rel_path),
            )
        )

    prepared: list[PreparedSource] = []
    manifest_sources: list[dict] = []
    current_files: set[Path] = set()
    worker_count = _source_worker_count(len(jobs))
    if worker_count == 1:
        results = [_prepare_source_job(job) for job in jobs]
    else:
        with ThreadPoolExecutor(max_workers=worker_count) as executor:
            results = list(executor.map(_prepare_source_job, jobs))

    for source, cache_data, extracted_path in results:
        current_files.add(extracted_path)
        relative_source = _prepared_source_with_relative_path(source, source_root, extracted_path)
        prepared.append(relative_source)
        manifest_entry = dict(cache_data)
        manifest_entry["extracted_path"] = relative_source.extracted_path
        manifest_sources.append(manifest_entry)

    _clear_stale_prepared_source_files(source_text_dir, current_files)

    manifest = {
        "cache_version": SOURCE_CACHE_VERSION,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source_count": len(prepared),
        "worker_count": worker_count,
        "sources": manifest_sources,
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


def _load_codex_task_prompt(settings: Settings, mode: str) -> str:
    raw_tasks = _read_config_text(settings.codex_task_prompts_path, "Prompt task Codex")
    try:
        tasks = json.loads(raw_tasks)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Prompt task Codex non valido: {settings.codex_task_prompts_path}") from exc

    task = tasks.get(mode)
    if not isinstance(task, str) or not task.strip():
        raise ValueError(f"Task prompt mancante per mode={mode}: {settings.codex_task_prompts_path}")

    return task.strip()


def _build_source_list(settings: Settings, sources: list[PreparedSource]) -> str:
    if not sources:
        return _read_config_text(
            settings.codex_source_list_empty_template_path,
            "Template lista fonti vuota Codex",
        ).strip()

    item_template = _read_config_text(
        settings.codex_source_list_item_template_path,
        "Template voce lista fonti Codex",
    )
    items = [
        _format_config_template(
            item_template,
            {
                "extracted_path": source.extracted_path,
                "rel_path": source.rel_path,
                "chars": source.chars,
                "truncated": source.truncated,
            },
            settings.codex_source_list_item_template_path,
        ).strip()
        for source in sources
    ]
    return "\n".join(items)


def _load_togaf_reference(settings: Settings) -> str:
    try:
        return _read_config_text(settings.codex_togaf_reference_path, "Reference artefatti TOGAF").strip()
    except FileNotFoundError:
        return "Reference artefatti TOGAF non configurata."


def build_codex_prompt(
    settings: Settings,
    mode: str,
    sources: list[PreparedSource],
    language: str = DEFAULT_WIKI_LANGUAGE,
) -> str:
    template = _read_config_text(settings.codex_prompt_template_path, "Prompt template Codex")
    language_label = wiki_language_label(language)
    return _format_config_template(
        template,
        {
            "mode": mode,
            "task": _load_codex_task_prompt(settings, mode),
            "source_list": _build_source_list(settings, sources),
            "togaf_reference": _load_togaf_reference(settings),
            "language": language_label,
            "language_instruction": (
                f"Scrivi e mantieni tutte le pagine wiki, _index.md, _log.md e il riepilogo finale "
                f"in lingua: {language_label}."
            ),
        },
        settings.codex_prompt_template_path,
    )


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


def run_codex_wiki_job(
    settings: Settings,
    mode: str = "compile",
    language: str = DEFAULT_WIKI_LANGUAGE,
) -> CodexRunResult:
    started = time.monotonic()
    language = normalize_wiki_language(language)
    if mode == "togaf":
        ensure_wiki_layout(settings)
        ensure_togaf_layout(settings)
        sources = []
    else:
        if mode == "compile":
            ensure_functional_requirements_layout(settings)
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

    language = ensure_wiki_language_config(settings.wiki_dir, language)
    prompt = build_codex_prompt(settings, mode, sources, language)
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
                "Codex ha aggiornato la wiki e i requisiti funzionali, ma lo spostamento in processed/ e' incompleto. "
                f"File spostati: {moved_count}, errori: {len(move_errors)}."
            )
            details = "\n".join(move_errors)
            stderr = (stderr + "\n\n" if stderr else "") + f"Errori spostamento in processed/:\n{details}"
        else:
            message = (
                "Codex ha aggiornato la wiki, la vista requisiti funzionali "
                f"e spostato {moved_count} file in processed/."
            )
    elif ok and mode == "togaf":
        message = "Codex ha aggiornato la wiki TOGAF partendo dalla LLM Wiki."
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
