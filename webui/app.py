"""Flask application for the local Unit Test Case console."""

from __future__ import annotations

from datetime import datetime, timezone
import io
import os
from pathlib import Path
import sys
import time
import urllib.parse
import zipfile

from flask import Flask, jsonify, render_template, request, send_file
from werkzeug.utils import secure_filename

from .config import WebUIConfig, load_webui_config
from .runner import LOG_BUFFER, run_script


def _utc_date() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def create_app(config: WebUIConfig | None = None) -> Flask:
    cfg = config or load_webui_config()
    app = Flask(
        __name__,
        template_folder=str(cfg.template_dir),
        static_folder=str(cfg.static_dir),
    )
    app.config["WEBUI_CFG"] = cfg
    app.config["MAX_CONTENT_LENGTH"] = cfg.max_upload_bytes

    state: dict[str, object] = {}

    def _repo_cfg() -> WebUIConfig:
        return app.config["WEBUI_CFG"]

    def _repo_rel(path: Path) -> str:
        return str(path.relative_to(_repo_cfg().repo_root)).replace("\\", "/")

    def _safe_repo_path(rel_path: str) -> Path:
        cfg_local = _repo_cfg()
        resolved = (cfg_local.repo_root / rel_path).resolve()
        if not resolved.is_relative_to(cfg_local.repo_root):
            raise ValueError("Path must stay inside repository root")
        return resolved

    def _safe_report_path(rel_path: str) -> Path:
        cfg_local = _repo_cfg()
        resolved = _safe_repo_path(rel_path)
        if not resolved.is_relative_to(cfg_local.reports_dir.resolve()):
            raise ValueError("Path must be inside test_reports")
        return resolved

    def _json_error(message: str, status: int = 500):
        return jsonify({"error": message, "last_log_lines": LOG_BUFFER.last_lines(50)}), status

    def _markdown_candidates() -> list[Path]:
        cfg_local = _repo_cfg()
        files = []
        for md_file in sorted(cfg_local.repo_root.glob("*.md")):
            if md_file.name.lower().startswith("readme"):
                continue
            files.append(md_file)
        return files

    def _report_files() -> list[Path]:
        reports_dir = _repo_cfg().reports_dir
        reports_dir.mkdir(parents=True, exist_ok=True)
        return sorted([p for p in reports_dir.iterdir() if p.is_file()], key=lambda p: p.name.lower())

    def _default_tableid(path: Path) -> str:
        reports_dir = _repo_cfg().reports_dir.resolve()
        if path.resolve().is_relative_to(reports_dir):
            return "OUTPUT"
        if path.suffix.lower() in {".md", ".xlsx", ".xls"}:
            return "INPUT"
        return "OUTPUT"

    def _run_fcs_check() -> tuple[int, list[str]]:
        cfg_local = _repo_cfg()
        return run_script(
            [sys.executable, str(cfg_local.fcs_script), "check-connectivity"],
            cwd=cfg_local.repo_root,
            env=os.environ.copy(),
            label="fcs-check",
        )

    def _upload_one(path: Path, tableid: str, project_name: str, date_stamp: str) -> tuple[int, list[str]]:
        cfg_local = _repo_cfg()
        argv = [
            sys.executable,
            str(cfg_local.fcs_script),
            "upload",
            str(path),
            tableid,
            "--project-name",
            project_name,
            "--date-stamp",
            date_stamp,
        ]
        return run_script(argv, cwd=cfg_local.repo_root, env=os.environ.copy(), label="fcs-upload")

    @app.get("/")
    def index():
        return render_template("index.html")

    @app.get("/api/markdown-files")
    def markdown_files():
        return jsonify({"files": [{"name": p.name, "path": _repo_rel(p)} for p in _markdown_candidates()]})

    @app.get("/api/reports")
    def reports():
        payload = []
        for report in _report_files():
            stat = report.stat()
            payload.append(
                {
                    "name": report.name,
                    "path": _repo_rel(report),
                    "size": stat.st_size,
                    "mtime": datetime.fromtimestamp(stat.st_mtime, timezone.utc).isoformat(),
                    "default_tableid": "OUTPUT",
                }
            )
        return jsonify({"files": payload})

    @app.post("/api/sync-devops")
    def sync_devops():
        cfg_local = _repo_cfg()
        body = request.get_json(silent=True) or {}
        try:
            argv = [sys.executable, str(cfg_local.azure_script)]
            mapping = {
                "output": "--output",
                "org": "--org",
                "project": "--project",
                "team": "--team",
                "work_item_type": "--work-item-type",
                "states": "--states",
                "from_date": "--from-date",
                "to_date": "--to-date",
            }
            for key, flag in mapping.items():
                value = body.get(key)
                if value:
                    argv.extend([flag, str(value)])
            if body.get("verbose"):
                argv.append("--verbose")
            if body.get("dry_run"):
                argv.append("--dry-run")

            code, _ = run_script(argv, cwd=cfg_local.repo_root, env=os.environ.copy(), label="sync-devops")
            if code != 0:
                return _json_error("Azure DevOps sync failed", 500)
            return jsonify({"ok": True, "markdown_files": [{"name": p.name, "path": _repo_rel(p)} for p in _markdown_candidates()]})
        except Exception as exc:
            LOG_BUFFER.append("sync-devops", repr(exc))
            return _json_error("Azure DevOps sync failed", 500)

    @app.post("/api/upload-excel")
    def upload_excel():
        cfg_local = _repo_cfg()
        uploaded = request.files.get("file")
        if uploaded is None or not uploaded.filename:
            return jsonify({"error": "No file uploaded"}), 400

        filename = secure_filename(uploaded.filename)
        if Path(filename).suffix.lower() not in {".xlsx", ".xls"}:
            return jsonify({"error": "Only .xlsx or .xls files are allowed"}), 400

        saved_path = cfg_local.repo_root / filename
        uploaded.save(saved_path)

        code, _ = run_script(
            [sys.executable, str(cfg_local.excel_script), str(saved_path)],
            cwd=cfg_local.repo_root,
            env=os.environ.copy(),
            label="upload-excel",
        )
        if code != 0:
            return _json_error("Excel conversion failed", 500)

        return jsonify(
            {
                "ok": True,
                "uploaded": _repo_rel(saved_path),
                "markdown": _repo_rel(saved_path.with_suffix(".md")),
                "markdown_files": [{"name": p.name, "path": _repo_rel(p)} for p in _markdown_candidates()],
            }
        )

    @app.post("/api/generate")
    def generate():
        cfg_local = _repo_cfg()
        body = request.get_json(silent=True) or {}
        rel_path = body.get("path")
        if not rel_path:
            return jsonify({"error": "Missing path"}), 400
        try:
            source_path = _safe_repo_path(rel_path)
        except ValueError:
            return jsonify({"error": "Invalid path"}), 400
        if source_path.suffix.lower() != ".md" or not source_path.exists():
            return jsonify({"error": "Source markdown not found"}), 404

        tests_before = sorted([_repo_rel(p) for p in cfg_local.tests_dir.glob("test_*.py") if p.is_file()])
        since_ts = time.time()
        prompt = f"Read `{source_path.name}` and generate unit test cases for the user stories."
        encoded = urllib.parse.quote(prompt)
        vscode_url = f"vscode://GitHub.copilot-chat/chat?prompt={encoded}"
        state["last_generate"] = {"source": _repo_rel(source_path), "since": since_ts, "tests_dir_before": tests_before}
        return jsonify(
            {
                "prompt": prompt,
                "vscode_chat_url": vscode_url,
                "tests_dir_before": tests_before,
                "since": since_ts,
            }
        )

    @app.get("/api/tests/diff")
    def tests_diff():
        cfg_local = _repo_cfg()
        try:
            since = float(request.args.get("since", "0"))
        except ValueError:
            since = 0.0

        changed = []
        for test_file in sorted(cfg_local.tests_dir.glob("test_*.py")):
            if test_file.is_file() and test_file.stat().st_mtime >= since:
                changed.append(
                    {
                        "path": _repo_rel(test_file),
                        "mtime": datetime.fromtimestamp(test_file.stat().st_mtime, timezone.utc).isoformat(),
                    }
                )

        return jsonify({"files": changed, "count": len(changed)})

    @app.post("/api/run-tests")
    def run_tests():
        cfg_local = _repo_cfg()
        body = request.get_json(silent=True) or {}
        project_name = body.get("project_name") or os.environ.get("AZURE_DEVOPS_PROJECT") or "UnitTestCaseAgent"
        date_stamp = body.get("date_stamp") or _utc_date()

        code, _ = run_script([sys.executable, "-m", "pytest"], cwd=cfg_local.repo_root, env=os.environ.copy(), label="pytest")
        if code != 0:
            return _json_error("pytest failed", 500)

        for fmt in ("docx", "xlsx"):
            argv = [
                sys.executable,
                str(cfg_local.export_script),
                "--format",
                fmt,
                "--project-name",
                project_name,
                "--date-stamp",
                date_stamp,
            ]
            code, _ = run_script(argv, cwd=cfg_local.repo_root, env=os.environ.copy(), label=f"export-{fmt}")
            if code != 0:
                return _json_error(f"export {fmt} failed", 500)

        return jsonify({"ok": True, "reports": [{"name": p.name, "path": _repo_rel(p)} for p in _report_files()]})

    @app.get("/api/download")
    def download():
        rel_path = request.args.get("path", "")
        try:
            file_path = _safe_report_path(rel_path)
        except ValueError:
            return jsonify({"error": "Invalid path"}), 400
        if not file_path.exists() or not file_path.is_file():
            return jsonify({"error": "File not found"}), 404
        return send_file(file_path, as_attachment=True, download_name=file_path.name)

    @app.post("/api/delete")
    def delete_report():
        rel_path = (request.get_json(silent=True) or {}).get("path", "")
        try:
            file_path = _safe_report_path(rel_path)
        except ValueError:
            return jsonify({"error": "Invalid path"}), 400
        if not file_path.exists():
            return jsonify({"error": "File not found"}), 404
        file_path.unlink()
        LOG_BUFFER.append("reports", f"Deleted {rel_path}")
        return jsonify({"ok": True})

    @app.get("/api/zip")
    def reports_zip():
        cfg_local = _repo_cfg()
        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, mode="w", compression=zipfile.ZIP_DEFLATED) as zf:
            for report in _report_files():
                zf.write(report, arcname=report.name)
        buffer.seek(0)
        return send_file(buffer, as_attachment=True, download_name="test_reports.zip", mimetype="application/zip")

    @app.post("/api/fcs-upload")
    def fcs_upload():
        cfg_local = _repo_cfg()
        body = request.get_json(silent=True) or {}
        rel_path = body.get("path")
        if not rel_path:
            return jsonify({"error": "Missing path"}), 400

        try:
            abs_path = _safe_repo_path(rel_path)
        except ValueError:
            return jsonify({"error": "Invalid path"}), 400

        if not abs_path.exists() or not abs_path.is_file():
            return jsonify({"error": "File not found"}), 404

        check_code, check_lines = _run_fcs_check()
        if check_code == 2:
            return jsonify({"skipped": True, "reason": "FC S host not reachable. Are you on the L&T network/VPN?"}), 503
        if check_code != 0:
            return jsonify({"error": "FC S connectivity check failed", "details": check_lines[-10:]}), 500

        tableid = (body.get("tableid") or _default_tableid(abs_path)).upper()
        project_name = body.get("project_name") or os.environ.get("AZURE_DEVOPS_PROJECT") or "UnitTestCaseAgent"
        date_stamp = body.get("date_stamp") or _utc_date()

        code, lines = _upload_one(abs_path, tableid, project_name, date_stamp)
        if code != 0:
            return jsonify({"error": "FC S upload failed", "details": lines[-10:]}), 500
        return jsonify({"ok": True, "path": _repo_rel(abs_path), "tableid": tableid})

    @app.post("/api/fcs-upload-all")
    def fcs_upload_all():
        cfg_local = _repo_cfg()
        body = request.get_json(silent=True) or {}
        project_name = body.get("project_name") or os.environ.get("AZURE_DEVOPS_PROJECT") or "UnitTestCaseAgent"
        date_stamp = body.get("date_stamp") or _utc_date()

        check_code, check_lines = _run_fcs_check()
        if check_code == 2:
            return jsonify({"skipped": True, "reason": "FC S host not reachable. Are you on the L&T network/VPN?"}), 503
        if check_code != 0:
            return jsonify({"error": "FC S connectivity check failed", "details": check_lines[-10:]}), 500

        uploads: list[dict[str, str]] = []
        failures: list[dict[str, object]] = []

        for report in sorted(cfg_local.reports_dir.glob("*.docx")) + sorted(cfg_local.reports_dir.glob("*.xlsx")):
            code, lines = _upload_one(report, "OUTPUT", project_name, date_stamp)
            if code == 0:
                uploads.append({"path": _repo_rel(report), "tableid": "OUTPUT"})
            else:
                failures.append({"path": _repo_rel(report), "details": lines[-10:]})

        markdowns = _markdown_candidates()
        if markdowns:
            latest_md = max(markdowns, key=lambda p: p.stat().st_mtime)
            code, lines = _upload_one(latest_md, "INPUT", project_name, date_stamp)
            if code == 0:
                uploads.append({"path": _repo_rel(latest_md), "tableid": "INPUT"})
            else:
                failures.append({"path": _repo_rel(latest_md), "details": lines[-10:]})

        if failures:
            return jsonify({"ok": False, "uploaded": uploads, "failures": failures}), 500
        return jsonify({"ok": True, "uploaded": uploads})

    @app.get("/api/fcs-check")
    def fcs_check():
        code, lines = _run_fcs_check()
        if code == 0:
            return jsonify({"ok": True, "reason": "reachable", "details": lines[-5:]})
        if code == 2:
            return jsonify({"ok": False, "reason": "FC S host not reachable. Are you on the L&T network/VPN?", "details": lines[-5:]})
        return jsonify({"ok": False, "reason": "FC S connectivity check failed", "details": lines[-5:]}), 500

    @app.get("/api/log/tail")
    def log_tail():
        try:
            since = int(request.args.get("since", "0"))
        except ValueError:
            since = 0
        entries = LOG_BUFFER.tail(since)
        next_seq = entries[-1]["seq"] if entries else since
        return jsonify({"entries": entries, "next_seq": next_seq})

    return app


def main() -> None:
    app = create_app()
    cfg: WebUIConfig = app.config["WEBUI_CFG"]
    app.run(host=cfg.host, port=cfg.port, debug=False)


if __name__ == "__main__":
    main()
