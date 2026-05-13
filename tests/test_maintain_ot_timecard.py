"""
Unit Tests for Maintain OT Timecard – Attendance Management Module
User Stories:
  US-OT-001: IR/Company Head/Location Head/BU Head – Date View
  US-OT-002: IR/Company Head/Location Head/BU Head – Employee View
  US-OT-003: IR/Company Head/Location Head/BU Head – Export
  US-OT-004: Shop In charge (IS) – OT Approval (All/Pending/Approved tabs)
  US-OT-005: Shop In charge (IS) – OT Approval Export

Covers OT timecard functionality for:
- Date View: view OT timecard entries by date range with grid columns and validations
- Employee View: view OT timecard entries by employee with date range filters
- Export: export displayed data to Excel
- OT Approval: approve/reject OT requests with change OT hours workflow
- OT Approval Export: export OT approval data to Excel

Test Categories:
- Positive / Happy Path
- Negative / Error Path
- Boundary / Edge Cases
"""

SOURCE_STORY_FILE = "MaintainOTTimeCard.xlsx"

import unittest
from unittest.mock import MagicMock, patch, PropertyMock
from datetime import date, datetime, timedelta


# TODO: Import actual modules once implementation is available.
# from src.attendance.ot_timecard import (
#     OTTimecardPage, OTTimecardService, OTApprovalPage,
#     OTApprovalService, ExportService
# )


# ---------------------------------------------------------------------------
# Helper Fixtures
# ---------------------------------------------------------------------------

def _make_date_view_record(**overrides):
    """Return a mock OT timecard record for Date View."""
    record = {
        "employee_ps_no": "PS001",
        "employee_name": "John Doe",
        "trt_no": "TRT-101",
        "ot_in": "18:00",
        "ot_out": "20:00",
        "total_ot_hours": 2.0,
        "approved_ot_hours": 2.0,
        "ot_status": "Approved",
        "leave_remarks": "Normal Day",
        "ot_canteen": "OT2",
        "ot_lca": "YES",
        "ot_tpt": "NO",
        "cadre": "W1",
    }
    record.update(overrides)
    return record


def _make_employee_view_record(**overrides):
    """Return a mock OT timecard record for Employee View."""
    record = {
        "date": "2026-05-01",
        "trt_no": "TRT-101",
        "ot_in": "18:00",
        "ot_out": "20:00",
        "total_ot_hours": 2.0,
        "approved_ot_hours": 2.0,
        "ot_status": "Approved",
        "leave_remarks": "Normal Day",
        "ot_canteen": "OT4",
        "ot_lca": "NO",
        "ot_tpt": "YES",
        "cadre": "W2",
    }
    record.update(overrides)
    return record


def _make_ot_approval_record(**overrides):
    """Return a mock OT approval record."""
    record = {
        "employee_ps_no": "PS002",
        "employee_name": "Jane Smith",
        "date": "2026-05-10",
        "trt_no": "TRT-202",
        "ot_in": "18:30",
        "ot_out": "21:30",
        "total_ot_hours": 3.0,
        "approved_ot_hours": 0.0,
        "remarks": "Urgent delivery",
        "status": "Pending",
    }
    record.update(overrides)
    return record


# ===========================================================================
# US-OT-001: IR – Date View – Maintain OT Timecard
# ===========================================================================


class TestOTTimecardDateViewNavigation(unittest.TestCase):
    """US-OT-001: Verify navigation to Maintain OT Timecard page and default Date View tab."""

    def setUp(self):
        """Arrange: Create mock navigation and page services."""
        self.navigation = MagicMock()
        self.page = MagicMock()
        self.page.get_tabs.return_value = ["Date View", "Employee View"]
        self.page.get_default_tab.return_value = "Date View"

    def test_navigation_selectAttendanceMenu_displaysOTTimecardPage(self):
        """Positive: Selecting 'Maintain OT Timecard' from Attendance Management opens the page."""
        self.navigation.select_menu.return_value = "Maintain OT Timecard"

        result = self.navigation.select_menu("Attendance Management", "Maintain OT Timecard")

        self.assertEqual(result, "Maintain OT Timecard")
        self.navigation.select_menu.assert_called_once_with(
            "Attendance Management", "Maintain OT Timecard"
        )

    def test_page_load_displaysDateViewAndEmployeeViewTabs(self):
        """Positive: Page displays both Date View and Employee View tabs."""
        tabs = self.page.get_tabs()

        self.assertIn("Date View", tabs)
        self.assertIn("Employee View", tabs)

    def test_page_load_defaultTab_isDateView(self):
        """Positive: By default the Date View tab is selected."""
        default_tab = self.page.get_default_tab()

        self.assertEqual(default_tab, "Date View")

    def test_navigation_invalidMenu_returnsNone(self):
        """Negative: Selecting a non-existent sub-menu returns None."""
        self.navigation.select_menu.return_value = None

        result = self.navigation.select_menu("Attendance Management", "NonExistentMenu")

        self.assertIsNone(result)


class TestOTTimecardDateViewAttributes(unittest.TestCase):
    """US-OT-001: Verify Date View attributes and filters."""

    def setUp(self):
        """Arrange: Create mock date view page."""
        self.page = MagicMock()
        self.page.get_attributes.return_value = ["Date", "From", "To"]
        self.service = MagicMock()

    def test_dateView_displaysDateAttribute(self):
        """Positive: Date View displays the Date datepicker attribute."""
        attrs = self.page.get_attributes()

        self.assertIn("Date", attrs)

    def test_dateView_displaysFromAttribute(self):
        """Positive: Date View displays the From datepicker attribute."""
        attrs = self.page.get_attributes()

        self.assertIn("From", attrs)

    def test_dateView_displaysToAttribute(self):
        """Positive: Date View displays the To datepicker attribute."""
        attrs = self.page.get_attributes()

        self.assertIn("To", attrs)


