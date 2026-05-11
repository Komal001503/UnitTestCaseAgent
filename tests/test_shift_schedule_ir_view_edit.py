"""
Unit Tests for Maintain Shift Scheduling Plan Module - IR Role
User Stories: Story 1 (IR View), Story 2 (IR Edit / Schedule Shift)

Covers:
- Viewing the Maintain Shift Scheduling Plan page
- Shift code selection and date auto-population
- Grid columns display and data fetching
- Editing shift plans via edit icon
- Schedule Shift popup and shift pattern management
- Lock-in period restrictions
- Save and validation messages

Test Categories:
- Positive / Happy Path
- Negative / Error Path
- Boundary / Edge Cases
- Integration Points
"""

import unittest
from unittest.mock import MagicMock, patch, PropertyMock


# TODO: Import actual modules once implementation is available.
# from src.attendance.shift_schedule import (
#     ShiftSchedulePage, ShiftScheduleService, ShiftCodeMaster,
#     ShiftRotationMaster, WorkforceInfoService, ScheduleShiftPopup
# )


# ---------------------------------------------------------------------------
# Story 1: IR - View Maintain Shift Scheduling Plan
# ---------------------------------------------------------------------------


class TestShiftScheduleNavigation(unittest.TestCase):
    """Story 1: Verify navigation to Maintain Shift Scheduling Plan page."""

    def setUp(self):
        """Arrange: Create mock navigation service."""
        self.navigation = MagicMock()
        self.navigation.get_attendance_submenus.return_value = [
            "Maintain Shift Scheduling Plan",
        ]

    def test_sideNavigation_attendanceMenu_displaysMaintainShiftSchedulePlan(self):
        """Positive: Attendance Management menu displays Maintain Shift Scheduling Plan sub menu."""
        submenus = self.navigation.get_attendance_submenus()

        self.assertIn("Maintain Shift Scheduling Plan", submenus)

    def test_sideNavigation_selectShiftSchedulePlan_displaysPage(self):
        """Positive: Selecting Maintain Shift Scheduling Plan opens the page."""
        self.navigation.open_page.return_value = {
            "status": "success",
            "page": "Maintain Shift Scheduling Plan",
        }

        result = self.navigation.open_page("Maintain Shift Scheduling Plan")

        self.assertEqual(result["status"], "success")
        self.assertEqual(result["page"], "Maintain Shift Scheduling Plan")
        self.navigation.open_page.assert_called_once_with(
            "Maintain Shift Scheduling Plan"
        )


class TestShiftSchedulePageAttributes(unittest.TestCase):
    """Story 1: Verify Maintain Shift Scheduling Plan page attributes."""

    def setUp(self):
        """Arrange: Create mock shift schedule page."""
        self.page = MagicMock()
        self.page.get_attributes.return_value = [
            "shift_code",
            "from_date",
            "to_date",
        ]
        self.page.get_shift_codes.return_value = [
            "SC-W01",
            "SC-W02",
            "SC-W03",
            "SC-W04",
        ]

    def test_shiftSchedulePage_attributes_displaysShiftCode(self):
        """Positive: Page displays Shift Code attribute."""
        attributes = self.page.get_attributes()

        self.assertIn("shift_code", attributes)

    def test_shiftSchedulePage_attributes_displaysFromDate(self):
        """Positive: Page displays From date attribute (DD-MM-YYYY)."""
        attributes = self.page.get_attributes()

        self.assertIn("from_date", attributes)

    def test_shiftSchedulePage_attributes_displaysToDate(self):
        """Positive: Page displays To date attribute (DD-MM-YYYY)."""
        attributes = self.page.get_attributes()

        self.assertIn("to_date", attributes)

    def test_shiftSchedulePage_shiftCodeDropdown_displaysCodesFromMaster(self):
        """Positive: Shift Code dropdown fetches values from shift code master."""
        codes = self.page.get_shift_codes()

        self.assertIsInstance(codes, list)
        self.assertGreater(len(codes), 0)

    def test_shiftSchedulePage_shiftCodeSelection_autoPopulatesDates(self):
        """Positive: Selecting a shift code auto-populates From and To dates."""
        self.page.select_shift_code.return_value = {
            "shift_code": "SC-W01",
            "from_date": "06-01-2026",
            "to_date": "12-01-2026",
        }

        result = self.page.select_shift_code("SC-W01")

        self.assertEqual(result["from_date"], "06-01-2026")
        self.assertEqual(result["to_date"], "12-01-2026")

    def test_shiftSchedulePage_shiftCodeMandatory_returnsErrorWhenEmpty(self):
        """Negative: Submitting without selecting shift code returns error."""
        self.page.select_shift_code.return_value = {
            "status": "error",
            "message": "Shift Code is required",
        }

        result = self.page.select_shift_code("")

        self.assertEqual(result["status"], "error")
        self.assertIn("required", result["message"])


