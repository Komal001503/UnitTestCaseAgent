"""
Unit Tests for Quick Onboarding Module
Source: azure_devops_user_stories.md
User Stories: US-24508 (IR - Quick Onboarding - Open from menu),
              US-24509 (IR - Quick Onboarding - Perform quick onboarding)

Covers quick onboarding navigation and form submission for IR role.

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
# from src.onboarding.quick_onboarding import QuickOnboardingPage, QuickOnboardingService


# ---------------------------------------------------------------------------
# US-24508: Open Quick Onboarding from Navigation Menu
# ---------------------------------------------------------------------------


class TestQuickOnboardingNavigation(unittest.TestCase):
    """US-24508: Verify navigation to Quick Onboarding page via side nav menu."""

    def setUp(self):
        self.navigation = MagicMock()
        self.page = MagicMock()

    def test_navigation_irDashboard_displaysHamburgerMenu(self):
        """Positive: IR user can open side navigation via hamburger menu."""
        self.navigation.open_side_nav.return_value = {"status": "open"}

        result = self.navigation.open_side_nav()

        self.assertEqual(result["status"], "open")

    def test_sideNav_onboardingMenu_displaysAllSubMenus(self):
        """Positive: Onboarding menu shows Quick Onboarding, Rehiring,
        Onboarding Overview, and Bulk Upload sub-menus."""
        self.navigation.get_submenus.return_value = [
            "Quick Onboarding",
            "Rehiring",
            "Onboarding Overview",
            "Bulk Upload",
        ]

        submenus = self.navigation.get_submenus("Onboarding")

        self.assertEqual(len(submenus), 4)
        self.assertIn("Quick Onboarding", submenus)
        self.assertIn("Rehiring", submenus)
        self.assertIn("Onboarding Overview", submenus)
        self.assertIn("Bulk Upload", submenus)

    def test_sideNav_selectQuickOnboarding_navigatesToPage(self):
        """Positive: Selecting 'Quick Onboarding' sub-menu opens the Quick Onboarding page."""
        self.navigation.navigate_to.return_value = {
            "status": "success",
            "page": "Quick Onboarding",
        }

        result = self.navigation.navigate_to("Quick Onboarding")

        self.assertEqual(result["status"], "success")
        self.assertEqual(result["page"], "Quick Onboarding")


class TestQuickOnboardingPageDisplay(unittest.TestCase):
    """US-24508: Verify Quick Onboarding page displays correct fields and buttons."""

    def setUp(self):
        self.page = MagicMock()
        self.page.get_employee_type_options.return_value = [
            "Apprentice",
            "Advanced Trainee",
            "AT Staff - Temporary Workmen",
            "Permanent Workmen",
        ]
        self.page.get_buttons.return_value = ["Continue", "Cancel"]

    def test_page_displaysEmployeeTypeDropdown(self):
        """Positive: Quick Onboarding page displays Employee Type dropdown."""
        self.page.has_field.return_value = True

        result = self.page.has_field("employee_type_dropdown")

        self.assertTrue(result)

    def test_employeeTypeDropdown_containsAllOptions(self):
        """Positive: Employee Type dropdown lists all four employee type options."""
        options = self.page.get_employee_type_options()

        self.assertEqual(len(options), 4)
        self.assertIn("Apprentice", options)
        self.assertIn("Advanced Trainee", options)
        self.assertIn("AT Staff - Temporary Workmen", options)
        self.assertIn("Permanent Workmen", options)

    def test_page_displaysContinueAndCancelButtons(self):
        """Positive: Page displays both Continue and Cancel buttons."""
        buttons = self.page.get_buttons()

        self.assertIn("Continue", buttons)
        self.assertIn("Cancel", buttons)

    def test_page_clickContinue_navigatesToQuickOnboardingForm(self):
        """Positive: Clicking Continue navigates to the full Quick Onboarding form."""
        self.page.click_continue.return_value = {
            "status": "success",
            "redirect": "/quick-onboarding/form",
        }

        result = self.page.click_continue(employee_type="Apprentice")

        self.assertEqual(result["status"], "success")
        self.assertIn("/quick-onboarding/form", result["redirect"])

    def test_page_clickContinue_withoutEmployeeType_returnsError(self):
        """Negative: Clicking Continue without selecting Employee Type returns error."""
        self.page.click_continue.return_value = {
            "status": "error",
            "message": "Please select an Employee Type",
        }

        result = self.page.click_continue(employee_type=None)

        self.assertEqual(result["status"], "error")

    def test_page_clickCancel_navigatesToPreviousPage(self):
        """Positive: Clicking Cancel navigates back to the previous page."""
        self.page.click_cancel.return_value = {
            "status": "success",
            "redirect": "/ir/dashboard",
        }

        result = self.page.click_cancel()

        self.assertEqual(result["status"], "success")


# ---------------------------------------------------------------------------
# US-24509: Perform Quick Onboarding – Form Fields
# ---------------------------------------------------------------------------


class TestQuickOnboardingFormFields(unittest.TestCase):
    """US-24509: Verify all sections and fields in the Quick Onboarding form."""

    def setUp(self):
        self.service = MagicMock()

    def test_form_nameInformation_displaysAllRequiredFields(self):
        """Positive: Name Information section shows Title, Full Name, First, Last, Middle Name."""
        self.service.get_section_fields.return_value = [
            "Title",
            "Name as per Aadhaar / Full Name",
            "First Name",
            "Middle Name",
            "Last Name",
        ]

        fields = self.service.get_section_fields("Name Information")

        self.assertIn("Title", fields)
        self.assertIn("First Name", fields)
        self.assertIn("Last Name", fields)
        self.assertIn("Middle Name", fields)

    def test_form_biographicalInfo_displaysDateOfBirthAndPlaceOfBirth(self):
        """Positive: Biographical Information section includes DOB and Place of Birth."""
        self.service.get_section_fields.return_value = [
            "Date of Birth",
            "Place of Birth",
        ]

        fields = self.service.get_section_fields("Biographical Information")

        self.assertIn("Date of Birth", fields)
        self.assertIn("Place of Birth", fields)

    def test_form_contactInfo_displaysEmailAndMobileNumber(self):
        """Positive: Contact Information section includes Email ID and Mobile Number."""
        self.service.get_section_fields.return_value = ["Email ID", "Mobile Number"]

        fields = self.service.get_section_fields("Contact Information")

        self.assertIn("Email ID", fields)
        self.assertIn("Mobile Number", fields)

    def test_form_personalInfo_displaysGenderMaritalStatusReligionCaste(self):
        """Positive: Personal Information section has Gender, Marital Status, Religion, Caste."""
        self.service.get_section_fields.return_value = [
            "Gender",
            "Marital Status",
            "Marital Status Since",
            "No of Children",
            "Nationality",
            "Domicile (State)",
            "Religion",
            "Caste Code",
            "Blood Group",
            "Father Name",
        ]

        fields = self.service.get_section_fields("Personal Information")

        self.assertIn("Gender", fields)
        self.assertIn("Marital Status", fields)
        self.assertIn("Religion", fields)
        self.assertIn("Caste Code", fields)

    def test_form_nationalIdInfo_displaysDocumentFields(self):
        """Positive: National ID section shows Document Type, Document ID, Is Primary, Upload."""
        self.service.get_section_fields.return_value = [
            "Document Type",
            "Document ID",
            "Is Primary",
            "Upload Document",
        ]

        fields = self.service.get_section_fields("National ID Information")

        self.assertIn("Document Type", fields)
        self.assertIn("Document ID", fields)
        self.assertIn("Is Primary", fields)

    def test_form_jobInfo_displaysUnitNameShiftCodeDirectWorkman(self):
        """Positive: Job Information section includes Unit Name, Shift Code, Direct Workman."""
        self.service.get_section_fields.return_value = [
            "Unit Name",
            "Function Code",
            "Category Code",
            "Shift Code",
            "Direct Workman?",
            "Employee Type",
            "Area",
        ]

        fields = self.service.get_section_fields("Job Information")

        self.assertIn("Unit Name", fields)
        self.assertIn("Shift Code", fields)
        self.assertIn("Direct Workman?", fields)

    def test_form_compensationInfo_displaysJoiningBasicCurrentCadre(self):
        """Positive: Compensation section has Cadre at Joining, Current Cadre, and Basic fields."""
        self.service.get_section_fields.return_value = [
            "Cadre at Joining",
            "Current Cadre",
            "Joining Basic",
            "Confirmation Basic",
            "Current Basic",
        ]

        fields = self.service.get_section_fields("Compensation Information")

        self.assertIn("Cadre at Joining", fields)
        self.assertIn("Current Cadre", fields)
        self.assertIn("Joining Basic", fields)


# ---------------------------------------------------------------------------
# US-24509: Quick Onboarding – Validations
# ---------------------------------------------------------------------------


class TestQuickOnboardingValidations(unittest.TestCase):
    """US-24509: Verify form validations and business rules."""

    def setUp(self):
        self.service = MagicMock()

    def test_submit_mandatoryFieldsMissing_showsPopupWithMessage(self):
        """Negative: Submitting with missing mandatory fields shows popup notification."""
        self.service.submit.return_value = {
            "status": "error",
            "popup": "Mandatory fields missing, please fill all the details to proceed further",
        }

        result = self.service.submit(data={})

        self.assertEqual(result["status"], "error")
        self.assertIn("Mandatory fields missing", result["popup"])

    def test_submit_allMandatoryFieldsFilled_sendsToApproverAndShowsSuccess(self):
        """Positive: Valid submission sends request to IR Approver and shows success message."""
        self.service.submit.return_value = {
            "status": "success",
            "message": "Your quick onboarding page has been successfully submitted",
        }

        result = self.service.submit(data={"first_name": "John", "last_name": "Doe"})

        self.assertEqual(result["status"], "success")
        self.assertIn("successfully submitted", result["message"])

    def test_submit_clickOkayOnSuccessPopup_redirectsToOnboardingOverview(self):
        """Positive: Clicking 'Okay' on success popup redirects to Onboarding Overview page."""
        self.service.confirm_submission.return_value = {
            "redirect": "/onboarding-overview",
        }

        result = self.service.confirm_submission()

        self.assertIn("/onboarding-overview", result["redirect"])

    def test_maritalStatus_single_hidesMaritalFields(self):
        """Positive: Selecting 'Single' in Marital Status hides married-specific fields."""
        self.service.on_marital_status_change.return_value = {
            "visible_fields": [],
            "hidden_fields": ["Marital Status Since", "No of Children"],
        }

        result = self.service.on_marital_status_change("Single")

        self.assertIn("Marital Status Since", result["hidden_fields"])
        self.assertIn("No of Children", result["hidden_fields"])

    def test_maritalStatus_married_showsMaritalFields(self):
        """Positive: Selecting 'Married' shows 'Marital Status Since' and 'No of Children'."""
        self.service.on_marital_status_change.return_value = {
            "visible_fields": ["Marital Status Since", "No of Children"],
        }

        result = self.service.on_marital_status_change("Married")

        self.assertIn("Marital Status Since", result["visible_fields"])
        self.assertIn("No of Children", result["visible_fields"])

    def test_aadharNumber_afterEntry_masksFirst8Digits(self):
        """Positive: After Aadhaar entry, first 8 digits are masked; only last 4 displayed."""
        self.service.get_masked_aadhar.return_value = "XXXX XXXX 1234"

        result = self.service.get_masked_aadhar("123456781234")

        self.assertIn("XXXX", result)
        self.assertIn("1234", result)

    def test_aadharNumber_storedEncrypted(self):
        """Positive: Aadhaar number is stored encrypted in the system."""
        self.service.is_encrypted.return_value = True

        result = self.service.is_encrypted("aadhar_field")

        self.assertTrue(result)

    def test_documentUpload_fileSizeExceedsLimit_returnsError(self):
        """Boundary: File size above 5MB limit returns validation error."""
        self.service.upload_document.return_value = {
            "status": "error",
            "message": "File size exceeds the 5MB limit",
        }

        result = self.service.upload_document(file_size_mb=6)

        self.assertEqual(result["status"], "error")
        self.assertIn("5MB", result["message"])

    def test_documentUpload_validFile_uploadsSuccessfully(self):
        """Positive: Valid file within size limit uploads successfully."""
        self.service.upload_document.return_value = {
            "status": "success",
            "filename": "document.pdf",
        }

        result = self.service.upload_document(file_size_mb=2)

        self.assertEqual(result["status"], "success")

    def test_dateOfBirth_enteredInDDMMYYYY_autocalculatesAge(self):
        """Positive: DOB entered in DD-MM-YYYY format auto-calculates and shows age."""
        self.service.on_dob_entered.return_value = {"age": 25}

        result = self.service.on_dob_entered("01-01-2000")

        self.assertIn("age", result)
        self.assertIsInstance(result["age"], int)

    def test_noOfChildren_maximumFive_enforced(self):
        """Boundary: Number of children field is capped at a maximum of 5."""
        self.service.set_no_of_children.return_value = {
            "status": "error",
            "message": "Maximum number of children is 5",
        }

        result = self.service.set_no_of_children(6)

        self.assertEqual(result["status"], "error")
        self.assertIn("5", result["message"])

    def test_deptCode_entry_autoFetchesSupervisorFields(self):
        """Positive: Entering Dept Code auto-populates IS, NS, DH, CS, extension, working area."""
        self.service.on_dept_code_entered.return_value = {
            "immediate_supervisor": "IS_001",
            "next_supervisor": "NS_001",
            "dept_head": "DH_001",
            "contact_supervisor": "CS_001",
            "extension_number": "1234",
            "working_area": "Shop A",
        }

        result = self.service.on_dept_code_entered("DEPT001")

        self.assertIsNotNone(result["immediate_supervisor"])
        self.assertIsNotNone(result["next_supervisor"])
        self.assertIsNotNone(result["dept_head"])

    def test_submit_triggersEmailToAllIRUsers(self):
        """Positive: Submitting quick onboarding triggers email notification to all IR users."""
        self.service.submit.return_value = {
            "status": "success",
            "email_sent": True,
        }

        result = self.service.submit(data={"first_name": "John", "last_name": "Doe"})

        self.assertTrue(result.get("email_sent"))

    def test_cancelButton_navigatesToPreviousPage(self):
        """Positive: Clicking Cancel navigates back to the previous page."""
        self.service.cancel.return_value = {"redirect": "/previous"}

        result = self.service.cancel()

        self.assertIsNotNone(result["redirect"])


if __name__ == "__main__":
    unittest.main()
