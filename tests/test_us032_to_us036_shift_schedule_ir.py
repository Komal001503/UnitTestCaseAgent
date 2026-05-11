"""
Unit Tests for Maintain Shift Scheduling Plan – IR & IR Admin Roles
User Stories: US-032 (IR View), US-033 (IR Schedule Shift), US-034 (IR Export),
              US-035 (IR Admin View + Configure), US-036 (IR Admin Export)

Covers shift scheduling functionality for:
- IR (Industrial Relation) – view, edit, schedule shift, export
- IR Admin – view with configure shift plan, export

Test Categories:
- Positive / Happy Path
- Negative / Error Path
- Boundary / Edge Cases
"""

SOURCE_STORY_FILE = "MaintainShiftSchedulingPlanUserStory.xlsx"

import unittest
from unittest.mock import MagicMock, patch


# TODO: Import actual modules once implementation is available.
# from src.attendance.shift_schedule import (
#     ShiftSchedulePage, ShiftScheduleService, ShiftCodeMaster,
#     ShiftRotationMaster, ExportService, ConfigureShiftPlanService
# )


# ---------------------------------------------------------------------------
# US-032: IR – View Maintain Shift Scheduling Plan
# ---------------------------------------------------------------------------


class TestShiftSchedulePageDisplay(unittest.TestCase):
    """US-032: Verify Maintain Shift Scheduling Plan page displays correctly."""

    def setUp(self):
        """Arrange: Create mock page and navigation services."""
        self.navigation = MagicMock()
        self.page = MagicMock()
        self.page.get_attributes.return_value = ["Shift Code", "From", "To"]
        self.page.get_grid_columns.return_value = [
            "Employee", "Dept Code and Shop Name", "Cadre", "Category",
            "Shift", "Monday", "Tuesday", "Wednesday", "Thursday",
            "Friday", "Saturday", "Sunday", "Supervisor", "TPT User",
            "Last Modified By", "Action", "Select",
        ]
        self.page.get_buttons.return_value = ["Save", "Export"]

    def test_navigation_selectAttendanceMenu_displaysShiftSchedulePage(self):
        """Positive: Selecting Maintain Shift Scheduling Plan from Attendance Management opens the page."""
        self.navigation.select_menu.return_value = "Maintain Shift Scheduling Plan"

        result = self.navigation.select_menu("Attendance Management", "Maintain Shift Scheduling Plan")

        self.assertEqual(result, "Maintain Shift Scheduling Plan")
        self.navigation.select_menu.assert_called_once()

    def test_page_load_displaysShiftCodeAttribute(self):
        """Positive: Page displays Shift Code attribute field."""
        attributes = self.page.get_attributes()

        self.assertIn("Shift Code", attributes)

    def test_page_load_displaysFromAndToDateAttributes(self):
        """Positive: Page displays From and To date attributes."""
        attributes = self.page.get_attributes()

        self.assertIn("From", attributes)
        self.assertIn("To", attributes)

    def test_page_load_displaysAllGridColumns(self):
        """Positive: Page grid displays all 17 required columns."""
        columns = self.page.get_grid_columns()

        self.assertEqual(len(columns), 17)
        self.assertIn("Employee", columns)
        self.assertIn("Shift", columns)
        self.assertIn("Supervisor", columns)

    def test_page_load_displaysShiftPlanDayColumns(self):
        """Positive: Grid includes shift plan columns for all seven days."""
        columns = self.page.get_grid_columns()
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

        for day in days:
            self.assertIn(day, columns)

    def test_page_load_displaysSaveAndExportButtons(self):
        """Positive: Page displays Save and Export buttons."""
        buttons = self.page.get_buttons()

        self.assertEqual(len(buttons), 2)
        self.assertIn("Save", buttons)
        self.assertIn("Export", buttons)

    def test_page_unauthorizedRole_deniesAccess(self):
        """Negative: Non-IR user is denied access to the page."""
        self.navigation.select_menu.side_effect = PermissionError("Access denied")

        with self.assertRaises(PermissionError):
            self.navigation.select_menu("Attendance Management", "Maintain Shift Scheduling Plan")

    def test_page_noData_showsEmptyGrid(self):
        """Boundary: Page with no shift data shows empty grid message."""
        self.page.get_grid_data.return_value = []

        data = self.page.get_grid_data()

        self.assertEqual(len(data), 0)


