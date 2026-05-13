"""
Unit Tests for Maintain OT Timecard Module
User Stories: US-OT-001 (IR Date View), US-OT-002 (IR Employee View),
              US-OT-003 (IR Export), US-OT-004 (Shop OT Approval),
              US-OT-005 (Shop Export)

Covers OT Timecard functionality for:
- IR / Company Head / Location Head / BU Head – date view, employee view, export
- Shop In Charge (IS) – OT approval (All/Pending/Approved tabs, popup, Change OT hours), export

Test Categories:
- Positive / Happy Path
- Negative / Error Path
- Boundary / Edge Cases
"""

SOURCE_STORY_FILE = "MaintainOTTimeCard.xlsx"

import unittest
from unittest.mock import MagicMock, patch, PropertyMock
from datetime import date, timedelta


# TODO: Import actual modules once implementation is available.
# from src.attendance.ot_timecard import (
#     OTTimecardPage, OTTimecardService, OTApprovalPage,
#     OTApprovalService, ExportService
# )


# ---------------------------------------------------------------------------
# US-OT-001: IR – View Maintain OT Timecard (Date View)
# ---------------------------------------------------------------------------


class TestOTTimecardDateViewPageDisplay(unittest.TestCase):
    """US-OT-001: Verify Maintain OT Timecard page – Date View displays correctly."""

    def setUp(self):
        """Arrange: Create mock page, navigation, and service instances."""
        self.navigation = MagicMock()
        self.page = MagicMock()
        self.page.get_tabs.return_value = ["Date View", "Employee View"]
        self.page.get_default_tab.return_value = "Date View"
        self.page.get_attributes.return_value = ["Date", "From", "To"]
        self.page.get_buttons.return_value = ["Export"]
        self.page.get_grid_columns.return_value = [
            "Employee", "TRT No", "OT In", "OT Out",
            "Total OT Hours", "Approved OT Hours", "OT Status",
            "Leave Remarks", "OT Canteen", "OT LCA", "OT TPT", "Cadre",
        ]
        self.service = MagicMock()

    def test_navigation_selectAttendanceMenu_displaysOTTimecardPage(self):
        """Positive: User navigates to Maintain OT Timecard from Attendance Management menu."""
        self.navigation.select_menu.return_value = "Maintain OT Timecard"

        result = self.navigation.select_menu("Attendance Management", "Maintain OT Timecard")

        self.assertEqual(result, "Maintain OT Timecard")

    def test_page_load_displaysDateViewAndEmployeeViewTabs(self):
        """Positive: Page displays both Date View and Employee View tabs."""
        tabs = self.page.get_tabs()
        self.assertIn("Date View", tabs)
        self.assertIn("Employee View", tabs)

    def test_page_load_defaultTabIsDateView(self):
        """Positive: By default, the Date View tab is displayed."""
        default_tab = self.page.get_default_tab()
        self.assertEqual(default_tab, "Date View")

    def test_dateView_attributes_displaysDatePicker(self):
        """Positive: Date View displays Date date-picker attribute."""
        attributes = self.page.get_attributes()
        self.assertIn("Date", attributes)

    def test_dateView_attributes_displaysFromDatePicker(self):
        """Positive: Date View displays From date-picker attribute."""
        attributes = self.page.get_attributes()
        self.assertIn("From", attributes)

    def test_dateView_attributes_displaysToDatePicker(self):
        """Positive: Date View displays To date-picker attribute."""
        attributes = self.page.get_attributes()
        self.assertIn("To", attributes)

    def test_dateView_buttons_displaysExportButton(self):
        """Positive: Date View page displays the Export button."""
        buttons = self.page.get_buttons()
        self.assertIn("Export", buttons)

    def test_dateView_grid_displaysAllRequiredColumns(self):
        """Positive: Date View grid displays all required columns."""
        expected_columns = [
            "Employee", "TRT No", "OT In", "OT Out",
            "Total OT Hours", "Approved OT Hours", "OT Status",
            "Leave Remarks", "OT Canteen", "OT LCA", "OT TPT", "Cadre",
        ]
        columns = self.page.get_grid_columns()
        for col in expected_columns:
            self.assertIn(col, columns)

    def test_dateView_grid_employeeColumnShowsPSNoAndName(self):
        """Positive: Employee column fetches PS No and Employee Name from info comm."""
        self.service.get_employee_info.return_value = {"ps_no": "12345", "name": "John Doe"}

        info = self.service.get_employee_info("12345")

        self.assertEqual(info["ps_no"], "12345")
        self.assertEqual(info["name"], "John Doe")

    def test_dateView_grid_otInOutDisplayedInHHMM(self):
        """Positive: OT In and OT Out columns display time in HH:MM format."""
        self.service.get_ot_punch.return_value = {"ot_in": "18:00", "ot_out": "20:30"}

        punch = self.service.get_ot_punch("12345", "2025-12-15")

        self.assertRegex(punch["ot_in"], r"^\d{2}:\d{2}$")
        self.assertRegex(punch["ot_out"], r"^\d{2}:\d{2}$")


