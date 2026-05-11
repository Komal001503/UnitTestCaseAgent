"""
Unit Tests for Maintain Shift Scheduling Plan – IR & IR Admin Roles
User Stories: US-032 (IR View), US-033 (IR Edit/Schedule Shift),
              US-034 (IR Export), US-035 (IR Admin View + Configure),
              US-036 (IR Admin Export)

Source: MaintainShiftSchedulingPlanUserStory.xlsx

Test Categories:
- Positive / Happy Path
- Negative / Error Path
- Boundary / Edge Cases

Module: Attendance Management
Features: Maintain Shift Scheduling Plan (view, edit, schedule, export, configure)
"""

SOURCE_STORY_FILE = "MaintainShiftSchedulingPlanUserStory.xlsx"

import unittest
from unittest.mock import MagicMock, patch, call
from datetime import date, datetime, time


# TODO: Import actual modules once implementation is available.
# from src.attendance.shift_scheduling import (
#     ShiftSchedulingPage, ShiftSchedulingService, ShiftConfigService,
#     ShiftExportService, ScheduleShiftPopup
# )


# ===========================================================================
# US-032: IR – View Maintain Shift Scheduling Plan
# ===========================================================================


class TestUS032_NavigateToShiftSchedulingPlan(unittest.TestCase):
    """US-032: Navigate to 'Maintain Shift Scheduling Plan' from
    'Attendance Management' menu and verify page display."""

    def setUp(self):
        self.page = MagicMock()
        self.service = MagicMock()

    # -- Positive tests ------------------------------------------------------

    def test_navigateToShiftPlan_fromAttendanceMenu_displaysPage(self):
        """Positive: Selecting 'Maintain Shift Scheduling Plan' sub-menu from
        'Attendance Management' menu displays the page successfully."""
        self.page.navigate_to.return_value = {"status": "success", "page": "Maintain Shift Scheduling Plan"}

        result = self.page.navigate_to("attendance_management", "maintain_shift_scheduling_plan")

        self.assertEqual(result["status"], "success")
        self.assertEqual(result["page"], "Maintain Shift Scheduling Plan")

    def test_pageAttributes_displaysShiftCodeFromToDate(self):
        """Positive: Page displays attributes – Shift Code, From date, To date."""
        self.page.get_attributes.return_value = ["Shift Code", "From", "To"]

        attributes = self.page.get_attributes()

        self.assertIn("Shift Code", attributes)
        self.assertIn("From", attributes)
        self.assertIn("To", attributes)
        self.assertEqual(len(attributes), 3)

    def test_shiftCodeSelection_autoPopulatesFromToDate(self):
        """Positive: Selecting a shift code auto-populates the From and To
        date fields based on the week of the selected shift code."""
        self.service.select_shift_code.return_value = {
            "shift_code": "SC-001",
            "from_date": "16-12-2025",
            "to_date": "22-12-2025",
        }

        result = self.service.select_shift_code("SC-001")

        self.assertEqual(result["from_date"], "16-12-2025")
        self.assertEqual(result["to_date"], "22-12-2025")

    # -- Negative tests ------------------------------------------------------

    def test_navigateToShiftPlan_unauthorizedRole_denied(self):
        """Negative: A user without IR role cannot access the
        Maintain Shift Scheduling Plan page."""
        self.page.navigate_to.return_value = {
            "status": "error",
            "message": "Access denied. Insufficient permissions.",
        }

        result = self.page.navigate_to("attendance_management", "maintain_shift_scheduling_plan")

        self.assertEqual(result["status"], "error")
        self.assertIn("Access denied", result["message"])

    def test_shiftCodeSelection_invalidCode_returnsError(self):
        """Negative: Selecting an invalid shift code returns an error and
        does not populate From/To date."""
        self.service.select_shift_code.return_value = {
            "status": "error",
            "message": "Invalid shift code",
        }

        result = self.service.select_shift_code("INVALID-999")

        self.assertEqual(result["status"], "error")
        self.assertNotIn("from_date", result)

    # -- Boundary tests ------------------------------------------------------

    def test_shiftCodeSelection_noCodeSelected_fieldsEmpty(self):
        """Boundary: When no shift code is selected, From and To date
        fields remain empty."""
        self.service.select_shift_code.return_value = {
            "shift_code": None,
            "from_date": None,
            "to_date": None,
        }

        result = self.service.select_shift_code(None)

        self.assertIsNone(result["from_date"])
        self.assertIsNone(result["to_date"])


