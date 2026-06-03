import argparse
import unittest
from unittest.mock import Mock, patch

from scripts.azure_devops_to_md import (
    AzureDevOpsConfig,
    MissingPATError,
    build_wiql,
    fetch_work_items,
    render_markdown,
    resolve_config,
    wiql_url,
)


class AzureDevOpsToMarkdownTests(unittest.TestCase):
    def test_resolve_config_missingPat_raisesClearError(self):
        args = argparse.Namespace(
            org="org",
            project="project",
            team=None,
            work_item_type=None,
            states=None,
            area_path=None,
            output="azure_devops_user_stories.md",
            dry_run=False,
            verbose=False,
        )

        with self.assertRaises(MissingPATError) as context:
            resolve_config(args, env={})

        self.assertIn("AZURE_DEVOPS_PAT", str(context.exception))

    def test_wiqlUrl_withoutTeam_usesProjectEndpoint(self):
        config = AzureDevOpsConfig(
            org="my org",
            project="my project",
            team=None,
            pat="pat",
            work_item_type="User Story",
            states=None,
            area_path=None,
        )

        url = wiql_url(config)

        self.assertEqual(
            "https://dev.azure.com/my%20org/my%20project/_apis/wit/wiql?api-version=7.1",
            url,
        )

    def test_buildWiql_withoutStates_excludesRemovedAndSupportsAreaPath(self):
        config = AzureDevOpsConfig(
            org="org",
            project="project",
            team="team",
            pat="pat",
            work_item_type="User Story",
            states=None,
            area_path="Main Area",
        )

        wiql = build_wiql(config)

        self.assertIn("[System.State] <> 'Removed'", wiql)
        self.assertIn("[System.AreaPath] UNDER 'Main Area'", wiql)
        self.assertIn("ORDER BY [System.Id] ASC", wiql)

    @patch("scripts.azure_devops_to_md.requests.post")
    def test_fetchWorkItems_batchesInChunksOf200(self, post_mock):
        config = AzureDevOpsConfig(
            org="org",
            project="project",
            team=None,
            pat="pat",
            work_item_type="User Story",
            states=None,
            area_path=None,
        )

        first_response = Mock()
        first_response.raise_for_status = Mock()
        first_response.json.return_value = {
            "value": [{"id": 2, "fields": {"System.Title": "Second"}}]
        }

        second_response = Mock()
        second_response.raise_for_status = Mock()
        second_response.json.return_value = {
            "value": [{"id": 1, "fields": {"System.Title": "First"}}]
        }

        post_mock.side_effect = [first_response, second_response]

        ids = list(range(1, 202))
        work_items = fetch_work_items(config, ids)

        self.assertEqual(2, post_mock.call_count)
        first_call_ids = post_mock.call_args_list[0].kwargs["json"]["ids"]
        second_call_ids = post_mock.call_args_list[1].kwargs["json"]["ids"]
        self.assertEqual(200, len(first_call_ids))
        self.assertEqual(1, len(second_call_ids))
        self.assertEqual([1, 2], [item["id"] for item in work_items])

    def test_renderMarkdown_outputsExpectedSections(self):
        work_items = [
            {
                "id": 101,
                "fields": {
                    "System.Title": "Login",
                    "System.State": "Active",
                    "Microsoft.VSTS.Common.Priority": 1,
                    "System.AssignedTo": {"displayName": "Alice"},
                    "System.Description": "<p>User signs in</p>",
                    "Microsoft.VSTS.Common.AcceptanceCriteria": "<ul><li>Valid login</li></ul>",
                    "System.Tags": "Auth;Regression",
                    "System.AreaPath": "Area",
                    "System.IterationPath": "Iteration",
                },
            }
        ]

        markdown = render_markdown(work_items, org="org", project="project")

        self.assertIn("| Story ID | Title | State | Priority | Assigned To |", markdown)
        self.assertIn("## US-101 — Login", markdown)
        self.assertIn("### Description", markdown)
        self.assertIn("### Acceptance Criteria", markdown)
        self.assertIn("[Open in ADO](https://dev.azure.com/org/project/_workitems/edit/101)", markdown)


if __name__ == "__main__":
    unittest.main()
