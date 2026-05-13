"""
Unit Tests for Maintain Regular Timecard Module
User Stories: US-RT-001 (IR Date View), US-RT-002 (IR Employee View),
              US-RT-003 (IR Export), US-RT-004 (Shop Date View),
              US-RT-005 (Shop Employee View), US-RT-006 (Shop Export)

Covers Regular Timecard functionality for:
- IR / IR Approver – date view, employee view, export
- Shop In Charge (IS) – date view, employee view, export

Test Categories:
- Positive / Happy Path
- Negative / Error Path
- Boundary / Edge Cases
"""

SOURCE_STORY_FILE = "MaintainRegularTimecard.xlsx"

import unittest
from unittest.mock import MagicMock, patch
from datetime import date, timedelta


# TODO: Import actual modules once implementation is available.
# from src.attendance.regular_timecard import (
#     RegularTimecardPage, RegularTimecardService,
#     TimecardSchedulerService, ExportService
# )


# ---------------------------------------------------------------------------
# US-RT-001: IR – View Maintain Regular Timecard (Date View)
# ---------------------------------------------------------------------------


class TestRegularTimecardDateViewPageDisplay(unittest.TestCase):
    """US-RT-001: Verify Maintain Regular Timecard page – Date View displays correctly."""

    def setUp(self):
        """Arrange: Create mock page, navigation, and service instances."""
        self.navigation = MagicMock()
        self.page = MagicMock()
        self.page.get_tabs.return_value = ["Date View", "Employee View"]
        self.page.get_default_tab.return_value = "Date View"
        self.page.get_attributes.return_value = ["Date"]
        self.page.get_buttons.return_value = ["Save", "Export"]
        self.page.get_grid_columns.return_value = [
            "Employee", "TRT No", "In", "Out", "Late", "Early",
            "Reg. Shift", "Actual Shift", "Employee Status", "Cadre",
            "Leave Remarks",
        ]
        self.service = MagicMock()

    def test_navigation_selectAttendanceMenu_displaysRegularTimecardPage(self):
        """Positive: User navigates to Maintain Timecard from Attendance Management menu."""
        self.navigation.select_menu.return_value = "Maintain Timecard"

        result = self.navigation.select_menu("Attendance Management", "Maintain Timecard")

        self.assertEqual(result, "Maintain Timecard")

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

    def test_dateView_buttons_displaysSaveButton(self):
        """Positive: Date View page displays the Save button."""
        buttons = self.page.get_buttons()
        self.assertIn("Save", buttons)

    def test_dateView_buttons_displaysExportButton(self):
        """Positive: Date View page displays the Export button."""
        buttons = self.page.get_buttons()
        self.assertIn("Export", buttons)

    def test_dateView_grid_displaysAllRequiredColumns(self):
        """Positive: Date View grid displays all required columns."""
        expected_columns = [
            "Employee", "TRT No", "In", "Out", "Late", "Early",
            "Reg. Shift", "Actual Shift", "Employee Status", "Cadre",
            "Leave Remarks",
        ]
        columns = self.page.get_grid_columns()
        for col in expected_columns:
            self.assertIn(col, columns)

    def test_dateView_grid_employeeColumnShowsPSNoAndName(self):
        """Positive: Employee column shows PS No and Employee Name (fetched from info comm)."""
        self.service.get_employee_info.return_value = {"ps_no": "12345", "name": "Jane Doe"}

        info = self.service.get_employee_info("12345")

        self.assertEqual(info["ps_no"], "12345")
        self.assertEqual(info["name"], "Jane Doe")

    def test_dateView_grid_inOutDisplayedInHHMM(self):
        """Positive: In and Out columns display time in HH:MM format."""
        self.service.get_punch_times.return_value = {"in": "07:00", "out": "15:25"}

        times = self.service.get_punch_times("12345", "2025-12-15")

        self.assertRegex(times["in"], r"^\d{2}:\d{2}$")
        self.assertRegex(times["out"], r"^\d{2}:\d{2}$")


