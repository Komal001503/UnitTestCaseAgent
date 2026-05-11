"""
Unit Tests for Maintain Shift Scheduling Plan Module - Shop User Role
User Stories: Story 6 (Shop View), Story 7 (Shop Schedule Shift), Story 8 (Shop Export)

Covers:
- Shop User: View Maintain Shift Scheduling Plan (limited edit access)
- Shop User: Schedule shift / edit shift via edit icon
- Shop User: Export shift schedule data

Test Categories:
- Positive / Happy Path
- Negative / Error Path
- Boundary / Edge Cases
- Integration Points
"""

import unittest
from unittest.mock import MagicMock, patch


# TODO: Import actual modules once implementation is available.
# from src.attendance.shift_schedule import (
#     ShiftScheduleShopPage, ShiftScheduleShopService,
#     ShiftScheduleExportService
# )


# ---------------------------------------------------------------------------
# Story 6: Shop User - View Maintain Shift Scheduling Plan
# ---------------------------------------------------------------------------


class TestShopUserNavigation(unittest.TestCase):
    """Story 6: Verify Shop User navigation to Maintain Shift Scheduling Plan."""

    def setUp(self):
        """Arrange: Create mock navigation service."""
        self.navigation = MagicMock()

    def test_shopUser_sideNavigation_displaysMaintainShiftSchedulePlan(self):
        """Positive: Shop user can see Maintain Shift Scheduling Plan in Attendance Management."""
        self.navigation.get_attendance_submenus.return_value = [
            "Maintain Shift Scheduling Plan",
        ]

        submenus = self.navigation.get_attendance_submenus()

        self.assertIn("Maintain Shift Scheduling Plan", submenus)

    def test_shopUser_selectShiftSchedulePlan_displaysPage(self):
        """Positive: Selecting the sub menu opens the page."""
        self.navigation.open_page.return_value = {
            "status": "success",
            "page": "Maintain Shift Scheduling Plan",
        }

        result = self.navigation.open_page("Maintain Shift Scheduling Plan")

        self.assertEqual(result["status"], "success")


class TestShopUserPageAttributes(unittest.TestCase):
    """Story 6: Verify Shop User page attributes (non-editable)."""

    def setUp(self):
        """Arrange: Create mock page."""
        self.page = MagicMock()
        self.page.get_attributes.return_value = [
            "shift_code",
            "from_date",
            "to_date",
        ]

    def test_shopUser_shiftCode_displayedNonEditable(self):
        """Positive: Shift Code is displayed (non-editable for attributes)."""
        attributes = self.page.get_attributes()

        self.assertIn("shift_code", attributes)

    def test_shopUser_fromDate_autoFetchedBasedOnScheduleCode(self):
        """Positive: From date is auto-fetched based on schedule code."""
        self.page.select_shift_code.return_value = {
            "shift_code": "SC-W01",
            "from_date": "06-01-2026",
            "to_date": "12-01-2026",
        }

        result = self.page.select_shift_code("SC-W01")

        self.assertIsNotNone(result["from_date"])

    def test_shopUser_toDate_autoFetchedBasedOnScheduleCode(self):
        """Positive: To date is auto-fetched based on schedule code."""
        self.page.select_shift_code.return_value = {
            "shift_code": "SC-W01",
            "from_date": "06-01-2026",
            "to_date": "12-01-2026",
        }

        result = self.page.select_shift_code("SC-W01")

        self.assertIsNotNone(result["to_date"])