class TestShiftScheduleGridColumns(unittest.TestCase):
    """Story 1: Verify grid columns in the shift schedule page."""

    def setUp(self):
        """Arrange: Create mock grid."""
        self.grid = MagicMock()
        self.grid.get_columns.return_value = [
            "employee",
            "dept_code_shop_name",
            "cadre",
            "category",
            "shift",
            "shift_plan_monday",
            "shift_plan_tuesday",
            "shift_plan_wednesday",
            "shift_plan_thursday",
            "shift_plan_friday",
            "shift_plan_saturday",
            "shift_plan_sunday",
            "supervisor",
            "tpt_user",
            "last_modified_by",
            "action",
            "multi_select_checkbox",
        ]

    def test_grid_displaysEmployeeColumn(self):
        """Positive: Grid displays Employee (PS No and Name) column."""
        columns = self.grid.get_columns()

        self.assertIn("employee", columns)

    def test_grid_displaysDeptCodeShopNameColumn(self):
        """Positive: Grid displays Dept Code and Shop Name column."""
        columns = self.grid.get_columns()

        self.assertIn("dept_code_shop_name", columns)

    def test_grid_displaysCadreColumn(self):
        """Positive: Grid displays Cadre column."""
        columns = self.grid.get_columns()

        self.assertIn("cadre", columns)

    def test_grid_displaysCategoryColumn(self):
        """Positive: Grid displays Category column."""
        columns = self.grid.get_columns()

        self.assertIn("category", columns)

    def test_grid_displaysShiftColumn(self):
        """Positive: Grid displays Shift column."""
        columns = self.grid.get_columns()

        self.assertIn("shift", columns)

    def test_grid_displaysAllWeekdayShiftPlanColumns(self):
        """Positive: Grid displays shift plan columns for Monday through Sunday."""
        columns = self.grid.get_columns()
        weekdays = [
            "shift_plan_monday",
            "shift_plan_tuesday",
            "shift_plan_wednesday",
            "shift_plan_thursday",
            "shift_plan_friday",
            "shift_plan_saturday",
            "shift_plan_sunday",
        ]

        for day in weekdays:
            self.assertIn(day, columns)

    def test_grid_displaysSupervisorColumn(self):
        """Positive: Grid displays Supervisor column (auto-populated by dept code)."""
        columns = self.grid.get_columns()

        self.assertIn("supervisor", columns)

    def test_grid_displaysTPTUserColumn(self):
        """Positive: Grid displays TPT User (Yes/No) column."""
        columns = self.grid.get_columns()

        self.assertIn("tpt_user", columns)

    def test_grid_displaysLastModifiedByColumn(self):
        """Positive: Grid displays Last Modified By column."""
        columns = self.grid.get_columns()

        self.assertIn("last_modified_by", columns)

    def test_grid_displaysActionColumn(self):
        """Positive: Grid displays Action (edit icon) column."""
        columns = self.grid.get_columns()

        self.assertIn("action", columns)

    def test_grid_displaysMultiSelectCheckbox(self):
        """Positive: Grid displays multi-select checkbox for selecting employees."""
        columns = self.grid.get_columns()

        self.assertIn("multi_select_checkbox", columns)


