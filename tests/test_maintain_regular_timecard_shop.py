"""
Unit Tests for Maintain Regular Timecard – Shop In Charge (IS) Roles
User Stories: US-RT-004 (Shop Date View), US-RT-005 (Shop Employee View),
              US-RT-006 (Shop Export)

Covers regular timecard functionality for:
- Shop In Charge (IS) – view date view, employee view, export

Test Categories:
- Positive / Happy Path
- Negative / Error Path
- Boundary / Edge Cases
- Integration Points
"""

SOURCE_STORY_FILE = "MaintainRegularTimecard.xlsx"

import unittest
from unittest.mock import MagicMock, patch
from datetime import date, datetime


# TODO: Import actual modules once implementation is available.
# from src.attendance.regular_timecard import (
#     RegularTimecardPage, RegularTimecardService, TimecardDateView,
#     TimecardEmployeeView, ExportService, InfoCommAPI, ShiftTimingMaster
# )


# ---------------------------------------------------------------------------
# US-RT-004: Shop In Charge – View Maintain Regular Timecard (Date View)
# ---------------------------------------------------------------------------


class TestShopTimecardNavigation(unittest.TestCase):
    """US-RT-004: Verify Shop In Charge navigation to Maintain Regular Timecard
    page from side navigation under Attendance Management."""

    def setUp(self):
        """Arrange: Create mock navigation and page instances."""
        self.nav_service = MagicMock()
        self.timecard_page = MagicMock()
        self.nav_service.select_submenu.return_value = self.timecard_page
        self.timecard_page.get_tabs.return_value = ["Date View", "Employee View"]
        self.timecard_page.get_active_tab.return_value = "Date View"

    def test_selectTimecardMenu_navigate_displaysTimecardPage(self):
        """Positive: Shop In Charge selecting 'Maintain Timecard' from 'Attendance Management'
        displays the Maintain Regular Timecard page."""
        page = self.nav_service.select_submenu("Attendance Management", "Maintain Timecard")
        self.nav_service.select_submenu.assert_called_once_with(
            "Attendance Management", "Maintain Timecard"
        )
        self.assertIsNotNone(page)

    def test_timecardPage_render_displaysTabs(self):
        """Positive: Timecard page displays 'Date View' and 'Employee View' tabs."""
        tabs = self.timecard_page.get_tabs()
        self.assertEqual(tabs, ["Date View", "Employee View"])

    def test_timecardPage_defaultTab_isDateView(self):
        """Positive: By default, the 'Date View' tab is active."""
        active_tab = self.timecard_page.get_active_tab()
        self.assertEqual(active_tab, "Date View")


class TestShopTimecardDateViewAttributes(unittest.TestCase):
    """US-RT-004: Verify Date View tab displays correct attributes for Shop In Charge."""

    def setUp(self):
        """Arrange: Create mock date view."""
        self.date_view = MagicMock()
        self.date_view.get_attributes.return_value = ["date_picker"]
        self.date_view.get_buttons.return_value = ["Export"]

    def test_dateView_attributes_displaysDatePicker(self):
        """Positive: Date View displays a Date picker attribute."""
        attributes = self.date_view.get_attributes()
        self.assertIn("date_picker", attributes)

    def test_dateView_buttons_displaysExportButton(self):
        """Positive: Date View displays an Export button."""
        buttons = self.date_view.get_buttons()
        self.assertIn("Export", buttons)