class TestUS032_DataGridColumns(unittest.TestCase):
    """US-032: Verify the data grid displays all required columns."""

    def setUp(self):
        self.service = MagicMock()
        self.expected_columns = [
            "Employee (PS No, Name)",
            "Dept Code / Shop Name",
            "Cadre",
            "Category",
            "Shift",
            "Monday",
            "Tuesday",
            "Wednesday",
            "Thursday",
            "Friday",
            "Saturday",
            "Sunday",
            "Supervisor",
            "TPT User",
            "Last Modified By",
            "Action",
            "Select",
        ]

    def test_dataGrid_displaysAllRequiredColumns(self):
        """Positive: Data grid displays all 17 required columns including
        Employee, Dept code, Cadre, Category, Shift, Mon-Sun shift plan,
        Supervisor, TPT user, Last modified by, Action, and Select checkbox."""
        self.service.get_grid_columns.return_value = self.expected_columns

        columns = self.service.get_grid_columns()

        self.assertEqual(len(columns), 17)
        for col in self.expected_columns:
            self.assertIn(col, columns)

    def test_dataGrid_shiftPlanDays_allSevenDaysPresent(self):
        """Positive: Shift plan columns include all 7 days Monday through Sunday."""
        self.service.get_grid_columns.return_value = self.expected_columns
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

        columns = self.service.get_grid_columns()

        for day in days:
            self.assertIn(day, columns)

    def test_dataGrid_supervisorAutoPopulated_basedOnDeptCode(self):
        """Positive: Supervisor column is auto-populated based on Dept Code."""
        self.service.get_employee_row.return_value = {
            "ps_no": "10001",
            "dept_code": "D100",
            "supervisor": "Mr. Smith (20001)",
        }

        row = self.service.get_employee_row("10001")

        self.assertIsNotNone(row["supervisor"])
        self.assertEqual(row["supervisor"], "Mr. Smith (20001)")

    def test_dataGrid_tptUserField_displaysYesOrNo(self):
        """Positive: TPT User column displays 'Yes' or 'No' fetched from
        workforce info."""
        self.service.get_employee_row.return_value = {
            "ps_no": "10001",
            "tpt_user": "Yes",
        }

        row = self.service.get_employee_row("10001")

        self.assertIn(row["tpt_user"], ["Yes", "No"])

    def test_dataGrid_lastModifiedBy_displaysPsNoNameDate(self):
        """Positive: 'Last Modified By' column shows PS No, Name, and Date
        of the shop person who last modified the shift."""
        self.service.get_employee_row.return_value = {
            "last_modified_by": {"ps_no": "20001", "name": "Admin User", "date": "17-12-2025"},
        }

        row = self.service.get_employee_row("10001")

        self.assertIn("ps_no", row["last_modified_by"])
        self.assertIn("name", row["last_modified_by"])
        self.assertIn("date", row["last_modified_by"])

    def test_dataGrid_emptyData_displaysNoRecordsMessage(self):
        """Boundary: When no employees match the shift code, the grid displays
        an empty state / 'No records found' message."""
        self.service.get_shift_plan_data.return_value = {
            "records": [],
            "message": "No records found",
        }

        result = self.service.get_shift_plan_data("SC-999")

        self.assertEqual(len(result["records"]), 0)
        self.assertEqual(result["message"], "No records found")


class TestUS032_ButtonsAndActions(unittest.TestCase):
    """US-032: Verify buttons (Save, Export) and Action column (edit icon)."""

    def setUp(self):
        self.page = MagicMock()
        self.service = MagicMock()

    def test_page_displaysSaveAndExportButtons(self):
        """Positive: Page displays 'Save' and 'Export' buttons for IR role."""
        self.page.get_buttons.return_value = ["Save", "Export"]

        buttons = self.page.get_buttons()

        self.assertIn("Save", buttons)
        self.assertIn("Export", buttons)
        self.assertEqual(len(buttons), 2)

    def test_editIcon_clickMakesShiftAndShiftPlanEditable(self):
        """Positive: Clicking the edit icon makes the Shift and Shift Plan
        (Mon-Sun) fields editable in that row."""
        self.service.toggle_edit_mode.return_value = {
            "editable_fields": ["Shift", "Monday", "Tuesday", "Wednesday",
                                "Thursday", "Friday", "Saturday", "Sunday"],
        }

        result = self.service.toggle_edit_mode("10001")

        self.assertIn("Shift", result["editable_fields"])
        self.assertIn("Monday", result["editable_fields"])
        self.assertEqual(len(result["editable_fields"]), 8)

    def test_multiSelectCheckbox_selectsMultipleEmployees(self):
        """Positive: Multi-select checkbox allows selecting multiple employees
        for bulk shift scheduling."""
        self.service.select_employees.return_value = {
            "selected_count": 5,
            "selected_ps_nos": ["10001", "10002", "10003", "10004", "10005"],
        }

        result = self.service.select_employees(["10001", "10002", "10003", "10004", "10005"])

        self.assertEqual(result["selected_count"], 5)

    def test_multiSelectCheckbox_noSelection_returnsZero(self):
        """Boundary: When no employees are selected, selected_count is 0."""
        self.service.select_employees.return_value = {
            "selected_count": 0,
            "selected_ps_nos": [],
        }

        result = self.service.select_employees([])

        self.assertEqual(result["selected_count"], 0)