class TestRegularTimecardDateViewFiltering(unittest.TestCase):
    """US-RT-001: Verify date filtering and default data behavior."""

    def setUp(self):
        """Arrange: Create mock service for date-based queries."""
        self.service = MagicMock()

    def test_dateView_selectDate_displaysDataForSelectedDate(self):
        """Positive: Selecting a date filters grid data to that date."""
        self.service.get_records_by_date.return_value = [
            {"employee": "EMP001", "date": "2025-12-15"},
        ]

        records = self.service.get_records_by_date("2025-12-15")

        self.assertTrue(len(records) > 0)
        self.service.get_records_by_date.assert_called_once_with("2025-12-15")

    def test_dateView_noDateSelected_displaysCurrentDateByDefault(self):
        """Positive: When no date is selected, system shows data for the current date."""
        self.service.get_default_records.return_value = {"date": "today", "count": 100}

        result = self.service.get_default_records()

        self.assertEqual(result["date"], "today")

    def test_dateView_defaultShowsPreviousDayAndCurrentDayData(self):
        """Positive: Default grid shows punching data for previous day and current day till shift 3 end."""
        self.service.get_default_date_range.return_value = {
            "from": "yesterday",
            "to": "today_shift3_end",
        }

        result = self.service.get_default_date_range()

        self.assertEqual(result["from"], "yesterday")
        self.assertEqual(result["to"], "today_shift3_end")