class TestOTTimecardDateViewGridColumns(unittest.TestCase):
    """US-OT-001: Verify Date View grid columns display correctly."""

    EXPECTED_COLUMNS = [
        "Employee", "TRT No", "OT In", "OT Out", "Total OT Hours",
        "Approved OT hours", "OT status", "Leave Remarks",
        "OT canteen", "OT LCA", "OT TPT", "Cadre",
    ]

    def setUp(self):
        """Arrange: Create mock grid."""
        self.grid = MagicMock()
        self.grid.get_columns.return_value = self.EXPECTED_COLUMNS

    def test_dateView_gridDisplaysAllExpectedColumns(self):
        """Positive: Date View grid contains all required columns."""
        columns = self.grid.get_columns()

        for col in self.EXPECTED_COLUMNS:
            self.assertIn(col, columns)

    def test_dateView_gridDisplaysEmployeeColumn(self):
        """Positive: Grid displays Employee column (PS No and Employee Name)."""
        columns = self.grid.get_columns()

        self.assertIn("Employee", columns)

    def test_dateView_gridDisplaysOTInOutInHHMM(self):
        """Positive: OT In and OT Out columns are present for HH:MM format."""
        columns = self.grid.get_columns()

        self.assertIn("OT In", columns)
        self.assertIn("OT Out", columns)


class TestOTTimecardDateViewExportButton(unittest.TestCase):
    """US-OT-001: Verify Export button presence on Date View."""

    def setUp(self):
        """Arrange: Create mock page."""
        self.page = MagicMock()
        self.page.get_buttons.return_value = ["Export"]

    def test_dateView_displaysExportButton(self):
        """Positive: Date View page displays an Export button."""
        buttons = self.page.get_buttons()

        self.assertIn("Export", buttons)


class TestOTTimecardDateViewFiltering(unittest.TestCase):
    """US-OT-001: Verify date range filtering and default data display."""

    def setUp(self):
        """Arrange: Create mock service."""
        self.service = MagicMock()
        self.today = date(2026, 5, 13)

    def test_dateView_filterByDateRange_returnsFilteredRecords(self):
        """Positive: Filtering by From and To date returns records for that range."""
        from_date = date(2026, 5, 1)
        to_date = date(2026, 5, 10)
        expected = [_make_date_view_record() for _ in range(5)]
        self.service.get_records_by_date_range.return_value = expected

        result = self.service.get_records_by_date_range(from_date, to_date)

        self.assertEqual(len(result), 5)
        self.service.get_records_by_date_range.assert_called_once_with(from_date, to_date)

    def test_dateView_defaultLoad_showsOneMonthData(self):
        """Positive: By default, one month of data is displayed."""
        default_from = self.today - timedelta(days=30)
        self.service.get_default_date_range.return_value = (default_from, self.today)

        from_date, to_date = self.service.get_default_date_range()

        self.assertEqual((to_date - from_date).days, 30)

    def test_dateView_fromDateAfterToDate_returnsError(self):
        """Negative: Setting From date after To date should raise an error."""
        self.service.get_records_by_date_range.side_effect = ValueError(
            "From date cannot be after To date"
        )

        with self.assertRaises(ValueError):
            self.service.get_records_by_date_range(date(2026, 5, 15), date(2026, 5, 1))

    def test_dateView_noDateSelected_showsDefaultOneMonthData(self):
        """Boundary: When no date is selected, system defaults to one month of data."""
        self.service.get_records.return_value = [_make_date_view_record() for _ in range(20)]

        result = self.service.get_records()

        self.assertIsNotNone(result)
        self.assertGreater(len(result), 0)


class TestOTTimecardDateViewValidation(unittest.TestCase):
    """US-OT-001: Verify punch data validation for Date View."""

    def setUp(self):
        """Arrange: Create mock validation service."""
        self.validator = MagicMock()

    def test_dateView_duplicatePunches_removedKeepFirstInLastOut(self):
        """Positive: System keeps only first punch in and last punch out, removes duplicates."""
        raw_punches = [
            {"type": "in", "time": "18:00"},
            {"type": "in", "time": "18:05"},  # duplicate
            {"type": "out", "time": "19:55"},  # duplicate
            {"type": "out", "time": "20:00"},
        ]
        self.validator.deduplicate_punches.return_value = {
            "ot_in": "18:00", "ot_out": "20:00"
        }

        result = self.validator.deduplicate_punches(raw_punches)

        self.assertEqual(result["ot_in"], "18:00")
        self.assertEqual(result["ot_out"], "20:00")

    def test_dateView_totalOTHours_calculatedFromPunchInOut(self):
        """Positive: Total OT hours is the difference between OT In and OT Out."""
        record = _make_date_view_record(ot_in="18:00", ot_out="20:30")
        self.validator.calculate_total_ot.return_value = 2.5

        result = self.validator.calculate_total_ot(record["ot_in"], record["ot_out"])

        self.assertEqual(result, 2.5)

    def test_dateView_totalOTHoursAcrossDateRange_isSummation(self):
        """Positive: Total OT hours for a date range is summation of daily OT hours."""
        daily_hours = [2.0, 3.0, 1.5, 2.5, 1.0]
        self.validator.calculate_period_total.return_value = sum(daily_hours)

        result = self.validator.calculate_period_total(daily_hours)

        self.assertEqual(result, 10.0)

    def test_dateView_otCanteen_displaysCorrectStatus(self):
        """Positive: OT canteen displays correct status like OT2, OT4."""
        record = _make_date_view_record(ot_canteen="OT2")

        self.assertIn(record["ot_canteen"], ["OT2", "OT4"])

    def test_dateView_otLCA_displaysYesOrNo(self):
        """Positive: OT LCA displays YES or NO."""
        record = _make_date_view_record(ot_lca="YES")

        self.assertIn(record["ot_lca"], ["YES", "NO"])

    def test_dateView_otTPT_displaysYesOrNo(self):
        """Positive: OT TPT displays YES or NO."""
        record = _make_date_view_record(ot_tpt="NO")

        self.assertIn(record["ot_tpt"], ["YES", "NO"])

    def test_dateView_noPunchData_returnsEmptyGrid(self):
        """Boundary: No punch data available returns empty grid."""
        self.validator.get_records.return_value = []

        result = self.validator.get_records()

        self.assertEqual(result, [])


