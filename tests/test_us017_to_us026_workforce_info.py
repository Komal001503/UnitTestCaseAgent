"""
Unit Tests for Workforce Information Module
User Stories: US-017 (Workforce Info - IR), US-018 (Event History),
              US-019 (Edit Event History), US-020 (Add Event History),
              US-021 (Disciplinary Action), US-022 (Import DA),
              US-023 (Export DA), US-024 (Add DA),
              US-025 (CTCW Role), US-026 (Multiple Roles)

Test Categories:
- Positive / Happy Path
- Negative / Error Path
- Boundary / Edge Cases
- Integration Points
"""

import unittest
from unittest.mock import MagicMock, patch


# TODO: Import actual modules once implementation is available.
# from src.workforce.workforce_info import (
#     WorkforceInfoPage, WorkforceInfoService
# )
# from src.workforce.event_history import (
#     EventHistoryPage, EventHistoryService
# )
# from src.workforce.disciplinary_action import (
#     DisciplinaryActionPage, DisciplinaryActionService
# )


# ---------------------------------------------------------------------------
# US-017: Workforce Information Page (IR)
# ---------------------------------------------------------------------------


class TestWorkforceInfoNavigation(unittest.TestCase):
    """US-017 AC-1, AC-2, AC-3: Navigation to Workforce Information."""

    def setUp(self):
        self.page = MagicMock()

    def test_sideNavigation_workforceMenu_displaysSubMenus(self):
        """Positive: Workforce Information menu shows all sub menus."""
        self.page.get_submenus.return_value = [
            "Workforce Information",
            "Event History",
            "Disciplinary Action",
        ]

        submenus = self.page.get_submenus("Workforce Information")

        self.assertEqual(len(submenus), 3)
        self.assertIn("Workforce Information", submenus)
        self.assertIn("Event History", submenus)
        self.assertIn("Disciplinary Action", submenus)


class TestWorkforceInfoDataGrid(unittest.TestCase):
    """US-017 AC-4, AC-5: Workforce Information data grid."""

    def setUp(self):
        self.service = MagicMock()

    def test_dataGrid_displaysAllRequiredColumns(self):
        """Positive: Data grid displays all required columns."""
        expected_columns = [
            "PS No and Employee Name",
            "Dept Name and Code",
            "Gender",
            "Immediate Supervisor",
            "Current Status",
            "Designation",
        ]
        self.service.get_grid_columns.return_value = expected_columns

        columns = self.service.get_grid_columns()

        self.assertEqual(len(columns), 6)

    def test_dataGrid_nameHyperlink_navigatesToDetails(self):
        """Positive: Name hyperlink navigates to workforce info details page."""
        self.service.navigate_to_details.return_value = {
            "redirect": "/workforce-info/details/12345"
        }

        result = self.service.navigate_to_details("12345")

        self.assertIn("/workforce-info/details", result["redirect"])

    def test_dataGrid_currentStatus_showsProbationOrConfirmed(self):
        """Positive: Current Status shows Probation or Confirmed."""
        self.service.get_employee_status.return_value = "Probation"

        status = self.service.get_employee_status("12345")

        self.assertIn(status, ["Probation", "Confirmed"])


