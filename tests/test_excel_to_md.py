import tempfile
import unittest
from pathlib import Path

import pandas as pd

from scripts.excel_to_md import convert_excel_to_markdown


class ConvertExcelToMarkdownTests(unittest.TestCase):
    def test_convert_excel_to_markdown_multiple_sheets_writes_expected_sections(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            workbook_path = Path(temporary_directory) / "user_stories.xlsx"
            output_path = workbook_path.with_suffix(".md")

            with pd.ExcelWriter(workbook_path, engine="openpyxl") as writer:
                pd.DataFrame(
                    [
                        {
                            "Story ID": "US-101",
                            "Title": "Login",
                            "Acceptance Criteria": "Valid credentials",
                            "Priority": "High",
                        }
                    ]
                ).to_excel(writer, sheet_name="Stories", index=False)
                pd.DataFrame(
                    [
                        {"Story ID": "US-102", "Title": None, "Acceptance Criteria": ""},
                    ]
                ).to_excel(writer, sheet_name="Backlog", index=False)

            returned_path = convert_excel_to_markdown(str(workbook_path))

            self.assertEqual(output_path, returned_path)
            markdown = output_path.read_text(encoding="utf-8")
            self.assertIn("## Stories", markdown)
            self.assertIn("## Backlog", markdown)
            self.assertIn("| US-101", markdown)
            self.assertIn("| US-102", markdown)
            self.assertNotIn("nan", markdown.lower())

    def test_convert_excel_to_markdown_marks_empty_sheet(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            workbook_path = Path(temporary_directory) / "empty.xlsx"
            output_path = workbook_path.with_suffix(".md")

            with pd.ExcelWriter(workbook_path, engine="openpyxl") as writer:
                pd.DataFrame(columns=["Story ID", "Title"]).to_excel(
                    writer,
                    sheet_name="Empty Sheet",
                    index=False,
                )

            convert_excel_to_markdown(str(workbook_path), str(output_path))

            markdown = output_path.read_text(encoding="utf-8")
            self.assertIn("## Empty Sheet", markdown)
            self.assertIn("_This sheet is empty._", markdown)


if __name__ == "__main__":
    unittest.main()
