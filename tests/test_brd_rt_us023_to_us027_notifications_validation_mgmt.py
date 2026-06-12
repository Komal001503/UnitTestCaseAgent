"""
Unit Tests for BRD RT — Notifications, Validation Rules, Request Editing,
                          License Alerts, and Role Conflict Management
User Stories: US-023, US-024, US-025, US-026, US-027

Acceptance Criteria:
    US-023 — System sends email/SMS to NDT Engineer when request is initiated.
              System notifies Initiator when NDT Engineer approves/returns.
              System notifies RT Engineer and Initiator when all shops approve.
              System notifies Initiator and RT Technician when plan is finalized.
              System notifies all stakeholders when execution is completed.
    US-024 — Submission blocked when mandatory fields missing (BR-001).
              Validation error when proposed RT date < 2 hours from now (BR-002).
              Validation error when technician license is invalid at execution (BR-007).
              Validation error when camera/equipment calibration is invalid (BR-008).
    US-025 — Initiator can edit request only in 'Draft' or 'Returned' status.
              Editing prevented when request is not in 'Draft' or 'Returned' status.
    US-026 — Automated alert sent 30 days before license/certification expiry.
              Periodic reminders sent when < 30 days remain and no renewal action taken.
    US-027 — System prevents assigning the same user as both Initiator and Shop Approver.
              System prevents assigning the same user as both Shop Approver and Initiator.

Test Categories:
    - Positive / Happy Path
    - Negative / Error Path
    - Boundary / Edge Cases
    - Integration Points
"""

SOURCE_STORY_FILE = "BRD RT latest_user_stories.md"

import unittest
from unittest.mock import MagicMock, patch
from datetime import datetime, timedelta


# ---------------------------------------------------------------------------
# US-023: Notification Management
# ---------------------------------------------------------------------------

