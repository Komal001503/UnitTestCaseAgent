#!/usr/bin/env python3
"""
Converts an Excel file containing user stories into Markdown format
that can be used as input for the Unit Test Generator agent.

Usage:
    python excel_to_md.py <input.xlsx> [--output output.md] [--sheet <sheet_name>]

Requirements:
    pip install pandas openpyxl tabulate
"""

import argparse
import sys
import pandas as pd


def parse_args():
    parser = argparse.ArgumentParser(
        description="Convert Excel user stories to Markdown for the Unit Test Generator agent."
    )
    parser.add_argument("input_file", help="Path to the Excel (.xlsx) file")
    parser.add_argument(
        "--output", "-o",
        help="Output Markdown file path (default: stdout)",
        default=None,
    )
    parser.add_argument(
        "--sheet", "-s",
        help="Name of the Excel sheet to read (default: first sheet)",
        default=0,
    )
    return parser.parse_args()


def excel_to_markdown(input_file: str, sheet=0) -> str:
    """Read an Excel file and convert it to a Markdown table."""
    try:
        df = pd.read_excel(input_file, sheet_name=sheet)
    except FileNotFoundError:
        print(f"Error: File '{input_file}' not found.", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error reading Excel file: {e}", file=sys.stderr)
        sys.exit(1)

    if df.empty:
        print("Warning: The Excel sheet is empty.", file=sys.stderr)
        return ""

    # Normalize column names
    df.columns = df.columns.str.strip()

    lines = []
    lines.append("# User Stories\n")
    lines.append(f"Total stories: {len(df)}\n")
    lines.append(df.to_markdown(index=False))
    lines.append("\n")

    # Also generate individual story blocks for clarity
    lines.append("---\n")
    lines.append("## Individual Stories\n")

    for _, row in df.iterrows():
        story_id = row.get("Story ID", row.get("ID", "N/A"))
        title = row.get("Title", row.get("Story Title", "N/A"))
        description = row.get("Description", "N/A")
        criteria = row.get("Acceptance Criteria", row.get("Criteria", "N/A"))
        priority = row.get("Priority", "N/A")

        lines.append(f"### {story_id}: {title}\n")
        lines.append(f"**Priority:** {priority}\n")
        lines.append(f"**Description:** {description}\n")
        lines.append(f"**Acceptance Criteria:**\n")

        # Split criteria by semicolons or newlines
        if pd.notna(criteria):
            criteria_str = str(criteria)
            for delimiter in [";", "\n"]:
                if delimiter in criteria_str:
                    for item in criteria_str.split(delimiter):
                        item = item.strip()
                        if item:
                            lines.append(f"- {item}")
                    break
            else:
                lines.append(f"- {criteria_str}")
        lines.append("\n")

    return "\n".join(lines)


def main():
    args = parse_args()
    markdown = excel_to_markdown(args.input_file, args.sheet)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(markdown)
        print(f"Markdown written to {args.output}", file=sys.stderr)
    else:
        print(markdown)


if __name__ == "__main__":
    main()
