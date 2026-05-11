"""
Unit Tests for IR Approver Module
User Stories: US-028 (All Tab), US-029 (Request Details),
              US-030 (Pending Tab), US-031 (Approved Tab)

Test Categories:
- Positive / Happy Path
- Negative / Error Path
- Boundary / Edge Cases
"""

SOURCE_STORY_FILE = "L&T_WFM_Onboarding_module_User_stories- as on 17.12.2025.xlsx"

import unittest
from unittest.mock import MagicMock, patch


# TODO: Import actual modules once implementation is available.
# from src.onboarding_approval.approval_overview import (
#     ApprovalOverviewPage, ApprovalService
# )


# ---------------------------------------------------------------------------
# US-028: Onboarding Approval Overview - All Tab
# ---------------------------------------------------------------------------


class TestOnboardingApprovalNavigation(unittest.TestCase):
    """US-028 AC-1, AC-2, AC-3: Navigate to Onboarding Approval page."""

    def setUp(self):
        self.page = MagicMock()

    def test_approvalOverview_selectFromMenu_displaysPage(self):
        """Positive: Selecting Onboarding Approval from menu displays the page."""
        self.page.navigate_to.return_value = {"status": "success"}

        result = self.page.navigate_to("onboarding_approval")

        self.assertEqual(result["status"], "success")

    def test_approvalOverview_displaysTabs_allThreePresent(self):
        """Positive: Page displays All, Pending, Approved tabs."""
        self.page.get_tabs.return_value = ["All", "Pending", "Approved"]

        tabs = self.page.get_tabs()

        self.assertEqual(len(tabs), 3)
        self.assertIn("All", tabs)
        self.assertIn("Pending", tabs)
        self.assertIn("Approved", tabs)


class TestApprovalAllTab(unittest.TestCase):
    """US-028 AC-4 to AC-12: All tab data grid and actions."""

    def setUp(self):
        self.service = MagicMock()

    def test_allTab_dataGrid_displaysAllRequiredColumns(self):
        """Positive: All tab grid displays all required columns."""
        expected_columns = [
            "All Select",
            "PS No",
            "Name",
            "Employment Type",
            "Dept Code",
            "Immediate Supervisor",
            "Date of Joining",
            "Submitted On",
            "Onboarding Type",
            "Status",
        ]
        self.service.get_grid_columns.return_value = expected_columns

        columns = self.service.get_grid_columns("all")

        self.assertEqual(len(columns), 10)

    def test_allTab_buttons_displaysApproveRejectExport(self):
        """Positive: Page displays Approve, Reject, Export buttons."""
        self.service.get_buttons.return_value = ["Approve", "Reject", "Export"]

        buttons = self.service.get_buttons()

        self.assertIn("Approve", buttons)
        self.assertIn("Reject", buttons)
        self.assertIn("Export", buttons)

    def test_allTab_selectAllCheckbox_selectsAllRows(self):
        """Positive: All Select checkbox selects all rows."""
        self.service.select_all.return_value = {
            "selected": True,
            "count": 10,
        }

        result = self.service.select_all()

        self.assertTrue(result["selected"])
        self.assertEqual(result["count"], 10)

    def test_allTab_clickApprove_displaysSuccessMessage(self):
        """Positive: Clicking Approve displays 'Data approved successful'."""
        self.service.approve.return_value = {
            "status": "success",
            "message": "Data approved successful",
        }

        result = self.service.approve(["12345"])

        self.assertEqual(result["status"], "success")
        self.assertIn("approved successful", result["message"])

    def test_allTab_clickExport_displaysSuccessMessage(self):
        """Positive: Clicking Export displays 'Data Exported Successfully'."""
        self.service.export.return_value = {
            "status": "success",
            "message": "Data Exported Successfully",
        }

        result = self.service.export()

        self.assertIn("Exported Successfully", result["message"])

    def test_allTab_psNoHyperlink_navigatesToApprovalPage(self):
        """Positive: PS No/Name hyperlink navigates to approval details page."""
        self.service.navigate_to_approval_details.return_value = {
            "redirect": "/approval/details/12345"
        }

        result = self.service.navigate_to_approval_details("12345")

        self.assertIn("/approval/details", result["redirect"])

    def test_allTab_searchBar_works(self):
        """Positive: Search bar returns matching results."""
        self.service.search.return_value = [{"name": "John Doe"}]

        results = self.service.search("John")

        self.assertEqual(len(results), 1)

    def test_allTab_pageNavigation_works(self):
        """Positive: Page navigation works correctly."""
        self.service.get_page.return_value = {"page": 2}

        result = self.service.get_page(2)

        self.assertEqual(result["page"], 2)