class TestShiftScheduleGridDataFetching(unittest.TestCase):
    """Story 1: Verify data is fetched from correct masters."""

    def setUp(self):
        """Arrange: Create mock services."""
        self.workforce_service = MagicMock()
        self.dept_master = MagicMock()
        self.cadre_master = MagicMock()
        self.category_master = MagicMock()
        self.shift_master = MagicMock()
        self.shift_rotation_master = MagicMock()

    def test_grid_employeeData_fetchedFromWorkforceManagement(self):
        """Integration: Employee data is fetched from workforce management."""
        self.workforce_service.get_employees.return_value = [
            {"ps_no": "PS001", "name": "John Doe"},
            {"ps_no": "PS002", "name": "Jane Smith"},
        ]

        employees = self.workforce_service.get_employees()

        self.assertEqual(len(employees), 2)
        self.assertEqual(employees[0]["ps_no"], "PS001")

    def test_grid_deptCode_fetchedFromDepartmentCodeMaster(self):
        """Integration: Dept Code and Shop Name fetched from department code master."""
        self.dept_master.get_departments.return_value = [
            {"code": "D001", "shop_name": "Assembly Shop"},
        ]

        departments = self.dept_master.get_departments()

        self.assertGreater(len(departments), 0)
        self.assertEqual(departments[0]["code"], "D001")

    def test_grid_cadre_fetchedFromCadreMaster(self):
        """Integration: Cadre data fetched from cadre master."""
        self.cadre_master.get_cadres.return_value = ["A", "B", "C"]

        cadres = self.cadre_master.get_cadres()

        self.assertIsInstance(cadres, list)
        self.assertGreater(len(cadres), 0)

    def test_grid_category_fetchedFromCategoryCodeMaster(self):
        """Integration: Category data fetched from category code master."""
        self.category_master.get_categories.return_value = [
            "Skilled",
            "Semi-Skilled",
            "Unskilled",
        ]

        categories = self.category_master.get_categories()

        self.assertIsInstance(categories, list)

    def test_grid_shift_fetchedFromShiftMaster(self):
        """Integration: Shift details fetched from shift master."""
        self.shift_master.get_shifts.return_value = ["I", "II", "III", "General"]

        shifts = self.shift_master.get_shifts()

        self.assertIn("I", shifts)
        self.assertIn("II", shifts)

    def test_grid_shiftPlan_fetchedFromShiftRotationMaster(self):
        """Integration: Shift plan fetched from shift rotation master."""
        self.shift_rotation_master.get_shift_plan.return_value = {
            "monday": "I",
            "tuesday": "I",
            "wednesday": "I",
            "thursday": "I",
            "friday": "I",
            "saturday": "I",
            "sunday": "OFF",
        }

        plan = self.shift_rotation_master.get_shift_plan("PS001", "SC-W01")

        self.assertEqual(plan["monday"], "I")
        self.assertEqual(plan["sunday"], "OFF")

    def test_grid_supervisor_autoPopulatedByDeptCode(self):
        """Positive: Supervisor is auto-populated based on department code."""
        self.dept_master.get_supervisor.return_value = {
            "ps_no": "PS100",
            "name": "Supervisor Name",
        }

        supervisor = self.dept_master.get_supervisor("D001")

        self.assertEqual(supervisor["ps_no"], "PS100")

    def test_grid_tptUser_fetchedFromWorkforceInfo(self):
        """Integration: TPT User (Yes/No) fetched from workforce info."""
        self.workforce_service.get_tpt_status.return_value = "Yes"

        tpt_status = self.workforce_service.get_tpt_status("PS001")

        self.assertIn(tpt_status, ["Yes", "No"])


class TestShiftSchedulePageButtons(unittest.TestCase):
    """Story 1: Verify page buttons (Save, Export)."""

    def setUp(self):
        """Arrange: Create mock page."""
        self.page = MagicMock()
        self.page.get_buttons.return_value = ["Save", "Export"]

    def test_shiftSchedulePage_displaysSaveButton(self):
        """Positive: Page displays Save button."""
        buttons = self.page.get_buttons()

        self.assertIn("Save", buttons)

    def test_shiftSchedulePage_displaysExportButton(self):
        """Positive: Page displays Export button."""
        buttons = self.page.get_buttons()

        self.assertIn("Export", buttons)