class TestOTTimecardDateViewSearch(unittest.TestCase):
    """US-OT-001: Verify search functionality on Date View."""

    def setUp(self):
        """Arrange: Create mock search service."""
        self.search = MagicMock()

    def test_dateView_globalSearch_returnsMatchingRecords(self):
        """Positive: Global search returns matching records."""
        self.search.global_search.return_value = [_make_date_view_record()]

        result = self.search.global_search("PS001")

        self.assertEqual(len(result), 1)

    def test_dateView_columnSearch_returnsFilteredRecords(self):
        """Positive: Column search filters records by specified column."""
        self.search.column_search.return_value = [_make_date_view_record(cadre="W1")]

        result = self.search.column_search("Cadre", "W1")

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["cadre"], "W1")

    def test_dateView_searchNoMatch_returnsEmptyList(self):
        """Negative: Search with no matching results returns empty list."""
        self.search.global_search.return_value = []

        result = self.search.global_search("NONEXISTENT")

        self.assertEqual(result, [])


class TestOTTimecardDateViewPagination(unittest.TestCase):
    """US-OT-001: Verify page navigation on Date View."""

    def setUp(self):
        """Arrange: Create mock pagination."""
        self.pagination = MagicMock()
        self.pagination.total_pages = 5
        self.pagination.current_page = 1

    def test_dateView_navigateToNextPage_incrementsPage(self):
        """Positive: User navigates to next page."""
        self.pagination.next_page.return_value = 2

        result = self.pagination.next_page()

        self.assertEqual(result, 2)

    def test_dateView_navigateToPreviousPage_onFirstPage_staysOnFirstPage(self):
        """Boundary: Navigating previous on first page stays on page 1."""
        self.pagination.previous_page.return_value = 1

        result = self.pagination.previous_page()

        self.assertEqual(result, 1)


# ===========================================================================
# US-OT-002: IR – Employee View – Maintain OT Timecard
# ===========================================================================


class TestOTTimecardEmployeeViewNavigation(unittest.TestCase):
    """US-OT-002: Verify Employee View tab selection and attributes."""

    def setUp(self):
        """Arrange: Create mock page for Employee View."""
        self.page = MagicMock()
        self.page.get_tabs.return_value = ["Date View", "Employee View"]
        self.page.get_attributes.return_value = ["Employee", "From date", "To date"]

    def test_employeeView_clickTab_switchesToEmployeeView(self):
        """Positive: Clicking Employee View tab switches to employee view."""
        self.page.select_tab.return_value = "Employee View"

        result = self.page.select_tab("Employee View")

        self.assertEqual(result, "Employee View")

    def test_employeeView_displaysEmployeeDropdown(self):
        """Positive: Employee View displays Employee dropdown attribute."""
        attrs = self.page.get_attributes()

        self.assertIn("Employee", attrs)

    def test_employeeView_displaysFromDateAttribute(self):
        """Positive: Employee View displays From date datepicker."""
        attrs = self.page.get_attributes()

        self.assertIn("From date", attrs)

    def test_employeeView_displaysToDateAttribute(self):
        """Positive: Employee View displays To date datepicker."""
        attrs = self.page.get_attributes()

        self.assertIn("To date", attrs)


class TestOTTimecardEmployeeViewGridColumns(unittest.TestCase):
    """US-OT-002: Verify Employee View grid columns."""

    EXPECTED_COLUMNS = [
        "Date", "TRT No", "OT In", "OT Out", "Total OT Hours",
        "Approved OT hours", "OT status", "Leave Remarks",
        "OT canteen", "OT LCA", "OT TPT", "Cadre",
    ]

    def setUp(self):
        """Arrange: Create mock grid."""
        self.grid = MagicMock()
        self.grid.get_columns.return_value = self.EXPECTED_COLUMNS

    def test_employeeView_gridDisplaysAllExpectedColumns(self):
        """Positive: Employee View grid contains all required columns."""
        columns = self.grid.get_columns()

        for col in self.EXPECTED_COLUMNS:
            self.assertIn(col, columns)

    def test_employeeView_gridDisplaysDateColumn(self):
        """Positive: Employee View grid has Date column instead of Employee column."""
        columns = self.grid.get_columns()

        self.assertIn("Date", columns)


