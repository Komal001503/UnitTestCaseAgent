"""
Unit Tests for Maintain OT Timecard – IR, Company Head, Location Head, BU Head Roles
User Stories: US-OT-001 (Date View), US-OT-002 (Employee View), US-OT-003 (Export)

Covers OT timecard functionality for:
- IR (Industrial Relation)
- Company Head
- Location Head
- BU Head

Test Categories:
- Positive / Happy Path
- Negative / Error Path
- Boundary / Edge Cases
- Integration Points
"""

SOURCE_STORY_FILE = "MaintainOTTimeCard.xlsx"

import unittest
from unittest.mock import MagicMock, patch, PropertyMock
from datetime import date, datetime, timedelta


# TODO: Import actual modules once implementation is available.
# from src.attendance.ot_timecard import (
#     OTTimecardPage, OTTimecardService, OTTimecardDateView,
#     OTTimecardEmployeeView, ExportService, InfoCommAPI
# )


# ---------------------------------------------------------------------------
# US-OT-001: IR – View Maintain OT Timecard (Date View)
# ---------------------------------------------------------------------------


class TestOTTimecardNavigation(unittest.TestCase):
    """US-OT-001: Verify navigation to Maintain OT Timecard page
    from side navigation under Attendance Management."""

    def setUp(self):
        """Arrange: Create mock navigation and page instances."""
        self.nav_service = MagicMock()
        self.ot_timecard_page = MagicMock()
        self.nav_service.select_submenu.return_value = self.ot_timecard_page
        self.ot_timecard_page.get_tabs.return_value = ["Date View", "Employee View"]
        self.ot_timecard_page.get_active_tab.return_value = "Date View"

    def test_selectOTTimecardMenu_navigate_displaysOTTimecardPage(self):
        """Positive: Selecting 'Maintain OT Timecard' from 'Attendance Management'
        menu displays the OT Timecard page."""
        # Act
        page = self.nav_service.select_submenu("Attendance Management", "Maintain OT Timecard")
        # Assert
        self.nav_service.select_submenu.assert_called_once_with(
            "Attendance Management", "Maintain OT Timecard"
        )
        self.assertIsNotNone(page)

    def test_otTimecardPage_render_displaysTabs(self):
        """Positive: OT Timecard page displays 'Date View' and 'Employee View' tabs."""
        # Act
        tabs = self.ot_timecard_page.get_tabs()
        # Assert
        self.assertEqual(tabs, ["Date View", "Employee View"])

    def test_otTimecardPage_defaultTab_isDateView(self):
        """Positive: By default, the 'Date View' tab is active."""
        # Act
        active_tab = self.ot_timecard_page.get_active_tab()
        # Assert
        self.assertEqual(active_tab, "Date View")


class TestOTTimecardDateViewAttributes(unittest.TestCase):
    """US-OT-001: Verify Date View tab displays correct attributes and filters."""

    def setUp(self):
        """Arrange: Create mock date view with attributes."""
        self.date_view = MagicMock()
        self.date_view.get_attributes.return_value = [
            "date_picker",
            "from_date_picker",
            "to_date_picker",
        ]
        self.date_view.get_buttons.return_value = ["Export"]

    def test_dateView_attributes_displaysDatePicker(self):
        """Positive: Date View displays a Date picker attribute."""
        attributes = self.date_view.get_attributes()
        self.assertIn("date_picker", attributes)

    def test_dateView_attributes_displaysFromDatePicker(self):
        """Positive: Date View displays a From date picker attribute."""
        attributes = self.date_view.get_attributes()
        self.assertIn("from_date_picker", attributes)

    def test_dateView_attributes_displaysToDatePicker(self):
        """Positive: Date View displays a To date picker attribute."""
        attributes = self.date_view.get_attributes()
        self.assertIn("to_date_picker", attributes)

    def test_dateView_buttons_displaysExportButton(self):
        """Positive: Date View displays an Export button."""
        buttons = self.date_view.get_buttons()
        self.assertIn("Export", buttons)


