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

### Pulling User Stories from Azure DevOps

You can also sync User Stories directly from Azure DevOps Boards into a Markdown file that the agent can read.

#### Required repository secret

Create a repository secret named `AZURE_DEVOPS_PAT`:

- Go to Azure DevOps → User settings → **Personal access tokens**
- Create a token with **Work Items (Read)** scope
- In GitHub, open **Settings → Secrets and variables → Actions → New repository secret**
- Add it as `AZURE_DEVOPS_PAT`

#### Run the workflow manually

1. Open **Actions**
2. Select **Sync Azure DevOps User Stories**
3. Click **Run workflow**
4. Optionally override `org`, `project`, `team`, and `output_path`

The workflow also runs daily on a schedule (`0 2 * * *` UTC) to keep the Markdown file up to date.

#### Run locally

```bash
pip install -r scripts/requirements.txt
export AZURE_DEVOPS_ORG="LnT-HeavyEngineering-IEMQS"
export AZURE_DEVOPS_PROJECT="Workforce Management by MX Techies"
export AZURE_DEVOPS_TEAM="Workforce Management by MX Techies Team"
export AZURE_DEVOPS_PAT="***"
python scripts/azure_devops_to_md.py --output azure_devops_user_stories.md
```

You can invoke the agent against this file exactly like `user_stories.md`, for example:

> Read `azure_devops_user_stories.md` and generate unit test cases for the user stories.

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

## Files

| File | Purpose |
|------|---------|
| `.github/agents/unit-test-generator.agent.md` | Agent definition and instructions |
| `.github/copilot-instructions.md` | Project-level Copilot customization |
| `.github/workflows/convert-excel.yml` | Auto-converts pushed Excel files to Markdown |
| `.github/workflows/sync-azure-devops.yml` | Pulls Azure DevOps user stories to Markdown on demand and daily |
| `scripts/excel_to_md.py` | Converts Excel workbooks to Markdown |
| `scripts/azure_devops_to_md.py` | Fetches Azure DevOps user stories and writes Markdown |
| `scripts/export_tests_to_text.py` | Exports test cases from `.py` files to text or Word documents |
| `scripts/requirements.txt` | Script dependencies (Excel conversion + Word export) |
| `sample/user_stories_sample.md` | Sample user stories for testing |