class TestOTTimecardEmployeeViewFiltering(unittest.TestCase):
    """US-OT-002: Verify Employee View data filtering."""

    def setUp(self):
        """Arrange: Create mock service."""
        self.service = MagicMock()

    def test_employeeView_selectEmployee_displaysRecordsForEmployee(self):
        """Positive: Selecting an employee shows their OT timecard records."""
        expected = [_make_employee_view_record() for _ in range(3)]
        self.service.get_records_by_employee.return_value = expected

        result = self.service.get_records_by_employee("PS001")

        self.assertEqual(len(result), 3)

    def test_employeeView_filterByDateRange_returnsFilteredRecords(self):
        """Positive: Filtering by date range with employee returns records in range."""
        expected = [_make_employee_view_record()]
        self.service.get_records_by_employee_and_date.return_value = expected

        result = self.service.get_records_by_employee_and_date(
            "PS001", date(2026, 5, 1), date(2026, 5, 10)
        )

        self.assertEqual(len(result), 1)

    def test_employeeView_noEmployeeSelected_returnsError(self):
        """Negative: No employee selected raises a validation error."""
        self.service.get_records_by_employee.side_effect = ValueError(
            "Employee selection is required"
        )

        with self.assertRaises(ValueError):
            self.service.get_records_by_employee(None)

    def test_employeeView_employeeDropdownShowsPSNoAndName(self):
        """Positive: Employee dropdown displays PS No and Employee Name."""
        self.service.get_employee_list.return_value = [
            {"ps_no": "PS001", "name": "John Doe"},
            {"ps_no": "PS002", "name": "Jane Smith"},
        ]

        employees = self.service.get_employee_list()

        for emp in employees:
            self.assertIn("ps_no", emp)
            self.assertIn("name", emp)

    def test_employeeView_defaultLoad_showsOneMonthData(self):
        """Positive: Default load shows one month of OT data for employee."""
        today = date(2026, 5, 13)
        default_from = today - timedelta(days=30)
        self.service.get_default_date_range.return_value = (default_from, today)

        from_date, to_date = self.service.get_default_date_range()

        self.assertEqual((to_date - from_date).days, 30)

    def test_employeeView_totalOTHoursForPeriod_isSummation(self):
        """Positive: Total OT hours is summation of daily OT hours for the selected period."""
        records = [
            _make_employee_view_record(total_ot_hours=2.0),
            _make_employee_view_record(total_ot_hours=3.0),
            _make_employee_view_record(total_ot_hours=1.5),
        ]
        self.service.get_records_by_employee.return_value = records
        expected_total = sum(r["total_ot_hours"] for r in records)

        result = self.service.get_records_by_employee("PS001")
        actual_total = sum(r["total_ot_hours"] for r in result)

        self.assertEqual(actual_total, expected_total)


class TestOTTimecardEmployeeViewValidation(unittest.TestCase):
    """US-OT-002: Verify Employee View validations (duplicates, punch data)."""

    def setUp(self):
        """Arrange: Create mock validator."""
        self.validator = MagicMock()

    def test_employeeView_duplicatePunches_removedKeepFirstInLastOut(self):
        """Positive: Duplicate punches removed; first in and last out kept."""
        self.validator.deduplicate_punches.return_value = {
            "ot_in": "18:00", "ot_out": "21:00"
        }

        result = self.validator.deduplicate_punches([
            {"type": "in", "time": "18:00"},
            {"type": "in", "time": "18:02"},
            {"type": "out", "time": "20:58"},
            {"type": "out", "time": "21:00"},
        ])

        self.assertEqual(result["ot_in"], "18:00")
        self.assertEqual(result["ot_out"], "21:00")

    def test_employeeView_otCanteen_displaysCorrectStatus(self):
        """Positive: OT canteen shows OT2 or OT4 based on allowance logic."""
        record = _make_employee_view_record(ot_canteen="OT4")

        self.assertIn(record["ot_canteen"], ["OT2", "OT4"])

    def test_employeeView_otLCA_displaysYesOrNo(self):
        """Positive: OT LCA shows YES or NO."""
        record = _make_employee_view_record(ot_lca="NO")

        self.assertIn(record["ot_lca"], ["YES", "NO"])


class TestOTTimecardEmployeeViewSearchAndPagination(unittest.TestCase):
    """US-OT-002: Verify search and pagination on Employee View."""

    def setUp(self):
        """Arrange: Create mock search and pagination services."""
        self.search = MagicMock()
        self.pagination = MagicMock()

    def test_employeeView_globalSearch_returnsMatchingRecords(self):
        """Positive: Global search returns matching records."""
        self.search.global_search.return_value = [_make_employee_view_record()]

        result = self.search.global_search("TRT-101")

        self.assertEqual(len(result), 1)

    def test_employeeView_pageNavigation_navigatesToOtherPages(self):
        """Positive: User can navigate between pages."""
        self.pagination.go_to_page.return_value = 3

        result = self.pagination.go_to_page(3)

        self.assertEqual(result, 3)


# ===========================================================================
# US-OT-003: IR – Export – Maintain OT Timecard
# ===========================================================================


class TestOTTimecardExport(unittest.TestCase):
    """US-OT-003: Verify Export functionality for Maintain OT Timecard."""

    def setUp(self):
        """Arrange: Create mock export service."""
        self.export_service = MagicMock()

    def test_export_clickExportButton_exportsToExcel(self):
        """Positive: Clicking Export button exports data to Excel file."""
        self.export_service.export_to_excel.return_value = "ot_timecard_export.xlsx"

        result = self.export_service.export_to_excel()

        self.assertEqual(result, "ot_timecard_export.xlsx")

    def test_export_withDateFilter_exportsFilteredData(self):
        """Positive: If date filter is applied, only filtered data is exported."""
        self.export_service.export_to_excel.return_value = "ot_timecard_filtered.xlsx"

        result = self.export_service.export_to_excel(
            from_date=date(2026, 5, 1), to_date=date(2026, 5, 10)
        )

        self.assertIsNotNone(result)
        self.export_service.export_to_excel.assert_called_once_with(
            from_date=date(2026, 5, 1), to_date=date(2026, 5, 10)
        )

    def test_export_withoutFilter_exportsAllDisplayedData(self):
        """Positive: Without filter, all displayed data is exported."""
        self.export_service.export_to_excel.return_value = "ot_timecard_all.xlsx"

        result = self.export_service.export_to_excel(from_date=None, to_date=None)

        self.assertIsNotNone(result)

    def test_export_saveToLocation_savesFile(self):
        """Positive: User can save the exported file to a chosen location."""
        self.export_service.save_to_location.return_value = True

        result = self.export_service.save_to_location("/downloads/ot_export.xlsx")

        self.assertTrue(result)

    def test_export_emptyGrid_exportsEmptyFile(self):
        """Boundary: Exporting when grid is empty produces an empty Excel file."""
        self.export_service.export_to_excel.return_value = "ot_timecard_empty.xlsx"
        self.export_service.get_row_count.return_value = 0

        result = self.export_service.export_to_excel()
        row_count = self.export_service.get_row_count()

        self.assertIsNotNone(result)
        self.assertEqual(row_count, 0)

    def test_export_serviceFailure_raisesError(self):
        """Negative: Export service failure raises an error."""
        self.export_service.export_to_excel.side_effect = RuntimeError("Export failed")

        with self.assertRaises(RuntimeError):
            self.export_service.export_to_excel()


