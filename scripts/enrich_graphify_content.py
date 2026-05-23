from __future__ import annotations

import json
import re
import textwrap
from pathlib import Path


ROOT = Path("knowledge")
OUT = ROOT / "graphify-out"
WIKI_DIRS = [OUT / "wiki", ROOT / "wiki"]
GRAPH_HTML = OUT / "graph.html"
GRAPH_JSON = OUT / "graph.json"

STOPWORDS = {
    "con",
    "del",
    "della",
    "delle",
    "degli",
    "dei",
    "alla",
    "alle",
    "agli",
    "nel",
    "nella",
    "nelle",
    "per",
    "che",
    "una",
    "uno",
    "the",
    "and",
    "for",
    "from",
    "page",
}


def normalize(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[_\-–—/|]+", " ", text)
    text = re.sub(r"[^a-z0-9àèéìòùç ]+", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def tokens(text: str) -> set[str]:
    return {t for t in normalize(text).split() if len(t) > 2 and t not in STOPWORDS}


def md_slug(title: str) -> str:
    return re.sub(r"[^A-Za-z0-9_]+", "_", title).strip("_")


def clean_excerpt(text: str, limit: int = 850) -> str:
    text = re.sub(r"<!--.*?-->", "", text, flags=re.S)
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r"[ \t]+", " ", text)
    text = text.strip()
    if len(text) <= limit:
        return text
    cut = text[:limit].rsplit(" ", 1)[0].rstrip()
    return cut + "..."


def split_sections(text: str) -> list[str]:
    lines = text.splitlines()
    sections: list[list[str]] = []
    current: list[str] = []
    header_re = re.compile(r"^(#{1,3}\s+|[A-Z]{2,}(?:-[A-Z0-9]+)+\s+[—-]|[A-Z]{2,}(?:-[A-Z0-9]+)+$)")
    for line in lines:
        if header_re.match(line.strip()) and current:
            sections.append(current)
            current = [line]
        else:
            current.append(line)
    if current:
        sections.append(current)
    return ["\n".join(section).strip() for section in sections if "\n".join(section).strip()]


def source_path(source_file: str | None) -> Path | None:
    if not source_file:
        return None
    candidate = ROOT / source_file
    if candidate.exists():
        return candidate
    candidate = OUT / source_file
    if candidate.exists():
        return candidate
    return None


def best_excerpt(label: str, source_file: str | None, file_type: str | None) -> str:
    path = source_path(source_file)
    if not path:
        return ""

    text = path.read_text(encoding="utf-8", errors="replace")
    text = re.sub(r"<!--.*?-->", "", text, flags=re.S).strip()
    if file_type == "document":
        return clean_excerpt(text, 900)

    label_tokens = tokens(label)
    if not label_tokens:
        return clean_excerpt(text, 700)

    best_score = -1
    best_section = ""
    for section in split_sections(text):
        section_tokens = tokens(section[:1500])
        overlap = len(label_tokens & section_tokens)
        phrase_bonus = 3 if normalize(label) in normalize(section[:1200]) else 0
        score = overlap + phrase_bonus
        if score > best_score:
            best_score = score
            best_section = section

    return clean_excerpt(best_section or text, 850)


def load_nodes() -> list[dict]:
    data = json.loads(GRAPH_JSON.read_text(encoding="utf-8"))
    return data.get("nodes", [])


def wiki_file_map() -> dict[str, Path]:
    mapping: dict[str, Path] = {}
    graphify_wiki = OUT / "wiki"
    if not graphify_wiki.exists():
        return mapping
    for path in graphify_wiki.glob("*.md"):
        if path.name == "index.md":
            continue
        mapping[normalize(path.stem.replace("_", " "))] = path
    return mapping


def enrich_wiki_page(path: Path, excerpt: str, source: str | None) -> None:
    if not excerpt:
        return
    original = path.read_text(encoding="utf-8", errors="replace")
    if "## Contenuto estratto" in original:
        updated = re.sub(
            r"\n## Contenuto estratto\n.*?(?=\n## Connections by Relation|\n---\n)",
            "",
            original,
            flags=re.S,
        )
    else:
        updated = original

    block = "\n## Contenuto estratto\n\n"
    block += textwrap.fill(excerpt, width=110)
    if source:
        block += f"\n\n**Fonte:** `{source}`"
    block += "\n"

    marker = "\n## Connections by Relation"
    if marker in updated:
        updated = updated.replace(marker, block + marker, 1)
    else:
        updated = updated.rstrip() + "\n" + block
    path.write_text(updated, encoding="utf-8")


def sync_page_to_main_wiki(graphify_page: Path) -> None:
    main = ROOT / "wiki" / graphify_page.name
    if main.exists():
        main.write_text(graphify_page.read_text(encoding="utf-8"), encoding="utf-8")


def enrich_wiki(nodes: list[dict]) -> dict[str, dict[str, str]]:
    pages = wiki_file_map()
    enriched: dict[str, dict[str, str]] = {}
    for node in nodes:
        label = node.get("label", "")
        key = normalize(label)
        page = pages.get(key)
        excerpt = best_excerpt(label, node.get("source_file"), node.get("file_type"))
        enriched[node["id"]] = {
            "content_excerpt": excerpt,
            "wiki_path": f"wiki/{page.name}" if page else "",
        }
        if page:
            enrich_wiki_page(page, excerpt, node.get("source_file"))
            sync_page_to_main_wiki(page)
    return enriched


def enrich_html(enriched: dict[str, dict[str, str]]) -> None:
    if not GRAPH_HTML.exists():
        return
    html = GRAPH_HTML.read_text(encoding="utf-8", errors="replace")
    match = re.search(r"const RAW_NODES = (\[.*?\]);\nconst RAW_EDGES =", html, flags=re.S)
    if not match:
        raise RuntimeError("Could not locate RAW_NODES in graph.html")
    raw_nodes = json.loads(match.group(1))
    for node in raw_nodes:
        extra = enriched.get(node.get("id"), {})
        node["content_excerpt"] = extra.get("content_excerpt", "")
        node["wiki_path"] = extra.get("wiki_path", "")
        if node["content_excerpt"]:
            node["title"] = f"{node.get('label', '')}\n\n{node['content_excerpt'][:450]}"
    html = html[: match.start(1)] + json.dumps(raw_nodes, ensure_ascii=False) + html[match.end(1) :]
    html = html.replace(
        "_source_file: n.source_file, _file_type: n.file_type, _degree: n.degree,",
        "_source_file: n.source_file, _file_type: n.file_type, _degree: n.degree,\n"
        "  _content_excerpt: n.content_excerpt || '', _wiki_path: n.wiki_path || '',",
    )
    html = html.replace(
        "<div class=\"field\">Degree: ${n._degree}</div>",
        "<div class=\"field\">Degree: ${n._degree}</div>\n"
        "    ${n._wiki_path ? `<div class=\"field\">Wiki: <a style=\"color:#7db7ff\" href=\"${esc(n._wiki_path)}\" target=\"_blank\">${esc(n._wiki_path)}</a></div>` : ''}\n"
        "    ${n._content_excerpt ? `<div class=\"field\" style=\"margin-top:10px;color:#aaa;font-size:11px\">Content</div><div class=\"field\" style=\"white-space:pre-wrap;color:#ddd;background:#202020;border-radius:6px;padding:8px;max-height:230px;overflow:auto\">${esc(n._content_excerpt)}</div>` : ''}",
    )
    GRAPH_HTML.write_text(html, encoding="utf-8")


def main() -> None:
    nodes = load_nodes()
    enriched = enrich_wiki(nodes)
    enrich_html(enriched)
    print(f"Enriched {sum(1 for v in enriched.values() if v['content_excerpt'])} graph nodes with content excerpts.")


if __name__ == "__main__":
    main()
