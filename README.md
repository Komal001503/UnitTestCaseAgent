# Unit Test Case Generator Agent

A custom GitHub Copilot agent that generates unit test cases from user stories.

## How It Works

1. **Provide user stories** — Push an `.xlsx` file to the repository or sync User Stories from Azure DevOps Boards.
2. **Markdown is generated automatically** — GitHub Actions converts Excel workbooks and can sync Azure DevOps User Stories into Markdown.
3. **Invoke the agent** — Use `@unit-test-generator` in Copilot Chat.
4. **Get test cases** — The agent analyzes your user stories, maps them to your codebase, and generates comprehensive unit tests.

## Setup

### Prerequisites
- GitHub Copilot Pro, Pro+, Business, or Enterprise plan
- Cloud agent access enabled for your org/account

### Converting Excel User Stories Locally

```bash
pip install -r scripts/requirements.txt
python scripts/excel_to_md.py path/to/user_stories.xlsx
```

The script writes `path/to/user_stories.md` by default. Use `--output` if you need a different Markdown path.

### Automatic Excel-to-Markdown Workflow

When you push a new or updated `.xlsx` file anywhere in the repository, `.github/workflows/convert-excel.yml` will:

1. Detect the changed Excel workbook(s)
2. Run `scripts/excel_to_md.py` with `pandas` and `openpyxl`
3. Generate a matching `.md` file in the same directory
4. Commit and push the generated Markdown file back to the same branch automatically

### Pulling User Stories from Azure DevOps

1. Create a repository secret named `AZURE_DEVOPS_PAT` with **Work Items: Read** scope.
2. Run `.github/workflows/sync-azure-devops.yml` manually from **Actions** (workflow_dispatch), or let the daily `0 2 * * *` UTC schedule sync stories automatically.
3. The workflow pulls `User Story` items and writes Markdown (default: `azure_devops_user_stories.md`) that the agent can consume directly.

#### Filtering which stories to fetch

Use `filter_mode` in the workflow **Run workflow** dialog:

- `All` → no extra scope filter (all stories of selected work item type)
- `ByIteration` → use `iteration_path` (example: `Workforce Management by MX Techies\\Sprint 12`)
- `ByArea` → use `area_path` (example: `Workforce Management by MX Techies\\Payroll`)
- `ByBacklog` → use `backlog` to select a team backlog by name (example: `IEMQS-SAP-Integration` or `Feature Team 1`). The workflow resolves that team's configured **Area Paths** from Azure DevOps at runtime, so you can sync any team's backlog from any project you point `project` at. If you mistype the name the run fails fast and prints every available backlog/team in the project.
- `ByAssignee` → use `assigned_to` (example: `alice@example.com` or `Alice Smith`)
- `ByTags` → use `tags` as comma-separated values (story must contain all tags)
- `ByIds` → use `ids` as comma-separated work item IDs (example: `1234,1240`)

You can also restrict by **State** independently of `filter_mode` — for example, fetch every story assigned to Alice that is still `New`:

- `state` → choose one of `All`, `New`, `Active`, `Resolved`, `Closed`, or `Open` (= `New, Active, Resolved`)
- `states` → advanced override: comma-separated list (e.g. `New,Active`). When set, this takes precedence over `state`.

`state` defaults to `All`, which keeps the original behaviour of returning every state except `Removed`. To mimic the Azure DevOps **Boards → Work items** default view (which hides closed items), pick `state=Active` or `state=Open`.

You can also apply date filtering in the same run:

- `from_date` and `to_date` are optional and use `YYYY-MM-DD` (inclusive when provided)
- `date_field` is fully optional — pick `None` (or leave the dates blank) to skip date filtering entirely
- If you provide a date but leave `date_field` as `None`, the sync falls back to `ChangedDate`

Example: To fetch only stories changed in November 2025, set `from_date=2025-11-01`, `to_date=2025-11-30`, and set `date_field=ChangedDate`. To skip date filtering, leave the dates blank or keep `date_field=None`.

Local usage:

```bash
pip install -r scripts/requirements.txt
export AZURE_DEVOPS_ORG="LnT-HeavyEngineering-IEMQS"
export AZURE_DEVOPS_PROJECT="Workforce Management by MX Techies"
export AZURE_DEVOPS_TEAM="Workforce Management by MX Techies Team"
export AZURE_DEVOPS_PAT="***"
python scripts/azure_devops_to_md.py --output azure_devops_user_stories.md
```

