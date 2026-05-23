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
    graphify_runner: str
    graphify_cli_command: str
    graphify_timeout_seconds: int
    graphify_backend: str | None
    graphify_model: str | None
    graphify_out_dir: Path
    graphify_max_workers: int | None
    graphify_token_budget: int | None
    graphify_max_concurrency: int | None


def _to_abs(path_value: str) -> Path:
    return Path(path_value).expanduser().resolve()


def get_settings() -> Settings:
    source_dir = _to_abs(os.getenv("WIKI_SOURCE_DIR", "./knowledge"))
    raw_dir = _to_abs(os.getenv("WIKI_RAW_DIR", str(source_dir / "raw")))
    wiki_dir = _to_abs(os.getenv("WIKI_OUTPUT_DIR", str(source_dir / "wiki")))
    app_host = os.getenv("APP_HOST", "127.0.0.1")
    app_port = int(os.getenv("APP_PORT", "8000"))
    graphify_runner = os.getenv("GRAPHIFY_RUNNER", "cli").strip().lower() or "cli"
    default_graphify_cli_command = "codex.cmd" if sys.platform.startswith("win") else "codex"
    graphify_cli_command = os.getenv("GRAPHIFY_CLI_COMMAND", default_graphify_cli_command)
    graphify_timeout_seconds = int(os.getenv("GRAPHIFY_TIMEOUT_SECONDS", "1800"))
    graphify_backend = os.getenv("GRAPHIFY_BACKEND") or None
    graphify_model = os.getenv("GRAPHIFY_MODEL") or None
    graphify_out_dir = _to_abs(os.getenv("GRAPHIFY_OUTPUT_DIR", str(source_dir)))
    graphify_max_workers = _optional_int(os.getenv("GRAPHIFY_MAX_WORKERS"))
    graphify_token_budget = _optional_int(os.getenv("GRAPHIFY_TOKEN_BUDGET"))
    graphify_max_concurrency = _optional_int(os.getenv("GRAPHIFY_MAX_CONCURRENCY"))

    return Settings(
        source_dir=source_dir,
        raw_dir=raw_dir,
        wiki_dir=wiki_dir,
        app_host=app_host,
        app_port=app_port,
        graphify_runner=graphify_runner,
        graphify_cli_command=graphify_cli_command,
        graphify_timeout_seconds=graphify_timeout_seconds,
        graphify_backend=graphify_backend,
        graphify_model=graphify_model,
        graphify_out_dir=graphify_out_dir,
        graphify_max_workers=graphify_max_workers,
        graphify_token_budget=graphify_token_budget,
        graphify_max_concurrency=graphify_max_concurrency,
    )


def _optional_int(value: str | None) -> int | None:
    if value is None or not value.strip():
        return None
    return int(value)
