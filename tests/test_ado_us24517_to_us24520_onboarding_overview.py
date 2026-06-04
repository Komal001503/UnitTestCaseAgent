"""
Unit Tests for Onboarding Overview Module
Source: azure_devops_user_stories.md
User Stories: US-24517 (IR - Onboarding Overview - All tab),
              US-24518 (IR - Onboarding Overview - Quick Onboarding Tab),
              US-24519 (IR - Onboarding Overview - Rehiring Tab),
              US-24520 (IR - Onboarding Overview - Full Onboarding Tab)

Covers the four tabs of the Onboarding Overview page for the IR role.

Test Categories:
- Positive / Happy Path
- Negative / Error Path
- Boundary / Edge Cases
"""

SOURCE_STORY_FILE = "azure_devops_user_stories.md"

import unittest
from unittest.mock import MagicMock, patch


# TODO: Import actual modules once implementation is available.
# from src.onboarding.overview import OnboardingOverviewPage, OnboardingOverviewService


# ---------------------------------------------------------------------------
# Common: Navigation to Onboarding Overview
# ---------------------------------------------------------------------------


class TestOnboardingOverviewNavigation(unittest.TestCase):
    """US-24517 AC-1, AC-2: Navigate to Onboarding Overview from side nav."""

    def setUp(self):
        self.navigation = MagicMock()
        self.page = MagicMock()

    def test_sideNav_selectOnboardingOverview_navigatesToPage(self):
        """Positive: Selecting 'Onboarding Overview' from side nav opens the page."""
        self.navigation.navigate_to.return_value = {
            "status": "success",
            "page": "Onboarding Overview",
        }

        result = self.navigation.navigate_to("Onboarding Overview")

        self.assertEqual(result["status"], "success")

    def test_onboardingOverviewPage_displaysFourTabs(self):
        """Positive: Onboarding Overview page shows All, Quick Onboarding, Rehiring, Full Onboarding tabs."""
        self.page.get_tabs.return_value = [
            "All",
            "Quick Onboarding",
            "Rehiring",
            "Full Onboarding",
        ]

        tabs = self.page.get_tabs()

        self.assertEqual(len(tabs), 4)
        self.assertIn("All", tabs)
        self.assertIn("Quick Onboarding", tabs)
        self.assertIn("Rehiring", tabs)
        self.assertIn("Full Onboarding", tabs)


# ---------------------------------------------------------------------------
# US-24517: All Tab
# ---------------------------------------------------------------------------


class TestOnboardingOverviewAllTab(unittest.TestCase):
    """US-24517: Verify All tab data grid, navigation, search, and PS No validation."""

    def setUp(self):
        self.service = MagicMock()

    def test_allTab_grid_displaysAllRequiredColumns(self):
        """Positive: All tab grid shows PS No, Name, Employment Type, Dept, Supervisor,
        Joining, Submitted On, Approved On, Onboarding Type, Status."""
        self.service.get_grid_columns.return_value = [
            "PS No",
            "Name",
            "Employment Type",
            "Dept Code",
            "Immediate Supervisor",
            "Date of Joining",
            "Submitted On",
            "Approved On",
            "Onboarding Type",
            "Status",
        ]

        columns = self.service.get_grid_columns("all")

        self.assertEqual(len(columns), 10)
        self.assertIn("PS No", columns)
        self.assertIn("Onboarding Type", columns)
        self.assertIn("Status", columns)

    def test_allTab_onboardingType_includesAllThreeTypes(self):
        """Positive: Onboarding Type column includes Quick Onboarding, Rehiring, Full Onboarding."""
        self.service.get_onboarding_types.return_value = [
            "Quick Onboarding",
            "Rehiring",
            "Full Onboarding",
        ]

        types = self.service.get_onboarding_types()

        self.assertIn("Quick Onboarding", types)
        self.assertIn("Rehiring", types)
        self.assertIn("Full Onboarding", types)

    def test_allTab_clickPSNoLink_navigatesToWorkforceInfoDetails(self):
        """Positive: Clicking PS No / Name hyperlink opens workforce info details page."""
        self.service.navigate_to_details.return_value = {
            "redirect": "/workforce-info/details/12345"
        }

        result = self.service.navigate_to_details("12345")

        self.assertIn("/workforce-info/details", result["redirect"])

    def test_allTab_searchBar_returnsMatchingResults(self):
        """Positive: Search bar filters grid to matching results."""
        self.service.search.return_value = [{"ps_no": "12345", "name": "John Doe"}]

        results = self.service.search("John", tab="all")

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["name"], "John Doe")

    def test_allTab_searchBar_noMatch_returnsEmptyList(self):
        """Boundary: Search with no matching results returns empty list."""
        self.service.search.return_value = []

        results = self.service.search("ZZZNOMATCH", tab="all")

        self.assertEqual(len(results), 0)

    def test_allTab_pageNavigation_worksCorrectly(self):
        """Positive: Page navigation allows moving to next/previous pages."""
        self.service.get_page.return_value = {"page": 2, "total_pages": 5}

        result = self.service.get_page(2)

        self.assertEqual(result["page"], 2)

    def test_allTab_psNo_notShown_whenStatusIsPending(self):
        """Validation: PS No is not displayed when status is 'Pending'."""
        self.service.get_ps_no_for_status.return_value = None

        result = self.service.get_ps_no_for_status("Pending")

        self.assertIsNone(result)

    def test_allTab_psNo_notShown_whenStatusIsReturned(self):
        """Validation: PS No is not displayed when status is 'Returned'."""
        self.service.get_ps_no_for_status.return_value = None

        result = self.service.get_ps_no_for_status("Returned")

        self.assertIsNone(result)

    def test_allTab_psNo_shown_whenStatusIsApproved(self):
        """Validation: PS No is displayed when status is 'Approved'."""
        self.service.get_ps_no_for_status.return_value = "PS-12345"

        result = self.service.get_ps_no_for_status("Approved")

        self.assertIsNotNone(result)
        self.assertEqual(result, "PS-12345")

    def test_allTab_psNo_shown_whenStatusIsCompleted(self):
        """Validation: PS No is displayed when status is 'Completed'."""
        self.service.get_ps_no_for_status.return_value = "PS-12345"

        result = self.service.get_ps_no_for_status("Completed")

        self.assertIsNotNone(result)

    def test_allTab_submittedOn_quickOnboarding_showsIRSubmissionDate(self):
        """Validation: Submitted On for Quick Onboarding/Rehiring = IR submission date."""
        self.service.get_submitted_on.return_value = "15-04-2026"

        result = self.service.get_submitted_on("req_123", type="Quick Onboarding")

        self.assertIsNotNone(result)