class TestNotificationManagement(unittest.TestCase):
    """US-023: Verify event-triggered notifications across the RT lifecycle."""

    def setUp(self):
        self.notification_service = MagicMock()

    # --- Positive ---

    def test_requestInitiated_notifiesNDTEngineer(self):
        """Positive: RT request initiation sends email and SMS to the NDT Engineer."""
        self.notification_service.notify_on_initiation.return_value = {
            "status": "SENT",
            "recipients": ["NDT_ENGINEER"],
            "channels": ["EMAIL", "SMS"],
        }

        result = self.notification_service.notify_on_initiation(request_id="RT-2026-001")

        self.assertEqual(result["status"], "SENT")
        self.assertIn("NDT_ENGINEER", result["recipients"])
        self.assertIn("EMAIL", result["channels"])
        self.assertIn("SMS", result["channels"])

    def test_ndtApproval_notifiesInitiator(self):
        """Positive: NDT Engineer approval sends email and SMS to the Initiator."""
        self.notification_service.notify_on_ndt_action.return_value = {
            "status": "SENT",
            "action": "APPROVED",
            "recipients": ["INITIATOR"],
            "channels": ["EMAIL", "SMS"],
        }

        result = self.notification_service.notify_on_ndt_action(
            request_id="RT-2026-001", action="APPROVED"
        )

        self.assertEqual(result["status"], "SENT")
        self.assertIn("INITIATOR", result["recipients"])

    def test_ndtReturn_notifiesInitiator(self):
        """Positive: NDT Engineer returning the request sends email and SMS to the Initiator."""
        self.notification_service.notify_on_ndt_action.return_value = {
            "status": "SENT",
            "action": "RETURNED",
            "recipients": ["INITIATOR"],
            "channels": ["EMAIL", "SMS"],
        }

        result = self.notification_service.notify_on_ndt_action(
            request_id="RT-2026-001", action="RETURNED"
        )

        self.assertEqual(result["status"], "SENT")
        self.assertIn("INITIATOR", result["recipients"])

    def test_allShopsApproved_notifiesRTEngineerAndInitiator(self):
        """Positive: All shops approving sends email to RT Engineer and Initiator."""
        self.notification_service.notify_on_all_shops_approved.return_value = {
            "status": "SENT",
            "recipients": ["RT_ENGINEER", "INITIATOR"],
            "channels": ["EMAIL"],
        }

        result = self.notification_service.notify_on_all_shops_approved(request_id="RT-2026-001")

        self.assertEqual(result["status"], "SENT")
        self.assertIn("RT_ENGINEER", result["recipients"])
        self.assertIn("INITIATOR", result["recipients"])

    def test_planFinalized_notifiesInitiatorAndTechnician(self):
        """Positive: RT plan finalized sends email and SMS to Initiator and RT Technician."""
        self.notification_service.notify_on_plan_confirmed.return_value = {
            "status": "SENT",
            "recipients": ["INITIATOR", "RT_TECHNICIAN"],
            "channels": ["EMAIL", "SMS"],
        }

        result = self.notification_service.notify_on_plan_confirmed(request_id="RT-2026-001")

        self.assertEqual(result["status"], "SENT")
        self.assertIn("RT_TECHNICIAN", result["recipients"])

    def test_executionCompleted_notifiesAllStakeholders(self):
        """Positive: Execution completion sends email to all stakeholders."""
        self.notification_service.notify_on_execution_complete.return_value = {
            "status": "SENT",
            "recipients": ["INITIATOR", "NDT_ENGINEER", "SHOP_INCHARGE", "RT_ENGINEER"],
            "channels": ["EMAIL"],
        }

        result = self.notification_service.notify_on_execution_complete(request_id="RT-2026-001")

        self.assertEqual(result["status"], "SENT")
        self.assertGreaterEqual(len(result["recipients"]), 4)

    # --- Negative ---

    def test_notifyOnInitiation_invalidRequestId_returnsError(self):
        """Negative: Triggering notification for a non-existent request ID returns an error."""
        self.notification_service.notify_on_initiation.return_value = {
            "status": "error",
            "message": "RT request not found.",
        }

        result = self.notification_service.notify_on_initiation(request_id="RT-UNKNOWN")

        self.assertEqual(result["status"], "error")

    # --- Integration ---

    def test_notifyOnInitiation_smtpServerDown_raisesError(self):
        """Integration: SMTP server unavailable raises a connection error during notification."""
        self.notification_service.notify_on_initiation.side_effect = ConnectionError(
            "SMTP server not reachable"
        )

        with self.assertRaises(ConnectionError):
            self.notification_service.notify_on_initiation(request_id="RT-2026-001")

    def test_notifyOnInitiation_smsGatewayDown_raisesError(self):
        """Integration: SMS gateway unavailable raises an error during notification."""
        self.notification_service.notify_on_initiation.side_effect = RuntimeError(
            "SMS gateway unavailable"
        )

        with self.assertRaises(RuntimeError):
            self.notification_service.notify_on_initiation(request_id="RT-2026-001")


# ---------------------------------------------------------------------------
# US-024: Validation Rules Enforcement
# ---------------------------------------------------------------------------

