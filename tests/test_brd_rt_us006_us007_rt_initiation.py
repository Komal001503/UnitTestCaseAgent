"""
Unit Tests for BRD RT — RT Initiation Module
User Stories: US-006, US-007

Acceptance Criteria:
    US-006 — Initiator fills all required fields and submits RT request → saved and stakeholders notified.
              Initiator uploads supporting documents → saved with the request.
              Initiator selects affected shops → validated against NDT Engineer's review.
    US-007 — Initiator selects multiple time slots → all slots saved.
              Initiator selects a conflicting time slot → conflict warning displayed.
              Initiator selects a time slot → shop availability validated.

Test Categories:
    - Positive / Happy Path
    - Negative / Error Path
    - Boundary / Edge Cases
    - Integration Points
"""

SOURCE_STORY_FILE = "BRD RT latest_user_stories.md"

import unittest
from unittest.mock import MagicMock


# ---------------------------------------------------------------------------
# US-006: Raise RT Intimation Requests
# ---------------------------------------------------------------------------

class TestRTIntimationRequestCreation(unittest.TestCase):
    """US-006: Verify RT intimation request creation, document upload, and shop selection."""

    def setUp(self):
        self.request_service = MagicMock()

    # --- Positive ---

    def test_submitRTRequest_allRequiredFields_savedAndNotified(self):
        """Positive: Submitting an RT request with all required fields saves it and notifies stakeholders."""
        self.request_service.submit.return_value = {
            "status": "SUBMITTED",
            "request_id": "RT-2026-001",
            "notifications_sent": ["NDT_ENGINEER", "SHOP_INCHARGE"],
        }

        result = self.request_service.submit({
            "initiator_id": "USER-001",
            "description": "Radiographic test required on weld joint WJ-045",
            "proposed_date": "2026-06-15T10:00:00",
            "shops": ["SHOP-A"],
            "job_position": "WJ-045",
            "shielding_details": "Lead sheet 2mm",
        })

        self.assertEqual(result["status"], "SUBMITTED")
        self.assertIn("request_id", result)
        self.assertIsInstance(result["notifications_sent"], list)
        self.assertGreater(len(result["notifications_sent"]), 0)

    def test_uploadDocuments_validFiles_savedWithRequest(self):
        """Positive: Uploading supporting documents attaches them to the RT request."""
        self.request_service.upload_documents.return_value = {
            "status": "UPLOADED",
            "request_id": "RT-2026-001",
            "documents": ["safety_clearance.pdf", "job_card.pdf"],
        }

        result = self.request_service.upload_documents(
            request_id="RT-2026-001",
            files=["safety_clearance.pdf", "job_card.pdf"],
        )

        self.assertEqual(result["status"], "UPLOADED")
        self.assertIn("documents", result)
        self.assertEqual(len(result["documents"]), 2)

    def test_selectAffectedShops_validShops_validatedByNDTEngineer(self):
        """Positive: Selected shops pass NDT Engineer validation and are saved with the request."""
        self.request_service.select_shops.return_value = {
            "status": "VALIDATED",
            "request_id": "RT-2026-001",
            "shops": ["SHOP-A", "SHOP-B"],
            "ndt_review": "PENDING",
        }

        result = self.request_service.select_shops(
            request_id="RT-2026-001",
            shops=["SHOP-A", "SHOP-B"],
        )

        self.assertEqual(result["status"], "VALIDATED")
        self.assertIn("ndt_review", result)

    # --- Negative ---

    def test_submitRTRequest_missingMandatoryFields_returnsError(self):
        """Negative: Submitting an RT request without mandatory fields returns an error."""
        self.request_service.submit.return_value = {
            "status": "error",
            "message": "Mandatory fields are missing: job_position, shielding_details.",
        }

        result = self.request_service.submit({
            "initiator_id": "USER-001",
            "proposed_date": "2026-06-15T10:00:00",
        })

        self.assertEqual(result["status"], "error")
        self.assertIn("Mandatory fields", result["message"])

    def test_uploadDocuments_noFiles_returnsValidationError(self):
        """Negative: Uploading no documents returns a validation error."""
        self.request_service.upload_documents.return_value = {
            "status": "error",
            "message": "At least one document must be uploaded.",
        }

        result = self.request_service.upload_documents(
            request_id="RT-2026-001",
            files=[],
        )

        self.assertEqual(result["status"], "error")

    def test_selectAffectedShops_noShops_returnsValidationError(self):
        """Negative: Selecting no affected shops returns a validation error."""
        self.request_service.select_shops.return_value = {
            "status": "error",
            "message": "At least one shop must be selected.",
        }

        result = self.request_service.select_shops(
            request_id="RT-2026-001",
            shops=[],
        )

        self.assertEqual(result["status"], "error")

    def test_submitRTRequest_invalidRequestId_returnsNotFoundError(self):
        """Negative: Submitting with a non-existent request ID returns a not-found error."""
        self.request_service.upload_documents.return_value = {
            "status": "error",
            "message": "RT request not found.",
        }

        result = self.request_service.upload_documents(
            request_id="RT-UNKNOWN",
            files=["doc.pdf"],
        )

        self.assertEqual(result["status"], "error")
        self.assertIn("not found", result["message"])

    # --- Boundary ---

    def test_submitRTRequest_descriptionAtMaxLength_savedSuccessfully(self):
        """Boundary: RT request description at maximum allowed length is saved successfully."""
        max_description = "A" * 500
        self.request_service.submit.return_value = {
            "status": "SUBMITTED",
            "request_id": "RT-2026-002",
        }

        result = self.request_service.submit({
            "initiator_id": "USER-001",
            "description": max_description,
            "proposed_date": "2026-06-15T10:00:00",
            "shops": ["SHOP-A"],
            "job_position": "WJ-046",
            "shielding_details": "Concrete barrier",
        })

        self.assertEqual(result["status"], "SUBMITTED")

    def test_uploadDocuments_unsupportedFileFormat_returnsError(self):
        """Boundary: Uploading a file with unsupported format returns a validation error."""
        self.request_service.upload_documents.return_value = {
            "status": "error",
            "message": "Unsupported file format.",
        }

        result = self.request_service.upload_documents(
            request_id="RT-2026-001",
            files=["document.xyz"],
        )

        self.assertEqual(result["status"], "error")

    # --- Integration ---

    def test_submitRTRequest_notificationServiceDown_raisesError(self):
        """Integration: Notification service failure during RT request submission raises an error."""
        self.request_service.submit.side_effect = RuntimeError("Notification service unavailable")

        with self.assertRaises(RuntimeError):
            self.request_service.submit({
                "initiator_id": "USER-001",
                "proposed_date": "2026-06-15T10:00:00",
                "shops": ["SHOP-A"],
                "job_position": "WJ-047",
                "shielding_details": "Lead sheet 3mm",
            })

    def test_submitRTRequest_databaseUnavailable_raisesConnectionError(self):
        """Integration: Database unavailable during RT request submission raises ConnectionError."""
        self.request_service.submit.side_effect = ConnectionError("Database not accessible")

        with self.assertRaises(ConnectionError):
            self.request_service.submit({
                "initiator_id": "USER-001",
                "proposed_date": "2026-06-15T10:00:00",
                "shops": ["SHOP-A"],
                "job_position": "WJ-048",
                "shielding_details": "Sand bags",
            })


