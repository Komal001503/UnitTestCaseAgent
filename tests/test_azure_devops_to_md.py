import argparse
from datetime import date
import unittest
from unittest.mock import Mock, patch

from scripts.azure_devops_to_md import (
    AzureDevOpsConfig,
    MissingPATError,
    _csv_to_int_list,
    _filter_to_type,
    _is_team_not_found_error,
    build_wiql,
    fetch_work_items,
    query_work_item_ids,
    render_markdown,
    resolve_backlog_area_paths,
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
            pat="pat",
            work_item_type="User Story",
            team="team",
            states=None,
            area_path="Main Area",
        )

        wiql = build_wiql(config)

        self.assertIn("[System.State] <> 'Removed'", wiql)
        self.assertIn("[System.AreaPath] UNDER 'Main Area'", wiql)
        self.assertIn("ORDER BY [System.Id] ASC", wiql)

    def test_buildWiql_appendsAllNewOptionalFilters(self):
        config = AzureDevOpsConfig(
            org="org",
            project="project",
            pat="pat",
            work_item_type="User Story",
            iteration_path="Project\\Sprint 12",
            assigned_to="O'Connor",
            tags=["API", "Regression"],
            ids=[1234, 1240, 1255],
            from_date=date(2025, 10, 1),
            to_date=date(2025, 12, 31),
            date_field="CreatedDate",
        )

        wiql = build_wiql(config)

        self.assertIn("[System.IterationPath] UNDER 'Project\\Sprint 12'", wiql)
        self.assertIn("[System.AssignedTo] CONTAINS 'O''Connor'", wiql)
        self.assertIn("[System.Tags] CONTAINS 'API'", wiql)
        self.assertIn("[System.Tags] CONTAINS 'Regression'", wiql)
        self.assertIn("[System.Id] IN (1234, 1240, 1255)", wiql)
        self.assertIn("[System.CreatedDate] >= '2025-10-01'", wiql)
        self.assertIn("[System.CreatedDate] <= '2025-12-31T23:59:59'", wiql)
        self.assertIn("[System.CreatedDate]", wiql)
        self.assertIn("[System.ChangedDate]", wiql)

    def test_buildWiql_withoutOptionalFilters_omitsNewClauses(self):
        config = AzureDevOpsConfig(
            org="org",
            project="project",
            pat="pat",
            work_item_type="User Story",
        )

        wiql = build_wiql(config)

        self.assertNotIn("[System.IterationPath] UNDER", wiql)
        self.assertNotIn("[System.AssignedTo] CONTAINS", wiql)
        self.assertNotIn("[System.Tags] CONTAINS", wiql)
        self.assertNotIn("[System.Id] IN", wiql)
        self.assertNotIn("T23:59:59", wiql)
        self.assertNotIn("[System.ChangedDate] >=", wiql)
        self.assertNotIn("[System.ChangedDate] <=", wiql)
        self.assertNotIn("[System.CreatedDate] >=", wiql)
        self.assertNotIn("[System.CreatedDate] <=", wiql)

    def test_buildWiql_backlogAreaPaths_appendsOrredAreaPathClause(self):
        config = AzureDevOpsConfig(
            org="org",
            project="project",
            pat="pat",
            work_item_type="User Story",
            area_path=None,
        )

        wiql = build_wiql(config, backlog_area_paths=["A\\B", "A\\C"])

        self.assertIn(
            "AND ([System.AreaPath] UNDER 'A\\B' OR [System.AreaPath] UNDER 'A\\C')",
            wiql,
        )

    def test_buildWiql_areaPathTakesPrecedenceOverBacklog(self):
        config = AzureDevOpsConfig(
            org="org",
            project="project",
            pat="pat",
            work_item_type="User Story",
            area_path="Explicit\\Area",
            backlog="Feature Team 1",
        )

        wiql = build_wiql(config, backlog_area_paths=["A\\B", "A\\C"])

        self.assertIn("[System.AreaPath] UNDER 'Explicit\\Area'", wiql)
        self.assertNotIn("[System.AreaPath] UNDER 'A\\B'", wiql)
        self.assertNotIn("[System.AreaPath] UNDER 'A\\C'", wiql)

    def test_buildWiql_assigneeEmail_usesContainsForIdentityMatch(self):
        config = AzureDevOpsConfig(
            org="org",
            project="project",
            pat="pat",
            work_item_type="User Story",
            assigned_to="Utkarsh.Brahmapurikar@larsentoubro.com",
        )

        wiql = build_wiql(config)

        self.assertIn(
            "[System.AssignedTo] CONTAINS 'Utkarsh.Brahmapurikar@larsentoubro.com'",
            wiql,
        )
        self.assertNotIn("[System.AssignedTo] =", wiql)

    def test_buildWiql_noneDateFieldWithoutDates_omitsDateClauses(self):
        config = AzureDevOpsConfig(
            org="org",
            project="project",
            pat="pat",
            work_item_type="User Story",
            date_field=None,
        )

        wiql = build_wiql(config)

        self.assertNotIn("[System.ChangedDate] >=", wiql)
        self.assertNotIn("[System.ChangedDate] <=", wiql)
        self.assertNotIn("[System.CreatedDate] >=", wiql)
        self.assertNotIn("[System.CreatedDate] <=", wiql)

    def test_buildWiql_noneDateFieldWithDates_fallsBackToChangedDate(self):
        config = AzureDevOpsConfig(
            org="org",
            project="project",
            pat="pat",
            work_item_type="User Story",
            from_date=date(2025, 11, 1),
            to_date=date(2025, 11, 30),
            date_field=None,
        )

        wiql = build_wiql(config)

        self.assertIn("[System.ChangedDate] >= '2025-11-01'", wiql)
        self.assertIn("[System.ChangedDate] <= '2025-11-30T23:59:59'", wiql)
        self.assertNotIn("[System.CreatedDate] >= '2025-11-01'", wiql)
        self.assertNotIn("[System.CreatedDate] <= '2025-11-30T23:59:59'", wiql)

    def test_buildWiql_changedDateWithoutDates_omitsDateClauses(self):
        config = AzureDevOpsConfig(
            org="org",
            project="project",
            pat="pat",
            work_item_type="User Story",
            date_field="ChangedDate",
        )

        wiql = build_wiql(config)

        self.assertNotIn("[System.ChangedDate] >=", wiql)
        self.assertNotIn("[System.ChangedDate] <=", wiql)
        self.assertNotIn("[System.CreatedDate] >=", wiql)
        self.assertNotIn("[System.CreatedDate] <=", wiql)

    def test_resolveConfig_invalidFromDate_raisesValueError(self):
        args = argparse.Namespace(
            org="org",
            project="project",
            team=None,
            work_item_type="User Story",
            states=None,
            area_path=None,
            from_date="2025/11/01",
            to_date=None,
            date_field=None,
            output="out.md",
            dry_run=False,
            verbose=False,
        )

        with self.assertRaises(ValueError) as context:
            resolve_config(args, env={"AZURE_DEVOPS_PAT": "pat"})

        self.assertEqual("Invalid date '2025/11/01': expected YYYY-MM-DD", str(context.exception))

    def test_resolveConfig_fromDateAfterToDate_raisesValueError(self):
        args = argparse.Namespace(
            org="org",
            project="project",
            team=None,
            work_item_type="User Story",
            states=None,
            area_path=None,
            from_date="2025-12-31",
            to_date="2025-01-01",
            date_field="ChangedDate",
            output="out.md",
            dry_run=False,
            verbose=False,
        )

        with self.assertRaises(ValueError) as context:
            resolve_config(args, env={"AZURE_DEVOPS_PAT": "pat"})

        self.assertIn("Invalid date range", str(context.exception))

    def test_resolveConfig_blankDatesAndNoneDateField_areTreatedAsMissing(self):
        args = argparse.Namespace(
            org="org",
            project="project",
            team=None,
            work_item_type="User Story",
            states=None,
            area_path=None,
            from_date=None,
            to_date=None,
            date_field=None,
            output="out.md",
            dry_run=False,
            verbose=False,
        )

        config = resolve_config(
            args,
            env={
                "AZURE_DEVOPS_PAT": "pat",
                "AZURE_DEVOPS_FROM_DATE": "   ",
                "AZURE_DEVOPS_TO_DATE": "",
                "AZURE_DEVOPS_DATE_FIELD": " None ",
            },
        )

        self.assertIsNone(config.from_date)
        self.assertIsNone(config.to_date)
        self.assertIsNone(config.date_field)

    def test_resolveConfig_blankOptionalScopeFilters_areTreatedAsMissing(self):
        args = argparse.Namespace(
            org="org",
            project="project",
            team=None,
            work_item_type="User Story",
            states=None,
            area_path=None,
            backlog=None,
            iteration_path=None,
            assigned_to=None,
            tags=None,
            ids=None,
            from_date=None,
            to_date=None,
            date_field=None,
            output="out.md",
            dry_run=False,
            verbose=False,
        )

        config = resolve_config(
            args,
            env={
                "AZURE_DEVOPS_PAT": "pat",
                "AZURE_DEVOPS_TEAM": "   ",
                "AZURE_DEVOPS_AREA_PATH": "",
                "AZURE_DEVOPS_BACKLOG": "  ",
                "AZURE_DEVOPS_ITERATION_PATH": " ",
                "AZURE_DEVOPS_ASSIGNED_TO": "   ",
            },
        )

        self.assertIsNone(config.team)
        self.assertIsNone(config.area_path)
        self.assertIsNone(config.backlog)
        self.assertIsNone(config.iteration_path)
        self.assertIsNone(config.assigned_to)

    def test_resolveConfig_dateField_isNormalized_caseInsensitively(self):
        args = argparse.Namespace(
            org="org",
            project="project",
            team=None,
            work_item_type="User Story",
            states=None,
            area_path=None,
            from_date="2025-11-01",
            to_date=None,
            date_field=None,
            output="out.md",
            dry_run=False,
            verbose=False,
        )

        config = resolve_config(
            args,
            env={
                "AZURE_DEVOPS_PAT": "pat",
                "AZURE_DEVOPS_DATE_FIELD": "createddate",
            },
        )

        self.assertEqual("CreatedDate", config.date_field)

    def test_csvToIntList_toleratesWhitespaceAndDropsNonIntegers(self):
        ids = _csv_to_int_list(" 1234, xyz, 1240, ,12a,1255 ")

        self.assertEqual([1234, 1240, 1255], ids)

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
                    "System.WorkItemType": "User Story",
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

    def test_buildWiql_includesWorkItemTypeInSelect(self):
        config = AzureDevOpsConfig(
            org="org",
            project="project",
            team=None,
            pat="pat",
            work_item_type="User Story",
            states=None,
            area_path=None,
        )

        wiql = build_wiql(config)

        self.assertIn("[System.WorkItemType]", wiql)
        # Should appear in both SELECT and WHERE
        self.assertGreaterEqual(wiql.count("[System.WorkItemType]"), 2)

    def test_buildWiql_whereClauseFiltersWorkItemType(self):
        config = AzureDevOpsConfig(
            org="org",
            project="project",
            team=None,
            pat="pat",
            work_item_type="Product Backlog Item",
            states=None,
            area_path=None,
        )

        wiql = build_wiql(config)

        self.assertIn("[System.WorkItemType] = 'Product Backlog Item'", wiql)

    def test_filterToType_keepsMatchingItems(self):
        work_items = [
            {"id": 1, "fields": {"System.WorkItemType": "User Story"}},
            {"id": 2, "fields": {"System.WorkItemType": "Bug"}},
            {"id": 3, "fields": {"System.WorkItemType": "User Story"}},
            {"id": 4, "fields": {"System.WorkItemType": "Task"}},
            {"id": 5, "fields": {"System.WorkItemType": "Feature"}},
        ]

        result = _filter_to_type(work_items, "User Story")

        self.assertEqual([1, 3], [item["id"] for item in result])

    def test_filterToType_caseInsensitiveAndTrimsWhitespace(self):
        work_items = [
            {"id": 1, "fields": {"System.WorkItemType": "  user story  "}},
            {"id": 2, "fields": {"System.WorkItemType": "USER STORY"}},
            {"id": 3, "fields": {"System.WorkItemType": "Bug"}},
        ]

        result = _filter_to_type(work_items, "User Story")

        self.assertEqual([1, 2], [item["id"] for item in result])

    def test_filterToType_allMatchNoWarning(self):
        work_items = [
            {"id": 1, "fields": {"System.WorkItemType": "User Story"}},
            {"id": 2, "fields": {"System.WorkItemType": "User Story"}},
        ]

        result = _filter_to_type(work_items, "User Story")

        self.assertEqual(2, len(result))

    def test_filterToType_warnsWhenItemsDropped(self):
        import io
        import sys

        work_items = [
            {"id": 1, "fields": {"System.WorkItemType": "User Story"}},
            {"id": 2, "fields": {"System.WorkItemType": "Bug"}},
            {"id": 3, "fields": {"System.WorkItemType": "Bug"}},
            {"id": 4, "fields": {"System.WorkItemType": "Task"}},
        ]

        captured = io.StringIO()
        old_stderr = sys.stderr
        sys.stderr = captured
        try:
            result = _filter_to_type(work_items, "User Story")
        finally:
            sys.stderr = old_stderr

        warning = captured.getvalue()
        self.assertIn("dropped 3 work item(s)", warning)
        self.assertIn("Bug=2", warning)
        self.assertIn("Task=1", warning)
        self.assertEqual(1, len(result))

    def test_renderMarkdown_includesWorkItemTypeRow(self):
        work_items = [
            {
                "id": 42,
                "fields": {
                    "System.Title": "My Story",
                    "System.WorkItemType": "User Story",
                    "System.State": "Active",
                    "Microsoft.VSTS.Common.Priority": 2,
                    "System.AssignedTo": None,
                    "System.Description": None,
                    "Microsoft.VSTS.Common.AcceptanceCriteria": None,
                    "System.Tags": "",
                    "System.AreaPath": "",
                    "System.IterationPath": "",
                },
            }
        ]

        markdown = render_markdown(work_items, org="org", project="proj", work_item_type="User Story")

        self.assertIn("| Work Item Type | User Story |", markdown)

    def test_renderMarkdown_includesTopLevelFilterNote(self):
        work_items = [
            {
                "id": 10,
                "fields": {
                    "System.Title": "Story",
                    "System.WorkItemType": "User Story",
                    "System.State": "Active",
                    "Microsoft.VSTS.Common.Priority": 1,
                    "System.AssignedTo": None,
                    "System.Description": None,
                    "Microsoft.VSTS.Common.AcceptanceCriteria": None,
                    "System.Tags": "",
                    "System.AreaPath": "",
                    "System.IterationPath": "",
                },
            }
        ]

        markdown = render_markdown(
            work_items,
            org="org",
            project="proj",
            work_item_type="User Story",
            iteration_path="Proj\\Sprint 1",
            ids=[10],
            from_date=date(2025, 11, 1),
            to_date=date(2025, 11, 30),
            date_field="ChangedDate",
        )

        self.assertIn(
            "_Filters: type=User Story · iteration=Proj\\Sprint 1 · ids=10 · changed between 2025-11-01 and 2025-11-30._",
            markdown,
        )

    def test_renderMarkdown_filterNote_onlyIncludesAppliedParts(self):
        work_items: list = []

        markdown = render_markdown(work_items, org="org", project="proj")

        self.assertIn("_Filters: type=User Story._", markdown)

    def test_renderMarkdown_backlogAppearsInFilterBanner(self):
        markdown = render_markdown(
            work_items=[],
            org="org",
            project="proj",
            backlog="IEMQS-SAP-Integration",
        )

        self.assertIn("backlog=IEMQS-SAP-Integration", markdown)

    def test_renderMarkdown_noneDateFieldWithoutDates_omitsDateFilterNote(self):
        markdown = render_markdown(work_items=[], org="org", project="proj", date_field=None)

        self.assertIn("_Filters: type=User Story._", markdown)
        self.assertNotIn("changed ", markdown)
        self.assertNotIn("created ", markdown)

    def test_renderMarkdown_noneDateFieldWithDates_usesChangedDateInFilterNote(self):
        markdown = render_markdown(
            work_items=[],
            org="org",
            project="proj",
            from_date=date(2025, 11, 1),
            to_date=date(2025, 11, 30),
            date_field=None,
        )

        self.assertIn(
            "_Filters: type=User Story · changed between 2025-11-01 and 2025-11-30._",
            markdown,
        )

    def test_renderMarkdown_changedDateWithoutDates_omitsDateFilterNote(self):
        markdown = render_markdown(work_items=[], org="org", project="proj", date_field="ChangedDate")

        self.assertIn("_Filters: type=User Story._", markdown)
        self.assertNotIn("changed ", markdown)
        self.assertNotIn("created ", markdown)

    def test_renderMarkdown_includesCreatedAndChangedDateRows(self):
        work_items: list = []
        work_items.append(
            {
                "id": 500,
                "fields": {
                    "System.Title": "Story",
                    "System.WorkItemType": "User Story",
                    "System.State": "Active",
                    "Microsoft.VSTS.Common.Priority": 1,
                    "System.AssignedTo": None,
                    "System.Description": None,
                    "Microsoft.VSTS.Common.AcceptanceCriteria": None,
                    "System.Tags": "",
                    "System.AreaPath": "",
                    "System.IterationPath": "",
                    "System.ChangedDate": "2025-11-30T10:15:00Z",
                    "System.CreatedDate": "2025-11-01T09:00:00Z",
                },
            }
        )

        markdown = render_markdown(work_items, org="org", project="proj", work_item_type="User Story")

        self.assertIn("| Changed Date | 2025-11-30T10:15:00Z |", markdown)
        self.assertIn("| Created Date | 2025-11-01T09:00:00Z |", markdown)


    def test_isTeamNotFoundError_returnsTrueForHttp500TeamNotFoundException(self):
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.json.return_value = {
            "$id": "1",
            "typeKey": "TeamNotFoundException",
            "message": "The team with id 'IEMQS 4.0' does not exist.",
        }

        self.assertTrue(_is_team_not_found_error(mock_response))

    def test_isTeamNotFoundError_returnsFalseForNon500(self):
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.json.return_value = {"typeKey": "TeamNotFoundException"}

        self.assertFalse(_is_team_not_found_error(mock_response))

    def test_isTeamNotFoundError_returnsFalseForDifferentTypeKey(self):
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.json.return_value = {"typeKey": "SomeOtherException"}

        self.assertFalse(_is_team_not_found_error(mock_response))

    def test_isTeamNotFoundError_returnsFalseForNonJsonBody(self):
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.json.side_effect = ValueError("not json")

        self.assertFalse(_is_team_not_found_error(mock_response))

    @patch("scripts.azure_devops_to_md.requests.get")
    def test_resolveBacklogAreaPaths_unknownTeam_raisesWithAvailableList(self, get_mock):
        config = AzureDevOpsConfig(
            org="org",
            project="IEMQS 4.0",
            pat="pat",
            work_item_type="User Story",
            backlog="IEMQS-SAP-Integrtaion",
        )

        teams_response = Mock()
        teams_response.status_code = 200
        teams_response.raise_for_status = Mock()
        teams_response.json.return_value = {
            "value": [
                {"name": "Common Backlog"},
                {"name": "Feature Team 1"},
                {"name": "Feature Team 2"},
                {"name": "Feature Team 3"},
                {"name": "GTM Execution Team"},
                {"name": "IEMQS-SAP-Integration"},
            ]
        }
        get_mock.return_value = teams_response

        with self.assertRaises(ValueError) as context:
            resolve_backlog_area_paths(config)

        message = str(context.exception)
        self.assertIn("Backlog/team 'IEMQS-SAP-Integrtaion' was not found", message)
        self.assertIn("Common Backlog", message)
        self.assertIn("Feature Team 1", message)
        self.assertIn("Feature Team 2", message)
        self.assertIn("Feature Team 3", message)
        self.assertIn("GTM Execution Team", message)
        self.assertIn("IEMQS-SAP-Integration", message)

    @patch("scripts.azure_devops_to_md.requests.get")
    def test_resolveBacklogAreaPaths_matchesCaseInsensitive(self, get_mock):
        config = AzureDevOpsConfig(
            org="org",
            project="IEMQS 4.0",
            pat="pat",
            work_item_type="User Story",
            backlog="iemqs-sap-integration",
        )

        teams_response = Mock()
        teams_response.status_code = 200
        teams_response.raise_for_status = Mock()
        teams_response.json.return_value = {
            "value": [
                {"id": "1111-2222", "name": "IEMQS-SAP-Integration"},
                {"id": "3333-4444", "name": "Feature Team 1"},
            ]
        }

        team_fields_response = Mock()
        team_fields_response.status_code = 200
        team_fields_response.raise_for_status = Mock()
        team_fields_response.json.return_value = {
            "values": [
                {"value": "IEMQS 4.0\\IEMQS-SAP-Integration", "includeChildren": True},
                {"value": "IEMQS 4.0\\IEMQS-SAP-Integration\\Sub", "includeChildren": True},
            ]
        }
        get_mock.side_effect = [teams_response, team_fields_response]

        result = resolve_backlog_area_paths(config)

        self.assertEqual(
            [
                "IEMQS 4.0\\IEMQS-SAP-Integration",
                "IEMQS 4.0\\IEMQS-SAP-Integration\\Sub",
            ],
            result,
        )

    @patch("scripts.azure_devops_to_md.requests.post")
    def test_queryWorkItemIds_retriesWithoutTeamOnTeamNotFoundException(self, post_mock):
        config = AzureDevOpsConfig(
            org="org",
            project="IEMQS 4.0",
            team="IEMQS 4.0",
            pat="pat",
            work_item_type="User Story",
        )

        team_not_found_response = Mock()
        team_not_found_response.status_code = 500
        team_not_found_response.json.return_value = {
            "typeKey": "TeamNotFoundException",
            "message": "The team with id 'IEMQS 4.0' does not exist.",
        }
        team_not_found_response.raise_for_status.side_effect = None

        fallback_response = Mock()
        fallback_response.status_code = 200
        fallback_response.raise_for_status = Mock()
        fallback_response.json.return_value = {
            "workItems": [{"id": 10}, {"id": 20}]
        }

        post_mock.side_effect = [team_not_found_response, fallback_response]

        ids = query_work_item_ids(config)

        self.assertEqual(2, post_mock.call_count)
        # First call uses team in URL
        first_url = post_mock.call_args_list[0].args[0]
        self.assertIn("IEMQS%204.0/IEMQS%204.0", first_url)
        # Retry call omits team from URL
        second_url = post_mock.call_args_list[1].args[0]
        self.assertNotIn("IEMQS%204.0/IEMQS%204.0", second_url)
        self.assertIn("IEMQS%204.0/_apis/wit/wiql", second_url)
        self.assertEqual([10, 20], ids)

    @patch("scripts.azure_devops_to_md.requests.post")
    def test_queryWorkItemIds_doesNotRetryWhenNoTeamSet(self, post_mock):
        config = AzureDevOpsConfig(
            org="org",
            project="project",
            team=None,
            pat="pat",
            work_item_type="User Story",
        )

        error_response = Mock()
        error_response.status_code = 500
        error_response.text = "internal error"
        error_response.raise_for_status.side_effect = __import__("requests").HTTPError(
            response=error_response
        )

        post_mock.return_value = error_response

        with self.assertRaises(RuntimeError):
            query_work_item_ids(config)

        self.assertEqual(1, post_mock.call_count)


if __name__ == "__main__":
    unittest.main()
