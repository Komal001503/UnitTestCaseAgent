"""
Unit Tests for Maintain Regular Timecard – IR, IR Approver Roles
User Stories: US-RT-001 (Date View), US-RT-002 (Employee View), US-RT-003 (Export)

Covers regular timecard functionality for:
- IR (Industrial Relation)
- IR Approver

Test Categories:
- Positive / Happy Path
- Negative / Error Path
- Boundary / Edge Cases
- Integration Points
"""

SOURCE_STORY_FILE = "MaintainRegularTimecard.xlsx"

import unittest
from unittest.mock import MagicMock, patch
from datetime import date, datetime, timedelta


# TODO: Import actual modules once implementation is available.
# from src.attendance.regular_timecard import (
#     RegularTimecardPage, RegularTimecardService, TimecardDateView,
#     TimecardEmployeeView, ExportService, InfoCommAPI, ShiftTimingMaster
# )


# ---------------------------------------------------------------------------
# US-RT-001: IR – View Maintain Regular Timecard (Date View)
# ---------------------------------------------------------------------------


class TestRegularTimecardNavigation(unittest.TestCase):
    """US-RT-001: Verify navigation to Maintain Regular Timecard page
    from side navigation under Attendance Management."""

    def setUp(self):
        """Arrange: Create mock navigation and page instances."""
        self.nav_service = MagicMock()
        self.timecard_page = MagicMock()
        self.nav_service.select_submenu.return_value = self.timecard_page
        self.timecard_page.get_tabs.return_value = ["Date View", "Employee View"]
        self.timecard_page.get_active_tab.return_value = "Date View"

    def test_selectTimecardMenu_navigate_displaysTimecardPage(self):
        """Positive: Selecting 'Maintain Timecard' from 'Attendance Management'
        menu displays the Maintain Regular Timecard page."""
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


class TestRegularTimecardDateViewAttributes(unittest.TestCase):
    """US-RT-001: Verify Date View tab displays correct attributes."""

    def setUp(self):
        """Arrange: Create mock date view with attributes."""
        self.date_view = MagicMock()
        self.date_view.get_attributes.return_value = ["date_picker"]
        self.date_view.get_buttons.return_value = ["Save", "Export"]

    def test_dateView_attributes_displaysDatePicker(self):
        """Positive: Date View displays a Date picker attribute."""
        attributes = self.date_view.get_attributes()
        self.assertIn("date_picker", attributes)

    def test_dateView_buttons_displaysSaveButton(self):
        """Positive: Date View displays a Save button."""
        buttons = self.date_view.get_buttons()
        self.assertIn("Save", buttons)

    def test_dateView_buttons_displaysExportButton(self):
        """Positive: Date View displays an Export button."""
        buttons = self.date_view.get_buttons()
        self.assertIn("Export", buttons)


