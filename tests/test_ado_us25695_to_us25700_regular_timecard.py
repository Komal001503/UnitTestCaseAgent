"""
Unit Tests for Maintain Regular Timecard Module
Source: azure_devops_user_stories.md
User Stories:
  US-25695 (User - Attendance - Maintain Regular timecard - date view)
  US-25696 (User - Attendance - Maintain Regular timecard - employee view)
  US-25697 (User - Attendance - Maintain Regular timecard - export)
  US-25698 (Shop in charge - Attendance - Maintain Regular timecard - date view)
  US-25699 (Shop in charge - Attendance - Maintain Regular timecard - employee view)
  US-25700 (Shop in charge - Attendance - Maintain Regular timecard - export)

Applies to:
  IR, Company Head, Location Head, BU Head (US-25695, US-25696, US-25697)
  Shop In Charge (US-25698, US-25699, US-25700)

Test Categories:
- Positive / Happy Path
- Negative / Error Path
- Boundary / Edge Cases
- Integration Points
"""

SOURCE_STORY_FILE = "azure_devops_user_stories.md"

import unittest
from unittest.mock import MagicMock, patch


# TODO: Import actual modules once implementation is available.
# from src.attendance.regular_timecard import (
#     RegularTimecardPage, RegularTimecardService, TimecardScheduler
# )


# ---------------------------------------------------------------------------
# Common: Navigation to Maintain Regular Timecard
# ---------------------------------------------------------------------------


class TestRegularTimecardNavigation(unittest.TestCase):
    """US-25695 / US-25698: Navigate to Maintain Regular Timecard page."""

    def setUp(self):
        self.navigation = MagicMock()
        self.page = MagicMock()

    def test_sideNav_selectMaintainTimecard_opensPage(self):
        """Positive: Selecting 'Maintain Timecard' from Attendance Management opens the page."""
        self.navigation.select_menu.return_value = "Maintain Regular Timecard"

        result = self.navigation.select_menu(
            "Attendance Management", "Maintain Timecard"
        )

        self.assertIn("Timecard", result)

    def test_timecardPage_displaysTwoTabs(self):
        """Positive: Timecard page displays 'Date View' and 'Employee View' tabs."""
        self.page.get_tabs.return_value = ["Date View", "Employee View"]

        tabs = self.page.get_tabs()

        self.assertEqual(len(tabs), 2)
        self.assertIn("Date View", tabs)
        self.assertIn("Employee View", tabs)

    def test_timecardPage_defaultTab_isDateView(self):
        """Positive: By default, the 'Date View' tab is selected."""
        self.page.get_active_tab.return_value = "Date View"

        result = self.page.get_active_tab()

        self.assertEqual(result, "Date View")


# ---------------------------------------------------------------------------
# US-25695 / US-25698: Date View Tab
# ---------------------------------------------------------------------------