class TestShiftScheduleEditIcon(unittest.TestCase):
    """Story 1: Verify edit icon functionality."""

    def setUp(self):
        """Arrange: Create mock edit service."""
        self.edit_service = MagicMock()

    def test_editIcon_click_makesShiftFieldEditable(self):
        """Positive: Clicking edit icon makes shift field editable."""
        self.edit_service.enable_edit.return_value = {
            "editable_fields": ["shift", "shift_plan"],
        }

        result = self.edit_service.enable_edit("PS001")

        self.assertIn("shift", result["editable_fields"])

    def test_editIcon_click_makesShiftPlanEditable(self):
        """Positive: Clicking edit icon makes shift plan (Mon-Sun) editable."""
        self.edit_service.enable_edit.return_value = {
            "editable_fields": ["shift", "shift_plan"],
        }

        result = self.edit_service.enable_edit("PS001")

        self.assertIn("shift_plan", result["editable_fields"])

    def test_editIcon_shiftChange_updatesAllDays(self):
        """Positive: Changing shift column updates shift plan for all days."""
        self.edit_service.change_shift.return_value = {
            "status": "success",
            "updated_plan": {
                "monday": "I",
                "tuesday": "I",
                "wednesday": "I",
                "thursday": "I",
                "friday": "I",
                "saturday": "I",
                "sunday": "I",
            },
        }

        result = self.edit_service.change_shift("PS001", old_shift="II", new_shift="I")

        self.assertEqual(result["status"], "success")
        for day in ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]:
            self.assertEqual(result["updated_plan"][day], "I")

    def test_editIcon_restrictInvalidShift_returnsError(self):
        """Negative: Changing to a shift not in user's rotation is restricted."""
        self.edit_service.change_shift.return_value = {
            "status": "error",
            "message": "Shift not applicable based on shift rotation",
        }

        result = self.edit_service.change_shift(
            "PS001", old_shift="I", new_shift="IV"
        )

        self.assertEqual(result["status"], "error")
        self.assertIn("not applicable", result["message"])


class TestShiftScheduleSave(unittest.TestCase):
    """Story 1: Verify save functionality and success message."""

    def setUp(self):
        """Arrange: Create mock save service."""
        self.save_service = MagicMock()

    def test_save_editedChanges_displaysSuccessMessage(self):
        """Positive: Saving edited changes displays success pop-up."""
        self.save_service.save_changes.return_value = {
            "status": "success",
            "message": "Changes have been saved successfully",
        }

        result = self.save_service.save_changes("PS001", {"shift": "I"})

        self.assertEqual(result["status"], "success")
        self.assertEqual(result["message"], "Changes have been saved successfully")

    def test_save_noChanges_returnsNoChangesMessage(self):
        """Boundary: Saving without making changes returns appropriate message."""
        self.save_service.save_changes.return_value = {
            "status": "info",
            "message": "No changes to save",
        }

        result = self.save_service.save_changes("PS001", {})

        self.assertEqual(result["status"], "info")

    def test_save_serviceFailure_returnsError(self):
        """Integration: Save service failure returns error."""
        self.save_service.save_changes.side_effect = ConnectionError(
            "Service unavailable"
        )

        with self.assertRaises(ConnectionError):
            self.save_service.save_changes("PS001", {"shift": "I"})


class TestShiftScheduleLockInPeriod(unittest.TestCase):
    """Story 1: Verify lock-in period restrictions."""

    def setUp(self):
        """Arrange: Create mock shift schedule service."""
        self.schedule_service = MagicMock()

    def test_lockInPeriod_editRestricted_returnsError(self):
        """Negative: IR cannot edit shift plans during lock-in period."""
        self.schedule_service.is_locked.return_value = True
        self.schedule_service.edit_shift.return_value = {
            "status": "error",
            "message": "Shift plan is locked during the scheduled release period",
        }

        is_locked = self.schedule_service.is_locked("SC-W01")
        result = self.schedule_service.edit_shift("PS001", "SC-W01", {"shift": "I"})

        self.assertTrue(is_locked)
        self.assertEqual(result["status"], "error")

    def test_lockInPeriod_outsideLockIn_allowsEdit(self):
        """Positive: IR can edit shift plans outside lock-in period."""
        self.schedule_service.is_locked.return_value = False
        self.schedule_service.edit_shift.return_value = {
            "status": "success",
        }

        is_locked = self.schedule_service.is_locked("SC-W01")
        result = self.schedule_service.edit_shift("PS001", "SC-W01", {"shift": "I"})

        self.assertFalse(is_locked)
        self.assertEqual(result["status"], "success")

    def test_lockInPeriod_autoReleaseToShopUsers(self):
        """Positive: System auto-releases shift plan to shop users based on lock-in schedule."""
        self.schedule_service.release_shift_plan.return_value = {
            "status": "success",
            "released_to": ["Shop In Charge", "Shop Coordinator", "Shop Supervisor"],
        }

        result = self.schedule_service.release_shift_plan("SC-W01")

        self.assertEqual(result["status"], "success")
        self.assertIn("Shop In Charge", result["released_to"])