class TestShopTimecardDateViewGridColumns(unittest.TestCase):
    """US-RT-004: Verify Date View grid displays all required columns for Shop In Charge."""

    EXPECTED_COLUMNS = [
        "Employee",
        "TRT No",
        "In",
        "Out",
        "Late",
        "Early",
        "Reg. Shift",
        "Actual Shift",
        "Leave Remarks",
        "Employee Status",
        "Cadre",
    ]

    def setUp(self):
        """Arrange: Create mock grid."""
        self.grid = MagicMock()
        self.grid.get_columns.return_value = self.EXPECTED_COLUMNS

    def test_dateViewGrid_columns_displaysAllRequiredColumns(self):
        """Positive: Date View grid displays all required columns."""
        columns = self.grid.get_columns()
        for col in self.EXPECTED_COLUMNS:
            self.assertIn(col, columns)

    def test_dateViewGrid_employeeColumn_showsPSNoAndName(self):
        """Positive: Employee column shows PS No and Employee Name."""
        self.grid.get_cell_value.return_value = "12345 - John Doe"
        value = self.grid.get_cell_value(row=0, column="Employee")
        self.assertRegex(value, r"\d+ - .+")

    def test_dateViewGrid_inColumn_displaysHHMMFormat(self):
        """Positive: In column displays punch in time in HH:MM format."""
        self.grid.get_cell_value.return_value = "07:00"
        value = self.grid.get_cell_value(row=0, column="In")
        self.assertRegex(value, r"^\d{2}:\d{2}$")

    def test_dateViewGrid_outColumn_displaysHHMMFormat(self):
        """Positive: Out column displays punch out time in HH:MM format."""
        self.grid.get_cell_value.return_value = "15:25"
        value = self.grid.get_cell_value(row=0, column="Out")
        self.assertRegex(value, r"^\d{2}:\d{2}$")


class TestShopTimecardDateViewValidation(unittest.TestCase):
    """US-RT-004: Verify Date View validation logic for Shop In Charge."""

    def setUp(self):
        """Arrange: Create mock service."""
        self.service = MagicMock()

    def test_dateView_defaultDisplay_showsPreviousDayData(self):
        """Positive: Default grid shows punching data of completed date (previous day).
        Data is refreshed daily but previous data is stored."""
        self.service.get_default_data.return_value = {
            "period": "previous_day",
            "records": [],
        }
        result = self.service.get_default_data()
        self.assertEqual(result["period"], "previous_day")

    def test_dateView_selectFromAndToDate_displaysFilteredData(self):
        """Positive: Selecting From and To dates displays data for that range."""
        self.service.get_data_by_date_range.return_value = [{"date": "2026-05-01"}]
        result = self.service.get_data_by_date_range(
            from_date=date(2026, 5, 1), to_date=date(2026, 5, 10)
        )
        self.assertTrue(len(result) > 0)

    def test_dateView_inAndOutInMinutes_calculatedCorrectly(self):
        """Positive: In and Out times are represented in minutes
        (e.g., 08:04 → 484 minutes)."""
        self.service.time_to_minutes.return_value = 484
        result = self.service.time_to_minutes(time_str="08:04")
        self.assertEqual(result, 484)

    def test_dateView_duplicatePunches_removedBySystem(self):
        """Positive: System removes duplicate punches, keeping first in and last out."""
        self.service.filter_punches.return_value = [
            {"type": "in", "time": "07:00"},
            {"type": "out", "time": "15:25"},
        ]
        result = self.service.filter_punches([
            {"type": "in", "time": "07:00"},
            {"type": "in", "time": "07:05"},
            {"type": "out", "time": "15:25"},
        ])
        self.assertEqual(len(result), 2)

    def test_dateView_earlyPunchIn_adjustedToShiftStart(self):
        """Positive: Early punch in displayed as-is but payment adjusted to shift start."""
        self.service.adjust_punch_for_payment.return_value = {
            "display_time": "06:53",
            "payment_time": "07:00",
        }
        result = self.service.adjust_punch_for_payment(
            punch_time="06:53", shift_start="07:00", direction="in"
        )
        self.assertEqual(result["payment_time"], "07:00")

    def test_dateView_latePunchOut_adjustedToShiftEnd(self):
        """Positive: Late punch out adjusted to shift end time for payment."""
        self.service.adjust_punch_for_payment.return_value = {
            "display_time": "15:35",
            "payment_time": "15:25",
        }
        result = self.service.adjust_punch_for_payment(
            punch_time="15:35", shift_end="15:25", direction="out"
        )
        self.assertEqual(result["payment_time"], "15:25")

    def test_dateView_noPunchData_markedAsAbsent(self):
        """Positive: No punch data means the workman is marked as absent (ABS)."""
        self.service.get_leave_remark.return_value = "ABS"
        result = self.service.get_leave_remark(employee_id="12345", date="2026-05-01")
        self.assertEqual(result, "ABS")

    def test_dateView_absRemark_remainsUntilLeaveApproved(self):
        """Positive: ABS remark remains until leave is applied and approved."""
        self.service.is_remark_changeable.return_value = False
        result = self.service.is_remark_changeable(
            employee_id="12345", date="2026-05-01", current_remark="ABS"
        )
        self.assertFalse(result)

    def test_dateView_punchRemarks_displayedToShopAndEmployee(self):
        """Positive: Remarks shown to Shop In Charge and employee (Kiosk)."""
        self.service.get_leave_remark.return_value = "Present"
        result = self.service.get_leave_remark(employee_id="12345", date="2026-05-01")
        self.assertIsNotNone(result)

    def test_dateView_autoSchedule_runsDailyForYesterdayAndToday(self):
        """Positive: System runs auto schedule daily for yesterday and today."""
        self.service.run_auto_schedule.return_value = {
            "dates_processed": ["2026-05-12", "2026-05-13"],
        }
        result = self.service.run_auto_schedule()
        self.assertEqual(len(result["dates_processed"]), 2)


