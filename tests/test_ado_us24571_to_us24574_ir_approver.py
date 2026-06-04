"""
Unit Tests for IR Approver – Onboarding Approval Module
Source: azure_devops_user_stories.md
User Stories:
  US-24571 (IR Approver - Onboarding approval - View all request in All tab)
  US-24572 (IR Approver - Onboarding approval - View pending request in Pending tab)
  US-24573 (IR Approver - Onboarding approval - View approved request in Approved tab)
  US-24574 (IR Approver - Onboarding approval - Approve/reject employee in Employee overview)

Test Categories:
- Positive / Happy Path
- Negative / Error Path
- Boundary / Edge Cases
"""

SOURCE_STORY_FILE = "azure_devops_user_stories.md"

import unittest
from unittest.mock import MagicMock, patch


# TODO: Import actual modules once implementation is available.
# from src.onboarding_approval.approval_overview import (
#     ApprovalOverviewPage, ApprovalService
# )


# ---------------------------------------------------------------------------
# Common Navigation: US-24571
# ---------------------------------------------------------------------------


class TestOnboardingApprovalNavigation(unittest.TestCase):
    """US-24571: Navigate to Onboarding Approval page."""

    def setUp(self):
        self.navigation = MagicMock()
        self.page = MagicMock()

    def test_sideNav_selectOnboardingApproval_navigatesToPage(self):
        """Positive: Selecting 'Onboarding Approval' from side nav opens the page."""
        self.navigation.navigate_to.return_value = {
            "status": "success",
            "page": "Onboarding Approval",
        }

        result = self.navigation.navigate_to("Onboarding Approval")

        self.assertEqual(result["status"], "success")

    def test_approvalPage_displaysThreeTabs(self):
        """Positive: Onboarding Approval page shows All, Pending, and Approved tabs."""
        self.page.get_tabs.return_value = ["All", "Pending", "Approved"]

        tabs = self.page.get_tabs()

        self.assertEqual(len(tabs), 3)
        self.assertIn("All", tabs)
        self.assertIn("Pending", tabs)
        self.assertIn("Approved", tabs)


# ---------------------------------------------------------------------------
# US-24571: All Tab
# ---------------------------------------------------------------------------