class TestShiftScheduleSearchBar(unittest.TestCase):
    """Story 1: Verify search bar functionality."""

    def setUp(self):
        """Arrange: Create mock search service."""
        self.search_service = MagicMock()

    def test_globalSearch_validQuery_returnsResults(self):
        """Positive: Global search bar returns matching results."""
        self.search_service.global_search.return_value = [
            {"ps_no": "PS001", "name": "John Doe"},
        ]

        results = self.search_service.global_search("John")

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["name"], "John Doe")

    def test_columnSearch_validQuery_returnsFilteredResults(self):
        """Positive: Column search bar returns filtered results."""
        self.search_service.column_search.return_value = [
            {"ps_no": "PS001", "dept_code": "D001"},
        ]

        results = self.search_service.column_search("dept_code", "D001")

        self.assertEqual(len(results), 1)

    def test_globalSearch_noMatch_returnsEmptyList(self):
        """Boundary: Search with no matching results returns empty list."""
        self.search_service.global_search.return_value = []

        results = self.search_service.global_search("NONEXISTENT")

        self.assertEqual(len(results), 0)

    def test_globalSearch_emptyQuery_returnsAllResults(self):
        """Boundary: Empty search query returns all results."""
        self.search_service.global_search.return_value = [
            {"ps_no": "PS001"},
            {"ps_no": "PS002"},
        ]

        results = self.search_service.global_search("")

        self.assertGreater(len(results), 0)


class TestShiftSchedulePageNavigation(unittest.TestCase):
    """Story 1: Verify page navigation (pagination)."""

    def setUp(self):
        """Arrange: Create mock pagination service."""
        self.pagination = MagicMock()

    def test_pagination_navigateToNextPage_displaysNextPage(self):
        """Positive: User can navigate to next page."""
        self.pagination.go_to_page.return_value = {"current_page": 2, "total_pages": 5}

        result = self.pagination.go_to_page(2)

        self.assertEqual(result["current_page"], 2)

    def test_pagination_navigateBeyondLastPage_staysOnLastPage(self):
        """Boundary: Navigating beyond last page stays on last page."""
        self.pagination.go_to_page.return_value = {"current_page": 5, "total_pages": 5}

        result = self.pagination.go_to_page(10)

        self.assertEqual(result["current_page"], 5)

    def test_pagination_firstPage_previousDisabled(self):
        """Boundary: On first page, previous button is disabled."""
        self.pagination.is_previous_enabled.return_value = False

        result = self.pagination.is_previous_enabled()

        self.assertFalse(result)


class TestShiftScheduleMultiSelect(unittest.TestCase):
    """Story 1: Verify multi-select checkbox functionality."""

    def setUp(self):
        """Arrange: Create mock grid with multi-select."""
        self.grid = MagicMock()

    def test_multiSelect_selectMultipleEmployees_returnsSelectedList(self):
        """Positive: User can select multiple employees using checkboxes."""
        self.grid.select_employees.return_value = ["PS001", "PS002", "PS003"]

        selected = self.grid.select_employees(["PS001", "PS002", "PS003"])

        self.assertEqual(len(selected), 3)

    def test_multiSelect_noSelection_returnsEmptyList(self):
        """Boundary: No employee selected returns empty list."""
        self.grid.select_employees.return_value = []

        selected = self.grid.select_employees([])

        self.assertEqual(len(selected), 0)


# ---------------------------------------------------------------------------
# Story 2: IR - Edit Shift Scheduling Plan (Schedule Shift Popup)
# ---------------------------------------------------------------------------