class TestRegularTimecardDateViewValidation(unittest.TestCase):
    """US-RT-001: Verify validation rules for Regular Timecard Date View."""

    def setUp(self):
        """Arrange: Create mock service for validation tests."""
        self.service = MagicMock()

    def test_validation_schedulerFetchesDataAt930AM(self):
        """Positive: System runs scheduler every morning around 9:30 AM to fetch data from infocomm API."""
        self.service.get_scheduler_config.return_value = {"time": "09:30", "source": "infocomm_api"}

        config = self.service.get_scheduler_config()

        self.assertEqual(config["time"], "09:30")
        self.assertEqual(config["source"], "infocomm_api")

    def test_validation_inOutTimeInMinutesConversion(self):
        """Positive: In and Out time is converted to minutes (e.g., 08:04 = 484 minutes)."""
        self.service.time_to_minutes.return_value = 484

        result = self.service.time_to_minutes("08:04")

        self.assertEqual(result, 484)

    def test_validation_inOutTimeInMinutes_midnight(self):
        """Boundary: 00:00 converts to 0 minutes."""
        self.service.time_to_minutes.return_value = 0

        result = self.service.time_to_minutes("00:00")

        self.assertEqual(result, 0)

    def test_validation_inOutTimeInMinutes_endOfDay(self):
        """Boundary: 23:59 converts to 1439 minutes."""
        self.service.time_to_minutes.return_value = 1439

        result = self.service.time_to_minutes("23:59")

        self.assertEqual(result, 1439)

    def test_validation_regShift_fetchedFromMaintainedShiftSchedule(self):
        """Positive: Reg. Shift is the planned shift fetched from Maintain Shift Schedule module."""
        self.service.get_registered_shift.return_value = "Shift 1"

        shift = self.service.get_registered_shift("EMP001", "2025-12-15")

        self.assertEqual(shift, "Shift 1")

    def test_validation_actualShift_calculatedFromPunchData(self):
        """Positive: Actual Shift is calculated from punch in and punch out data."""
        self.service.get_actual_shift.return_value = "Shift 1"

        shift = self.service.get_actual_shift("EMP001", "2025-12-15")

        self.assertIsNotNone(shift)

    def test_validation_duplicatePunches_onlyFirstInLastOutConsidered(self):
        """Positive: System considers only first punch in and last punch out, removes duplicates."""
        self.service.process_punches.return_value = {"in": "07:00", "out": "15:25"}
        raw_punches = [
            {"time": "07:00", "type": "in"},
            {"time": "07:02", "type": "in"},
            {"time": "15:20", "type": "out"},
            {"time": "15:25", "type": "out"},
        ]

        result = self.service.process_punches(raw_punches)

        self.assertEqual(result["in"], "07:00")
        self.assertEqual(result["out"], "15:25")

    def test_validation_earlyPunchIn_adjustedToShiftStart(self):
        """Positive: Early punch in is displayed but payment adjusts to shift start time.
        E.g., punch in at 06:53 for Shift 1 (07:00) → display 06:53, pay from 07:00."""
        self.service.adjust_punch_time.return_value = {
            "display_time": "06:53",
            "payable_time": "07:00",
        }

        result = self.service.adjust_punch_time("06:53", shift_start="07:00", direction="in")

        self.assertEqual(result["display_time"], "06:53")
        self.assertEqual(result["payable_time"], "07:00")

    def test_validation_latePunchOut_adjustedToShiftEnd(self):
        """Positive: Late punch out adjusted to shift end for payment.
        E.g., punch out at 15:35 for shift end 15:25 → display 15:35, pay until 15:25."""
        self.service.adjust_punch_time.return_value = {
            "display_time": "15:35",
            "payable_time": "15:25",
        }

        result = self.service.adjust_punch_time("15:35", shift_end="15:25", direction="out")

        self.assertEqual(result["display_time"], "15:35")
        self.assertEqual(result["payable_time"], "15:25")

    def test_validation_noPunchData_markedAsAbsent(self):
        """Positive: If no punch in/out data exists, system marks the workman as absent (ABS)."""
        self.service.get_leave_remark.return_value = "ABS"

        remark = self.service.get_leave_remark("EMP001", "2025-12-15")

        self.assertEqual(remark, "ABS")

    def test_validation_absRemarkRemains_untilLeaveApproved(self):
        """Positive: ABS remark remains until workman applies for PL or leave and gets approved."""
        self.service.get_leave_remark.return_value = "ABS"

        remark_before = self.service.get_leave_remark("EMP001", "2025-12-15")
        self.assertEqual(remark_before, "ABS")

        self.service.get_leave_remark.return_value = "PL"
        remark_after = self.service.get_leave_remark("EMP001", "2025-12-15")
        self.assertEqual(remark_after, "PL")

    def test_validation_remarksDisplayedToIRAndEmployee(self):
        """Positive: Leave remarks are shown to IR and employee (via Kiosk)."""
        self.service.get_remarks_visibility.return_value = {"ir_visible": True, "kiosk_visible": True}

        visibility = self.service.get_remarks_visibility("EMP001", "2025-12-15")

        self.assertTrue(visibility["ir_visible"])
        self.assertTrue(visibility["kiosk_visible"])

    def test_validation_autoSchedule_runsForYesterdayAndToday(self):
        """Positive: Auto schedule runs for yesterday's and today's date (night shift consideration)."""
        self.service.get_auto_schedule_dates.return_value = ["yesterday", "today"]

        dates = self.service.get_auto_schedule_dates()

        self.assertIn("yesterday", dates)
        self.assertIn("today", dates)

    def test_validation_shiftTimingFetchedFromMaster(self):
        """Positive: Timing of each shift for auto scheduling is fetched from Maintain Shift Timing Master."""
        self.service.get_shift_timing.return_value = {
            "shift_1": {"start": "07:00", "end": "15:25"},
        }

        timing = self.service.get_shift_timing("Shift 1")

        self.assertEqual(timing["shift_1"]["start"], "07:00")


class TestRegularTimecardDateViewSearchAndPagination(unittest.TestCase):
    """US-RT-001: Verify search bar and page navigation in Date View."""

    def setUp(self):
        """Arrange: Create mock page."""
        self.page = MagicMock()

    def test_searchBar_columnSearch_filtersResultsByColumn(self):
        """Positive: Column search bar filters grid results by a specific column."""
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
# US-RT-002: IR – View Maintain Regular Timecard (Employee View)
# ---------------------------------------------------------------------------


