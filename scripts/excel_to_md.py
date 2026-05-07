#!/usr/bin/env python3
"""Convert an Excel workbook into Markdown tables."""

import argparse
from pathlib import Path
import sys

import pandas as pd


def parse_args():
    parser = argparse.ArgumentParser(
        description="Convert an Excel workbook to Markdown for the Unit Test Generator agent."
    )
    parser.add_argument("input_file", help="Path to the Excel (.xlsx) file")
    parser.add_argument(
        "--output",
        "-o",
        help="Output Markdown file path (default: same name as input with .md extension)",
        default=None,
    )
    return parser.parse_args()


def default_output_path(input_file: str) -> Path:
    return Path(input_file).with_suffix(".md")


def _normalize_dataframe(dataframe: pd.DataFrame) -> pd.DataFrame:
    normalized = dataframe.copy()
    normalized.columns = [str(column).strip() for column in normalized.columns]
    return normalized.astype(object).where(pd.notna(normalized), "")


def workbook_to_markdown(input_file: str) -> str:
    sections = []

    with pd.ExcelFile(input_file, engine="openpyxl") as workbook:
        for sheet_name in workbook.sheet_names:
            dataframe = pd.read_excel(workbook, sheet_name=sheet_name)
            normalized = _normalize_dataframe(dataframe)

            sections.append(f"## {sheet_name}\n")
            if normalized.empty:
                sections.append("_This sheet is empty._\n")
                continue

            sections.append(normalized.to_markdown(index=False))
            sections.append("")

    return "\n".join(sections).strip() + "\n"


def convert_excel_to_markdown(input_file: str, output_file: str | None = None) -> Path:
    input_path = Path(input_file)
    if not input_path.is_file():
        raise FileNotFoundError(f"File '{input_file}' not found.")

    output_path = Path(output_file) if output_file else default_output_path(input_file)
    markdown = workbook_to_markdown(str(input_path))
    output_path.write_text(markdown, encoding="utf-8")
    return output_path


def main():
    args = parse_args()

    try:
        output_path = convert_excel_to_markdown(args.input_file, args.output)
    except FileNotFoundError as error:
        print(f"Error: {error}", file=sys.stderr)
        sys.exit(1)
    except Exception as error:  # pragma: no cover - defensive CLI handling
        print(f"Error reading Excel file: {error}", file=sys.stderr)
        sys.exit(1)

    print(f"Markdown written to {output_path}", file=sys.stderr)


if __name__ == "__main__":
    main()