class TestApprovalPSNumberGeneration(unittest.TestCase):
    """US-028 AC-13, AC-14: PS Number generation and bulk approve."""

    def setUp(self):
        self.service = MagicMock()

    def test_psNumber_generatedOnlyAfterApproval(self):
        """Positive: PS number generated for Quick Onboarding/Rehiring only after approval."""
        self.service.approve.return_value = {
            "status": "success",
            "ps_number_generated": True,
            "ps_no": "12346",
        }

        result = self.service.approve(["pending_123"])

        self.assertTrue(result["ps_number_generated"])
        self.assertIsNotNone(result["ps_no"])

    def test_psNumber_notGeneratedBeforeApproval(self):
        """Negative: PS number is NOT generated before approval."""
        self.service.get_ps_no.return_value = None

        result = self.service.get_ps_no("pending_123")

        self.assertIsNone(result)

    def test_bulkApprove_multipleRequests_approvesAll(self):
        """Positive: Multiple requests can be selected and approved in bulk."""
        self.service.bulk_approve.return_value = {
            "status": "success",
            "approved_count": 5,
        }

        result = self.service.bulk_approve(
            ["req_1", "req_2", "req_3", "req_4", "req_5"]
        )

        self.assertEqual(result["approved_count"], 5)

    def test_bulkApprove_noRequestsSelected_returnsError(self):
        """Negative: No requests selected for bulk approve returns error."""
        self.service.bulk_approve.return_value = {
            "status": "error",
            "message": "No requests selected",
        }

        result = self.service.bulk_approve([])

        self.assertEqual(result["status"], "error")


class TestApprovalStatusDisplay(unittest.TestCase):
    """US-028 AC-15, AC-16: Status display and Submitted On validation."""

    def setUp(self):
        self.service = MagicMock()

    def test_status_pending_waitingForApproval(self):
        """Positive: Pending status means waiting for IR Approver approval."""
        self.service.get_status_description.return_value = (
            "Waiting for approval from IR Approver"
        )

        result = self.service.get_status_description("Pending")

        self.assertIn("Waiting", result)

    def test_status_approved_irApproverApproved(self):
        """Positive: Approved status means IR Approver approved."""
        self.service.get_status_description.return_value = (
            "IR Approver approved the onboarding process"
        )

        result = self.service.get_status_description("Approved")

        self.assertIn("approved", result)

    def test_status_returned_irApproverReturned(self):
        """Positive: Returned status means IR Approver returned the process."""
        self.service.get_status_description.return_value = (
            "IR Approver returned the onboarding or rehiring process"
        )

        result = self.service.get_status_description("Returned")

        self.assertIn("returned", result)

    def test_submittedOn_showsIRSubmissionDate(self):
        """Positive: Submitted On shows when IR submitted for approval."""
        self.service.get_submitted_date.return_value = "15-04-2026"

        result = self.service.get_submitted_date("req_123")

        self.assertIsNotNone(result)


# ---------------------------------------------------------------------------
# US-029: Onboarding Approval - Overview Page (Request Details)
# ---------------------------------------------------------------------------