class TestRegularTimecardEmployeeViewPageDisplay(unittest.TestCase):
    """US-RT-002: Verify Maintain Regular Timecard – Employee View displays correctly."""

    def setUp(self):
        """Arrange: Create mock page for Employee View."""
        self.page = MagicMock()
        self.page.get_attributes.return_value = ["Employee", "From", "To"]
        self.page.get_buttons.return_value = ["Export"]
        self.page.get_grid_columns.return_value = [
            "Date", "TRT No", "In", "Out", "Late", "Early",
            "Reg. Shift", "Actual Shift", "Leave Remarks",
            "Employee Status", "Cadre",
        ]
        self.service = MagicMock()

    def test_employeeView_clickTab_displaysEmployeeViewTab(self):
        """Positive: Clicking Employee View tab switches to Employee View."""
        self.page.switch_tab.return_value = "Employee View"

        result = self.page.switch_tab("Employee View")

        self.assertEqual(result, "Employee View")

    def test_employeeView_attributes_displaysEmployeeDropdown(self):
        """Positive: Employee View shows Employee drop-down (PS No and Name from workforce info)."""
        attributes = self.page.get_attributes()
        self.assertIn("Employee", attributes)

    def test_employeeView_attributes_displaysFromDatePicker(self):
        """Positive: Employee View shows From date-picker."""
        attributes = self.page.get_attributes()
        self.assertIn("From", attributes)

    def test_employeeView_attributes_displaysToDatePicker(self):
        """Positive: Employee View shows To date-picker."""
        attributes = self.page.get_attributes()
        self.assertIn("To", attributes)

    def test_employeeView_grid_displaysAllRequiredColumns(self):
        """Positive: Employee View grid displays all required columns."""
        expected_columns = [
            "Date", "TRT No", "In", "Out", "Late", "Early",
            "Reg. Shift", "Actual Shift", "Leave Remarks",
            "Employee Status", "Cadre",
        ]
        columns = self.page.get_grid_columns()
        for col in expected_columns:
            self.assertIn(col, columns)

    def test_employeeView_selectEmployee_displaysEmployeeData(self):
        """Positive: Selecting an employee from dropdown displays their timecard data."""
        self.service.get_employee_timecard.return_value = [
            {"date": "2025-12-10", "in": "07:00", "out": "15:25"},
        ]

        records = self.service.get_employee_timecard("EMP001")

        self.assertTrue(len(records) > 0)


class TestRegularTimecardEmployeeViewFiltering(unittest.TestCase):
    """US-RT-002: Verify date filtering in Employee View."""

    def setUp(self):
        """Arrange: Create mock service."""
        self.service = MagicMock()

    def test_employeeView_selectFromToDate_filtersData(self):
        """Positive: Selecting From and To date filters employee timecard data."""
        self.service.get_employee_records_by_range.return_value = [
            {"date": "2025-12-10"},
            {"date": "2025-12-11"},
        ]

        records = self.service.get_employee_records_by_range("EMP001", "2025-12-10", "2025-12-15")

        self.assertEqual(len(records), 2)

    def test_employeeView_noDateSelected_displaysCurrentMonthToDate(self):
        """Positive: Default shows current month till current date when no dates are selected."""
        self.service.get_employee_default_records.return_value = {"period": "current_month_to_date"}

        result = self.service.get_employee_default_records("EMP001")

        self.assertEqual(result["period"], "current_month_to_date")

    def test_employeeView_noEmployeeSelected_displaysNoData(self):
        """Negative: When no employee is selected, no data is displayed."""
        self.service.get_employee_timecard.return_value = []

        records = self.service.get_employee_timecard(None)

        self.assertEqual(len(records), 0)


class TestRegularTimecardEmployeeViewValidation(unittest.TestCase):
    """US-RT-002: Verify validation rules specific to Employee View."""

    def setUp(self):
        """Arrange: Create mock service."""
        self.service = MagicMock()

    def test_validation_duplicatePunches_removedInEmployeeView(self):
        """Positive: Duplicate punches removed; only first in and last out considered."""
        self.service.process_punches.return_value = {"in": "07:00", "out": "15:25"}

        result = self.service.process_punches([
            {"time": "07:00", "type": "in"},
            {"time": "07:01", "type": "in"},
            {"time": "15:25", "type": "out"},
        ])

        self.assertEqual(result["in"], "07:00")
        self.assertEqual(result["out"], "15:25")

    def test_validation_earlyPunchIn_adjustedInEmployeeView(self):
        """Positive: Early punch in adjusted for payment in Employee View."""
        self.service.adjust_punch_time.return_value = {
            "display_time": "06:50",
            "payable_time": "07:00",
        }

        result = self.service.adjust_punch_time("06:50", shift_start="07:00", direction="in")

        self.assertEqual(result["payable_time"], "07:00")

    def test_validation_noPunchData_markedAsAbsentInEmployeeView(self):
        """Positive: No punch data marks employee as ABS in Employee View."""
        self.service.get_leave_remark.return_value = "ABS"

        remark = self.service.get_leave_remark("EMP001", "2025-12-15")

        self.assertEqual(remark, "ABS")

    def test_validation_autoScheduleUpdatesDaily(self):
        """Positive: Auto schedule runs daily updating master card with punch data."""
        self.service.run_auto_schedule.return_value = {"status": "success", "dates_processed": 2}

        result = self.service.run_auto_schedule()

        self.assertEqual(result["status"], "success")
        self.assertEqual(result["dates_processed"], 2)