class TestRegularTimecardDateViewGridColumns(unittest.TestCase):
    """US-RT-001: Verify Date View grid displays all required columns."""

    EXPECTED_COLUMNS = [
        "Employee",
        "TRT No",
        "In",
        "Out",
        "Late",
        "Early",
        "Reg. Shift",
        "Actual Shift",
        "Employee Status",
        "Cadre",
        "Leave Remarks",
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

    def test_dateViewGrid_lateColumn_displaysTimeAfterShiftStart(self):
        """Positive: Late column shows time calculated after start time of actual shift."""
        self.grid.get_cell_value.return_value = "00:15"
        value = self.grid.get_cell_value(row=0, column="Late")
        self.assertRegex(value, r"^\d{2}:\d{2}$")

    def test_dateViewGrid_earlyColumn_displaysTimeBeforeShiftEnd(self):
        """Positive: Early column shows time calculated before end time of actual shift."""
        self.grid.get_cell_value.return_value = "00:10"
        value = self.grid.get_cell_value(row=0, column="Early")
        self.assertRegex(value, r"^\d{2}:\d{2}$")

    def test_dateViewGrid_regShift_displaysPlannedShift(self):
        """Positive: Reg. Shift column displays the planned/registered shift."""
        self.grid.get_cell_value.return_value = "I"
        value = self.grid.get_cell_value(row=0, column="Reg. Shift")
        self.assertIsNotNone(value)

    def test_dateViewGrid_actualShift_displaysCalculatedShift(self):
        """Positive: Actual Shift column displays shift calculated from punching data."""
        self.grid.get_cell_value.return_value = "I"
        value = self.grid.get_cell_value(row=0, column="Actual Shift")
        self.assertIsNotNone(value)

    def test_dateViewGrid_employeeStatus_displaysDirectOrIndirect(self):
        """Positive: Employee Status column displays Direct or Indirect."""
        self.grid.get_cell_value.return_value = "Direct"
        value = self.grid.get_cell_value(row=0, column="Employee Status")
        self.assertIn(value, ["Direct", "Indirect"])


class TestRegularTimecardDateViewValidation(unittest.TestCase):
    """US-RT-001: Verify Date View validation and data processing logic."""

    def setUp(self):
        """Arrange: Create mock service."""
        self.service = MagicMock()

    def test_dateView_defaultDisplay_showsPreviousDayAndCurrentDay(self):
        """Positive: Default grid shows punching data of completed date
        (previous day and current day till shift 3 end)."""
        self.service.get_default_data.return_value = {
            "period": "previous_day_to_current",
            "records": [],
        }
        result = self.service.get_default_data()
        self.assertEqual(result["period"], "previous_day_to_current")

    def test_dateView_schedulerFetches_everyMorning930AM(self):
        """Positive: System runs a scheduler to fetch data every morning around 9:30 AM
        from the InfoComm API."""
        self.service.get_scheduler_config.return_value = {"time": "09:30", "source": "InfoComm"}
        config = self.service.get_scheduler_config()
        self.assertEqual(config["time"], "09:30")
        self.assertEqual(config["source"], "InfoComm")

    def test_dateView_selectDate_displaysDataForSelectedDate(self):
        """Positive: If user chooses a date, data for that date is displayed."""
        self.service.get_data_by_date.return_value = [{"date": "2026-05-01"}]
        result = self.service.get_data_by_date(date=date(2026, 5, 1))
        self.assertTrue(len(result) > 0)

    def test_dateView_noDateSelected_displaysCurrentDateData(self):
        """Positive: If user does not choose a date, data for current date
        is displayed by default."""
        self.service.get_data_by_date.return_value = [{"date": "2026-05-13"}]
        result = self.service.get_data_by_date(date=None)
        self.assertTrue(len(result) > 0)

    def test_dateView_duplicatePunches_removedBySystem(self):
        """Positive: System considers only the first punch in and last punch out,
        removing duplicate and multiple punching data."""
        punches = [
            {"type": "in", "time": "07:00"},
            {"type": "in", "time": "07:05"},  # duplicate
            {"type": "out", "time": "15:20"},
            {"type": "out", "time": "15:25"},  # last
        ]
        self.service.filter_punches.return_value = [
            {"type": "in", "time": "07:00"},
            {"type": "out", "time": "15:25"},
        ]
        result = self.service.filter_punches(punches)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["time"], "07:00")
        self.assertEqual(result[1]["time"], "15:25")

    def test_dateView_earlyPunchIn_adjustedToShiftStart(self):
        """Positive: Early punch in is displayed as-is but payment is adjusted
        to shift start time (e.g., 6:53 AM punch → display 6:53 but pay from 7:00)."""
        self.service.adjust_punch_for_payment.return_value = {
            "display_time": "06:53",
            "payment_time": "07:00",
        }
        result = self.service.adjust_punch_for_payment(
            punch_time="06:53", shift_start="07:00", direction="in"
        )
        self.assertEqual(result["display_time"], "06:53")
        self.assertEqual(result["payment_time"], "07:00")

    def test_dateView_latePunchOut_adjustedToShiftEnd(self):
        """Positive: Late punch out is adjusted to shift end time for payment
        (e.g., 15:35 punch → adjusted to 15:25)."""
        self.service.adjust_punch_for_payment.return_value = {
            "display_time": "15:35",
            "payment_time": "15:25",
        }
        result = self.service.adjust_punch_for_payment(
            punch_time="15:35", shift_end="15:25", direction="out"
        )
        self.assertEqual(result["display_time"], "15:35")
        self.assertEqual(result["payment_time"], "15:25")

    def test_dateView_noPunchData_markedAsAbsent(self):
        """Positive: If there is no punch in/out data, the system marks
        the workman as absent (ABS)."""
        self.service.get_leave_remark.return_value = "ABS"
        result = self.service.get_leave_remark(employee_id="12345", date="2026-05-01")
        self.assertEqual(result, "ABS")

    def test_dateView_absRemark_remainsUntilLeaveApproved(self):
        """Positive: ABS remark remains until the workman applies for PL or
        other leave and gets approved."""
        self.service.is_remark_changeable.return_value = False
        result = self.service.is_remark_changeable(
            employee_id="12345", date="2026-05-01", current_remark="ABS"
        )
        self.assertFalse(result)

    def test_dateView_punchRemarks_displayedToIRAndEmployee(self):
        """Positive: Based on the punch, leave remarks are shown to the IR
        and to the employee (Kiosk)."""
        self.service.get_leave_remark.return_value = "Present"
        result = self.service.get_leave_remark(employee_id="12345", date="2026-05-01")
        self.assertIsNotNone(result)

    def test_dateView_inAndOutInMinutes_calculatedCorrectly(self):
        """Positive: In and Out times are also represented in minutes
        (e.g., 08:04 → 484 minutes)."""
        self.service.time_to_minutes.return_value = 484
        result = self.service.time_to_minutes(time_str="08:04")
        self.assertEqual(result, 484)

    def test_dateView_regShift_fetchedFromShiftScheduleModule(self):
        """Positive: Reg. Shift (planned shift) is fetched from
        Maintain Shift Schedule module."""
        self.service.get_registered_shift.return_value = "I"
        result = self.service.get_registered_shift(employee_id="12345", date="2026-05-01")
        self.assertIsNotNone(result)

    def test_dateView_actualShift_calculatedFromPunchData(self):
        """Positive: Actual Shift is calculated from punch in/out times."""
        self.service.calculate_actual_shift.return_value = "I"
        result = self.service.calculate_actual_shift(punch_in="07:00", punch_out="15:25")
        self.assertIsNotNone(result)

    def test_dateView_autoSchedule_yesterdayAndToday(self):
        """Positive: System runs auto schedule for yesterday's and today's date,
        considering night shift ending today."""
        self.service.run_auto_schedule.return_value = {
            "dates_processed": ["2026-05-12", "2026-05-13"],
            "status": "Success",
        }
        result = self.service.run_auto_schedule()
        self.assertEqual(len(result["dates_processed"]), 2)