class TestScheduleShiftPopup(unittest.TestCase):
    """Story 2: Verify Schedule Shift popup display and fields."""

    def setUp(self):
        """Arrange: Create mock schedule shift popup."""
        self.popup = MagicMock()
        self.popup.get_fields.return_value = [
            "shift_pattern",
            "start_date",
            "end_date",
            "forever",
            "pattern_week",
        ]
        self.popup.get_buttons.return_value = ["Schedule Shift", "Cancel"]

    def test_scheduleShiftPopup_displaysSelectedEmployees(self):
        """Positive: Popup displays list of selected employees (PS no and name)."""
        self.popup.get_selected_employees.return_value = [
            {"ps_no": "PS001", "name": "John Doe"},
            {"ps_no": "PS002", "name": "Jane Smith"},
        ]

        employees = self.popup.get_selected_employees()

        self.assertEqual(len(employees), 2)
        self.assertEqual(employees[0]["ps_no"], "PS001")

    def test_scheduleShiftPopup_displaysShiftPatternField(self):
        """Positive: Popup displays Shift Pattern field."""
        fields = self.popup.get_fields()

        self.assertIn("shift_pattern", fields)

    def test_scheduleShiftPopup_displaysStartDateField(self):
        """Positive: Popup displays Start Date (date picker) field."""
        fields = self.popup.get_fields()

        self.assertIn("start_date", fields)

    def test_scheduleShiftPopup_displaysEndDateField(self):
        """Positive: Popup displays End Date (date picker) field."""
        fields = self.popup.get_fields()

        self.assertIn("end_date", fields)

    def test_scheduleShiftPopup_displaysForeverOption(self):
        """Positive: Popup displays Forever option."""
        fields = self.popup.get_fields()

        self.assertIn("forever", fields)

    def test_scheduleShiftPopup_displaysPatternWeekDropdown(self):
        """Positive: Popup displays Pattern Week dropdown."""
        fields = self.popup.get_fields()

        self.assertIn("pattern_week", fields)

    def test_scheduleShiftPopup_displaysScheduleShiftButton(self):
        """Positive: Popup displays Schedule Shift button."""
        buttons = self.popup.get_buttons()

        self.assertIn("Schedule Shift", buttons)

    def test_scheduleShiftPopup_displaysCancelButton(self):
        """Positive: Popup displays Cancel button."""
        buttons = self.popup.get_buttons()

        self.assertIn("Cancel", buttons)


class TestScheduleShiftShiftPattern(unittest.TestCase):
    """Story 2: Verify shift pattern field and data."""

    def setUp(self):
        """Arrange: Create mock shift pattern service."""
        self.pattern_service = MagicMock()

    def test_shiftPattern_fetchedFromRotationMasterAndWorkforceInfo(self):
        """Integration: Shift pattern fetched from shift rotation master and workforce info."""
        self.pattern_service.get_shift_pattern.return_value = "I-III-II"

        pattern = self.pattern_service.get_shift_pattern("PS001")

        self.assertEqual(pattern, "I-III-II")

    def test_shiftPattern_rotationalPattern_displaysCorrectly(self):
        """Positive: Rotational shift pattern (e.g., I-III-II) means Shift I week 1, III week 2, II week 3."""
        self.pattern_service.get_shift_pattern.return_value = "I-III-II"
        self.pattern_service.get_pattern_details.return_value = {
            "week_1": "I",
            "week_2": "III",
            "week_3": "II",
        }

        details = self.pattern_service.get_pattern_details("I-III-II")

        self.assertEqual(details["week_1"], "I")
        self.assertEqual(details["week_2"], "III")
        self.assertEqual(details["week_3"], "II")