The same filters are available as CLI flags/environment variables for local runs:

```bash
python scripts/azure_devops_to_md.py \
  --backlog "IEMQS-SAP-Integration" \
  --iteration-path "Workforce Management by MX Techies\\Sprint 12" \
  --states "New,Active" \
  --from-date 2025-11-01 --to-date 2025-11-30 \
  --output azure_devops_user_stories.md
```

You can invoke the agent with Azure DevOps markdown the same way as Excel-generated markdown:

> Read `azure_devops_user_stories.md` and generate unit test cases for the user stories.

End-to-end flow: **Azure DevOps User Story → `azure_devops_user_stories.md` → `@unit-test-generator` → tests in `tests/`**.

#### Troubleshooting: Only seeing certain types?

The script filters strictly by `--work-item-type` (default `User Story`). If your Azure DevOps project uses a different process template, override it:

- Scrum → `--work-item-type "Product Backlog Item"`
- Basic → `--work-item-type "Issue"`
- CMMI → `--work-item-type "Requirement"`

Bugs, Tasks, and other types are always excluded.

### Excel Format

Your Excel file should have these columns:

| Story ID | Title | Description | Acceptance Criteria | Priority |
|----------|-------|-------------|---------------------|----------|
| US-101   | User Login | User should be able to log in | Valid credentials → success; Invalid → error message | High |

## Usage

In GitHub Copilot Chat, select the **Unit Test Generator** agent and provide your prompt:

> Read `user_stories.md` and generate unit test cases for the user stories.

The agent will:
- Parse each user story and its acceptance criteria
- Identify positive, negative, and edge-case scenarios
- Search your codebase for relevant source files
- Generate unit tests following your project's conventions

## Exporting Test Cases to Text or Word

The agent generates test cases as `.py` files in the `tests/` directory. To export them as a human-readable **text**, **Word**, or **Excel** document grouped by user story, use the export script:

```bash
# Export as plain text file
python scripts/export_tests_to_text.py

# Export as Word document (.docx)
pip install python-docx
python scripts/export_tests_to_text.py --format docx

# Export as Excel spreadsheet (.xlsx) — with project name and date in filename
python scripts/export_tests_to_text.py --format xlsx \
  --project-name "Workforce Management by MX Techies"
```

Output files are saved to `test_reports/` by default. Use `--output-dir` to change the destination, or `--tests-dir` to point at a different test directory.

### Report filename

When `--project-name` is provided the report file is named after the **project** and the **generation date** (UTC):

```
WorkforceManagementByMXTechies_2026-06-04_test_report.xlsx
WorkforceManagementByMXTechies_2026-06-04_test_report.docx
```

The project name is sanitized automatically: whitespace is removed (words joined in CamelCase) and any characters outside `[A-Za-z0-9._-]` are replaced with underscores.

Use `--date-stamp YYYY-MM-DD` to pin the date (useful in CI or reproducible builds):

```bash
python scripts/export_tests_to_text.py --format xlsx \
  --project-name "Workforce Management by MX Techies" \
  --date-stamp 2026-06-04
```

`--project-name` can also be supplied via the `AZURE_DEVOPS_PROJECT` environment variable so CI workflows pick it up automatically.

Without `--project-name` the script falls back to the legacy `<sourceStoryStem>_test_report.{ext}` or `unit_test_cases_report.{ext}` naming.

### No tests yet?

If no `test_*.py` files exist under `tests/` (or none contain any test methods), the script exits **cleanly with code 0** and prints:

```
No tests found — skipping report generation. Run the Unit Test Generator agent to create test files in tests/ first.
```

No empty report files are written. Run the agent first to generate tests, then re-run the export script.

Each report includes:
- Test cases organized by user story ID (US-001, US-002, etc.)
- Test type classification (Positive, Negative, Boundary, Integration)
- Test method names and descriptions
- A summary with total counts per user story

## Uploading to FC S (File/Content Server)

Input documents (user stories converted from Excel or synced from Azure DevOps) and output
documents (generated test-case reports) can optionally be uploaded to the FC S server using
`scripts/fcs_uploader.py`.

### Upload endpoint

```
POST https://vhzqaplmfcs.lthed.com/api/DocumentUpload
```

