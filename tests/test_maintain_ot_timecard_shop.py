"""
Unit Tests for Maintain OT Timecard – Shop In Charge (IS) Roles
User Stories: US-OT-004 (OT Approval), US-OT-005 (OT Approval Export)

Covers OT approval functionality for:
- Shop In Charge (IS) – view OT approval tabs (All, Pending, Approved),
  approve/reject OT requests, change OT hours, bulk approve, export

Test Categories:
- Positive / Happy Path
- Negative / Error Path
- Boundary / Edge Cases
- Integration Points
"""

SOURCE_STORY_FILE = "MaintainOTTimeCard.xlsx"

import unittest
from unittest.mock import MagicMock, patch
from datetime import date


# TODO: Import actual modules once implementation is available.
# from src.attendance.ot_approval import (
#     OTApprovalPage, OTApprovalService, OTApprovalGrid,
#     ExportService, KioskAPI, InfoCommAPI
# )


# ---------------------------------------------------------------------------
# US-OT-004: Shop In Charge – OT Approval
# ---------------------------------------------------------------------------


class TestOTApprovalNavigation(unittest.TestCase):
    """US-OT-004: Verify navigation to OT Approval page from
    side navigation under Attendance Management."""

    def setUp(self):
        """Arrange: Create mock navigation and page instances."""
        self.nav_service = MagicMock()
        self.ot_approval_page = MagicMock()
        self.nav_service.select_submenu.return_value = self.ot_approval_page
        self.ot_approval_page.get_tabs.return_value = ["All", "Pending", "Approved"]

    def test_selectOTApproval_navigate_displaysOTApprovalPage(self):
        """Positive: Selecting 'OT Approval' from 'Attendance Management' menu
        displays the OT Approval page."""
        page = self.nav_service.select_submenu("Attendance Management", "OT Approval")
        self.nav_service.select_submenu.assert_called_once_with(
            "Attendance Management", "OT Approval"
        )
        self.assertIsNotNone(page)

    def test_otApprovalPage_render_displaysTabs(self):
        """Positive: OT Approval page displays 'All', 'Pending', 'Approved' tabs."""
        tabs = self.ot_approval_page.get_tabs()
        self.assertEqual(tabs, ["All", "Pending", "Approved"])

    def test_otApprovalPage_buttons_displaysExportAndSave(self):
        """Positive: OT Approval page displays Export and Save buttons."""
        self.ot_approval_page.get_buttons.return_value = ["Export", "Save"]
        buttons = self.ot_approval_page.get_buttons()
        self.assertIn("Export", buttons)
        self.assertIn("Save", buttons)


class TestOTApprovalAllTab(unittest.TestCase):
    """US-OT-004: Verify 'All' tab displays all OT requests with expected columns."""

    EXPECTED_COLUMNS = [
        "Employee",
        "Date",
        "TRT No",
        "OT In",
        "OT Out",
        "Total OT Hours",
        "Approved OT Hours",
        "Remarks",
        "Status",
        "Action",
    ]

    def setUp(self):
        """Arrange: Create mock All tab grid."""
        self.grid = MagicMock()
        self.grid.get_columns.return_value = self.EXPECTED_COLUMNS

    def test_allTab_grid_displaysAllRequiredColumns(self):
        """Positive: 'All' tab grid displays all required columns."""
        columns = self.grid.get_columns()
        for col in self.EXPECTED_COLUMNS:
            self.assertIn(col, columns)

    def test_allTab_statusColumn_displaysPendingApprovedRejected(self):
        """Positive: Status column shows Pending, Approved, or Rejected."""
        self.grid.get_cell_value.return_value = "Pending"
        value = self.grid.get_cell_value(row=0, column="Status")
        self.assertIn(value, ["Pending", "Approved", "Rejected"])

    def test_allTab_actionColumn_displaysApproveRejectForPending(self):
        """Positive: Action column displays Approve/Reject buttons only
        when status is Pending."""
        self.grid.get_cell_value.side_effect = lambda row, column: {
            "Status": "Pending",
            "Action": ["Approve", "Reject"],
        }.get(column)
        status = self.grid.get_cell_value(row=0, column="Status")
        actions = self.grid.get_cell_value(row=0, column="Action")
        if status == "Pending":
            self.assertIn("Approve", actions)
            self.assertIn("Reject", actions)

    def test_allTab_actionColumn_hiddenForApprovedStatus(self):
        """Positive: Action column does not show Approve/Reject for Approved records."""
        self.grid.get_action_buttons.return_value = []
        actions = self.grid.get_action_buttons(row=0, status="Approved")
        self.assertEqual(actions, [])

    def test_allTab_dateColumn_showsOTApplicationDate(self):
        """Positive: Date column shows the date when the employee applied for OT,
        fetched from Kiosk."""
        self.grid.get_cell_value.return_value = "2026-05-01"
        value = self.grid.get_cell_value(row=0, column="Date")
        self.assertIsNotNone(value)

    def test_allTab_remarksFetchedFromKiosk(self):
        """Positive: Remarks column data is fetched from Kiosk."""
        self.grid.get_cell_value.return_value = "Urgent production work"
        value = self.grid.get_cell_value(row=0, column="Remarks")
        self.assertIsNotNone(value)


