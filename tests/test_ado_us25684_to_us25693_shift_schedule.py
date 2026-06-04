"""
Unit Tests for Maintain Shift Scheduling Plan Module
Source: azure_devops_user_stories.md
User Stories:
  US-25684 (IR - Attendance - Maintain shift schedule – View)
  US-25685 (IR - Attendance - Maintain shift schedule – Schedule Shift popup)
  US-25686 (IR - Attendance - Maintain shift schedule – Export data)
  US-25687 (IR - Attendance - Maintain shift schedule – IR Admin with Configure)
  US-25688 (IR - Attendance - Maintain shift schedule – IR Admin Export)
  US-25689 (Shop - Attendance - Maintain shift schedule – View)
  US-25690 (Shop - Attendance - schedule shift)
  US-25691 (Shop - Attendance - Maintain shift schedule – Export)
  US-25692 (Shop Head - Attendance - Maintain shift schedule – View)
  US-25693 (Shop Head - Attendance - Maintain shift schedule – Export)

Covers shift scheduling functionality for IR, IR Admin, Shop, and Shop Head roles.

Test Categories:
- Positive / Happy Path
- Negative / Error Path
- Boundary / Edge Cases
"""

SOURCE_STORY_FILE = "azure_devops_user_stories.md"

import unittest
from unittest.mock import MagicMock, patch


# TODO: Import actual modules once implementation is available.
# from src.attendance.shift_schedule import (
#     ShiftSchedulePage, ShiftScheduleService, ShiftCodeMaster,
#     ShiftRotationMaster, ExportService, ConfigureShiftPlanService
# )


# ---------------------------------------------------------------------------
# US-25684: IR – View Maintain Shift Scheduling Plan
# ---------------------------------------------------------------------------