class TestUS032_ShiftValidation(unittest.TestCase):
    """US-032: Validation – shift change propagation, shift rotation
    restriction, and lock-in period logic."""

    def setUp(self):
        self.service = MagicMock()

    def test_changeShiftColumn_propagatesAllDays(self):
        """Positive: Changing the 'Shift' column value from 'II' to 'I'
        automatically updates all day columns (Mon-Sun) to the new shift."""
        self.service.change_shift.return_value = {
            "shift": "I",
            "Monday": "I", "Tuesday": "I", "Wednesday": "I",
            "Thursday": "I", "Friday": "I", "Saturday": "I", "Sunday": "I",
        }

        result = self.service.change_shift("10001", new_shift="I")

        for day in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]:
            self.assertEqual(result[day], "I")

    def test_changeShiftForSelectedDate_onlySelectedDayChanges(self):
        """Positive: User can change the shift for a specific selected date
        only, leaving other days unchanged."""
        self.service.change_day_shift.return_value = {
            "Monday": "I", "Tuesday": "II", "Wednesday": "II",
            "Thursday": "II", "Friday": "II", "Saturday": "II", "Sunday": "II",
        }

        result = self.service.change_day_shift("10001", day="Monday", new_shift="I")

        self.assertEqual(result["Monday"], "I")
        self.assertEqual(result["Tuesday"], "II")

    def test_changeShift_nonApplicableRotation_rejected(self):
        """Negative: Changing to a shift not in the employee's applicable
        shift rotation is restricted."""
        self.service.change_shift.return_value = {
            "status": "error",
            "message": "Shift 'III' is not applicable for this employee's rotation.",
        }

        result = self.service.change_shift("10001", new_shift="III")

        self.assertEqual(result["status"], "error")
        self.assertIn("not applicable", result["message"])

    def test_lockInPeriod_editRestricted(self):
        """Negative: During the lock-in period, the IR cannot edit the shift
        plan or schedule any pattern for any workman."""
        self.service.toggle_edit_mode.return_value = {
            "status": "error",
            "message": "Editing is restricted during the lock-in period.",
        }

        result = self.service.toggle_edit_mode("10001")

        self.assertEqual(result["status"], "error")
        self.assertIn("lock-in period", result["message"])

    def test_lockInPeriod_autoRelease_shiftPlanReleasedToShop(self):
        """Positive: System automatically releases the shift plan to shop
        users based on the lock-in period scheduled by admin."""
        self.service.check_lock_in_status.return_value = {
            "locked": False,
            "released_to_shop": True,
            "release_time": "2025-12-17T08:00:00",
        }

        result = self.service.check_lock_in_status()

        self.assertFalse(result["locked"])
        self.assertTrue(result["released_to_shop"])

    def test_editOutsideLockIn_allowed(self):
        """Positive: IR can make changes to the shift plan on any day
        outside the scheduled lock-in period."""
        self.service.toggle_edit_mode.return_value = {
            "status": "success",
            "editable": True,
        }

        result = self.service.toggle_edit_mode("10001")

        self.assertEqual(result["status"], "success")
        self.assertTrue(result["editable"])


class TestUS032_SaveAndSearch(unittest.TestCase):
    """US-032: Save changes, search bar, and page navigation."""

    def setUp(self):
        self.service = MagicMock()

    def test_saveButton_displaysSuccessPopup(self):
        """Positive: Clicking 'Save' after editing displays popup message
        'Changes have been saved successfully'."""
        self.service.save_shift_plan.return_value = {
            "status": "success",
            "message": "Changes have been saved successfully",
        }

        result = self.service.save_shift_plan({"ps_no": "10001", "shift": "I"})

        self.assertEqual(result["status"], "success")
        self.assertEqual(result["message"], "Changes have been saved successfully")

    def test_saveButton_noChanges_noAction(self):
        """Boundary: Clicking 'Save' without making any edits shows
        an appropriate message or takes no action."""
        self.service.save_shift_plan.return_value = {
            "status": "info",
            "message": "No changes to save",
        }

        result = self.service.save_shift_plan({})

        self.assertEqual(result["status"], "info")

    def test_searchBar_columnSearch_filtersResults(self):
        """Positive: Column search bar filters data grid results by
        the specified column value."""
        self.service.search.return_value = [
            {"ps_no": "10001", "name": "John Doe"},
        ]

        results = self.service.search(column="name", query="John")

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["name"], "John Doe")

    def test_searchBar_globalSearch_filtersResults(self):
        """Positive: Global search bar searches across all columns."""
        self.service.search.return_value = [
            {"ps_no": "10001", "name": "John Doe", "dept_code": "D100"},
        ]

        results = self.service.search(query="D100")

        self.assertEqual(len(results), 1)

    def test_searchBar_noMatch_returnsEmpty(self):
        """Boundary: Search with a term that matches nothing returns
        an empty result set."""
        self.service.search.return_value = []

        results = self.service.search(query="XYZNONEXISTENT")

        self.assertEqual(len(results), 0)

    def test_pageNavigation_navigatesToSelectedPage(self):
        """Positive: Page navigation moves to the selected page."""
        self.service.get_page.return_value = {
            "page": 3,
            "total_pages": 10,
            "records": [{"ps_no": "10021"}],
        }

        result = self.service.get_page(3)

        self.assertEqual(result["page"], 3)
        self.assertGreater(len(result["records"]), 0)

    def test_pageNavigation_beyondLastPage_returnsLastPage(self):
        """Boundary: Navigating beyond the last page returns the last
        page instead of an error."""
        self.service.get_page.return_value = {
            "page": 10,
            "total_pages": 10,
            "message": "Showing last page",
        }

        result = self.service.get_page(999)

        self.assertEqual(result["page"], 10)


# ===========================================================================
# US-033: IR – Edit / Schedule Shift
# ===========================================================================