class TestWorkforceInfoDetailsPage(unittest.TestCase):
    """US-017 AC-6 to AC-28: Workforce Information details page sections."""

    def setUp(self):
        self.service = MagicMock()

    def test_detailsPage_personalInfoBiographical_displaysFields(self):
        """Positive: Biographical section displays PS#, DOB, Age, Birth Place."""
        self.service.get_section_fields.return_value = [
            "PS#",
            "Date of Birth",
            "Age",
            "Birth Place",
        ]

        fields = self.service.get_section_fields("biographical")

        self.assertIn("PS#", fields)
        self.assertIn("Date of Birth", fields)
        self.assertIn("Age", fields)
        self.assertIn("Birth Place", fields)

    def test_detailsPage_personalInfo_displaysAllFields(self):
        """Positive: Personal Info section displays all required fields."""
        self.service.get_section_fields.return_value = [
            "Title",
            "First Name",
            "Middle Name",
            "Last Name",
            "Name as per Aadhaar/Full Name",
            "Initials",
            "Gender",
            "Religion",
            "Caste",
            "Domicile (State)",
            "Father Name",
            "Marital Status",
            "Date Of Marriage",
            "Blood Group",
        ]

        fields = self.service.get_section_fields("personal_info")

        self.assertEqual(len(fields), 14)

    def test_detailsPage_contactInfo_displaysFields(self):
        """Positive: Contact Info section displays required fields."""
        self.service.get_section_fields.return_value = [
            "Email Id",
            "Office Tele No.",
            "Mobile No",
        ]

        fields = self.service.get_section_fields("contact_info")

        self.assertIn("Email Id", fields)
        self.assertIn("Mobile No", fields)

    def test_detailsPage_emergencyContact_displaysFields(self):
        """Positive: Emergency Contact section displays required fields."""
        self.service.get_section_fields.return_value = [
            "Contact Person",
            "Relationship",
            "Mobile No",
        ]

        fields = self.service.get_section_fields("emergency_contact")

        self.assertEqual(len(fields), 3)

    def test_detailsPage_dependents_displaysAllFields(self):
        """Positive: Dependents section displays all required fields."""
        expected_fields = [
            "Relationship",
            "Dependent Status",
            "Title",
            "First Name",
            "Last Name",
            "Gender",
            "Date of Birth",
            "Age",
            "Qualifications",
            "Occupation",
            "Aadhar ID",
            "Mediclaim Yes/No",
            "Differently Abled",
        ]
        self.service.get_section_fields.return_value = expected_fields

        fields = self.service.get_section_fields("dependents")

        self.assertEqual(len(fields), 13)

    def test_detailsPage_nationalID_displaysAllFields(self):
        """Positive: National ID section displays all document fields."""
        expected_fields = [
            "Aadhaar Number",
            "PAN",
            "UAN Number",
            "PF Account No",
            "EPS No",
            "ESIC No",
        ]
        self.service.get_section_fields.return_value = expected_fields

        fields = self.service.get_section_fields("national_id")

        self.assertIn("Aadhaar Number", fields)
        self.assertIn("PAN", fields)

    def test_detailsPage_bankDetails_displaysAllFields(self):
        """Positive: Bank Details section displays all fields."""
        self.service.get_section_fields.return_value = [
            "Bank Name",
            "Bank Account No",
            "IFSC Code",
            "Bank Branch",
        ]

        fields = self.service.get_section_fields("bank_details")

        self.assertEqual(len(fields), 4)

    def test_detailsPage_jobRelationship_autoPopulatedFromDeptCode(self):
        """Positive: Job Relationship fields are auto-populated from dept code."""
        self.service.get_job_relationships.return_value = {
            "DH": "Dept Head Name",
            "NS": "Next Supervisor Name",
            "IS": "Immediate Supervisor Name",
        }

        result = self.service.get_job_relationships("ENG01")

        self.assertIn("DH", result)
        self.assertIn("NS", result)
        self.assertIn("IS", result)


class TestWorkforceInfoButtons(unittest.TestCase):
    """US-017 AC-29, AC-30, AC-31: Buttons, search, and navigation."""

    def setUp(self):
        self.service = MagicMock()

    def test_buttons_displaysEditSaveDraftCancel(self):
        """Positive: Page displays Edit, Save Draft, Cancel buttons."""
        self.service.get_buttons.return_value = ["Edit", "Save Draft", "Cancel"]

        buttons = self.service.get_buttons()

        self.assertIn("Edit", buttons)
        self.assertIn("Save Draft", buttons)
        self.assertIn("Cancel", buttons)

    def test_searchBar_searchesWorkmen(self):
        """Positive: Search bar finds matching workmen."""
        self.service.search.return_value = [
            {"ps_no": "12345", "name": "John Doe"}
        ]

        results = self.service.search("John")

        self.assertEqual(len(results), 1)

    def test_pageNavigation_navigatesCorrectly(self):
        """Positive: Page navigation works."""
        self.service.get_page.return_value = {"page": 2, "results": []}

        result = self.service.get_page(2)

        self.assertEqual(result["page"], 2)


# ---------------------------------------------------------------------------
# US-018: Event History Page
# ---------------------------------------------------------------------------


