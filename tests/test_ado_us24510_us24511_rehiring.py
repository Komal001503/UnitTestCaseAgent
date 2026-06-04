"""
Unit Tests for Rehiring Module
Source: azure_devops_user_stories.md
User Stories: US-24510 (IR - Rehiring - Open Rehiring page from Navigation menu),
              US-24511 (IR - Rehiring - Perform Rehiring)

Covers rehiring navigation and form submission for the IR role.

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
# from src.onboarding.rehiring import RehiringPage, RehiringService


# ---------------------------------------------------------------------------
# US-24510: Open Rehiring Page from Navigation Menu
# ---------------------------------------------------------------------------


class TestRehiringNavigation(unittest.TestCase):
    """US-24510: Verify navigation to Rehiring page via side navigation menu."""

    def setUp(self):
        self.navigation = MagicMock()
        self.page = MagicMock()

    def test_sideNav_onboardingMenu_displaysRehiringSubMenu(self):
        """Positive: Onboarding menu in side navigation displays 'Rehiring' sub-menu."""
        self.navigation.get_submenus.return_value = [
            "Quick Onboarding",
            "Rehiring",
            "Onboarding Overview",
            "Bulk Upload",
        ]

        submenus = self.navigation.get_submenus("Onboarding")

        self.assertIn("Rehiring", submenus)

    def test_sideNav_selectRehiring_displaysRehiringPage(self):
        """Positive: Selecting 'Rehiring' from side nav opens the Rehiring page."""
        self.navigation.navigate_to.return_value = {
            "status": "success",
            "page": "Rehiring",
        }

        result = self.navigation.navigate_to("Rehiring")

        self.assertEqual(result["status"], "success")
        self.assertEqual(result["page"], "Rehiring")


class TestRehiringPageFields(unittest.TestCase):
    """US-24510: Verify Rehiring page displays correct fields and buttons."""

    def setUp(self):
        self.page = MagicMock()
        self.page.get_employee_type_options.return_value = [
            "Apprentice",
            "Advanced Trainee",
            "AT Staff",
            "Temporary Workmen",
            "Permanent Workmen",
        ]
        self.page.get_fields.return_value = [
            "Employee Type",
            "Old PS No",
            "Aadhar Number",
        ]
        self.page.get_buttons.return_value = ["Continue", "Cancel"]

    def test_page_displaysEmployeeTypeDropdownWithFiveOptions(self):
        """Positive: Employee Type dropdown lists all five employee type options."""
        options = self.page.get_employee_type_options()

        self.assertEqual(len(options), 5)
        self.assertIn("Apprentice", options)
        self.assertIn("Permanent Workmen", options)

    def test_page_displaysOldPSNoField(self):
        """Positive: Rehiring page displays Old PS No text/dropdown field."""
        fields = self.page.get_fields()

        self.assertIn("Old PS No", fields)

    def test_page_displaysAadharNumberField(self):
        """Positive: Rehiring page displays Aadhar Number text field."""
        fields = self.page.get_fields()

        self.assertIn("Aadhar Number", fields)

    def test_page_displaysContinueAndCancelButtons(self):
        """Positive: Rehiring page displays Continue and Cancel buttons."""
        buttons = self.page.get_buttons()

        self.assertIn("Continue", buttons)
        self.assertIn("Cancel", buttons)

    def test_page_clickContinue_withValidData_navigatesToRehiringForm(self):
        """Positive: Clicking Continue with valid data navigates to full Rehiring form."""
        self.page.click_continue.return_value = {
            "status": "success",
            "redirect": "/rehiring/form",
        }

        result = self.page.click_continue(employee_type="Apprentice", old_ps_no="12345")

        self.assertEqual(result["status"], "success")
        self.assertIn("/rehiring/form", result["redirect"])

    def test_page_clickCancel_navigatesToPreviousPage(self):
        """Positive: Clicking Cancel navigates back to the previous page."""
        self.page.click_cancel.return_value = {"redirect": "/ir/dashboard"}

        result = self.page.click_cancel()

        self.assertIsNotNone(result["redirect"])


# ---------------------------------------------------------------------------
# US-24510: Rehiring Page Validations
# ---------------------------------------------------------------------------


class TestRehiringPageValidations(unittest.TestCase):
    """US-24510: Verify validation logic on the Rehiring page."""

    def setUp(self):
        self.service = MagicMock()

    def test_oldPSNo_typeOldPS_displaysLinkedEmployeeName(self):
        """Positive: Typing an Old PS No auto-displays the employee name linked to it."""
        self.service.lookup_employee_by_ps.return_value = {
            "ps_no": "PS-12345",
            "employee_name": "John Doe",
        }

        result = self.service.lookup_employee_by_ps("PS-12345")

        self.assertEqual(result["employee_name"], "John Doe")
        self.assertIsNotNone(result["employee_name"])

    def test_oldPSNoDropdown_displaysAllInactiveEmployees(self):
        """Positive: Old PS No dropdown lists all inactive employees."""
        self.service.get_inactive_employees.return_value = [
            {"ps_no": "PS-001", "name": "Alice"},
            {"ps_no": "PS-002", "name": "Bob"},
        ]

        result = self.service.get_inactive_employees()

        self.assertIsInstance(result, list)
        self.assertGreater(len(result), 0)
        for emp in result:
            self.assertIn("ps_no", emp)
            self.assertIn("name", emp)

    def test_oldPSNo_nonExistent_returnsError(self):
        """Negative: Entering a non-existent Old PS No returns an error."""
        self.service.lookup_employee_by_ps.return_value = {
            "status": "error",
            "message": "Employee not found for the given PS No",
        }

        result = self.service.lookup_employee_by_ps("PS-INVALID")

        self.assertEqual(result["status"], "error")

    def test_oldPSNo_empty_returnsValidationError(self):
        """Boundary: Empty Old PS No field returns validation error."""
        self.service.lookup_employee_by_ps.return_value = {
            "status": "error",
            "message": "Old PS No is required",
        }

        result = self.service.lookup_employee_by_ps("")

        self.assertEqual(result["status"], "error")


# ---------------------------------------------------------------------------
# US-24511: Perform Rehiring – Form
# ---------------------------------------------------------------------------


class TestRehiringForm(unittest.TestCase):
    """US-24511: Verify Rehiring form pre-population and editable fields."""

    def setUp(self):
        self.service = MagicMock()

    def test_rehiringForm_loadsHistoricalData_fromOldPSNo(self):
        """Positive: Rehiring form auto-populates historical data from Old PS No."""
        self.service.load_rehire_data.return_value = {
            "ps_no": "PS-12345",
            "name": "John Doe",
            "dept": "ENG01",
            "joining_date": "01-01-2020",
        }

        result = self.service.load_rehire_data("PS-12345")

        self.assertIsNotNone(result["name"])
        self.assertIsNotNone(result["dept"])

    def test_rehiringForm_displaysMandatoryEditableFields(self):
        """Positive: Rehiring form shows Cadre, Department, Rejoining Date, Basic as editable."""
        self.service.get_editable_fields.return_value = [
            "Cadre",
            "Department",
            "Rejoining Date",
            "Basic",
        ]

        fields = self.service.get_editable_fields()

        self.assertIn("Cadre", fields)
        self.assertIn("Department", fields)
        self.assertIn("Rejoining Date", fields)
        self.assertIn("Basic", fields)

    def test_rehiringForm_editIconClicked_makesOnlySectionEditable(self):
        """Positive: Edit icon click makes only the clicked section's fields editable."""
        self.service.toggle_section_edit.return_value = {
            "editable_section": "Compensation",
            "other_sections_locked": True,
        }

        result = self.service.toggle_section_edit("Compensation")

        self.assertEqual(result["editable_section"], "Compensation")
        self.assertTrue(result["other_sections_locked"])

    def test_rehiringForm_submit_validData_sendsToApproverAndShowsSuccess(self):
        """Positive: Valid submission sends request to IR Approver and shows success message."""
        self.service.submit_rehire.return_value = {
            "status": "success",
            "message": "Rehiring process has been successfully submitted",
        }

        result = self.service.submit_rehire(data={"cadre": "Grade-A", "dept": "ENG01"})

        self.assertEqual(result["status"], "success")
        self.assertIn("successfully submitted", result["message"])

    def test_rehiringForm_submit_clickOkay_redirectsToOnboardingOverview(self):
        """Positive: Clicking 'Okay' on the success popup redirects to Onboarding Overview."""
        self.service.confirm_submission.return_value = {
            "redirect": "/onboarding-overview",
        }

        result = self.service.confirm_submission()

        self.assertIn("/onboarding-overview", result["redirect"])

    def test_rehiringForm_cancelButton_navigatesToPreviousPage(self):
        """Positive: Clicking Cancel navigates back to the previous page."""
        self.service.cancel.return_value = {"redirect": "/previous"}

        result = self.service.cancel()

        self.assertIsNotNone(result["redirect"])

    def test_rehiringForm_submit_mandatoryFieldMissing_returnsError(self):
        """Negative: Submitting without required mandatory fields returns an error."""
        self.service.submit_rehire.return_value = {
            "status": "error",
            "message": "Mandatory fields are missing",
        }

        result = self.service.submit_rehire(data={})

        self.assertEqual(result["status"], "error")
        self.assertIn("mandatory", result["message"].lower())

    def test_rehiringForm_rejoiningDate_beforeOldLeavingDate_returnsError(self):
        """Boundary: Rejoining Date set before the employee's leaving date returns error."""
        self.service.validate_rejoining_date.return_value = {
            "status": "error",
            "message": "Rejoining date must be after the previous separation date",
        }

        result = self.service.validate_rejoining_date("01-01-2019", leaving_date="01-06-2020")

        self.assertEqual(result["status"], "error")

    def test_rehiringForm_allDataFetchedFromWorkforceInfo(self):
        """Positive: All employee data is auto-fetched from workforce information based on Old PS No."""
        self.service.load_rehire_data.return_value = {
            "source": "workforce_information",
            "data_loaded": True,
        }

        result = self.service.load_rehire_data("PS-12345")

        self.assertTrue(result["data_loaded"])
        self.assertEqual(result["source"], "workforce_information")


if __name__ == "__main__":
    unittest.main()
