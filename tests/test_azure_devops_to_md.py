import io
import unittest
from contextlib import redirect_stderr
from unittest.mock import patch

from scripts import azure_devops_to_md

SOURCE_STORY_FILE = "azure_devops_user_stories.md"


class AzureDevOpsToMarkdownTests(unittest.TestCase):
    def test_parse_args_includes_expected_flags(self):
        args = azure_devops_to_md.parse_args(
            [
                "--output",
                "out.md",
                "--org",
                "org",
                "--project",
                "project",
                "--team",
                "team",
                "--work-item-type",
                "User Story",
                "--states",
                "New,Active",
                "--area-path",
                "Area\\Sub",
                "--dry-run",
                "--verbose",
            ]
        )

        self.assertEqual(args.output, "out.md")
        self.assertEqual(args.org, "org")
        self.assertEqual(args.project, "project")
        self.assertEqual(args.team, "team")
        self.assertEqual(args.work_item_type, "User Story")
        self.assertEqual(args.states, "New,Active")
        self.assertEqual(args.area_path, "Area\\Sub")
        self.assertTrue(args.dry_run)
        self.assertTrue(args.verbose)

    def test_build_wiql_query_excludes_removed_by_default(self):
        with patch.dict(
            "os.environ",
            {
                "AZURE_DEVOPS_ORG": "org",
                "AZURE_DEVOPS_PROJECT": "proj",
                "AZURE_DEVOPS_PAT": "token",
            },
            clear=True,
        ):
            config = azure_devops_to_md.resolve_config(azure_devops_to_md.parse_args([]))

        wiql = azure_devops_to_md.build_wiql_query(config)
        self.assertIn("[System.WorkItemType] = 'User Story'", wiql)
        self.assertIn("[System.State] <> 'Removed'", wiql)
        self.assertIn("ORDER BY [System.Id] ASC", wiql)

    def test_main_missing_pat_exits_non_zero_with_clear_message(self):
        stderr = io.StringIO()
        with patch.dict(
            "os.environ",
            {"AZURE_DEVOPS_ORG": "org", "AZURE_DEVOPS_PROJECT": "proj"},
            clear=True,
        ), redirect_stderr(stderr):
            exit_code = azure_devops_to_md.main([])

        self.assertNotEqual(exit_code, 0)
        self.assertIn("Missing AZURE_DEVOPS_PAT", stderr.getvalue())

    def test_render_markdown_includes_required_sections(self):
        config = azure_devops_to_md.Config(
            org="org",
            project="project",
            team="team",
            pat="token",
            work_item_type="User Story",
            states=None,
            area_path=None,
            output=azure_devops_to_md.DEFAULT_OUTPUT_PATH,
            dry_run=False,
            verbose=False,
        )
        items = [
            {
                "fields": {
                    "System.Id": 101,
                    "System.Title": "User Login",
                    "System.State": "Active",
                    "Microsoft.VSTS.Common.Priority": 1,
                    "System.AssignedTo": {"displayName": "Jane Doe"},
                    "System.AreaPath": "Product\\Auth",
                    "System.IterationPath": "Sprint 1",
                    "System.Tags": "auth;login",
                    "System.Description": "<p>As a user, I can sign in.</p>",
                    "Microsoft.VSTS.Common.AcceptanceCriteria": "<ul><li>Valid login works</li></ul>",
                }
            }
        ]

        markdown = azure_devops_to_md.render_markdown(config, items)

        self.assertIn("## US-101 — User Login", markdown)
        self.assertIn("| Story ID | Title | State | Priority | Assigned To |", markdown)
        self.assertIn("| ADO URL | https://dev.azure.com/org/project/_workitems/edit/101 |", markdown)
        self.assertIn("### Description", markdown)
        self.assertIn("### Acceptance Criteria", markdown)

    def test_safe_cell_normalizes_table_breaking_characters(self):
        self.assertEqual(azure_devops_to_md._safe_cell("a|b\nc\rd"), "a\\|b c d")


if __name__ == "__main__":
    unittest.main()
