import io
from pathlib import Path

import pytest

from webui.app import create_app
from webui.config import WebUIConfig
from webui.runner import LOG_BUFFER


@pytest.fixture()
def webui_client(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()

    scripts_dir = repo / "scripts"
    scripts_dir.mkdir()
    for name in ["azure_devops_to_md.py", "excel_to_md.py", "export_tests_to_text.py", "fcs_uploader.py"]:
        (scripts_dir / name).write_text("# stub\n", encoding="utf-8")

    tests_dir = repo / "tests"
    tests_dir.mkdir()
    (tests_dir / "test_existing.py").write_text("def test_existing():\n    assert True\n", encoding="utf-8")

    reports_dir = repo / "test_reports"
    reports_dir.mkdir()
    report_path = reports_dir / "sample_report.xlsx"
    report_path.write_bytes(b"report")

    (repo / "README.md").write_text("readme", encoding="utf-8")
    (repo / "user_stories.md").write_text("# stories", encoding="utf-8")

    project_root = Path(__file__).resolve().parents[1]
    cfg = WebUIConfig(
        repo_root=repo,
        scripts_dir=scripts_dir,
        tests_dir=tests_dir,
        reports_dir=reports_dir,
        azure_script=scripts_dir / "azure_devops_to_md.py",
        excel_script=scripts_dir / "excel_to_md.py",
        export_script=scripts_dir / "export_tests_to_text.py",
        fcs_script=scripts_dir / "fcs_uploader.py",
        template_dir=project_root / "webui" / "templates",
        static_dir=project_root / "webui" / "static",
        host="127.0.0.1",
        port=5000,
        max_upload_bytes=25 * 1024 * 1024,
    )

    app = create_app(cfg)
    app.testing = True
    return app.test_client(), repo


def test_markdown_files_happy_path(webui_client):
    client, _ = webui_client

    response = client.get("/api/markdown-files")

    assert response.status_code == 200
    payload = response.get_json()
    assert [f["name"] for f in payload["files"]] == ["user_stories.md"]


def test_reports_happy_path(webui_client):
    client, _ = webui_client

    response = client.get("/api/reports")

    assert response.status_code == 200
    payload = response.get_json()
    assert payload["files"][0]["name"] == "sample_report.xlsx"


def test_sync_devops_happy_path(webui_client, monkeypatch):
    client, _ = webui_client

    def fake_run(argv, *, cwd, env, label):
        return 0, ["ok"]

    monkeypatch.setattr("webui.app.run_script", fake_run)

    response = client.post("/api/sync-devops", json={"project": "Demo"})

    assert response.status_code == 200
    assert response.get_json()["ok"] is True


def test_upload_excel_happy_path(webui_client, monkeypatch):
    client, repo = webui_client

    def fake_run(argv, *, cwd, env, label):
        (repo / "uploaded.md").write_text("# md", encoding="utf-8")
        return 0, ["ok"]

    monkeypatch.setattr("webui.app.run_script", fake_run)

    response = client.post(
        "/api/upload-excel",
        data={"file": (io.BytesIO(b"excel"), "uploaded.xlsx")},
        content_type="multipart/form-data",
    )

    assert response.status_code == 200
    payload = response.get_json()
    assert payload["uploaded"] == "uploaded.xlsx"


def test_generate_happy_path(webui_client):
    client, _ = webui_client

    response = client.post("/api/generate", json={"path": "user_stories.md"})

    assert response.status_code == 200
    payload = response.get_json()
    assert "Read `user_stories.md`" in payload["prompt"]
    assert "vscode://" in payload["vscode_chat_url"]
    assert payload["tests_dir_before"] == ["tests/test_existing.py"]


def test_tests_diff_happy_path(webui_client):
    client, repo = webui_client
    test_file = repo / "tests" / "test_new.py"
    test_file.write_text("def test_new():\n    assert True\n", encoding="utf-8")

    response = client.get("/api/tests/diff?since=0")

    assert response.status_code == 200
    payload = response.get_json()
    assert payload["count"] >= 1


def test_run_tests_happy_path(webui_client, monkeypatch):
    client, _ = webui_client
    calls = []

    def fake_run(argv, *, cwd, env, label):
        calls.append((label, argv))
        return 0, ["ok"]

    monkeypatch.setattr("webui.app.run_script", fake_run)

    response = client.post("/api/run-tests", json={"project_name": "Demo", "date_stamp": "2026-06-19"})

    assert response.status_code == 200
    labels = [label for label, _ in calls]
    assert labels == ["pytest", "export-docx", "export-xlsx"]


def test_download_happy_path(webui_client):
    client, _ = webui_client

    response = client.get("/api/download?path=test_reports/sample_report.xlsx")

    assert response.status_code == 200


def test_download_rejects_path_traversal(webui_client):
    client, _ = webui_client

    response = client.get("/api/download?path=../README.md")

    assert response.status_code == 400


def test_fcs_upload_happy_path(webui_client, monkeypatch):
    client, _ = webui_client

    def fake_run(argv, *, cwd, env, label):
        if argv[-1] == "check-connectivity":
            return 0, ["ok"]
        return 0, ["uploaded"]

    monkeypatch.setattr("webui.app.run_script", fake_run)

    response = client.post(
        "/api/fcs-upload",
        json={
            "path": "test_reports/sample_report.xlsx",
            "tableid": "OUTPUT",
            "project_name": "Demo",
            "date_stamp": "2026-06-19",
        },
    )

    assert response.status_code == 200
    assert response.get_json()["ok"] is True


def test_fcs_upload_rejects_path_traversal(webui_client):
    client, _ = webui_client

    response = client.post("/api/fcs-upload", json={"path": "../../etc/passwd"})

    assert response.status_code == 400


def test_fcs_upload_connectivity_skip_returns_503(webui_client, monkeypatch):
    client, _ = webui_client

    def fake_run(argv, *, cwd, env, label):
        if argv[-1] == "check-connectivity":
            return 2, ["dns failure"]
        return 0, ["uploaded"]

    monkeypatch.setattr("webui.app.run_script", fake_run)

    response = client.post("/api/fcs-upload", json={"path": "test_reports/sample_report.xlsx"})

    assert response.status_code == 503
    assert response.get_json()["skipped"] is True


def test_fcs_check_happy_path(webui_client, monkeypatch):
    client, _ = webui_client

    monkeypatch.setattr("webui.app.run_script", lambda *args, **kwargs: (0, ["ok"]))

    response = client.get("/api/fcs-check")

    assert response.status_code == 200
    assert response.get_json()["ok"] is True


def test_log_tail_happy_path(webui_client):
    client, _ = webui_client
    LOG_BUFFER.append("test", "hello")

    response = client.get("/api/log/tail?since=0")

    assert response.status_code == 200
    payload = response.get_json()
    assert payload["entries"]