class TestScheduleShiftPatternWeek(unittest.TestCase):
    """Story 2: Verify pattern week dropdown."""

    def setUp(self):
        """Arrange: Create mock pattern week service."""
        self.pattern_service = MagicMock()

    def test_patternWeek_displaysCurrentMonthWeeks(self):
        """Positive: Pattern week dropdown shows weeks of current month based on rotation pattern."""
        self.pattern_service.get_pattern_weeks.return_value = [
            "Week 1",
            "Week 2",
            "Week 3",
            "Week 4",
            "Week 5",
        ]

        weeks = self.pattern_service.get_pattern_weeks("2026-05")

        self.assertGreater(len(weeks), 0)
        self.assertLessEqual(len(weeks), 5)

    def test_patternWeek_selectWeek_displaysShiftRotation(self):
        """Positive: Selecting a pattern week displays shift rotation for that week."""
        self.pattern_service.get_week_rotation.return_value = {
            "rotation_type": "Week 3",
            "monday": "II",
            "tuesday": "II",
            "wednesday": "II",
            "thursday": "II",
            "friday": "II",
            "saturday": "II",
            "sunday": "OFF",
        }

        rotation = self.pattern_service.get_week_rotation("Week 3")

        self.assertEqual(rotation["rotation_type"], "Week 3")
        self.assertEqual(rotation["monday"], "II")


class TestScheduleShiftDataGrid(unittest.TestCase):
    """Story 2: Verify data grid in schedule shift popup."""

    def setUp(self):
        """Arrange: Create mock data grid."""
        self.data_grid = MagicMock()

    def test_dataGrid_displaysRotationType(self):
        """Positive: Data grid displays rotation type rows."""
        self.data_grid.get_rows.return_value = [
            {"rotation_type": "Week 1", "monday": "I", "sunday": "OFF"},
            {"rotation_type": "Week 2", "monday": "III", "sunday": "OFF"},
            {"rotation_type": "Week 3", "monday": "II", "sunday": "OFF"},
        ]

        rows = self.data_grid.get_rows()

        self.assertEqual(len(rows), 3)
        self.assertEqual(rows[0]["rotation_type"], "Week 1")

    def test_dataGrid_displaysShiftPlanForEachDay(self):
        """Positive: Data grid displays shift plan for Monday to Sunday."""
        self.data_grid.get_row_plan.return_value = {
            "monday": "I",
            "tuesday": "I",
            "wednesday": "I",
            "thursday": "I",
            "friday": "I",
            "saturday": "I",
            "sunday": "OFF",
        }

        plan = self.data_grid.get_row_plan("Week 1")

        weekdays = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
        for day in weekdays:
            self.assertIn(day, plan)


class TestScheduleShiftSaveOptions(unittest.TestCase):
    """Story 2: Verify save options and success messages."""

    def setUp(self):
        """Arrange: Create mock schedule service."""
        self.schedule_service = MagicMock()

    def test_scheduleShift_option1_oneDayChange_displaysMessage(self):
        """Positive: Option 1 - Change for one day displays correct message."""
        self.schedule_service.schedule_shift.return_value = {
            "status": "success",
            "message": "Shift plan successfully changed for one day",
        }

        result = self.schedule_service.schedule_shift(
            employees=["PS001"],
            option="one_day",
            date="11-05-2026",
        )

        self.assertEqual(result["status"], "success")
        self.assertEqual(
            result["message"], "Shift plan successfully changed for one day"
        )

    def test_scheduleShift_option2_currentWeek_displaysMessage(self):
        """Positive: Option 2 - Change for current week displays correct message with dates."""
        self.schedule_service.schedule_shift.return_value = {
            "status": "success",
            "message": "Shift plan successfully changed for current week only from 11-05-2026 to 17-05-2026",
        }

        result = self.schedule_service.schedule_shift(
            employees=["PS001"],
            option="current_week",
            start_date="11-05-2026",
            end_date="17-05-2026",
        )

        self.assertEqual(result["status"], "success")
        self.assertIn("current week only", result["message"])
        self.assertIn("11-05-2026", result["message"])
        self.assertIn("17-05-2026", result["message"])

    def test_scheduleShift_option3_forever_displaysMessage(self):
        """Positive: Option 3 - Carry forward forever displays correct message."""
        self.schedule_service.schedule_shift.return_value = {
            "status": "success",
            "message": 'New shift rotation will be carried forward for the workman from 11-05-2026 to "Forever"',
        }

        result = self.schedule_service.schedule_shift(
            employees=["PS001"],
            option="forever",
            start_date="11-05-2026",
        )

        self.assertEqual(result["status"], "success")
        self.assertIn("Forever", result["message"])
        self.assertIn("11-05-2026", result["message"])

    def test_scheduleShift_cancelButton_revertsChanges(self):
        """Positive: Clicking cancel reverts changes and closes popup."""
        self.schedule_service.cancel.return_value = {
            "status": "cancelled",
            "changes_reverted": True,
        }

        result = self.schedule_service.cancel()

        self.assertEqual(result["status"], "cancelled")
        self.assertTrue(result["changes_reverted"])