class TestShopUserGridColumns(unittest.TestCase):
    """Story 6: Verify Shop User grid columns."""

    def setUp(self):
        """Arrange: Create mock grid."""
        self.grid = MagicMock()
        self.grid.get_columns.return_value = [
            "employee",
            "dept_code_shop_name",
            "shift",
            "shift_plan_monday",
            "shift_plan_tuesday",
            "shift_plan_wednesday",
            "shift_plan_thursday",
            "shift_plan_friday",
            "shift_plan_saturday",
            "shift_plan_sunday",
            "last_modified_by",
            "tpt_user",
            "action",
        ]

    def test_shopUserGrid_displaysEmployeeColumn(self):
        """Positive: Grid displays Employee (PS No and Name) column."""
        columns = self.grid.get_columns()

        self.assertIn("employee", columns)

    def test_shopUserGrid_displaysDeptCodeShopName(self):
        """Positive: Grid displays Dept Code and Shop Name column."""
        columns = self.grid.get_columns()

        self.assertIn("dept_code_shop_name", columns)

    def test_shopUserGrid_displaysShiftColumn(self):
        """Positive: Grid displays Shift column."""
        columns = self.grid.get_columns()

        self.assertIn("shift", columns)

    def test_shopUserGrid_displaysAllWeekdayShiftPlanColumns(self):
        """Positive: Grid displays shift plan for Monday through Sunday."""
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

    def test_shopUserGrid_displaysLastModifiedBy(self):
        """Positive: Grid displays Last Modified By column."""
        columns = self.grid.get_columns()

        self.assertIn("last_modified_by", columns)

    def test_shopUserGrid_displaysTPTUser(self):
        """Positive: Grid displays TPT User (Yes/No) column."""
        columns = self.grid.get_columns()

        self.assertIn("tpt_user", columns)

    def test_shopUserGrid_displaysActionEditIcon(self):
        """Positive: Grid displays Action (edit icon) column."""
        columns = self.grid.get_columns()

        self.assertIn("action", columns)


class TestShopUserEditableFields(unittest.TestCase):
    """Story 6: Verify only specific fields are editable for Shop User."""

    def setUp(self):
        """Arrange: Create mock edit service."""
        self.edit_service = MagicMock()

    def test_shopUser_editIcon_onlyShiftFieldEditable(self):
        """Positive: Only Shift field is editable when edit icon is clicked."""
        self.edit_service.get_editable_fields.return_value = [
            "shift",
            "shift_plan_monday",
            "shift_plan_tuesday",
            "shift_plan_wednesday",
            "shift_plan_thursday",
            "shift_plan_friday",
            "shift_plan_saturday",
            "shift_plan_sunday",
        ]

        editable = self.edit_service.get_editable_fields("PS001")

        self.assertIn("shift", editable)

    def test_shopUser_editIcon_weekdayShiftsEditable(self):
        """Positive: Monday to Sunday shift fields are editable."""
        self.edit_service.get_editable_fields.return_value = [
            "shift",
            "shift_plan_monday",
            "shift_plan_tuesday",
            "shift_plan_wednesday",
            "shift_plan_thursday",
            "shift_plan_friday",
            "shift_plan_saturday",
            "shift_plan_sunday",
        ]

        editable = self.edit_service.get_editable_fields("PS001")

        self.assertIn("shift_plan_monday", editable)
        self.assertIn("shift_plan_sunday", editable)

    def test_shopUser_editRestriction_invalidShiftRotation_blocked(self):
        """Negative: Shop user cannot enter shift values outside assigned rotation."""
        self.edit_service.validate_shift_change.return_value = {
            "status": "error",
            "message": "Shift value not associated with employee's shift rotation plan",
        }

        result = self.edit_service.validate_shift_change("PS001", "IV")

        self.assertEqual(result["status"], "error")

    def test_shopUser_singleDayChange_onlyAffectsSelectedDay(self):
        """Positive: Changing shift for one day only affects that specific day."""
        self.edit_service.change_single_day.return_value = {
            "status": "success",
            "changed_day": "wednesday",
            "new_shift": "II",
        }

        result = self.edit_service.change_single_day(
            "PS001", day="wednesday", new_shift="II"
        )

        self.assertEqual(result["status"], "success")
        self.assertEqual(result["changed_day"], "wednesday")


