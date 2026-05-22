import os
import sys
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Settings:
    source_dir: Path
    raw_dir: Path
    wiki_dir: Path
    app_host: str
    app_port: int
    codex_command: str
    codex_shell: str
    codex_model: str | None
    codex_timeout_seconds: int
    codex_source_char_limit: int
    codex_prompt_template_path: Path
    codex_task_prompts_path: Path
    codex_source_extract_template_path: Path
    codex_source_list_item_template_path: Path
    codex_source_list_empty_template_path: Path
    codex_togaf_reference_path: Path


def _to_abs(path_value: str) -> Path:
    return Path(path_value).expanduser().resolve()


def get_settings() -> Settings:
    source_dir = _to_abs(os.getenv("WIKI_SOURCE_DIR", "./knowledge"))
    raw_dir = _to_abs(os.getenv("WIKI_RAW_DIR", str(source_dir / "raw")))
    wiki_dir = _to_abs(os.getenv("WIKI_OUTPUT_DIR", str(source_dir / "wiki")))
    app_host = os.getenv("APP_HOST", "127.0.0.1")
    app_port = int(os.getenv("APP_PORT", "8000"))
    default_codex_command = "codex.cmd" if sys.platform.startswith("win") else "codex"
    codex_command = os.getenv("CODEX_COMMAND", default_codex_command)
    codex_shell = os.getenv("CODEX_SHELL", "powershell")
    codex_model = os.getenv("CODEX_MODEL") or None
    codex_timeout_seconds = int(os.getenv("CODEX_TIMEOUT_SECONDS", "900"))
    codex_source_char_limit = int(os.getenv("CODEX_SOURCE_CHAR_LIMIT", "0"))
    codex_prompt_template_path = _to_abs(os.getenv("CODEX_PROMPT_TEMPLATE", "./config/codex-wiki-prompt.md"))
    codex_task_prompts_path = _to_abs(os.getenv("CODEX_TASK_PROMPTS", "./config/codex-wiki-tasks.json"))
    codex_source_extract_template_path = _to_abs(
        os.getenv("CODEX_SOURCE_EXTRACT_TEMPLATE", "./config/codex-source-extract-template.md")
    )
    codex_source_list_item_template_path = _to_abs(
        os.getenv("CODEX_SOURCE_LIST_ITEM_TEMPLATE", "./config/codex-source-list-item.txt")
    )
    codex_source_list_empty_template_path = _to_abs(
        os.getenv("CODEX_SOURCE_LIST_EMPTY_TEMPLATE", "./config/codex-source-list-empty.txt")
    )
    codex_togaf_reference_path = _to_abs(
        os.getenv("CODEX_TOGAF_REFERENCE", "./config/togaf-template-deliverables.md")
    )

    return Settings(
        source_dir=source_dir,
        raw_dir=raw_dir,
        wiki_dir=wiki_dir,
        app_host=app_host,
        app_port=app_port,
        codex_command=codex_command,
        codex_shell=codex_shell,
        codex_model=codex_model,
        codex_timeout_seconds=codex_timeout_seconds,
        codex_source_char_limit=codex_source_char_limit,
        codex_prompt_template_path=codex_prompt_template_path,
        codex_task_prompts_path=codex_task_prompts_path,
        codex_source_extract_template_path=codex_source_extract_template_path,
        codex_source_list_item_template_path=codex_source_list_item_template_path,
        codex_source_list_empty_template_path=codex_source_list_empty_template_path,
        codex_togaf_reference_path=codex_togaf_reference_path,
    )