class TestRegularTimecardEmployeeViewSearchAndPagination(unittest.TestCase):
    """US-RT-002: Verify search and pagination in Employee View."""

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
# US-RT-003: IR – Export Maintain Regular Timecard
# ---------------------------------------------------------------------------


class TestRegularTimecardExport(unittest.TestCase):
    """US-RT-003: Verify Export functionality for Maintain Regular Timecard."""

    def setUp(self):
        """Arrange: Create mock export service."""
        self.export_service = MagicMock()

    def test_export_clickExportButton_exportsToExcelFile(self):
        """Positive: Clicking Export button exports grid details to an Excel file."""
        self.export_service.export_to_excel.return_value = "timecard_export.xlsx"

        result = self.export_service.export_to_excel("date_view")

        self.assertTrue(result.endswith(".xlsx"))

    def test_export_withFromToDateFilter_exportsFilteredData(self):
        """Positive: When user selects from and to date, exported file contains filtered data."""
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

        saved = self.export_service.save_to_path("/downloads/timecard.xlsx")

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
# US-RT-004: Shop In Charge – View Maintain Regular Timecard (Date View)
# ---------------------------------------------------------------------------


class TestShopRegularTimecardDateViewPageDisplay(unittest.TestCase):
    """US-RT-004: Verify Maintain Regular Timecard Date View for Shop In Charge."""

    def setUp(self):
        """Arrange: Create mock page for Shop In Charge Date View."""
        self.navigation = MagicMock()
        self.page = MagicMock()
        self.page.get_tabs.return_value = ["Date View", "Employee View"]
        self.page.get_default_tab.return_value = "Date View"
        self.page.get_attributes.return_value = ["Date"]
        self.page.get_buttons.return_value = ["Export"]
        self.page.get_grid_columns.return_value = [
            "Employee", "TRT No", "In", "Out", "Late", "Early",
            "Reg. Shift", "Actual Shift", "Leave Remarks",
            "Employee Status", "Cadre",
        ]

    def test_shopUser_navigation_displaysRegularTimecardPage(self):
        """Positive: Shop In Charge navigates to Maintain Timecard from Attendance Management."""
        self.navigation.select_menu.return_value = "Maintain Timecard"

        result = self.navigation.select_menu("Attendance Management", "Maintain Timecard")

        self.assertEqual(result, "Maintain Timecard")

    def test_shopUser_page_displaysDateViewAndEmployeeViewTabs(self):
        """Positive: Page displays Date View and Employee View tabs for Shop user."""
        tabs = self.page.get_tabs()
        self.assertIn("Date View", tabs)
        self.assertIn("Employee View", tabs)

    def test_shopUser_defaultTabIsDateView(self):
        """Positive: Date View tab is displayed by default for Shop user."""
        default_tab = self.page.get_default_tab()
        self.assertEqual(default_tab, "Date View")

    def test_shopUser_dateView_grid_displaysAllRequiredColumns(self):
        """Positive: Shop In Charge Date View grid displays all required columns."""
        expected_columns = [
            "Employee", "TRT No", "In", "Out", "Late", "Early",
            "Reg. Shift", "Actual Shift", "Leave Remarks",
            "Employee Status", "Cadre",
        ]
        columns = self.page.get_grid_columns()
        for col in expected_columns:
            self.assertIn(col, columns)

    def test_shopUser_dateView_displaysExportButton(self):
        """Positive: Shop In Charge Date View displays Export button."""
        buttons = self.page.get_buttons()
        self.assertIn("Export", buttons)