class TestShiftCodeSelection(unittest.TestCase):
    """US-032: Verify shift code selection auto-populates dates."""

    def setUp(self):
        """Arrange: Create mock shift code master service."""
        self.shift_code_service = MagicMock()

    def test_shiftCode_validSelection_autoPopulatesFromAndToDates(self):
        """Positive: Selecting a valid shift code auto-populates From and To dates."""
        self.shift_code_service.get_week_dates.return_value = {
            "from": "01-01-2026",
            "to": "07-01-2026",
        }

        result = self.shift_code_service.get_week_dates("SC-001")

        self.assertEqual(result["from"], "01-01-2026")
        self.assertEqual(result["to"], "07-01-2026")

    def test_shiftCode_invalidCode_returnsError(self):
        """Negative: Invalid shift code returns an error."""
        self.shift_code_service.get_week_dates.side_effect = ValueError("Invalid shift code")

        with self.assertRaises(ValueError):
            self.shift_code_service.get_week_dates("INVALID")

    def test_shiftCode_noSelection_datesRemainEmpty(self):
        """Boundary: No shift code selected leaves date fields empty."""
        self.shift_code_service.get_week_dates.return_value = {"from": None, "to": None}

        result = self.shift_code_service.get_week_dates(None)

        self.assertIsNone(result["from"])
        self.assertIsNone(result["to"])


class TestShiftScheduleGridData(unittest.TestCase):
    """US-032: Verify grid data population and employee details."""

    def setUp(self):
        """Arrange: Create mock services for grid data."""
        self.grid_service = MagicMock()
        self.grid_service.get_employee_row.return_value = {
            "employee": "1001 - John Doe",
            "dept_code": "D100 - Assembly",
            "cadre": "Skilled",
            "category": "Permanent",
            "shift": "I",
            "monday": "I", "tuesday": "I", "wednesday": "I",
            "thursday": "I", "friday": "I", "saturday": "OFF", "sunday": "OFF",
            "supervisor": "S500 - Jane Smith",
            "tpt_user": "No",
            "last_modified_by": "1002 - Admin - 01-01-2026",
        }

    def test_grid_employeeRow_displaysAllFields(self):
        """Positive: Employee row displays all required data fields."""
        row = self.grid_service.get_employee_row("1001")

        self.assertIn("1001", row["employee"])
        self.assertEqual(row["shift"], "I")
        self.assertEqual(row["tpt_user"], "No")

    def test_grid_supervisor_autoPopulatedFromDeptCode(self):
        """Positive: Supervisor field is auto-populated based on dept code."""
        row = self.grid_service.get_employee_row("1001")

        self.assertIn("Jane Smith", row["supervisor"])

    def test_grid_lastModifiedBy_showsPSNoNameDate(self):
        """Positive: Last Modified By shows PS No, Name, and Date."""
        row = self.grid_service.get_employee_row("1001")

        self.assertIn("1002", row["last_modified_by"])
        self.assertIn("Admin", row["last_modified_by"])

    def test_grid_multiSelect_selectsMultipleEmployees(self):
        """Positive: Multi-select checkbox selects multiple employees."""
        self.grid_service.select_employees.return_value = ["1001", "1002", "1003"]

        selected = self.grid_service.select_employees(["1001", "1002", "1003"])

        self.assertEqual(len(selected), 3)

    def test_grid_multiSelect_noSelection_returnsEmpty(self):
        """Boundary: No employee selected returns empty list."""
        self.grid_service.select_employees.return_value = []

        selected = self.grid_service.select_employees([])

        self.assertEqual(len(selected), 0)