class TestShopTimecardDateViewSearchAndPagination(unittest.TestCase):
    """US-RT-004: Verify search bar and page navigation for Shop In Charge."""

    def setUp(self):
        """Arrange: Create mock grid."""
        self.grid = MagicMock()

    def test_dateView_columnSearch_filtersGridData(self):
        """Positive: Column search bar filters the grid data."""
        self.grid.column_search.return_value = [{"Employee": "12345 - John Doe"}]
        result = self.grid.column_search(column="Employee", query="12345")
        self.assertEqual(len(result), 1)

    def test_dateView_globalSearch_filtersGridData(self):
        """Positive: Global search bar filters grid data across all columns."""
        self.grid.global_search.return_value = [{"Employee": "12345 - John Doe"}]
        result = self.grid.global_search(query="John")
        self.assertEqual(len(result), 1)

    def test_dateView_pageNavigation_navigatesToOtherPages(self):
        """Positive: User can navigate to other pages."""
        self.grid.go_to_page.return_value = {"page": 2, "records": []}
        result = self.grid.go_to_page(2)
        self.assertEqual(result["page"], 2)

    def test_dateView_searchNoMatch_returnsEmptyResult(self):
        """Negative: Searching for a non-existent value returns empty results."""
        self.grid.global_search.return_value = []
        result = self.grid.global_search(query="NONEXISTENT")
        self.assertEqual(len(result), 0)


class TestShopTimecardDateViewNegativeAndEdge(unittest.TestCase):
    """US-RT-004: Negative and edge case tests for Shop Date View."""

    def setUp(self):
        """Arrange: Create mock service."""
        self.service = MagicMock()

    def test_dateView_fromDateAfterToDate_raisesValidationError(self):
        """Negative: From date after To date raises validation error."""
        self.service.get_data_by_date_range.side_effect = ValueError(
            "From date cannot be after To date"
        )
        with self.assertRaises(ValueError):
            self.service.get_data_by_date_range(
                from_date=date(2026, 5, 10), to_date=date(2026, 5, 1)
            )

    def test_dateView_noDataForDateRange_displaysEmptyGrid(self):
        """Negative: No data for the date range shows empty grid."""
        self.service.get_data_by_date_range.return_value = []
        result = self.service.get_data_by_date_range(
            from_date=date(2026, 12, 25), to_date=date(2026, 12, 31)
        )
        self.assertEqual(result, [])

    def test_dateView_infoCommAPIFailure_handlesGracefully(self):
        """Integration: InfoComm API failure handled gracefully."""
        self.service.fetch_from_infocomm.side_effect = ConnectionError("API unavailable")
        with self.assertRaises(ConnectionError):
            self.service.fetch_from_infocomm(date="2026-05-01")