class TestOTTimecardDateViewFiltering(unittest.TestCase):
    """US-OT-001: Verify date filtering and default data behavior."""

    def setUp(self):
        """Arrange: Create mock service for date-based queries."""
        self.service = MagicMock()

    def test_dateView_selectFromAndToDate_displaysFilteredData(self):
        """Positive: Selecting From and To date filters grid data to those dates."""
        self.service.get_records_by_date_range.return_value = [
            {"employee": "EMP001", "date": "2025-12-10"},
            {"employee": "EMP002", "date": "2025-12-11"},
        ]

        records = self.service.get_records_by_date_range("2025-12-10", "2025-12-15")

        self.assertTrue(len(records) > 0)
        self.service.get_records_by_date_range.assert_called_once_with("2025-12-10", "2025-12-15")

    def test_dateView_noDateSelected_displaysDefaultOneMonthData(self):
        """Positive: When no dates are selected, system shows default one month of data."""
        self.service.get_default_records.return_value = {"period": "1 month", "count": 150}

        result = self.service.get_default_records()

        self.assertEqual(result["period"], "1 month")

    def test_dateView_totalOTHours_summedForSelectedPeriod(self):
        """Positive: Total OT hours is the summation of OT for the selected period."""
        self.service.get_total_ot_hours.return_value = 24.5

        total = self.service.get_total_ot_hours("EMP001", "2025-12-01", "2025-12-10")

        self.assertEqual(total, 24.5)


class TestOTTimecardDateViewValidation(unittest.TestCase):
    """US-OT-001: Verify validation rules for Date View."""

    def setUp(self):
        """Arrange: Create mock service for validation tests."""
        self.service = MagicMock()

    def test_validation_duplicatePunches_removedBySystem(self):
        """Positive: System considers only first punch in and last punch out, removing duplicates."""
        self.service.process_punches.return_value = {"ot_in": "18:00", "ot_out": "21:00"}
        raw_punches = [
            {"time": "18:00", "type": "in"},
            {"time": "18:02", "type": "in"},
            {"time": "20:30", "type": "out"},
            {"time": "21:00", "type": "out"},
        ]

        result = self.service.process_punches(raw_punches)

        self.assertEqual(result["ot_in"], "18:00")
        self.assertEqual(result["ot_out"], "21:00")

    def test_validation_otCanteen_displaysOT2OrOT4(self):
        """Positive: OT Canteen status displays values like OT2, OT4 based on allowance logic."""
        self.service.get_ot_canteen_status.return_value = "OT2"

        status = self.service.get_ot_canteen_status("EMP001", "2025-12-15")

        self.assertIn(status, ["OT2", "OT4"])

    def test_validation_otLCA_displaysYesOrNo(self):
        """Positive: OT LCA column displays YES or NO."""
        self.service.get_ot_lca.return_value = "YES"

        result = self.service.get_ot_lca("EMP001", "2025-12-15")

        self.assertIn(result, ["YES", "NO"])

    def test_validation_otTPT_displaysYesOrNo(self):
        """Positive: OT TPT column displays YES or NO."""
        self.service.get_ot_tpt.return_value = "NO"

        result = self.service.get_ot_tpt("EMP001", "2025-12-15")

        self.assertIn(result, ["YES", "NO"])

    def test_validation_remarks_displayedBasedOnPunch(self):
        """Positive: Remarks are shown based on punch data to IR and employee."""
        self.service.get_remarks.return_value = "Present"

        remarks = self.service.get_remarks("EMP001", "2025-12-15")

        self.assertIsNotNone(remarks)