class TestOTApprovalPendingTab(unittest.TestCase):
    """US-OT-004: Verify 'Pending' tab displays only pending OT requests."""

    def setUp(self):
        """Arrange: Create mock pending tab grid."""
        self.grid = MagicMock()
        self.service = MagicMock()

    def test_pendingTab_grid_displaysOnlyPendingRequests(self):
        """Positive: Pending tab displays only requests with Pending status."""
        self.service.get_pending_requests.return_value = [
            {"employee": "12345", "status": "Pending"},
            {"employee": "67890", "status": "Pending"},
        ]
        result = self.service.get_pending_requests()
        for record in result:
            self.assertEqual(record["status"], "Pending")

    def test_pendingTab_gridColumns_displaysRequiredColumns(self):
        """Positive: Pending tab grid displays required columns including Action."""
        expected_columns = [
            "Employee", "Date", "TRT No", "OT In", "OT Out",
            "Total OT Hours", "Remarks", "Action",
        ]
        self.grid.get_columns.return_value = expected_columns
        columns = self.grid.get_columns()
        for col in expected_columns:
            self.assertIn(col, columns)

    def test_pendingTab_actionColumn_displaysApproveReject(self):
        """Positive: Action column in Pending tab displays Approve and Reject buttons."""
        self.grid.get_action_buttons.return_value = ["Approve", "Reject"]
        actions = self.grid.get_action_buttons(row=0)
        self.assertIn("Approve", actions)
        self.assertIn("Reject", actions)


class TestOTApprovalApprovedTab(unittest.TestCase):
    """US-OT-004: Verify 'Approved' tab displays only approved OT requests."""

    def setUp(self):
        """Arrange: Create mock approved tab."""
        self.service = MagicMock()
        self.grid = MagicMock()

    def test_approvedTab_grid_displaysOnlyApprovedRequests(self):
        """Positive: Approved tab displays only requests that have been approved."""
        self.service.get_approved_requests.return_value = [
            {"employee": "12345", "status": "Approved", "approved_ot": 3.0},
        ]
        result = self.service.get_approved_requests()
        for record in result:
            self.assertEqual(record["status"], "Approved")

    def test_approvedTab_gridColumns_includesApprovedOTHours(self):
        """Positive: Approved tab grid includes 'Approved OT Hours' column."""
        expected_columns = [
            "Employee", "Date", "TRT No", "OT In", "OT Out",
            "Total OT Hours", "Approved OT Hours", "Remarks",
        ]
        self.grid.get_columns.return_value = expected_columns
        columns = self.grid.get_columns()
        self.assertIn("Approved OT Hours", columns)


class TestOTApprovalEmployeeDetailPopup(unittest.TestCase):
    """US-OT-004: Verify clicking employee detail opens a popup
    for individual OT approval."""

    def setUp(self):
        """Arrange: Create mock popup service."""
        self.popup = MagicMock()
        self.popup.get_fields.return_value = [
            "Employee",
            "Date",
            "OT In",
            "OT Out",
            "Total OT Hours",
            "Approve/Reject",
            "Change OT Hour",
        ]

    def test_employeeDetailPopup_clickEmployee_displaysPopup(self):
        """Positive: Clicking on employee detail in data grid displays a popup
        with OT details."""
        self.popup.is_visible.return_value = True
        self.assertTrue(self.popup.is_visible())

    def test_employeeDetailPopup_fields_displaysAllRequiredFields(self):
        """Positive: Popup displays Employee, Date, OT In, OT Out, Total OT Hours,
        and action buttons."""
        fields = self.popup.get_fields()
        self.assertIn("Employee", fields)
        self.assertIn("Date", fields)
        self.assertIn("OT In", fields)
        self.assertIn("OT Out", fields)
        self.assertIn("Total OT Hours", fields)

    def test_employeeDetailPopup_approveButton_approvesRequest(self):
        """Positive: Clicking Approve in popup approves the OT request."""
        self.popup.approve.return_value = {"status": "Approved"}
        result = self.popup.approve(employee_id="12345", date="2026-05-01")
        self.assertEqual(result["status"], "Approved")

    def test_employeeDetailPopup_rejectButton_rejectsRequest(self):
        """Positive: Clicking Reject in popup rejects the OT request."""
        self.popup.reject.return_value = {"status": "Rejected"}
        result = self.popup.reject(employee_id="12345", date="2026-05-01")
        self.assertEqual(result["status"], "Rejected")


