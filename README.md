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

## Files

| File | Purpose |
|------|---------|
| `.github/agents/unit-test-generator.agent.md` | Agent definition and instructions |
| `.github/copilot-instructions.md` | Project-level Copilot customization |
| `.github/workflows/convert-excel.yml` | Auto-converts pushed Excel files to Markdown |
| `scripts/excel_to_md.py` | Converts Excel workbooks to Markdown |
| `scripts/requirements.txt` | Excel conversion dependencies |
| `sample/user_stories_sample.md` | Sample user stories for testing |