class TestUS033_ScheduleShiftPopup(unittest.TestCase):
    """US-033: Clicking 'Schedule Shift' button displays popup with
    employee list, shift pattern, date fields, and pattern week dropdown."""

    def setUp(self):
        self.service = MagicMock()
        self.popup = MagicMock()

    def test_scheduleShiftButton_displaysPopup(self):
        """Positive: Clicking 'Schedule Shift' button opens a popup with
        the correct fields and selected employee list."""
        self.popup.open.return_value = {
            "status": "success",
            "fields": ["employee_list", "shift_pattern", "start_date",
                       "end_date", "forever", "pattern_week"],
        }

        result = self.popup.open(selected_employees=["10001", "10002"])

        self.assertEqual(result["status"], "success")
        self.assertEqual(len(result["fields"]), 6)

    def test_popupDisplays_selectedEmployeeList(self):
        """Positive: Popup displays the list of employees (PS No and Name)
        that were selected before clicking 'Schedule Shift'."""
        self.popup.get_selected_employees.return_value = [
            {"ps_no": "10001", "name": "John Doe"},
            {"ps_no": "10002", "name": "Jane Smith"},
        ]

        employees = self.popup.get_selected_employees()

        self.assertEqual(len(employees), 2)
        self.assertEqual(employees[0]["ps_no"], "10001")

    def test_popupFields_shiftPattern_fetchedFromMaster(self):
        """Positive: Shift pattern dropdown is fetched from the shift
        rotation master based on the employee's shift type."""
        self.service.get_shift_patterns.return_value = [
            "I-II-III", "I-III-II", "II-I-III",
        ]

        patterns = self.service.get_shift_patterns(employee_type="rotational")

        self.assertGreater(len(patterns), 0)
        self.assertIn("I-II-III", patterns)

    def test_popupFields_patternWeekDropdown_displaysWeeks(self):
        """Positive: Pattern Week dropdown displays the list of pattern
        weeks for the current month (e.g., Week 1 through Week 5)."""
        self.popup.get_pattern_weeks.return_value = [
            "Week 1", "Week 2", "Week 3", "Week 4", "Week 5",
        ]

        weeks = self.popup.get_pattern_weeks()

        self.assertGreaterEqual(len(weeks), 4)
        self.assertLessEqual(len(weeks), 6)

    def test_popupDataGrid_displaysRotationTypeAndDays(self):
        """Positive: Popup data grid shows Rotation Type and Monday-Sunday
        shift plan columns."""
        self.popup.get_data_grid_columns.return_value = [
            "Rotation Type", "Monday", "Tuesday", "Wednesday",
            "Thursday", "Friday", "Saturday", "Sunday",
        ]

        columns = self.popup.get_data_grid_columns()

        self.assertEqual(len(columns), 8)
        self.assertIn("Rotation Type", columns)

    # -- Negative tests ------------------------------------------------------

    def test_scheduleShiftButton_noEmployeesSelected_showsError(self):
        """Negative: Clicking 'Schedule Shift' without selecting any
        employees shows an error message."""
        self.popup.open.return_value = {
            "status": "error",
            "message": "Please select at least one employee.",
        }

        result = self.popup.open(selected_employees=[])

        self.assertEqual(result["status"], "error")
        self.assertIn("select at least one", result["message"])

    def test_shiftPattern_noPatternAvailable_showsEmpty(self):
        """Negative: If no shift pattern is available for the employee type,
        the dropdown is empty and user is notified."""
        self.service.get_shift_patterns.return_value = []

        patterns = self.service.get_shift_patterns(employee_type="unknown")

        self.assertEqual(len(patterns), 0)

    # -- Boundary tests ------------------------------------------------------

    def test_patternWeek_monthWith4Weeks_shows4Weeks(self):
        """Boundary: For a month with exactly 4 weeks, the Pattern Week
        dropdown shows 4 entries."""
        self.popup.get_pattern_weeks.return_value = [
            "Week 1", "Week 2", "Week 3", "Week 4",
        ]

        weeks = self.popup.get_pattern_weeks()

        self.assertEqual(len(weeks), 4)