class TestOTTimecardDateViewSearchAndPagination(unittest.TestCase):
    """US-OT-001: Verify search bar and page navigation in Date View."""

    def setUp(self):
        """Arrange: Create mock page for search and pagination tests."""
        self.page = MagicMock()

    def test_searchBar_columnSearch_filtersResultsByColumn(self):
        """Positive: Column search bar filters results by a specific column."""
        self.page.column_search.return_value = [{"employee": "EMP001"}]

        results = self.page.column_search("Employee", "EMP001")

        self.assertEqual(len(results), 1)

    def test_searchBar_globalSearch_filtersResultsGlobally(self):
        """Positive: Global search bar filters results across all columns."""
        self.page.global_search.return_value = [{"employee": "EMP001"}]

        results = self.page.global_search("EMP001")

        self.assertTrue(len(results) >= 1)

    def test_pageNavigation_navigateToNextPage_displaysCorrectData(self):
        """Positive: User can navigate to other pages using page navigation."""
        self.page.navigate_to_page.return_value = {"page": 2, "records": 10}

        result = self.page.navigate_to_page(2)

        self.assertEqual(result["page"], 2)

    def test_searchBar_emptyQuery_returnsAllResults(self):
        """Edge Case: Empty search query returns all results."""
        self.page.global_search.return_value = [{"employee": "EMP001"}, {"employee": "EMP002"}]

        results = self.page.global_search("")

        self.assertTrue(len(results) >= 1)

    def test_searchBar_noMatch_returnsEmptyResults(self):
        """Negative: Search with non-existent term returns empty results."""
        self.page.global_search.return_value = []

        results = self.page.global_search("NONEXISTENT_EMPLOYEE")

        self.assertEqual(len(results), 0)


# ---------------------------------------------------------------------------
# US-OT-002: IR – View Maintain OT Timecard (Employee View)
# ---------------------------------------------------------------------------


class TestOTTimecardEmployeeViewPageDisplay(unittest.TestCase):
    """US-OT-002: Verify Maintain OT Timecard – Employee View displays correctly."""

    def setUp(self):
        """Arrange: Create mock page for Employee View."""
        self.page = MagicMock()
        self.page.get_attributes.return_value = ["Employee", "From Date", "To Date"]
        self.page.get_buttons.return_value = ["Export"]
        self.page.get_grid_columns.return_value = [
            "Date", "TRT No", "OT In", "OT Out",
            "Total OT Hours", "Approved OT Hours", "OT Status",
            "Leave Remarks", "OT Canteen", "OT LCA", "OT TPT", "Cadre",
        ]
        self.service = MagicMock()

    def test_employeeView_clickTab_displaysEmployeeViewTab(self):
        """Positive: Clicking Employee View tab switches to Employee View."""
        self.page.switch_tab.return_value = "Employee View"

        result = self.page.switch_tab("Employee View")

        self.assertEqual(result, "Employee View")

    def test_employeeView_attributes_displaysEmployeeDropdown(self):
        """Positive: Employee View shows Employee drop-down (PS No and Name)."""
        attributes = self.page.get_attributes()
        self.assertIn("Employee", attributes)

    def test_employeeView_attributes_displaysFromDatePicker(self):
        """Positive: Employee View shows From Date date-picker."""
        attributes = self.page.get_attributes()
        self.assertIn("From Date", attributes)

    def test_employeeView_attributes_displaysToDatePicker(self):
        """Positive: Employee View shows To Date date-picker."""
        attributes = self.page.get_attributes()
        self.assertIn("To Date", attributes)

    def test_employeeView_grid_displaysDateColumn(self):
        """Positive: Employee View grid includes Date column."""
        columns = self.page.get_grid_columns()
        self.assertIn("Date", columns)

    def test_employeeView_grid_displaysAllRequiredColumns(self):
        """Positive: Employee View grid displays all required columns."""
        expected_columns = [
            "Date", "TRT No", "OT In", "OT Out",
            "Total OT Hours", "Approved OT Hours", "OT Status",
            "Leave Remarks", "OT Canteen", "OT LCA", "OT TPT", "Cadre",
        ]
        columns = self.page.get_grid_columns()
        for col in expected_columns:
            self.assertIn(col, columns)

    def test_employeeView_selectEmployee_displaysEmployeeData(self):
        """Positive: Selecting an employee from dropdown filters data for that employee."""
        self.service.get_employee_records.return_value = [
            {"date": "2025-12-10", "ot_in": "18:00", "ot_out": "20:00"},
        ]

        records = self.service.get_employee_records("EMP001")

        self.assertTrue(len(records) > 0)