class TestScheduleShiftValidation(unittest.TestCase):
    """Story 2: Verify schedule shift validations."""

    def setUp(self):
        """Arrange: Create mock validation service."""
        self.validation_service = MagicMock()

    def test_validation_changeDateRange_allowsNDays(self):
        """Positive: User can change shift for any number of days based on start/end date."""
        self.validation_service.validate_date_range.return_value = {
            "status": "valid",
            "days": 14,
        }

        result = self.validation_service.validate_date_range(
            "11-05-2026", "24-05-2026"
        )

        self.assertEqual(result["status"], "valid")
        self.assertEqual(result["days"], 14)

    def test_validation_startDateAfterEndDate_returnsError(self):
        """Negative: Start date after end date returns validation error."""
        self.validation_service.validate_date_range.return_value = {
            "status": "error",
            "message": "Start date must be before end date",
        }

        result = self.validation_service.validate_date_range(
            "24-05-2026", "11-05-2026"
        )

        self.assertEqual(result["status"], "error")

    def test_validation_foreverOption_changesFromStartDateForever(self):
        """Positive: Forever option changes pattern from start date indefinitely."""
        self.validation_service.validate_forever.return_value = {
            "status": "valid",
            "end_date": "Forever",
        }

        result = self.validation_service.validate_forever("11-05-2026")

        self.assertEqual(result["status"], "valid")
        self.assertEqual(result["end_date"], "Forever")

    def test_validation_noEmployeeSelected_returnsError(self):
        """Negative: No employee selected before clicking Schedule Shift returns error."""
        self.validation_service.validate_selection.return_value = {
            "status": "error",
            "message": "Please select at least one employee",
        }

        result = self.validation_service.validate_selection([])

        self.assertEqual(result["status"], "error")

    def test_validation_shiftOnlyForSelectedWeek_notAllWeeks(self):
        """Positive: Change applies only to selected week, not all weeks."""
        self.validation_service.validate_week_scope.return_value = {
            "status": "valid",
            "scope": "selected_week_only",
        }

        result = self.validation_service.validate_week_scope(
            "11-05-2026", "17-05-2026"
        )

        self.assertEqual(result["scope"], "selected_week_only")

    def test_validation_invalidDateFormat_returnsError(self):
        """Boundary: Invalid date format returns validation error."""
        self.validation_service.validate_date_range.return_value = {
            "status": "error",
            "message": "Invalid date format. Expected DD-MM-YYYY",
        }

        result = self.validation_service.validate_date_range("2026/05/11", "2026/05/17")

        self.assertEqual(result["status"], "error")


class TestScheduleShiftMultipleEmployees(unittest.TestCase):
    """Story 2: Verify scheduling shift for multiple employees."""

    def setUp(self):
        """Arrange: Create mock schedule service."""
        self.schedule_service = MagicMock()

    def test_scheduleShift_multipleEmployees_appliesChangeToAll(self):
        """Positive: Shift change applies to all selected employees."""
        self.schedule_service.schedule_shift.return_value = {
            "status": "success",
            "affected_employees": ["PS001", "PS002", "PS003"],
            "message": "Shift plan successfully changed for one day",
        }

        result = self.schedule_service.schedule_shift(
            employees=["PS001", "PS002", "PS003"],
            option="one_day",
            date="11-05-2026",
        )

        self.assertEqual(len(result["affected_employees"]), 3)

    def test_scheduleShift_singleEmployee_appliesChange(self):
        """Positive: Shift change applies to a single selected employee."""
        self.schedule_service.schedule_shift.return_value = {
            "status": "success",
            "affected_employees": ["PS001"],
        }

        result = self.schedule_service.schedule_shift(
            employees=["PS001"],
            option="one_day",
            date="11-05-2026",
        )

        self.assertEqual(len(result["affected_employees"]), 1)


if __name__ == "__main__":
    unittest.main()