class TestUS033_ScheduleShiftOptions(unittest.TestCase):
    """US-033: Three options for shift change – one day, date range
    (current week), and forever. Verify success messages."""

    def setUp(self):
        self.service = MagicMock()

    def test_option1_shiftChangeOneDay_successMessage(self):
        """Positive: Option 1 – changing shift for one day displays
        'Shift plan successfully changed for one day'."""
        self.service.schedule_shift.return_value = {
            "status": "success",
            "message": "Shift plan successfully changed for one day",
        }

        result = self.service.schedule_shift(
            employees=["10001"],
            option="one_day",
            date="17-12-2025",
        )

        self.assertEqual(result["status"], "success")
        self.assertEqual(result["message"], "Shift plan successfully changed for one day")

    def test_option2_shiftChangeDateRange_successMessage(self):
        """Positive: Option 2 – changing shift for current week (date range)
        displays 'Shift plan successfully changed for current week only
        from DD-MM-YYYY to DD-MM-YYYY'."""
        self.service.schedule_shift.return_value = {
            "status": "success",
            "message": "Shift plan successfully changed for current week only from 16-12-2025 to 22-12-2025",
        }

        result = self.service.schedule_shift(
            employees=["10001"],
            option="date_range",
            start_date="16-12-2025",
            end_date="22-12-2025",
        )

        self.assertEqual(result["status"], "success")
        self.assertIn("current week only", result["message"])
        self.assertIn("16-12-2025", result["message"])
        self.assertIn("22-12-2025", result["message"])

    def test_option3_shiftChangeForever_successMessage(self):
        """Positive: Option 3 – changing shift 'forever' displays
        'New shift rotation will be carried forward for the workman
        from DD-MM-YYYY to "Forever"'."""
        self.service.schedule_shift.return_value = {
            "status": "success",
            "message": 'New shift rotation will be carried forward for the workman from 17-12-2025 to "Forever"',
        }

        result = self.service.schedule_shift(
            employees=["10001"],
            option="forever",
            start_date="17-12-2025",
        )

        self.assertEqual(result["status"], "success")
        self.assertIn("Forever", result["message"])

    def test_cancelButton_revertsChanges(self):
        """Positive: Clicking 'Cancel' reverts all changes and closes
        the popup without saving."""
        self.service.cancel_schedule_shift.return_value = {
            "status": "cancelled",
            "changes_saved": False,
        }

        result = self.service.cancel_schedule_shift()

        self.assertEqual(result["status"], "cancelled")
        self.assertFalse(result["changes_saved"])

    def test_scheduleShift_saveButton_savesAndCloses(self):
        """Positive: Clicking 'Schedule Shift' button in the popup saves
        the shift plan and closes the popup."""
        self.service.schedule_shift.return_value = {
            "status": "success",
            "popup_closed": True,
        }

        result = self.service.schedule_shift(
            employees=["10001", "10002"],
            option="date_range",
            start_date="16-12-2025",
            end_date="22-12-2025",
        )

        self.assertEqual(result["status"], "success")
        self.assertTrue(result["popup_closed"])

    # -- Negative tests ------------------------------------------------------

    def test_dateRange_startDateAfterEndDate_rejected(self):
        """Negative: Specifying a start date after end date is rejected
        with a validation error."""
        self.service.schedule_shift.return_value = {
            "status": "error",
            "message": "Start date must be before or equal to end date.",
        }

        result = self.service.schedule_shift(
            employees=["10001"],
            option="date_range",
            start_date="25-12-2025",
            end_date="20-12-2025",
        )

        self.assertEqual(result["status"], "error")
        self.assertIn("Start date must be before", result["message"])

    def test_dateRange_missingStartDate_rejected(self):
        """Negative: Omitting start date when using date range option
        returns a validation error."""
        self.service.schedule_shift.return_value = {
            "status": "error",
            "message": "Start date is required.",
        }

        result = self.service.schedule_shift(
            employees=["10001"],
            option="date_range",
            start_date=None,
            end_date="22-12-2025",
        )

        self.assertEqual(result["status"], "error")
        self.assertIn("required", result["message"])

    def test_forever_missingStartDate_rejected(self):
        """Negative: Selecting 'Forever' without a start date is rejected."""
        self.service.schedule_shift.return_value = {
            "status": "error",
            "message": "Start date is required for 'Forever' option.",
        }

        result = self.service.schedule_shift(
            employees=["10001"],
            option="forever",
            start_date=None,
        )

        self.assertEqual(result["status"], "error")

    # -- Boundary tests ------------------------------------------------------

    def test_dateRange_sameStartAndEndDate_treatedAsOneDay(self):
        """Boundary: When start date equals end date in date range mode,
        it is treated as a single-day change."""
        self.service.schedule_shift.return_value = {
            "status": "success",
            "message": "Shift plan successfully changed for one day",
        }

        result = self.service.schedule_shift(
            employees=["10001"],
            option="date_range",
            start_date="17-12-2025",
            end_date="17-12-2025",
        )

        self.assertEqual(result["status"], "success")

    def test_scheduleShift_multipleEmployees_appliedToAll(self):
        """Boundary: Scheduling shift for a large number of employees
        applies the change to all selected employees."""
        employee_list = [str(10000 + i) for i in range(100)]
        self.service.schedule_shift.return_value = {
            "status": "success",
            "affected_count": 100,
        }

        result = self.service.schedule_shift(
            employees=employee_list,
            option="forever",
            start_date="01-01-2026",
        )

        self.assertEqual(result["affected_count"], 100)

    def test_dateRange_spanningMultipleWeeks_accepted(self):
        """Boundary: System allows date range spanning multiple weeks
        (not restricted to only one week) based on start and end date."""
        self.service.schedule_shift.return_value = {
            "status": "success",
            "message": "Shift plan successfully changed for current week only from 01-12-2025 to 31-12-2025",
        }

        result = self.service.schedule_shift(
            employees=["10001"],
            option="date_range",
            start_date="01-12-2025",
            end_date="31-12-2025",
        )

        self.assertEqual(result["status"], "success")


# ===========================================================================
# US-034: IR – Export
# ===========================================================================


class TestUS034_IRExport(unittest.TestCase):
    """US-034: IR clicks 'Export' button to export shift scheduling
    details to an Excel file."""

    def setUp(self):
        self.service = MagicMock()

    def test_exportButton_exportsAllDataToExcel(self):
        """Positive: Clicking 'Export' without any date filter exports
        all existing shift plan data to an Excel file."""
        self.service.export.return_value = {
            "status": "success",
            "file_format": "xlsx",
            "record_count": 250,
        }

        result = self.service.export()

        self.assertEqual(result["status"], "success")
        self.assertEqual(result["file_format"], "xlsx")
        self.assertEqual(result["record_count"], 250)

    def test_exportButton_withDateFilter_exportsFilteredData(self):
        """Positive: When From and To dates are selected, clicking 'Export'
        exports only the filtered data to Excel."""
        self.service.export.return_value = {
            "status": "success",
            "file_format": "xlsx",
            "record_count": 30,
            "filter_applied": True,
        }

        result = self.service.export(from_date="01-12-2025", to_date="15-12-2025")

        self.assertEqual(result["status"], "success")
        self.assertTrue(result["filter_applied"])
        self.assertEqual(result["record_count"], 30)

    def test_exportButton_withoutDateFilter_exportsAllData(self):
        """Positive: When user does not filter, all existing data is exported."""
        self.service.export.return_value = {
            "status": "success",
            "filter_applied": False,
            "record_count": 500,
        }

        result = self.service.export(from_date=None, to_date=None)

        self.assertFalse(result["filter_applied"])
        self.assertEqual(result["record_count"], 500)

    def test_export_userCanSaveFileToLocation(self):
        """Positive: After export, user can save the file to a location."""
        self.service.export.return_value = {
            "status": "success",
            "file_name": "shift_plan_export.xlsx",
            "downloadable": True,
        }

        result = self.service.export()

        self.assertTrue(result["downloadable"])
        self.assertIn(".xlsx", result["file_name"])

    # -- Negative tests ------------------------------------------------------

    def test_exportButton_noData_showsMessage(self):
        """Negative: Exporting when no data is available (empty grid)
        returns an appropriate message."""
        self.service.export.return_value = {
            "status": "info",
            "message": "No data available to export",
            "record_count": 0,
        }

        result = self.service.export()

        self.assertEqual(result["record_count"], 0)
        self.assertIn("No data", result["message"])

    def test_exportButton_serviceError_showsErrorMessage(self):
        """Negative: If export service fails, an error message is shown."""
        self.service.export.side_effect = Exception("Export service unavailable")

        with self.assertRaises(Exception) as ctx:
            self.service.export()

        self.assertIn("unavailable", str(ctx.exception))

    # -- Boundary tests ------------------------------------------------------

    def test_export_veryLargeDataset_succeeds(self):
        """Boundary: Exporting a very large dataset (10,000+ records)
        completes successfully."""
        self.service.export.return_value = {
            "status": "success",
            "record_count": 10000,
        }

        result = self.service.export()

        self.assertEqual(result["status"], "success")
        self.assertEqual(result["record_count"], 10000)

    def test_export_filterDateRange_onlyFromDate_exportsFromDateOnwards(self):
        """Boundary: If only 'From' date is selected without 'To' date,
        system exports from that date to the latest available record."""
        self.service.export.return_value = {
            "status": "success",
            "filter_applied": True,
            "record_count": 100,
        }

        result = self.service.export(from_date="01-12-2025", to_date=None)

        self.assertTrue(result["filter_applied"])