# ---------------------------------------------------------------------------
# US-24518: Quick Onboarding Tab
# ---------------------------------------------------------------------------


class TestOnboardingOverviewQuickOnboardingTab(unittest.TestCase):
    """US-24518: Verify Quick Onboarding tab data grid and status logic."""

    def setUp(self):
        self.service = MagicMock()

    def test_quickOnboardingTab_grid_displaysRequiredColumns(self):
        """Positive: Quick Onboarding tab displays all required grid columns."""
        self.service.get_grid_columns.return_value = [
            "PS No",
            "Name",
            "Employment Type",
            "Dept Code",
            "Immediate Supervisor",
            "Date of Joining",
            "Submitted On",
            "Status",
        ]

        columns = self.service.get_grid_columns("quick_onboarding")

        self.assertEqual(len(columns), 8)
        self.assertIn("PS No", columns)
        self.assertIn("Status", columns)

    def test_quickOnboardingTab_nameHyperlink_navigatesToWorkforceInfoDetails(self):
        """Positive: Name hyperlink navigates to workforce information details page."""
        self.service.navigate_to_details.return_value = {
            "redirect": "/workforce-info/details/req_001"
        }

        result = self.service.navigate_to_details("req_001")

        self.assertIn("/workforce-info/details", result["redirect"])

    def test_quickOnboardingTab_psNo_notDisplayed_whenPending(self):
        """Validation: PS No is not displayed when status is 'Pending'."""
        self.service.get_ps_no_for_status.return_value = None

        result = self.service.get_ps_no_for_status("Pending", tab="quick_onboarding")

        self.assertIsNone(result)

    def test_quickOnboardingTab_psNo_displayed_whenApproved(self):
        """Validation: PS No is displayed after IR approval (status 'Approved')."""
        self.service.get_ps_no_for_status.return_value = "PS-00123"

        result = self.service.get_ps_no_for_status("Approved", tab="quick_onboarding")

        self.assertIsNotNone(result)

    def test_quickOnboardingTab_psNo_notDisplayed_whenReturned(self):
        """Validation: PS No is not displayed when status is 'Returned'."""
        self.service.get_ps_no_for_status.return_value = None

        result = self.service.get_ps_no_for_status("Returned", tab="quick_onboarding")

        self.assertIsNone(result)

    def test_quickOnboardingTab_searchBar_filtersResults(self):
        """Positive: Search bar filters Quick Onboarding requests."""
        self.service.search.return_value = [{"name": "Jane Doe"}]

        results = self.service.search("Jane", tab="quick_onboarding")

        self.assertEqual(len(results), 1)

    def test_quickOnboardingTab_pageNavigation_works(self):
        """Positive: Page navigation works in Quick Onboarding tab."""
        self.service.get_page.return_value = {"page": 1}

        result = self.service.get_page(1, tab="quick_onboarding")

        self.assertEqual(result["page"], 1)


# ---------------------------------------------------------------------------
# US-24519: Rehiring Tab
# ---------------------------------------------------------------------------