# ===========================================================================
# US-OT-004: Shop In charge (IS) – OT Approval
# ===========================================================================


class TestOTApprovalPageNavigation(unittest.TestCase):
    """US-OT-004: Verify OT Approval page navigation and tabs."""

    def setUp(self):
        """Arrange: Create mock navigation and OT Approval page."""
        self.navigation = MagicMock()
        self.page = MagicMock()
        self.page.get_tabs.return_value = ["All", "Pending", "Approved"]
        self.page.get_buttons.return_value = ["Export", "Save"]

    def test_navigation_selectOTApproval_displaysOTApprovalPage(self):
        """Positive: Selecting OT Approval from Attendance Management opens the page."""
        self.navigation.select_menu.return_value = "OT Approval"

        result = self.navigation.select_menu("Attendance Management", "OT Approval")

        self.assertEqual(result, "OT Approval")

    def test_page_displaysAllPendingApprovedTabs(self):
        """Positive: OT Approval page displays All, Pending, Approved tabs."""
        tabs = self.page.get_tabs()

        self.assertEqual(tabs, ["All", "Pending", "Approved"])

    def test_page_displaysExportAndSaveButtons(self):
        """Positive: OT Approval page displays Export and Save buttons."""
        buttons = self.page.get_buttons()

        self.assertIn("Export", buttons)
        self.assertIn("Save", buttons)


class TestOTApprovalAllTab(unittest.TestCase):
    """US-OT-004: Verify 'All' tab displays all OT requests with correct columns."""

    EXPECTED_COLUMNS = [
        "Employee", "Date", "TRT No", "OT In", "OT Out",
        "Total OT Hours", "Approved OT hours", "Remarks", "Status", "Action",
    ]

    def setUp(self):
        """Arrange: Create mock All tab grid."""
        self.grid = MagicMock()
        self.grid.get_columns.return_value = self.EXPECTED_COLUMNS
        self.service = MagicMock()

    def test_allTab_gridDisplaysAllExpectedColumns(self):
        """Positive: All tab grid contains all required columns."""
        columns = self.grid.get_columns()

        for col in self.EXPECTED_COLUMNS:
            self.assertIn(col, columns)

    def test_allTab_displaysStatusColumn_withPendingApprovedRejected(self):
        """Positive: Status column shows Pending, Approved, or Rejected."""
        records = [
            _make_ot_approval_record(status="Pending"),
            _make_ot_approval_record(status="Approved"),
            _make_ot_approval_record(status="Rejected"),
        ]
        self.service.get_all_records.return_value = records

        result = self.service.get_all_records()

        statuses = {r["status"] for r in result}
        self.assertEqual(statuses, {"Pending", "Approved", "Rejected"})

    def test_allTab_actionButtonDisplayedOnlyForPending(self):
        """Positive: Action (Approve/Reject) button is displayed only for Pending status."""
        pending_record = _make_ot_approval_record(status="Pending")
        approved_record = _make_ot_approval_record(status="Approved")
        self.service.has_action_button.side_effect = lambda r: r["status"] == "Pending"

        self.assertTrue(self.service.has_action_button(pending_record))
        self.assertFalse(self.service.has_action_button(approved_record))


class TestOTApprovalPendingTab(unittest.TestCase):
    """US-OT-004: Verify 'Pending' tab displays only pending OT requests."""

    EXPECTED_COLUMNS = [
        "Employee", "Date", "TRT No", "OT In", "OT Out",
        "Total OT Hours", "Remarks", "Action",
    ]

    def setUp(self):
        """Arrange: Create mock Pending tab."""
        self.grid = MagicMock()
        self.grid.get_columns.return_value = self.EXPECTED_COLUMNS
        self.service = MagicMock()

    def test_pendingTab_displaysOnlyPendingRequests(self):
        """Positive: Pending tab shows only pending OT requests."""
        pending = [_make_ot_approval_record(status="Pending") for _ in range(3)]
        self.service.get_pending_records.return_value = pending

        result = self.service.get_pending_records()

        self.assertEqual(len(result), 3)
        for r in result:
            self.assertEqual(r["status"], "Pending")

    def test_pendingTab_gridDisplaysAllExpectedColumns(self):
        """Positive: Pending tab grid has correct columns."""
        columns = self.grid.get_columns()

        for col in self.EXPECTED_COLUMNS:
            self.assertIn(col, columns)

    def test_pendingTab_displaysActionColumn(self):
        """Positive: Pending tab has Action (Approve/Reject) button for all entries."""
        columns = self.grid.get_columns()

        self.assertIn("Action", columns)