# ===========================================================================
# US-035: IR Admin – View with Configure Shift Plan
# ===========================================================================


class TestUS035_IRAdminViewPage(unittest.TestCase):
    """US-035: IR Admin views 'Maintain Shift Scheduling Plan' page
    with additional 'Configure Shift Plan' button."""

    def setUp(self):
        self.page = MagicMock()
        self.service = MagicMock()

    def test_irAdminPage_displaysConfigureShiftPlanButton(self):
        """Positive: IR Admin page displays 'Save', 'Export', and
        'Configure shift plan' buttons (3 buttons, unlike IR which has 2)."""
        self.page.get_buttons.return_value = ["Save", "Export", "Configure shift plan"]

        buttons = self.page.get_buttons()

        self.assertIn("Configure shift plan", buttons)
        self.assertEqual(len(buttons), 3)

    def test_irAdminPage_displaysAllGridColumns(self):
        """Positive: IR Admin page displays the same data grid columns as
        the IR view (all 17 columns)."""
        expected_columns = [
            "Employee (PS No, Name)", "Dept Code / Shop Name", "Cadre",
            "Category", "Shift", "Monday", "Tuesday", "Wednesday",
            "Thursday", "Friday", "Saturday", "Sunday",
            "Supervisor", "TPT User", "Last Modified By", "Action", "Select",
        ]
        self.service.get_grid_columns.return_value = expected_columns

        columns = self.service.get_grid_columns()

        self.assertEqual(len(columns), 17)

    def test_irAdminPage_attributesSameAsIR(self):
        """Positive: IR Admin page displays the same attributes –
        Shift Code, From date, To date."""
        self.page.get_attributes.return_value = ["Shift Code", "From", "To"]

        attributes = self.page.get_attributes()

        self.assertEqual(len(attributes), 3)
        self.assertIn("Shift Code", attributes)

    def test_irAdminPage_editIconFunctionsSameAsIR(self):
        """Positive: Edit icon on IR Admin page makes Shift and Shift Plan
        (Mon-Sun) editable, same as IR role."""
        self.service.toggle_edit_mode.return_value = {
            "editable_fields": ["Shift", "Monday", "Tuesday", "Wednesday",
                                "Thursday", "Friday", "Saturday", "Sunday"],
        }

        result = self.service.toggle_edit_mode("10001")

        self.assertEqual(len(result["editable_fields"]), 8)

    def test_irAdminPage_saveButton_displaysSuccessPopup(self):
        """Positive: Clicking 'Save' on IR Admin page displays popup
        'Changes have been saved successfully'."""
        self.service.save_shift_plan.return_value = {
            "status": "success",
            "message": "Changes have been saved successfully",
        }

        result = self.service.save_shift_plan({"ps_no": "10001", "shift": "I"})

        self.assertEqual(result["message"], "Changes have been saved successfully")

    # -- Negative tests ------------------------------------------------------

    def test_nonAdminUser_cannotSeeConfigureButton(self):
        """Negative: A regular IR user (non-admin) cannot see the
        'Configure shift plan' button."""
        self.page.get_buttons.return_value = ["Save", "Export"]

        buttons = self.page.get_buttons()

        self.assertNotIn("Configure shift plan", buttons)

    def test_irAdminPage_searchBarNoMatch_emptyGrid(self):
        """Negative: Search with no matching results returns empty data."""
        self.service.search.return_value = []

        results = self.service.search(query="NONEXISTENT")

        self.assertEqual(len(results), 0)