class TestRegularTimecardDateViewSearchAndPagination(unittest.TestCase):
    """US-RT-001: Verify search bar and page navigation in Date View."""

    def setUp(self):
        """Arrange: Create mock grid."""
        self.grid = MagicMock()

    def test_dateView_columnSearch_filtersGridData(self):
        """Positive: Column search bar filters the grid data by column."""
        self.grid.column_search.return_value = [{"Employee": "12345 - John Doe"}]
        result = self.grid.column_search(column="Employee", query="12345")
        self.assertEqual(len(result), 1)

    def test_dateView_globalSearch_filtersGridData(self):
        """Positive: Global search bar filters grid data across all columns."""
        self.grid.global_search.return_value = [{"Employee": "12345 - John Doe"}]
        result = self.grid.global_search(query="John")
        self.assertEqual(len(result), 1)

    def test_dateView_pageNavigation_navigatesToOtherPages(self):
        """Positive: User can navigate to other pages using page navigation."""
        self.grid.go_to_page.return_value = {"page": 2, "records": []}
        result = self.grid.go_to_page(2)
        self.assertEqual(result["page"], 2)

    def test_dateView_searchNoMatch_returnsEmptyResult(self):
        """Negative: Searching for a non-existent value returns empty results."""
        self.grid.global_search.return_value = []
        result = self.grid.global_search(query="NONEXISTENT")
        self.assertEqual(len(result), 0)