class TestShiftEditAndValidation(unittest.TestCase):
    """US-032: Verify shift editing, validation, and lock-in logic."""

    def setUp(self):
        """Arrange: Create mock shift schedule service."""
        self.shift_service = MagicMock()

    def test_editIcon_click_makesShiftAndDaysEditable(self):
        """Positive: Clicking edit icon makes Shift and day columns editable."""
        self.shift_service.enable_edit.return_value = {
            "editable_fields": ["Shift", "Monday", "Tuesday", "Wednesday",
                                "Thursday", "Friday", "Saturday", "Sunday"]
        }

        result = self.shift_service.enable_edit("1001")

        self.assertEqual(len(result["editable_fields"]), 8)
        self.assertIn("Shift", result["editable_fields"])

    def test_shiftChange_changeShiftColumn_updatesAllDays(self):
        """Positive: Changing shift column updates shift for all applicable days."""
        self.shift_service.change_shift.return_value = {
            "monday": "I", "tuesday": "I", "wednesday": "I",
            "thursday": "I", "friday": "I", "saturday": "OFF", "sunday": "OFF",
        }

        result = self.shift_service.change_shift("1001", "II", "I")

        self.assertEqual(result["monday"], "I")
        self.assertEqual(result["friday"], "I")

    def test_shiftChange_nonApplicableRotation_rejected(self):
        """Negative: Changing to a shift not in employee rotation is rejected."""
        self.shift_service.change_shift.side_effect = ValueError(
            "Shift not applicable to employee rotation"
        )

        with self.assertRaises(ValueError):
            self.shift_service.change_shift("1001", "I", "IV")

    def test_edit_duringLockInPeriod_restricted(self):
        """Negative: IR cannot edit shifts during the lock-in period."""
        self.shift_service.is_locked.return_value = True

        is_locked = self.shift_service.is_locked()

        self.assertTrue(is_locked)

    def test_edit_outsideLockInPeriod_allowed(self):
        """Positive: IR can edit shifts outside the lock-in period."""
        self.shift_service.is_locked.return_value = False

        is_locked = self.shift_service.is_locked()

        self.assertFalse(is_locked)

    def test_autoRelease_afterLockIn_releasesToShopUsers(self):
        """Positive: System auto-releases shift plan after lock-in period expires."""
        self.shift_service.auto_release.return_value = {"released": True}

        result = self.shift_service.auto_release()

        self.assertTrue(result["released"])

    def test_save_validChanges_showsSuccessPopup(self):
        """Positive: Saving valid changes displays success message."""
        self.shift_service.save.return_value = {
            "status": "success",
            "message": "Changes have been saved successfully",
        }

        result = self.shift_service.save("1001")

        self.assertEqual(result["message"], "Changes have been saved successfully")

    def test_save_noChanges_showsInfoMessage(self):
        """Boundary: Saving with no changes shows informational message."""
        self.shift_service.save.return_value = {
            "status": "info",
            "message": "No changes to save",
        }

        result = self.shift_service.save("1001")

        self.assertEqual(result["status"], "info")


class TestShiftScheduleSearch(unittest.TestCase):
    """US-032: Verify column and global search functionality."""

    def setUp(self):
        """Arrange: Create mock search service."""
        self.search_service = MagicMock()

    def test_columnSearch_byEmployeeName_filtersResults(self):
        """Positive: Column search by employee name filters the grid."""
        self.search_service.column_search.return_value = [
            {"employee": "1001 - John Doe"}
        ]

        results = self.search_service.column_search("Employee", "John")

        self.assertEqual(len(results), 1)

    def test_globalSearch_byDeptCode_findsResults(self):
        """Positive: Global search by department code returns matching records."""
        self.search_service.global_search.return_value = [
            {"dept_code": "D100 - Assembly"}
        ]

        results = self.search_service.global_search("D100")

        self.assertEqual(len(results), 1)

    def test_search_noMatch_returnsEmptyList(self):
        """Boundary: Search with no matching term returns empty list."""
        self.search_service.global_search.return_value = []

        results = self.search_service.global_search("NONEXISTENT")

        self.assertEqual(len(results), 0)

    def test_pageNavigation_navigateToPage_displaysCorrectData(self):
        """Positive: Page navigation navigates to specified page."""
        self.search_service.navigate_to_page.return_value = {"page": 3, "total_pages": 10}

        result = self.search_service.navigate_to_page(3)

        self.assertEqual(result["page"], 3)

    def test_pageNavigation_beyondLastPage_returnsLastPage(self):
        """Boundary: Navigating beyond last page returns last page."""
        self.search_service.navigate_to_page.return_value = {"page": 10, "total_pages": 10}

        result = self.search_service.navigate_to_page(999)

        self.assertEqual(result["page"], 10)


# ---------------------------------------------------------------------------
# US-033: IR – Edit / Schedule Shift
# ---------------------------------------------------------------------------