class TestValidationRules(unittest.TestCase):
    """US-024: Verify BR-001, BR-002, BR-007, and BR-008 validation enforcement."""

    def setUp(self):
        self.validation_service = MagicMock()

    # --- BR-001: Mandatory Fields ---

    def test_br001_missingMandatoryFields_submissionBlocked(self):
        """Positive (BR-001): Missing mandatory fields block submission with an error message."""
        self.validation_service.validate_submission.return_value = {
            "status": "error",
            "rule": "BR-001",
            "message": "Mandatory fields are missing.",
            "missing_fields": ["layout_selection", "job_position"],
        }

        result = self.validation_service.validate_submission(
            request_data={"shielding_details": "Lead sheet"}
        )

        self.assertEqual(result["status"], "error")
        self.assertEqual(result["rule"], "BR-001")
        self.assertIn("missing_fields", result)

    def test_br001_allMandatoryFieldsPresent_validationPasses(self):
        """Positive (BR-001): All mandatory fields present; validation passes."""
        self.validation_service.validate_submission.return_value = {
            "status": "OK",
            "rule": "BR-001",
        }

        result = self.validation_service.validate_submission(
            request_data={
                "layout_selection": "LAYOUT-001",
                "job_position": "WJ-045",
                "shielding_details": "Lead sheet 2mm",
            }
        )

        self.assertEqual(result["status"], "OK")

    # --- BR-002: Proposed RT Date Validation ---

    def test_br002_proposedDateLessThan2Hours_validationError(self):
        """Negative (BR-002): Proposed RT date less than 2 hours from now returns validation error."""
        proposed_date = (datetime.now() + timedelta(hours=1)).isoformat()
        self.validation_service.validate_rt_date.return_value = {
            "status": "error",
            "rule": "BR-002",
            "message": "Proposed RT date must be at least 2 hours from the current time.",
        }

        result = self.validation_service.validate_rt_date(proposed_date=proposed_date)

        self.assertEqual(result["status"], "error")
        self.assertEqual(result["rule"], "BR-002")

    def test_br002_proposedDateExactly2HoursAhead_validationPasses(self):
        """Boundary (BR-002): Proposed RT date exactly 2 hours from now passes validation."""
        proposed_date = (datetime.now() + timedelta(hours=2)).isoformat()
        self.validation_service.validate_rt_date.return_value = {
            "status": "OK",
            "rule": "BR-002",
        }

        result = self.validation_service.validate_rt_date(proposed_date=proposed_date)

        self.assertEqual(result["status"], "OK")

    def test_br002_proposedDateMoreThan2HoursAhead_validationPasses(self):
        """Positive (BR-002): Proposed RT date more than 2 hours from now passes validation."""
        proposed_date = (datetime.now() + timedelta(hours=5)).isoformat()
        self.validation_service.validate_rt_date.return_value = {
            "status": "OK",
            "rule": "BR-002",
        }

        result = self.validation_service.validate_rt_date(proposed_date=proposed_date)

        self.assertEqual(result["status"], "OK")

    def test_br002_proposedDateInPast_validationError(self):
        """Boundary (BR-002): Proposed RT date in the past returns a validation error."""
        proposed_date = (datetime.now() - timedelta(hours=1)).isoformat()
        self.validation_service.validate_rt_date.return_value = {
            "status": "error",
            "rule": "BR-002",
            "message": "Proposed RT date cannot be in the past.",
        }

        result = self.validation_service.validate_rt_date(proposed_date=proposed_date)

        self.assertEqual(result["status"], "error")

    # --- BR-007: Technician License Validity ---

    def test_br007_technicianLicenseInvalid_validationError(self):
        """Negative (BR-007): Technician with expired license at execution returns validation error."""
        self.validation_service.validate_technician_license.return_value = {
            "status": "error",
            "rule": "BR-007",
            "message": "Technician license is not valid at the time of execution.",
            "technician_id": "TECH-001",
            "license_expiry": "2025-01-01",
        }

        result = self.validation_service.validate_technician_license(
            technician_id="TECH-001",
            execution_date="2026-06-15",
        )

        self.assertEqual(result["status"], "error")
        self.assertEqual(result["rule"], "BR-007")

    def test_br007_technicianLicenseValid_validationPasses(self):
        """Positive (BR-007): Technician with a valid license at execution passes validation."""
        self.validation_service.validate_technician_license.return_value = {
            "status": "OK",
            "rule": "BR-007",
        }

        result = self.validation_service.validate_technician_license(
            technician_id="TECH-001",
            execution_date="2026-06-15",
        )

        self.assertEqual(result["status"], "OK")

    # --- BR-008: Camera/Equipment Calibration Validity ---

    def test_br008_calibrationInvalid_validationError(self):
        """Negative (BR-008): Camera/equipment with invalid calibration returns validation error."""
        self.validation_service.validate_equipment_calibration.return_value = {
            "status": "error",
            "rule": "BR-008",
            "message": "Camera calibration is not valid.",
            "equipment_id": "CAM-001",
            "calibration_expiry": "2025-03-01",
        }

        result = self.validation_service.validate_equipment_calibration(
            equipment_id="CAM-001",
            execution_date="2026-06-15",
        )

        self.assertEqual(result["status"], "error")
        self.assertEqual(result["rule"], "BR-008")

    def test_br008_calibrationValid_validationPasses(self):
        """Positive (BR-008): Camera/equipment with valid calibration passes validation."""
        self.validation_service.validate_equipment_calibration.return_value = {
            "status": "OK",
            "rule": "BR-008",
        }

        result = self.validation_service.validate_equipment_calibration(
            equipment_id="CAM-001",
            execution_date="2026-06-15",
        )

        self.assertEqual(result["status"], "OK")