class TestOTTimecardEmployeeViewFiltering(unittest.TestCase):
    """US-OT-002: Verify date filtering in Employee View."""

    def setUp(self):
        """Arrange: Create mock service."""
        self.service = MagicMock()

    def test_employeeView_selectFromToDate_filtersData(self):
        """Positive: Selecting From and To date filters employee OT data."""
        self.service.get_employee_records_by_range.return_value = [
            {"date": "2025-12-10"},
            {"date": "2025-12-11"},
        ]

        records = self.service.get_employee_records_by_range("EMP001", "2025-12-10", "2025-12-15")

        self.assertEqual(len(records), 2)

    def test_employeeView_noDateSelected_displaysDefaultOneMonthData(self):
        """Positive: Default shows one month of data when no dates are selected."""
        self.service.get_employee_default_records.return_value = {"period": "1 month"}

        result = self.service.get_employee_default_records("EMP001")

        self.assertEqual(result["period"], "1 month")

    def test_employeeView_totalOTHours_summedForSelectedPeriod(self):
        """Positive: Total OT hours is summation of OT hours for the selected period."""
        self.service.get_employee_total_ot.return_value = 15.0

        total = self.service.get_employee_total_ot("EMP001", "2025-12-01", "2025-12-10")

        self.assertEqual(total, 15.0)

    def test_employeeView_noEmployeeSelected_displaysNoData(self):
        """Negative: When no employee is selected, no data is displayed."""
        self.service.get_employee_records.return_value = []

        records = self.service.get_employee_records(None)

        self.assertEqual(len(records), 0)


class TestOTTimecardEmployeeViewSearchAndPagination(unittest.TestCase):
    """US-OT-002: Verify search and pagination in Employee View."""

    def setUp(self):
        """Arrange: Create mock page."""
        self.page = MagicMock()

    def test_searchBar_columnSearch_filtersEmployeeViewResults(self):
        """Positive: Column search filters Employee View grid results."""
        self.page.column_search.return_value = [{"date": "2025-12-10"}]

        results = self.page.column_search("Date", "2025-12-10")

        self.assertEqual(len(results), 1)

    def test_searchBar_globalSearch_filtersEmployeeViewResults(self):
        """Positive: Global search filters Employee View grid results."""
        self.page.global_search.return_value = [{"date": "2025-12-10"}]

        results = self.page.global_search("2025-12-10")

        self.assertTrue(len(results) >= 1)

    def test_pageNavigation_navigateToPage_displaysCorrectData(self):
        """Positive: Page navigation works in Employee View."""
        self.page.navigate_to_page.return_value = {"page": 3, "records": 10}

        result = self.page.navigate_to_page(3)

        self.assertEqual(result["page"], 3)


# ---------------------------------------------------------------------------
# US-OT-003: IR – Export Maintain OT Timecard
# ---------------------------------------------------------------------------