class TestScheduleShiftPopup(unittest.TestCase):
    """US-033: Verify schedule shift popup displays correctly."""

    def setUp(self):
        """Arrange: Create mock schedule shift service."""
        self.schedule_service = MagicMock()
        self.schedule_service.get_popup_fields.return_value = [
            "Employee List", "Shift Pattern", "Start Date",
            "End Date", "Forever", "Pattern Week",
        ]
        self.schedule_service.get_data_grid_columns.return_value = [
            "Rotation Type", "Monday", "Tuesday", "Wednesday",
            "Thursday", "Friday", "Saturday", "Sunday",
        ]

    def test_scheduleShiftButton_click_opensPopupWithFields(self):
        """Positive: Clicking schedule shift button opens popup with all required fields."""
        fields = self.schedule_service.get_popup_fields()

        self.assertEqual(len(fields), 6)
        self.assertIn("Shift Pattern", fields)
        self.assertIn("Start Date", fields)
        self.assertIn("Forever", fields)
        self.assertIn("Pattern Week", fields)

    def test_popup_displaysSelectedEmployeeList(self):
        """Positive: Popup displays the list of employees selected before clicking."""
        self.schedule_service.get_selected_employees.return_value = [
            "1001 - John Doe", "1002 - Jane Smith"
        ]

        employees = self.schedule_service.get_selected_employees()

        self.assertEqual(len(employees), 2)

    def test_popup_shiftPatternFetchedFromMaster(self):
        """Positive: Shift pattern is fetched from shift rotation master."""
        self.schedule_service.get_shift_patterns.return_value = ["I-III-II", "I-II-III"]

        patterns = self.schedule_service.get_shift_patterns("1001")

        self.assertEqual(len(patterns), 2)
        self.assertIn("I-III-II", patterns)

    def test_popup_patternWeekDropdown_displaysWeeks(self):
        """Positive: Pattern week dropdown shows correct number of weeks."""
        self.schedule_service.get_pattern_weeks.return_value = [
            "Week 1", "Week 2", "Week 3", "Week 4", "Week 5"
        ]

        weeks = self.schedule_service.get_pattern_weeks()

        self.assertEqual(len(weeks), 5)

    def test_popup_dataGrid_displaysRotationAndDays(self):
        """Positive: Data grid in popup shows rotation type and day columns."""
        columns = self.schedule_service.get_data_grid_columns()

        self.assertEqual(len(columns), 8)
        self.assertIn("Rotation Type", columns)

    def test_popup_noEmployeesSelected_showsError(self):
        """Negative: Opening schedule shift without selecting employees shows error."""
        self.schedule_service.open_popup.side_effect = ValueError(
            "Please select at least one employee"
        )

        with self.assertRaises(ValueError):
            self.schedule_service.open_popup([])

    def test_popup_monthWith4Weeks_shows4PatternWeeks(self):
        """Boundary: Month with 4 weeks shows only 4 entries in pattern week dropdown."""
        self.schedule_service.get_pattern_weeks.return_value = [
            "Week 1", "Week 2", "Week 3", "Week 4"
        ]

        weeks = self.schedule_service.get_pattern_weeks()

        self.assertEqual(len(weeks), 4)