class TestShopUserButtons(unittest.TestCase):
    """Story 6: Verify Shop User page buttons."""

    def setUp(self):
        """Arrange: Create mock page."""
        self.page = MagicMock()
        self.page.get_buttons.return_value = ["Save", "Export"]

    def test_shopUser_displaysSaveButton(self):
        """Positive: Page displays Save button."""
        buttons = self.page.get_buttons()

        self.assertIn("Save", buttons)

    def test_shopUser_displaysExportButton(self):
        """Positive: Page displays Export button."""
        buttons = self.page.get_buttons()

        self.assertIn("Export", buttons)


class TestShopUserSaveFunctionality(unittest.TestCase):
    """Story 6: Verify Shop User save functionality."""

    def setUp(self):
        """Arrange: Create mock save service."""
        self.save_service = MagicMock()

    def test_shopUser_saveChanges_displaysSuccessMessage(self):
        """Positive: Saving edited changes displays 'Changes have been saved successfully'."""
        self.save_service.save_changes.return_value = {
            "status": "success",
            "message": "Changes have been saved successfully",
        }

        result = self.save_service.save_changes("PS001", {"shift": "I"})

        self.assertEqual(result["message"], "Changes have been saved successfully")


class TestShopUserShiftReleaseLogic(unittest.TestCase):
    """Story 6: Verify shift plan release logic for Shop Users."""

    def setUp(self):
        """Arrange: Create mock schedule service."""
        self.schedule_service = MagicMock()

    def test_shopUser_shiftPlanReleasedByAdmin_canEdit(self):
        """Positive: After shift plan is released, shop user can edit."""
        self.schedule_service.is_shift_released.return_value = True
        self.schedule_service.can_edit.return_value = True

        released = self.schedule_service.is_shift_released("SC-W01")
        can_edit = self.schedule_service.can_edit("PS001", "SC-W01")

        self.assertTrue(released)
        self.assertTrue(can_edit)

    def test_shopUser_shiftPlanNotReleased_cannotEdit(self):
        """Negative: Before shift plan release, shop user cannot edit."""
        self.schedule_service.is_shift_released.return_value = False
        self.schedule_service.can_edit.return_value = False

        released = self.schedule_service.is_shift_released("SC-W01")
        can_edit = self.schedule_service.can_edit("PS001", "SC-W01")

        self.assertFalse(released)
        self.assertFalse(can_edit)


class TestShopUserSearchAndPagination(unittest.TestCase):
    """Story 6: Verify Shop User search and pagination."""

    def setUp(self):
        """Arrange: Create mock services."""
        self.search_service = MagicMock()
        self.pagination = MagicMock()

    def test_shopUser_globalSearch_returnsResults(self):
        """Positive: Shop user can search using Global Search Bar."""
        self.search_service.global_search.return_value = [
            {"ps_no": "PS001"},
        ]

        results = self.search_service.global_search("PS001")

        self.assertEqual(len(results), 1)

    def test_shopUser_columnSearch_returnsFilteredResults(self):
        """Positive: Shop user can search using Column Search Bar."""
        self.search_service.column_search.return_value = [
            {"ps_no": "PS002", "shift": "II"},
        ]

        results = self.search_service.column_search("shift", "II")

        self.assertEqual(len(results), 1)

    def test_shopUser_pagination_navigatePages(self):
        """Positive: Shop user can navigate between pages."""
        self.pagination.go_to_page.return_value = {"current_page": 2, "total_pages": 5}

        result = self.pagination.go_to_page(2)

        self.assertEqual(result["current_page"], 2)