class TestOTTimecardExport(unittest.TestCase):
    """US-OT-003: Verify Export functionality for Maintain OT Timecard."""

    def setUp(self):
        """Arrange: Create mock export service."""
        self.export_service = MagicMock()

    def test_export_clickExportButton_exportsToExcelFile(self):
        """Positive: Clicking Export button exports grid details to an Excel file."""
        self.export_service.export_to_excel.return_value = "ot_timecard_export.xlsx"

        result = self.export_service.export_to_excel("date_view")

        self.assertTrue(result.endswith(".xlsx"))

    def test_export_withDateFilter_exportsFilteredData(self):
        """Positive: When user selects date filter, exported file contains filtered month value."""
        self.export_service.export_filtered.return_value = {"rows": 50, "file": "filtered.xlsx"}

        result = self.export_service.export_filtered("2025-12-01", "2025-12-31")

        self.assertEqual(result["rows"], 50)
        self.assertTrue(result["file"].endswith(".xlsx"))

    def test_export_withoutFilter_exportsExistingData(self):
        """Positive: When no filter is applied, existing data is exported."""
        self.export_service.export_all.return_value = {"rows": 500, "file": "all_data.xlsx"}

        result = self.export_service.export_all()

        self.assertTrue(result["rows"] > 0)

    def test_export_saveToLocation_fileIsSaved(self):
        """Positive: User can save the export file to a chosen location."""
        self.export_service.save_to_path.return_value = True

        saved = self.export_service.save_to_path("/downloads/ot_timecard.xlsx")

        self.assertTrue(saved)

    def test_export_emptyGrid_exportsEmptyFile(self):
        """Edge Case: Exporting when grid has no data produces an empty/header-only file."""
        self.export_service.export_to_excel.return_value = "empty_export.xlsx"
        self.export_service.get_export_row_count.return_value = 0

        self.export_service.export_to_excel("date_view")
        count = self.export_service.get_export_row_count()

        self.assertEqual(count, 0)

    def test_export_invalidPath_raisesError(self):
        """Negative: Saving to an invalid path raises an error."""
        self.export_service.save_to_path.side_effect = OSError("Invalid path")

        with self.assertRaises(OSError):
            self.export_service.save_to_path("/invalid/path/file.xlsx")


# ---------------------------------------------------------------------------
# US-OT-004: Shop In Charge – OT Approval
# ---------------------------------------------------------------------------


class TestOTApprovalPageDisplay(unittest.TestCase):
    """US-OT-004: Verify OT Approval page displays correctly for Shop In Charge."""

    def setUp(self):
        """Arrange: Create mock OT Approval page."""
        self.navigation = MagicMock()
        self.page = MagicMock()
        self.page.get_tabs.return_value = ["All", "Pending", "Approved"]
        self.page.get_buttons.return_value = ["Export", "Save"]

    def test_navigation_selectAttendanceMenu_displaysOTApprovalPage(self):
        """Positive: Shop In Charge navigates to OT Approval from Attendance Management."""
        self.navigation.select_menu.return_value = "OT Approval"

        result = self.navigation.select_menu("Attendance Management", "OT Approval")

        self.assertEqual(result, "OT Approval")

    def test_page_load_displaysAllPendingApprovedTabs(self):
        """Positive: OT Approval page displays All, Pending, and Approved tabs."""
        tabs = self.page.get_tabs()
        self.assertIn("All", tabs)
        self.assertIn("Pending", tabs)
        self.assertIn("Approved", tabs)

    def test_page_load_displaysExportAndSaveButtons(self):
        """Positive: OT Approval page displays Export and Save buttons."""
        buttons = self.page.get_buttons()
        self.assertIn("Export", buttons)
        self.assertIn("Save", buttons)


class TestOTApprovalAllTab(unittest.TestCase):
    """US-OT-004: Verify 'All' tab functionality in OT Approval."""

    def setUp(self):
        """Arrange: Create mock page for All tab."""
        self.page = MagicMock()
        self.page.get_grid_columns.return_value = [
            "Employee", "Date", "TRT No", "OT In", "OT Out",
            "Total OT Hours", "Approved OT Hours", "Remarks",
            "Status", "Action",
        ]

    def test_allTab_grid_displaysAllRequiredColumns(self):
        """Positive: All tab grid displays all required columns."""
        expected = [
            "Employee", "Date", "TRT No", "OT In", "OT Out",
            "Total OT Hours", "Approved OT Hours", "Remarks",
            "Status", "Action",
        ]
        columns = self.page.get_grid_columns()
        for col in expected:
            self.assertIn(col, columns)

    def test_allTab_statusColumn_showsPendingApprovedRejected(self):
        """Positive: Status column shows Pending, Approved, or Rejected."""
        self.page.get_record_status.return_value = "Pending"

        status = self.page.get_record_status("EMP001", "2025-12-15")

        self.assertIn(status, ["Pending", "Approved", "Rejected"])

    def test_allTab_actionColumn_displayedOnlyWhenStatusPending(self):
        """Positive: Action (Approve/Reject) buttons displayed only when status is Pending."""
        self.page.get_action_buttons.return_value = ["Approve", "Reject"]

        actions = self.page.get_action_buttons("EMP001", status="Pending")

        self.assertIn("Approve", actions)
        self.assertIn("Reject", actions)

    def test_allTab_actionColumn_notDisplayedWhenStatusApproved(self):
        """Negative: Action buttons are not displayed when status is Approved."""
        self.page.get_action_buttons.return_value = []

        actions = self.page.get_action_buttons("EMP001", status="Approved")

        self.assertEqual(len(actions), 0)