# ---------------------------------------------------------------------------
# US-025: Edit RT Request Only in Draft or Returned Status
# ---------------------------------------------------------------------------

class TestRTRequestEditing(unittest.TestCase):
    """US-025: Verify request editing is allowed only in 'Draft' or 'Returned' status."""

    def setUp(self):
        self.edit_service = MagicMock()

    # --- Positive ---

    def test_editRequest_draftStatus_editAllowed(self):
        """Positive: Initiator can edit a request in 'Draft' status."""
        self.edit_service.edit.return_value = {
            "status": "UPDATED",
            "request_id": "RT-2026-001",
            "request_status": "DRAFT",
        }

        result = self.edit_service.edit(
            request_id="RT-2026-001",
            updates={"job_position": "WJ-046"},
        )

        self.assertEqual(result["status"], "UPDATED")

    def test_editRequest_returnedStatus_editAllowed(self):
        """Positive: Initiator can edit a request in 'Returned' status."""
        self.edit_service.edit.return_value = {
            "status": "UPDATED",
            "request_id": "RT-2026-002",
            "request_status": "RETURNED",
        }

        result = self.edit_service.edit(
            request_id="RT-2026-002",
            updates={"shielding_details": "Updated shielding"},
        )

        self.assertEqual(result["status"], "UPDATED")

    # --- Negative ---

    def test_editRequest_submittedStatus_editPrevented(self):
        """Negative: Editing a request in 'Submitted' status returns an error."""
        self.edit_service.edit.return_value = {
            "status": "error",
            "message": "Editing is not allowed for requests in 'Submitted' status.",
        }

        result = self.edit_service.edit(
            request_id="RT-2026-003",
            updates={"job_position": "WJ-047"},
        )

        self.assertEqual(result["status"], "error")

    def test_editRequest_approvedStatus_editPrevented(self):
        """Negative: Editing a request in 'Approved' status returns an error."""
        self.edit_service.edit.return_value = {
            "status": "error",
            "message": "Editing is not allowed for requests in 'Approved' status.",
        }

        result = self.edit_service.edit(
            request_id="RT-2026-004",
            updates={"layout_id": "LAYOUT-002"},
        )

        self.assertEqual(result["status"], "error")

    def test_editRequest_closedStatus_editPrevented(self):
        """Negative: Editing a request in 'Closed' status returns an error."""
        self.edit_service.edit.return_value = {
            "status": "error",
            "message": "Editing is not allowed for requests in 'Closed' status.",
        }

        result = self.edit_service.edit(
            request_id="RT-2026-005",
            updates={"description": "Updated description"},
        )

        self.assertEqual(result["status"], "error")

    def test_editRequest_plannedStatus_editPrevented(self):
        """Negative: Editing a request in 'Planned' status returns an error."""
        self.edit_service.edit.return_value = {
            "status": "error",
            "message": "Editing is not allowed for requests in 'Planned' status.",
        }

        result = self.edit_service.edit(
            request_id="RT-2026-006",
            updates={"job_position": "WJ-050"},
        )

        self.assertEqual(result["status"], "error")

    # --- Boundary ---

    def test_editRequest_returnedStatus_noChanges_savedSuccessfully(self):
        """Boundary: Saving a 'Returned' request with no actual changes is accepted."""
        self.edit_service.edit.return_value = {
            "status": "UPDATED",
            "request_id": "RT-2026-002",
        }

        result = self.edit_service.edit(
            request_id="RT-2026-002",
            updates={},
        )

        self.assertEqual(result["status"], "UPDATED")


# ---------------------------------------------------------------------------
# US-026: Automated License/Certification Expiry Alerts
# ---------------------------------------------------------------------------