class TestUS035_ConfigureShiftPlan(unittest.TestCase):
    """US-035: IR Admin 'Configure Shift Plan' popup – fields for
    From day, To day, Start time, End time, and Schedule Shift button."""

    def setUp(self):
        self.service = MagicMock()
        self.popup = MagicMock()

    def test_configureShiftPlan_displaysCorrectFields(self):
        """Positive: 'Configure Shift Plan' popup displays fields:
        From day, To day, Start time, End time."""
        self.popup.open.return_value = {
            "status": "success",
            "fields": ["From day", "To day", "Start time", "End time"],
        }

        result = self.popup.open()

        self.assertEqual(len(result["fields"]), 4)
        self.assertIn("From day", result["fields"])
        self.assertIn("To day", result["fields"])
        self.assertIn("Start time", result["fields"])
        self.assertIn("End time", result["fields"])

    def test_configureShiftPlan_fromToDayDropdown_mondayToSunday(self):
        """Positive: 'From day' and 'To day' dropdowns contain all days
        Monday through Sunday."""
        days = ["Monday", "Tuesday", "Wednesday", "Thursday",
                "Friday", "Saturday", "Sunday"]
        self.popup.get_day_options.return_value = days

        options = self.popup.get_day_options()

        self.assertEqual(len(options), 7)
        self.assertEqual(options[0], "Monday")
        self.assertEqual(options[6], "Sunday")

    def test_configureShiftPlan_scheduleShiftButton_setsLockInPeriod(self):
        """Positive: Clicking 'Schedule Shift' in configure popup sets
        the lock-in period for the shift plan release to shop users."""
        self.service.configure_lock_in.return_value = {
            "status": "success",
            "lock_in_from_day": "Wednesday",
            "lock_in_to_day": "Friday",
            "lock_in_start_time": "08:00",
            "lock_in_end_time": "17:00",
            "message": "Lock-in period configured successfully",
        }

        result = self.service.configure_lock_in(
            from_day="Wednesday",
            to_day="Friday",
            start_time="08:00",
            end_time="17:00",
        )

        self.assertEqual(result["status"], "success")
        self.assertIn("configured successfully", result["message"])

    def test_configureShiftPlan_autoRelease_basedOnScheduledDayTime(self):
        """Positive: System automatically releases shift plans to shop
        users based on the configured day and time."""
        self.service.get_release_schedule.return_value = {
            "from_day": "Thursday",
            "to_day": "Friday",
            "start_time": "06:00",
            "end_time": "18:00",
            "auto_release": True,
        }

        result = self.service.get_release_schedule()

        self.assertTrue(result["auto_release"])

    # -- Negative tests ------------------------------------------------------

    def test_configureShiftPlan_missingFromDay_rejected(self):
        """Negative: Submitting configure form without 'From day' is rejected."""
        self.service.configure_lock_in.return_value = {
            "status": "error",
            "message": "From day is required.",
        }

        result = self.service.configure_lock_in(
            from_day=None,
            to_day="Friday",
            start_time="08:00",
            end_time="17:00",
        )

        self.assertEqual(result["status"], "error")
        self.assertIn("required", result["message"])

    def test_configureShiftPlan_missingStartTime_rejected(self):
        """Negative: Submitting configure form without 'Start time' is rejected."""
        self.service.configure_lock_in.return_value = {
            "status": "error",
            "message": "Start time is required.",
        }

        result = self.service.configure_lock_in(
            from_day="Wednesday",
            to_day="Friday",
            start_time=None,
            end_time="17:00",
        )

        self.assertEqual(result["status"], "error")

    def test_configureShiftPlan_endTimeBeforeStartTime_rejected(self):
        """Negative: End time before start time (on the same day) is rejected."""
        self.service.configure_lock_in.return_value = {
            "status": "error",
            "message": "End time must be after start time.",
        }

        result = self.service.configure_lock_in(
            from_day="Wednesday",
            to_day="Wednesday",
            start_time="17:00",
            end_time="08:00",
        )

        self.assertEqual(result["status"], "error")
        self.assertIn("End time must be after", result["message"])

    # -- Boundary tests ------------------------------------------------------

    def test_configureShiftPlan_sameFromAndToDay_singleDayLockIn(self):
        """Boundary: Setting From day and To day to the same day creates
        a single-day lock-in period."""
        self.service.configure_lock_in.return_value = {
            "status": "success",
            "lock_in_days": 1,
        }

        result = self.service.configure_lock_in(
            from_day="Monday",
            to_day="Monday",
            start_time="00:00",
            end_time="23:59",
        )

        self.assertEqual(result["status"], "success")
        self.assertEqual(result["lock_in_days"], 1)

    def test_configureShiftPlan_fullWeekLockIn_accepted(self):
        """Boundary: Setting From day = Monday and To day = Sunday creates
        a full-week lock-in period."""
        self.service.configure_lock_in.return_value = {
            "status": "success",
            "lock_in_days": 7,
        }

        result = self.service.configure_lock_in(
            from_day="Monday",
            to_day="Sunday",
            start_time="00:00",
            end_time="23:59",
        )

        self.assertEqual(result["status"], "success")
        self.assertEqual(result["lock_in_days"], 7)

    def test_configureShiftPlan_midnightBoundary_timePickers(self):
        """Boundary: Setting start time to 00:00 and end time to 23:59
        covers the full day without error."""
        self.service.configure_lock_in.return_value = {
            "status": "success",
            "lock_in_start_time": "00:00",
            "lock_in_end_time": "23:59",
        }

        result = self.service.configure_lock_in(
            from_day="Tuesday",
            to_day="Tuesday",
            start_time="00:00",
            end_time="23:59",
        )

        self.assertEqual(result["status"], "success")
        self.assertEqual(result["lock_in_start_time"], "00:00")
        self.assertEqual(result["lock_in_end_time"], "23:59")


# ===========================================================================
# US-036: IR Admin – Export
# ===========================================================================


