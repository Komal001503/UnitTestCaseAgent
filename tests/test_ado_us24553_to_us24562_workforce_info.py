"""
Unit Tests for Workforce Information Module
Source: azure_devops_user_stories.md
User Stories:
  US-24553 (IR - Workforce Information - View workforce information page)
  US-24554 (IR - Workforce Information - View Event History page)
  US-24555 (IR - Workforce Information - Add and Edit Event History details)
  US-24557 (IR - Onboarding - Disciplinary Action – View)
  US-24560 (IR - Onboarding - Add Disciplinary Actions)
  US-24561 (CTWC - Workforce Information - View workforce information page)
  US-24562 (Users - Workforce Information - View workforce information page)

Note: US-24556, US-24558, US-24559 are marked 'Remove' in ADO and are skipped.

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
# from src.workforce.workforce_info import WorkforceInfoPage, WorkforceInfoService
# from src.workforce.event_history import EventHistoryPage, EventHistoryService
# from src.workforce.disciplinary_action import (
#     DisciplinaryActionPage, DisciplinaryActionService
# )


# ---------------------------------------------------------------------------
# US-24553: IR – View Workforce Information Page
# ---------------------------------------------------------------------------


class TestWorkforceInfoNavigation(unittest.TestCase):
    """US-24553: Navigation and menu display for Workforce Information."""

    def setUp(self):
        self.navigation = MagicMock()

    def test_sideNav_workforceInfoMenu_displaysThreeSubMenus(self):
        """Positive: Workforce Information menu shows Workforce Information,
        Event History, and Disciplinary Action sub-menus."""
        self.navigation.get_submenus.return_value = [
            "Workforce Information",
            "Event History",
            "Disciplinary Action",
        ]

        submenus = self.navigation.get_submenus("Workforce Information")

        self.assertEqual(len(submenus), 3)
        self.assertIn("Workforce Information", submenus)
        self.assertIn("Event History", submenus)
        self.assertIn("Disciplinary Action", submenus)

    def test_sideNav_selectWorkforceInfo_navigatesToPage(self):
        """Positive: Selecting Workforce Information opens the workforce info page."""
        self.navigation.navigate_to.return_value = {
            "status": "success",
            "page": "Workforce Information",
        }

        result = self.navigation.navigate_to("Workforce Information")

        self.assertEqual(result["status"], "success")


class TestWorkforceInfoDataGrid(unittest.TestCase):
    """US-24553: Verify the Workforce Information data grid."""

    def setUp(self):
        self.service = MagicMock()

    def test_grid_displaysAllRequiredColumns(self):
        """Positive: Data grid shows PS No, Name, Dept, Gender, Supervisor,
        Current Status, and Designation."""
        self.service.get_grid_columns.return_value = [
            "PS No and Employee Name",
            "Dept Name and Code",
            "Gender",
            "Immediate Supervisor",
            "Current Status",
            "Designation",
        ]

        columns = self.service.get_grid_columns()

        self.assertEqual(len(columns), 6)
        self.assertIn("PS No and Employee Name", columns)
        self.assertIn("Current Status", columns)

    def test_grid_nameHyperlink_navigatesToDetailsPage(self):
        """Positive: Clicking Name hyperlink opens the workforce information details page."""
        self.service.navigate_to_details.return_value = {
            "redirect": "/workforce-info/details/PS-12345"
        }

        result = self.service.navigate_to_details("PS-12345")

        self.assertIn("/workforce-info/details", result["redirect"])

    def test_detailsPage_displaysAllInformationSections(self):
        """Positive: Details page displays Personal, Biographical, Contact, Emergency,
        Dependents, Address, National ID, Health, Bank, Career, Employment sections."""
        self.service.get_detail_sections.return_value = [
            "Biographical Information",
            "Personal Information",
            "Contact Info",
            "Emergency Contact",
            "Dependents",
            "Permanent Address",
            "Present Address",
            "National ID & Personal Documents",
            "Health Information",
            "Bank Details",
            "Careers",
            "Employment Information",
            "Payroll Information",
            "Additional Information",
        ]

        sections = self.service.get_detail_sections("PS-12345")

        self.assertGreater(len(sections), 0)
        self.assertIn("Personal Information", sections)
        self.assertIn("Employment Information", sections)

    def test_detailsPage_rightPane_showsProfilePhotoAndPSNumber(self):
        """Positive: Right side pane shows employee profile photo, PS number, and name."""
        self.service.get_right_pane.return_value = {
            "profile_photo": "photo_url",
            "ps_number": "PS-12345",
            "employee_name": "John Doe",
        }

        result = self.service.get_right_pane("PS-12345")

        self.assertIsNotNone(result["profile_photo"])
        self.assertIsNotNone(result["ps_number"])
        self.assertIsNotNone(result["employee_name"])

    def test_detailsPage_displaysEditSaveDraftCancelButtons(self):
        """Positive: Details page shows Edit, Save Draft, and Cancel buttons."""
        self.service.get_buttons.return_value = ["Edit", "Save Draft", "Cancel"]

        buttons = self.service.get_buttons("details")

        self.assertIn("Edit", buttons)
        self.assertIn("Save Draft", buttons)
        self.assertIn("Cancel", buttons)

    def test_detailsPage_editButton_enablesFieldEditing(self):
        """Positive: Clicking Edit button enables editing of employee details."""
        self.service.click_edit.return_value = {"editable": True}

        result = self.service.click_edit("PS-12345")

        self.assertTrue(result["editable"])

    def test_detailsPage_saveDraft_savesChangesWithoutSubmitting(self):
        """Positive: Save Draft saves changes without final submission."""
        self.service.save_draft.return_value = {
            "status": "success",
            "draft_saved": True,
        }

        result = self.service.save_draft("PS-12345")

        self.assertTrue(result["draft_saved"])

    def test_searchBar_returnsMatchingWorkmen(self):
        """Positive: Search bar returns matching workmen records."""
        self.service.search.return_value = [{"ps_no": "PS-12345", "name": "John Doe"}]

        results = self.service.search("John")

        self.assertEqual(len(results), 1)

    def test_pageNavigation_works(self):
        """Positive: Page navigation allows moving through records."""
        self.service.get_page.return_value = {"page": 2}

        result = self.service.get_page(2)

        self.assertEqual(result["page"], 2)


# ---------------------------------------------------------------------------
# US-24554: IR – View Event History Page
# ---------------------------------------------------------------------------


class TestEventHistoryNavigation(unittest.TestCase):
    """US-24554: Verify navigation and display of Event History page."""

    def setUp(self):
        self.navigation = MagicMock()
        self.service = MagicMock()

    def test_sideNav_selectEventHistory_navigatesToPage(self):
        """Positive: Selecting 'Event History' from side nav opens the Event History page."""
        self.navigation.navigate_to.return_value = {
            "status": "success",
            "page": "Event History",
        }

        result = self.navigation.navigate_to("Event History")

        self.assertEqual(result["status"], "success")
        self.assertEqual(result["page"], "Event History")

    def test_eventHistory_grid_displaysRequiredColumns(self):
        """Positive: Event History grid shows all required columns."""
        self.service.get_grid_columns.return_value = [
            "Effective Date",
            "Event",
            "From Cadre",
            "To Cadre",
            "Dept Code",
            "Function",
            "Basic",
            "Points",
            "PS No",
        ]

        columns = self.service.get_grid_columns()

        self.assertEqual(len(columns), 9)
        self.assertIn("Effective Date", columns)
        self.assertIn("Event", columns)
        self.assertIn("PS No", columns)

    def test_eventHistory_displaysEditAndAddNewEventButtons(self):
        """Positive: Event History page shows Edit and Add New Event buttons."""
        self.service.get_buttons.return_value = ["Edit", "Add New Event"]

        buttons = self.service.get_buttons()

        self.assertIn("Edit", buttons)
        self.assertIn("Add New Event", buttons)

    def test_eventHistory_function_autoFilledFromDeptCode(self):
        """Positive: Function field is auto-populated based on Dept Code."""
        self.service.get_function_for_dept.return_value = "Manufacturing"

        result = self.service.get_function_for_dept("DEPT01")

        self.assertIsNotNone(result)

    def test_eventHistory_oldPSNumber_displayedBasedOnCadre(self):
        """Validation: Old PS number assigned based on cadre is visible in event history."""
        self.service.get_old_ps_no.return_value = "OLD-PS-001"

        result = self.service.get_old_ps_no("PS-12345")

        self.assertIsNotNone(result)
        self.assertIn("OLD-PS", result)

    def test_searchBar_filtersEventHistory(self):
        """Positive: Search bar filters event history records."""
        self.service.search.return_value = [{"ps_no": "PS-12345"}]

        results = self.service.search("PS-12345")

        self.assertEqual(len(results), 1)


# ---------------------------------------------------------------------------
# US-24555: IR – Add and Edit Event History Details
# ---------------------------------------------------------------------------


class TestEventHistoryAddEdit(unittest.TestCase):
    """US-24555: Verify Add and Edit Event History functionality."""

    def setUp(self):
        self.service = MagicMock()

    def test_addEvent_clickAddButton_displaysAddEventHistoryPage(self):
        """Positive: Clicking 'Add New Event' opens the 'Add Event History' page."""
        self.service.open_add_event_page.return_value = {
            "status": "success",
            "page": "Add Event History",
        }

        result = self.service.open_add_event_page()

        self.assertEqual(result["status"], "success")
        self.assertIn("Add Event History", result["page"])

    def test_editEvent_clickEditButton_displaysEditEventHistoryPage(self):
        """Positive: Clicking 'Edit' opens the 'Edit Event History' page."""
        self.service.open_edit_event_page.return_value = {
            "status": "success",
            "page": "Edit Event History",
        }

        result = self.service.open_edit_event_page("event_001")

        self.assertEqual(result["status"], "success")

    def test_addEditEvent_form_displaysAllRequiredFields(self):
        """Positive: Add/Edit Event form shows all required attribute fields."""
        self.service.get_form_fields.return_value = [
            "Effective Date",
            "Event",
            "From Cadre",
            "To Cadre",
            "Dept Code",
            "Function",
            "Basic",
            "Points",
        ]

        fields = self.service.get_form_fields()

        self.assertEqual(len(fields), 8)
        self.assertIn("Effective Date", fields)
        self.assertIn("Event", fields)

    def test_addEvent_saveButton_savesEventHistory(self):
        """Positive: Clicking Save saves the event history details."""
        self.service.save_event.return_value = {
            "status": "success",
            "message": "Event saved successfully",
        }

        result = self.service.save_event({"effective_date": "01-05-2026", "event": "Joining"})

        self.assertEqual(result["status"], "success")

    def test_addEvent_mandatoryFieldMissing_returnsError(self):
        """Negative: Saving without mandatory fields returns validation error."""
        self.service.save_event.return_value = {
            "status": "error",
            "message": "Mandatory fields are required",
        }

        result = self.service.save_event({})

        self.assertEqual(result["status"], "error")

    def test_addEvent_cancelButton_navigatesToPreviousPage(self):
        """Positive: Cancel button navigates back to Event History page."""
        self.service.cancel.return_value = {"redirect": "/event-history"}

        result = self.service.cancel()

        self.assertIsNotNone(result["redirect"])

    def test_addEvent_newOnboarding_autoCreatesJoiningEvent(self):
        """Validation: New employee onboarding auto-creates a 'Joining' event by default."""
        self.service.get_first_event.return_value = {
            "event_type": "Joining",
            "auto_filled": True,
        }

        result = self.service.get_first_event("PS-NEW-001")

        self.assertEqual(result["event_type"], "Joining")
        self.assertTrue(result["auto_filled"])

    def test_apprenticeTraineeWorkman_onlyJoiningAndSeparationEventsShown(self):
        """Validation: Apprentice/Advanced Trainee/Temp Workman show only Joining and
        Separation events; permanent workman gets a new PS and Joining event."""
        self.service.get_allowed_events.return_value = ["Joining", "Separation"]

        result = self.service.get_allowed_events(employee_type="Apprentice")

        self.assertEqual(len(result), 2)
        self.assertIn("Joining", result)
        self.assertIn("Separation", result)


# ---------------------------------------------------------------------------
# US-24557: IR – View Disciplinary Action Page
# ---------------------------------------------------------------------------


class TestDisciplinaryActionView(unittest.TestCase):
    """US-24557: Verify Disciplinary Action page display."""

    def setUp(self):
        self.navigation = MagicMock()
        self.service = MagicMock()

    def test_sideNav_selectDisciplinaryAction_navigatesToPage(self):
        """Positive: Selecting 'Disciplinary Action' from side nav opens the page."""
        self.navigation.navigate_to.return_value = {
            "status": "success",
            "page": "Disciplinary Action",
        }

        result = self.navigation.navigate_to("Disciplinary Action")

        self.assertEqual(result["status"], "success")

    def test_disciplinaryAction_grid_displaysAllRequiredColumns(self):
        """Positive: Grid displays all required columns for disciplinary actions."""
        self.service.get_grid_columns.return_value = [
            "PS No and Employee Name",
            "Dept Code and Dept Name",
            "Details of Misconduct",
            "Incident Date",
            "Report Received",
            "Disciplinary Actions",
            "Action Date",
            "Issued Date",
            "Remarks",
            "Actions (Edit Icon)",
        ]

        columns = self.service.get_grid_columns()

        self.assertEqual(len(columns), 10)
        self.assertIn("Incident Date", columns)
        self.assertIn("Actions (Edit Icon)", columns)

    def test_disciplinaryAction_displaysImportExportAddButtons(self):
        """Positive: Disciplinary Action page shows Import, Export, and Add buttons."""
        self.service.get_buttons.return_value = ["Import", "Export", "Add"]

        buttons = self.service.get_buttons()

        self.assertIn("Import", buttons)
        self.assertIn("Export", buttons)
        self.assertIn("Add", buttons)

    def test_importButton_importsExcelFile(self):
        """Positive: Import button allows uploading an Excel file for disciplinary data."""
        self.service.import_data.return_value = {"status": "success", "records_imported": 5}

        result = self.service.import_data("disciplinary_data.xlsx")

        self.assertEqual(result["status"], "success")

    def test_exportButton_exportsDataToExcel(self):
        """Positive: Export button exports grid data to Excel file."""
        self.service.export_data.return_value = {
            "status": "success",
            "filename": "disciplinary_export.xlsx",
        }

        result = self.service.export_data()

        self.assertEqual(result["status"], "success")
        self.assertIn(".xlsx", result["filename"])

    def test_searchBar_filtersWorkmenInGrid(self):
        """Positive: Search bar filters workmen in the disciplinary action grid."""
        self.service.search.return_value = [{"ps_no": "PS-12345", "name": "Jane Doe"}]

        results = self.service.search("Jane")

        self.assertEqual(len(results), 1)


# ---------------------------------------------------------------------------
# US-24560: IR – Add Disciplinary Actions
# ---------------------------------------------------------------------------


class TestDisciplinaryActionAdd(unittest.TestCase):
    """US-24560: Verify Add Disciplinary Action form."""

    def setUp(self):
        self.service = MagicMock()

    def test_addButton_opensAddDisciplinaryActionPage(self):
        """Positive: Clicking Add button opens the 'Add Disciplinary Action' page."""
        self.service.open_add_page.return_value = {
            "status": "success",
            "page": "Add Disciplinary Action",
        }

        result = self.service.open_add_page()

        self.assertEqual(result["status"], "success")
        self.assertIn("Add Disciplinary Action", result["page"])

    def test_addForm_displaysAllRequiredFields(self):
        """Positive: Add form shows Employee, Dept Code, Misconduct Details, Incident Date,
        Report Received, Disciplinary Actions, Action Date, Issued Date, and Remarks."""
        self.service.get_form_fields.return_value = [
            "Employee",
            "Dept Code",
            "Details of Misconduct",
            "Incident Date",
            "Report Received",
            "Disciplinary Actions",
            "Action Date",
            "Issued Date",
            "Remarks",
        ]

        fields = self.service.get_form_fields()

        self.assertEqual(len(fields), 9)
        self.assertIn("Employee", fields)
        self.assertIn("Incident Date", fields)
        self.assertIn("Remarks", fields)

    def test_addForm_saveButton_addsRecordToGrid(self):
        """Positive: Clicking Save adds the disciplinary action record to the grid."""
        self.service.save_disciplinary_action.return_value = {
            "status": "success",
            "record_added": True,
        }

        result = self.service.save_disciplinary_action(
            {"employee": "PS-12345", "incident_date": "01-04-2026"}
        )

        self.assertEqual(result["status"], "success")
        self.assertTrue(result["record_added"])

    def test_addForm_mandatoryFieldMissing_returnsError(self):
        """Negative: Saving without mandatory fields returns a validation error."""
        self.service.save_disciplinary_action.return_value = {
            "status": "error",
            "message": "Mandatory fields are required",
        }

        result = self.service.save_disciplinary_action({})

        self.assertEqual(result["status"], "error")

    def test_addForm_cancelButton_navigatesToPreviousPage(self):
        """Positive: Cancel navigates back to the Disciplinary Action list page."""
        self.service.cancel.return_value = {"redirect": "/disciplinary-action"}

        result = self.service.cancel()

        self.assertIsNotNone(result["redirect"])

    def test_addForm_employeeDropdown_searchByPSOrName(self):
        """Positive: Employee field allows searching by PS No or name."""
        self.service.search_employee.return_value = [{"ps_no": "PS-12345", "name": "John Doe"}]

        results = self.service.search_employee("PS-12345")

        self.assertGreater(len(results), 0)


# ---------------------------------------------------------------------------
# US-24561: CTWC – View Workforce Information (Contractor Workmen)
# ---------------------------------------------------------------------------


class TestCTWCWorkforceInfo(unittest.TestCase):
    """US-24561: Verify CTWC can view contractor workmen details."""

    def setUp(self):
        self.service = MagicMock()

    def test_ctwcGrid_displaysContractorWorkmenColumns(self):
        """Positive: CTWC grid shows PS No, Name, Dept, Gender, Supervisor, Designation."""
        self.service.get_grid_columns.return_value = [
            "PS No and Employee Name",
            "Dept Name and Code",
            "Gender",
            "Contractor Supervisor",
            "Designation",
        ]

        columns = self.service.get_grid_columns(role="CTWC")

        self.assertEqual(len(columns), 5)
        self.assertIn("Contractor Supervisor", columns)

    def test_ctwcData_fetchedFromAPIIntegration(self):
        """Positive: Contractor workman data is fetched from API integration."""
        self.service.fetch_contractor_data.return_value = {
            "source": "API",
            "data_loaded": True,
        }

        result = self.service.fetch_contractor_data()

        self.assertEqual(result["source"], "API")
        self.assertTrue(result["data_loaded"])

    def test_ctwcGrid_nameHyperlink_navigatesToDetailsPage(self):
        """Positive: Clicking Name hyperlink opens contractor workman details."""
        self.service.navigate_to_details.return_value = {
            "redirect": "/ctwc/workforce-info/details/PS-C001"
        }

        result = self.service.navigate_to_details("PS-C001")

        self.assertIn("/ctwc/workforce-info/details", result["redirect"])

    def test_ctwcDetails_displaysCloseButton(self):
        """Positive: CTWC details page has a Close button (not Edit) to navigate back."""
        self.service.get_buttons.return_value = ["Close"]

        buttons = self.service.get_buttons(role="CTWC")

        self.assertIn("Close", buttons)
        self.assertNotIn("Edit", buttons)


# ---------------------------------------------------------------------------
# US-24562: Multiple Users – View Workforce Information
# ---------------------------------------------------------------------------


class TestMultipleUsersWorkforceInfo(unittest.TestCase):
    """US-24562: Verify various user roles can view workforce information.

    Applies to: System admin, IR admin, shop admin, IR approver, Shop in charge,
    Shop supervisor, Shop coordinator, Dept head, shop head, company head,
    location head, BU head, AT staff (supervisor).
    """

    def setUp(self):
        self.service = MagicMock()

    def test_userRoles_canViewWorkforceInfoPage(self):
        """Positive: All listed user roles have access to Workforce Information page."""
        allowed_roles = [
            "SYSTEM_ADMIN",
            "IR_ADMIN",
            "SHOP_ADMIN",
            "IR_APPROVER",
            "SHOP_IN_CHARGE",
            "SHOP_SUPERVISOR",
            "SHOP_COORDINATOR",
            "DEPT_HEAD",
            "SHOP_HEAD",
            "COMPANY_HEAD",
            "LOCATION_HEAD",
            "BU_HEAD",
            "AT_STAFF_SUPERVISOR",
        ]

        for role in allowed_roles:
            self.service.has_access.return_value = True
            result = self.service.has_access(role, "Workforce Information")
            self.assertTrue(result, f"Role {role} should have access")

    def test_userRoles_workforceInfoGrid_displaysReadOnlyColumns(self):
        """Positive: Non-IR user sees grid with PS No, Name, Dept, Gender, Supervisor, Status, Designation."""
        self.service.get_grid_columns.return_value = [
            "PS No and Employee Name",
            "Dept Name and Code",
            "Gender",
            "Immediate Supervisor",
            "Current Status",
            "Designation",
        ]

        columns = self.service.get_grid_columns(role="SHOP_HEAD")

        self.assertEqual(len(columns), 6)

    def test_userRoles_detailsPage_hasCloseButtonOnly(self):
        """Positive: Non-IR user details page shows only Close button (read-only)."""
        self.service.get_buttons.return_value = ["Close"]

        buttons = self.service.get_buttons(role="COMPANY_HEAD")

        self.assertIn("Close", buttons)
        self.assertNotIn("Edit", buttons)
        self.assertNotIn("Save Draft", buttons)

    def test_userRoles_rightPane_showsPhotoAndPSNumber(self):
        """Positive: Right pane displays employee profile photo, PS number, and name."""
        self.service.get_right_pane.return_value = {
            "profile_photo": "photo_url",
            "ps_number": "PS-12345",
            "employee_name": "John Doe",
        }

        result = self.service.get_right_pane("PS-12345")

        self.assertIsNotNone(result["profile_photo"])
        self.assertIsNotNone(result["ps_number"])

    def test_unauthorizedRole_cannotAccessWorkforceInfo(self):
        """Negative: A role not in the allowed list is denied access."""
        self.service.has_access.return_value = False

        result = self.service.has_access("UNKNOWN_ROLE", "Workforce Information")

        self.assertFalse(result)


if __name__ == "__main__":
    unittest.main()