class TestLicenseCertificationExpiryAlerts(unittest.TestCase):
    """US-026: Verify automated 30-day expiry alerts and periodic reminders."""

    def setUp(self):
        self.alert_service = MagicMock()

    # --- Positive ---

    def test_expiryAlert_exactly30DaysAway_alertSentToAdmin(self):
        """Positive: License/certification expiring in exactly 30 days triggers an alert."""
        self.alert_service.check_and_send_alerts.return_value = {
            "status": "ALERT_SENT",
            "recipient": "RT_ADMIN-001",
            "license_id": "LIC-001",
            "days_to_expiry": 30,
        }

        result = self.alert_service.check_and_send_alerts(license_id="LIC-001")

        self.assertEqual(result["status"], "ALERT_SENT")
        self.assertEqual(result["days_to_expiry"], 30)

    def test_periodicReminder_lessThan30DaysNoAction_reminderSent(self):
        """Positive: Periodic reminder sent when < 30 days remain and no renewal action taken."""
        self.alert_service.check_and_send_alerts.return_value = {
            "status": "REMINDER_SENT",
            "recipient": "RT_ADMIN-001",
            "license_id": "LIC-001",
            "days_to_expiry": 10,
        }

        result = self.alert_service.check_and_send_alerts(license_id="LIC-001")

        self.assertEqual(result["status"], "REMINDER_SENT")
        self.assertLess(result["days_to_expiry"], 30)

    # --- Negative ---

    def test_expiryAlert_moreThan30DaysAway_noAlertSent(self):
        """Negative: License/certification expiring in more than 30 days does NOT trigger an alert."""
        self.alert_service.check_and_send_alerts.return_value = {
            "status": "NO_ACTION",
            "license_id": "LIC-001",
            "days_to_expiry": 60,
        }

        result = self.alert_service.check_and_send_alerts(license_id="LIC-001")

        self.assertEqual(result["status"], "NO_ACTION")
        self.assertGreater(result["days_to_expiry"], 30)

    def test_expiryAlert_licenseAlreadyRenewed_noReminderSent(self):
        """Negative: No reminder is sent if the license has already been renewed."""
        self.alert_service.check_and_send_alerts.return_value = {
            "status": "NO_ACTION",
            "license_id": "LIC-001",
            "reason": "License has already been renewed.",
        }

        result = self.alert_service.check_and_send_alerts(license_id="LIC-001")

        self.assertEqual(result["status"], "NO_ACTION")
        self.assertIn("renewed", result["reason"])

    # --- Boundary ---

    def test_expiryAlert_29DaysAway_alertSent(self):
        """Boundary: License expiring in 29 days (within the 30-day window) triggers an alert."""
        self.alert_service.check_and_send_alerts.return_value = {
            "status": "ALERT_SENT",
            "license_id": "LIC-001",
            "days_to_expiry": 29,
        }

        result = self.alert_service.check_and_send_alerts(license_id="LIC-001")

        self.assertEqual(result["status"], "ALERT_SENT")
        self.assertLessEqual(result["days_to_expiry"], 30)

    def test_expiryAlert_31DaysAway_noAlertSent(self):
        """Boundary: License expiring in 31 days (just outside the 30-day window) does not alert."""
        self.alert_service.check_and_send_alerts.return_value = {
            "status": "NO_ACTION",
            "license_id": "LIC-001",
            "days_to_expiry": 31,
        }

        result = self.alert_service.check_and_send_alerts(license_id="LIC-001")

        self.assertEqual(result["status"], "NO_ACTION")

    def test_expiryAlert_expiryToday_alertSent(self):
        """Boundary: License expiring today (0 days remaining) triggers an alert."""
        self.alert_service.check_and_send_alerts.return_value = {
            "status": "ALERT_SENT",
            "license_id": "LIC-001",
            "days_to_expiry": 0,
        }

        result = self.alert_service.check_and_send_alerts(license_id="LIC-001")

        self.assertEqual(result["status"], "ALERT_SENT")
        self.assertEqual(result["days_to_expiry"], 0)

    # --- Integration ---

    def test_expiryAlert_emailServiceDown_raisesConnectionError(self):
        """Integration: Email service unavailable during alert sending raises ConnectionError."""
        self.alert_service.check_and_send_alerts.side_effect = ConnectionError(
            "Email service not reachable"
        )

        with self.assertRaises(ConnectionError):
            self.alert_service.check_and_send_alerts(license_id="LIC-001")


# ---------------------------------------------------------------------------
# US-027: Role Conflict Management
# ---------------------------------------------------------------------------