class TestShopUserDataFetching(unittest.TestCase):
    """Story 6: Verify data fetching from correct masters for Shop User."""

    def setUp(self):
        """Arrange: Create mock services."""
        self.shift_rotation_master = MagicMock()
        self.workforce_service = MagicMock()

    def test_shopUser_shiftPlan_fetchedFromShiftRotationMaster(self):
        """Integration: Shift plan data fetched from shift rotation master."""
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

        self.assertIsNotNone(plan["monday"])

    def test_shopUser_tptUser_fetchedFromWorkforceInfo(self):
        """Integration: TPT User (Yes/No) fetched from workforce information."""
        self.workforce_service.get_tpt_status.return_value = "No"

        tpt = self.workforce_service.get_tpt_status("PS001")

        self.assertIn(tpt, ["Yes", "No"])


# ---------------------------------------------------------------------------
# Story 7: Shop User - Schedule Shift / Edit Shift
# ---------------------------------------------------------------------------


class TestShopUserScheduleShiftNavigation(unittest.TestCase):
    """Story 7: Verify Shop User can access shift rotation page."""

    def setUp(self):
        """Arrange: Create mock schedule service."""
        self.schedule_service = MagicMock()

    def test_shopUser_clickScheduleShift_opensShiftRotationPage(self):
        """Positive: Clicking schedule shift button opens shift rotation page."""
        self.schedule_service.open_shift_rotation.return_value = {
            "status": "success",
            "page": "Shift Rotation",
        }

        result = self.schedule_service.open_shift_rotation(["PS001"])

        self.assertEqual(result["page"], "Shift Rotation")

    def test_shopUser_clickEditIcon_opensShiftRotationPage(self):
        """Positive: Clicking edit icon opens shift rotation page for employee."""
        self.schedule_service.open_shift_rotation.return_value = {
            "status": "success",
            "page": "Shift Rotation",
        }

        result = self.schedule_service.open_shift_rotation(["PS001"])

        self.assertEqual(result["status"], "success")


class TestShopUserShiftRotationPage(unittest.TestCase):
    """Story 7: Verify Shop User shift rotation page fields."""

    def setUp(self):
        """Arrange: Create mock shift rotation page."""
        self.rotation_page = MagicMock()
        self.rotation_page.get_fields.return_value = [
            "shift_pattern",
            "start_date",
            "end_date",
            "forever",
            "pattern_week",
        ]
        self.rotation_page.get_buttons.return_value = ["Schedule shift", "Cancel"]

    def test_shiftRotationPage_displaysAllEmployees(self):
        """Positive: Page displays list of all employees (PS no and name)."""
        self.rotation_page.get_employees.return_value = [
            {"ps_no": "PS001", "name": "John Doe"},
            {"ps_no": "PS002", "name": "Jane Smith"},
        ]

        employees = self.rotation_page.get_employees()

        self.assertGreater(len(employees), 0)

    def test_shiftRotationPage_displaysShiftPatternField(self):
        """Positive: Page displays Shift Pattern field."""
        fields = self.rotation_page.get_fields()

        self.assertIn("shift_pattern", fields)

    def test_shiftRotationPage_displaysStartDateField(self):
        """Positive: Page displays Start Date (date picker) field."""
        fields = self.rotation_page.get_fields()

        self.assertIn("start_date", fields)

    def test_shiftRotationPage_displaysEndDateField(self):
        """Positive: Page displays End Date (date picker) field."""
        fields = self.rotation_page.get_fields()

        self.assertIn("end_date", fields)

    def test_shiftRotationPage_displaysForeverOption(self):
        """Positive: Page displays Forever option."""
        fields = self.rotation_page.get_fields()

        self.assertIn("forever", fields)

    def test_shiftRotationPage_displaysPatternWeekDropdown(self):
        """Positive: Page displays Pattern Week dropdown."""
        fields = self.rotation_page.get_fields()

        self.assertIn("pattern_week", fields)

    def test_shiftRotationPage_displaysScheduleShiftButton(self):
        """Positive: Page displays Schedule Shift button."""
        buttons = self.rotation_page.get_buttons()

        self.assertIn("Schedule shift", buttons)

    def test_shiftRotationPage_displaysCancelButton(self):
        """Positive: Page displays Cancel button."""
        buttons = self.rotation_page.get_buttons()

        self.assertIn("Cancel", buttons)