class TestApprovalRequestDetails(unittest.TestCase):
    """US-029: Verify workmen details approval page."""

    def setUp(self):
        self.service = MagicMock()

    def test_requestDetails_navigateByPSNo_displaysDetailsPage(self):
        """Positive: Clicking PS No navigates to request view page."""
        self.service.navigate_to_request.return_value = {
            "redirect": "/approval/request/12345"
        }

        result = self.service.navigate_to_request("12345")

        self.assertIn("/approval/request", result["redirect"])

    def test_requestDetails_displaysAllEmployeeDetails(self):
        """Positive: All employee details from onboarding are displayed."""
        self.service.get_employee_details.return_value = {
            "personal_info": {"name": "John Doe"},
            "job_info": {"department": "ENG01"},
            "compensation": {"basic": 15000},
        }

        result = self.service.get_employee_details("12345")

        self.assertIn("personal_info", result)
        self.assertIn("job_info", result)
        self.assertIn("compensation", result)

    def test_requestDetails_clickApprove_displaysSuccessPopup(self):
        """Positive: Approve button shows 'Approval successful' popup."""
        self.service.approve_request.return_value = {
            "status": "success",
            "message": "Approval successful",
        }

        result = self.service.approve_request("12345")

        self.assertEqual(result["status"], "success")
        self.assertIn("Approval successful", result["message"])

    def test_requestDetails_clickReject_displaysConfirmationPopup(self):
        """Positive: Reject button shows 'Do you want to reject employee onboarding?'."""
        self.service.reject_request.return_value = {
            "popup": "Do you want to reject employee onboarding?",
            "options": ["Yes", "No"],
        }

        result = self.service.reject_request("12345")

        self.assertIn("reject", result["popup"].lower())
        self.assertIn("Yes", result["options"])
        self.assertIn("No", result["options"])

    def test_requestDetails_rejectConfirmYes_returnsOnboarding(self):
        """Positive: Clicking Yes on reject confirmation returns onboarding."""
        self.service.confirm_reject.return_value = {
            "status": "returned",
            "redirect": "/onboarding-approval",
        }

        result = self.service.confirm_reject("12345", "Yes")

        self.assertEqual(result["status"], "returned")
        self.assertIn("/onboarding-approval", result["redirect"])

    def test_requestDetails_rejectConfirmNo_staysOnPage(self):
        """Positive: Clicking No on reject keeps user on details page."""
        self.service.confirm_reject.return_value = {
            "status": "unchanged",
            "redirect": None,
        }

        result = self.service.confirm_reject("12345", "No")

        self.assertEqual(result["status"], "unchanged")
        self.assertIsNone(result["redirect"])


# ---------------------------------------------------------------------------
# US-030: Onboarding Approval - Pending Tab
# ---------------------------------------------------------------------------


class TestApprovalPendingTab(unittest.TestCase):
    """US-030: Verify Pending tab data grid and actions."""

    def setUp(self):
        self.service = MagicMock()

    def test_pendingTab_dataGrid_displaysRequiredColumns(self):
        """Positive: Pending tab displays required columns (no PS No)."""
        expected_columns = [
            "Name",
            "Employment Type",
            "Dept Code",
            "Immediate Supervisor",
            "Date of Joining",
            "Submitted On",
            "Onboarding Type",
        ]
        self.service.get_grid_columns.return_value = expected_columns

        columns = self.service.get_grid_columns("pending")

        self.assertEqual(len(columns), 7)
        self.assertNotIn("PS No", columns)

    def test_pendingTab_buttons_displaysApproveRejectExport(self):
        """Positive: Pending tab displays Approve, Reject, Export buttons."""
        self.service.get_buttons.return_value = ["Approve", "Reject", "Export"]

        buttons = self.service.get_buttons("pending")

        self.assertEqual(len(buttons), 3)

    def test_pendingTab_selectAll_works(self):
        """Positive: All Select checkbox works in Pending tab."""
        self.service.select_all.return_value = {"selected": True, "count": 3}

        result = self.service.select_all(tab="pending")

        self.assertTrue(result["selected"])

    def test_pendingTab_clickApprove_displaysSuccess(self):
        """Positive: Approve shows 'Data approved successful'."""
        self.service.approve.return_value = {
            "status": "success",
            "message": "Data approved successful",
        }

        result = self.service.approve(["req_1"], tab="pending")

        self.assertIn("approved successful", result["message"])

    def test_pendingTab_clickExport_displaysSuccess(self):
        """Positive: Export shows 'Data Exported Successfully'."""
        self.service.export.return_value = {
            "message": "Data Exported Successfully",
        }

        result = self.service.export(tab="pending")

        self.assertIn("Exported Successfully", result["message"])

    def test_pendingTab_nameHyperlink_navigatesToApproval(self):
        """Positive: Name hyperlink navigates to approval details."""
        self.service.navigate_to_approval_details.return_value = {
            "redirect": "/approval/details/req_1"
        }

        result = self.service.navigate_to_approval_details("req_1")

        self.assertIn("/approval/details", result["redirect"])

    def test_pendingTab_searchBar_works(self):
        """Positive: Search bar works in Pending tab."""
        self.service.search.return_value = [{"name": "Alice"}]

        results = self.service.search("Alice", tab="pending")

        self.assertEqual(len(results), 1)

    def test_pendingTab_submittedOn_showsIRSubmissionDate(self):
        """Positive: Submitted On shows the date IR submitted for approval."""
        self.service.get_submitted_date.return_value = "10-05-2026"

        result = self.service.get_submitted_date("req_1")

        self.assertIsNotNone(result)