By default the uploader sends `folder`, `tableid`, `linkedto`, `psno`, and `deleteright`
as multipart form fields and sends browser-like `Origin` / `Referer` headers using the browse
origin `https://vhziemqsqa.lthed.com:86/`. You can still switch the metadata to query params
or send it both ways via environment variables.

### Quick start

```bash
# Upload an input user-story file
python scripts/fcs_uploader.py upload path/to/user_stories.xlsx INPUT \
    "WorkforceManagementByMXTechies_2026-06-10"

# Upload an output report (let the script build the linkedto value from the project name)
python scripts/fcs_uploader.py upload test_reports/report.xlsx OUTPUT \
    --project-name "Workforce Management by MX Techies" --date-stamp 2026-06-10
```

Input and the matching output **must** share the same `linkedto` value so they can be paired
on the FC S side.

### Environment variables

| Variable           | Default                          | Description |
|--------------------|----------------------------------|-------------|
| `FCS_BASE_URL`     | `https://vhzqaplmfcs.lthed.com`  | FC S upload server base URL |
| `FCS_UPLOAD_PATH`  | `/api/DocumentUpload`            | Upload path |
| `FCS_HTTP_METHOD`  | `POST`                           | HTTP verb used for uploads |
| `FCS_FIELD_NAME`   | `file`                           | Multipart form-field name for the uploaded file |
| `FCS_FOLDER`       | `UnitTestCaseAgent`              | Folder metadata value |
| `FCS_PSNO`         | `20342252`                       | `psno` metadata value |
| `FCS_DELETE_RIGHT` | `False`                          | `deleteright` metadata value |
| `FCS_PARAMS_AS`    | `form`                           | Send metadata as `form`, `query`, or `both` |
| `FCS_BROWSE_ORIGIN`| `https://vhziemqsqa.lthed.com:86`| Sent as `Origin` and `Referer` |
| `FCS_FIELD_FOLDER` | `folder`                         | Field name for folder metadata |
| `FCS_FIELD_TABLEID`| `tableid`                        | Field name for tableid metadata |
| `FCS_FIELD_LINKEDTO`| `linkedto`                      | Field name for linkedto metadata |
| `FCS_FIELD_PSNO`   | `psno`                           | Field name for psno metadata |
| `FCS_FIELD_DELETERIGHT`| `deleteright`                | Field name for deleteright metadata |
| `FCS_USERNAME`     | —                                | Basic-auth username |
| `FCS_PASSWORD`     | —                                | Basic-auth password |
| `FCS_TOKEN`        | —                                | Bearer-token (alternative to basic auth) |
| `FCS_VERIFY_SSL`   | `true`                           | Set to `false` for self-signed certificates |
| `FCS_TIMEOUT`      | `60`                             | Request timeout in seconds |
| `FCS_MAX_RETRIES`  | `3`                              | Retry attempts on connection errors / HTTP 5xx |

### Probe mode

Use `--probe` to print the resolved request without uploading a file:

```bash
python scripts/fcs_uploader.py upload test_reports/report.xlsx OUTPUT \
    --project-name "Workforce Management by MX Techies" --probe
```

### Workflow integration

The existing Azure DevOps sync workflow now uploads the synced Markdown as `INPUT`, and the
report-export workflow uploads generated report files as `OUTPUT`.

### Retry behaviour

The client retries automatically on connection errors and HTTP 5xx responses using exponential
back-off (1 s → 2 s → 4 s …).  4xx responses are **not** retried and raise `FCSUploadError`
immediately.

## Files

| File | Purpose |
|------|---------|
| `.github/agents/unit-test-generator.agent.md` | Agent definition and instructions |
| `.github/copilot-instructions.md` | Project-level Copilot customization |
| `.github/workflows/convert-excel.yml` | Auto-converts pushed Excel files to Markdown |
| `.github/workflows/sync-azure-devops.yml` | Pulls Azure DevOps User Stories to Markdown on schedule/manual trigger |
| `scripts/azure_devops_to_md.py` | Fetches Azure DevOps User Stories and converts them to Markdown |
| `scripts/excel_to_md.py` | Converts Excel workbooks to Markdown |
| `scripts/export_tests_to_text.py` | Exports test cases from `.py` files to text or Word documents |
| `scripts/fcs_uploader.py` | Uploads input/output documents to the FC S server |
| `scripts/requirements.txt` | Script dependencies (Excel conversion + Azure DevOps sync + Word export) |
| `sample/user_stories_sample.md` | Sample user stories for testing |
