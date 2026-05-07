#!/usr/bin/env python3
"""Export unit test cases from .py test files to structured text files.

Parses Python unittest files, extracts test classes and methods with their
docstrings, and produces a human-readable text report grouped by user story.

Usage:
    python scripts/export_tests_to_text.py [--output-dir OUTPUT_DIR] [--format {txt,docx}]

By default, output is written to ``test_reports/`` in the repository root.
"""

import argparse
import ast
import re
import textwrap
from pathlib import Path


# ---------------------------------------------------------------------------
# Argument parsing
# ---------------------------------------------------------------------------

def parse_args():
    parser = argparse.ArgumentParser(
        description="Export Python unit tests to text (or Word) files grouped by user story."
    )
    parser.add_argument(
        "--tests-dir",
        default=None,
        help="Directory containing test_*.py files (default: tests/ in repo root)",
    )
    parser.add_argument(
        "--output-dir",
        "-o",
        default=None,
        help="Directory for output files (default: test_reports/ in repo root)",
    )
    parser.add_argument(
        "--format",
        choices=["txt", "docx"],
        default="txt",
        help="Output format: 'txt' (plain text) or 'docx' (Word document). Default: txt",
    )
    return parser.parse_args()


# ---------------------------------------------------------------------------
# AST helpers – extract structured info from test files
# ---------------------------------------------------------------------------

def _extract_docstring(node) -> str:
    """Return the docstring of an AST node, or empty string."""
    ds = ast.get_docstring(node)
    return ds.strip() if ds else ""


def _extract_test_type(docstring: str) -> str:
    """Heuristically determine test type from the docstring prefix."""
    lower = docstring.lower()
    for label in ("positive", "negative", "boundary", "integration", "edge"):
        if lower.startswith(label):
            return label.capitalize()
    return "General"


_US_PATTERN = re.compile(r"US-\d+", re.IGNORECASE)


def _extract_user_stories(text: str) -> list[str]:
    """Return a sorted unique list of user story IDs found in *text*."""
    return sorted(set(m.group().upper() for m in _US_PATTERN.finditer(text)))


def parse_test_file(filepath: Path) -> list[dict]:
    """Parse a single test file and return a list of test-class dicts.

    Each dict has keys:
        class_name, class_docstring, user_stories, tests
    where ``tests`` is a list of dicts with:
        method_name, docstring, test_type
    """
    source = filepath.read_text(encoding="utf-8")
    tree = ast.parse(source, filename=str(filepath))

    # Also extract user stories mentioned in the module docstring.
    module_docstring = _extract_docstring(tree)
    module_stories = _extract_user_stories(module_docstring)

    classes: list[dict] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.ClassDef):
            continue
        cls_doc = _extract_docstring(node)
        cls_stories = _extract_user_stories(cls_doc) or module_stories

        methods: list[dict] = []
        for item in node.body:
            if isinstance(item, ast.FunctionDef) and item.name.startswith("test_"):
                m_doc = _extract_docstring(item)
                methods.append({
                    "method_name": item.name,
                    "docstring": m_doc,
                    "test_type": _extract_test_type(m_doc),
                })

        if methods:
            classes.append({
                "class_name": node.name,
                "class_docstring": cls_doc,
                "user_stories": cls_stories,
                "source_file": filepath.name,
                "tests": methods,
            })

    return classes


# ---------------------------------------------------------------------------
# Group parsed data by user story
# ---------------------------------------------------------------------------

def group_by_user_story(all_classes: list[dict]) -> dict[str, list[dict]]:
    """Return {story_id: [class_dict, ...]} mapping."""
    grouped: dict[str, list[dict]] = {}
    for cls in all_classes:
        for story_id in cls["user_stories"]:
            grouped.setdefault(story_id, []).append(cls)
    return dict(sorted(grouped.items(), key=lambda kv: kv[0]))


# ---------------------------------------------------------------------------
# Rendering – plain text
# ---------------------------------------------------------------------------

def _story_sort_key(story_id: str) -> int:
    """Extract numeric part of US-NNN for sorting."""
    m = re.search(r"\d+", story_id)
    return int(m.group()) if m else 0