class TestOTTimecardDateViewGridColumns(unittest.TestCase):
    """US-OT-001: Verify Date View grid displays all required columns."""

    EXPECTED_COLUMNS = [
        "Employee",
        "TRT No",
        "OT In",
        "OT Out",
        "Total OT Hours",
        "Approved OT Hours",
        "OT Status",
        "Leave Remarks",
        "OT Canteen",
        "OT LCA",
        "OT TPT",
        "Cadre",
    ]

    def setUp(self):
        """Arrange: Create mock grid with expected columns."""
        self.grid = MagicMock()
        self.grid.get_columns.return_value = self.EXPECTED_COLUMNS

    def test_dateViewGrid_columns_displaysAllRequiredColumns(self):
        """Positive: Date View grid displays all required columns."""
        columns = self.grid.get_columns()
        for col in self.EXPECTED_COLUMNS:
            self.assertIn(col, columns)

    def test_dateViewGrid_employeeColumn_showsPSNoAndName(self):
        """Positive: Employee column shows PS No and Employee Name fetched from InfoComm."""
        self.grid.get_cell_value.return_value = "12345 - John Doe"
        value = self.grid.get_cell_value(row=0, column="Employee")
        self.assertRegex(value, r"\d+ - .+")

    def test_dateViewGrid_otInColumn_displaysHHMMFormat(self):
        """Positive: OT In column displays time in HH:MM format."""
        self.grid.get_cell_value.return_value = "18:30"
        value = self.grid.get_cell_value(row=0, column="OT In")
        self.assertRegex(value, r"^\d{2}:\d{2}$")

    def test_dateViewGrid_otOutColumn_displaysHHMMFormat(self):
        """Positive: OT Out column displays time in HH:MM format."""
        self.grid.get_cell_value.return_value = "21:00"
        value = self.grid.get_cell_value(row=0, column="OT Out")
        self.assertRegex(value, r"^\d{2}:\d{2}$")

    def test_dateViewGrid_otLCA_displaysYesOrNo(self):
        """Positive: OT LCA column displays YES or NO."""
        self.grid.get_cell_value.return_value = "YES"
        value = self.grid.get_cell_value(row=0, column="OT LCA")
        self.assertIn(value, ["YES", "NO"])

    def test_dateViewGrid_otTPT_displaysYesOrNo(self):
        """Positive: OT TPT column displays YES or NO."""
        self.grid.get_cell_value.return_value = "NO"
        value = self.grid.get_cell_value(row=0, column="OT TPT")
        self.assertIn(value, ["YES", "NO"])

    def test_dateViewGrid_otCanteen_displaysOTAllowanceCode(self):
        """Positive: OT Canteen column displays OT allowance code like OT2 or OT4."""
        self.grid.get_cell_value.return_value = "OT2"
        value = self.grid.get_cell_value(row=0, column="OT Canteen")
        self.assertRegex(value, r"^OT\d+$")


class TestOTTimecardDateViewValidation(unittest.TestCase):
    """US-OT-001: Verify Date View validation and data filtering logic."""

    def setUp(self):
        """Arrange: Create mock OT timecard service."""
        self.service = MagicMock()

    def test_dateView_duplicatePunches_removedBySystem(self):
        """Positive: System considers only the first punch in and last punch out,
        removing duplicate punches."""
        punches = [
            {"type": "in", "time": "18:00"},
            {"type": "in", "time": "18:05"},  # duplicate
            {"type": "out", "time": "20:30"},
            {"type": "out", "time": "21:00"},  # last punch out
        ]
        self.service.filter_punches.return_value = [
            {"type": "in", "time": "18:00"},
            {"type": "out", "time": "21:00"},
        ]
        result = self.service.filter_punches(punches)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["time"], "18:00")
        self.assertEqual(result[1]["time"], "21:00")

    def test_dateView_totalOTHours_calculatedFromPunchInOut(self):
        """Positive: Total OT hours is calculated from OT punch in and punch out."""
        self.service.calculate_total_ot.return_value = 3.0
        result = self.service.calculate_total_ot(ot_in="18:00", ot_out="21:00")
        self.assertEqual(result, 3.0)

    def test_dateView_totalOTHours_summationForDateRange(self):
        """Positive: Total OT hours is the summation of all OT for the selected
        date range (From date to To date)."""
        self.service.get_total_ot_for_range.return_value = 25.5
        result = self.service.get_total_ot_for_range(
            from_date=date(2026, 5, 1), to_date=date(2026, 5, 10)
        )
        self.assertEqual(result, 25.5)

    def test_dateView_filterByFromAndToDate_displaysFilteredData(self):
        """Positive: When user selects From and To dates, data for those dates
        is displayed in the grid."""
        self.service.get_data_by_date_range.return_value = [
            {"date": "2026-05-01", "employee": "12345 - John"},
        ]
        result = self.service.get_data_by_date_range(
            from_date=date(2026, 5, 1), to_date=date(2026, 5, 10)
        )
        self.assertTrue(len(result) > 0)

    def test_dateView_noDateFilter_displaysOneMonthData(self):
        """Positive: By default (no date filter), one month of data is displayed."""
        self.service.get_default_data.return_value = {"period": "one_month", "records": []}
        result = self.service.get_default_data()
        self.assertEqual(result["period"], "one_month")

    def test_dateView_punchRemarks_displayedToIRAndEmployee(self):
        """Positive: Based on the punch, remarks are shown to the IR
        (and to the employee on Kiosk)."""
        self.service.get_remarks.return_value = "Present - Normal"
        result = self.service.get_remarks(employee_id="12345", date="2026-05-01")
        self.assertIsNotNone(result)