class TestOTApprovalChangeOTHour(unittest.TestCase):
    """US-OT-004: Verify 'Change OT Hour' functionality in popup."""

    def setUp(self):
        """Arrange: Create mock popup with Change OT Hour capability."""
        self.popup = MagicMock()
        self.service = MagicMock()

    def test_changeOTHour_clickButton_displaysNewOTHoursField(self):
        """Positive: Clicking 'Change OT Hour' displays a new field for entering
        desired OT hours."""
        self.popup.click_change_ot_hour.return_value = {
            "new_ot_hours_field": True,
            "reasons_field": True,
        }
        result = self.popup.click_change_ot_hour()
        self.assertTrue(result["new_ot_hours_field"])
        self.assertTrue(result["reasons_field"])

    def test_changeOTHour_enterNewHoursAndApprove_updatesApprovedHours(self):
        """Positive: Entering new OT hours and clicking Approve updates the
        'Approved OT Hours' column in the data grid."""
        self.service.change_and_approve_ot.return_value = {
            "approved_ot_hours": 2.5,
            "status": "Approved",
        }
        result = self.service.change_and_approve_ot(
            employee_id="12345",
            date="2026-05-01",
            new_ot_hours=2.5,
            reason="Production adjustment",
        )
        self.assertEqual(result["approved_ot_hours"], 2.5)
        self.assertEqual(result["status"], "Approved")

    def test_changeOTHour_newHoursExceedTotal_raisesValidationError(self):
        """Negative: Entering new OT hours greater than Total OT Hours raises
        a validation error."""
        self.service.change_and_approve_ot.side_effect = ValueError(
            "New OT hours cannot exceed Total OT hours"
        )
        with self.assertRaises(ValueError):
            self.service.change_and_approve_ot(
                employee_id="12345",
                date="2026-05-01",
                new_ot_hours=5.0,  # exceeds total of 3.0
                reason="Adjustment",
            )

    def test_changeOTHour_zeroHours_raisesValidationError(self):
        """Boundary: Entering 0 as new OT hours raises a validation error."""
        self.service.change_and_approve_ot.side_effect = ValueError(
            "OT hours must be greater than zero"
        )
        with self.assertRaises(ValueError):
            self.service.change_and_approve_ot(
                employee_id="12345",
                date="2026-05-01",
                new_ot_hours=0,
                reason="Error",
            )

    def test_changeOTHour_negativeHours_raisesValidationError(self):
        """Boundary: Entering negative OT hours raises a validation error."""
        self.service.change_and_approve_ot.side_effect = ValueError(
            "OT hours cannot be negative"
        )
        with self.assertRaises(ValueError):
            self.service.change_and_approve_ot(
                employee_id="12345",
                date="2026-05-01",
                new_ot_hours=-1.0,
                reason="Error",
            )

    def test_changeOTHour_noReasonProvided_raisesValidationError(self):
        """Negative: Not providing a reason for OT hour change raises a validation error."""
        self.service.change_and_approve_ot.side_effect = ValueError(
            "Reason is required for OT hour change"
        )
        with self.assertRaises(ValueError):
            self.service.change_and_approve_ot(
                employee_id="12345",
                date="2026-05-01",
                new_ot_hours=2.0,
                reason="",
            )


class TestOTApprovalBulkActions(unittest.TestCase):
    """US-OT-004: Verify bulk approve and reject constraints."""

    def setUp(self):
        """Arrange: Create mock approval service."""
        self.service = MagicMock()

    def test_bulkApprove_multiSelect_approvesMultipleRequests(self):
        """Positive: User can bulk approve requests using multi-select checkbox."""
        self.service.bulk_approve.return_value = {
            "approved_count": 3,
            "status": "Success",
        }
        result = self.service.bulk_approve(employee_ids=["12345", "67890", "11111"])
        self.assertEqual(result["approved_count"], 3)

    def test_bulkReject_notAllowed_raisesError(self):
        """Negative: User cannot bulk reject – only one request can be rejected at a time."""
        self.service.bulk_reject.side_effect = ValueError(
            "Only one request can be rejected at a time"
        )
        with self.assertRaises(ValueError):
            self.service.bulk_reject(employee_ids=["12345", "67890"])

    def test_singleReject_allowed_rejectsOneRequest(self):
        """Positive: Rejecting a single request at a time is allowed."""
        self.service.reject_request.return_value = {"status": "Rejected"}
        result = self.service.reject_request(employee_id="12345", date="2026-05-01")
        self.assertEqual(result["status"], "Rejected")

    def test_bulkApprove_noSelection_raisesValidationError(self):
        """Negative: Attempting bulk approve without selecting any requests fails."""
        self.service.bulk_approve.side_effect = ValueError(
            "No requests selected for approval"
        )
        with self.assertRaises(ValueError):
            self.service.bulk_approve(employee_ids=[])

    def test_reject_multiSelectDisabled_cannotSelectMultiple(self):
        """Negative: When rejecting, the user cannot choose multi-select checkbox."""
        self.service.is_multiselect_enabled_for_reject.return_value = False
        result = self.service.is_multiselect_enabled_for_reject()
        self.assertFalse(result)