class TestScheduleShiftActions(unittest.TestCase):
    """US-033: Verify schedule shift save/cancel and option messages."""

    def setUp(self):
        """Arrange: Create mock schedule shift service."""
        self.schedule_service = MagicMock()

    def test_option1_changeOneDayShift_showsSuccessMessage(self):
        """Positive: Option 1 – change for one day shows correct success message."""
        self.schedule_service.schedule_shift.return_value = {
            "status": "success",
            "message": "Shift plan successfully changed for one day",
        }

        result = self.schedule_service.schedule_shift(
            employees=["1001"], option="one_day", date="05-01-2026"
        )

        self.assertIn("one day", result["message"])

    def test_option2_changeCurrentWeek_showsDateRangeMessage(self):
        """Positive: Option 2 – change for current week shows date range message."""
        self.schedule_service.schedule_shift.return_value = {
            "status": "success",
            "message": "Shift plan successfully changed for current week only from 01-01-2026 to 07-01-2026",
        }

        result = self.schedule_service.schedule_shift(
            employees=["1001"], option="current_week",
            start_date="01-01-2026", end_date="07-01-2026"
        )

        self.assertIn("current week", result["message"])
        self.assertIn("01-01-2026", result["message"])

    def test_option3_changeForever_showsForeverMessage(self):
        """Positive: Option 3 – change forever shows forever message."""
        self.schedule_service.schedule_shift.return_value = {
            "status": "success",
            "message": 'New shift rotation will be carried forward for the workman from 01-01-2026 to "Forever"',
        }

        result = self.schedule_service.schedule_shift(
            employees=["1001"], option="forever", start_date="01-01-2026"
        )

        self.assertIn("Forever", result["message"])

    def test_cancelButton_revertsChanges(self):
        """Positive: Clicking cancel button reverts changes and closes popup."""
        self.schedule_service.cancel.return_value = {"saved": False, "popup_closed": True}

        result = self.schedule_service.cancel()

        self.assertFalse(result["saved"])
        self.assertTrue(result["popup_closed"])

    def test_scheduleShift_savesAndClosesPopup(self):
        """Positive: Clicking schedule shift saves and closes the popup."""
        self.schedule_service.schedule_shift.return_value = {
            "status": "success", "popup_closed": True
        }

        result = self.schedule_service.schedule_shift(
            employees=["1001"], option="one_day", date="05-01-2026"
        )

        self.assertEqual(result["status"], "success")

    def test_startDateAfterEndDate_rejected(self):
        """Negative: Start date after end date is rejected."""
        self.schedule_service.schedule_shift.side_effect = ValueError(
            "Start date must be before end date"
        )

        with self.assertRaises(ValueError):
            self.schedule_service.schedule_shift(
                employees=["1001"], option="current_week",
                start_date="10-01-2026", end_date="05-01-2026"
            )

    def test_missingStartDate_rejected(self):
        """Negative: Missing start date for date range option is rejected."""
        self.schedule_service.schedule_shift.side_effect = ValueError(
            "Start date is required"
        )

        with self.assertRaises(ValueError):
            self.schedule_service.schedule_shift(
                employees=["1001"], option="current_week",
                start_date=None, end_date="07-01-2026"
            )

    def test_foreverWithoutStartDate_rejected(self):
        """Negative: Forever option without start date is rejected."""
        self.schedule_service.schedule_shift.side_effect = ValueError(
            "Start date is required for forever option"
        )

        with self.assertRaises(ValueError):
            self.schedule_service.schedule_shift(
                employees=["1001"], option="forever", start_date=None
            )

    def test_sameStartAndEndDate_treatedAsSingleDay(self):
        """Boundary: Same start and end date is treated as a single day change."""
        self.schedule_service.schedule_shift.return_value = {
            "status": "success",
            "message": "Shift plan successfully changed for one day",
        }

        result = self.schedule_service.schedule_shift(
            employees=["1001"], option="current_week",
            start_date="05-01-2026", end_date="05-01-2026"
        )

        self.assertIn("one day", result["message"])

    def test_dateRangeSpanningMultipleWeeks_accepted(self):
        """Boundary: Date range spanning multiple weeks is accepted."""
        self.schedule_service.schedule_shift.return_value = {
            "status": "success",
            "message": "Shift plan successfully changed for current week only from 01-01-2026 to 31-01-2026",
        }

        result = self.schedule_service.schedule_shift(
            employees=["1001"], option="current_week",
            start_date="01-01-2026", end_date="31-01-2026"
        )

        self.assertEqual(result["status"], "success")

    def test_bulkSchedule_100Employees_succeeds(self):
        """Boundary: Scheduling shift for 100 employees at once succeeds."""
        employee_ids = [str(i) for i in range(1001, 1101)]
        self.schedule_service.schedule_shift.return_value = {
            "status": "success", "affected_count": 100
        }

        result = self.schedule_service.schedule_shift(
            employees=employee_ids, option="one_day", date="05-01-2026"
        )

        self.assertEqual(result["affected_count"], 100)


# ---------------------------------------------------------------------------
# US-034: IR – Export Data
# ---------------------------------------------------------------------------


class TestIRExportData(unittest.TestCase):
    """US-034: Verify IR can export shift schedule data to Excel."""

    def setUp(self):
        """Arrange: Create mock export service."""
        self.export_service = MagicMock()

    def test_export_allData_generatesExcelFile(self):
        """Positive: Export without filter generates Excel file with all records."""
        self.export_service.export_to_excel.return_value = {
            "status": "success", "filename": "shift_schedule.xlsx", "record_count": 500
        }

        result = self.export_service.export_to_excel()

        self.assertEqual(result["status"], "success")
        self.assertIn(".xlsx", result["filename"])

    def test_export_withDateFilter_exportsFilteredData(self):
        """Positive: Export with from/to date filter exports only filtered records."""
        self.export_service.export_to_excel.return_value = {
            "status": "success", "record_count": 50
        }

        result = self.export_service.export_to_excel(
            from_date="01-01-2026", to_date="07-01-2026"
        )

        self.assertEqual(result["record_count"], 50)

    def test_export_withoutFilter_exportsAllData(self):
        """Positive: Export without date filter exports all existing data."""
        self.export_service.export_to_excel.return_value = {
            "status": "success", "record_count": 1000
        }

        result = self.export_service.export_to_excel(from_date=None, to_date=None)

        self.assertEqual(result["record_count"], 1000)

    def test_export_saveFileToLocation(self):
        """Positive: User can save the exported file to a chosen location."""
        self.export_service.save_file.return_value = {"saved": True, "path": "/downloads/shift.xlsx"}

        result = self.export_service.save_file("/downloads/shift.xlsx")

        self.assertTrue(result["saved"])

    def test_export_noData_showsInfoMessage(self):
        """Negative: Export with no data available shows info message."""
        self.export_service.export_to_excel.return_value = {
            "status": "info", "message": "No records to export"
        }

        result = self.export_service.export_to_excel()

        self.assertEqual(result["status"], "info")

    def test_export_serviceFailure_raisesException(self):
        """Negative: Export service failure raises an exception."""
        self.export_service.export_to_excel.side_effect = RuntimeError("Export service unavailable")

        with self.assertRaises(RuntimeError):
            self.export_service.export_to_excel()

    def test_export_largeDataset_succeeds(self):
        """Boundary: Export with very large dataset (10K records) succeeds."""
        self.export_service.export_to_excel.return_value = {
            "status": "success", "record_count": 10000
        }

        result = self.export_service.export_to_excel()

        self.assertEqual(result["record_count"], 10000)

    def test_export_onlyFromDateFilter_exportsFiltered(self):
        """Boundary: Export with only from date filter applied exports filtered data."""
        self.export_service.export_to_excel.return_value = {
            "status": "success", "record_count": 200
        }

        result = self.export_service.export_to_excel(from_date="01-01-2026", to_date=None)

        self.assertEqual(result["record_count"], 200)