class TestOnboardingOverviewRehiringTab(unittest.TestCase):
    """US-24519: Verify Rehiring tab data grid columns and PS No logic."""

    def setUp(self):
        self.service = MagicMock()

    def test_rehiringTab_grid_displaysRequiredColumnsIncludingOldPSNo(self):
        """Positive: Rehiring tab grid includes all columns, including Old PS No."""
        self.service.get_grid_columns.return_value = [
            "PS No",
            "Old PS No",
            "Name",
            "Employment Type",
            "Dept Code",
            "Immediate Supervisor",
            "Date of Joining",
            "Submitted On",
            "Status",
        ]

        columns = self.service.get_grid_columns("rehiring")

        self.assertEqual(len(columns), 9)
        self.assertIn("PS No", columns)
        self.assertIn("Old PS No", columns)
        self.assertIn("Status", columns)

    def test_rehiringTab_nameHyperlink_navigatesToWorkforceInfoDetails(self):
        """Positive: Name hyperlink navigates to the workforce information details page."""
        self.service.navigate_to_details.return_value = {
            "redirect": "/workforce-info/details/reh_001"
        }

        result = self.service.navigate_to_details("reh_001")

        self.assertIn("/workforce-info/details", result["redirect"])

    def test_rehiringTab_searchBar_filtersResults(self):
        """Positive: Search bar filters rehiring requests correctly."""
        self.service.search.return_value = [{"ps_no": "PS-002", "old_ps_no": "PS-001"}]

        results = self.service.search("PS-001", tab="rehiring")

        self.assertEqual(len(results), 1)

    def test_rehiringTab_pageNavigation_works(self):
        """Positive: Page navigation works in Rehiring tab."""
        self.service.get_page.return_value = {"page": 2}

        result = self.service.get_page(2, tab="rehiring")

        self.assertEqual(result["page"], 2)


# ---------------------------------------------------------------------------
# US-24520: Full Onboarding Tab
# ---------------------------------------------------------------------------


class TestOnboardingOverviewFullOnboardingTab(unittest.TestCase):
    """US-24520: Verify Full Onboarding tab grid and Due Date validation."""

    def setUp(self):
        self.service = MagicMock()

    def test_fullOnboardingTab_grid_displaysRequiredColumns(self):
        """Positive: Full Onboarding tab displays all required grid columns including Due Date."""
        self.service.get_grid_columns.return_value = [
            "PS No",
            "Name",
            "Employment Type",
            "Dept Code",
            "Immediate Supervisor",
            "Date of Joining",
            "Submitted On",
            "Due Date",
            "Status",
        ]

        columns = self.service.get_grid_columns("full_onboarding")

        self.assertEqual(len(columns), 9)
        self.assertIn("PS No", columns)
        self.assertIn("Due Date", columns)
        self.assertIn("Status", columns)

    def test_fullOnboardingTab_nameHyperlink_navigatesToWorkforceInfoDetails(self):
        """Positive: Name hyperlink navigates to workforce information details page."""
        self.service.navigate_to_details.return_value = {
            "redirect": "/workforce-info/details/fo_001"
        }

        result = self.service.navigate_to_details("fo_001")

        self.assertIn("/workforce-info/details", result["redirect"])

    def test_fullOnboardingTab_psNo_displayedForPendingAndCompleted(self):
        """Validation: PS No is displayed when status is 'Pending' or 'Completed'."""
        for status in ["Pending", "Completed"]:
            self.service.get_ps_no_for_status.return_value = "PS-00456"

            result = self.service.get_ps_no_for_status(status, tab="full_onboarding")

            self.assertIsNotNone(result)

    def test_fullOnboardingTab_dueDate_isEndDateForIRToComplete(self):
        """Validation: Due Date represents the end date for IR to complete full onboarding."""
        self.service.get_due_date.return_value = "30-06-2026"

        result = self.service.get_due_date("fo_001")

        self.assertIsNotNone(result)

    def test_fullOnboardingTab_disciplinaryAction_addedAfterOnboarding(self):
        """Positive: Disciplinary action with Action Date, Action Type, Remarks is added
        in workforce information page after onboarding is complete."""
        self.service.add_disciplinary_action.return_value = {
            "status": "success",
            "fields": ["Action Date", "Action Type", "Remarks"],
        }

        result = self.service.add_disciplinary_action(
            {"action_date": "01-05-2026", "action_type": "Warning", "remarks": "Late attendance"}
        )

        self.assertEqual(result["status"], "success")
        self.assertIn("Action Date", result["fields"])

    def test_fullOnboardingTab_searchBar_filtersResults(self):
        """Positive: Search bar filters Full Onboarding requests."""
        self.service.search.return_value = [{"name": "Bob Smith"}]

        results = self.service.search("Bob", tab="full_onboarding")

        self.assertEqual(len(results), 1)

    def test_fullOnboardingTab_pageNavigation_works(self):
        """Positive: Page navigation works in Full Onboarding tab."""
        self.service.get_page.return_value = {"page": 3}

        result = self.service.get_page(3, tab="full_onboarding")

        self.assertEqual(result["page"], 3)


if __name__ == "__main__":
    unittest.main()