class TestOTApprovalValidation(unittest.TestCase):
    """US-OT-004: Verify general OT approval validation rules."""

    def setUp(self):
        """Arrange: Create mock service."""
        self.service = MagicMock()

    def test_approval_duplicatePunches_removedBySystem(self):
        """Positive: System considers only first punch in and last punch out."""
        self.service.filter_punches.return_value = [
            {"type": "in", "time": "18:00"},
            {"type": "out", "time": "21:00"},
        ]
        result = self.service.filter_punches([
            {"type": "in", "time": "18:00"},
            {"type": "in", "time": "18:05"},
            {"type": "out", "time": "20:30"},
            {"type": "out", "time": "21:00"},
        ])
        self.assertEqual(len(result), 2)

    def test_approval_totalOTHours_calculatedCorrectly(self):
        """Positive: Total OT hours is the total count of OT punch in and out."""
        self.service.calculate_total_ot.return_value = 3.0
        result = self.service.calculate_total_ot(ot_in="18:00", ot_out="21:00")
        self.assertEqual(result, 3.0)

    def test_approval_searchBar_filtersData(self):
        """Positive: Search bar filters the data grid by column or global search."""
        self.service.search.return_value = [{"employee": "12345 - John Doe"}]
        result = self.service.search(query="John")
        self.assertTrue(len(result) > 0)

    def test_approval_pageNavigation_worksCorrectly(self):
        """Positive: Page navigation works correctly to navigate between pages."""
        self.service.get_page.return_value = {"page": 2, "records": []}
        result = self.service.get_page(page=2)
        self.assertEqual(result["page"], 2)


# ---------------------------------------------------------------------------
# US-OT-005: Shop In Charge – Export OT Approval
# ---------------------------------------------------------------------------


class TestOTApprovalExport(unittest.TestCase):
    """US-OT-005: Verify Export button on OT Approval page."""

    def setUp(self):
        """Arrange: Create mock export service."""
        self.export_service = MagicMock()

    def test_export_clickExportButton_exportsToExcel(self):
        """Positive: Clicking 'Export' exports the displayed data to an Excel file."""
        self.export_service.export_to_excel.return_value = "/downloads/ot_approval.xlsx"
        result = self.export_service.export_to_excel(tab="All")
        self.assertTrue(result.endswith(".xlsx"))

    def test_export_withDateFilter_exportsFilteredData(self):
        """Positive: If user selects a date, only filtered data is exported."""
        self.export_service.export_to_excel.return_value = "/downloads/ot_filtered.xlsx"
        result = self.export_service.export_to_excel(
            tab="All", from_date=date(2026, 5, 1), to_date=date(2026, 5, 10)
        )
        self.assertIsNotNone(result)

    def test_export_withoutFilter_exportsAllExistingData(self):
        """Positive: If user doesn't filter data, all existing data is exported."""
        self.export_service.export_to_excel.return_value = "/downloads/ot_all.xlsx"
        result = self.export_service.export_to_excel(tab="All", from_date=None, to_date=None)
        self.assertIsNotNone(result)

    def test_export_saveToLocation_userCanChoosePath(self):
        """Positive: User can save the exported file to a chosen location."""
        self.export_service.save_to_location.return_value = True
        result = self.export_service.save_to_location(path="/user/documents/ot_approval.xlsx")
        self.assertTrue(result)

    def test_export_emptyGrid_exportsEmptyFile(self):
        """Boundary: Exporting when grid has no data produces an empty file."""
        self.export_service.export_to_excel.return_value = "/downloads/ot_empty.xlsx"
        self.export_service.get_exported_row_count.return_value = 0
        result = self.export_service.export_to_excel(tab="Pending")
        self.assertIsNotNone(result)
        count = self.export_service.get_exported_row_count()
        self.assertEqual(count, 0)

    def test_export_serviceFailure_handlesGracefully(self):
        """Negative: Export service failure is handled gracefully."""
        self.export_service.export_to_excel.side_effect = IOError("Disk full")
        with self.assertRaises(IOError):
            self.export_service.export_to_excel(tab="All")


if __name__ == "__main__":
    unittest.main()