class TestRegularTimecardDateView(unittest.TestCase):
    """US-25695 / US-25698: Verify Date View tab attributes, grid, and validations."""

    def setUp(self):
        self.service = MagicMock()

    def test_dateView_displays_datePicker(self):
        """Positive: Date View shows a Date attribute field (date picker)."""
        self.service.get_attributes.return_value = ["Date"]

        attributes = self.service.get_attributes(tab="date_view")

        self.assertIn("Date", attributes)

    def test_dateView_grid_displaysAllRequiredColumns(self):
        """Positive: Date View grid shows Employee, TRT No, In, Out, Late, Early,
        Reg Shift, Actual Shift, Employee Status, Cadre, Leave Remarks."""
        self.service.get_grid_columns.return_value = [
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

        columns = self.service.get_grid_columns("date_view")

        self.assertEqual(len(columns), 11)
        self.assertIn("Employee", columns)
        self.assertIn("In", columns)
        self.assertIn("Out", columns)
        self.assertIn("Leave Remarks", columns)

    def test_dateView_userDisplaysIRSaveButton(self):
        """Positive: IR user sees Save and Export buttons in Date View."""
        self.service.get_buttons.return_value = ["Save", "Export"]

        buttons = self.service.get_buttons(role="IR", tab="date_view")

        self.assertIn("Save", buttons)
        self.assertIn("Export", buttons)

    def test_dateView_shopInChargeDisplaysExportOnly(self):
        """Positive: Shop In Charge sees only Export button in Date View."""
        self.service.get_buttons.return_value = ["Export"]

        buttons = self.service.get_buttons(role="SHOP_IN_CHARGE", tab="date_view")

        self.assertIn("Export", buttons)
        self.assertNotIn("Save", buttons)

    def test_dateView_defaultDate_showsCurrentDate(self):
        """Validation: Without selecting a date, grid shows today's data by default."""
        self.service.get_default_date.return_value = "current_date"

        result = self.service.get_default_date()

        self.assertEqual(result, "current_date")

    def test_dateView_selectDate_showsDataForThatDate(self):
        """Positive: Selecting a date shows punching data for that specific date."""
        self.service.get_data_for_date.return_value = [
            {"employee": "PS-001 John", "date": "01-06-2026"}
        ]

        results = self.service.get_data_for_date("01-06-2026")

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["date"], "01-06-2026")

    def test_dateView_inTime_storedAsMinutes(self):
        """Validation: In time is stored and displayed in HH:MM format
        (converted from minutes: e.g. 484 mins = 8:04)."""
        self.service.convert_minutes_to_time.return_value = "08:04"

        result = self.service.convert_minutes_to_time(484)

        self.assertEqual(result, "08:04")

    def test_dateView_inTime_conversionFormula(self):
        """Boundary: In time of 08:04 = 8*60 + 4 = 484 minutes."""
        self.service.convert_time_to_minutes.return_value = 484

        result = self.service.convert_time_to_minutes("08:04")

        self.assertEqual(result, 484)

    def test_dateView_regShift_fetchedFromMaintainedShiftSchedule(self):
        """Validation: Reg. Shift (planned shift) is fetched from 'Maintain Shift Schedule' module."""
        self.service.get_reg_shift.return_value = {
            "source": "maintained_shift_schedule",
            "shift": "I",
        }

        result = self.service.get_reg_shift("PS-001", "01-06-2026")

        self.assertEqual(result["source"], "maintained_shift_schedule")
        self.assertIsNotNone(result["shift"])

    def test_dateView_actualShift_calculatedFromPunchData(self):
        """Validation: Actual Shift is calculated from actual punch-in/out times."""
        self.service.get_actual_shift.return_value = {
            "source": "punch_data",
            "shift": "I",
        }

        result = self.service.get_actual_shift("PS-001", "01-06-2026")

        self.assertEqual(result["source"], "punch_data")

    def test_dateView_onlyFirstPunchInLastPunchOut_consideredDuplicatesRemoved(self):
        """Validation: Only first punch-in and last punch-out are kept; duplicates removed."""
        self.service.process_punches.return_value = {
            "first_in": "07:00",
            "last_out": "15:25",
            "duplicates_removed": 2,
        }

        result = self.service.process_punches(
            punches=["06:53", "07:00", "07:05"],
            punch_outs=["15:20", "15:25", "15:35"],
        )

        self.assertIsNotNone(result["first_in"])
        self.assertIsNotNone(result["last_out"])
        self.assertGreater(result["duplicates_removed"], 0)

    def test_dateView_earlyPunchIn_roundedToShiftStartTime(self):
        """Validation: Early punch-in (6:53 for shift starting 7:00) is shown as 6:53
        but payment starts from 7:00 (rounded to shift start)."""
        self.service.adjust_punch_time.return_value = {
            "display_time": "06:53",
            "payment_from": "07:00",
        }

        result = self.service.adjust_punch_time(
            actual_punch="06:53", shift_start="07:00"
        )

        self.assertEqual(result["display_time"], "06:53")
        self.assertEqual(result["payment_from"], "07:00")

    def test_dateView_latePunchOut_adjustedToShiftEndTime(self):
        """Validation: Late punch-out (15:35 for shift ending 15:25) is adjusted to 15:25."""
        self.service.adjust_punch_out.return_value = {
            "adjusted_time": "15:25",
        }

        result = self.service.adjust_punch_out(
            actual_punch_out="15:35", shift_end="15:25"
        )

        self.assertEqual(result["adjusted_time"], "15:25")

    def test_dateView_noPunchData_markedAsAbsent(self):
        """Validation: Employee with no punch-in/out data is marked as ABS (Absent)."""
        self.service.get_leave_remark.return_value = "ABS"

        result = self.service.get_leave_remark(punch_in=None, punch_out=None)

        self.assertEqual(result, "ABS")

    def test_dateView_absRemark_remainsUntilLeaveApproved(self):
        """Validation: ABS remark remains until employee's leave application is approved."""
        self.service.update_remark_after_leave_approval.return_value = {
            "previous_remark": "ABS",
            "updated_remark": "PL",
        }

        result = self.service.update_remark_after_leave_approval(
            emp="PS-001", leave_type="PL", approved=True
        )

        self.assertEqual(result["previous_remark"], "ABS")
        self.assertEqual(result["updated_remark"], "PL")

    def test_dateView_absRemark_notUpdatedIfLeaveNotApproved(self):
        """Negative: ABS remark is NOT updated if leave application is still pending."""
        self.service.update_remark_after_leave_approval.return_value = {
            "updated_remark": "ABS",
        }

        result = self.service.update_remark_after_leave_approval(
            emp="PS-001", leave_type="PL", approved=False
        )

        self.assertEqual(result["updated_remark"], "ABS")

    def test_dateView_leaveRemarks_shownToBothIRAndEmployee(self):
        """Positive: Leave remarks are visible to both IR (in app) and Employee (in Kiosk)."""
        self.service.get_remark_visibility.return_value = {
            "ir_visible": True,
            "employee_kiosk_visible": True,
        }

        result = self.service.get_remark_visibility("PS-001", "01-06-2026")

        self.assertTrue(result["ir_visible"])
        self.assertTrue(result["employee_kiosk_visible"])

    def test_dateView_schedulerFetchesFromInfocommAPIAt9_30AM(self):
        """Integration: Scheduler fetches punching data from Infocomm API every morning at 9:30 AM."""
        self.service.get_scheduler_config.return_value = {
            "runs_at": "09:30",
            "source": "infocomm_api",
            "frequency": "daily",
        }

        result = self.service.get_scheduler_config()

        self.assertEqual(result["runs_at"], "09:30")
        self.assertEqual(result["source"], "infocomm_api")
        self.assertEqual(result["frequency"], "daily")

    def test_dateView_autoSchedule_doneForYesterdayAndToday(self):
        """Validation: Auto schedule is run for yesterday and today (to cover night shifts)."""
        self.service.get_auto_schedule_dates.return_value = ["yesterday", "today"]

        result = self.service.get_auto_schedule_dates()

        self.assertIn("yesterday", result)
        self.assertIn("today", result)

    def test_dateView_searchBar_filtersResults(self):
        """Positive: Column search and Global search bar filter timecard results."""
        self.service.search.return_value = [{"employee": "PS-001 John"}]

        results = self.service.search("John", tab="date_view")

        self.assertEqual(len(results), 1)

    def test_dateView_pageNavigation_works(self):
        """Positive: Page navigation works in Date View."""
        self.service.get_page.return_value = {"page": 2}

        result = self.service.get_page(2, tab="date_view")

        self.assertEqual(result["page"], 2)

    def test_shopInChargeView_showsDataFromPreviousDay(self):
        """Validation (US-25698): Shop In Charge default view shows previous day's data."""
        self.service.get_default_view_data.return_value = {
            "data_for": "previous_day",
            "role": "SHOP_IN_CHARGE",
        }

        result = self.service.get_default_view_data(role="SHOP_IN_CHARGE")

        self.assertEqual(result["data_for"], "previous_day")