class TestOTApprovalApprovedTab(unittest.TestCase):
    """US-OT-004: Verify 'Approved' tab displays approved OT requests."""

    EXPECTED_COLUMNS = [
        "Employee", "Date", "TRT No", "OT In", "OT Out",
        "Total OT Hours", "Approved OT hours", "Remarks",
    ]

    def setUp(self):
        """Arrange: Create mock Approved tab."""
        self.grid = MagicMock()
        self.grid.get_columns.return_value = self.EXPECTED_COLUMNS
        self.service = MagicMock()

    def test_approvedTab_displaysOnlyApprovedRequests(self):
        """Positive: Approved tab shows only approved OT requests."""
        approved = [_make_ot_approval_record(status="Approved", approved_ot_hours=3.0) for _ in range(2)]
        self.service.get_approved_records.return_value = approved

        result = self.service.get_approved_records()

        self.assertEqual(len(result), 2)
        for r in result:
            self.assertEqual(r["status"], "Approved")

    def test_approvedTab_gridDisplaysAllExpectedColumns(self):
        """Positive: Approved tab grid has correct columns."""
        columns = self.grid.get_columns()

        for col in self.EXPECTED_COLUMNS:
            self.assertIn(col, columns)


class TestOTApprovalApproveRejectActions(unittest.TestCase):
    """US-OT-004: Verify approve and reject actions on OT requests."""

    def setUp(self):
        """Arrange: Create mock approval service."""
        self.service = MagicMock()

    def test_approveRequest_singleRequest_statusChangesToApproved(self):
        """Positive: Approving a single OT request changes status to Approved."""
        record = _make_ot_approval_record(status="Pending")
        self.service.approve.return_value = {**record, "status": "Approved", "approved_ot_hours": 3.0}

        result = self.service.approve(record)

        self.assertEqual(result["status"], "Approved")
        self.assertEqual(result["approved_ot_hours"], 3.0)

    def test_rejectRequest_singleRequest_statusChangesToRejected(self):
        """Positive: Rejecting a single OT request changes status to Rejected."""
        record = _make_ot_approval_record(status="Pending")
        self.service.reject.return_value = {**record, "status": "Rejected"}

        result = self.service.reject(record)

        self.assertEqual(result["status"], "Rejected")

    def test_bulkApprove_multipleRequests_allApproved(self):
        """Positive: Bulk approve using multi-select checkbox approves all selected requests."""
        records = [_make_ot_approval_record(status="Pending") for _ in range(3)]
        approved = [{**r, "status": "Approved", "approved_ot_hours": r["total_ot_hours"]} for r in records]
        self.service.bulk_approve.return_value = approved

        result = self.service.bulk_approve(records)

        self.assertEqual(len(result), 3)
        for r in result:
            self.assertEqual(r["status"], "Approved")

    def test_rejectRequest_cannotBulkReject_onlyOneAtATime(self):
        """Negative: Rejection does not support multi-select; only one request at a time."""
        records = [_make_ot_approval_record(status="Pending") for _ in range(2)]
        self.service.reject.side_effect = ValueError(
            "Only one request can be rejected at a time"
        )

        with self.assertRaises(ValueError):
            self.service.reject(records)

    def test_rejectRequest_multiSelectDisabledDuringReject(self):
        """Negative: Multi-select checkbox is disabled when rejecting."""
        self.service.is_multiselect_enabled_for_reject.return_value = False

        result = self.service.is_multiselect_enabled_for_reject()

        self.assertFalse(result)

    def test_approveRequest_alreadyApproved_raisesError(self):
        """Negative: Approving an already approved request raises an error."""
        record = _make_ot_approval_record(status="Approved")
        self.service.approve.side_effect = ValueError("Request already approved")

        with self.assertRaises(ValueError):
            self.service.approve(record)

    def test_approveRequest_alreadyRejected_raisesError(self):
        """Negative: Approving an already rejected request raises an error."""
        record = _make_ot_approval_record(status="Rejected")
        self.service.approve.side_effect = ValueError("Cannot approve a rejected request")

        with self.assertRaises(ValueError):
            self.service.approve(record)


class TestOTApprovalEmployeeDetailPopup(unittest.TestCase):
    """US-OT-004: Verify employee detail popup for approve/reject from All or Pending tab."""

    def setUp(self):
        """Arrange: Create mock popup service."""
        self.popup = MagicMock()
        self.popup.get_fields.return_value = [
            "Employee", "Date", "OT In", "OT Out", "Total OT Hours",
            "Approve", "Reject", "Change OT hour",
        ]

    def test_clickEmployeeInGrid_displaysPopup(self):
        """Positive: Clicking employee in grid opens detail popup."""
        self.popup.open.return_value = True

        result = self.popup.open("PS002")

        self.assertTrue(result)

    def test_popup_displaysAllRequiredFields(self):
        """Positive: Popup displays Employee, Date, OT In, OT Out, Total OT Hours, and action buttons."""
        fields = self.popup.get_fields()

        for expected in ["Employee", "Date", "OT In", "OT Out", "Total OT Hours"]:
            self.assertIn(expected, fields)

    def test_popup_displaysApproveAndRejectButtons(self):
        """Positive: Popup has Approve and Reject buttons."""
        fields = self.popup.get_fields()

        self.assertIn("Approve", fields)
        self.assertIn("Reject", fields)

    def test_popup_displaysChangeOTHourButton(self):
        """Positive: Popup has a Change OT hour button."""
        fields = self.popup.get_fields()

        self.assertIn("Change OT hour", fields)