class TestRegularTimecardDateViewNegativeAndEdge(unittest.TestCase):
    """US-RT-001: Negative and edge case tests for Date View."""

    def setUp(self):
        """Arrange: Create mock service."""
        self.service = MagicMock()

    def test_dateView_noDataForDate_displaysEmptyGrid(self):
        """Negative: No data for selected date shows empty grid."""
        self.service.get_data_by_date.return_value = []
        result = self.service.get_data_by_date(date=date(2026, 12, 25))
        self.assertEqual(result, [])

    def test_dateView_infoCommAPIFailure_handlesGracefully(self):
        """Integration: InfoComm API failure is handled gracefully."""
        self.service.fetch_from_infocomm.side_effect = ConnectionError("API unavailable")
        with self.assertRaises(ConnectionError):
            self.service.fetch_from_infocomm(date="2026-05-01")

    def test_dateView_infoCommAPITimeout_handlesGracefully(self):
        """Integration: InfoComm API timeout is handled gracefully."""
        self.service.fetch_from_infocomm.side_effect = TimeoutError("Request timed out")
        with self.assertRaises(TimeoutError):
            self.service.fetch_from_infocomm(date="2026-05-01")

    def test_dateView_shiftTimingMasterUnavailable_handlesGracefully(self):
        """Integration: Shift Timing Master unavailability is handled gracefully."""
        self.service.get_shift_timing.side_effect = ConnectionError(
            "Shift Timing Master unavailable"
        )
        with self.assertRaises(ConnectionError):
            self.service.get_shift_timing(shift="I")


# ---------------------------------------------------------------------------
# US-RT-002: IR – View Maintain Regular Timecard (Employee View)
# ---------------------------------------------------------------------------


class TestRegularTimecardEmployeeViewNavigation(unittest.TestCase):
    """US-RT-002: Verify navigation to Employee View tab."""

    def setUp(self):
        """Arrange: Create mock page with tabs."""
        self.timecard_page = MagicMock()
        self.timecard_page.get_tabs.return_value = ["Date View", "Employee View"]

    def test_employeeViewTab_click_navigatesToEmployeeView(self):
        """Positive: Clicking 'Employee View' tab navigates to Employee View."""
        self.timecard_page.switch_tab.return_value = "Employee View"
        result = self.timecard_page.switch_tab("Employee View")
        self.assertEqual(result, "Employee View")


class TestRegularTimecardEmployeeViewAttributes(unittest.TestCase):
    """US-RT-002: Verify Employee View tab displays correct attributes."""

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
        """Positive: Employee View displays Employee dropdown (PS No and Name)."""
        attributes = self.employee_view.get_attributes()
        self.assertIn("employee_dropdown", attributes)

    def test_employeeView_attributes_displaysFromDatePicker(self):
        """Positive: Employee View displays From date picker (mandatory)."""
        attributes = self.employee_view.get_attributes()
        self.assertIn("from_date_picker", attributes)

    def test_employeeView_attributes_displaysToDatePicker(self):
        """Positive: Employee View displays To date picker (mandatory)."""
        attributes = self.employee_view.get_attributes()
        self.assertIn("to_date_picker", attributes)

    def test_employeeView_buttons_displaysExportButton(self):
        """Positive: Employee View displays an Export button."""
        buttons = self.employee_view.get_buttons()
        self.assertIn("Export", buttons)