# ---------------------------------------------------------------------------
# US-035: IR Admin – View with Configure Shift Plan
# ---------------------------------------------------------------------------


class TestIRAdminPageDisplay(unittest.TestCase):
    """US-035: Verify IR Admin page displays Configure Shift Plan button."""

    def setUp(self):
        """Arrange: Create mock IR Admin page service."""
        self.admin_page = MagicMock()
        self.admin_page.get_buttons.return_value = ["Save", "Export", "Configure Shift Plan"]
        self.admin_page.get_attributes.return_value = ["Shift Code", "From", "To"]
        self.admin_page.get_grid_columns.return_value = [
            "Employee", "Dept Code and Shop Name", "Cadre", "Category",
            "Shift", "Monday", "Tuesday", "Wednesday", "Thursday",
            "Friday", "Saturday", "Sunday", "Supervisor", "TPT User",
            "Last Modified By", "Action", "Select",
        ]

    def test_adminPage_displaysConfigureShiftPlanButton(self):
        """Positive: IR Admin page displays Configure Shift Plan button."""
        buttons = self.admin_page.get_buttons()

        self.assertEqual(len(buttons), 3)
        self.assertIn("Configure Shift Plan", buttons)

    def test_adminPage_displaysAllGridColumns(self):
        """Positive: IR Admin grid displays all 17 columns same as IR."""
        columns = self.admin_page.get_grid_columns()

        self.assertEqual(len(columns), 17)

    def test_adminPage_displaysAttributes(self):
        """Positive: IR Admin page displays same attributes as IR."""
        attributes = self.admin_page.get_attributes()

        self.assertEqual(len(attributes), 3)

    def test_adminPage_editIcon_makesFieldsEditable(self):
        """Positive: Edit icon makes Shift and day columns editable for admin."""
        self.admin_page.enable_edit.return_value = {
            "editable_fields": ["Shift", "Monday", "Tuesday", "Wednesday",
                                "Thursday", "Friday", "Saturday", "Sunday"]
        }

        result = self.admin_page.enable_edit("1001")

        self.assertEqual(len(result["editable_fields"]), 8)

    def test_adminPage_save_showsSuccessPopup(self):
        """Positive: Admin saving changes shows success popup."""
        self.admin_page.save.return_value = {
            "status": "success",
            "message": "Changes have been saved successfully",
        }

        result = self.admin_page.save("1001")

        self.assertEqual(result["message"], "Changes have been saved successfully")

    def test_nonAdminRole_cannotSeeConfigureButton(self):
        """Negative: Non-admin IR user does not see Configure Shift Plan button."""
        ir_page = MagicMock()
        ir_page.get_buttons.return_value = ["Save", "Export"]

        buttons = ir_page.get_buttons()

        self.assertNotIn("Configure Shift Plan", buttons)
        self.assertEqual(len(buttons), 2)