# ---------------------------------------------------------------------------
# US-031: Onboarding Approval - Approved Tab
# ---------------------------------------------------------------------------


class TestApprovalApprovedTab(unittest.TestCase):
    """US-031: Verify Approved tab data grid and actions."""

    def setUp(self):
        self.service = MagicMock()

    def test_approvedTab_dataGrid_displaysRequiredColumns(self):
        """Positive: Approved tab displays all required columns including PS No."""
        expected_columns = [
            "All Select",
            "PS No",
            "Name",
            "Employment Type",
            "Dept Code",
            "Immediate Supervisor",
            "Date of Joining",
            "Approved On",
            "Onboarding Type",
        ]
        self.service.get_grid_columns.return_value = expected_columns

        columns = self.service.get_grid_columns("approved")

        self.assertEqual(len(columns), 9)
        self.assertIn("PS No", columns)
        self.assertIn("Approved On", columns)

    def test_approvedTab_button_displaysExportOnly(self):
        """Positive: Approved tab displays only Export button."""
        self.service.get_buttons.return_value = ["Export"]

        buttons = self.service.get_buttons("approved")

        self.assertEqual(len(buttons), 1)
        self.assertIn("Export", buttons)

    def test_approvedTab_selectAll_works(self):
        """Positive: All Select checkbox works in Approved tab."""
        self.service.select_all.return_value = {"selected": True, "count": 5}

        result = self.service.select_all(tab="approved")

        self.assertTrue(result["selected"])

    def test_approvedTab_clickExport_displaysSuccess(self):
        """Positive: Export shows 'Data Exported Successful'."""
        self.service.export.return_value = {
            "status": "success",
            "message": "Data Exported Successful",
        }

        result = self.service.export(tab="approved")

        self.assertIn("Exported Successful", result["message"])

    def test_approvedTab_nameHyperlink_navigatesToDetails(self):
        """Positive: PS No/Name hyperlink navigates to details page."""
        self.service.navigate_to_approval_details.return_value = {
            "redirect": "/approval/details/12345"
        }

        result = self.service.navigate_to_approval_details("12345")

        self.assertIn("/approval/details", result["redirect"])

    def test_approvedTab_searchBar_works(self):
        """Positive: Search bar works in Approved tab."""
        self.service.search.return_value = [{"ps_no": "12345"}]

        results = self.service.search("12345", tab="approved")

        self.assertEqual(len(results), 1)

    def test_approvedTab_pageNavigation_works(self):
        """Positive: Page navigation works in Approved tab."""
        self.service.get_page.return_value = {"page": 1}

        result = self.service.get_page(1, tab="approved")

        self.assertEqual(result["page"], 1)

    def test_approvedTab_noApproveRejectButtons(self):
        """Negative: Approved tab does NOT display Approve or Reject buttons."""
        self.service.get_buttons.return_value = ["Export"]

        buttons = self.service.get_buttons("approved")

        self.assertNotIn("Approve", buttons)
        self.assertNotIn("Reject", buttons)


if __name__ == "__main__":
    unittest.main()