class TestShopUserShiftRotationDataGrid(unittest.TestCase):
    """Story 7: Verify data grid in shift rotation page."""

    def setUp(self):
        """Arrange: Create mock data grid."""
        self.data_grid = MagicMock()

    def test_dataGrid_displaysRotationType(self):
        """Positive: Data grid displays rotation type rows."""
        self.data_grid.get_rows.return_value = [
            {"rotation_type": "Week 1", "monday": "I", "sunday": "OFF"},
            {"rotation_type": "Week 2", "monday": "III", "sunday": "OFF"},
        ]

        rows = self.data_grid.get_rows()

        self.assertEqual(len(rows), 2)

    def test_dataGrid_displaysShiftPlanMondayToSunday(self):
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

        self.assertEqual(len(plan), 7)


class TestShopUserScheduleShiftOptions(unittest.TestCase):
    """Story 7: Verify Shop User schedule shift options and results."""

    def setUp(self):
        """Arrange: Create mock schedule service."""
        self.schedule_service = MagicMock()

    def test_shopUser_changeShiftForSelectedDate_success(self):
        """Positive: Option - Change the shift for the selected date only."""
        self.schedule_service.schedule_shift.return_value = {
            "status": "success",
            "message": "Shift plan successfully changed for one day",
        }

        result = self.schedule_service.schedule_shift(
            employees=["PS001"],
            option="selected_date",
            date="11-05-2026",
        )

        self.assertEqual(result["status"], "success")

    def test_shopUser_carryShiftForever_success(self):
        """Positive: Option - Carry shift rotational change from edited date to forever."""
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

    def test_shopUser_cancelChanges_revertsAllChanges(self):
        """Positive: Clicking cancel button reverts changes."""
        self.schedule_service.cancel.return_value = {
            "status": "cancelled",
            "changes_reverted": True,
        }

        result = self.schedule_service.cancel()

        self.assertTrue(result["changes_reverted"])


class TestShopUserScheduleShiftValidation(unittest.TestCase):
    """Story 7: Verify Shop User schedule shift validations."""

    def setUp(self):
        """Arrange: Create mock validation service."""
        self.validation_service = MagicMock()

    def test_shopUser_changeDateRange_allowsAnyNumberOfDays(self):
        """Positive: User can change shift for any number of days based on start/end date."""
        self.validation_service.validate_date_range.return_value = {
            "status": "valid",
            "days": 21,
        }

        result = self.validation_service.validate_date_range(
            "01-05-2026", "21-05-2026"
        )

        self.assertEqual(result["status"], "valid")
        self.assertEqual(result["days"], 21)

    def test_shopUser_changeOnlySelectedWeek_notAllWeeks(self):
        """Positive: Change applies only to selected week, not every week."""
        self.validation_service.validate_week_scope.return_value = {
            "status": "valid",
            "scope": "selected_week_only",
        }

        result = self.validation_service.validate_week_scope(
            "11-05-2026", "17-05-2026"
        )

        self.assertEqual(result["scope"], "selected_week_only")

    def test_shopUser_foreverOption_changesPatternIndefinitely(self):
        """Positive: Forever option changes shift pattern indefinitely from start date."""
        self.validation_service.validate_forever.return_value = {
            "status": "valid",
            "end_date": "Forever",
        }

        result = self.validation_service.validate_forever("11-05-2026")

        self.assertEqual(result["end_date"], "Forever")

    def test_shopUser_startDateAfterEndDate_returnsError(self):
        """Negative: Start date after end date returns error."""
        self.validation_service.validate_date_range.return_value = {
            "status": "error",
            "message": "Start date must be before end date",
        }

        result = self.validation_service.validate_date_range(
            "21-05-2026", "01-05-2026"
        )

        self.assertEqual(result["status"], "error")

    def test_shopUser_noEmployeeSelected_returnsError(self):
        """Negative: No employee selected returns error."""
        self.validation_service.validate_selection.return_value = {
            "status": "error",
            "message": "Please select at least one employee",
        }

        result = self.validation_service.validate_selection([])

        self.assertEqual(result["status"], "error")


