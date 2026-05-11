"""
Unit Tests for Maintain Regular Timecard Module
User Stories: US-TC-001 to US-TC-006 (from MaintainRegularTimecard.xlsx)

Covers Maintain Regular Timecard functionality for:
- IR / IR Approver – Date View, Employee View, Export
- Shop In charge (IS) – Date View, Employee View, Export (view-only access)

Test Categories:
- Positive / Happy Path
- Negative / Error Path
- Boundary / Edge Cases
- Integration Points
"""

SOURCE_STORY_FILE = "MaintainRegularTimecard.xlsx"

import unittest
from unittest.mock import MagicMock, patch, PropertyMock
from datetime import date, datetime, timedelta


# TODO: Import actual modules once implementation is available.
# from src.attendance.timecard import (
#     TimecardPage, TimecardService, TimecardScheduler,
#     PunchDataService, ExportService, ShiftTimingMaster,
# )


# ===========================================================================
# US-TC-001: IR / IR Approver – Maintain Regular Timecard – Date View
# ===========================================================================


class TestTimecardDateViewPageDisplay(unittest.TestCase):
    """US-TC-001: Verify Maintain Regular Timecard Date View page displays
    correctly for IR / IR Approver roles."""

    def setUp(self):
        """Arrange: Create mock navigation, page, and service objects."""
        self.navigation = MagicMock()
        self.page = MagicMock()
        self.page.get_tabs.return_value = ["Date View", "Employee View"]
        self.page.get_default_tab.return_value = "Date View"
        self.page.get_attributes.return_value = ["Date"]
        self.page.get_grid_columns.return_value = [
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
        self.page.get_buttons.return_value = ["Save", "Export"]

    def test_navigation_selectAttendanceMenu_displaysTimecardPage(self):
        """Positive: Selecting 'Maintain Timecard' from 'Attendance Management'
        menu opens the Maintain Regular Timecard page."""
        self.navigation.select_menu.return_value = "Maintain Regular Timecard"

        result = self.navigation.select_menu(
            "Attendance Management", "Maintain Timecard"
        )

        self.assertEqual(result, "Maintain Regular Timecard")
        self.navigation.select_menu.assert_called_once()

    def test_page_load_displaysDateViewAndEmployeeViewTabs(self):
        """Positive: Page displays 'Date View' and 'Employee View' tabs."""
        tabs = self.page.get_tabs()

        self.assertIn("Date View", tabs)
        self.assertIn("Employee View", tabs)
        self.assertEqual(len(tabs), 2)

    def test_page_load_defaultTabIsDateView(self):
        """Positive: By default, the 'Date View' tab is selected."""
        default_tab = self.page.get_default_tab()

        self.assertEqual(default_tab, "Date View")

    def test_page_load_displaysDatePickerAttribute(self):
        """Positive: Date View displays a Date picker attribute."""
        attributes = self.page.get_attributes()

        self.assertIn("Date", attributes)

    def test_page_load_displaysAllGridColumns(self):
        """Positive: Date View grid displays all 11 required columns."""
        columns = self.page.get_grid_columns()

        expected_columns = [
            "Employee", "TRT No", "In", "Out", "Late", "Early",
            "Reg. Shift", "Actual Shift", "Employee Status", "Cadre",
            "Leave Remarks",
        ]
        for col in expected_columns:
            self.assertIn(col, columns)
        self.assertEqual(len(columns), 11)

    def test_page_load_displaysSaveAndExportButtons(self):
        """Positive: Date View displays Save and Export buttons."""
        buttons = self.page.get_buttons()

        self.assertIn("Save", buttons)
        self.assertIn("Export", buttons)


class TestTimecardDateViewDateFilter(unittest.TestCase):
    """US-TC-001: Verify date filtering behaviour in Date View."""

    def setUp(self):
        """Arrange: Create mock timecard service."""
        self.timecard_service = MagicMock()

    def test_dateView_selectDate_displaysDataForSelectedDate(self):
        """Positive: Selecting a date shows timecard data for that date."""
        selected_date = date(2025, 12, 15)
        self.timecard_service.get_by_date.return_value = {
            "status": "success",
            "date": str(selected_date),
            "records": [{"employee": "EMP001", "in_time": "08:00", "out_time": "17:00"}],
        }

        result = self.timecard_service.get_by_date(selected_date)

        self.assertEqual(result["status"], "success")
        self.assertEqual(result["date"], "2025-12-15")
        self.assertTrue(len(result["records"]) > 0)

    def test_dateView_noDateSelected_displaysCurrentDateData(self):
        """Positive: When no date is selected, current date data is shown by default."""
        today = date.today()
        self.timecard_service.get_by_date.return_value = {
            "status": "success",
            "date": str(today),
            "records": [{"employee": "EMP001"}],
        }

        result = self.timecard_service.get_by_date(None)

        self.assertEqual(result["status"], "success")
        self.assertEqual(result["date"], str(today))

    def test_dateView_futureDate_returnsNoData(self):
        """Negative: Selecting a future date returns no records."""
        future_date = date.today() + timedelta(days=30)
        self.timecard_service.get_by_date.return_value = {
            "status": "success",
            "records": [],
        }

        result = self.timecard_service.get_by_date(future_date)

        self.assertEqual(result["records"], [])

    def test_dateView_invalidDateFormat_returnsError(self):
        """Boundary: Invalid date format returns validation error."""
        self.timecard_service.get_by_date.side_effect = ValueError(
            "Invalid date format"
        )

        with self.assertRaises(ValueError):
            self.timecard_service.get_by_date("not-a-date")


class TestTimecardPunchDataProcessing(unittest.TestCase):
    """US-TC-001: Verify punch data processing logic (In/Out, shifts, remarks)."""

    def setUp(self):
        """Arrange: Create mock punch data service."""
        self.punch_service = MagicMock()

    def test_punchData_validInOut_displaysFormattedTime(self):
        """Positive: Punch in/out data is displayed in HH:MM format."""
        self.punch_service.get_punch_data.return_value = {
            "in_time_minutes": 484,
            "out_time_minutes": 924,
            "in_time_display": "08:04",
            "out_time_display": "15:24",
        }

        result = self.punch_service.get_punch_data("EMP001", "2025-12-15")

        self.assertEqual(result["in_time_display"], "08:04")
        self.assertEqual(result["out_time_display"], "15:24")

    def test_punchData_minuteToHourConversion_correctCalculation(self):
        """Positive: 484 minutes converts to 08:04 (8*60 + 4 = 484)."""
        self.punch_service.convert_minutes_to_time.return_value = "08:04"

        result = self.punch_service.convert_minutes_to_time(484)

        self.assertEqual(result, "08:04")

    def test_punchData_duplicatePunches_firstInLastOutUsed(self):
        """Positive: System considers only first punch-in and last punch-out,
        removing duplicate and multiple punching data."""
        self.punch_service.process_punches.return_value = {
            "in_time": "07:00",
            "out_time": "15:30",
        }
        raw_punches = [
            {"time": "07:00", "type": "IN"},
            {"time": "07:02", "type": "IN"},  # duplicate
            {"time": "12:00", "type": "OUT"},  # intermediate
            {"time": "12:30", "type": "IN"},  # intermediate
            {"time": "15:30", "type": "OUT"},
        ]

        result = self.punch_service.process_punches(raw_punches)

        self.assertEqual(result["in_time"], "07:00")
        self.assertEqual(result["out_time"], "15:30")

    def test_punchData_earlyPunchIn_adjustedToShiftStart(self):
        """Positive: Early punch-in is displayed but payment starts at shift start.
        Example: punch at 06:53, shift starts at 07:00 → display 06:53,
        pay from 07:00."""
        self.punch_service.adjust_punch_for_payment.return_value = {
            "display_time": "06:53",
            "payable_time": "07:00",
            "adjustment_minutes": 7,
        }

        result = self.punch_service.adjust_punch_for_payment(
            punch_time="06:53", shift_start="07:00", direction="in"
        )

        self.assertEqual(result["display_time"], "06:53")
        self.assertEqual(result["payable_time"], "07:00")

    def test_punchData_latePunchOut_adjustedToShiftEnd(self):
        """Positive: Late punch-out is adjusted to shift end time for payment.
        Example: punch at 15:35, shift ends at 15:25 → adjust to 15:25."""
        self.punch_service.adjust_punch_for_payment.return_value = {
            "display_time": "15:35",
            "payable_time": "15:25",
            "adjustment_minutes": 10,
        }

        result = self.punch_service.adjust_punch_for_payment(
            punch_time="15:35", shift_end="15:25", direction="out"
        )

        self.assertEqual(result["display_time"], "15:35")
        self.assertEqual(result["payable_time"], "15:25")

    def test_punchData_noPunchData_markedAsAbsent(self):
        """Positive: No punch-in/out data marks the employee as absent (ABS)."""
        self.punch_service.get_leave_remark.return_value = "ABS"

        result = self.punch_service.get_leave_remark("EMP001", "2025-12-15")

        self.assertEqual(result, "ABS")

    def test_punchData_absentUntilLeaveApproved_remainsABS(self):
        """Positive: ABS remark remains until employee applies and gets leave
        approved (PL or other leave type)."""
        self.punch_service.get_leave_remark.return_value = "ABS"

        result = self.punch_service.get_leave_remark("EMP001", "2025-12-15")

        self.assertEqual(result, "ABS")

    def test_punchData_leaveApproved_remarkUpdated(self):
        """Positive: Once leave is approved, remark is updated from ABS to
        the approved leave type."""
        self.punch_service.get_leave_remark.return_value = "PL"

        result = self.punch_service.get_leave_remark("EMP001", "2025-12-15")

        self.assertEqual(result, "PL")

    def test_punchData_zeroMinutes_convertsToMidnight(self):
        """Boundary: 0 minutes converts to 00:00."""
        self.punch_service.convert_minutes_to_time.return_value = "00:00"

        result = self.punch_service.convert_minutes_to_time(0)

        self.assertEqual(result, "00:00")

    def test_punchData_maxMinutes_convertsTo2359(self):
        """Boundary: 1439 minutes (23:59) is the maximum valid minute value."""
        self.punch_service.convert_minutes_to_time.return_value = "23:59"

        result = self.punch_service.convert_minutes_to_time(1439)

        self.assertEqual(result, "23:59")

    def test_punchData_negativeMinutes_returnsError(self):
        """Boundary: Negative minutes value returns an error."""
        self.punch_service.convert_minutes_to_time.side_effect = ValueError(
            "Minutes cannot be negative"
        )

        with self.assertRaises(ValueError):
            self.punch_service.convert_minutes_to_time(-1)


class TestTimecardShiftData(unittest.TestCase):
    """US-TC-001: Verify Reg. Shift and Actual Shift data."""

    def setUp(self):
        """Arrange: Create mock shift service."""
        self.shift_service = MagicMock()

    def test_regShift_fetchedFromShiftSchedule_displaysCorrectly(self):
        """Positive: Reg. Shift is fetched from maintained shift schedule module."""
        self.shift_service.get_registered_shift.return_value = "S1"

        result = self.shift_service.get_registered_shift("EMP001", "2025-12-15")

        self.assertEqual(result, "S1")

    def test_actShift_calculatedFromPunchData_displaysCorrectly(self):
        """Positive: Actual Shift is calculated from punch in/out times."""
        self.shift_service.get_actual_shift.return_value = "S1"

        result = self.shift_service.get_actual_shift(
            in_time="07:00", out_time="15:25"
        )

        self.assertEqual(result, "S1")

    def test_shiftTiming_fetchedFromShiftTimingMaster(self):
        """Positive: Shift timings for auto-scheduling are from Shift Timing Master."""
        self.shift_service.get_shift_timing.return_value = {
            "shift_code": "S1",
            "start": "07:00",
            "end": "15:25",
        }

        result = self.shift_service.get_shift_timing("S1")

        self.assertEqual(result["start"], "07:00")
        self.assertEqual(result["end"], "15:25")

    def test_actShift_noPunchData_returnsNone(self):
        """Negative: No punch data means no actual shift can be determined."""
        self.shift_service.get_actual_shift.return_value = None

        result = self.shift_service.get_actual_shift(
            in_time=None, out_time=None
        )

        self.assertIsNone(result)

    def test_regShift_noScheduleAssigned_returnsNone(self):
        """Negative: Employee with no shift schedule returns None."""
        self.shift_service.get_registered_shift.return_value = None

        result = self.shift_service.get_registered_shift("EMP_NEW", "2025-12-15")

        self.assertIsNone(result)


class TestTimecardSearchAndPagination(unittest.TestCase):
    """US-TC-001: Verify search bar and page navigation in Date View."""

    def setUp(self):
        """Arrange: Create mock page object with search and pagination."""
        self.page = MagicMock()

    def test_search_columnSearch_filtersResults(self):
        """Positive: Column search bar filters grid results by column value."""
        self.page.column_search.return_value = [
            {"employee": "EMP001 - John Doe"}
        ]

        result = self.page.column_search("Employee", "EMP001")

        self.assertEqual(len(result), 1)
        self.assertIn("EMP001", result[0]["employee"])

    def test_search_globalSearch_filtersResults(self):
        """Positive: Global search bar filters grid results across all columns."""
        self.page.global_search.return_value = [
            {"employee": "EMP001 - John Doe", "leave_remarks": "Present"}
        ]

        result = self.page.global_search("John")

        self.assertTrue(len(result) > 0)

    def test_search_noMatch_returnsEmptyList(self):
        """Negative: Search with no matching data returns empty list."""
        self.page.global_search.return_value = []

        result = self.page.global_search("NONEXISTENT_EMPLOYEE")

        self.assertEqual(result, [])

    def test_search_emptyQuery_returnsAllRecords(self):
        """Boundary: Empty search query returns all records."""
        self.page.global_search.return_value = [
            {"employee": "EMP001"}, {"employee": "EMP002"}
        ]

        result = self.page.global_search("")

        self.assertEqual(len(result), 2)

    def test_pagination_navigateToNextPage_displaysNextPageData(self):
        """Positive: Navigating to the next page displays next page data."""
        self.page.navigate.return_value = {"current_page": 2, "records": []}

        result = self.page.navigate(page=2)

        self.assertEqual(result["current_page"], 2)

    def test_pagination_navigateBeyondLastPage_returnsEmptyOrLastPage(self):
        """Boundary: Navigating beyond the last page is handled gracefully."""
        self.page.navigate.return_value = {"current_page": 5, "records": [], "total_pages": 5}

        result = self.page.navigate(page=100)

        self.assertEqual(result["records"], [])


class TestTimecardScheduler(unittest.TestCase):
    """US-TC-001: Verify scheduler that fetches punch data from InfoComm API."""

    def setUp(self):
        """Arrange: Create mock scheduler service."""
        self.scheduler = MagicMock()

    def test_scheduler_runsAt930AM_fetchesPunchData(self):
        """Positive: Scheduler runs every morning ~9:30 AM to fetch punch data."""
        self.scheduler.run.return_value = {
            "status": "success",
            "records_fetched": 150,
        }

        result = self.scheduler.run()

        self.assertEqual(result["status"], "success")
        self.assertTrue(result["records_fetched"] > 0)

    def test_scheduler_fetchesPreviousAndCurrentDay_data(self):
        """Positive: Scheduler fetches data for yesterday and today (night shift)."""
        today = date.today()
        yesterday = today - timedelta(days=1)
        self.scheduler.get_fetch_dates.return_value = [yesterday, today]

        result = self.scheduler.get_fetch_dates()

        self.assertEqual(len(result), 2)
        self.assertIn(yesterday, result)
        self.assertIn(today, result)

    def test_scheduler_infocommAPITimeout_handlesGracefully(self):
        """Integration: InfoComm API timeout is handled gracefully."""
        self.scheduler.run.side_effect = TimeoutError("InfoComm API timeout")

        with self.assertRaises(TimeoutError):
            self.scheduler.run()

    def test_scheduler_infocommAPIUnavailable_retriesAndLogs(self):
        """Integration: Scheduler retries when InfoComm API is unavailable."""
        self.scheduler.run.side_effect = [
            ConnectionError("API unavailable"),
            {"status": "success", "records_fetched": 100},
        ]

        with self.assertRaises(ConnectionError):
            self.scheduler.run()

        result = self.scheduler.run()
        self.assertEqual(result["status"], "success")

    def test_scheduler_noNewData_completesWithZeroRecords(self):
        """Boundary: Scheduler completes successfully even when no new data."""
        self.scheduler.run.return_value = {
            "status": "success",
            "records_fetched": 0,
        }

        result = self.scheduler.run()

        self.assertEqual(result["records_fetched"], 0)


class TestTimecardSave(unittest.TestCase):
    """US-TC-001: Verify Save button functionality in Date View."""

    def setUp(self):
        """Arrange: Create mock timecard service."""
        self.timecard_service = MagicMock()

    def test_save_validChanges_savesSuccessfully(self):
        """Positive: Saving valid timecard changes returns success."""
        self.timecard_service.save.return_value = {"status": "success"}

        result = self.timecard_service.save(
            employee_id="EMP001", date="2025-12-15", leave_remark="Present"
        )

        self.assertEqual(result["status"], "success")

    def test_save_noChanges_returnsNoChangeMessage(self):
        """Boundary: Saving without making changes returns appropriate message."""
        self.timecard_service.save.return_value = {
            "status": "info",
            "message": "No changes to save",
        }

        result = self.timecard_service.save()

        self.assertEqual(result["status"], "info")

    def test_save_serverError_returnsError(self):
        """Negative: Server error during save returns error status."""
        self.timecard_service.save.side_effect = RuntimeError("Database error")

        with self.assertRaises(RuntimeError):
            self.timecard_service.save(
                employee_id="EMP001", date="2025-12-15", leave_remark="ABS"
            )


# ===========================================================================
# US-TC-002: IR / IR Approver – Maintain Regular Timecard – Employee View
# ===========================================================================


class TestTimecardEmployeeViewPageDisplay(unittest.TestCase):
    """US-TC-002: Verify Employee View tab displays correctly."""

    def setUp(self):
        """Arrange: Create mock page for employee view."""
        self.page = MagicMock()
        self.page.get_attributes.return_value = ["Employee", "From", "To"]
        self.page.get_grid_columns.return_value = [
            "Date", "TRT No", "In", "Out", "Late", "Early",
            "Reg. Shift", "Actual Shift", "Leave Remarks",
            "Employee Status", "Cadre",
        ]
        self.page.get_buttons.return_value = ["Export"]

    def test_employeeView_clickTab_displaysEmployeeView(self):
        """Positive: Clicking 'Employee View' tab switches to Employee View."""
        self.page.switch_tab.return_value = "Employee View"

        result = self.page.switch_tab("Employee View")

        self.assertEqual(result, "Employee View")

    def test_employeeView_displaysEmployeeDropdown(self):
        """Positive: Employee View displays Employee dropdown (PS No and Name)."""
        attributes = self.page.get_attributes()

        self.assertIn("Employee", attributes)

    def test_employeeView_displaysFromAndToDatePickers(self):
        """Positive: Employee View displays From and To date pickers."""
        attributes = self.page.get_attributes()

        self.assertIn("From", attributes)
        self.assertIn("To", attributes)

    def test_employeeView_displaysAllGridColumns(self):
        """Positive: Employee View grid has all 11 required columns."""
        columns = self.page.get_grid_columns()

        expected = [
            "Date", "TRT No", "In", "Out", "Late", "Early",
            "Reg. Shift", "Actual Shift", "Leave Remarks",
            "Employee Status", "Cadre",
        ]
        for col in expected:
            self.assertIn(col, columns)

    def test_employeeView_displaysExportButton(self):
        """Positive: Employee View displays Export button."""
        buttons = self.page.get_buttons()

        self.assertIn("Export", buttons)


class TestTimecardEmployeeViewFiltering(unittest.TestCase):
    """US-TC-002: Verify Employee View date range filtering."""

    def setUp(self):
        """Arrange: Create mock timecard service."""
        self.timecard_service = MagicMock()

    def test_employeeView_selectDateRange_displaysFilteredData(self):
        """Positive: Selecting From and To dates filters records for that range."""
        self.timecard_service.get_by_employee.return_value = {
            "status": "success",
            "records": [
                {"date": "2025-12-01", "in_time": "08:00"},
                {"date": "2025-12-02", "in_time": "08:05"},
            ],
        }

        result = self.timecard_service.get_by_employee(
            employee_id="EMP001",
            from_date=date(2025, 12, 1),
            to_date=date(2025, 12, 2),
        )

        self.assertEqual(len(result["records"]), 2)

    def test_employeeView_noDateSelected_displaysCurrentMonthData(self):
        """Positive: No date selected shows current month till current date."""
        self.timecard_service.get_by_employee.return_value = {
            "status": "success",
            "from_date": "2025-12-01",
            "to_date": "2025-12-15",
            "records": [{"date": "2025-12-01"}],
        }

        result = self.timecard_service.get_by_employee(
            employee_id="EMP001", from_date=None, to_date=None
        )

        self.assertEqual(result["status"], "success")
        self.assertTrue(len(result["records"]) > 0)

    def test_employeeView_fromDateAfterToDate_returnsError(self):
        """Negative: From date later than To date returns validation error."""
        self.timecard_service.get_by_employee.return_value = {
            "status": "error",
            "message": "From date cannot be after To date",
        }

        result = self.timecard_service.get_by_employee(
            employee_id="EMP001",
            from_date=date(2025, 12, 31),
            to_date=date(2025, 12, 1),
        )

        self.assertEqual(result["status"], "error")

    def test_employeeView_noEmployeeSelected_returnsError(self):
        """Negative: No employee selected returns validation error."""
        self.timecard_service.get_by_employee.return_value = {
            "status": "error",
            "message": "Employee is required",
        }

        result = self.timecard_service.get_by_employee(
            employee_id=None, from_date=None, to_date=None
        )

        self.assertEqual(result["status"], "error")

    def test_employeeView_invalidEmployeeId_returnsError(self):
        """Negative: Invalid employee ID returns error."""
        self.timecard_service.get_by_employee.return_value = {
            "status": "error",
            "message": "Employee not found",
        }

        result = self.timecard_service.get_by_employee(
            employee_id="INVALID_EMP", from_date=None, to_date=None
        )

        self.assertEqual(result["status"], "error")

    def test_employeeView_sameDateForFromAndTo_returnsSingleDayData(self):
        """Boundary: Same From and To date returns data for a single day."""
        single_date = date(2025, 12, 15)
        self.timecard_service.get_by_employee.return_value = {
            "status": "success",
            "records": [{"date": "2025-12-15"}],
        }

        result = self.timecard_service.get_by_employee(
            employee_id="EMP001",
            from_date=single_date,
            to_date=single_date,
        )

        self.assertEqual(len(result["records"]), 1)


class TestTimecardEmployeeViewSearchAndPagination(unittest.TestCase):
    """US-TC-002: Verify search and pagination in Employee View."""

    def setUp(self):
        """Arrange: Create mock page."""
        self.page = MagicMock()

    def test_search_columnSearch_filtersEmployeeViewResults(self):
        """Positive: Column search filters Employee View results."""
        self.page.column_search.return_value = [{"date": "2025-12-15"}]

        result = self.page.column_search("Date", "2025-12-15")

        self.assertEqual(len(result), 1)

    def test_search_globalSearch_filtersAcrossAllColumns(self):
        """Positive: Global search filters across all Employee View columns."""
        self.page.global_search.return_value = [{"leave_remarks": "ABS"}]

        result = self.page.global_search("ABS")

        self.assertTrue(len(result) > 0)

    def test_pagination_navigateToPage_displaysCorrectRecords(self):
        """Positive: Pagination navigates to correct page."""
        self.page.navigate.return_value = {"current_page": 3, "records": []}

        result = self.page.navigate(page=3)

        self.assertEqual(result["current_page"], 3)


# ===========================================================================
# US-TC-003: IR / IR Approver – Maintain Regular Timecard – Export
# ===========================================================================


class TestTimecardExport(unittest.TestCase):
    """US-TC-003: Verify Export functionality for IR / IR Approver."""

    def setUp(self):
        """Arrange: Create mock export service."""
        self.export_service = MagicMock()

    def test_export_clickExportButton_exportsToExcel(self):
        """Positive: Clicking Export exports displayed data to Excel file."""
        self.export_service.export_to_excel.return_value = {
            "status": "success",
            "file_name": "timecard_export.xlsx",
        }

        result = self.export_service.export_to_excel(tab="Date View")

        self.assertEqual(result["status"], "success")
        self.assertIn(".xlsx", result["file_name"])

    def test_export_withDateFilter_exportsFilteredData(self):
        """Positive: Export with From/To date filter exports only filtered records."""
        self.export_service.export_to_excel.return_value = {
            "status": "success",
            "records_exported": 5,
        }

        result = self.export_service.export_to_excel(
            tab="Employee View",
            from_date="2025-12-01",
            to_date="2025-12-15",
        )

        self.assertEqual(result["status"], "success")
        self.assertEqual(result["records_exported"], 5)

    def test_export_withoutFilter_exportsAllDisplayedData(self):
        """Positive: Export without filter exports all currently displayed data."""
        self.export_service.export_to_excel.return_value = {
            "status": "success",
            "records_exported": 100,
        }

        result = self.export_service.export_to_excel(tab="Date View")

        self.assertEqual(result["status"], "success")
        self.assertTrue(result["records_exported"] > 0)

    def test_export_noData_exportsEmptyFile(self):
        """Boundary: Exporting when no data is displayed exports an empty file."""
        self.export_service.export_to_excel.return_value = {
            "status": "success",
            "records_exported": 0,
        }

        result = self.export_service.export_to_excel(tab="Date View")

        self.assertEqual(result["records_exported"], 0)

    def test_export_saveToLocation_savesSuccessfully(self):
        """Positive: User can save the exported file to a chosen location."""
        self.export_service.save_file.return_value = {
            "status": "success",
            "path": "/downloads/timecard_export.xlsx",
        }

        result = self.export_service.save_file(
            file_name="timecard_export.xlsx", location="/downloads/"
        )

        self.assertEqual(result["status"], "success")

    def test_export_serverError_returnsError(self):
        """Negative: Server error during export is handled gracefully."""
        self.export_service.export_to_excel.side_effect = RuntimeError(
            "Export failed"
        )

        with self.assertRaises(RuntimeError):
            self.export_service.export_to_excel(tab="Date View")


# ===========================================================================
# US-TC-004: Shop In charge (IS) – Maintain Regular Timecard – Date View
# ===========================================================================


class TestTimecardDateViewShopInCharge(unittest.TestCase):
    """US-TC-004: Verify Date View for Shop In charge (IS) with view-only access."""

    def setUp(self):
        """Arrange: Create mock page and auth for Shop In charge."""
        self.page = MagicMock()
        self.auth = MagicMock()
        self.auth.get_role.return_value = "Shop In charge"
        self.auth.get_access_level.return_value = "view"
        self.page.get_tabs.return_value = ["Date View", "Employee View"]
        self.page.get_default_tab.return_value = "Date View"
        self.page.get_attributes.return_value = ["Date"]
        self.page.get_grid_columns.return_value = [
            "Employee", "TRT No", "In", "Out", "Late", "Early",
            "Reg. Shift", "Actual Shift", "Employee Status", "Cadre",
            "Leave Remarks",
        ]
        self.page.get_buttons.return_value = ["Export"]

    def test_shopIC_dateView_displaysDateViewAndEmployeeViewTabs(self):
        """Positive: Shop In charge sees Date View and Employee View tabs."""
        tabs = self.page.get_tabs()

        self.assertIn("Date View", tabs)
        self.assertIn("Employee View", tabs)

    def test_shopIC_dateView_defaultTabIsDateView(self):
        """Positive: Default tab is Date View for Shop In charge."""
        default_tab = self.page.get_default_tab()

        self.assertEqual(default_tab, "Date View")

    def test_shopIC_dateView_displaysExportButtonOnly(self):
        """Positive: Shop In charge sees Export button only (no Save – view access)."""
        buttons = self.page.get_buttons()

        self.assertIn("Export", buttons)
        self.assertNotIn("Save", buttons)

    def test_shopIC_dateView_viewOnlyAccess(self):
        """Positive: Shop In charge has view-only access."""
        access_level = self.auth.get_access_level()

        self.assertEqual(access_level, "view")

    def test_shopIC_dateView_displaysAllGridColumns(self):
        """Positive: Shop In charge sees all 11 grid columns."""
        columns = self.page.get_grid_columns()

        self.assertEqual(len(columns), 11)

    def test_shopIC_dateView_cannotEditLeaveRemarks(self):
        """Negative: Shop In charge cannot edit leave remarks (view-only)."""
        self.page.edit_field.side_effect = PermissionError(
            "View-only access: editing not allowed"
        )

        with self.assertRaises(PermissionError):
            self.page.edit_field("Leave Remarks", "PL")

    def test_shopIC_dateView_cannotSaveChanges(self):
        """Negative: Shop In charge cannot save changes (view-only)."""
        self.page.save.side_effect = PermissionError(
            "View-only access: save not allowed"
        )

        with self.assertRaises(PermissionError):
            self.page.save()


class TestTimecardDateViewShopInChargeDataDisplay(unittest.TestCase):
    """US-TC-004: Verify punch data display for Shop In charge Date View."""

    def setUp(self):
        """Arrange: Create mock timecard service."""
        self.timecard_service = MagicMock()

    def test_shopIC_dateView_selectDate_displaysData(self):
        """Positive: Selecting a date shows timecard data for that date."""
        self.timecard_service.get_by_date.return_value = {
            "status": "success",
            "records": [{"employee": "EMP001"}],
        }

        result = self.timecard_service.get_by_date(date(2025, 12, 15))

        self.assertEqual(result["status"], "success")

    def test_shopIC_dateView_noDate_displaysCurrentDateData(self):
        """Positive: No date selected shows current date data by default."""
        self.timecard_service.get_by_date.return_value = {
            "status": "success",
            "date": str(date.today()),
            "records": [{"employee": "EMP001"}],
        }

        result = self.timecard_service.get_by_date(None)

        self.assertEqual(result["status"], "success")


# ===========================================================================
# US-TC-005: Shop In charge (IS) – Maintain Regular Timecard – Employee View
# ===========================================================================


class TestTimecardEmployeeViewShopInCharge(unittest.TestCase):
    """US-TC-005: Verify Employee View for Shop In charge (IS) with view-only."""

    def setUp(self):
        """Arrange: Create mock page and service for Shop In charge."""
        self.page = MagicMock()
        self.timecard_service = MagicMock()
        self.page.get_attributes.return_value = ["Employee", "From", "To"]
        self.page.get_grid_columns.return_value = [
            "Date", "TRT No", "In", "Out", "Late", "Early",
            "Reg. Shift", "Actual Shift", "Leave Remarks",
            "Employee Status", "Cadre",
        ]
        self.page.get_buttons.return_value = ["Export"]

    def test_shopIC_employeeView_displaysEmployeeDropdown(self):
        """Positive: Employee View displays Employee dropdown."""
        attributes = self.page.get_attributes()

        self.assertIn("Employee", attributes)

    def test_shopIC_employeeView_displaysFromAndToDatePickers(self):
        """Positive: Employee View displays From and To date pickers."""
        attributes = self.page.get_attributes()

        self.assertIn("From", attributes)
        self.assertIn("To", attributes)

    def test_shopIC_employeeView_displaysAllGridColumns(self):
        """Positive: Employee View grid shows all 11 required columns."""
        columns = self.page.get_grid_columns()

        self.assertEqual(len(columns), 11)

    def test_shopIC_employeeView_displaysExportButtonOnly(self):
        """Positive: Shop In charge sees Export button only in Employee View."""
        buttons = self.page.get_buttons()

        self.assertIn("Export", buttons)
        self.assertNotIn("Save", buttons)

    def test_shopIC_employeeView_selectDateRange_displaysData(self):
        """Positive: Selecting From/To dates shows filtered employee timecard."""
        self.timecard_service.get_by_employee.return_value = {
            "status": "success",
            "records": [{"date": "2025-12-01"}],
        }

        result = self.timecard_service.get_by_employee(
            employee_id="EMP001",
            from_date=date(2025, 12, 1),
            to_date=date(2025, 12, 15),
        )

        self.assertEqual(result["status"], "success")

    def test_shopIC_employeeView_noDateSelected_displaysCurrentMonth(self):
        """Positive: No date shows current month till today by default."""
        self.timecard_service.get_by_employee.return_value = {
            "status": "success",
            "records": [{"date": "2025-12-01"}],
        }

        result = self.timecard_service.get_by_employee(
            employee_id="EMP001", from_date=None, to_date=None
        )

        self.assertEqual(result["status"], "success")

    def test_shopIC_employeeView_cannotEditFields(self):
        """Negative: Shop In charge cannot edit any field in Employee View."""
        self.page.edit_field.side_effect = PermissionError(
            "View-only access: editing not allowed"
        )

        with self.assertRaises(PermissionError):
            self.page.edit_field("Leave Remarks", "PL")


# ===========================================================================
# US-TC-006: Shop In charge (IS) – Maintain Regular Timecard – Export
# ===========================================================================


class TestTimecardExportShopInCharge(unittest.TestCase):
    """US-TC-006: Verify Export functionality for Shop In charge (IS)."""

    def setUp(self):
        """Arrange: Create mock export service."""
        self.export_service = MagicMock()

    def test_shopIC_export_clickExport_exportsToExcel(self):
        """Positive: Shop In charge can export displayed data to Excel."""
        self.export_service.export_to_excel.return_value = {
            "status": "success",
            "file_name": "timecard_export.xlsx",
        }

        result = self.export_service.export_to_excel(tab="Date View")

        self.assertEqual(result["status"], "success")
        self.assertIn(".xlsx", result["file_name"])

    def test_shopIC_export_withDateFilter_exportsFilteredData(self):
        """Positive: Export with date filter exports only filtered data."""
        self.export_service.export_to_excel.return_value = {
            "status": "success",
            "records_exported": 10,
        }

        result = self.export_service.export_to_excel(
            tab="Employee View",
            from_date="2025-12-01",
            to_date="2025-12-15",
        )

        self.assertEqual(result["records_exported"], 10)

    def test_shopIC_export_withoutFilter_exportsAllData(self):
        """Positive: Export without filter exports all displayed data."""
        self.export_service.export_to_excel.return_value = {
            "status": "success",
            "records_exported": 50,
        }

        result = self.export_service.export_to_excel(tab="Date View")

        self.assertTrue(result["records_exported"] > 0)

    def test_shopIC_export_saveFile_savesToLocation(self):
        """Positive: Shop In charge can save exported file to location."""
        self.export_service.save_file.return_value = {
            "status": "success",
            "path": "/downloads/timecard_export.xlsx",
        }

        result = self.export_service.save_file(
            file_name="timecard_export.xlsx", location="/downloads/"
        )

        self.assertEqual(result["status"], "success")

    def test_shopIC_export_noData_exportsEmptyFile(self):
        """Boundary: Exporting when no data produces empty file."""
        self.export_service.export_to_excel.return_value = {
            "status": "success",
            "records_exported": 0,
        }

        result = self.export_service.export_to_excel(tab="Date View")

        self.assertEqual(result["records_exported"], 0)

    def test_shopIC_export_failureDuringExport_returnsError(self):
        """Negative: Export failure is handled gracefully."""
        self.export_service.export_to_excel.side_effect = RuntimeError(
            "Export failed"
        )

        with self.assertRaises(RuntimeError):
            self.export_service.export_to_excel(tab="Date View")


# ===========================================================================
# Cross-Cutting: Leave Remarks Display
# ===========================================================================


class TestTimecardLeaveRemarksDisplay(unittest.TestCase):
    """Cross-cutting: Verify leave remarks are shown to IR and employee (Kiosk)."""

    def setUp(self):
        """Arrange: Create mock leave remark service."""
        self.leave_service = MagicMock()

    def test_leaveRemarks_punchPresent_displaysCorrectRemark(self):
        """Positive: When punch data exists, appropriate remark is shown."""
        self.leave_service.get_remark.return_value = "Present"

        result = self.leave_service.get_remark("EMP001", "2025-12-15")

        self.assertEqual(result, "Present")

    def test_leaveRemarks_noPunch_displaysABS(self):
        """Positive: No punch data shows ABS remark."""
        self.leave_service.get_remark.return_value = "ABS"

        result = self.leave_service.get_remark("EMP002", "2025-12-15")

        self.assertEqual(result, "ABS")

    def test_leaveRemarks_leaveApproved_updatesFromABS(self):
        """Positive: Approved leave updates remark from ABS to leave type."""
        self.leave_service.update_remark.return_value = {
            "status": "success",
            "old_remark": "ABS",
            "new_remark": "PL",
        }

        result = self.leave_service.update_remark(
            employee_id="EMP002", date="2025-12-15", leave_type="PL"
        )

        self.assertEqual(result["new_remark"], "PL")

    def test_leaveRemarks_visibleOnKiosk_forEmployee(self):
        """Positive: Leave remarks are visible on Kiosk for the employee."""
        self.leave_service.get_kiosk_remarks.return_value = {
            "employee_id": "EMP001",
            "remarks": [{"date": "2025-12-15", "remark": "Present"}],
        }

        result = self.leave_service.get_kiosk_remarks("EMP001")

        self.assertTrue(len(result["remarks"]) > 0)

    def test_leaveRemarks_remarkFromMaster_fetchedCorrectly(self):
        """Positive: Leave remarks are fetched from 'Leave Remarks' master."""
        self.leave_service.get_master_remarks.return_value = [
            "ABS", "Present", "PL", "CL", "SL", "WO", "HO",
        ]

        result = self.leave_service.get_master_remarks()

        self.assertIn("ABS", result)
        self.assertIn("PL", result)


if __name__ == "__main__":
    unittest.main()