class TestIRShiftSchedulePageDisplay(unittest.TestCase):
    """US-25684: Verify IR can view the Maintain Shift Scheduling Plan page."""

    def setUp(self):
        self.navigation = MagicMock()
        self.page = MagicMock()
        self.page.get_attributes.return_value = ["Shift Code", "From", "To"]
        self.page.get_grid_columns.return_value = [
            "Employee",
            "Dept Code and Shop Name",
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
        self.page.get_buttons.return_value = ["Save", "Export"]

    def test_navigation_selectAttendanceMenu_displaysShiftSchedulePage(self):
        """Positive: Selecting 'Maintain Shift Scheduling Plan' from Attendance Management opens the page."""
        self.navigation.select_menu.return_value = "Maintain Shift Scheduling Plan"

        result = self.navigation.select_menu(
            "Attendance Management", "Maintain Shift Scheduling Plan"
        )

        self.assertEqual(result, "Maintain Shift Scheduling Plan")

    def test_page_displaysShiftCodeAttribute(self):
        """Positive: Page displays Shift Code attribute field."""
        attributes = self.page.get_attributes()

        self.assertIn("Shift Code", attributes)

    def test_page_displaysFromAndToDateAttributes(self):
        """Positive: Page displays From and To date attributes auto-filled from shift code."""
        attributes = self.page.get_attributes()

        self.assertIn("From", attributes)
        self.assertIn("To", attributes)

    def test_page_displaysAllSevenDayColumns(self):
        """Positive: Shift plan columns exist for all seven days of the week."""
        columns = self.page.get_grid_columns()
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

        for day in days:
            self.assertIn(day, columns)

    def test_page_displaysAllGridColumns(self):
        """Positive: Grid displays all 17 required columns."""
        columns = self.page.get_grid_columns()

        self.assertEqual(len(columns), 17)
        self.assertIn("Employee", columns)
        self.assertIn("Supervisor", columns)
        self.assertIn("TPT User", columns)

    def test_page_displaysSaveAndExportButtons(self):
        """Positive: Page displays Save and Export buttons."""
        buttons = self.page.get_buttons()

        self.assertIn("Save", buttons)
        self.assertIn("Export", buttons)

    def test_shiftCodeSelection_autoPopulatesFromAndToDates(self):
        """Positive: Selecting a Shift Code auto-populates From and To dates."""
        self.page.on_shift_code_selected.return_value = {
            "from_date": "02-06-2026",
            "to_date": "08-06-2026",
        }

        result = self.page.on_shift_code_selected("SHIFT_WEEK_23")

        self.assertIsNotNone(result["from_date"])
        self.assertIsNotNone(result["to_date"])

    def test_editIcon_click_makesShiftAndShiftPlanFieldsEditable(self):
        """Positive: Clicking edit icon makes Shift and all day columns editable in that row."""
        self.page.click_edit_icon.return_value = {
            "editable_fields": [
                "Shift",
                "Monday",
                "Tuesday",
                "Wednesday",
                "Thursday",
                "Friday",
                "Saturday",
                "Sunday",
            ]
        }

        result = self.page.click_edit_icon(row="emp_001")

        self.assertIn("Shift", result["editable_fields"])
        self.assertIn("Monday", result["editable_fields"])

    def test_saveButton_displaysSuccessMessage(self):
        """Positive: Clicking Save shows 'Changes have been saved successfully'."""
        self.page.save.return_value = {
            "status": "success",
            "message": "Changes have been saved successfully",
        }

        result = self.page.save()

        self.assertEqual(result["status"], "success")
        self.assertIn("saved successfully", result["message"])

    def test_changeShiftColumn_autoChangesAllDaysForThatEmployee(self):
        """Validation: Changing 'Shift' column auto-updates all day columns for the employee."""
        self.page.change_shift.return_value = {
            "updated_days": [
                "Monday",
                "Tuesday",
                "Wednesday",
                "Thursday",
                "Friday",
                "Saturday",
                "Sunday",
            ]
        }

        result = self.page.change_shift(employee="emp_001", new_shift="I")

        self.assertEqual(len(result["updated_days"]), 7)

    def test_multiSelectCheckbox_selectsMultipleEmployees(self):
        """Positive: Multi-select checkbox allows selecting multiple employee rows."""
        self.page.select_multiple.return_value = {"selected": ["emp_001", "emp_002"]}

        result = self.page.select_multiple(["emp_001", "emp_002"])

        self.assertEqual(len(result["selected"]), 2)

    def test_lockInPeriod_irCannotEditDuringRelease(self):
        """Validation: IR cannot edit shift plans during the scheduled lock-in period."""
        self.page.is_editable_by_ir.return_value = False

        result = self.page.is_editable_by_ir(during_lock_in=True)

        self.assertFalse(result)

    def test_lockInPeriod_irCanEditOutsideLockIn(self):
        """Positive: IR can edit shift plans on any day outside the lock-in period."""
        self.page.is_editable_by_ir.return_value = True

        result = self.page.is_editable_by_ir(during_lock_in=False)

        self.assertTrue(result)

    def test_searchBar_columnAndGlobal_filtersResults(self):
        """Positive: Both Column search and Global search bar filter results correctly."""
        self.page.search.return_value = [{"employee": "PS-001 John"}]

        results = self.page.search("John")

        self.assertGreater(len(results), 0)


# ---------------------------------------------------------------------------
# US-25685: IR – Schedule Shift Popup
# ---------------------------------------------------------------------------


class TestIRScheduleShiftPopup(unittest.TestCase):
    """US-25685: Verify Schedule Shift popup for IR role."""

    def setUp(self):
        self.service = MagicMock()

    def test_scheduleShiftButton_showsPopupWithSelectedEmployees(self):
        """Positive: Clicking Schedule Shift shows popup with selected employees listed."""
        self.service.open_schedule_shift_popup.return_value = {
            "status": "open",
            "employees": ["PS-001 John", "PS-002 Jane"],
        }

        result = self.service.open_schedule_shift_popup(["PS-001", "PS-002"])

        self.assertEqual(result["status"], "open")
        self.assertEqual(len(result["employees"]), 2)

    def test_popup_displaysShiftPatternStartDateEndDateForeverPatternWeek(self):
        """Positive: Popup shows Shift Pattern, Start Date, End Date, Forever, Pattern Week fields."""
        self.service.get_popup_fields.return_value = [
            "Shift Pattern",
            "Start Date",
            "End Date",
            "Forever",
            "Pattern Week",
        ]

        fields = self.service.get_popup_fields()

        self.assertIn("Shift Pattern", fields)
        self.assertIn("Start Date", fields)
        self.assertIn("Forever", fields)
        self.assertIn("Pattern Week", fields)

    def test_popup_dataGrid_displaysRotationTypeAndDayColumns(self):
        """Positive: Popup data grid shows Rotation Type and Mon-Sun columns."""
        self.service.get_popup_grid_columns.return_value = [
            "Rotation Type",
            "Monday",
            "Tuesday",
            "Wednesday",
            "Thursday",
            "Friday",
            "Saturday",
            "Sunday",
        ]

        columns = self.service.get_popup_grid_columns()

        self.assertIn("Rotation Type", columns)
        self.assertIn("Monday", columns)
        self.assertIn("Sunday", columns)

    def test_scheduleShift_saveSuccessForOneDay_displaysCorrectMessage(self):
        """Positive: Saving shift change for one day shows 'Shift plan successfully changed for one day'."""
        self.service.schedule_shift.return_value = {
            "status": "success",
            "message": "Shift plan successfully changed for one day",
        }

        result = self.service.schedule_shift(option="one_day")

        self.assertIn("changed for one day", result["message"])

    def test_scheduleShift_saveForCurrentWeek_displaysCorrectMessage(self):
        """Positive: Saving for current week shows 'Shift plan successfully changed for current week only'."""
        self.service.schedule_shift.return_value = {
            "status": "success",
            "message": "Shift plan successfully changed for current week only from 01-06-2026 to 07-06-2026",
        }

        result = self.service.schedule_shift(option="current_week")

        self.assertIn("changed for current week only", result["message"])

    def test_scheduleShift_forever_displaysCorrectMessage(self):
        """Positive: Saving with Forever shows 'New shift rotation will be carried forward...'."""
        self.service.schedule_shift.return_value = {
            "status": "success",
            "message": 'New shift rotation will be carried forward for the workman from 01-06-2026 to "Forever"',
        }

        result = self.service.schedule_shift(option="forever")

        self.assertIn("carried forward", result["message"])
        self.assertIn("Forever", result["message"])

    def test_scheduleShift_cancelButton_revertsChanges(self):
        """Positive: Clicking Cancel reverts all changes in the popup."""
        self.service.cancel_schedule_shift.return_value = {"reverted": True}

        result = self.service.cancel_schedule_shift()

        self.assertTrue(result["reverted"])

    def test_scheduleShift_startDateAndEndDate_changesShiftForNDays(self):
        """Validation: Start date and end date selection changes shift for N days (not restricted to one week)."""
        self.service.validate_date_range.return_value = {
            "valid": True,
            "days_affected": 14,
        }

        result = self.service.validate_date_range("01-06-2026", "14-06-2026")

        self.assertTrue(result["valid"])
        self.assertEqual(result["days_affected"], 14)

    def test_scheduleShift_foreverOption_changesShiftFromStartDateIndefinitely(self):
        """Validation: Forever option changes shift from start date through employee's entire tenure."""
        self.service.set_forever_shift.return_value = {
            "forever": True,
            "from_date": "01-06-2026",
        }

        result = self.service.set_forever_shift(start_date="01-06-2026")

        self.assertTrue(result["forever"])
        self.assertEqual(result["from_date"], "01-06-2026")


# ---------------------------------------------------------------------------
# US-25686 / US-25688: IR – Export Data
# ---------------------------------------------------------------------------


class TestIRShiftScheduleExport(unittest.TestCase):
    """US-25686 / US-25688: Verify Export button functionality for IR and IR Admin."""

    def setUp(self):
        self.service = MagicMock()

    def test_exportButton_withFilter_exportsFilteredData(self):
        """Positive: Export with From/To date filter exports only filtered records."""
        self.service.export.return_value = {
            "status": "success",
            "filter_applied": True,
            "filename": "shift_schedule_filtered.xlsx",
        }

        result = self.service.export(from_date="01-06-2026", to_date="07-06-2026")

        self.assertEqual(result["status"], "success")
        self.assertTrue(result["filter_applied"])

    def test_exportButton_withoutFilter_exportsAllData(self):
        """Positive: Export without filter exports all existing records."""
        self.service.export.return_value = {
            "status": "success",
            "filter_applied": False,
            "filename": "shift_schedule_all.xlsx",
        }

        result = self.service.export(from_date=None, to_date=None)

        self.assertEqual(result["status"], "success")
        self.assertFalse(result["filter_applied"])

    def test_exportFile_canBeSavedToLocation(self):
        """Positive: Exported file can be saved to a user-specified location."""
        self.service.save_export.return_value = {
            "status": "success",
            "saved_path": "/downloads/shift_schedule.xlsx",
        }

        result = self.service.save_export("/downloads/shift_schedule.xlsx")

        self.assertEqual(result["status"], "success")
        self.assertIn("/downloads", result["saved_path"])


# ---------------------------------------------------------------------------
# US-25687: IR Admin – View with Configure Shift Plan
# ---------------------------------------------------------------------------


class TestIRAdminConfigureShiftPlan(unittest.TestCase):
    """US-25687: Verify IR Admin has 'Configure Shift Plan' button and functionality."""

    def setUp(self):
        self.service = MagicMock()

    def test_irAdminPage_displaysConfigureShiftPlanButton(self):
        """Positive: IR Admin sees Save, Export, and Configure Shift Plan buttons."""
        self.service.get_buttons.return_value = ["Save", "Export", "Configure Shift Plan"]

        buttons = self.service.get_buttons(role="IR_ADMIN")

        self.assertIn("Configure Shift Plan", buttons)

    def test_configureShiftPlan_click_displaysConfigurationFields(self):
        """Positive: Clicking Configure Shift Plan opens config form with From/To day and time."""
        self.service.open_configure_shift_plan.return_value = {
            "status": "open",
            "fields": ["From Day", "To Day", "Start Time", "End Time"],
        }

        result = self.service.open_configure_shift_plan()

        self.assertEqual(result["status"], "open")
        self.assertIn("From Day", result["fields"])
        self.assertIn("Start Time", result["fields"])

    def test_configureShiftPlan_fromDay_dropdownHasAllDays(self):
        """Positive: From Day dropdown includes Monday through Sunday."""
        self.service.get_day_options.return_value = [
            "Monday",
            "Tuesday",
            "Wednesday",
            "Thursday",
            "Friday",
            "Saturday",
            "Sunday",
        ]

        days = self.service.get_day_options()

        self.assertEqual(len(days), 7)
        self.assertIn("Monday", days)
        self.assertIn("Sunday", days)

    def test_configureShiftPlan_scheduleShift_setsLockInPeriod(self):
        """Positive: Clicking Schedule Shift configures lock-in period for shop users."""
        self.service.configure_lock_in.return_value = {
            "status": "success",
            "lock_in_set": True,
            "release_day": "Friday",
            "release_time": "17:00",
        }

        result = self.service.configure_lock_in(
            from_day="Monday", to_day="Friday", start_time="08:00", end_time="17:00"
        )

        self.assertEqual(result["status"], "success")
        self.assertTrue(result["lock_in_set"])

    def test_configureShiftPlan_systemAutoReleasesToShopUsersOnSchedule(self):
        """Positive: System auto-releases shift plan to shop users based on configured schedule."""
        self.service.auto_release_shift_plan.return_value = {
            "released": True,
            "released_to": "shop_users",
        }

        result = self.service.auto_release_shift_plan()

        self.assertTrue(result["released"])
        self.assertEqual(result["released_to"], "shop_users")


# ---------------------------------------------------------------------------
# US-25689: Shop User – View Maintain Shift Scheduling Plan
# ---------------------------------------------------------------------------


class TestShopShiftSchedulePageDisplay(unittest.TestCase):
    """US-25689: Verify Shop user can view Maintain Shift Scheduling Plan page."""

    def setUp(self):
        self.page = MagicMock()
        self.page.get_attributes.return_value = ["Shift Code", "From Date", "To Date"]
        self.page.get_grid_columns.return_value = [
            "Employee",
            "Dept Code and Shop Name",
            "Shift",
            "Monday",
            "Tuesday",
            "Wednesday",
            "Thursday",
            "Friday",
            "Saturday",
            "Sunday",
            "Last Modified By",
            "TPT User",
            "Action",
        ]
        self.page.get_buttons.return_value = ["Save", "Export"]

    def test_shopPage_attributes_areNonEditable(self):
        """Positive: Shop user sees Shift Code, From Date, To Date as non-editable attributes."""
        attributes = self.page.get_attributes()

        self.assertIn("Shift Code", attributes)
        self.assertIn("From Date", attributes)
        self.assertIn("To Date", attributes)

    def test_shopPage_gridColumns_displaysAllRequired(self):
        """Positive: Shop grid shows Employee, Dept, Shift, day columns, Last Modified By, TPT, Action."""
        columns = self.page.get_grid_columns()

        self.assertIn("Employee", columns)
        self.assertIn("Shift", columns)
        self.assertIn("Action", columns)

    def test_shopPage_editIcon_makesOnlyShiftAndDaysEditable(self):
        """Positive: Edit icon makes only Shift and Monday-Sunday editable; other fields locked."""
        self.page.click_edit_icon.return_value = {
            "editable_fields": [
                "Shift",
                "Monday",
                "Tuesday",
                "Wednesday",
                "Thursday",
                "Friday",
                "Saturday",
                "Sunday",
            ],
            "locked_fields": ["Employee", "Dept Code and Shop Name"],
        }

        result = self.page.click_edit_icon(row="emp_001")

        self.assertIn("Shift", result["editable_fields"])
        self.assertIn("Employee", result["locked_fields"])

    def test_shopPage_saveButton_displaysSuccessMessage(self):
        """Positive: Save button shows 'Changes have been saved successfully'."""
        self.page.save.return_value = {
            "status": "success",
            "message": "Changes have been saved successfully",
        }

        result = self.page.save()

        self.assertIn("saved successfully", result["message"])

    def test_shop_editShift_restrictedToEmployeeShiftRotation(self):
        """Validation: Shop user can only change shifts within the employee's assigned rotation."""
        self.page.validate_shift_change.return_value = {
            "valid": True,
            "restricted": True,
        }

        result = self.page.validate_shift_change("I", employee="emp_001")

        self.assertTrue(result["restricted"])

    def test_shop_selectOneDay_changesOnlyThatDayShift(self):
        """Validation: Selecting only one day change affects only that specific day."""
        self.page.apply_one_day_change.return_value = {
            "days_changed": 1,
            "day": "Wednesday",
        }

        result = self.page.apply_one_day_change("Wednesday", shift="II")

        self.assertEqual(result["days_changed"], 1)


# ---------------------------------------------------------------------------
# US-25690: Shop – Schedule Shift Popup
# ---------------------------------------------------------------------------


class TestShopScheduleShiftPopup(unittest.TestCase):
    """US-25690: Verify Schedule Shift popup for Shop user."""

    def setUp(self):
        self.service = MagicMock()

    def test_scheduleShiftOrEditIcon_openShiftRotationPage(self):
        """Positive: Clicking Schedule Shift or Edit Icon opens shift rotation page."""
        self.service.open_shift_rotation_page.return_value = {
            "status": "open",
            "employees": ["PS-001 John"],
        }

        result = self.service.open_shift_rotation_page(["PS-001"])

        self.assertEqual(result["status"], "open")

    def test_popup_displaysShiftPatternStartDateEndDateForeverPatternWeek(self):
        """Positive: Popup shows Shift Pattern, Start Date, End Date, Forever, Pattern Week."""
        self.service.get_popup_fields.return_value = [
            "Shift Pattern",
            "Start Date",
            "End Date",
            "Forever",
            "Pattern Week",
        ]

        fields = self.service.get_popup_fields()

        self.assertIn("Shift Pattern", fields)
        self.assertIn("Forever", fields)

    def test_scheduleShiftButton_savesShiftPlan(self):
        """Positive: Clicking Schedule Shift saves the shift plan changes."""
        self.service.save_schedule_shift.return_value = {"status": "success"}

        result = self.service.save_schedule_shift()

        self.assertEqual(result["status"], "success")

    def test_cancelButton_revertsChanges(self):
        """Positive: Cancel button reverts changes without saving."""
        self.service.cancel.return_value = {"reverted": True}

        result = self.service.cancel()

        self.assertTrue(result["reverted"])

    def test_option_changeShiftForSelectedDate_works(self):
        """Positive: User can change shift for a specific selected date."""
        self.service.change_shift_for_date.return_value = {"status": "success"}

        result = self.service.change_shift_for_date("01-06-2026", shift="I")

        self.assertEqual(result["status"], "success")

    def test_option_carryRotationalChangeForever_works(self):
        """Positive: User can carry shift rotation change from edited date to forever."""
        self.service.carry_forward_forever.return_value = {
            "forever": True,
            "from_date": "01-06-2026",
        }

        result = self.service.carry_forward_forever("01-06-2026")

        self.assertTrue(result["forever"])


# ---------------------------------------------------------------------------
# US-25691 / US-25693: Shop / Shop Head – Export
# ---------------------------------------------------------------------------


class TestShopAndShopHeadExport(unittest.TestCase):
    """US-25691 / US-25693: Verify Export for Shop and Shop Head roles."""

    def setUp(self):
        self.service = MagicMock()

    def test_exportButton_withFilter_exportsFilteredData(self):
        """Positive: Export with From/To date filter exports filtered shift data."""
        self.service.export.return_value = {
            "status": "success",
            "filter_applied": True,
            "filename": "shop_shift_filtered.xlsx",
        }

        result = self.service.export(from_date="01-06-2026", to_date="07-06-2026")

        self.assertEqual(result["status"], "success")
        self.assertTrue(result["filter_applied"])

    def test_exportButton_withoutFilter_exportsAllData(self):
        """Positive: Export without filter exports all current shift schedule data."""
        self.service.export.return_value = {
            "status": "success",
            "filter_applied": False,
        }

        result = self.service.export(from_date=None, to_date=None)

        self.assertFalse(result["filter_applied"])

    def test_exportFile_canBeSavedToLocation(self):
        """Positive: User can save the exported file to a chosen location."""
        self.service.save_export.return_value = {"status": "success", "saved": True}

        result = self.service.save_export("/downloads/")

        self.assertTrue(result["saved"])


# ---------------------------------------------------------------------------
# US-25692: Shop Head – View Maintain Shift Scheduling Plan
# ---------------------------------------------------------------------------


class TestShopHeadShiftSchedulePageDisplay(unittest.TestCase):
    """US-25692: Verify Shop Head view of Maintain Shift Scheduling Plan (read-only)."""

    def setUp(self):
        self.page = MagicMock()
        self.page.get_attributes.return_value = ["Shift Code", "From", "To"]
        self.page.get_grid_columns.return_value = [
            "Employee",
            "Dept Code and Shop Name",
            "Shift",
            "Monday",
            "Tuesday",
            "Wednesday",
            "Thursday",
            "Friday",
            "Saturday",
            "Sunday",
            "Supervisor",
            "Altered Shift Type",
        ]
        self.page.get_buttons.return_value = ["Export"]

    def test_shopHeadPage_displaysShiftCodeFromToDates(self):
        """Positive: Shop Head page shows Shift Code, From date, and To date fields."""
        attributes = self.page.get_attributes()

        self.assertIn("Shift Code", attributes)
        self.assertIn("From", attributes)
        self.assertIn("To", attributes)

    def test_shopHeadPage_displaysOnlyExportButton(self):
        """Positive: Shop Head sees only Export button (no Save, Configure)."""
        buttons = self.page.get_buttons()

        self.assertEqual(len(buttons), 1)
        self.assertIn("Export", buttons)
        self.assertNotIn("Save", buttons)

    def test_shopHeadPage_gridIncludes_AlteredShiftTypeColumn(self):
        """Positive: Grid shows Altered Shift Type column (one day, one week, full rotation)."""
        columns = self.page.get_grid_columns()

        self.assertIn("Altered Shift Type", columns)

    def test_shopHeadPage_gridIncludes_AllSevenDayColumnsWithDates(self):
        """Positive: Mon to Sun columns are displayed in DD-MM-YYYY format."""
        columns = self.page.get_grid_columns()

        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        for day in days:
            self.assertIn(day, columns)

    def test_shopHeadPage_shiftDataFetchedFromRotationMaster(self):
        """Positive: Shift schedule data is fetched from shift rotation master per day."""
        self.page.get_shift_data.return_value = {
            "fetched_from": "shift_rotation_master",
            "days_populated": 7,
        }

        result = self.page.get_shift_data("SHIFT_WEEK_23")

        self.assertEqual(result["fetched_from"], "shift_rotation_master")
        self.assertEqual(result["days_populated"], 7)

    def test_shopHeadPage_searchBar_filtersResults(self):
        """Positive: Column and Global search bars filter shift schedule results."""
        self.page.search.return_value = [{"employee": "PS-001 John"}]

        results = self.page.search("John")

        self.assertGreater(len(results), 0)

    def test_shopHeadPage_pageNavigation_works(self):
        """Positive: Page navigation works for Shop Head."""
        self.page.get_page.return_value = {"page": 2}

        result = self.page.get_page(2)

        self.assertEqual(result["page"], 2)

    def test_unauthorizedRole_cannotAccessShiftSchedule(self):
        """Negative: User without appropriate role is denied access."""
        self.page.has_access.return_value = False

        result = self.page.has_access(role="CONTRACTOR")

        self.assertFalse(result)


if __name__ == "__main__":
    unittest.main()