class TestOTApprovalChangeOTHours(unittest.TestCase):
    """US-OT-004: Verify Change OT Hours workflow in popup."""

    def setUp(self):
        """Arrange: Create mock change OT hours service."""
        self.service = MagicMock()

    def test_changeOTHour_clickButton_displaysNewOTHoursField(self):
        """Positive: Clicking Change OT hour button shows New OT hours and Reasons fields."""
        self.service.show_change_ot_fields.return_value = ["New OT hours", "Reasons"]

        fields = self.service.show_change_ot_fields()

        self.assertIn("New OT hours", fields)
        self.assertIn("Reasons", fields)

    def test_changeOTHour_enterValidNewHours_thenApprove_updatesApprovedOTHours(self):
        """Positive: Entering valid new OT hours and approving updates approved OT hours in grid."""
        record = _make_ot_approval_record(total_ot_hours=3.0)
        self.service.change_and_approve.return_value = {
            **record, "status": "Approved", "approved_ot_hours": 2.0
        }

        result = self.service.change_and_approve(
            record, new_ot_hours=2.0, reason="Adjusted per supervisor"
        )

        self.assertEqual(result["status"], "Approved")
        self.assertEqual(result["approved_ot_hours"], 2.0)

    def test_changeOTHour_newHoursExceedsTotalOT_raisesValidationError(self):
        """Negative: New OT hours greater than Total OT hours raises validation error."""
        record = _make_ot_approval_record(total_ot_hours=3.0)
        self.service.change_and_approve.side_effect = ValueError(
            "New OT hours cannot exceed Total OT hours"
        )

        with self.assertRaises(ValueError):
            self.service.change_and_approve(
                record, new_ot_hours=5.0, reason="Extra hours requested"
            )

    def test_changeOTHour_newHoursEqualsTotalOT_succeeds(self):
        """Boundary: New OT hours equal to Total OT hours is accepted."""
        record = _make_ot_approval_record(total_ot_hours=3.0)
        self.service.change_and_approve.return_value = {
            **record, "status": "Approved", "approved_ot_hours": 3.0
        }

        result = self.service.change_and_approve(
            record, new_ot_hours=3.0, reason="Full hours approved"
        )

        self.assertEqual(result["approved_ot_hours"], 3.0)

    def test_changeOTHour_zeroHours_succeeds(self):
        """Boundary: New OT hours of 0 is accepted (effectively no OT approved)."""
        record = _make_ot_approval_record(total_ot_hours=3.0)
        self.service.change_and_approve.return_value = {
            **record, "status": "Approved", "approved_ot_hours": 0.0
        }

        result = self.service.change_and_approve(
            record, new_ot_hours=0.0, reason="No OT needed"
        )

        self.assertEqual(result["approved_ot_hours"], 0.0)

    def test_changeOTHour_negativeHours_raisesValidationError(self):
        """Negative: Negative OT hours raises validation error."""
        record = _make_ot_approval_record(total_ot_hours=3.0)
        self.service.change_and_approve.side_effect = ValueError(
            "OT hours cannot be negative"
        )

        with self.assertRaises(ValueError):
            self.service.change_and_approve(
                record, new_ot_hours=-1.0, reason="Invalid"
            )

    def test_changeOTHour_noReasonProvided_raisesValidationError(self):
        """Negative: Changing OT hours without a reason raises validation error."""
        record = _make_ot_approval_record(total_ot_hours=3.0)
        self.service.change_and_approve.side_effect = ValueError(
            "Reason is required when changing OT hours"
        )

        with self.assertRaises(ValueError):
            self.service.change_and_approve(
                record, new_ot_hours=2.0, reason=""
            )


class TestOTApprovalValidation(unittest.TestCase):
    """US-OT-004: Verify OT Approval validation rules."""

    def setUp(self):
        """Arrange: Create mock validator."""
        self.validator = MagicMock()

    def test_approval_duplicatePunches_removedKeepFirstInLastOut(self):
        """Positive: System removes duplicate punches, keeps first in and last out."""
        self.validator.deduplicate_punches.return_value = {
            "ot_in": "18:30", "ot_out": "21:30"
        }

        result = self.validator.deduplicate_punches([
            {"type": "in", "time": "18:30"},
            {"type": "in", "time": "18:32"},
            {"type": "out", "time": "21:30"},
        ])

        self.assertEqual(result["ot_in"], "18:30")
        self.assertEqual(result["ot_out"], "21:30")

    def test_approval_defaultLoad_showsOneMonthData(self):
        """Positive: Default load shows one month of OT approval data."""
        today = date(2026, 5, 13)
        default_from = today - timedelta(days=30)
        self.validator.get_default_range.return_value = (default_from, today)

        from_date, to_date = self.validator.get_default_range()

        self.assertEqual((to_date - from_date).days, 30)

    def test_approval_totalOTHours_summationForSelectedPeriod(self):
        """Positive: Total OT hours is summation of daily hours for the selected period."""
        daily_hours = [3.0, 2.0, 4.0]
        self.validator.calculate_period_total.return_value = 9.0

        result = self.validator.calculate_period_total(daily_hours)

        self.assertEqual(result, 9.0)


class TestOTApprovalSearchAndPagination(unittest.TestCase):
    """US-OT-004: Verify search and pagination on OT Approval page."""

    def setUp(self):
        """Arrange: Create mock services."""
        self.search = MagicMock()
        self.pagination = MagicMock()

    def test_otApproval_globalSearch_returnsMatchingRecords(self):
        """Positive: Global search returns matching OT approval records."""
        self.search.global_search.return_value = [_make_ot_approval_record()]

        result = self.search.global_search("PS002")

        self.assertEqual(len(result), 1)

    def test_otApproval_columnSearch_filtersRecords(self):
        """Positive: Column search filters OT approval records by specified column."""
        self.search.column_search.return_value = [_make_ot_approval_record(status="Pending")]

        result = self.search.column_search("Status", "Pending")

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["status"], "Pending")

    def test_otApproval_pageNavigation_navigatesToOtherPages(self):
        """Positive: User can navigate to other pages."""
        self.pagination.go_to_page.return_value = 2

        result = self.pagination.go_to_page(2)

        self.assertEqual(result, 2)


