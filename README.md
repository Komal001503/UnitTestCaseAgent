# Unit Test Case Generator Agent

A custom GitHub Copilot agent that generates unit test cases from user stories.

## How It Works

1. **Provide user stories** — Push an `.xlsx` file to the repository or convert one locally with the included script.
2. **Markdown is generated automatically** — GitHub Actions converts each pushed Excel workbook into a `.md` file with the same name in the same directory.
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

The agent generates test cases as `.py` files in the `tests/` directory. To export them as a human-readable **text** or **Word** document grouped by user story, use the export script:

```bash
# Export as plain text file
python scripts/export_tests_to_text.py

# Export as Word document (.docx)
pip install python-docx
python scripts/export_tests_to_text.py --format docx
```

Output files are saved to `test_reports/` by default. Use `--output-dir` to change the destination, or `--tests-dir` to point at a different test directory.

Each report includes:
- Test cases organized by user story ID (US-001, US-002, etc.)
- Test type classification (Positive, Negative, Boundary, Integration)
- Test method names and descriptions
- A summary with total counts per user story

## Pulling User Stories from Azure DevOps

You can pull User Stories directly from an Azure DevOps Boards backlog instead of uploading an Excel file.

### Prerequisites

1. **Create a Personal Access Token (PAT)** in Azure DevOps:
   - Go to <https://dev.azure.com> → User Settings → Personal Access Tokens → New Token.
   - Grant the **Work Items: Read** scope (all other scopes can be left unchecked).
   - Copy the generated token.

2. **Add the PAT as a repository secret** named `AZURE_DEVOPS_PAT`:
   - Repository → Settings → Secrets and variables → Actions → New repository secret.
   - Name: `AZURE_DEVOPS_PAT` · Value: the token you copied above.

### Running the workflow manually

1. Go to **Actions** → **Sync Azure DevOps User Stories** → **Run workflow**.
2. Fill in (or accept the defaults for):
   - **org** – Azure DevOps organisation
   - **project** – Azure DevOps project
   - **team** – Azure DevOps team
   - **output\_path** – destination Markdown file (default: `azure_devops_user_stories.md`)
3. Click **Run workflow**.

The workflow also runs automatically **every day at 02:00 UTC** (configurable via the `schedule` trigger in `.github/workflows/sync-azure-devops.yml`).

### Local usage

```bash
# Replace the values below with your own Azure DevOps organisation, project, and team
pip install -r scripts/requirements.txt
export AZURE_DEVOPS_ORG="LnT-HeavyEngineering-IEMQS"
export AZURE_DEVOPS_PROJECT="Workforce Management by MX Techies"
export AZURE_DEVOPS_TEAM="Workforce Management by MX Techies Team"
export AZURE_DEVOPS_PAT="***"
python scripts/azure_devops_to_md.py --output azure_devops_user_stories.md
```

Additional flags (see `--help` for the full list):

| Flag | Description |
|------|-------------|
| `--org` | ADO organisation (overrides `AZURE_DEVOPS_ORG`) |
| `--project` | ADO project (overrides `AZURE_DEVOPS_PROJECT`) |
| `--team` | ADO team (overrides `AZURE_DEVOPS_TEAM`) |
| `--work-item-type` | Work item type (default: `User Story`) |
| `--states` | Comma-separated state filter (default: all except `Removed`) |
| `--area-path` | Area path filter |
| `--output` / `-o` | Output file path |
| `--dry-run` | Print WIQL + matched item count without writing a file |
| `--verbose` / `-v` | Enable verbose logging |

### Using the generated file with the agent

Invoke `@unit-test-generator` in Copilot Chat exactly as you would for any other user-story Markdown file:

> Read `azure_devops_user_stories.md` and generate unit test cases for the user stories.

The agent will parse each User Story, identify acceptance criteria, and produce unit tests in the `tests/` directory — the same flow as for `user_stories.md`.

## Files

| File | Purpose |
|------|---------|
| `.github/agents/unit-test-generator.agent.md` | Agent definition and instructions |
| `.github/copilot-instructions.md` | Project-level Copilot customization |
| `.github/workflows/convert-excel.yml` | Auto-converts pushed Excel files to Markdown |
| `.github/workflows/sync-azure-devops.yml` | Pulls User Stories from Azure DevOps Boards to Markdown (daily + manual) |
| `scripts/excel_to_md.py` | Converts Excel workbooks to Markdown |
| `scripts/azure_devops_to_md.py` | Fetches User Stories from Azure DevOps and writes Markdown |
| `scripts/export_tests_to_text.py` | Exports test cases from `.py` files to text or Word documents |
| `scripts/requirements.txt` | Script dependencies (Excel conversion + Word export + ADO sync) |
| `sample/user_stories_sample.md` | Sample user stories for testing |
