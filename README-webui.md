# Local Web Console (Flask)

This repository includes a local-only Flask web console under `webui/`.

## Quick start

```bash
git clone https://github.com/Komal001503/UnitTestCaseAgent.git
cd UnitTestCaseAgent
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r scripts/requirements.txt
python run_webui.py
```

Open: `http://localhost:5000`

## Important local-only note

This app is designed for localhost use only. Default bind host is `127.0.0.1`. Do not expose it to a shared network.

## Environment setup

Copy `.env.example` to `.env` and fill your values:

- Azure DevOps: `AZURE_DEVOPS_ORG`, `AZURE_DEVOPS_PROJECT`, `AZURE_DEVOPS_TEAM`, `AZURE_DEVOPS_PAT`
- FC S: `FCS_USERNAME`, `FCS_PASSWORD`, `FCS_TOKEN`, `FCS_BASE_URL`, `FCS_VERIFY_SSL`

## Generate flow (Flavor B)

When you click **Generate Test Cases**:

1. The app creates a prompt from the selected markdown file.
2. The browser copies the prompt to clipboard.
3. You paste it into Copilot Chat in VS Code and run generation there.
4. Click **I've finished — refresh test list** to detect new test files.
5. Optionally run pytest + report export (`docx` and `xlsx`) from the UI.

## FC S upload note

FC S upload works only when your machine can resolve/reach the FC S host (for example, on L&T network/VPN). If connectivity check returns DNS skip, the UI shows a non-fatal warning.

## Routes

- `GET /`
- `GET /api/markdown-files`
- `GET /api/reports`
- `POST /api/sync-devops`
- `POST /api/upload-excel`
- `POST /api/generate`
- `GET /api/tests/diff?since=<ts>`
- `POST /api/run-tests`
- `GET /api/download?path=<rel>`
- `GET /api/zip`
- `POST /api/fcs-upload`
- `POST /api/fcs-upload-all`
- `GET /api/fcs-check`
- `GET /api/log/tail?since=<seq>`