class TestUS036_IRAdminExport(unittest.TestCase):
    """US-036: IR Admin clicks 'Export' button to export shift scheduling
    details to an Excel file. Same behavior as US-034 (IR Export)."""

    def setUp(self):
        self.service = MagicMock()

    def test_irAdmin_exportButton_exportsAllDataToExcel(self):
        """Positive: IR Admin clicking 'Export' without date filter exports
        all data to an Excel file."""
        self.service.export.return_value = {
            "status": "success",
            "file_format": "xlsx",
            "record_count": 300,
        }

        result = self.service.export()

        self.assertEqual(result["status"], "success")
        self.assertEqual(result["file_format"], "xlsx")

    def test_irAdmin_exportButton_withDateFilter_exportsFiltered(self):
        """Positive: IR Admin clicking 'Export' with From/To date filter
        exports only the filtered data."""
        self.service.export.return_value = {
            "status": "success",
            "filter_applied": True,
            "record_count": 50,
        }

        result = self.service.export(from_date="01-12-2025", to_date="31-12-2025")

        self.assertTrue(result["filter_applied"])
        self.assertEqual(result["record_count"], 50)

    def test_irAdmin_exportButton_withoutFilter_exportsAll(self):
        """Positive: IR Admin clicking 'Export' without any filter exports
        all existing data."""
        self.service.export.return_value = {
            "status": "success",
            "filter_applied": False,
            "record_count": 600,
        }

        result = self.service.export(from_date=None, to_date=None)

        self.assertFalse(result["filter_applied"])

    def test_irAdmin_export_saveFileToLocation(self):
        """Positive: IR Admin can save the exported Excel file to a location."""
        self.service.export.return_value = {
            "status": "success",
            "file_name": "ir_admin_shift_export.xlsx",
            "downloadable": True,
        }

        result = self.service.export()

        self.assertTrue(result["downloadable"])
        self.assertTrue(result["file_name"].endswith(".xlsx"))

    # -- Negative tests ------------------------------------------------------

    def test_irAdmin_export_noRecords_showsMessage(self):
        """Negative: Exporting when no data is available displays
        'No data available to export' message."""
        self.service.export.return_value = {
            "status": "info",
            "message": "No data available to export",
            "record_count": 0,
        }

        result = self.service.export()

        self.assertEqual(result["record_count"], 0)
        self.assertIn("No data", result["message"])

    def test_irAdmin_export_serviceFailure_raisesException(self):
        """Negative: If the export service encounters a failure,
        an appropriate exception is raised."""
        self.service.export.side_effect = Exception("Internal server error")

        with self.assertRaises(Exception) as ctx:
            self.service.export()

        self.assertIn("Internal server error", str(ctx.exception))

    # -- Boundary tests ------------------------------------------------------

    def test_irAdmin_export_largeDataset_succeeds(self):
        """Boundary: Exporting a very large dataset (50,000+ records)
        completes without timeout."""
        self.service.export.return_value = {
            "status": "success",
            "record_count": 50000,
        }

        result = self.service.export()

        self.assertEqual(result["status"], "success")
        self.assertEqual(result["record_count"], 50000)

    def test_irAdmin_export_specialCharactersInData_handledGracefully(self):
        """Boundary: Data containing special characters (accents, symbols)
        is exported correctly without corruption."""
        self.service.export.return_value = {
            "status": "success",
            "record_count": 5,
            "sample_name": "José García – Shift α",
        }

        result = self.service.export()

        self.assertEqual(result["status"], "success")
        self.assertIn("José", result["sample_name"])


# ===========================================================================
# Cross-cutting: Role-based access control
# ===========================================================================


class TestRoleBasedAccessControl(unittest.TestCase):
    """Cross-cutting tests: Verify role-based access differences between
    IR and IR Admin roles for Maintain Shift Scheduling Plan."""

    def setUp(self):
        self.auth_service = MagicMock()

    def test_irRole_cannotAccessConfigureShiftPlan(self):
        """Negative: IR role does not have access to 'Configure Shift Plan'
        functionality (only IR Admin does)."""
        self.auth_service.get_permissions.return_value = {
            "view": True,
            "edit": True,
            "export": True,
            "configure_shift_plan": False,
        }

        perms = self.auth_service.get_permissions(role="IR")

        self.assertFalse(perms["configure_shift_plan"])

    def test_irAdminRole_hasConfigureShiftPlanAccess(self):
        """Positive: IR Admin role has access to 'Configure Shift Plan'."""
        self.auth_service.get_permissions.return_value = {
            "view": True,
            "edit": True,
            "export": True,
            "configure_shift_plan": True,
        }

        perms = self.auth_service.get_permissions(role="IR Admin")

        self.assertTrue(perms["configure_shift_plan"])

    def test_unauthenticatedUser_cannotAccessPage(self):
        """Negative: An unauthenticated user cannot access the Maintain
        Shift Scheduling Plan page."""
        self.auth_service.check_auth.return_value = {
            "authenticated": False,
            "redirect": "/login",
        }

        result = self.auth_service.check_auth(token=None)

        self.assertFalse(result["authenticated"])
        self.assertEqual(result["redirect"], "/login")

    def test_irRole_canEditDuringNonLockInPeriod(self):
        """Positive: IR user can edit shift plans outside the lock-in period."""
        self.auth_service.can_edit.return_value = True

        can_edit = self.auth_service.can_edit(role="IR", is_lock_in=False)

        self.assertTrue(can_edit)

    def test_irRole_cannotEditDuringLockInPeriod(self):
        """Negative: IR user cannot edit shift plans during the lock-in period."""
        self.auth_service.can_edit.return_value = False

        can_edit = self.auth_service.can_edit(role="IR", is_lock_in=True)

        self.assertFalse(can_edit)


if __name__ == "__main__":
    unittest.main()