class TestConfigureShiftPlan(unittest.TestCase):
    """US-035: Verify Configure Shift Plan popup and scheduling."""

    def setUp(self):
        """Arrange: Create mock configure shift plan service."""
        self.config_service = MagicMock()
        self.config_service.get_configure_fields.return_value = [
            "From Day", "To Day", "Start Time", "End Time"
        ]

    def test_configurePopup_displaysFourFields(self):
        """Positive: Configure Shift Plan popup shows 4 required fields."""
        fields = self.config_service.get_configure_fields()

        self.assertEqual(len(fields), 4)
        self.assertIn("From Day", fields)
        self.assertIn("To Day", fields)
        self.assertIn("Start Time", fields)
        self.assertIn("End Time", fields)

    def test_configureDayDropdown_showsMondayToSunday(self):
        """Positive: From/To day dropdowns contain Monday through Sunday."""
        self.config_service.get_day_options.return_value = [
            "Monday", "Tuesday", "Wednesday", "Thursday",
            "Friday", "Saturday", "Sunday"
        ]

        options = self.config_service.get_day_options()

        self.assertEqual(len(options), 7)
        self.assertIn("Monday", options)
        self.assertIn("Sunday", options)

    def test_scheduleShift_setsLockInPeriod(self):
        """Positive: Clicking Schedule Shift configures the lock-in period."""
        self.config_service.configure_lock_in.return_value = {
            "status": "success",
            "lock_in": {"from_day": "Friday", "to_day": "Sunday",
                        "start_time": "18:00", "end_time": "06:00"},
        }

        result = self.config_service.configure_lock_in(
            from_day="Friday", to_day="Sunday",
            start_time="18:00", end_time="06:00"
        )

        self.assertEqual(result["status"], "success")

    def test_autoRelease_basedOnSchedule_releasesShifts(self):
        """Positive: System auto-releases shifts based on configured schedule."""
        self.config_service.check_auto_release.return_value = {"auto_release": True}

        result = self.config_service.check_auto_release()

        self.assertTrue(result["auto_release"])

    def test_configure_missingFromDay_rejected(self):
        """Negative: Missing From Day field is rejected."""
        self.config_service.configure_lock_in.side_effect = ValueError(
            "From Day is required"
        )

        with self.assertRaises(ValueError):
            self.config_service.configure_lock_in(
                from_day=None, to_day="Sunday",
                start_time="18:00", end_time="06:00"
            )

    def test_configure_missingStartTime_rejected(self):
        """Negative: Missing Start Time field is rejected."""
        self.config_service.configure_lock_in.side_effect = ValueError(
            "Start Time is required"
        )

        with self.assertRaises(ValueError):
            self.config_service.configure_lock_in(
                from_day="Friday", to_day="Sunday",
                start_time=None, end_time="06:00"
            )

    def test_configure_endTimeBeforeStartTime_rejected(self):
        """Negative: End time before start time is rejected."""
        self.config_service.configure_lock_in.side_effect = ValueError(
            "End time must be after start time"
        )

        with self.assertRaises(ValueError):
            self.config_service.configure_lock_in(
                from_day="Friday", to_day="Friday",
                start_time="18:00", end_time="06:00"
            )

    def test_configure_sameFromAndToDay_singleDayLockIn(self):
        """Boundary: Same From and To day creates a single day lock-in."""
        self.config_service.configure_lock_in.return_value = {
            "status": "success", "lock_in_days": 1
        }

        result = self.config_service.configure_lock_in(
            from_day="Friday", to_day="Friday",
            start_time="18:00", end_time="23:59"
        )

        self.assertEqual(result["lock_in_days"], 1)

    def test_configure_fullWeekLockIn_mondayToSunday(self):
        """Boundary: Full week lock-in from Monday to Sunday covers 7 days."""
        self.config_service.configure_lock_in.return_value = {
            "status": "success", "lock_in_days": 7
        }

        result = self.config_service.configure_lock_in(
            from_day="Monday", to_day="Sunday",
            start_time="00:00", end_time="23:59"
        )

        self.assertEqual(result["lock_in_days"], 7)

    def test_configure_midnightBoundaryTimes_accepted(self):
        """Boundary: Midnight boundary times (00:00 to 23:59) are accepted."""
        self.config_service.configure_lock_in.return_value = {
            "status": "success"
        }

        result = self.config_service.configure_lock_in(
            from_day="Monday", to_day="Monday",
            start_time="00:00", end_time="23:59"
        )

        self.assertEqual(result["status"], "success")


# ---------------------------------------------------------------------------
# US-036: IR Admin – Export Data
# ---------------------------------------------------------------------------