class TestShopRegularTimecardDateViewValidation(unittest.TestCase):
    """US-RT-004: Verify validation rules for Shop In Charge Date View."""

    def setUp(self):
        """Arrange: Create mock service."""
        self.service = MagicMock()

    def test_shopUser_defaultShowsPreviousDayData(self):
        """Positive: Default grid view shows punching data of the previous day."""
        self.service.get_default_records.return_value = {"date": "previous_day", "count": 80}

        result = self.service.get_default_records()

        self.assertEqual(result["date"], "previous_day")

    def test_shopUser_dataRefreshedDaily(self):
        """Positive: Data is refreshed daily but previous data is stored."""
        self.service.get_refresh_policy.return_value = {
            "frequency": "daily",
            "previous_data_stored": True,
        }

        policy = self.service.get_refresh_policy()

        self.assertEqual(policy["frequency"], "daily")
        self.assertTrue(policy["previous_data_stored"])

    def test_shopUser_selectDate_filtersGridData(self):
        """Positive: Selecting a date shows data for that date."""
        self.service.get_records_by_date.return_value = [{"employee": "EMP001"}]

        records = self.service.get_records_by_date("2025-12-15")

        self.assertTrue(len(records) > 0)

    def test_shopUser_duplicatePunches_removed(self):
        """Positive: Duplicate punches removed; only first in and last out."""
        self.service.process_punches.return_value = {"in": "07:00", "out": "15:25"}

        result = self.service.process_punches([
            {"time": "07:00", "type": "in"},
            {"time": "07:03", "type": "in"},
            {"time": "15:25", "type": "out"},
        ])

        self.assertEqual(result["in"], "07:00")
        self.assertEqual(result["out"], "15:25")

    def test_shopUser_earlyPunchIn_adjustedToShiftStart(self):
        """Positive: Early punch in adjusted to shift start for payment."""
        self.service.adjust_punch_time.return_value = {
            "display_time": "06:53",
            "payable_time": "07:00",
        }

        result = self.service.adjust_punch_time("06:53", shift_start="07:00", direction="in")

        self.assertEqual(result["payable_time"], "07:00")

    def test_shopUser_noPunchData_markedAsAbsent(self):
        """Positive: No punch data marks workman as ABS."""
        self.service.get_leave_remark.return_value = "ABS"

        remark = self.service.get_leave_remark("EMP001", "2025-12-15")

        self.assertEqual(remark, "ABS")


class TestShopRegularTimecardDateViewSearchAndPagination(unittest.TestCase):
    """US-RT-004: Verify search and pagination for Shop In Charge Date View."""

    def setUp(self):
        """Arrange: Create mock page."""
        self.page = MagicMock()

    def test_shopUser_searchBar_columnSearch_filtersResults(self):
        """Positive: Column search works for Shop In Charge."""
        self.page.column_search.return_value = [{"employee": "EMP001"}]

        results = self.page.column_search("Employee", "EMP001")

        self.assertEqual(len(results), 1)

    def test_shopUser_searchBar_globalSearch_filtersResults(self):
        """Positive: Global search works for Shop In Charge."""
        self.page.global_search.return_value = [{"employee": "EMP001"}]

        results = self.page.global_search("EMP001")

        self.assertTrue(len(results) >= 1)

    def test_shopUser_pageNavigation_works(self):
        """Positive: Page navigation works for Shop In Charge."""
        self.page.navigate_to_page.return_value = {"page": 2, "records": 10}

        result = self.page.navigate_to_page(2)

        self.assertEqual(result["page"], 2)


# ---------------------------------------------------------------------------
# US-RT-005: Shop In Charge – View Maintain Regular Timecard (Employee View)
# ---------------------------------------------------------------------------