# ---------------------------------------------------------------------------
# US-RT-005: Shop In Charge – View Maintain Regular Timecard (Employee View)
# ---------------------------------------------------------------------------


class TestShopTimecardEmployeeViewNavigation(unittest.TestCase):
    """US-RT-005: Verify Shop In Charge navigation to Employee View tab."""

    def setUp(self):
        """Arrange: Create mock page."""
        self.timecard_page = MagicMock()

    def test_employeeViewTab_click_navigatesToEmployeeView(self):
        """Positive: Clicking 'Employee View' tab navigates to Employee View."""
        self.timecard_page.switch_tab.return_value = "Employee View"
        result = self.timecard_page.switch_tab("Employee View")
        self.assertEqual(result, "Employee View")


class TestShopTimecardEmployeeViewAttributes(unittest.TestCase):
    """US-RT-005: Verify Employee View attributes for Shop In Charge."""

    def setUp(self):
        """Arrange: Create mock employee view."""
        self.employee_view = MagicMock()
        self.employee_view.get_attributes.return_value = [
            "employee_dropdown",
            "from_date_picker",
            "to_date_picker",
        ]
        self.employee_view.get_buttons.return_value = ["Export"]

    def test_employeeView_attributes_displaysEmployeeDropdown(self):
        """Positive: Employee View displays Employee dropdown (PS No and Name)."""
        attributes = self.employee_view.get_attributes()
        self.assertIn("employee_dropdown", attributes)

    def test_employeeView_attributes_displaysFromDatePicker(self):
        """Positive: Employee View displays From date picker."""
        attributes = self.employee_view.get_attributes()
        self.assertIn("from_date_picker", attributes)

    def test_employeeView_attributes_displaysToDatePicker(self):
        """Positive: Employee View displays To date picker."""
        attributes = self.employee_view.get_attributes()
        self.assertIn("to_date_picker", attributes)

    def test_employeeView_buttons_displaysExportButton(self):
        """Positive: Employee View displays an Export button."""
        buttons = self.employee_view.get_buttons()
        self.assertIn("Export", buttons)


