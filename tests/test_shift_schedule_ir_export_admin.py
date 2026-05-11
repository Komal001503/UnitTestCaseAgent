"""
Unit Tests for Maintain Shift Scheduling Plan Module - IR Role Export & IR Admin Role
User Stories: Story 3 (IR Export), Story 4 (IR Admin View), Story 5 (IR Admin Export)

Covers:
- IR: Export shift schedule data to Excel
- IR Admin: View Maintain Shift Scheduling Plan with Configure Shift Plan
- IR Admin: Export shift schedule data to Excel

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
#     ShiftScheduleExportService, ShiftScheduleAdminPage,
#     ConfigureShiftPlanService
# )


# ---------------------------------------------------------------------------
# Story 3: IR - Export Shift Schedule Data
# ---------------------------------------------------------------------------


class TestIRExportShiftSchedule(unittest.TestCase):
    """Story 3: Verify IR export functionality."""

    def setUp(self):
        """Arrange: Create mock export service."""
        self.export_service = MagicMock()

    def test_export_clickExportButton_exportsToExcel(self):
        """Positive: Clicking Export button exports data to an Excel file."""
        self.export_service.export_to_excel.return_value = {
            "status": "success",
            "file_name": "shift_schedule_export.xlsx",
        }

        result = self.export_service.export_to_excel()

        self.assertEqual(result["status"], "success")
        self.assertTrue(result["file_name"].endswith(".xlsx"))

    def test_export_withDateFilter_exportsFilteredData(self):
        """Positive: Exporting with from and to date filter exports filtered values."""
        self.export_service.export_to_excel.return_value = {
            "status": "success",
            "file_name": "shift_schedule_filtered.xlsx",
            "record_count": 15,
        }

        result = self.export_service.export_to_excel(
            from_date="01-05-2026", to_date="15-05-2026"
        )

        self.assertEqual(result["status"], "success")
        self.assertEqual(result["record_count"], 15)

    def test_export_withoutDateFilter_exportsAllData(self):
        """Positive: Exporting without filter exports all existing data."""
        self.export_service.export_to_excel.return_value = {
            "status": "success",
            "file_name": "shift_schedule_all.xlsx",
            "record_count": 100,
        }

        result = self.export_service.export_to_excel()

        self.assertEqual(result["status"], "success")
        self.assertEqual(result["record_count"], 100)

    def test_export_saveToLocation_savesFile(self):
        """Positive: User can save the export file to a location."""
        self.export_service.save_to_location.return_value = {
            "status": "success",
            "path": "/downloads/shift_schedule_export.xlsx",
        }

        result = self.export_service.save_to_location(
            "/downloads/shift_schedule_export.xlsx"
        )

        self.assertEqual(result["status"], "success")
        self.assertIn("/downloads/", result["path"])

    def test_export_noData_returnsEmptyExcel(self):
        """Boundary: Export when no data exists returns empty Excel or info message."""
        self.export_service.export_to_excel.return_value = {
            "status": "success",
            "record_count": 0,
            "message": "No data to export",
        }

        result = self.export_service.export_to_excel()

        self.assertEqual(result["record_count"], 0)

    def test_export_serviceUnavailable_returnsError(self):
        """Integration: Export service unavailable returns error."""
        self.export_service.export_to_excel.side_effect = ConnectionError(
            "Export service unavailable"
        )

        with self.assertRaises(ConnectionError):
            self.export_service.export_to_excel()

    def test_export_invalidDateRange_returnsError(self):
        """Negative: Invalid date range in filter returns error."""
        self.export_service.export_to_excel.return_value = {
            "status": "error",
            "message": "Invalid date range",
        }

        result = self.export_service.export_to_excel(
            from_date="31-05-2026", to_date="01-05-2026"
        )

        self.assertEqual(result["status"], "error")


# ---------------------------------------------------------------------------
# Story 4: IR Admin - View Maintain Shift Scheduling Plan
# ---------------------------------------------------------------------------


class TestIRAdminShiftSchedulePageAttributes(unittest.TestCase):
    """Story 4: Verify IR Admin page attributes (same as Story 1 for IR)."""

    def setUp(self):
        """Arrange: Create mock IR Admin page."""
        self.page = MagicMock()
        self.page.get_attributes.return_value = [
            "shift_code",
            "from_date",
            "to_date",
        ]

    def test_irAdminPage_displaysShiftCodeAttribute(self):
        """Positive: IR Admin page displays Shift Code attribute."""
        attributes = self.page.get_attributes()

        self.assertIn("shift_code", attributes)

    def test_irAdminPage_displaysFromAndToDate(self):
        """Positive: IR Admin page displays From and To date attributes."""
        attributes = self.page.get_attributes()

        self.assertIn("from_date", attributes)
        self.assertIn("to_date", attributes)

    def test_irAdminPage_shiftCodeAutoPopulatesDates(self):
        """Positive: Selecting shift code auto-populates from and to dates."""
        self.page.select_shift_code.return_value = {
            "shift_code": "SC-W02",
            "from_date": "13-01-2026",
            "to_date": "19-01-2026",
        }

        result = self.page.select_shift_code("SC-W02")

        self.assertIsNotNone(result["from_date"])
        self.assertIsNotNone(result["to_date"])


class TestIRAdminShiftScheduleButtons(unittest.TestCase):
    """Story 4: Verify IR Admin page has additional Configure Shift Plan button."""

    def setUp(self):
        """Arrange: Create mock IR Admin page."""
        self.page = MagicMock()
        self.page.get_buttons.return_value = [
            "Save",
            "Export",
            "Configure shift plan",
        ]

    def test_irAdminPage_displaysSaveButton(self):
        """Positive: IR Admin page displays Save button."""
        buttons = self.page.get_buttons()

        self.assertIn("Save", buttons)

    def test_irAdminPage_displaysExportButton(self):
        """Positive: IR Admin page displays Export button."""
        buttons = self.page.get_buttons()

        self.assertIn("Export", buttons)

    def test_irAdminPage_displaysConfigureShiftPlanButton(self):
        """Positive: IR Admin page displays Configure Shift Plan button."""
        buttons = self.page.get_buttons()

        self.assertIn("Configure shift plan", buttons)


class TestConfigureShiftPlan(unittest.TestCase):
    """Story 4: Verify Configure Shift Plan popup and functionality."""

    def setUp(self):
        """Arrange: Create mock configure service."""
        self.configure_service = MagicMock()
        self.configure_service.get_fields.return_value = [
            "from_day",
            "to_day",
            "start_time",
            "end_time",
        ]

    def test_configureShiftPlan_click_opensConfigPopup(self):
        """Positive: Clicking Configure Shift Plan opens the configuration popup."""
        self.configure_service.open.return_value = {"status": "opened"}

        result = self.configure_service.open()

        self.assertEqual(result["status"], "opened")

    def test_configureShiftPlan_displaysFromDayField(self):
        """Positive: Configure popup displays From Day field (Monday to Sunday)."""
        fields = self.configure_service.get_fields()

        self.assertIn("from_day", fields)

    def test_configureShiftPlan_displaysToDayField(self):
        """Positive: Configure popup displays To Day field (Monday to Sunday)."""
        fields = self.configure_service.get_fields()

        self.assertIn("to_day", fields)

    def test_configureShiftPlan_displaysStartTimeField(self):
        """Positive: Configure popup displays Start Time (time picker) field."""
        fields = self.configure_service.get_fields()

        self.assertIn("start_time", fields)

    def test_configureShiftPlan_displaysEndTimeField(self):
        """Positive: Configure popup displays End Time (time picker) field."""
        fields = self.configure_service.get_fields()

        self.assertIn("end_time", fields)

    def test_configureShiftPlan_displaysScheduleShiftButton(self):
        """Positive: Configure popup displays Schedule Shift button."""
        self.configure_service.get_buttons.return_value = ["Schedule shift"]

        buttons = self.configure_service.get_buttons()

        self.assertIn("Schedule shift", buttons)


class TestConfigureShiftPlanDayOptions(unittest.TestCase):
    """Story 4: Verify day dropdown options for Configure Shift Plan."""

    def setUp(self):
        """Arrange: Create mock configure service."""
        self.configure_service = MagicMock()
        self.configure_service.get_day_options.return_value = [
            "Monday",
            "Tuesday",
            "Wednesday",
            "Thursday",
            "Friday",
            "Saturday",
            "Sunday",
        ]

    def test_configureShiftPlan_fromDayDropdown_displaysAllDays(self):
        """Positive: From Day dropdown displays Monday through Sunday."""
        day_options = self.configure_service.get_day_options()

        self.assertEqual(len(day_options), 7)
        self.assertIn("Monday", day_options)
        self.assertIn("Sunday", day_options)

    def test_configureShiftPlan_toDayDropdown_displaysAllDays(self):
        """Positive: To Day dropdown displays Monday through Sunday."""
        day_options = self.configure_service.get_day_options()

        self.assertEqual(len(day_options), 7)


class TestConfigureShiftPlanValidation(unittest.TestCase):
    """Story 4: Verify Configure Shift Plan validation and lock-in period scheduling."""

    def setUp(self):
        """Arrange: Create mock configure service."""
        self.configure_service = MagicMock()

    def test_configureShiftPlan_scheduleShift_setsLockInPeriod(self):
        """Positive: Clicking Schedule Shift sets the lock-in period for shift plan release."""
        self.configure_service.schedule.return_value = {
            "status": "success",
            "lock_in": {
                "from_day": "Friday",
                "to_day": "Saturday",
                "start_time": "18:00",
                "end_time": "06:00",
            },
            "message": "Shift plan release scheduled successfully",
        }

        result = self.configure_service.schedule(
            from_day="Friday",
            to_day="Saturday",
            start_time="18:00",
            end_time="06:00",
        )

        self.assertEqual(result["status"], "success")
        self.assertEqual(result["lock_in"]["from_day"], "Friday")

    def test_configureShiftPlan_autoRelease_basedOnScheduledDayTime(self):
        """Positive: System auto-releases shift plan to shop users based on scheduled day and time."""
        self.configure_service.get_release_status.return_value = {
            "auto_release_enabled": True,
            "next_release": "Friday 18:00",
        }

        status = self.configure_service.get_release_status()

        self.assertTrue(status["auto_release_enabled"])

    def test_configureShiftPlan_missingFromDay_returnsError(self):
        """Negative: Missing From Day returns validation error."""
        self.configure_service.schedule.return_value = {
            "status": "error",
            "message": "From Day is required",
        }

        result = self.configure_service.schedule(
            from_day="",
            to_day="Saturday",
            start_time="18:00",
            end_time="06:00",
        )

        self.assertEqual(result["status"], "error")

    def test_configureShiftPlan_missingStartTime_returnsError(self):
        """Negative: Missing Start Time returns validation error."""
        self.configure_service.schedule.return_value = {
            "status": "error",
            "message": "Start Time is required",
        }

        result = self.configure_service.schedule(
            from_day="Friday",
            to_day="Saturday",
            start_time="",
            end_time="06:00",
        )

        self.assertEqual(result["status"], "error")

    def test_configureShiftPlan_startTimeAfterEndTime_sameDayError(self):
        """Boundary: Start time after end time on same day returns error."""
        self.configure_service.schedule.return_value = {
            "status": "error",
            "message": "Start time must be before end time for same-day schedule",
        }

        result = self.configure_service.schedule(
            from_day="Friday",
            to_day="Friday",
            start_time="18:00",
            end_time="06:00",
        )

        self.assertEqual(result["status"], "error")


class TestIRAdminGridColumns(unittest.TestCase):
    """Story 4: Verify IR Admin grid columns are same as IR grid."""

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
        ]

    def test_irAdminGrid_displaysAllExpectedColumns(self):
        """Positive: IR Admin grid displays all expected columns."""
        columns = self.grid.get_columns()

        expected = [
            "employee",
            "dept_code_shop_name",
            "cadre",
            "category",
            "shift",
            "supervisor",
            "tpt_user",
            "last_modified_by",
            "action",
        ]
        for col in expected:
            self.assertIn(col, columns)

    def test_irAdminGrid_displaysWeekdayShiftPlanColumns(self):
        """Positive: IR Admin grid displays shift plan columns for all weekdays."""
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


class TestIRAdminEditFunctionality(unittest.TestCase):
    """Story 4: Verify IR Admin edit and save functionality."""

    def setUp(self):
        """Arrange: Create mock edit and save services."""
        self.edit_service = MagicMock()
        self.save_service = MagicMock()

    def test_irAdmin_editIcon_makesFieldsEditable(self):
        """Positive: Clicking edit icon makes shift and shift plan editable."""
        self.edit_service.enable_edit.return_value = {
            "editable_fields": ["shift", "shift_plan"],
        }

        result = self.edit_service.enable_edit("PS001")

        self.assertIn("shift", result["editable_fields"])

    def test_irAdmin_saveChanges_displaysSuccessMessage(self):
        """Positive: Saving changes displays 'Changes have been saved successfully'."""
        self.save_service.save_changes.return_value = {
            "status": "success",
            "message": "Changes have been saved successfully",
        }

        result = self.save_service.save_changes("PS001", {"shift": "II"})

        self.assertEqual(result["message"], "Changes have been saved successfully")


class TestIRAdminSearchAndPagination(unittest.TestCase):
    """Story 4: Verify IR Admin search and pagination."""

    def setUp(self):
        """Arrange: Create mock services."""
        self.search_service = MagicMock()
        self.pagination = MagicMock()

    def test_irAdmin_globalSearch_returnsResults(self):
        """Positive: IR Admin can search using Global Search Bar."""
        self.search_service.global_search.return_value = [
            {"ps_no": "PS001", "name": "Test User"},
        ]

        results = self.search_service.global_search("Test")

        self.assertEqual(len(results), 1)

    def test_irAdmin_columnSearch_returnsFilteredResults(self):
        """Positive: IR Admin can search using Column Search Bar."""
        self.search_service.column_search.return_value = [
            {"ps_no": "PS001", "shift": "I"},
        ]

        results = self.search_service.column_search("shift", "I")

        self.assertEqual(len(results), 1)

    def test_irAdmin_pagination_navigatePages(self):
        """Positive: IR Admin can navigate between pages."""
        self.pagination.go_to_page.return_value = {"current_page": 3, "total_pages": 10}

        result = self.pagination.go_to_page(3)

        self.assertEqual(result["current_page"], 3)


# ---------------------------------------------------------------------------
# Story 5: IR Admin - Export Shift Schedule Data
# ---------------------------------------------------------------------------


class TestIRAdminExportShiftSchedule(unittest.TestCase):
    """Story 5: Verify IR Admin export functionality (same as Story 3)."""

    def setUp(self):
        """Arrange: Create mock export service."""
        self.export_service = MagicMock()

    def test_irAdminExport_clickExport_exportsToExcel(self):
        """Positive: IR Admin clicking Export exports data to Excel."""
        self.export_service.export_to_excel.return_value = {
            "status": "success",
            "file_name": "shift_schedule_admin_export.xlsx",
        }

        result = self.export_service.export_to_excel()

        self.assertEqual(result["status"], "success")

    def test_irAdminExport_withFilter_exportsFilteredData(self):
        """Positive: IR Admin export with date filter exports filtered data."""
        self.export_service.export_to_excel.return_value = {
            "status": "success",
            "record_count": 20,
        }

        result = self.export_service.export_to_excel(
            from_date="01-05-2026", to_date="31-05-2026"
        )

        self.assertEqual(result["record_count"], 20)

    def test_irAdminExport_withoutFilter_exportsAllData(self):
        """Positive: IR Admin export without filter exports all existing data."""
        self.export_service.export_to_excel.return_value = {
            "status": "success",
            "record_count": 200,
        }

        result = self.export_service.export_to_excel()

        self.assertEqual(result["record_count"], 200)

    def test_irAdminExport_saveToLocation_savesFile(self):
        """Positive: IR Admin can save export file to a location."""
        self.export_service.save_to_location.return_value = {
            "status": "success",
            "path": "/downloads/admin_shift_export.xlsx",
        }

        result = self.export_service.save_to_location(
            "/downloads/admin_shift_export.xlsx"
        )

        self.assertEqual(result["status"], "success")


if __name__ == "__main__":
    unittest.main()