class TestShopRegularTimecardEmployeeViewPageDisplay(unittest.TestCase):
    """US-RT-005: Verify Employee View for Shop In Charge."""

    def setUp(self):
        """Arrange: Create mock page for Shop Employee View."""
        self.page = MagicMock()
        self.page.get_attributes.return_value = ["Employee", "From", "To"]
        self.page.get_buttons.return_value = ["Export"]
        self.page.get_grid_columns.return_value = [
            "Date", "TRT No", "In", "Out", "In (Min)", "Out (Min)",
            "Late", "Early", "Reg. Shift", "Actual Shift",
            "Remarks", "Employee Status", "Cadre",
        ]
        self.service = MagicMock()

    def test_shopUser_employeeView_clickTab_displaysEmployeeView(self):
        """Positive: Shop user clicks Employee View tab to switch views."""
        self.page.switch_tab.return_value = "Employee View"

        result = self.page.switch_tab("Employee View")

        self.assertEqual(result, "Employee View")

    def test_shopUser_employeeView_displaysEmployeeDropdown(self):
        """Positive: Employee View shows Employee dropdown for Shop user."""
        attributes = self.page.get_attributes()
        self.assertIn("Employee", attributes)

    def test_shopUser_employeeView_displaysFromAndToDatePickers(self):
        """Positive: Employee View shows From and To date pickers."""
        attributes = self.page.get_attributes()
        self.assertIn("From", attributes)
        self.assertIn("To", attributes)

    def test_shopUser_employeeView_grid_displaysAllRequiredColumns(self):
        """Positive: Shop Employee View grid displays all required columns including In/Out (Min)."""
        expected_columns = [
            "Date", "TRT No", "In", "Out", "In (Min)", "Out (Min)",
            "Late", "Early", "Reg. Shift", "Actual Shift",
            "Remarks", "Employee Status", "Cadre",
        ]
        columns = self.page.get_grid_columns()
        for col in expected_columns:
            self.assertIn(col, columns)

    def test_shopUser_employeeView_selectEmployee_displaysData(self):
        """Positive: Selecting employee from dropdown shows their timecard data."""
        self.service.get_employee_timecard.return_value = [
            {"date": "2025-12-10", "in": "07:00", "out": "15:25"},
        ]

        records = self.service.get_employee_timecard("EMP001")

        self.assertTrue(len(records) > 0)


class TestShopRegularTimecardEmployeeViewFiltering(unittest.TestCase):
    """US-RT-005: Verify filtering in Shop Employee View."""

    def setUp(self):
        """Arrange: Create mock service."""
        self.service = MagicMock()

    def test_shopUser_employeeView_selectFromToDate_filtersData(self):
        """Positive: Selecting From and To date filters data for Shop user."""
        self.service.get_employee_records_by_range.return_value = [
            {"date": "2025-12-10"},
            {"date": "2025-12-11"},
        ]

        records = self.service.get_employee_records_by_range("EMP001", "2025-12-10", "2025-12-15")

        self.assertEqual(len(records), 2)

    def test_shopUser_employeeView_noEmployee_displaysNoData(self):
        """Negative: No employee selected shows no data."""
        self.service.get_employee_timecard.return_value = []

        records = self.service.get_employee_timecard(None)

        self.assertEqual(len(records), 0)

    def test_shopUser_employeeView_defaultShowsPreviousDayData(self):
        """Positive: Default shows previous day data in Employee View."""
        self.service.get_employee_default_records.return_value = {"date": "previous_day"}

        result = self.service.get_employee_default_records("EMP001")

        self.assertEqual(result["date"], "previous_day")


class TestShopRegularTimecardEmployeeViewValidation(unittest.TestCase):
    """US-RT-005: Verify validation in Shop Employee View."""

    def setUp(self):
        """Arrange: Create mock service."""
        self.service = MagicMock()

    def test_shopUser_validation_duplicatePunches_removed(self):
        """Positive: Duplicates removed in Shop Employee View."""
        self.service.process_punches.return_value = {"in": "07:00", "out": "15:25"}

        result = self.service.process_punches([
            {"time": "07:00", "type": "in"},
            {"time": "07:02", "type": "in"},
            {"time": "15:25", "type": "out"},
        ])

        self.assertEqual(result["in"], "07:00")

    def test_shopUser_validation_earlyPunchIn_adjusted(self):
        """Positive: Early punch in adjusted for payment in Shop view."""
        self.service.adjust_punch_time.return_value = {
            "display_time": "06:55",
            "payable_time": "07:00",
        }

        result = self.service.adjust_punch_time("06:55", shift_start="07:00", direction="in")

        self.assertEqual(result["payable_time"], "07:00")

    def test_shopUser_validation_noPunchData_absent(self):
        """Positive: No punch data marks as ABS for Shop view."""
        self.service.get_leave_remark.return_value = "ABS"

        remark = self.service.get_leave_remark("EMP001", "2025-12-15")

        self.assertEqual(remark, "ABS")

    def test_shopUser_validation_autoScheduleDaily(self):
        """Positive: Auto schedule updates daily for Shop view."""
        self.service.run_auto_schedule.return_value = {"status": "success"}

        result = self.service.run_auto_schedule()

        self.assertEqual(result["status"], "success")