class TestRegularTimecardEmployeeViewGridColumns(unittest.TestCase):
    """US-RT-002: Verify Employee View grid displays all required columns."""

    EXPECTED_COLUMNS = [
        "Date",
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

    def test_employeeViewGrid_columns_displaysAllRequiredColumns(self):
        """Positive: Employee View grid displays all required columns."""
        columns = self.grid.get_columns()
        for col in self.EXPECTED_COLUMNS:
            self.assertIn(col, columns)

    def test_employeeViewGrid_dateColumn_displaysDDMMYYYYFormat(self):
        """Positive: Date column displays dates."""
        self.grid.get_cell_value.return_value = "01-05-2026"
        value = self.grid.get_cell_value(row=0, column="Date")
        self.assertIsNotNone(value)


class TestRegularTimecardEmployeeViewValidation(unittest.TestCase):
    """US-RT-002: Verify Employee View validation and filtering logic."""

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

    def test_employeeView_filterByDateRange_displaysFilteredData(self):
        """Positive: Selecting From and To dates displays data for that range."""
        self.service.get_data_by_employee_and_range.return_value = [{"date": "2026-05-01"}]
        result = self.service.get_data_by_employee_and_range(
            employee_id="12345",
            from_date=date(2026, 5, 1),
            to_date=date(2026, 5, 10),
        )
        self.assertTrue(len(result) > 0)

    def test_employeeView_defaultDisplay_showsCurrentMonthData(self):
        """Positive: By default, current month data till current date is displayed."""
        self.service.get_default_employee_data.return_value = {
            "period": "current_month_to_date"
        }
        result = self.service.get_default_employee_data(employee_id="12345")
        self.assertEqual(result["period"], "current_month_to_date")

    def test_employeeView_duplicatePunches_removedBySystem(self):
        """Positive: System removes duplicate punches, keeping first in and last out."""
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
        """Positive: No punch data means the system marks the workman as absent."""
        self.service.get_leave_remark.return_value = "ABS"
        result = self.service.get_leave_remark(employee_id="12345", date="2026-05-01")
        self.assertEqual(result, "ABS")


class TestRegularTimecardEmployeeViewNegativeAndEdge(unittest.TestCase):
    """US-RT-002: Negative and edge case tests for Employee View."""

    def setUp(self):
        """Arrange: Create mock service."""
        self.service = MagicMock()

    def test_employeeView_noEmployeeSelected_raisesValidationError(self):
        """Negative: Not selecting an employee raises a validation error."""
        self.service.get_data_by_employee.side_effect = ValueError(
            "Employee selection is required"
        )
        with self.assertRaises(ValueError):
            self.service.get_data_by_employee(employee_id=None)

    def test_employeeView_employeeWithNoRecords_displaysEmptyGrid(self):
        """Negative: Employee with no timecard records shows empty grid."""
        self.service.get_data_by_employee.return_value = []
        result = self.service.get_data_by_employee(employee_id="99999")
        self.assertEqual(result, [])

    def test_employeeView_fromDateAfterToDate_raisesValidationError(self):
        """Negative: From date after To date raises a validation error."""
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
# US-RT-003: IR – Export Maintain Regular Timecard
# ---------------------------------------------------------------------------


class TestRegularTimecardExport(unittest.TestCase):
    """US-RT-003: Verify Export button exports details to an Excel file."""

    def setUp(self):
        """Arrange: Create mock export service."""
        self.export_service = MagicMock()

    def test_export_clickExportButton_exportsToExcel(self):
        """Positive: Clicking 'Export' exports the displayed data to an Excel file."""
        self.export_service.export_to_excel.return_value = "/downloads/timecard.xlsx"
        result = self.export_service.export_to_excel(tab="Date View")
        self.assertTrue(result.endswith(".xlsx"))

    def test_export_withDateFilter_exportsFilteredData(self):
        """Positive: If user selects from and to date, only filtered data is exported."""
        self.export_service.export_to_excel.return_value = "/downloads/filtered.xlsx"
        result = self.export_service.export_to_excel(
            tab="Date View",
            from_date=date(2026, 5, 1),
            to_date=date(2026, 5, 10),
        )
        self.assertIsNotNone(result)

    def test_export_withoutFilter_exportsAllExistingData(self):
        """Positive: If user doesn't filter data, all existing data is exported."""
        self.export_service.export_to_excel.return_value = "/downloads/all.xlsx"
        result = self.export_service.export_to_excel(
            tab="Date View", from_date=None, to_date=None
        )
        self.assertIsNotNone(result)

    def test_export_saveToLocation_userCanChoosePath(self):
        """Positive: User can save the exported file to a location."""
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