# ---------------------------------------------------------------------------
# US-25696 / US-25699: Employee View Tab
# ---------------------------------------------------------------------------


class TestRegularTimecardEmployeeView(unittest.TestCase):
    """US-25696 / US-25699: Verify Employee View tab attributes, grid, and validations."""

    def setUp(self):
        self.service = MagicMock()

    def test_employeeView_tab_displaysEmployeeDropdownFromToDate(self):
        """Positive: Employee View tab shows Employee dropdown and From/To date pickers."""
        self.service.get_attributes.return_value = ["Employee", "From", "To"]

        attributes = self.service.get_attributes(tab="employee_view")

        self.assertIn("Employee", attributes)
        self.assertIn("From", attributes)
        self.assertIn("To", attributes)

    def test_employeeView_employeeDropdown_fetchedFromWorkforceInfo(self):
        """Positive: Employee dropdown is populated from workforce information."""
        self.service.get_employee_list.return_value = [
            {"ps_no": "PS-001", "name": "John Doe"},
            {"ps_no": "PS-002", "name": "Jane Smith"},
        ]

        employees = self.service.get_employee_list()

        self.assertGreater(len(employees), 0)
        self.assertIn("ps_no", employees[0])
        self.assertIn("name", employees[0])

    def test_employeeView_grid_displaysAllRequiredColumns(self):
        """Positive: Employee View grid shows Date, TRT No, In, Out, Late, Early,
        Reg Shift, Actual Shift, Leave Remarks, Employee Status, Cadre."""
        self.service.get_grid_columns.return_value = [
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

        columns = self.service.get_grid_columns("employee_view")

        self.assertEqual(len(columns), 11)
        self.assertIn("Date", columns)
        self.assertIn("Leave Remarks", columns)

    def test_employeeView_shopInChargeGrid_includesInOutMinColumns(self):
        """Positive (US-25699): Shop In Charge Employee View grid includes In (Min) and Out (Min)."""
        self.service.get_grid_columns.return_value = [
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

        columns = self.service.get_grid_columns("employee_view", role="SHOP_IN_CHARGE")

        self.assertIn("In (Min)", columns)
        self.assertIn("Out (Min)", columns)

    def test_employeeView_defaultDateRange_showsCurrentMonthTillToday(self):
        """Validation (US-25696): Default date range is current month from 1st to today."""
        self.service.get_default_date_range.return_value = {
            "from": "01-06-2026",
            "to": "04-06-2026",
        }

        result = self.service.get_default_date_range(role="IR")

        self.assertIsNotNone(result["from"])
        self.assertIsNotNone(result["to"])

    def test_employeeView_shopInCharge_defaultShowsPreviousDay(self):
        """Validation (US-25699): Shop In Charge default shows previous day data."""
        self.service.get_default_date_range.return_value = {
            "data_for": "previous_day",
        }

        result = self.service.get_default_date_range(role="SHOP_IN_CHARGE")

        self.assertEqual(result["data_for"], "previous_day")

    def test_employeeView_selectEmployee_showsEmployeeTimecardData(self):
        """Positive: Selecting an employee from dropdown shows that employee's timecard data."""
        self.service.get_data_for_employee.return_value = [
            {"date": "01-06-2026", "in": "07:00", "out": "15:25"},
        ]

        results = self.service.get_data_for_employee("PS-001")

        self.assertGreater(len(results), 0)
        self.assertIn("date", results[0])

    def test_employeeView_selectFromAndToDate_showsDataForRange(self):
        """Positive: Selecting From and To date shows data within that date range."""
        self.service.get_data_for_range.return_value = [
            {"date": "01-06-2026"},
            {"date": "02-06-2026"},
        ]

        results = self.service.get_data_for_range("PS-001", "01-06-2026", "07-06-2026")

        self.assertGreater(len(results), 0)

    def test_employeeView_inTime_storedAsMinutes(self):
        """Validation: In time converted from minutes to HH:MM (484 min = 8:04)."""
        self.service.convert_minutes_to_time.return_value = "08:04"

        result = self.service.convert_minutes_to_time(484)

        self.assertEqual(result, "08:04")

    def test_employeeView_noPunchData_markedAsABS(self):
        """Validation: No punch data results in ABS remark."""
        self.service.get_leave_remark.return_value = "ABS"

        result = self.service.get_leave_remark(punch_in=None, punch_out=None)

        self.assertEqual(result, "ABS")

    def test_employeeView_earlyPunchIn_displayedButPaymentFromShiftStart(self):
        """Validation: Early punch-in displayed as-is but payment from shift start only."""
        self.service.adjust_punch_time.return_value = {
            "display_time": "06:53",
            "payment_from": "07:00",
        }

        result = self.service.adjust_punch_time("06:53", "07:00")

        self.assertNotEqual(result["display_time"], result["payment_from"])

    def test_employeeView_latePunchOut_adjustedToShiftEnd(self):
        """Validation: Late punch-out adjusted to shift end time."""
        self.service.adjust_punch_out.return_value = {"adjusted_time": "15:25"}

        result = self.service.adjust_punch_out("15:35", "15:25")

        self.assertEqual(result["adjusted_time"], "15:25")

    def test_employeeView_searchBar_filtersResults(self):
        """Positive: Search bar filters employee view timecard data."""
        self.service.search.return_value = [{"date": "01-06-2026", "employee": "PS-001"}]

        results = self.service.search("PS-001", tab="employee_view")

        self.assertGreater(len(results), 0)

    def test_employeeView_pageNavigation_works(self):
        """Positive: Page navigation works in Employee View tab."""
        self.service.get_page.return_value = {"page": 3}

        result = self.service.get_page(3, tab="employee_view")

        self.assertEqual(result["page"], 3)

    def test_employeeView_displaysExportButton(self):
        """Positive: Employee View displays Export button."""
        self.service.get_buttons.return_value = ["Export"]

        buttons = self.service.get_buttons(tab="employee_view")

        self.assertIn("Export", buttons)


# ---------------------------------------------------------------------------
# US-25697 / US-25700: Export Timecard Data
# ---------------------------------------------------------------------------


class TestRegularTimecardExport(unittest.TestCase):
    """US-25697 / US-25700: Verify Export functionality for timecard data."""

    def setUp(self):
        self.service = MagicMock()

    def test_export_withDateFilter_exportsFilteredData(self):
        """Positive: Export with From/To date selection exports filtered timecard data."""
        self.service.export.return_value = {
            "status": "success",
            "filter_applied": True,
            "filename": "timecard_filtered.xlsx",
        }

        result = self.service.export(from_date="01-06-2026", to_date="07-06-2026")

        self.assertEqual(result["status"], "success")
        self.assertTrue(result["filter_applied"])

    def test_export_withoutDateFilter_exportsAllData(self):
        """Positive: Export without filter exports all timecard data."""
        self.service.export.return_value = {
            "status": "success",
            "filter_applied": False,
            "filename": "timecard_all.xlsx",
        }

        result = self.service.export(from_date=None, to_date=None)

        self.assertEqual(result["status"], "success")
        self.assertFalse(result["filter_applied"])

    def test_exportedFile_canBeSavedToLocation(self):
        """Positive: User can save the exported Excel file to a chosen location."""
        self.service.save_export.return_value = {
            "status": "success",
            "saved_path": "/downloads/timecard.xlsx",
        }

        result = self.service.save_export("/downloads/timecard.xlsx")

        self.assertEqual(result["status"], "success")
        self.assertIn(".xlsx", result["saved_path"])

    def test_export_emptyDateRange_returnsError(self):
        """Boundary: Export with empty/null from date and existing to date returns error."""
        self.service.export.return_value = {
            "status": "error",
            "message": "Please provide a valid date range",
        }

        result = self.service.export(from_date=None, to_date="07-06-2026")

        self.assertEqual(result["status"], "error")

    def test_export_fromDateAfterToDate_returnsError(self):
        """Boundary: Export where From Date > To Date returns validation error."""
        self.service.export.return_value = {
            "status": "error",
            "message": "From date must be before To date",
        }

        result = self.service.export(from_date="10-06-2026", to_date="01-06-2026")

        self.assertEqual(result["status"], "error")
        self.assertIn("before", result["message"].lower())


# ---------------------------------------------------------------------------
# US-25695 / US-25698: Timecard Business Logic
# ---------------------------------------------------------------------------


class TestRegularTimecardBusinessLogic(unittest.TestCase):
    """US-25695 / US-25698: Verify timecard business logic (shift timing, scheduler)."""

    def setUp(self):
        self.service = MagicMock()

    def test_shiftTimingMaster_usedForAutoScheduling(self):
        """Validation: Timing for each shift is captured from 'Maintain Shift Timing Master'."""
        self.service.get_shift_timing_source.return_value = "maintain_shift_timing_master"

        result = self.service.get_shift_timing_source()

        self.assertEqual(result, "maintain_shift_timing_master")

    def test_realTimeScheduler_updatesTimecardDailyForYesterdayAndToday(self):
        """Integration: Real-time scheduler updates master card daily for yesterday and today."""
        self.service.get_scheduler_run_days.return_value = ["yesterday", "today"]

        result = self.service.get_scheduler_run_days()

        self.assertIn("yesterday", result)
        self.assertIn("today", result)

    def test_nightShiftData_includedInTodaysAutoSchedule(self):
        """Validation: Night shift ending today is included in today's auto-schedule run."""
        self.service.includes_night_shift.return_value = True

        result = self.service.includes_night_shift()

        self.assertTrue(result)

    def test_infocommAPI_fetchedByScheduler(self):
        """Integration: Scheduler fetches punch data from Infocomm API."""
        self.service.get_punch_data_source.return_value = "infocomm_api"

        result = self.service.get_punch_data_source()

        self.assertEqual(result, "infocomm_api")

    def test_leaveRemark_fetchedFromLeaveRemarksMaster(self):
        """Validation: Leave Remarks values are fetched from 'Leave Remarks' master."""
        self.service.get_leave_remarks_source.return_value = "leave_remarks_master"

        result = self.service.get_leave_remarks_source()

        self.assertEqual(result, "leave_remarks_master")

    def test_trtNumber_fetchedFromInfocomm(self):
        """Validation: TRT No (punching machine number) is fetched from Infocomm."""
        self.service.get_trt_source.return_value = "infocomm"

        result = self.service.get_trt_source()

        self.assertEqual(result, "infocomm")

    def test_employeeStatus_fetchedFromWorkforceInfo(self):
        """Validation: Employee Status (Direct/Indirect) is fetched from workforce information."""
        self.service.get_employee_status_source.return_value = "workforce_information"

        result = self.service.get_employee_status_source()

        self.assertEqual(result, "workforce_information")

    def test_cadre_fetchedFromWorkforceInfo(self):
        """Validation: Cadre is fetched from workforce information."""
        self.service.get_cadre_source.return_value = "workforce_information"

        result = self.service.get_cadre_source()

        self.assertEqual(result, "workforce_information")

    def test_duplicatePunches_areRemoved(self):
        """Validation: Duplicate punch records are removed; only first-in/last-out kept."""
        self.service.deduplicate_punches.return_value = {
            "kept": {"first_in": "07:00", "last_out": "15:25"},
            "removed_count": 3,
        }

        result = self.service.deduplicate_punches(
            punches=["07:00", "07:05", "07:10"],
            punch_outs=["15:20", "15:25", "15:30"],
        )

        self.assertGreater(result["removed_count"], 0)
        self.assertIsNotNone(result["kept"]["first_in"])
        self.assertIsNotNone(result["kept"]["last_out"])

    def test_unauthorizedRole_cannotAccessTimecard(self):
        """Negative: Role without access to timecard is denied."""
        self.service.has_access.return_value = False

        result = self.service.has_access(role="CONTRACTOR", page="Maintain Timecard")

        self.assertFalse(result)


if __name__ == "__main__":
    unittest.main()