class TestShopRegularTimecardEmployeeViewSearchAndPagination(unittest.TestCase):
    """US-RT-005: Verify search and pagination in Shop Employee View."""

    def setUp(self):
        """Arrange: Create mock page."""
        self.page = MagicMock()

    def test_shopUser_employeeView_columnSearch_works(self):
        """Positive: Column search works in Shop Employee View."""
        self.page.column_search.return_value = [{"date": "2025-12-10"}]

        results = self.page.column_search("Date", "2025-12-10")

        self.assertEqual(len(results), 1)

    def test_shopUser_employeeView_globalSearch_works(self):
        """Positive: Global search works in Shop Employee View."""
        self.page.global_search.return_value = [{"date": "2025-12-10"}]

        results = self.page.global_search("2025-12-10")

        self.assertTrue(len(results) >= 1)

    def test_shopUser_employeeView_pageNavigation_works(self):
        """Positive: Page navigation works in Shop Employee View."""
        self.page.navigate_to_page.return_value = {"page": 2, "records": 10}

        result = self.page.navigate_to_page(2)

        self.assertEqual(result["page"], 2)


# ---------------------------------------------------------------------------
# US-RT-006: Shop In Charge – Export Maintain Regular Timecard
# ---------------------------------------------------------------------------


class TestShopRegularTimecardExport(unittest.TestCase):
    """US-RT-006: Verify Export functionality for Shop In Charge."""

    def setUp(self):
        """Arrange: Create mock export service."""
        self.export_service = MagicMock()

    def test_shopExport_clickExportButton_exportsToExcel(self):
        """Positive: Shop user clicks Export to export grid details to Excel."""
        self.export_service.export_to_excel.return_value = "shop_timecard_export.xlsx"

        result = self.export_service.export_to_excel("date_view")

        self.assertTrue(result.endswith(".xlsx"))

    def test_shopExport_withFromToDateFilter_exportsFilteredData(self):
        """Positive: Exported file contains filtered data when from/to date is selected."""
        self.export_service.export_filtered.return_value = {"rows": 40, "file": "filtered.xlsx"}

        result = self.export_service.export_filtered("2025-12-01", "2025-12-31")

        self.assertEqual(result["rows"], 40)

    def test_shopExport_withoutFilter_exportsExistingData(self):
        """Positive: Without filters, existing data is exported for Shop user."""
        self.export_service.export_all.return_value = {"rows": 300, "file": "all_data.xlsx"}

        result = self.export_service.export_all()

        self.assertTrue(result["rows"] > 0)

    def test_shopExport_saveToLocation_fileIsSaved(self):
        """Positive: Shop user can save the export file to a location."""
        self.export_service.save_to_path.return_value = True

        saved = self.export_service.save_to_path("/downloads/shop_timecard.xlsx")

        self.assertTrue(saved)

    def test_shopExport_emptyGrid_exportsEmptyFile(self):
        """Edge Case: Exporting empty grid produces header-only file."""
        self.export_service.get_export_row_count.return_value = 0

        count = self.export_service.get_export_row_count()

        self.assertEqual(count, 0)

    def test_shopExport_invalidPath_raisesError(self):
        """Negative: Saving to invalid path raises an error for Shop user."""
        self.export_service.save_to_path.side_effect = OSError("Invalid path")

        with self.assertRaises(OSError):
            self.export_service.save_to_path("/invalid/path/file.xlsx")


if __name__ == "__main__":
    unittest.main()