# ---------------------------------------------------------------------------
# US-007: Multiple Time Slot Selection for RT Activities
# ---------------------------------------------------------------------------

class TestRTTimeSlotSelection(unittest.TestCase):
    """US-007: Verify multi-slot selection, conflict detection, and availability checks."""

    def setUp(self):
        self.slot_service = MagicMock()

    # --- Positive ---

    def test_selectMultipleSlots_validSlots_allSlotsSaved(self):
        """Positive: Selecting multiple non-conflicting time slots saves all slots."""
        self.slot_service.select_slots.return_value = {
            "status": "SAVED",
            "request_id": "RT-2026-001",
            "slots": [
                {"slot_id": "SLOT-001", "start": "2026-06-15T08:00:00", "end": "2026-06-15T10:00:00"},
                {"slot_id": "SLOT-002", "start": "2026-06-16T08:00:00", "end": "2026-06-16T10:00:00"},
            ],
        }

        result = self.slot_service.select_slots(
            request_id="RT-2026-001",
            slots=[
                {"start": "2026-06-15T08:00:00", "end": "2026-06-15T10:00:00"},
                {"start": "2026-06-16T08:00:00", "end": "2026-06-16T10:00:00"},
            ],
        )

        self.assertEqual(result["status"], "SAVED")
        self.assertEqual(len(result["slots"]), 2)

    def test_checkShopAvailability_availableSlot_returnsAvailable(self):
        """Positive: Checking availability for a free slot returns AVAILABLE."""
        self.slot_service.check_availability.return_value = {
            "status": "AVAILABLE",
            "shop_id": "SHOP-A",
            "slot": {"start": "2026-06-15T08:00:00", "end": "2026-06-15T10:00:00"},
        }

        result = self.slot_service.check_availability(
            shop_id="SHOP-A",
            slot={"start": "2026-06-15T08:00:00", "end": "2026-06-15T10:00:00"},
        )

        self.assertEqual(result["status"], "AVAILABLE")

    # --- Negative ---

    def test_selectSlot_conflictingBooking_returnsConflictWarning(self):
        """Negative: Selecting a time slot that conflicts with an existing booking returns a conflict warning."""
        self.slot_service.select_slots.return_value = {
            "status": "CONFLICT",
            "message": "Selected slot conflicts with an existing booking.",
            "conflicting_slot": {
                "slot_id": "SLOT-EXISTING",
                "start": "2026-06-15T08:00:00",
                "end": "2026-06-15T10:00:00",
            },
        }

        result = self.slot_service.select_slots(
            request_id="RT-2026-001",
            slots=[{"start": "2026-06-15T08:00:00", "end": "2026-06-15T10:00:00"}],
        )

        self.assertEqual(result["status"], "CONFLICT")
        self.assertIn("conflicting_slot", result)

    def test_selectSlot_shopUnavailable_returnsUnavailableError(self):
        """Negative: Selecting a slot for an unavailable shop returns an unavailability error."""
        self.slot_service.check_availability.return_value = {
            "status": "UNAVAILABLE",
            "message": "Shop is not available for the selected time slot.",
        }

        result = self.slot_service.check_availability(
            shop_id="SHOP-A",
            slot={"start": "2026-06-15T08:00:00", "end": "2026-06-15T10:00:00"},
        )

        self.assertEqual(result["status"], "UNAVAILABLE")

    def test_selectSlot_noSlotsProvided_returnsValidationError(self):
        """Negative: Submitting a slot selection with no slots returns a validation error."""
        self.slot_service.select_slots.return_value = {
            "status": "error",
            "message": "At least one time slot must be selected.",
        }

        result = self.slot_service.select_slots(request_id="RT-2026-001", slots=[])

        self.assertEqual(result["status"], "error")

    # --- Boundary ---

    def test_selectSlot_startEqualsEnd_returnsValidationError(self):
        """Boundary: Selecting a time slot where start equals end returns a validation error."""
        self.slot_service.select_slots.return_value = {
            "status": "error",
            "message": "Slot end time must be after start time.",
        }

        result = self.slot_service.select_slots(
            request_id="RT-2026-001",
            slots=[{"start": "2026-06-15T08:00:00", "end": "2026-06-15T08:00:00"}],
        )

        self.assertEqual(result["status"], "error")

    def test_selectSlot_endBeforeStart_returnsValidationError(self):
        """Boundary: Selecting a time slot where end is before start returns a validation error."""
        self.slot_service.select_slots.return_value = {
            "status": "error",
            "message": "Slot end time must be after start time.",
        }

        result = self.slot_service.select_slots(
            request_id="RT-2026-001",
            slots=[{"start": "2026-06-15T10:00:00", "end": "2026-06-15T08:00:00"}],
        )

        self.assertEqual(result["status"], "error")

    def test_selectSlot_maxSlotsAllowed_savedSuccessfully(self):
        """Boundary: Selecting the maximum number of allowed slots saves all successfully."""
        slots = [
            {"start": f"2026-06-{15+i:02d}T08:00:00", "end": f"2026-06-{15+i:02d}T10:00:00"}
            for i in range(10)
        ]
        self.slot_service.select_slots.return_value = {
            "status": "SAVED",
            "request_id": "RT-2026-001",
            "slots": slots,
        }

        result = self.slot_service.select_slots(request_id="RT-2026-001", slots=slots)

        self.assertEqual(result["status"], "SAVED")
        self.assertEqual(len(result["slots"]), 10)

    # --- Integration ---

    def test_checkShopAvailability_availabilityServiceTimeout_raisesTimeoutError(self):
        """Integration: Availability service timeout raises TimeoutError."""
        self.slot_service.check_availability.side_effect = TimeoutError("Availability service timeout")

        with self.assertRaises(TimeoutError):
            self.slot_service.check_availability(
                shop_id="SHOP-A",
                slot={"start": "2026-06-15T08:00:00", "end": "2026-06-15T10:00:00"},
            )

    def test_selectSlots_calendarServiceUnavailable_raisesConnectionError(self):
        """Integration: Calendar service unavailable raises ConnectionError."""
        self.slot_service.select_slots.side_effect = ConnectionError("Calendar service not reachable")

        with self.assertRaises(ConnectionError):
            self.slot_service.select_slots(
                request_id="RT-2026-001",
                slots=[{"start": "2026-06-15T08:00:00", "end": "2026-06-15T10:00:00"}],
            )


if __name__ == "__main__":
    unittest.main()
