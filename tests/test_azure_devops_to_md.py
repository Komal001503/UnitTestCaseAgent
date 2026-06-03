import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts import azure_devops_to_md


class AzureDevOpsToMarkdownTests(unittest.TestCase):
    def test_build_wiql_defaults_to_excluding_removed(self):
        config = azure_devops_to_md.Config(
            org="org",
            project="project",
            team=None,
            pat="token",
            work_item_type="User Story",
            states=None,
            area_path=None,
        )

        wiql = azure_devops_to_md.build_wiql(config)

        self.assertIn("[System.State] <> 'Removed'", wiql)
        self.assertNotIn("[System.State] IN", wiql)

    def test_build_wiql_with_states_and_area_path(self):
        config = azure_devops_to_md.Config(
            org="org",
            project="project",
            team="team",
            pat="token",
            work_item_type="User Story",
            states=["New", "Active"],
            area_path="Product\\Area",
        )

        wiql = azure_devops_to_md.build_wiql(config)

        self.assertIn("[System.State] IN ('New', 'Active')", wiql)
        self.assertIn("[System.AreaPath] UNDER 'Product\\Area'", wiql)

    def test_resolve_config_requires_pat(self):
        args = azure_devops_to_md.parse_args(["--org", "org", "--project", "project"])
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaisesRegex(ValueError, "AZURE_DEVOPS_PAT is required"):
                azure_devops_to_md.resolve_config(args)

    def test_to_markdown_includes_required_sections(self):
        config = azure_devops_to_md.Config(
            org="LnT-HeavyEngineering-IEMQS",
            project="Workforce Management by MX Techies",
            team=None,
            pat="token",
            work_item_type="User Story",
            states=None,
            area_path=None,
        )
        work_items = [
            {
                "fields": {
                    "System.Id": 101,
                    "System.Title": "Login story",
                    "System.State": "Active",
                    "Microsoft.VSTS.Common.Priority": 1,
                    "System.AssignedTo": {"displayName": "User One"},
                    "System.AreaPath": "Area\\Path",
                    "System.IterationPath": "Sprint 1",
                    "System.Tags": "auth;login",
                    "System.Description": "<p>User can login</p>",
                    "Microsoft.VSTS.Common.AcceptanceCriteria": "<ul><li>Valid credentials</li></ul>",
                }
            }
        ]

        markdown = azure_devops_to_md.to_markdown(config, work_items)

        self.assertIn("| Story ID | Title | State | Priority | Assigned To |", markdown)
        self.assertIn("## US-101 — Login story", markdown)
        self.assertIn("### Description", markdown)
        self.assertIn("### Acceptance Criteria", markdown)
        self.assertIn("https://dev.azure.com/LnT-HeavyEngineering-IEMQS/Workforce%20Management%20by%20MX%20Techies/_workitems/edit/101", markdown)

    def test_run_dry_run_does_not_write_file(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "stories.md"
            args = azure_devops_to_md.parse_args(
                ["--org", "org", "--project", "project", "--output", str(output_path), "--dry-run"]
            )
            with patch.dict(os.environ, {"AZURE_DEVOPS_PAT": "token"}, clear=True):
                with patch("scripts.azure_devops_to_md.fetch_work_item_ids", return_value=[1]) as mocked_ids:
                    with patch("scripts.azure_devops_to_md.fetch_work_items", return_value=[]):
                        exit_code = azure_devops_to_md.run(args)

            self.assertEqual(exit_code, 0)
            self.assertFalse(output_path.exists())
            mocked_ids.assert_called_once()


if __name__ == "__main__":
    unittest.main()
