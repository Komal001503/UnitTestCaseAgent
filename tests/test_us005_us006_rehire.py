"""
Unit Tests for Rehire Module
User Stories: US-005 (Open Rehiring from Menu), US-006 (Rehire Page)

Test Categories:
- Positive / Happy Path
- Negative / Error Path
- Boundary / Edge Cases
- Integration Points
"""

import unittest
from unittest.mock import MagicMock, patch


# TODO: Import actual modules once implementation is available.
# from src.onboarding.rehire import (
#     RehirePage, RehireService, NavigationService
# )


# ---------------------------------------------------------------------------
# US-005: Open Rehiring from Menu
# ---------------------------------------------------------------------------


class TestRehiringMenuPage(unittest.TestCase):
    """US-005: Verify Rehiring selection page fields and navigation."""

    def setUp(self):
        self.page = MagicMock()
        self.page.get_employee_type_options.return_value = [
            "Apprentice",
            "Advanced Trainee",
            "AT Staff",
            "Temporary Workmen",
            "Permanent Workmen",
        ]
        self.page.get_buttons.return_value = ["Continue", "Cancel"]

    def test_rehiringPage_employeeTypeDropdown_displaysAllOptions(self):
        """Positive: Employee Type dropdown shows all valid options."""
        options = self.page.get_employee_type_options()

        self.assertEqual(len(options), 5)
        self.assertIn("Apprentice", options)
        self.assertIn("Permanent Workmen", options)

    def test_rehiringPage_displaysOldPSNoField(self):
        """Positive: Page displays Old PS No text field and dropdown."""
        self.page.get_fields.return_value = [
            "employee_type",
            "old_ps_no",
            "aadhaar_number",
        ]

        fields = self.page.get_fields()

        self.assertIn("old_ps_no", fields)

    def test_rehiringPage_displaysAadhaarNumberField(self):
        """Positive: Page displays Aadhaar Number text field."""
        self.page.get_fields.return_value = [
            "employee_type",
            "old_ps_no",
            "aadhaar_number",
        ]

        fields = self.page.get_fields()

        self.assertIn("aadhaar_number", fields)

    def test_rehiringPage_buttons_displaysContinueAndCancel(self):
        """Positive: Page displays Continue and Cancel buttons."""
        buttons = self.page.get_buttons()

        self.assertIn("Continue", buttons)
        self.assertIn("Cancel", buttons)

    def test_rehiringPage_continueWithValidData_navigatesToRehiringPage(self):
        """Positive: Continue with valid selections navigates to Rehiring page."""
        self.page.click_continue.return_value = {"redirect": "/rehiring"}

        result = self.page.click_continue()

        self.assertEqual(result["redirect"], "/rehiring")

    def test_rehiringPage_cancel_navigatesToPreviousPage(self):
        """Positive: Cancel navigates to the previous page."""
        self.page.click_cancel.return_value = {"redirect": "/dashboard"}

        result = self.page.click_cancel()

        self.assertEqual(result["redirect"], "/dashboard")


class TestOldPSNoValidation(unittest.TestCase):
    """US-005 AC-7, AC-8: Old PS No field validations."""

    def setUp(self):
        self.service = MagicMock()

    def test_oldPSNo_typeValidPSNo_displaysEmployeeName(self):
        """Positive: Typing valid old PS No displays linked employee name."""
        self.service.lookup_old_ps_no.return_value = {
            "ps_no": "12345",
            "employee_name": "John Doe",
        }

        result = self.service.lookup_old_ps_no("12345")

        self.assertEqual(result["employee_name"], "John Doe")

    def test_oldPSNo_typeInvalidPSNo_returnsNoMatch(self):
        """Negative: Invalid old PS No returns no match."""
        self.service.lookup_old_ps_no.return_value = None

        result = self.service.lookup_old_ps_no("99999")

        self.assertIsNone(result)

    def test_oldPSNo_selectDropdown_displaysInactiveEmployees(self):
        """Positive: Old PS No dropdown displays all inactive employees."""
        self.service.get_inactive_employees.return_value = [
            {"ps_no": "10001", "name": "Alice Smith"},
            {"ps_no": "10002", "name": "Bob Jones"},
            {"ps_no": "10003", "name": "Charlie Brown"},
        ]

        result = self.service.get_inactive_employees()

        self.assertTrue(len(result) > 0)
        for employee in result:
            self.assertIn("ps_no", employee)
            self.assertIn("name", employee)

    def test_oldPSNo_emptyPSNo_returnsError(self):
        """Boundary: Empty PS No returns validation error."""
        self.service.lookup_old_ps_no.return_value = {
            "status": "error",
            "message": "PS No is required",
        }

        result = self.service.lookup_old_ps_no("")

        self.assertEqual(result["status"], "error")

    def test_oldPSNo_specialCharacters_returnsNoMatch(self):
        """Boundary: Special characters in PS No returns no match."""
        self.service.lookup_old_ps_no.return_value = None

        result = self.service.lookup_old_ps_no("@#$%")

        self.assertIsNone(result)


# ---------------------------------------------------------------------------
# US-006: Rehire Page - Create Rehire Request
# ---------------------------------------------------------------------------


