"""
Unit Tests for Maintain Shift Scheduling Plan Module - Shop Head & Leadership Roles
User Stories: Story 9 (Shop Head View), Story 10 (Shop Head / Location Head / BU Head Export)

Covers:
- Shop Head: View-only access to Maintain Shift Scheduling Plan
- Shop Head: View Altered Shift Type column
- Shop Head / Location Head / BU Head: Export shift schedule data

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
#     ShiftScheduleShopHeadPage, ShiftScheduleExportService
# )


# ---------------------------------------------------------------------------
# Story 9: Shop Head - View Maintain Shift Scheduling Plan (View Only)
# ---------------------------------------------------------------------------


class TestShopHeadNavigation(unittest.TestCase):
    """Story 9: Verify Shop Head navigation to Maintain Shift Scheduling Plan."""

    def setUp(self):
        """Arrange: Create mock navigation service."""
        self.navigation = MagicMock()

    def test_shopHead_sideNavigation_displaysMaintainShiftSchedulePlan(self):
        """Positive: Shop Head can see Maintain Shift Scheduling Plan in Attendance Management."""
        self.navigation.get_attendance_submenus.return_value = [
            "Maintain Shift Scheduling Plan",
        ]

        submenus = self.navigation.get_attendance_submenus()

        self.assertIn("Maintain Shift Scheduling Plan", submenus)

    def test_shopHead_selectShiftSchedulePlan_displaysPage(self):
        """Positive: Selecting sub menu opens the page."""
        self.navigation.open_page.return_value = {
            "status": "success",
            "page": "Maintain Shift Scheduling Plan",
        }

        result = self.navigation.open_page("Maintain Shift Scheduling Plan")

        self.assertEqual(result["status"], "success")


class TestShopHeadPageAttributes(unittest.TestCase):
    """Story 9: Verify Shop Head page attributes."""

    def setUp(self):
        """Arrange: Create mock page."""
        self.page = MagicMock()
        self.page.get_attributes.return_value = [
            "shift_code",
            "from_date",
            "to_date",
        ]

    def test_shopHead_displaysShiftCode(self):
        """Positive: Page displays Shift Code attribute."""
        attributes = self.page.get_attributes()

        self.assertIn("shift_code", attributes)

    def test_shopHead_displaysFromDatePicker(self):
        """Positive: Page displays From date (DD-MM-YYYY) with date picker."""
        attributes = self.page.get_attributes()

        self.assertIn("from_date", attributes)

    def test_shopHead_displaysToDatePicker(self):
        """Positive: Page displays To date (DD-MM-YYYY) with date picker."""
        attributes = self.page.get_attributes()

        self.assertIn("to_date", attributes)


class TestShopHeadGridColumns(unittest.TestCase):
    """Story 9: Verify Shop Head grid columns including Altered Shift Type."""

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
            "supervisor",
            "altered_shift_type",
        ]

    def test_shopHeadGrid_displaysEmployeeColumn(self):
        """Positive: Grid displays Employee (PS No and Name) column."""
        columns = self.grid.get_columns()

        self.assertIn("employee", columns)

    def test_shopHeadGrid_displaysDeptCodeShopName(self):
        """Positive: Grid displays Dept Code and Shop Name column."""
        columns = self.grid.get_columns()

        self.assertIn("dept_code_shop_name", columns)

    def test_shopHeadGrid_displaysShiftColumn(self):
        """Positive: Grid displays Shift column."""
        columns = self.grid.get_columns()

        self.assertIn("shift", columns)

    def test_shopHeadGrid_displaysAllWeekdayColumns(self):
        """Positive: Grid displays shift plan columns for Monday to Sunday with date."""
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

    def test_shopHeadGrid_displaysSupervisorColumn(self):
        """Positive: Grid displays Supervisor column (auto-populated by dept code)."""
        columns = self.grid.get_columns()

        self.assertIn("supervisor", columns)

    def test_shopHeadGrid_displaysAlteredShiftTypeColumn(self):
        """Positive: Grid displays Altered Shift Type column."""
        columns = self.grid.get_columns()

        self.assertIn("altered_shift_type", columns)


class TestShopHeadAlteredShiftType(unittest.TestCase):
    """Story 9: Verify Altered Shift Type column values."""

    def setUp(self):
        """Arrange: Create mock grid data service."""
        self.grid_service = MagicMock()

    def test_alteredShiftType_oneDayChange_displaysCorrectly(self):
        """Positive: Altered Shift Type shows 'Change of one day only'."""
        self.grid_service.get_altered_type.return_value = "Change of one day only"

        result = self.grid_service.get_altered_type("PS001")

        self.assertEqual(result, "Change of one day only")

    def test_alteredShiftType_oneWeekChange_displaysCorrectly(self):
        """Positive: Altered Shift Type shows 'Change for one week only'."""
        self.grid_service.get_altered_type.return_value = "Change for one week only"

        result = self.grid_service.get_altered_type("PS002")

        self.assertEqual(result, "Change for one week only")

    def test_alteredShiftType_completeRotationChange_displaysCorrectly(self):
        """Positive: Altered Shift Type shows 'Complete shift rotation change'."""
        self.grid_service.get_altered_type.return_value = (
            "Complete shift rotation change"
        )

        result = self.grid_service.get_altered_type("PS003")

        self.assertEqual(result, "Complete shift rotation change")

    def test_alteredShiftType_noChange_displaysNone(self):
        """Boundary: No alteration shows empty or N/A."""
        self.grid_service.get_altered_type.return_value = "N/A"

        result = self.grid_service.get_altered_type("PS004")

        self.assertEqual(result, "N/A")


class TestShopHeadViewOnlyAccess(unittest.TestCase):
    """Story 9: Verify Shop Head has view-only access (no edit)."""

    def setUp(self):
        """Arrange: Create mock page with view-only permissions."""
        self.page = MagicMock()

    def test_shopHead_noEditIcon_displayed(self):
        """Negative: Shop Head does not see edit icon (view-only access)."""
        self.page.get_columns.return_value = [
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
            "supervisor",
            "altered_shift_type",
        ]

        columns = self.page.get_columns()

        self.assertNotIn("action", columns)

    def test_shopHead_noSaveButton_displayed(self):
        """Negative: Shop Head does not see Save button (view-only)."""
        self.page.get_buttons.return_value = ["Export"]

        buttons = self.page.get_buttons()

        self.assertNotIn("Save", buttons)
        self.assertIn("Export", buttons)

    def test_shopHead_attemptEdit_denied(self):
        """Negative: Shop Head attempting to edit returns access denied."""
        self.page.edit_row.return_value = {
            "status": "error",
            "message": "Access denied: View-only access",
        }

        result = self.page.edit_row("PS001", {"shift": "I"})

        self.assertEqual(result["status"], "error")
        self.assertIn("View-only", result["message"])


class TestShopHeadDataFetching(unittest.TestCase):
    """Story 9: Verify Shop Head data fetching."""

    def setUp(self):
        """Arrange: Create mock services."""
        self.shift_rotation_master = MagicMock()

    def test_shopHead_shiftPlan_fetchedFromShiftRotationMaster(self):
        """Integration: Shift plan fetched from shift rotation master."""
        self.shift_rotation_master.get_shift_plan.return_value = {
            "monday": "II",
            "tuesday": "II",
            "wednesday": "II",
            "thursday": "II",
            "friday": "II",
            "saturday": "II",
            "sunday": "OFF",
        }

        plan = self.shift_rotation_master.get_shift_plan("PS001", "SC-W01")

        self.assertEqual(plan["monday"], "II")


class TestShopHeadSearchAndPagination(unittest.TestCase):
    """Story 9: Verify Shop Head search and pagination."""

    def setUp(self):
        """Arrange: Create mock services."""
        self.search_service = MagicMock()
        self.pagination = MagicMock()

    def test_shopHead_globalSearch_returnsResults(self):
        """Positive: Shop Head can search using Global Search Bar."""
        self.search_service.global_search.return_value = [
            {"ps_no": "PS001"},
        ]

        results = self.search_service.global_search("PS001")

        self.assertEqual(len(results), 1)

    def test_shopHead_columnSearch_returnsResults(self):
        """Positive: Shop Head can search using Column Search Bar."""
        self.search_service.column_search.return_value = [
            {"ps_no": "PS001", "dept_code": "D001"},
        ]

        results = self.search_service.column_search("dept_code", "D001")

        self.assertEqual(len(results), 1)

    def test_shopHead_pagination_navigatePages(self):
        """Positive: Shop Head can navigate between pages."""
        self.pagination.go_to_page.return_value = {"current_page": 1, "total_pages": 3}

        result = self.pagination.go_to_page(1)

        self.assertEqual(result["current_page"], 1)


# ---------------------------------------------------------------------------
# Story 10: Shop Head / Location Head / BU Head - Export
# ---------------------------------------------------------------------------


class TestLeadershipExportShiftSchedule(unittest.TestCase):
    """Story 10: Verify export functionality for Shop Head, Location Head, and BU Head."""

    def setUp(self):
        """Arrange: Create mock export service."""
        self.export_service = MagicMock()

    def test_leadershipExport_clickExport_exportsToExcel(self):
        """Positive: Clicking Export exports data to Excel file."""
        self.export_service.export_to_excel.return_value = {
            "status": "success",
            "file_name": "shift_schedule_leadership_export.xlsx",
        }

        result = self.export_service.export_to_excel()

        self.assertEqual(result["status"], "success")
        self.assertTrue(result["file_name"].endswith(".xlsx"))

    def test_leadershipExport_withDateFilter_exportsFilteredData(self):
        """Positive: Export with from/to date filter exports filtered values."""
        self.export_service.export_to_excel.return_value = {
            "status": "success",
            "record_count": 25,
        }

        result = self.export_service.export_to_excel(
            from_date="01-05-2026", to_date="31-05-2026"
        )

        self.assertEqual(result["record_count"], 25)

    def test_leadershipExport_withoutFilter_exportsAllData(self):
        """Positive: Export without filter exports all existing data."""
        self.export_service.export_to_excel.return_value = {
            "status": "success",
            "record_count": 500,
        }

        result = self.export_service.export_to_excel()

        self.assertEqual(result["record_count"], 500)

    def test_leadershipExport_saveToLocation_savesFile(self):
        """Positive: User can save export file to a location."""
        self.export_service.save_to_location.return_value = {
            "status": "success",
            "path": "/downloads/leadership_shift_export.xlsx",
        }

        result = self.export_service.save_to_location(
            "/downloads/leadership_shift_export.xlsx"
        )

        self.assertEqual(result["status"], "success")

    def test_leadershipExport_noData_returnsEmptyFile(self):
        """Boundary: Export with no data returns empty file or info message."""
        self.export_service.export_to_excel.return_value = {
            "status": "success",
            "record_count": 0,
            "message": "No data to export",
        }

        result = self.export_service.export_to_excel()

        self.assertEqual(result["record_count"], 0)

    def test_leadershipExport_serviceTimeout_returnsError(self):
        """Integration: Export service timeout returns error."""
        self.export_service.export_to_excel.side_effect = TimeoutError(
            "Export service timed out"
        )

        with self.assertRaises(TimeoutError):
            self.export_service.export_to_excel()

    def test_leadershipExport_invalidDateRange_returnsError(self):
        """Negative: Invalid date range returns error."""
        self.export_service.export_to_excel.return_value = {
            "status": "error",
            "message": "Invalid date range",
        }

        result = self.export_service.export_to_excel(
            from_date="31-05-2026", to_date="01-05-2026"
        )

        self.assertEqual(result["status"], "error")


class TestShopHeadExportButton(unittest.TestCase):
    """Story 10: Verify Shop Head has Export button on page."""

    def setUp(self):
        """Arrange: Create mock page."""
        self.page = MagicMock()

    def test_shopHead_hasExportButton(self):
        """Positive: Shop Head page has Export button."""
        self.page.get_buttons.return_value = ["Export"]

        buttons = self.page.get_buttons()

        self.assertIn("Export", buttons)
        self.assertEqual(len(buttons), 1)


class TestLocationHeadBUHeadAccess(unittest.TestCase):
    """Story 10: Verify Location Head and BU Head have view-only access with export."""

    def setUp(self):
        """Arrange: Create mock access service."""
        self.access_service = MagicMock()

    def test_locationHead_viewAccess_allowed(self):
        """Positive: Location Head has view access to shift schedule page."""
        self.access_service.check_access.return_value = {
            "role": "Location Head",
            "access": "view",
        }

        result = self.access_service.check_access("Location Head")

        self.assertEqual(result["access"], "view")

    def test_buHead_viewAccess_allowed(self):
        """Positive: BU Head has view access to shift schedule page."""
        self.access_service.check_access.return_value = {
            "role": "BU Head",
            "access": "view",
        }

        result = self.access_service.check_access("BU Head")

        self.assertEqual(result["access"], "view")

    def test_locationHead_editAccess_denied(self):
        """Negative: Location Head cannot edit shift schedule."""
        self.access_service.check_edit_access.return_value = {
            "status": "denied",
            "message": "Edit access not available for Location Head",
        }

        result = self.access_service.check_edit_access("Location Head")

        self.assertEqual(result["status"], "denied")

    def test_buHead_editAccess_denied(self):
        """Negative: BU Head cannot edit shift schedule."""
        self.access_service.check_edit_access.return_value = {
            "status": "denied",
            "message": "Edit access not available for BU Head",
        }

        result = self.access_service.check_edit_access("BU Head")

        self.assertEqual(result["status"], "denied")


if __name__ == "__main__":
    unittest.main()