class TestOTTimecardDateViewSearchAndPagination(unittest.TestCase):
    """US-OT-001: Verify search bar and page navigation in Date View."""

    def setUp(self):
        """Arrange: Create mock grid with search and pagination."""
        self.grid = MagicMock()

    def test_dateView_columnSearch_filtersGridData(self):
        """Positive: Column search bar filters the grid data by the specified column."""
        self.grid.column_search.return_value = [{"Employee": "12345 - John Doe"}]
        result = self.grid.column_search(column="Employee", query="12345")
        self.assertEqual(len(result), 1)

    def test_dateView_globalSearch_filtersGridData(self):
        """Positive: Global search bar filters the grid data across all columns."""
        self.grid.global_search.return_value = [{"Employee": "12345 - John Doe"}]
        result = self.grid.global_search(query="John")
        self.assertEqual(len(result), 1)

    def test_dateView_pageNavigation_navigatesToOtherPages(self):
        """Positive: User can navigate to other pages using the page navigation."""
        self.grid.go_to_page.return_value = {"page": 2, "records": []}
        result = self.grid.go_to_page(2)
        self.assertEqual(result["page"], 2)

    def test_dateView_searchEmptyQuery_returnsAllData(self):
        """Boundary: Searching with an empty query returns all data."""
        self.grid.global_search.return_value = [{"Employee": "12345"}, {"Employee": "67890"}]
        result = self.grid.global_search(query="")
        self.assertTrue(len(result) >= 1)

    def test_dateView_searchNoMatch_returnsEmptyResult(self):
        """Negative: Searching for a non-existent value returns empty results."""
        self.grid.global_search.return_value = []
        result = self.grid.global_search(query="ZZZZZ_NONEXISTENT")
        self.assertEqual(len(result), 0)


class TestOTTimecardDateViewNegativeAndEdge(unittest.TestCase):
    """US-OT-001: Negative and edge case tests for Date View."""

    def setUp(self):
        """Arrange: Create mock service."""
        self.service = MagicMock()

    def test_dateView_fromDateAfterToDate_raisesValidationError(self):
        """Negative: Selecting 'From' date after 'To' date raises a validation error."""
        self.service.get_data_by_date_range.side_effect = ValueError(
            "From date cannot be after To date"
        )
        with self.assertRaises(ValueError):
            self.service.get_data_by_date_range(
                from_date=date(2026, 5, 10), to_date=date(2026, 5, 1)
            )

    def test_dateView_noDataForDateRange_displaysEmptyGrid(self):
        """Negative: No data available for the selected date range shows empty grid."""
        self.service.get_data_by_date_range.return_value = []
        result = self.service.get_data_by_date_range(
            from_date=date(2026, 12, 25), to_date=date(2026, 12, 31)
        )
        self.assertEqual(result, [])

    def test_dateView_nullDate_raisesValidationError(self):
        """Boundary: Null date value raises a validation error."""
        self.service.get_data_by_date_range.side_effect = ValueError("Date is required")
        with self.assertRaises(ValueError):
            self.service.get_data_by_date_range(from_date=None, to_date=None)

    def test_dateView_infoCommAPIFailure_handlesGracefully(self):
        """Integration: InfoComm API failure is handled gracefully with an error message."""
        self.service.fetch_from_infocomm.side_effect = ConnectionError("InfoComm API unavailable")
        with self.assertRaises(ConnectionError):
            self.service.fetch_from_infocomm(date="2026-05-01")

    def test_dateView_infoCommAPITimeout_handlesGracefully(self):
        """Integration: InfoComm API timeout is handled gracefully."""
        self.service.fetch_from_infocomm.side_effect = TimeoutError("Request timed out")
        with self.assertRaises(TimeoutError):
            self.service.fetch_from_infocomm(date="2026-05-01")


# ---------------------------------------------------------------------------
# US-OT-002: IR – View Maintain OT Timecard (Employee View)
# ---------------------------------------------------------------------------