def render_text(grouped: dict[str, list[dict]]) -> str:
    """Render grouped test data as a human-readable plain-text report."""
    lines: list[str] = []
    lines.append("=" * 80)
    lines.append("UNIT TEST CASES REPORT")
    lines.append("Generated from Python test files")
    lines.append("=" * 80)
    lines.append("")

    sorted_stories = sorted(grouped.keys(), key=_story_sort_key)

    for story_id in sorted_stories:
        classes = grouped[story_id]
        lines.append("-" * 80)
        lines.append(f"USER STORY: {story_id}")
        lines.append("-" * 80)
        lines.append("")

        test_counter = 0
        for cls in classes:
            lines.append(f"  Test Class: {cls['class_name']}")
            if cls["class_docstring"]:
                lines.append(f"  Description: {cls['class_docstring']}")
            lines.append(f"  Source File: {cls['source_file']}")
            lines.append("")

            # Build scenario table
            lines.append(f"  {'#':<4} {'Type':<14} {'Test Method':<55} Description")
            lines.append(f"  {'─'*4} {'─'*14} {'─'*55} {'─'*40}")

            for test in cls["tests"]:
                test_counter += 1
                ttype = test["test_type"]
                name = test["method_name"]
                desc = test["docstring"] or "(no description)"
                # Remove type prefix from description since we show it separately
                desc_clean = re.sub(
                    r"^(Positive|Negative|Boundary|Integration|Edge|General)\s*:\s*",
                    "",
                    desc,
                    flags=re.IGNORECASE,
                )
                lines.append(f"  {test_counter:<4} {ttype:<14} {name:<55} {desc_clean}")

            lines.append("")

        lines.append(f"  Total test cases for {story_id}: {test_counter}")
        lines.append("")

    # Summary
    lines.append("=" * 80)
    lines.append("SUMMARY")
    lines.append("=" * 80)
    total = 0
    for story_id in sorted_stories:
        count = sum(len(c["tests"]) for c in grouped[story_id])
        total += count
        lines.append(f"  {story_id}: {count} test case(s)")
    lines.append(f"\n  TOTAL TEST CASES: {total}")
    lines.append("")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Rendering – Word document (docx)
# ---------------------------------------------------------------------------

def render_docx(grouped: dict[str, list[dict]], output_path: Path) -> None:
    """Render grouped test data as a Word (.docx) document."""
    try:
        from docx import Document
        from docx.shared import Pt, Inches
        from docx.enum.text import WD_ALIGN_PARAGRAPH
    except ImportError:
        raise SystemExit(
            "python-docx is required for Word output. Install it with:\n"
            "  pip install python-docx"
        )

    doc = Document()

    # Title
    title = doc.add_heading("Unit Test Cases Report", level=0)
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    doc.add_paragraph("Generated from Python test files")
    doc.add_paragraph("")

    sorted_stories = sorted(grouped.keys(), key=_story_sort_key)

    for story_id in sorted_stories:
        classes = grouped[story_id]
        doc.add_heading(f"User Story: {story_id}", level=1)

        for cls in classes:
            doc.add_heading(cls["class_name"], level=2)
            if cls["class_docstring"]:
                doc.add_paragraph(cls["class_docstring"])
            doc.add_paragraph(f"Source File: {cls['source_file']}")

            # Table: #, Type, Test Method, Description
            table = doc.add_table(rows=1, cols=4)
            table.style = "Light Grid Accent 1"
            hdr = table.rows[0].cells
            hdr[0].text = "#"
            hdr[1].text = "Type"
            hdr[2].text = "Test Method"
            hdr[3].text = "Description"

            for idx, test in enumerate(cls["tests"], start=1):
                row = table.add_row().cells
                row[0].text = str(idx)
                row[1].text = test["test_type"]
                row[2].text = test["method_name"]
                desc = test["docstring"] or "(no description)"
                desc_clean = re.sub(
                    r"^(Positive|Negative|Boundary|Integration|Edge|General)\s*:\s*",
                    "",
                    desc,
                    flags=re.IGNORECASE,
                )
                row[3].text = desc_clean

            doc.add_paragraph("")

    # Summary
    doc.add_heading("Summary", level=1)
    total = 0
    for story_id in sorted_stories:
        count = sum(len(c["tests"]) for c in grouped[story_id])
        total += count
        doc.add_paragraph(f"{story_id}: {count} test case(s)")
    doc.add_paragraph(f"\nTotal Test Cases: {total}")

    doc.save(str(output_path))


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    args = parse_args()

    repo_root = Path(__file__).resolve().parent.parent
    tests_dir = Path(args.tests_dir) if args.tests_dir else repo_root / "tests"
    output_dir = Path(args.output_dir) if args.output_dir else repo_root / "test_reports"

    if not tests_dir.is_dir():
        raise SystemExit(f"Tests directory not found: {tests_dir}")

    output_dir.mkdir(parents=True, exist_ok=True)

    # Collect all test files (exclude __init__.py and non-test files)
    test_files = sorted(tests_dir.glob("test_*.py"))
    if not test_files:
        raise SystemExit(f"No test_*.py files found in {tests_dir}")

    # Parse all files
    all_classes: list[dict] = []
    for tf in test_files:
        all_classes.extend(parse_test_file(tf))

    # Group by user story
    grouped = group_by_user_story(all_classes)

    if args.format == "txt":
        report = render_text(grouped)
        out_file = output_dir / "unit_test_cases_report.txt"
        out_file.write_text(report, encoding="utf-8")
        print(f"Text report written to {out_file}")
    elif args.format == "docx":
        out_file = output_dir / "unit_test_cases_report.docx"
        render_docx(grouped, out_file)
        print(f"Word document written to {out_file}")


if __name__ == "__main__":
    main()