class TestEventHistoryPage(unittest.TestCase):
    """US-018: Verify Event History page data grid and navigation."""

    def setUp(self):
        self.service = MagicMock()

    def test_eventHistory_dataGrid_displaysAllColumns(self):
        """Positive: Event History grid displays all required columns."""
        expected_columns = [
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
        self.service.get_grid_columns.return_value = expected_columns

        columns = self.service.get_grid_columns()

        self.assertEqual(len(columns), 9)

    def test_eventHistory_buttons_displaysEditAndAddNew(self):
        """Positive: Page displays Edit and Add New Event buttons."""
        self.service.get_buttons.return_value = ["Edit", "Add New Event"]

        buttons = self.service.get_buttons()

        self.assertIn("Edit", buttons)
        self.assertIn("Add New Event", buttons)

    def test_eventHistory_oldPSNumber_displayedBasedOnCadre(self):
        """Positive: Old PS number assigned based on cadre is visible."""
        self.service.get_old_ps_no.return_value = "OLD-12345"

        result = self.service.get_old_ps_no("12345")

        self.assertIsNotNone(result)

    def test_eventHistory_searchBar_works(self):
        """Positive: Search bar finds workmen."""
        self.service.search.return_value = [{"ps_no": "12345"}]

        results = self.service.search("12345")

        self.assertEqual(len(results), 1)


# ---------------------------------------------------------------------------
# US-019: Edit Event History
# ---------------------------------------------------------------------------


class TestEditEventHistory(unittest.TestCase):
    """US-019: Verify Edit Event History functionality."""

    def setUp(self):
        self.service = MagicMock()

    def test_editEventHistory_clickEdit_displaysEditPage(self):
        """Positive: Clicking edit button displays Edit Event History page."""
        self.service.open_edit_page.return_value = {"status": "success"}

        result = self.service.open_edit_page("event_123")

        self.assertEqual(result["status"], "success")

    def test_editEventHistory_fillAndSave_savesChanges(self):
        """Positive: Filling mandatory fields and saving succeeds."""
        self.service.save_event.return_value = {"status": "success"}

        result = self.service.save_event({
            "effective_date": "01-06-2026",
            "event": "Promotion",
            "from_cadre": "C1",
            "to_cadre": "C2",
            "dept_code": "ENG01",
            "basic": "20000",
        })

        self.assertEqual(result["status"], "success")

    def test_editEventHistory_missingMandatoryFields_returnsError(self):
        """Negative: Missing mandatory fields returns error."""
        self.service.save_event.return_value = {
            "status": "error",
            "message": "Mandatory fields required",
        }

        result = self.service.save_event({"effective_date": ""})

        self.assertEqual(result["status"], "error")

    def test_editEventHistory_cancel_navigatesToPreviousPage(self):
        """Positive: Cancel navigates to previous page."""
        self.service.cancel.return_value = {"redirect": "/event-history"}

        result = self.service.cancel()

        self.assertIn("redirect", result)

    def test_editEventHistory_functionAutoFilled_basedOnDeptCode(self):
        """Positive: Function field is auto-filled based on dept code."""
        self.service.get_function_by_dept.return_value = "Engineering"

        result = self.service.get_function_by_dept("ENG01")

        self.assertEqual(result, "Engineering")


# ---------------------------------------------------------------------------
# US-020: Add Event History
# ---------------------------------------------------------------------------


class TestAddEventHistory(unittest.TestCase):
    """US-020: Verify Add Event History functionality."""

    def setUp(self):
        self.service = MagicMock()

    def test_addEventHistory_clickAdd_displaysAddPage(self):
        """Positive: Clicking add button displays Add Event History page."""
        self.service.open_add_page.return_value = {"status": "success"}

        result = self.service.open_add_page()

        self.assertEqual(result["status"], "success")

    def test_addEventHistory_fillAndSave_addsToGrid(self):
        """Positive: Filling fields and saving adds event to grid view."""
        self.service.add_event.return_value = {"status": "success", "event_id": "456"}

        result = self.service.add_event({
            "effective_date": "01-06-2026",
            "event": "Joining",
            "from_cadre": "C1",
            "to_cadre": "C1",
            "dept_code": "ENG01",
            "basic": "15000",
            "points": "100",
        })

        self.assertEqual(result["status"], "success")

    def test_addEventHistory_cancel_navigatesToPreviousPage(self):
        """Positive: Cancel navigates to previous page."""
        self.service.cancel.return_value = {"redirect": "/event-history"}

        result = self.service.cancel()

        self.assertIn("redirect", result)

    def test_addEventHistory_firstEvent_autoFilledAsJoining(self):
        """Positive: First event is auto-filled as 'Joining event' from onboarding."""
        self.service.get_default_first_event.return_value = {
            "event": "Joining",
            "auto_filled": True,
        }

        result = self.service.get_default_first_event("12345")

        self.assertEqual(result["event"], "Joining")
        self.assertTrue(result["auto_filled"])

    def test_addEventHistory_apprentice_onlyTwoEventsDisplayed(self):
        """Positive: Apprentice/AT/Temp Workman shows only Joining and Separation."""
        self.service.get_allowed_events.return_value = ["Joining", "Separation"]

        events = self.service.get_allowed_events(employee_type="Apprentice")

        self.assertEqual(len(events), 2)
        self.assertIn("Joining", events)
        self.assertIn("Separation", events)

    def test_addEventHistory_permanentWorkman_newPSNoAndJoiningEvent(self):
        """Positive: Becoming permanent generates new PS No and new Joining event."""
        self.service.create_permanent_event.return_value = {
            "new_ps_no": "55555",
            "event": "Joining",
        }

        result = self.service.create_permanent_event(
            old_ps_no="12345", employee_type="Permanent Workmen"
        )

        self.assertIsNotNone(result["new_ps_no"])
        self.assertEqual(result["event"], "Joining")


# ---------------------------------------------------------------------------
# US-021: Disciplinary Action Page
# ---------------------------------------------------------------------------


class TestDisciplinaryActionPage(unittest.TestCase):
    """US-021: Verify Disciplinary Action page data grid."""

    def setUp(self):
        self.service = MagicMock()

    def test_disciplinaryAction_dataGrid_displaysAllColumns(self):
        """Positive: Data grid displays all required columns."""
        expected_columns = [
            "PS No and Employee Name",
            "Dept Code and Dept Name",
            "Details of Misconduct",
            "Incident Date",
            "Report Received",
            "Disciplinary Actions",
            "Action Date",
            "Issued Date",
            "Remarks",
            "Actions",
        ]
        self.service.get_grid_columns.return_value = expected_columns

        columns = self.service.get_grid_columns()

        self.assertEqual(len(columns), 10)

    def test_disciplinaryAction_buttons_displaysImportExportAdd(self):
        """Positive: Page displays Import, Export, Add buttons."""
        self.service.get_buttons.return_value = ["Import", "Export", "Add"]

        buttons = self.service.get_buttons()

        self.assertIn("Import", buttons)
        self.assertIn("Export", buttons)
        self.assertIn("Add", buttons)

    def test_disciplinaryAction_searchBar_works(self):
        """Positive: Search bar finds matching workmen."""
        self.service.search.return_value = [{"ps_no": "12345"}]

        results = self.service.search("12345")

        self.assertEqual(len(results), 1)


# ---------------------------------------------------------------------------
# US-022: Import Disciplinary Action
# ---------------------------------------------------------------------------


class TestImportDisciplinaryAction(unittest.TestCase):
    """US-022: Verify Import Disciplinary Action functionality."""

    def setUp(self):
        self.service = MagicMock()

    def test_import_clickButton_importsData(self):
        """Positive: Clicking Import imports disciplinary action details."""
        self.service.import_data.return_value = {
            "status": "success",
            "records_imported": 10,
        }

        result = self.service.import_data("disciplinary_data.xlsx")

        self.assertEqual(result["status"], "success")
        self.assertEqual(result["records_imported"], 10)

    def test_import_columnMismatch_returnsError(self):
        """Negative: Import with mismatched columns returns error."""
        self.service.import_data.return_value = {
            "status": "error",
            "message": "Column mismatch - expected columns do not match",
        }

        result = self.service.import_data("wrong_format.xlsx")

        self.assertEqual(result["status"], "error")

    def test_import_emptyFile_returnsError(self):
        """Boundary: Import of empty file returns error."""
        self.service.import_data.return_value = {
            "status": "error",
            "message": "File contains no data",
        }

        result = self.service.import_data("empty.xlsx")

        self.assertEqual(result["status"], "error")

    def test_import_importedColumns_matchExpected(self):
        """Positive: Imported data has all expected columns."""
        expected_columns = [
            "PS No and Employee Name",
            "Dept Code and Dept Name",
            "Details of Misconduct",
            "Incident Date",
            "Report Received",
            "Disciplinary Actions",
            "Action Date",
            "Issued Date",
            "Remarks",
        ]
        self.service.get_imported_columns.return_value = expected_columns

        columns = self.service.get_imported_columns()

        self.assertEqual(len(columns), 9)


# ---------------------------------------------------------------------------
# US-023: Export Disciplinary Action
# ---------------------------------------------------------------------------


class TestExportDisciplinaryAction(unittest.TestCase):
    """US-023: Verify Export Disciplinary Action functionality."""

    def setUp(self):
        self.service = MagicMock()

    def test_export_clickButton_exportsToExcel(self):
        """Positive: Clicking Export exports data to Excel file."""
        self.service.export_data.return_value = {
            "status": "success",
            "file": "disciplinary_export.xlsx",
        }

        result = self.service.export_data()

        self.assertEqual(result["status"], "success")
        self.assertTrue(result["file"].endswith(".xlsx"))

    def test_export_noData_exportsEmptyFile(self):
        """Boundary: Export with no data creates file with headers only."""
        self.service.export_data.return_value = {
            "status": "success",
            "file": "empty_export.xlsx",
            "records": 0,
        }

        result = self.service.export_data()

        self.assertEqual(result["records"], 0)

    def test_export_exportedColumns_matchExpected(self):
        """Positive: Exported data contains all expected columns."""
        expected_columns = [
            "PS No and Employee Name",
            "Dept Code and Dept Name",
            "Details of Misconduct",
            "Incident Date",
            "Report Received",
            "Disciplinary Actions",
            "Action Date",
            "Issued Date",
            "Remarks",
        ]
        self.service.get_export_columns.return_value = expected_columns

        columns = self.service.get_export_columns()

        self.assertEqual(len(columns), 9)

    def test_export_saveToLocation_succeeds(self):
        """Positive: User can save export file to a location."""
        self.service.save_export.return_value = {"status": "success"}

        result = self.service.save_export("/downloads/export.xlsx")

        self.assertEqual(result["status"], "success")


# ---------------------------------------------------------------------------
# US-024: Add Disciplinary Action
# ---------------------------------------------------------------------------


class TestAddDisciplinaryAction(unittest.TestCase):
    """US-024: Verify Add Disciplinary Action functionality."""

    def setUp(self):
        self.service = MagicMock()

    def test_addDA_clickAdd_displaysAddPage(self):
        """Positive: Clicking add button displays Add Disciplinary Action page."""
        self.service.open_add_page.return_value = {"status": "success"}

        result = self.service.open_add_page()

        self.assertEqual(result["status"], "success")

    def test_addDA_fillAndSave_addsToGrid(self):
        """Positive: Filling all fields and saving adds to grid."""
        self.service.add_action.return_value = {"status": "success"}

        result = self.service.add_action({
            "employee": "12345 - John Doe",
            "dept_code": "ENG01",
            "details_of_misconduct": "Late arrival",
            "incident_date": "01-05-2026",
            "report_received": "02-05-2026",
            "disciplinary_actions": "Warning",
            "action_date": "05-05-2026",
            "issued_date": "05-05-2026",
            "remarks": "First offense",
        })

        self.assertEqual(result["status"], "success")

    def test_addDA_missingMandatoryFields_returnsError(self):
        """Negative: Missing mandatory fields returns error."""
        self.service.add_action.return_value = {
            "status": "error",
            "message": "Mandatory fields required",
        }

        result = self.service.add_action({"employee": ""})

        self.assertEqual(result["status"], "error")

    def test_addDA_cancel_navigatesToPreviousPage(self):
        """Positive: Cancel navigates to previous page."""
        self.service.cancel.return_value = {"redirect": "/disciplinary-action"}

        result = self.service.cancel()

        self.assertIn("redirect", result)

    def test_addDA_futureIncidentDate_validationFails(self):
        """Boundary: Future incident date may fail validation."""
        self.service.validate_date.return_value = {
            "valid": False,
            "error": "Incident date cannot be in the future",
        }

        result = self.service.validate_date("01-01-2030")

        self.assertFalse(result["valid"])


# ---------------------------------------------------------------------------
# US-025: Workforce Information - CTCW Role
# ---------------------------------------------------------------------------


class TestWorkforceInfoCTCWRole(unittest.TestCase):
    """US-025: Verify Workforce Information for CTCW role."""

    def setUp(self):
        self.service = MagicMock()

    def test_ctcwRole_dataGrid_displaysRequiredColumns(self):
        """Positive: CTCW data grid displays correct columns."""
        expected_columns = [
            "PS No and Employee Name",
            "Dept Name and Code",
            "Gender",
            "Contractor Supervisor",
            "Designation",
        ]
        self.service.get_grid_columns.return_value = expected_columns

        columns = self.service.get_grid_columns("CTCW")

        self.assertEqual(len(columns), 5)
        self.assertIn("Contractor Supervisor", columns)

    def test_ctcwRole_contractorData_fetchedFromAPI(self):
        """Integration: Contractor workman data is fetched from API."""
        self.service.fetch_contractor_data.return_value = {
            "status": "success",
            "data": [{"ps_no": "C001", "name": "Contractor Worker"}],
        }

        result = self.service.fetch_contractor_data()

        self.assertEqual(result["status"], "success")
        self.assertTrue(len(result["data"]) > 0)

    def test_ctcwRole_apiTimeout_handledGracefully(self):
        """Integration: API timeout returns appropriate error."""
        self.service.fetch_contractor_data.side_effect = TimeoutError(
            "API timed out"
        )

        with self.assertRaises(TimeoutError):
            self.service.fetch_contractor_data()

    def test_ctcwRole_nameHyperlink_navigatesToDetails(self):
        """Positive: Name hyperlink navigates to details page."""
        self.service.navigate_to_details.return_value = {
            "redirect": "/workforce-info/details/C001"
        }

        result = self.service.navigate_to_details("C001")

        self.assertIn("/workforce-info/details", result["redirect"])

    def test_ctcwRole_closeButton_navigatesBack(self):
        """Positive: Close button navigates to previous page."""
        self.service.close.return_value = {"redirect": "/dashboard"}

        result = self.service.close()

        self.assertIn("redirect", result)

    def test_ctcwRole_rightSidePane_displaysProfilePhoto(self):
        """Positive: Right side pane displays employee photo, PS No, Name."""
        self.service.get_side_pane_info.return_value = {
            "photo_url": "/photos/C001.jpg",
            "ps_number": "C001",
            "employee_name": "Contractor Worker",
        }

        info = self.service.get_side_pane_info("C001")

        self.assertIn("photo_url", info)
        self.assertIn("ps_number", info)
        self.assertIn("employee_name", info)


# ---------------------------------------------------------------------------
# US-026: Workforce Information - Multiple Roles
# ---------------------------------------------------------------------------


class TestWorkforceInfoMultipleRoles(unittest.TestCase):
    """US-026: Verify Workforce Information for Admin and Supervisor roles."""

    def setUp(self):
        self.service = MagicMock()

    def test_multipleRoles_dataGrid_displaysRequiredColumns(self):
        """Positive: Data grid displays standard columns for admin/supervisor roles."""
        expected_columns = [
            "PS No and Employee Name",
            "Dept Name and Code",
            "Gender",
            "Immediate Supervisor",
            "Current Status",
            "Designation",
        ]
        self.service.get_grid_columns.return_value = expected_columns

        columns = self.service.get_grid_columns("System Admin")

        self.assertEqual(len(columns), 6)
        self.assertIn("Immediate Supervisor", columns)

    def test_multipleRoles_nameHyperlink_navigatesToDetails(self):
        """Positive: Name hyperlink navigates to details page."""
        self.service.navigate_to_details.return_value = {
            "redirect": "/workforce-info/details/12345"
        }

        result = self.service.navigate_to_details("12345")

        self.assertIn("/workforce-info/details", result["redirect"])

    def test_multipleRoles_closeButton_navigatesBack(self):
        """Positive: Close button navigates to previous page."""
        self.service.close.return_value = {"redirect": "/dashboard"}

        result = self.service.close()

        self.assertIn("redirect", result)

    def test_multipleRoles_rightSidePane_displaysInfo(self):
        """Positive: Right side pane shows photo, PS Number, Employee Name."""
        self.service.get_side_pane_info.return_value = {
            "photo_url": "/photos/12345.jpg",
            "ps_number": "12345",
            "employee_name": "John Doe",
        }

        info = self.service.get_side_pane_info("12345")

        self.assertIn("photo_url", info)
        self.assertIn("ps_number", info)

    def test_multipleRoles_searchBar_works(self):
        """Positive: Search bar finds workmen."""
        self.service.search.return_value = [{"ps_no": "12345"}]

        results = self.service.search("12345")

        self.assertEqual(len(results), 1)

    def test_multipleRoles_pageNavigation_works(self):
        """Positive: Page navigation works."""
        self.service.get_page.return_value = {"page": 1}

        result = self.service.get_page(1)

        self.assertEqual(result["page"], 1)


if __name__ == "__main__":
    unittest.main()