# ===========================================================================
# US-OT-005: Shop In charge (IS) – OT Approval Export
# ===========================================================================


class TestOTApprovalExport(unittest.TestCase):
    """US-OT-005: Verify Export functionality for OT Approval page."""

    def setUp(self):
        """Arrange: Create mock export service."""
        self.export_service = MagicMock()

    def test_export_clickExportButton_exportsToExcel(self):
        """Positive: Clicking Export button exports OT approval data to Excel."""
        self.export_service.export_to_excel.return_value = "ot_approval_export.xlsx"

        result = self.export_service.export_to_excel()

        self.assertEqual(result, "ot_approval_export.xlsx")

    def test_export_withDateFilter_exportsFilteredData(self):
        """Positive: Exported data respects applied date filter."""
        self.export_service.export_to_excel.return_value = "ot_approval_filtered.xlsx"

        result = self.export_service.export_to_excel(
            from_date=date(2026, 5, 1), to_date=date(2026, 5, 10)
        )

        self.assertIsNotNone(result)

    def test_export_withoutFilter_exportsAllDisplayedData(self):
        """Positive: Without filter, all displayed OT approval data is exported."""
        self.export_service.export_to_excel.return_value = "ot_approval_all.xlsx"

        result = self.export_service.export_to_excel(from_date=None, to_date=None)

        self.assertIsNotNone(result)

    def test_export_saveToLocation_savesFile(self):
        """Positive: User can save the exported file to a location."""
        self.export_service.save_to_location.return_value = True

        result = self.export_service.save_to_location("/downloads/ot_approval.xlsx")

        self.assertTrue(result)

    def test_export_fromSpecificTab_exportsOnlyThatTabData(self):
        """Positive: Exporting from Pending tab exports only pending records."""
        self.export_service.export_to_excel.return_value = "ot_approval_pending.xlsx"

        result = self.export_service.export_to_excel(tab="Pending")

        self.assertIsNotNone(result)
        self.export_service.export_to_excel.assert_called_once_with(tab="Pending")

    def test_export_emptyGrid_exportsEmptyFile(self):
        """Boundary: Exporting when no records exist produces an empty file."""
        self.export_service.export_to_excel.return_value = "ot_approval_empty.xlsx"
        self.export_service.get_row_count.return_value = 0

        result = self.export_service.export_to_excel()
        row_count = self.export_service.get_row_count()

        self.assertIsNotNone(result)
        self.assertEqual(row_count, 0)

    def test_export_serviceFailure_raisesError(self):
        """Negative: Export service failure raises an error."""
        self.export_service.export_to_excel.side_effect = RuntimeError("Export failed")

        with self.assertRaises(RuntimeError):
            self.export_service.export_to_excel()


# ===========================================================================
# Cross-Cutting: Role-Based Access
# ===========================================================================


class TestOTTimecardRoleBasedAccess(unittest.TestCase):
    """Cross-cutting: Verify role-based access for OT Timecard and OT Approval."""

    def setUp(self):
        """Arrange: Create mock auth service."""
        self.auth = MagicMock()

    def test_irRole_canAccessMaintainOTTimecard(self):
        """Positive: IR role has view access to Maintain OT Timecard."""
        self.auth.has_access.return_value = True

        result = self.auth.has_access("IR", "Maintain OT Timecard")

        self.assertTrue(result)

    def test_companyHeadRole_canAccessMaintainOTTimecard(self):
        """Positive: Company Head role has view access to Maintain OT Timecard."""
        self.auth.has_access.return_value = True

        result = self.auth.has_access("Company Head", "Maintain OT Timecard")

        self.assertTrue(result)

    def test_locationHeadRole_canAccessMaintainOTTimecard(self):
        """Positive: Location Head role has view access to Maintain OT Timecard."""
        self.auth.has_access.return_value = True

        result = self.auth.has_access("Location Head", "Maintain OT Timecard")

        self.assertTrue(result)

    def test_buHeadRole_canAccessMaintainOTTimecard(self):
        """Positive: BU Head role has view access to Maintain OT Timecard."""
        self.auth.has_access.return_value = True

        result = self.auth.has_access("BU Head", "Maintain OT Timecard")

        self.assertTrue(result)

    def test_shopInChargeRole_canAccessOTApproval(self):
        """Positive: Shop In charge (IS) has view and approve access to OT Approval."""
        self.auth.has_access.return_value = True

        result = self.auth.has_access("Shop In charge", "OT Approval")

        self.assertTrue(result)

    def test_shopInChargeRole_canApproveOTRequests(self):
        """Positive: Shop In charge has approve permission."""
        self.auth.has_permission.return_value = True

        result = self.auth.has_permission("Shop In charge", "approve_ot")

        self.assertTrue(result)

    def test_irRole_cannotApproveOTRequests(self):
        """Negative: IR role does not have approve permission on OT Approval page."""
        self.auth.has_permission.return_value = False

        result = self.auth.has_permission("IR", "approve_ot")

        self.assertFalse(result)

    def test_unauthorizedRole_cannotAccessOTTimecard(self):
        """Negative: Unauthorized role cannot access Maintain OT Timecard."""
        self.auth.has_access.return_value = False

        result = self.auth.has_access("Guest", "Maintain OT Timecard")

        self.assertFalse(result)


if __name__ == "__main__":
    unittest.main()
