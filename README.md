# Unit Test Case Generator Agent

A custom GitHub Copilot agent that generates unit test cases from user stories.

## How It Works

1. **Provide user stories** — Paste them from Excel or convert your `.xlsx` file to Markdown using the included script.
2. **Invoke the agent** — Use `@unit-test-generator` in Copilot Chat.
3. **Get test cases** — The agent analyzes your user stories, maps them to your codebase, and generates comprehensive unit tests.

## Setup

### Prerequisites
- GitHub Copilot Pro, Pro+, Business, or Enterprise plan
- Cloud agent access enabled for your org/account

### Converting Excel User Stories

```bash
pip install pandas openpyxl tabulate
python scripts/excel_to_md.py path/to/user_stories.xlsx > user_stories.md
```

### Excel Format

Your Excel file should have these columns:

| Story ID | Title | Description | Acceptance Criteria | Priority |
|----------|-------|-------------|---------------------|----------|
| US-101   | User Login | User should be able to log in | Valid credentials → success; Invalid → error message | High |

## Usage

In GitHub Copilot Chat, select the **Unit Test Generator** agent and provide your prompt:

> Generate unit test cases for the following user stories:
>
> | Story ID | Title | Acceptance Criteria |
> |----------|-------|---------------------|
> | US-101 | User Login | Valid credentials → success; Invalid → error |
> | US-102 | Password Reset | Reset email sent; Link expires after 24h |

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
| `scripts/excel_to_md.py` | Converts Excel user stories to Markdown |
| `sample/user_stories_sample.md` | Sample user stories for testing |