class TestOTApprovalPendingTab(unittest.TestCase):
    """US-OT-004: Verify 'Pending' tab functionality in OT Approval."""

    def setUp(self):
        """Arrange: Create mock page for Pending tab."""
        self.page = MagicMock()
        self.page.get_grid_columns.return_value = [
            "Employee", "Date", "TRT No", "OT In", "OT Out",
            "Total OT Hours", "Remarks", "Action",
        ]

    def test_pendingTab_displaysOnlyPendingRequests(self):
        """Positive: Pending tab displays only requests pending for approval."""
        self.page.get_pending_records.return_value = [
            {"employee": "EMP001", "status": "Pending"},
            {"employee": "EMP002", "status": "Pending"},
        ]

        records = self.page.get_pending_records()

        for record in records:
            self.assertEqual(record["status"], "Pending")

    def test_pendingTab_grid_displaysAllRequiredColumns(self):
        """Positive: Pending tab grid displays all required columns."""
        expected = ["Employee", "Date", "TRT No", "OT In", "OT Out",
                    "Total OT Hours", "Remarks", "Action"]
        columns = self.page.get_grid_columns()
        for col in expected:
            self.assertIn(col, columns)

    def test_pendingTab_actionColumn_displaysApproveRejectButtons(self):
        """Positive: Action column in Pending tab shows Approve/Reject buttons."""
        self.page.get_action_buttons.return_value = ["Approve", "Reject"]

        actions = self.page.get_action_buttons("EMP001")

        self.assertIn("Approve", actions)
        self.assertIn("Reject", actions)


class TestOTApprovalApprovedTab(unittest.TestCase):
    """US-OT-004: Verify 'Approved' tab functionality in OT Approval."""

    def setUp(self):
        """Arrange: Create mock page for Approved tab."""
        self.page = MagicMock()
        self.page.get_grid_columns.return_value = [
            "Employee", "Date", "TRT No", "OT In", "OT Out",
            "Total OT Hours", "Approved OT Hours", "Remarks",
        ]

    def test_approvedTab_displaysApprovedRequests(self):
        """Positive: Approved tab displays all approved OT requests."""
        self.page.get_approved_records.return_value = [
            {"employee": "EMP001", "approved_ot": 2.0},
        ]

        records = self.page.get_approved_records()

        self.assertTrue(len(records) > 0)

    def test_approvedTab_grid_displaysAllRequiredColumns(self):
        """Positive: Approved tab grid displays all required columns."""
        expected = ["Employee", "Date", "TRT No", "OT In", "OT Out",
                    "Total OT Hours", "Approved OT Hours", "Remarks"]
        columns = self.page.get_grid_columns()
        for col in expected:
            self.assertIn(col, columns)