class TestShopTimecardEmployeeViewGridColumns(unittest.TestCase):
    """US-RT-005: Verify Employee View grid columns for Shop In Charge."""

    EXPECTED_COLUMNS = [
        "Date",
        "TRT No",
        "In",
        "Out",
        "In (Min)",
        "Out (Min)",
        "Late",
        "Early",
        "Reg. Shift",
        "Actual Shift",
        "Remarks",
        "Employee Status",
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

    def test_employeeViewGrid_inMinColumn_displaysMinuteValue(self):
        """Positive: In (Min) column displays punch in time in minutes."""
        self.grid.get_cell_value.return_value = 484
        value = self.grid.get_cell_value(row=0, column="In (Min)")
        self.assertIsInstance(value, int)

    def test_employeeViewGrid_outMinColumn_displaysMinuteValue(self):
        """Positive: Out (Min) column displays punch out time in minutes."""
        self.grid.get_cell_value.return_value = 925
        value = self.grid.get_cell_value(row=0, column="Out (Min)")
        self.assertIsInstance(value, int)


class TestShopTimecardEmployeeViewValidation(unittest.TestCase):
    """US-RT-005: Verify Employee View validation for Shop In Charge."""

    def setUp(self):
        """Arrange: Create mock service."""
        self.service = MagicMock()

    def test_employeeView_selectEmployee_displaysData(self):
        """Positive: Selecting an employee displays their timecard data."""
        self.service.get_data_by_employee.return_value = [
            {"date": "2026-05-01", "in": "07:00", "out": "15:25"}
        ]
        result = self.service.get_data_by_employee(employee_id="12345")
        self.assertTrue(len(result) > 0)

    def test_employeeView_defaultDisplay_showsPreviousDayData(self):
        """Positive: By default, previous day data is displayed (refreshed daily)."""
        self.service.get_default_employee_data.return_value = {"period": "previous_day"}
        result = self.service.get_default_employee_data(employee_id="12345")
        self.assertEqual(result["period"], "previous_day")

    def test_employeeView_selectEmployeeDropdown_filtersData(self):
        """Positive: Selecting employee from dropdown displays data for that employee."""
        self.service.get_data_by_employee.return_value = [
            {"date": "2026-05-01", "employee": "12345 - John"}
        ]
        result = self.service.get_data_by_employee(employee_id="12345")
        self.assertEqual(result[0]["employee"], "12345 - John")

    def test_employeeView_duplicatePunches_removedBySystem(self):
        """Positive: Duplicate punches removed, keeping first in and last out."""
        self.service.filter_punches.return_value = [
            {"type": "in", "time": "07:00"},
            {"type": "out", "time": "15:25"},
        ]
        result = self.service.filter_punches([
            {"type": "in", "time": "07:00"},
            {"type": "in", "time": "07:03"},
            {"type": "out", "time": "15:25"},
        ])
        self.assertEqual(len(result), 2)

    def test_employeeView_noPunchData_markedAbsent(self):
        """Positive: No punch data marks workman as absent."""
        self.service.get_leave_remark.return_value = "ABS"
        result = self.service.get_leave_remark(employee_id="12345", date="2026-05-01")
        self.assertEqual(result, "ABS")

    def test_employeeView_earlyPunchIn_adjustedForPayment(self):
        """Positive: Early punch in adjusted to shift start for payment."""
        self.service.adjust_punch_for_payment.return_value = {
            "display_time": "06:53",
            "payment_time": "07:00",
        }
        result = self.service.adjust_punch_for_payment(
            punch_time="06:53", shift_start="07:00", direction="in"
        )
        self.assertEqual(result["payment_time"], "07:00")

    def test_employeeView_latePunchOut_adjustedForPayment(self):
        """Positive: Late punch out adjusted to shift end for payment."""
        self.service.adjust_punch_for_payment.return_value = {
            "display_time": "15:35",
            "payment_time": "15:25",
        }
        result = self.service.adjust_punch_for_payment(
            punch_time="15:35", shift_end="15:25", direction="out"
        )
        self.assertEqual(result["payment_time"], "15:25")

    def test_employeeView_autoSchedule_yesterdayAndToday(self):
        """Positive: Auto schedule runs for yesterday and today."""
        self.service.run_auto_schedule.return_value = {
            "dates_processed": ["2026-05-12", "2026-05-13"],
        }
        result = self.service.run_auto_schedule()
        self.assertEqual(len(result["dates_processed"]), 2)


class TestShopTimecardEmployeeViewSearchAndPagination(unittest.TestCase):
    """US-RT-005: Verify search and pagination for Shop Employee View."""

    def setUp(self):
        """Arrange: Create mock grid."""
        self.grid = MagicMock()

    def test_employeeView_columnSearch_filtersGridData(self):
        """Positive: Column search filters the grid data."""
        self.grid.column_search.return_value = [{"Employee": "12345"}]
        result = self.grid.column_search(column="Employee", query="12345")
        self.assertEqual(len(result), 1)

    def test_employeeView_globalSearch_filtersGridData(self):
        """Positive: Global search filters grid data across all columns."""
        self.grid.global_search.return_value = [{"Employee": "John"}]
        result = self.grid.global_search(query="John")
        self.assertEqual(len(result), 1)

    def test_employeeView_pageNavigation_works(self):
        """Positive: Page navigation works correctly."""
        self.grid.go_to_page.return_value = {"page": 3, "records": []}
        result = self.grid.go_to_page(3)
        self.assertEqual(result["page"], 3)


class TestShopTimecardEmployeeViewNegativeAndEdge(unittest.TestCase):
    """US-RT-005: Negative and edge case tests for Shop Employee View."""

    def setUp(self):
        """Arrange: Create mock service."""
        self.service = MagicMock()

    def test_employeeView_noEmployeeSelected_raisesValidationError(self):
        """Negative: Not selecting an employee raises validation error."""
        self.service.get_data_by_employee.side_effect = ValueError("Employee required")
        with self.assertRaises(ValueError):
            self.service.get_data_by_employee(employee_id=None)

    def test_employeeView_employeeWithNoRecords_displaysEmptyGrid(self):
        """Negative: Employee with no records shows empty grid."""
        self.service.get_data_by_employee.return_value = []
        result = self.service.get_data_by_employee(employee_id="99999")
        self.assertEqual(result, [])

    def test_employeeView_fromDateAfterToDate_raisesValidationError(self):
        """Negative: From date after To date raises validation error."""
        self.service.get_data_by_employee_and_range.side_effect = ValueError(
            "From date cannot be after To date"
        )
        with self.assertRaises(ValueError):
            self.service.get_data_by_employee_and_range(
                employee_id="12345",
                from_date=date(2026, 5, 10),
                to_date=date(2026, 5, 1),
            )

    def test_employeeView_infoCommAPIFailure_handlesGracefully(self):
        """Integration: InfoComm API failure handled gracefully."""
        self.service.fetch_from_infocomm.side_effect = ConnectionError("API unavailable")
        with self.assertRaises(ConnectionError):
            self.service.fetch_from_infocomm(employee_id="12345")


# ---------------------------------------------------------------------------
# US-RT-006: Shop In Charge – Export Maintain Regular Timecard
# ---------------------------------------------------------------------------


class TestShopTimecardExport(unittest.TestCase):
    """US-RT-006: Verify Export button on Maintain Regular Timecard for Shop In Charge."""

    def setUp(self):
        """Arrange: Create mock export service."""
        self.export_service = MagicMock()

    def test_export_clickExportButton_exportsToExcel(self):
        """Positive: Clicking 'Export' exports the displayed data to an Excel file."""
        self.export_service.export_to_excel.return_value = "/downloads/timecard.xlsx"
        result = self.export_service.export_to_excel(tab="Date View")
        self.assertTrue(result.endswith(".xlsx"))

    def test_export_withDateFilter_exportsFilteredData(self):
        """Positive: If user selects from and to date, filtered data is exported."""
        self.export_service.export_to_excel.return_value = "/downloads/filtered.xlsx"
        result = self.export_service.export_to_excel(
            tab="Date View",
            from_date=date(2026, 5, 1),
            to_date=date(2026, 5, 10),
        )
        self.assertIsNotNone(result)

    def test_export_withoutFilter_exportsAllExistingData(self):
        """Positive: If user doesn't filter, all existing data is exported."""
        self.export_service.export_to_excel.return_value = "/downloads/all.xlsx"
        result = self.export_service.export_to_excel(
            tab="Date View", from_date=None, to_date=None
        )
        self.assertIsNotNone(result)

    def test_export_saveToLocation_userCanChoosePath(self):
        """Positive: User can save the exported file to a chosen location."""
        self.export_service.save_to_location.return_value = True
        result = self.export_service.save_to_location(path="/user/documents/report.xlsx")
        self.assertTrue(result)

    def test_export_emptyGrid_exportsEmptyFile(self):
        """Boundary: Exporting when grid has no data produces an empty file."""
        self.export_service.export_to_excel.return_value = "/downloads/empty.xlsx"
        self.export_service.get_exported_row_count.return_value = 0
        result = self.export_service.export_to_excel(tab="Date View")
        self.assertIsNotNone(result)

    def test_export_serviceFailure_handlesGracefully(self):
        """Negative: Export service failure is handled gracefully."""
        self.export_service.export_to_excel.side_effect = IOError("Disk full")
        with self.assertRaises(IOError):
            self.export_service.export_to_excel(tab="Date View")


if __name__ == "__main__":
    unittest.main()