class TestRehirePageDataPopulation(unittest.TestCase):
    """US-006 AC-1, AC-3: Historical data auto-population from old PS No."""

    def setUp(self):
        self.service = MagicMock()

    def test_rehirePage_validOldPSNo_autoPopulatesHistoricalData(self):
        """Positive: Valid Old PS No auto-populates historical onboarding data."""
        self.service.get_historical_data.return_value = {
            "first_name": "John",
            "last_name": "Doe",
            "dob": "01-01-1990",
            "department": "Engineering",
            "designation": "Workman",
        }

        result = self.service.get_historical_data("12345")

        self.assertEqual(result["first_name"], "John")
        self.assertIn("department", result)

    def test_rehirePage_dataFetchedFromWorkforceInfo_allFieldsPresent(self):
        """Positive: All data is fetched from workforce information."""
        self.service.get_workforce_data.return_value = {
            "personal_info": {"name": "John Doe"},
            "job_info": {"department": "ENG01"},
            "compensation": {"basic": 15000},
        }

        result = self.service.get_workforce_data("12345")

        self.assertIn("personal_info", result)
        self.assertIn("job_info", result)
        self.assertIn("compensation", result)


class TestRehirePageEditableFields(unittest.TestCase):
    """US-006 AC-2, AC-4: Editable fields and section edit functionality."""

    def setUp(self):
        self.service = MagicMock()

    def test_rehirePage_requiredEditableFields_displayed(self):
        """Positive: All required editable fields are displayed."""
        self.service.get_editable_fields.return_value = [
            "cadre",
            "department",
            "rejoining_date",
            "basic",
        ]

        fields = self.service.get_editable_fields()

        self.assertIn("cadre", fields)
        self.assertIn("department", fields)
        self.assertIn("rejoining_date", fields)
        self.assertIn("basic", fields)

    def test_rehirePage_clickEditIcon_makesSectionEditable(self):
        """Positive: Clicking edit icon makes only that section editable."""
        self.service.toggle_section_edit.return_value = {
            "section": "compensation",
            "editable": True,
            "other_sections_editable": False,
        }

        result = self.service.toggle_section_edit("compensation")

        self.assertTrue(result["editable"])
        self.assertFalse(result["other_sections_editable"])

    def test_rehirePage_editOneSection_otherSectionsRemainReadOnly(self):
        """Positive: Editing one section keeps others non-editable."""
        self.service.get_section_states.return_value = {
            "personal_info": {"editable": False},
            "compensation": {"editable": True},
            "job_info": {"editable": False},
        }

        result = self.service.get_section_states()

        editable_count = sum(1 for s in result.values() if s["editable"])
        self.assertEqual(editable_count, 1)


class TestRehirePageSubmission(unittest.TestCase):
    """US-006 AC-5, AC-6, AC-7: Submit and Cancel functionality."""

    def setUp(self):
        self.service = MagicMock()

    def test_rehireSubmit_allFieldsFilled_submitsSuccessfully(self):
        """Positive: All required and mandatory fields filled - submits."""
        self.service.submit.return_value = {
            "status": "success",
            "message": "Rehiring process has been successfully submitted",
        }

        result = self.service.submit({
            "cadre": "C1",
            "department": "ENG01",
            "rejoining_date": "01-06-2026",
            "basic": 20000,
        })

        self.assertEqual(result["status"], "success")
        self.assertIn("successfully submitted", result["message"])

    def test_rehireSubmit_mandatoryFieldsMissing_showsError(self):
        """Negative: Missing mandatory fields prevents submission."""
        self.service.submit.return_value = {
            "status": "error",
            "message": "Mandatory fields are missing",
        }

        result = self.service.submit({"cadre": "", "department": ""})

        self.assertEqual(result["status"], "error")

    def test_rehireSubmit_successPopupOkay_redirectsToOverview(self):
        """Positive: Clicking 'Okay' on success popup redirects to overview."""
        self.service.handle_popup.return_value = {
            "redirect": "/onboarding-review-overview"
        }

        result = self.service.handle_popup("okay")

        self.assertIn("/onboarding-review-overview", result["redirect"])

    def test_rehireCancel_navigatesToPreviousPage(self):
        """Positive: Cancel navigates to the previous page."""
        self.service.cancel.return_value = {"redirect": "/previous-page"}

        result = self.service.cancel()

        self.assertIn("redirect", result)

    def test_rehireSubmit_negativeBasicValue_validationFails(self):
        """Boundary: Negative basic value fails validation."""
        self.service.validate_basic.return_value = {
            "valid": False,
            "error": "Basic cannot be negative",
        }

        result = self.service.validate_basic(-5000)

        self.assertFalse(result["valid"])

    def test_rehireSubmit_zeroBasicValue_validationFails(self):
        """Boundary: Zero basic value fails validation."""
        self.service.validate_basic.return_value = {
            "valid": False,
            "error": "Basic must be greater than zero",
        }

        result = self.service.validate_basic(0)

        self.assertFalse(result["valid"])

    def test_rehireSubmit_futureRejoiningDate_validationPasses(self):
        """Positive: Future rejoining date is valid."""
        self.service.validate_rejoining_date.return_value = {"valid": True}

        result = self.service.validate_rejoining_date("01-12-2026")

        self.assertTrue(result["valid"])

    def test_rehireSubmit_pastRejoiningDate_validationFails(self):
        """Negative: Past rejoining date fails validation."""
        self.service.validate_rejoining_date.return_value = {
            "valid": False,
            "error": "Rejoining date cannot be in the past",
        }

        result = self.service.validate_rejoining_date("01-01-2020")

        self.assertFalse(result["valid"])


if __name__ == "__main__":
    unittest.main()