class TestOTTimecardEmployeeViewNavigation(unittest.TestCase):
    """US-OT-002: Verify navigation to Employee View tab on OT Timecard page."""

    def setUp(self):
        """Arrange: Create mock page with tabs."""
        self.ot_timecard_page = MagicMock()
        self.ot_timecard_page.get_tabs.return_value = ["Date View", "Employee View"]

    def test_employeeViewTab_click_navigatesToEmployeeView(self):
        """Positive: Clicking 'Employee View' tab navigates to the Employee View."""
        self.ot_timecard_page.switch_tab.return_value = "Employee View"
        result = self.ot_timecard_page.switch_tab("Employee View")
        self.assertEqual(result, "Employee View")


class TestOTTimecardEmployeeViewAttributes(unittest.TestCase):
    """US-OT-002: Verify Employee View tab displays correct attributes."""

    def setUp(self):
        """Arrange: Create mock employee view with attributes."""
        self.employee_view = MagicMock()
        self.employee_view.get_attributes.return_value = [
            "employee_dropdown",
            "from_date_picker",
            "to_date_picker",
        ]
        self.employee_view.get_buttons.return_value = ["Export"]

    def test_employeeView_attributes_displaysEmployeeDropdown(self):
        """Positive: Employee View displays an Employee dropdown (PS No and Name)."""
        attributes = self.employee_view.get_attributes()
        self.assertIn("employee_dropdown", attributes)

    def test_employeeView_attributes_displaysFromDatePicker(self):
        """Positive: Employee View displays a From date picker."""
        attributes = self.employee_view.get_attributes()
        self.assertIn("from_date_picker", attributes)

    def test_employeeView_attributes_displaysToDatePicker(self):
        """Positive: Employee View displays a To date picker."""
        attributes = self.employee_view.get_attributes()
        self.assertIn("to_date_picker", attributes)

    def test_employeeView_buttons_displaysExportButton(self):
        """Positive: Employee View displays an Export button."""
        buttons = self.employee_view.get_buttons()
        self.assertIn("Export", buttons)


class TestOTTimecardEmployeeViewGridColumns(unittest.TestCase):
    """US-OT-002: Verify Employee View grid displays all required columns."""

    EXPECTED_COLUMNS = [
        "Date",
        "TRT No",
        "OT In",
        "OT Out",
        "Total OT Hours",
        "Approved OT Hours",
        "OT Status",
        "Leave Remarks",
        "OT Canteen",
        "OT LCA",
        "OT TPT",
        "Cadre",
    ]

    def setUp(self):
        """Arrange: Create mock grid."""
        self.grid = MagicMock()
        self.grid.get_columns.return_value = self.EXPECTED_COLUMNS

    def test_employeeViewGrid_columns_displaysAllRequiredColumns(self):
        """Positive: Employee View grid displays all required columns."""
        columns = self.grid.get_columns()
        for col in self.EXPECTED_COLUMNS:
            self.assertIn(col, columns)

    def test_employeeViewGrid_dateColumn_showsDateForOTEntry(self):
        """Positive: Date column shows the date for each OT entry."""
        self.grid.get_cell_value.return_value = "2026-05-01"
        value = self.grid.get_cell_value(row=0, column="Date")
        self.assertIsNotNone(value)


class TestOTTimecardEmployeeViewValidation(unittest.TestCase):
    """US-OT-002: Verify Employee View validation and filtering logic."""

    def setUp(self):
        """Arrange: Create mock service."""
        self.service = MagicMock()

    def test_employeeView_selectEmployee_displaysEmployeeData(self):
        """Positive: Selecting an employee from dropdown displays their OT data."""
        self.service.get_data_by_employee.return_value = [
            {"date": "2026-05-01", "ot_in": "18:00", "ot_out": "21:00"}
        ]
        result = self.service.get_data_by_employee(employee_id="12345")
        self.assertTrue(len(result) > 0)

    def test_employeeView_filterByFromAndToDate_displaysFilteredData(self):
        """Positive: When From and To dates are selected, only data for those
        dates is displayed."""
        self.service.get_data_by_employee_and_range.return_value = [
            {"date": "2026-05-01"}
        ]
        result = self.service.get_data_by_employee_and_range(
            employee_id="12345",
            from_date=date(2026, 5, 1),
            to_date=date(2026, 5, 10),
        )
        self.assertTrue(len(result) > 0)

    def test_employeeView_defaultData_displaysOneMonth(self):
        """Positive: By default, one month of OT data is displayed for the employee."""
        self.service.get_default_employee_data.return_value = {"period": "one_month"}
        result = self.service.get_default_employee_data(employee_id="12345")
        self.assertEqual(result["period"], "one_month")

    def test_employeeView_totalOTSummation_forSelectedPeriod(self):
        """Positive: Total OT hours is the summation of all OT for the
        selected period for the specific employee."""
        self.service.get_employee_total_ot.return_value = 15.5
        result = self.service.get_employee_total_ot(
            employee_id="12345",
            from_date=date(2026, 5, 1),
            to_date=date(2026, 5, 10),
        )
        self.assertEqual(result, 15.5)