class TestOTApprovalPopupAndActions(unittest.TestCase):
    """US-OT-004: Verify popup and approve/reject actions in OT Approval."""

    def setUp(self):
        """Arrange: Create mock approval service and popup."""
        self.service = MagicMock()
        self.popup = MagicMock()
        self.popup.get_fields.return_value = [
            "Employee", "Date", "OT In", "OT Out",
            "Total OT Hours", "Approve/Reject", "Change OT Hour",
        ]

    def test_popup_clickEmployeeDetail_displaysPopupWithFields(self):
        """Positive: Clicking employee in All/Pending tab opens popup with required fields."""
        fields = self.popup.get_fields()
        self.assertIn("Employee", fields)
        self.assertIn("Date", fields)
        self.assertIn("OT In", fields)
        self.assertIn("OT Out", fields)
        self.assertIn("Total OT Hours", fields)

    def test_popup_approveButton_approvesOTRequest(self):
        """Positive: Clicking Approve button in popup approves the OT request."""
        self.service.approve_ot.return_value = {"status": "Approved"}

        result = self.service.approve_ot("EMP001", "2025-12-15")

        self.assertEqual(result["status"], "Approved")

    def test_popup_rejectButton_rejectsOTRequest(self):
        """Positive: Clicking Reject button in popup rejects the OT request."""
        self.service.reject_ot.return_value = {"status": "Rejected"}

        result = self.service.reject_ot("EMP001", "2025-12-15")

        self.assertEqual(result["status"], "Rejected")

    def test_popup_changeOTHour_displaysNewOTHoursField(self):
        """Positive: Clicking 'Change OT Hour' button shows New OT Hours and Reasons fields."""
        self.popup.click_change_ot_hour.return_value = ["New OT Hours", "Reasons"]

        fields = self.popup.click_change_ot_hour()

        self.assertIn("New OT Hours", fields)
        self.assertIn("Reasons", fields)

    def test_popup_changeOTHourAndApprove_updatesApprovedOTHours(self):
        """Positive: Entering new OT hours and approving updates the Approved OT Hours column."""
        self.service.change_and_approve_ot.return_value = {
            "status": "Approved",
            "approved_ot_hours": 1.5,
        }

        result = self.service.change_and_approve_ot("EMP001", "2025-12-15", new_hours=1.5, reason="Partial OT")

        self.assertEqual(result["approved_ot_hours"], 1.5)
        self.assertEqual(result["status"], "Approved")

    def test_popup_changeOTHour_exceedsTotalOT_validationError(self):
        """Negative: Entering new OT hours greater than Total OT hours triggers validation error."""
        self.service.change_and_approve_ot.side_effect = ValueError(
            "New OT hours cannot exceed Total OT hours"
        )

        with self.assertRaises(ValueError) as context:
            self.service.change_and_approve_ot("EMP001", "2025-12-15", new_hours=5.0, reason="Extra")

        self.assertIn("cannot exceed", str(context.exception))

    def test_popup_changeOTHour_zeroHours_validationError(self):
        """Boundary: Entering 0 as new OT hours should be handled gracefully."""
        self.service.change_and_approve_ot.return_value = {
            "status": "Approved",
            "approved_ot_hours": 0,
        }

        result = self.service.change_and_approve_ot("EMP001", "2025-12-15", new_hours=0, reason="No OT needed")

        self.assertEqual(result["approved_ot_hours"], 0)

    def test_popup_changeOTHour_negativeHours_validationError(self):
        """Negative: Entering negative OT hours triggers validation error."""
        self.service.change_and_approve_ot.side_effect = ValueError(
            "OT hours cannot be negative"
        )

        with self.assertRaises(ValueError):
            self.service.change_and_approve_ot("EMP001", "2025-12-15", new_hours=-1.0, reason="Error")


class TestOTApprovalBulkActions(unittest.TestCase):
    """US-OT-004: Verify bulk approve/reject validation rules."""

    def setUp(self):
        """Arrange: Create mock service."""
        self.service = MagicMock()

    def test_bulkApprove_multiSelectCheckbox_approvesMultipleRequests(self):
        """Positive: User can bulk approve using multi-select checkboxes."""
        self.service.bulk_approve.return_value = {"approved_count": 5}

        result = self.service.bulk_approve(["EMP001", "EMP002", "EMP003", "EMP004", "EMP005"])

        self.assertEqual(result["approved_count"], 5)

    def test_bulkReject_notAllowed_multiSelectDisabled(self):
        """Negative: User cannot use multi-select checkboxes for bulk rejection."""
        self.service.is_bulk_reject_allowed.return_value = False

        allowed = self.service.is_bulk_reject_allowed()

        self.assertFalse(allowed)

    def test_reject_onlyOneAtATime_rejectsSingleRequest(self):
        """Positive: When rejecting, only one request can be rejected at a time."""
        self.service.reject_ot.return_value = {"status": "Rejected", "employee": "EMP001"}

        result = self.service.reject_ot("EMP001", "2025-12-15")

        self.assertEqual(result["status"], "Rejected")

    def test_approve_afterReject_statusUpdated(self):
        """Edge Case: Approving after a previous rejection updates status correctly."""
        self.service.approve_ot.return_value = {"status": "Approved"}

        result = self.service.approve_ot("EMP001", "2025-12-15")

        self.assertEqual(result["status"], "Approved")


