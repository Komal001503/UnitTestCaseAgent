"""Configuration helpers for the local web UI."""

from __future__ import annotations

from dataclasses import dataclass
import os
from pathlib import Path

from dotenv import load_dotenv


@dataclass(frozen=True)
class WebUIConfig:
    repo_root: Path
    scripts_dir: Path
    tests_dir: Path
    reports_dir: Path
    azure_script: Path
    excel_script: Path
    export_script: Path
    fcs_script: Path
    template_dir: Path
    static_dir: Path
    host: str
    port: int
    max_upload_bytes: int


def find_repo_root(start: Path) -> Path:
    """Walk upward until the repository root is found."""
    current = start.resolve()
    for candidate in [current, *current.parents]:
        if (candidate / "scripts" / "fcs_uploader.py").is_file():
            return candidate
    raise RuntimeError("Could not locate repository root (missing scripts/fcs_uploader.py)")


def load_webui_config() -> WebUIConfig:
    repo_root = find_repo_root(Path(__file__).resolve())
    load_dotenv(repo_root / ".env")

    scripts_dir = repo_root / "scripts"
    template_dir = repo_root / "webui" / "templates"
    static_dir = repo_root / "webui" / "static"

    host = os.environ.get("WEBUI_HOST", "127.0.0.1")
    try:
        port = int(os.environ.get("WEBUI_PORT", "5000"))
    except ValueError:
        port = 5000

    return WebUIConfig(
        repo_root=repo_root,
        scripts_dir=scripts_dir,
        tests_dir=repo_root / "tests",
        reports_dir=repo_root / "test_reports",
        azure_script=scripts_dir / "azure_devops_to_md.py",
        excel_script=scripts_dir / "excel_to_md.py",
        export_script=scripts_dir / "export_tests_to_text.py",
        fcs_script=scripts_dir / "fcs_uploader.py",
        template_dir=template_dir,
        static_dir=static_dir,
        host=host,
        port=port,
        max_upload_bytes=25 * 1024 * 1024,
    )