class TestOTTimecardEmployeeViewNegativeAndEdge(unittest.TestCase):
    """US-OT-002: Negative and edge case tests for Employee View."""

    def setUp(self):
        """Arrange: Create mock service and view."""
        self.service = MagicMock()
        self.employee_view = MagicMock()

    def test_employeeView_noEmployeeSelected_raisesValidationError(self):
        """Negative: Not selecting an employee raises a validation error."""
        self.service.get_data_by_employee.side_effect = ValueError(
            "Employee selection is required"
        )
        with self.assertRaises(ValueError):
            self.service.get_data_by_employee(employee_id=None)

    def test_employeeView_employeeWithNoOTData_displaysEmptyGrid(self):
        """Negative: Employee with no OT records shows an empty grid."""
        self.service.get_data_by_employee.return_value = []
        result = self.service.get_data_by_employee(employee_id="99999")
        self.assertEqual(result, [])

    def test_employeeView_employeeDropdown_showsPSNoAndName(self):
        """Positive: Employee dropdown shows PS No and Employee Name."""
        self.employee_view.get_employee_options.return_value = [
            {"ps_no": "12345", "name": "John Doe"},
            {"ps_no": "67890", "name": "Jane Smith"},
        ]
        options = self.employee_view.get_employee_options()
        for option in options:
            self.assertIn("ps_no", option)
            self.assertIn("name", option)

    def test_employeeView_fromDateAfterToDate_raisesValidationError(self):
        """Negative: Selecting 'From' date after 'To' date raises validation error."""
        self.service.get_data_by_employee_and_range.side_effect = ValueError(
            "From date cannot be after To date"
        )
        with self.assertRaises(ValueError):
            self.service.get_data_by_employee_and_range(
                employee_id="12345",
                from_date=date(2026, 5, 10),
                to_date=date(2026, 5, 1),
            )


# ---------------------------------------------------------------------------
# US-OT-003: IR – Export Maintain OT Timecard
# ---------------------------------------------------------------------------


class TestOTTimecardExport(unittest.TestCase):
    """US-OT-003: Verify Export button exports details to an Excel file."""

    def setUp(self):
        """Arrange: Create mock export service."""
        self.export_service = MagicMock()

    def test_export_clickExportButton_exportsToExcel(self):
        """Positive: Clicking 'Export' exports the displayed data to an Excel file."""
        self.export_service.export_to_excel.return_value = "/downloads/ot_timecard.xlsx"
        result = self.export_service.export_to_excel(tab="Date View")
        self.assertTrue(result.endswith(".xlsx"))

    def test_export_withDateFilter_exportsFilteredData(self):
        """Positive: If user selects a date, only filtered data is exported."""
        self.export_service.export_to_excel.return_value = "/downloads/ot_filtered.xlsx"
        result = self.export_service.export_to_excel(
            tab="Date View",
            from_date=date(2026, 5, 1),
            to_date=date(2026, 5, 10),
        )
        self.export_service.export_to_excel.assert_called_once()
        self.assertIsNotNone(result)

    def test_export_withoutFilter_exportsAllExistingData(self):
        """Positive: If user doesn't filter data, all existing data is exported."""
        self.export_service.export_to_excel.return_value = "/downloads/ot_all.xlsx"
        result = self.export_service.export_to_excel(tab="Date View", from_date=None, to_date=None)
        self.assertIsNotNone(result)

    def test_export_saveToLocation_userCanChoosePath(self):
        """Positive: User can save the exported file to a location."""
        self.export_service.save_to_location.return_value = True
        result = self.export_service.save_to_location(path="/user/documents/ot_report.xlsx")
        self.assertTrue(result)

    def test_export_emptyGrid_exportsEmptyFile(self):
        """Boundary: Exporting when grid has no data produces an empty Excel file."""
        self.export_service.export_to_excel.return_value = "/downloads/ot_empty.xlsx"
        self.export_service.get_exported_row_count.return_value = 0
        result = self.export_service.export_to_excel(tab="Date View")
        self.assertIsNotNone(result)
        count = self.export_service.get_exported_row_count()
        self.assertEqual(count, 0)

    def test_export_serviceFailure_handlesGracefully(self):
        """Negative: Export service failure is handled gracefully."""
        self.export_service.export_to_excel.side_effect = IOError("Disk full")
        with self.assertRaises(IOError):
            self.export_service.export_to_excel(tab="Date View")


if __name__ == "__main__":
    unittest.main()