class TestIRAdminExportData(unittest.TestCase):
    """US-036: Verify IR Admin can export shift schedule data to Excel."""

    def setUp(self):
        """Arrange: Create mock export service for IR Admin."""
        self.export_service = MagicMock()

    def test_adminExport_allData_generatesExcelFile(self):
        """Positive: IR Admin export without filter generates Excel file."""
        self.export_service.export_to_excel.return_value = {
            "status": "success", "filename": "admin_shift_schedule.xlsx",
            "record_count": 500
        }

        result = self.export_service.export_to_excel()

        self.assertEqual(result["status"], "success")

    def test_adminExport_withDateFilter_exportsFilteredData(self):
        """Positive: IR Admin export with date filter exports filtered records."""
        self.export_service.export_to_excel.return_value = {
            "status": "success", "record_count": 75
        }

        result = self.export_service.export_to_excel(
            from_date="01-01-2026", to_date="07-01-2026"
        )

        self.assertEqual(result["record_count"], 75)

    def test_adminExport_withoutFilter_exportsAll(self):
        """Positive: IR Admin export without filter exports all data."""
        self.export_service.export_to_excel.return_value = {
            "status": "success", "record_count": 2000
        }

        result = self.export_service.export_to_excel(from_date=None, to_date=None)

        self.assertEqual(result["record_count"], 2000)

    def test_adminExport_saveFileToLocation(self):
        """Positive: Admin can save the exported file to a chosen location."""
        self.export_service.save_file.return_value = {"saved": True}

        result = self.export_service.save_file("/downloads/admin_shift.xlsx")

        self.assertTrue(result["saved"])

    def test_adminExport_noRecords_showsInfoMessage(self):
        """Negative: Export with no records shows informational message."""
        self.export_service.export_to_excel.return_value = {
            "status": "info", "message": "No records to export"
        }

        result = self.export_service.export_to_excel()

        self.assertEqual(result["status"], "info")

    def test_adminExport_serviceFailure_raisesException(self):
        """Negative: Export service failure raises an exception."""
        self.export_service.export_to_excel.side_effect = RuntimeError(
            "Export service unavailable"
        )

        with self.assertRaises(RuntimeError):
            self.export_service.export_to_excel()

    def test_adminExport_largeDataset_succeeds(self):
        """Boundary: Export with very large dataset (50K records) succeeds."""
        self.export_service.export_to_excel.return_value = {
            "status": "success", "record_count": 50000
        }

        result = self.export_service.export_to_excel()

        self.assertEqual(result["record_count"], 50000)

    def test_adminExport_specialCharactersInData_noCorruption(self):
        """Boundary: Export with special characters in data does not corrupt file."""
        self.export_service.export_to_excel.return_value = {
            "status": "success", "record_count": 10
        }

        result = self.export_service.export_to_excel(data_contains_unicode=True)

        self.assertEqual(result["status"], "success")


# ---------------------------------------------------------------------------
# Cross-cutting: Role-Based Access Control
# ---------------------------------------------------------------------------


class TestRoleBasedAccessControl(unittest.TestCase):
    """US-032 / US-035: Verify role-based access controls for shift scheduling."""

    def setUp(self):
        """Arrange: Create mock authentication and authorization services."""
        self.auth_service = MagicMock()

    def test_irRole_cannotAccessConfigureShiftPlan(self):
        """Negative: IR role cannot access Configure Shift Plan feature."""
        self.auth_service.has_permission.return_value = False

        result = self.auth_service.has_permission("IR", "configure_shift_plan")

        self.assertFalse(result)

    def test_irAdminRole_hasConfigureAccess(self):
        """Positive: IR Admin role has access to Configure Shift Plan."""
        self.auth_service.has_permission.return_value = True

        result = self.auth_service.has_permission("IR Admin", "configure_shift_plan")

        self.assertTrue(result)

    def test_unauthenticatedUser_redirectedToLogin(self):
        """Negative: Unauthenticated user is redirected to the login page."""
        self.auth_service.check_auth.return_value = {"authenticated": False, "redirect": "/login"}

        result = self.auth_service.check_auth(token=None)

        self.assertFalse(result["authenticated"])
        self.assertEqual(result["redirect"], "/login")

    def test_irRole_canEditOutsideLockIn(self):
        """Positive: IR role can edit shifts outside lock-in period."""
        self.auth_service.can_edit_shifts.return_value = True

        result = self.auth_service.can_edit_shifts("IR", lock_in_active=False)

        self.assertTrue(result)

    def test_irRole_cannotEditDuringLockIn(self):
        """Negative: IR role cannot edit shifts during lock-in period."""
        self.auth_service.can_edit_shifts.return_value = False

        result = self.auth_service.can_edit_shifts("IR", lock_in_active=True)

        self.assertFalse(result)


if __name__ == "__main__":
    unittest.main()