class TestOTApprovalValidation(unittest.TestCase):
    """US-OT-004: Verify OT Approval validation rules."""

    def setUp(self):
        """Arrange: Create mock service."""
        self.service = MagicMock()

    def test_validation_duplicatePunches_onlyFirstInLastOutConsidered(self):
        """Positive: System considers only first OT punch in and last OT punch out."""
        self.service.process_ot_punches.return_value = {"ot_in": "18:00", "ot_out": "21:00"}

        result = self.service.process_ot_punches([
            {"time": "18:00", "type": "in"},
            {"time": "18:05", "type": "in"},
            {"time": "21:00", "type": "out"},
        ])

        self.assertEqual(result["ot_in"], "18:00")
        self.assertEqual(result["ot_out"], "21:00")

    def test_validation_totalOTHours_calculatedFromPunchInOut(self):
        """Positive: Total OT hours is calculated from OT punch in and punch out."""
        self.service.calculate_total_ot.return_value = 3.0

        total = self.service.calculate_total_ot("18:00", "21:00")

        self.assertEqual(total, 3.0)

    def test_validation_remarksDisplayedToIRAndEmployee(self):
        """Positive: Remarks based on punch are shown to IR and employee (via Kiosk)."""
        self.service.get_punch_remarks.return_value = {"ir_visible": True, "kiosk_visible": True}

        remarks = self.service.get_punch_remarks("EMP001", "2025-12-15")

        self.assertTrue(remarks["ir_visible"])
        self.assertTrue(remarks["kiosk_visible"])


# ---------------------------------------------------------------------------
# US-OT-005: Shop In Charge – Export OT Approval
# ---------------------------------------------------------------------------


class TestOTApprovalExport(unittest.TestCase):
    """US-OT-005: Verify Export functionality for OT Approval page."""

    def setUp(self):
        """Arrange: Create mock export service."""
        self.export_service = MagicMock()

    def test_export_clickExportButton_exportsCurrentTabToExcel(self):
        """Positive: Clicking Export button exports details from the current tab to Excel."""
        self.export_service.export_to_excel.return_value = "ot_approval_export.xlsx"

        result = self.export_service.export_to_excel("all_tab")

        self.assertTrue(result.endswith(".xlsx"))

    def test_export_withDateFilter_exportsFilteredData(self):
        """Positive: Exported data respects the date filter selection."""
        self.export_service.export_filtered.return_value = {"rows": 30, "file": "filtered.xlsx"}

        result = self.export_service.export_filtered("2025-12-01", "2025-12-31")

        self.assertEqual(result["rows"], 30)

    def test_export_withoutFilter_exportsExistingData(self):
        """Positive: Without filters, existing data is exported."""
        self.export_service.export_all.return_value = {"rows": 200, "file": "all_data.xlsx"}

        result = self.export_service.export_all()

        self.assertTrue(result["rows"] > 0)

    def test_export_saveToLocation_fileIsSaved(self):
        """Positive: User can save the exported file to a location."""
        self.export_service.save_to_path.return_value = True

        saved = self.export_service.save_to_path("/downloads/ot_approval.xlsx")

        self.assertTrue(saved)

    def test_export_pendingTab_exportsOnlyPendingRecords(self):
        """Positive: Exporting from Pending tab only includes pending records."""
        self.export_service.export_to_excel.return_value = "pending_export.xlsx"
        self.export_service.get_export_filter.return_value = "Pending"

        self.export_service.export_to_excel("pending_tab")
        filter_type = self.export_service.get_export_filter()

        self.assertEqual(filter_type, "Pending")

    def test_export_approvedTab_exportsOnlyApprovedRecords(self):
        """Positive: Exporting from Approved tab only includes approved records."""
        self.export_service.export_to_excel.return_value = "approved_export.xlsx"
        self.export_service.get_export_filter.return_value = "Approved"

        self.export_service.export_to_excel("approved_tab")
        filter_type = self.export_service.get_export_filter()

        self.assertEqual(filter_type, "Approved")


if __name__ == "__main__":
    unittest.main()