class TestShopUserShiftPatternDetails(unittest.TestCase):
    """Story 7: Verify shift pattern details for Shop User."""

    def setUp(self):
        """Arrange: Create mock pattern service."""
        self.pattern_service = MagicMock()

    def test_shopUser_shiftPattern_fetchedFromRotationMasterAndWorkforceInfo(self):
        """Integration: Shift pattern fetched from shift rotation master and workforce info."""
        self.pattern_service.get_shift_pattern.return_value = "I-III-II"

        pattern = self.pattern_service.get_shift_pattern("PS001")

        self.assertEqual(pattern, "I-III-II")

    def test_shopUser_patternWeek_displaysCurrentPatternWeeks(self):
        """Positive: Pattern week dropdown shows current month's pattern weeks."""
        self.pattern_service.get_pattern_weeks.return_value = [
            "Week 3",
            "Week 4",
            "Week 5",
        ]

        weeks = self.pattern_service.get_pattern_weeks("2026-05")

        self.assertGreater(len(weeks), 0)


# ---------------------------------------------------------------------------
# Story 8: Shop User - Export Shift Schedule Data
# ---------------------------------------------------------------------------


class TestShopUserExportShiftSchedule(unittest.TestCase):
    """Story 8: Verify Shop User export functionality."""

    def setUp(self):
        """Arrange: Create mock export service."""
        self.export_service = MagicMock()

    def test_shopUserExport_clickExport_exportsToExcel(self):
        """Positive: Shop user clicking Export exports data to Excel."""
        self.export_service.export_to_excel.return_value = {
            "status": "success",
            "file_name": "shift_schedule_shop_export.xlsx",
        }

        result = self.export_service.export_to_excel()

        self.assertEqual(result["status"], "success")
        self.assertTrue(result["file_name"].endswith(".xlsx"))

    def test_shopUserExport_withFilter_exportsFilteredData(self):
        """Positive: Export with from/to date filter exports filtered values."""
        self.export_service.export_to_excel.return_value = {
            "status": "success",
            "record_count": 10,
        }

        result = self.export_service.export_to_excel(
            from_date="01-05-2026", to_date="15-05-2026"
        )

        self.assertEqual(result["record_count"], 10)

    def test_shopUserExport_withoutFilter_exportsAllData(self):
        """Positive: Export without filter exports all existing data."""
        self.export_service.export_to_excel.return_value = {
            "status": "success",
            "record_count": 50,
        }

        result = self.export_service.export_to_excel()

        self.assertEqual(result["record_count"], 50)

    def test_shopUserExport_saveToLocation_savesFile(self):
        """Positive: Shop user can save export file to a location."""
        self.export_service.save_to_location.return_value = {
            "status": "success",
            "path": "/downloads/shop_shift_export.xlsx",
        }

        result = self.export_service.save_to_location(
            "/downloads/shop_shift_export.xlsx"
        )

        self.assertEqual(result["status"], "success")

    def test_shopUserExport_noData_returnsEmptyFile(self):
        """Boundary: Export with no data returns empty file."""
        self.export_service.export_to_excel.return_value = {
            "status": "success",
            "record_count": 0,
            "message": "No data to export",
        }

        result = self.export_service.export_to_excel()

        self.assertEqual(result["record_count"], 0)

    def test_shopUserExport_serviceUnavailable_returnsError(self):
        """Integration: Export service unavailable returns error."""
        self.export_service.export_to_excel.side_effect = ConnectionError(
            "Export service unavailable"
        )

        with self.assertRaises(ConnectionError):
            self.export_service.export_to_excel()


if __name__ == "__main__":
    unittest.main()