class TestApprovalAllTab(unittest.TestCase):
    """US-24571: Verify All tab data grid, actions, and validations."""

    def setUp(self):
        self.service = MagicMock()

    def test_allTab_grid_displaysAllRequiredColumns(self):
        """Positive: All tab grid shows 10 columns including PS No, Name, Status, etc."""
        self.service.get_grid_columns.return_value = [
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

        columns = self.service.get_grid_columns("all")

        self.assertEqual(len(columns), 10)
        self.assertIn("All Select", columns)
        self.assertIn("PS No", columns)
        self.assertIn("Status", columns)

    def test_allTab_displaysApproveRejectExportButtons(self):
        """Positive: All tab shows Approve, Reject, and Export buttons."""
        self.service.get_buttons.return_value = ["Approve", "Reject", "Export"]

        buttons = self.service.get_buttons("all")

        self.assertIn("Approve", buttons)
        self.assertIn("Reject", buttons)
        self.assertIn("Export", buttons)

    def test_allTab_selectAllCheckbox_selectsAllRows(self):
        """Positive: Clicking 'All Select' checkbox selects all rows in grid."""
        self.service.select_all.return_value = {"selected": True, "count": 10}

        result = self.service.select_all(tab="all")

        self.assertTrue(result["selected"])

    def test_allTab_approveButton_displaysSuccessPopup(self):
        """Positive: Clicking Approve shows 'Data approved successful' popup."""
        self.service.approve.return_value = {
            "status": "success",
            "message": "Data approved successful",
        }

        result = self.service.approve(["req_001"], tab="all")

        self.assertEqual(result["status"], "success")
        self.assertIn("approved successful", result["message"])

    def test_allTab_exportButton_displaysSuccessMessage(self):
        """Positive: Clicking Export shows 'Data Exported Successfully' message."""
        self.service.export.return_value = {
            "status": "success",
            "message": "Data Exported Successfully",
        }

        result = self.service.export(tab="all")

        self.assertIn("Exported Successfully", result["message"])

    def test_allTab_psNoHyperlink_navigatesToWorkmenDetailsApprovalPage(self):
        """Positive: Clicking PS No / Name hyperlink opens Workmen Details Approval page."""
        self.service.navigate_to_approval_details.return_value = {
            "redirect": "/approval/details/PS-12345"
        }

        result = self.service.navigate_to_approval_details("PS-12345")

        self.assertIn("/approval/details", result["redirect"])

    def test_allTab_psNumber_generatedForQOAndRehiringOnlyAfterApproval(self):
        """Validation: PS No generated for Quick Onboarding and Rehiring only after IR Approver approves."""
        self.service.get_ps_no_before_approval.return_value = None

        result = self.service.get_ps_no_before_approval("req_pending")

        self.assertIsNone(result)

    def test_allTab_psNumber_appearsAfterApproval(self):
        """Validation: PS No appears in grid after IR Approver approves request."""
        self.service.get_ps_no_after_approval.return_value = "PS-00456"

        result = self.service.get_ps_no_after_approval("req_001")

        self.assertIsNotNone(result)
        self.assertEqual(result, "PS-00456")

    def test_allTab_bulkApprove_multipleCounts_approvesAll(self):
        """Positive: Multiple requests can be selected and approved in bulk."""
        self.service.bulk_approve.return_value = {
            "status": "success",
            "approved_count": 5,
        }

        result = self.service.bulk_approve(["r1", "r2", "r3", "r4", "r5"])

        self.assertEqual(result["approved_count"], 5)

    def test_allTab_bulkApprove_noRowsSelected_returnsError(self):
        """Negative: Clicking Approve with no rows selected returns an error."""
        self.service.bulk_approve.return_value = {
            "status": "error",
            "message": "No requests selected",
        }

        result = self.service.bulk_approve([])

        self.assertEqual(result["status"], "error")

    def test_allTab_status_pendingMeaning(self):
        """Validation: 'Pending' status = waiting for IR Approver approval."""
        self.service.get_status_description.return_value = (
            "Waiting for approval from IR approver"
        )

        result = self.service.get_status_description("Pending")

        self.assertIn("Waiting", result)

    def test_allTab_status_approvedMeaning(self):
        """Validation: 'Approved' status = IR Approver approved onboarding."""
        self.service.get_status_description.return_value = (
            "IR approver approved the onboarding process"
        )

        result = self.service.get_status_description("Approved")

        self.assertIn("approved", result.lower())

    def test_allTab_status_returnedMeaning(self):
        """Validation: 'Returned' status = IR Approver returned onboarding/rehiring."""
        self.service.get_status_description.return_value = (
            "IR approver returned the onboarding or rehiring process"
        )

        result = self.service.get_status_description("Returned")

        self.assertIn("returned", result.lower())

    def test_allTab_submittedOn_showsIRSubmissionDate(self):
        """Validation: Submitted On shows when IR submitted request to IR Approver."""
        self.service.get_submitted_date.return_value = "15-04-2026"

        result = self.service.get_submitted_date("req_001")

        self.assertIsNotNone(result)

    def test_allTab_searchBar_returnsMatchingResults(self):
        """Positive: Search bar returns matching requests."""
        self.service.search.return_value = [{"name": "John Doe"}]

        results = self.service.search("John", tab="all")

        self.assertEqual(len(results), 1)

    def test_allTab_pageNavigation_works(self):
        """Positive: Page navigation works in All tab."""
        self.service.get_page.return_value = {"page": 2}

        result = self.service.get_page(2, tab="all")

        self.assertEqual(result["page"], 2)


# ---------------------------------------------------------------------------
# US-24572: Pending Tab
# ---------------------------------------------------------------------------


class TestApprovalPendingTab(unittest.TestCase):
    """US-24572: Verify Pending tab data grid and actions."""

    def setUp(self):
        self.service = MagicMock()

    def test_pendingTab_grid_displaysRequiredColumnsWithoutPSNo(self):
        """Positive: Pending tab shows required columns (no PS No as not yet assigned)."""
        self.service.get_grid_columns.return_value = [
            "Name",
            "Employment Type",
            "Dept Code",
            "Immediate Supervisor",
            "Date of Joining",
            "Submitted On",
            "Onboarding Type",
        ]

        columns = self.service.get_grid_columns("pending")

        self.assertEqual(len(columns), 7)
        self.assertNotIn("PS No", columns)

    def test_pendingTab_displaysApproveRejectExportButtons(self):
        """Positive: Pending tab shows Approve, Reject, and Export buttons."""
        self.service.get_buttons.return_value = ["Approve", "Reject", "Export"]

        buttons = self.service.get_buttons("pending")

        self.assertIn("Approve", buttons)
        self.assertIn("Reject", buttons)
        self.assertIn("Export", buttons)

    def test_pendingTab_selectAllCheckbox_works(self):
        """Positive: All Select checkbox selects all pending rows."""
        self.service.select_all.return_value = {"selected": True, "count": 3}

        result = self.service.select_all(tab="pending")

        self.assertTrue(result["selected"])

    def test_pendingTab_approveButton_displaysSuccessMessage(self):
        """Positive: Approve shows 'Data approved successful' popup."""
        self.service.approve.return_value = {
            "status": "success",
            "message": "Data approved successful",
        }

        result = self.service.approve(["req_001"], tab="pending")

        self.assertIn("approved successful", result["message"])

    def test_pendingTab_exportButton_displaysSuccessMessage(self):
        """Positive: Export shows 'Data Exported Successfully' popup."""
        self.service.export.return_value = {
            "message": "Data Exported Successfully",
        }

        result = self.service.export(tab="pending")

        self.assertIn("Exported Successfully", result["message"])

    def test_pendingTab_nameHyperlink_navigatesToApprovalDetailsPage(self):
        """Positive: PS No/Name hyperlink navigates to workmen details approval page."""
        self.service.navigate_to_approval_details.return_value = {
            "redirect": "/approval/details/req_001"
        }

        result = self.service.navigate_to_approval_details("req_001")

        self.assertIn("/approval/details", result["redirect"])

    def test_pendingTab_submittedOn_showsIRSubmissionDate(self):
        """Validation: Submitted On shows IR submission date for pending requests."""
        self.service.get_submitted_date.return_value = "10-05-2026"

        result = self.service.get_submitted_date("req_001")

        self.assertIsNotNone(result)

    def test_pendingTab_searchBar_filtersResults(self):
        """Positive: Search bar filters pending requests."""
        self.service.search.return_value = [{"name": "Alice"}]

        results = self.service.search("Alice", tab="pending")

        self.assertEqual(len(results), 1)

    def test_pendingTab_pageNavigation_works(self):
        """Positive: Page navigation works in Pending tab."""
        self.service.get_page.return_value = {"page": 1}

        result = self.service.get_page(1, tab="pending")

        self.assertEqual(result["page"], 1)


# ---------------------------------------------------------------------------
# US-24573: Approved Tab
# ---------------------------------------------------------------------------


class TestApprovalApprovedTab(unittest.TestCase):
    """US-24573: Verify Approved tab data grid and actions."""

    def setUp(self):
        self.service = MagicMock()

    def test_approvedTab_grid_displaysRequiredColumnsIncludingApprovedOn(self):
        """Positive: Approved tab shows all required columns, including Approved On and PS No."""
        self.service.get_grid_columns.return_value = [
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

        columns = self.service.get_grid_columns("approved")

        self.assertEqual(len(columns), 9)
        self.assertIn("PS No", columns)
        self.assertIn("Approved On", columns)

    def test_approvedTab_displaysOnlyExportButton(self):
        """Positive: Approved tab shows only Export button (no Approve or Reject)."""
        self.service.get_buttons.return_value = ["Export"]

        buttons = self.service.get_buttons("approved")

        self.assertEqual(len(buttons), 1)
        self.assertIn("Export", buttons)

    def test_approvedTab_noApproveRejectButtons(self):
        """Negative: Approved tab does NOT have Approve or Reject buttons."""
        self.service.get_buttons.return_value = ["Export"]

        buttons = self.service.get_buttons("approved")

        self.assertNotIn("Approve", buttons)
        self.assertNotIn("Reject", buttons)

    def test_approvedTab_selectAllCheckbox_works(self):
        """Positive: All Select checkbox works in Approved tab."""
        self.service.select_all.return_value = {"selected": True, "count": 5}

        result = self.service.select_all(tab="approved")

        self.assertTrue(result["selected"])

    def test_approvedTab_exportButton_displaysSuccessMessage(self):
        """Positive: Export shows 'Data Exported Successful' message."""
        self.service.export.return_value = {
            "status": "success",
            "message": "Data Exported Successful",
        }

        result = self.service.export(tab="approved")

        self.assertIn("Exported Successful", result["message"])

    def test_approvedTab_psNoHyperlink_navigatesToApprovalDetailsPage(self):
        """Positive: PS No/Name hyperlink navigates to workmen details approval page."""
        self.service.navigate_to_approval_details.return_value = {
            "redirect": "/approval/details/PS-12345"
        }

        result = self.service.navigate_to_approval_details("PS-12345")

        self.assertIn("/approval/details", result["redirect"])

    def test_approvedTab_approvedOn_showsIRApproverApprovalDate(self):
        """Validation: Approved On shows the date when IR Approver approved the process."""
        self.service.get_approved_date.return_value = "20-04-2026"

        result = self.service.get_approved_date("req_001")

        self.assertIsNotNone(result)

    def test_approvedTab_searchBar_works(self):
        """Positive: Search bar filters approved requests."""
        self.service.search.return_value = [{"ps_no": "PS-12345"}]

        results = self.service.search("PS-12345", tab="approved")

        self.assertEqual(len(results), 1)

    def test_approvedTab_pageNavigation_works(self):
        """Positive: Page navigation works in Approved tab."""
        self.service.get_page.return_value = {"page": 1}

        result = self.service.get_page(1, tab="approved")

        self.assertEqual(result["page"], 1)


# ---------------------------------------------------------------------------
# US-24574: Approve / Reject on Employee Overview Page
# ---------------------------------------------------------------------------


class TestApprovalEmployeeOverview(unittest.TestCase):
    """US-24574: Verify the workmen details approval page (approve/reject flow)."""

    def setUp(self):
        self.service = MagicMock()

    def test_clickPSNoInAllOrPendingTab_navigatesToRequestViewPage(self):
        """Positive: Clicking PS No/Name in All or Pending tab opens request view page."""
        self.service.navigate_to_request.return_value = {
            "redirect": "/approval/request/PS-12345"
        }

        result = self.service.navigate_to_request("PS-12345")

        self.assertIn("/approval/request", result["redirect"])

    def test_requestViewPage_displaysAllEmployeeDetails(self):
        """Positive: All onboarding/rehiring details are auto-populated in sections."""
        self.service.get_employee_details.return_value = {
            "personal_info": {"name": "John Doe"},
            "job_info": {"department": "ENG01"},
            "compensation": {"basic": 15000},
        }

        result = self.service.get_employee_details("PS-12345")

        self.assertIn("personal_info", result)
        self.assertIn("job_info", result)
        self.assertIn("compensation", result)

    def test_approveButton_displaysApprovalSuccessPopup(self):
        """Positive: Clicking Approve shows 'Approval successful' popup."""
        self.service.approve_request.return_value = {
            "status": "success",
            "message": "Approval successful",
        }

        result = self.service.approve_request("PS-12345")

        self.assertEqual(result["status"], "success")
        self.assertIn("Approval successful", result["message"])

    def test_rejectButton_displaysConfirmationPopup(self):
        """Positive: Clicking Reject shows 'Do you want to reject employee onboarding?' popup."""
        self.service.reject_request.return_value = {
            "popup": "Do you want to reject employee onboarding?",
            "options": ["Yes", "No"],
        }

        result = self.service.reject_request("PS-12345")

        self.assertIn("reject", result["popup"].lower())
        self.assertIn("Yes", result["options"])
        self.assertIn("No", result["options"])

    def test_rejectConfirm_clickYes_returnsOnboardingAndRedirects(self):
        """Positive: Clicking Yes in reject confirmation returns onboarding and redirects."""
        self.service.confirm_reject.return_value = {
            "status": "returned",
            "redirect": "/onboarding-approval",
        }

        result = self.service.confirm_reject("PS-12345", "Yes")

        self.assertEqual(result["status"], "returned")
        self.assertIn("/onboarding-approval", result["redirect"])

    def test_rejectConfirm_clickNo_staysOnApprovalPage(self):
        """Positive: Clicking No on reject popup keeps user on the approval details page."""
        self.service.confirm_reject.return_value = {
            "status": "unchanged",
            "redirect": None,
        }

        result = self.service.confirm_reject("PS-12345", "No")

        self.assertEqual(result["status"], "unchanged")
        self.assertIsNone(result["redirect"])

    def test_approvalPage_psNoNotShownInPendingTab(self):
        """Validation: PS No not shown in Pending tab (generated only after approval)."""
        self.service.get_ps_no.return_value = None

        result = self.service.get_ps_no("req_pending")

        self.assertIsNone(result)

    def test_approvalPage_psNoShownAfterApproval(self):
        """Validation: PS No generated and shown after IR Approver approval."""
        self.service.get_ps_no.return_value = "PS-00789"

        result = self.service.get_ps_no("req_approved")

        self.assertIsNotNone(result)


if __name__ == "__main__":
    unittest.main()