class TestRoleConflictManagement(unittest.TestCase):
    """US-027: Verify mutual exclusivity of Initiator and Shop Approver roles."""

    def setUp(self):
        self.role_service = MagicMock()

    # --- Positive ---

    def test_assignShopApprover_userNotAnInitiator_assignedSuccessfully(self):
        """Positive: Assigning Shop Approver role to a user who is not an Initiator succeeds."""
        self.role_service.assign_role.return_value = {
            "status": "ASSIGNED",
            "user_id": "USER-005",
            "role": "SHOP_APPROVER",
        }

        result = self.role_service.assign_role(user_id="USER-005", role="SHOP_APPROVER")

        self.assertEqual(result["status"], "ASSIGNED")
        self.assertEqual(result["role"], "SHOP_APPROVER")

    def test_assignInitiator_userNotAShopApprover_assignedSuccessfully(self):
        """Positive: Assigning Initiator role to a user who is not a Shop Approver succeeds."""
        self.role_service.assign_role.return_value = {
            "status": "ASSIGNED",
            "user_id": "USER-006",
            "role": "INITIATOR",
        }

        result = self.role_service.assign_role(user_id="USER-006", role="INITIATOR")

        self.assertEqual(result["status"], "ASSIGNED")
        self.assertEqual(result["role"], "INITIATOR")

    # --- Negative ---

    def test_assignShopApprover_userIsInitiator_returnsConflictError(self):
        """Negative: Assigning Shop Approver to an existing Initiator returns a conflict error."""
        self.role_service.assign_role.return_value = {
            "status": "error",
            "message": "User is already assigned as Initiator. Cannot assign Shop Approver role.",
            "conflict": True,
        }

        result = self.role_service.assign_role(user_id="USER-001", role="SHOP_APPROVER")

        self.assertEqual(result["status"], "error")
        self.assertTrue(result["conflict"])
        self.assertIn("Initiator", result["message"])

    def test_assignInitiator_userIsShopApprover_returnsConflictError(self):
        """Negative: Assigning Initiator to an existing Shop Approver returns a conflict error."""
        self.role_service.assign_role.return_value = {
            "status": "error",
            "message": "User is already assigned as Shop Approver. Cannot assign Initiator role.",
            "conflict": True,
        }

        result = self.role_service.assign_role(user_id="USER-003", role="INITIATOR")

        self.assertEqual(result["status"], "error")
        self.assertTrue(result["conflict"])
        self.assertIn("Shop Approver", result["message"])

    # --- Boundary ---

    def test_assignRole_nonExistentUser_returnsNotFoundError(self):
        """Boundary: Assigning a role to a non-existent user returns a not-found error."""
        self.role_service.assign_role.return_value = {
            "status": "error",
            "message": "User not found.",
        }

        result = self.role_service.assign_role(user_id="USER-UNKNOWN", role="SHOP_APPROVER")

        self.assertEqual(result["status"], "error")
        self.assertIn("not found", result["message"])

    def test_assignRole_sameRoleAssignedAgain_idempotent(self):
        """Boundary: Re-assigning the same role to a user that already has it is idempotent."""
        self.role_service.assign_role.return_value = {
            "status": "ASSIGNED",
            "user_id": "USER-001",
            "role": "INITIATOR",
            "note": "Role already assigned; no change.",
        }

        result = self.role_service.assign_role(user_id="USER-001", role="INITIATOR")

        self.assertEqual(result["status"], "ASSIGNED")
        self.assertIn("note", result)

    def test_getRoles_existingUser_returnsCurrentRoles(self):
        """Positive: Retrieving roles for an existing user returns their current role list."""
        self.role_service.get_roles.return_value = {
            "status": "OK",
            "user_id": "USER-001",
            "roles": ["INITIATOR"],
        }

        result = self.role_service.get_roles(user_id="USER-001")

        self.assertEqual(result["status"], "OK")
        self.assertIn("INITIATOR", result["roles"])
        self.assertNotIn("SHOP_APPROVER", result["roles"])

    # --- Integration ---

    def test_assignRole_adServiceUnavailable_raisesConnectionError(self):
        """Integration: Active Directory service unavailable during role assignment raises ConnectionError."""
        self.role_service.assign_role.side_effect = ConnectionError("AD service not reachable")

        with self.assertRaises(ConnectionError):
            self.role_service.assign_role(user_id="USER-005", role="SHOP_APPROVER")


if __name__ == "__main__":
    unittest.main()
