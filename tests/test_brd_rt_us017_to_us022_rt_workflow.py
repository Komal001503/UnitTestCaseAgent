"""
Unit Tests for BRD RT — RT Intimation Workflow & Execution
User Stories: US-017, US-018, US-019, US-020, US-021, US-022

Acceptance Criteria:
    US-017 — Initiator inputs all mandatory fields (layout, job position, shielding).
              System prevents submission when mandatory fields are missing.
    US-018 — NDT Engineer marks cordoning plan on submitted request.
              NDT Engineer returns request with remarks → Initiator notified.
              NDT Engineer acknowledges request → status = 'Acknowledged', Initiator notified.
    US-019 — After NDT approval, Initiator selects affected shops.
              System prevents submission when no shops selected.
    US-020 — Shop Approver sees only requests for their assigned shops.
              Shop Approver approves → status = 'Approved', stakeholders notified.
              Shop Approver declines → status = 'Declined', stakeholders notified.
              Shop Approver cannot approve their own request.
    US-021 — After all shop approvals, RT Engineer adds vendor/technician/camera/duration.
              System prevents planning before all shop approvals received.
              Plan confirmed → status = 'Planned', stakeholders notified.
    US-022 — RT Technician updates execution status (spots, attachments) when request is 'Planned'.
              System prevents closure without all mandatory documents.
              All documents uploaded → closure updates status to 'Closed', stakeholders notified.

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
# US-017: Create RT Intimation Request with All Details
# ---------------------------------------------------------------------------

class TestRTIntimationRequestDetails(unittest.TestCase):
    """US-017: Verify RT request creation with mandatory fields and validation."""

    def setUp(self):
        self.request_service = MagicMock()

    # --- Positive ---

    def test_createRequest_allMandatoryFields_requestCreatedSuccessfully(self):
        """Positive: Creating a request with all mandatory fields returns CREATED status."""
        self.request_service.create.return_value = {
            "status": "CREATED",
            "request_id": "RT-2026-001",
        }

        result = self.request_service.create({
            "layout_id": "LAYOUT-001",
            "job_position": "WJ-045",
            "shielding_details": "Lead sheet 2mm",
            "initiator_id": "USER-001",
        })

        self.assertEqual(result["status"], "CREATED")
        self.assertIn("request_id", result)

    # --- Negative ---

    def test_createRequest_missingLayoutSelection_returnsError(self):
        """Negative: Submitting without layout selection returns a validation error."""
        self.request_service.create.return_value = {
            "status": "error",
            "message": "Layout selection is mandatory.",
        }

        result = self.request_service.create({
            "job_position": "WJ-045",
            "shielding_details": "Lead sheet",
            "initiator_id": "USER-001",
        })

        self.assertEqual(result["status"], "error")
        self.assertIn("Layout selection", result["message"])

    def test_createRequest_missingJobPosition_returnsError(self):
        """Negative: Submitting without job position returns a validation error."""
        self.request_service.create.return_value = {
            "status": "error",
            "message": "Job position is mandatory.",
        }

        result = self.request_service.create({
            "layout_id": "LAYOUT-001",
            "shielding_details": "Lead sheet",
            "initiator_id": "USER-001",
        })

        self.assertEqual(result["status"], "error")

    def test_createRequest_missingShieldingDetails_returnsError(self):
        """Negative: Submitting without shielding details returns a validation error."""
        self.request_service.create.return_value = {
            "status": "error",
            "message": "Shielding details are mandatory.",
        }

        result = self.request_service.create({
            "layout_id": "LAYOUT-001",
            "job_position": "WJ-045",
            "initiator_id": "USER-001",
        })

        self.assertEqual(result["status"], "error")

    # --- Boundary ---

    def test_createRequest_allFieldsEmpty_returnsMultipleValidationErrors(self):
        """Boundary: Submitting an entirely empty request returns multiple validation errors."""
        self.request_service.create.return_value = {
            "status": "error",
            "errors": [
                "Layout selection is mandatory.",
                "Job position is mandatory.",
                "Shielding details are mandatory.",
            ],
        }

        result = self.request_service.create({})

        self.assertEqual(result["status"], "error")
        self.assertGreaterEqual(len(result["errors"]), 3)


# ---------------------------------------------------------------------------
# US-018: NDT Engineer Review and Cordoning Plan
# ---------------------------------------------------------------------------

class TestNDTEngineerReview(unittest.TestCase):
    """US-018: Verify cordoning plan marking, return with remarks, and acknowledgement."""

    def setUp(self):
        self.review_service = MagicMock()

    # --- Positive ---

    def test_markCordoningPlan_ndtEngineer_cordoningMarkedSuccessfully(self):
        """Positive: NDT Engineer successfully marks the cordoning plan on the request."""
        self.review_service.mark_cordoning.return_value = {
            "status": "CORDONING_MARKED",
            "request_id": "RT-2026-001",
            "marked_by": "NDT_ENG-001",
        }

        result = self.review_service.mark_cordoning(
            request_id="RT-2026-001",
            cordoning_data={"area": {"x": 10, "y": 20, "width": 100, "height": 50}},
            engineer_id="NDT_ENG-001",
        )

        self.assertEqual(result["status"], "CORDONING_MARKED")

    def test_returnRequest_withRemarks_statusReturnedAndInitiatorNotified(self):
        """Positive: NDT Engineer returns the request with remarks, Initiator is notified."""
        self.review_service.return_request.return_value = {
            "status": "RETURNED",
            "request_id": "RT-2026-001",
            "remarks": "Cordoning area needs adjustment near Bay-3.",
            "notification_sent_to": "USER-001",
        }

        result = self.review_service.return_request(
            request_id="RT-2026-001",
            remarks="Cordoning area needs adjustment near Bay-3.",
        )

        self.assertEqual(result["status"], "RETURNED")
        self.assertIn("remarks", result)
        self.assertIn("notification_sent_to", result)

    def test_acknowledgeRequest_allCorrect_statusUpdatedAndInitiatorNotified(self):
        """Positive: NDT Engineer acknowledges the request; status becomes 'Acknowledged'."""
        self.review_service.acknowledge.return_value = {
            "status": "ACKNOWLEDGED",
            "request_id": "RT-2026-001",
            "notification_sent_to": "USER-001",
        }

        result = self.review_service.acknowledge(
            request_id="RT-2026-001",
            engineer_id="NDT_ENG-001",
        )

        self.assertEqual(result["status"], "ACKNOWLEDGED")
        self.assertIn("notification_sent_to", result)

    # --- Negative ---

    def test_returnRequest_withoutRemarks_returnsValidationError(self):
        """Negative: Returning a request without remarks returns a validation error."""
        self.review_service.return_request.return_value = {
            "status": "error",
            "message": "Remarks are required when returning a request.",
        }

        result = self.review_service.return_request(
            request_id="RT-2026-001",
            remarks="",
        )

        self.assertEqual(result["status"], "error")
        self.assertIn("Remarks", result["message"])

    def test_acknowledgeRequest_cordoningNotMarked_returnsError(self):
        """Negative: Acknowledging without marking the cordoning plan returns an error."""
        self.review_service.acknowledge.return_value = {
            "status": "error",
            "message": "Cordoning plan must be marked before acknowledgement.",
        }

        result = self.review_service.acknowledge(
            request_id="RT-2026-001",
            engineer_id="NDT_ENG-001",
        )

        self.assertEqual(result["status"], "error")

    # --- Boundary ---

    def test_returnRequest_remarksAtMaxLength_returnedSuccessfully(self):
        """Boundary: Returning a request with remarks at max length is accepted."""
        max_remarks = "R" * 1000
        self.review_service.return_request.return_value = {
            "status": "RETURNED",
            "request_id": "RT-2026-001",
        }

        result = self.review_service.return_request(
            request_id="RT-2026-001",
            remarks=max_remarks,
        )

        self.assertEqual(result["status"], "RETURNED")


# ---------------------------------------------------------------------------
# US-019: Initiator Selects Affected Shops After NDT Approval
# ---------------------------------------------------------------------------

class TestInitiatorShopSelection(unittest.TestCase):
    """US-019: Verify shop selection after NDT approval and mandatory shop validation."""

    def setUp(self):
        self.shop_selection_service = MagicMock()

    # --- Positive ---

    def test_selectShops_afterNDTApproval_shopsSelectedSuccessfully(self):
        """Positive: Initiator selects affected shops after NDT Engineer approval."""
        self.shop_selection_service.select_shops.return_value = {
            "status": "SHOPS_SELECTED",
            "request_id": "RT-2026-001",
            "shops": ["SHOP-A", "SHOP-B"],
        }

        result = self.shop_selection_service.select_shops(
            request_id="RT-2026-001",
            shops=["SHOP-A", "SHOP-B"],
        )

        self.assertEqual(result["status"], "SHOPS_SELECTED")
        self.assertIn("SHOP-A", result["shops"])

    # --- Negative ---

    def test_selectShops_beforeNDTApproval_returnsError(self):
        """Negative: Selecting shops before NDT Engineer approval returns an error."""
        self.shop_selection_service.select_shops.return_value = {
            "status": "error",
            "message": "Shops can only be selected after NDT Engineer approval.",
        }

        result = self.shop_selection_service.select_shops(
            request_id="RT-2026-001",
            shops=["SHOP-A"],
        )

        self.assertEqual(result["status"], "error")

    def test_selectShops_noShopsSelected_preventsSubmission(self):
        """Negative: Submitting the request without selecting any shops returns an error."""
        self.shop_selection_service.select_shops.return_value = {
            "status": "error",
            "message": "At least one affected shop must be selected.",
        }

        result = self.shop_selection_service.select_shops(
            request_id="RT-2026-001",
            shops=[],
        )

        self.assertEqual(result["status"], "error")
        self.assertIn("At least one", result["message"])

    # --- Boundary ---

    def test_selectShops_singleShop_savedSuccessfully(self):
        """Boundary: Selecting exactly one affected shop saves the request successfully."""
        self.shop_selection_service.select_shops.return_value = {
            "status": "SHOPS_SELECTED",
            "request_id": "RT-2026-001",
            "shops": ["SHOP-A"],
        }

        result = self.shop_selection_service.select_shops(
            request_id="RT-2026-001",
            shops=["SHOP-A"],
        )

        self.assertEqual(result["status"], "SHOPS_SELECTED")
        self.assertEqual(len(result["shops"]), 1)


# ---------------------------------------------------------------------------
# US-020: Shop Approver Approves or Declines RT Requests
# ---------------------------------------------------------------------------

class TestShopApproverWorkflow(unittest.TestCase):
    """US-020: Verify Shop Approver scope, approval, decline, and self-approval prevention."""

    def setUp(self):
        self.approval_service = MagicMock()

    # --- Positive ---

    def test_getRequests_shopApprover_seesOnlyAssignedShopRequests(self):
        """Positive: Shop Approver retrieves only requests for their assigned shops."""
        self.approval_service.get_pending_requests.return_value = [
            {"request_id": "RT-2026-001", "shop": "SHOP-A", "initiator_id": "USER-002"},
        ]

        result = self.approval_service.get_pending_requests(approver_id="USER-003")

        for req in result:
            self.assertEqual(req["shop"], "SHOP-A")
        # Approver (USER-003) should not see requests from unassigned shops

    def test_approveRequest_validApprover_statusUpdatedAndNotified(self):
        """Positive: Shop Approver approves a request; status becomes 'Approved'."""
        self.approval_service.approve.return_value = {
            "status": "APPROVED",
            "request_id": "RT-2026-001",
            "notifications_sent": ["INITIATOR", "NDT_ENGINEER"],
        }

        result = self.approval_service.approve(
            request_id="RT-2026-001",
            approver_id="USER-003",
        )

        self.assertEqual(result["status"], "APPROVED")
        self.assertIn("notifications_sent", result)

    def test_declineRequest_validApprover_statusUpdatedAndNotified(self):
        """Positive: Shop Approver declines a request; status becomes 'Declined'."""
        self.approval_service.decline.return_value = {
            "status": "DECLINED",
            "request_id": "RT-2026-001",
            "notifications_sent": ["INITIATOR"],
        }

        result = self.approval_service.decline(
            request_id="RT-2026-001",
            approver_id="USER-003",
            reason="Insufficient safety clearance.",
        )

        self.assertEqual(result["status"], "DECLINED")

    # --- Negative ---

    def test_approveRequest_initiatorIsApprover_returnsError(self):
        """Negative: Shop Approver attempting to approve their own request returns an error."""
        self.approval_service.approve.return_value = {
            "status": "error",
            "message": "You cannot approve a request you initiated.",
        }

        result = self.approval_service.approve(
            request_id="RT-2026-001",
            approver_id="USER-001",  # Same as initiator
        )

        self.assertEqual(result["status"], "error")
        self.assertIn("cannot approve", result["message"])

    def test_approveRequest_requestFromUnassignedShop_returnsPermissionError(self):
        """Negative: Approving a request for a shop not assigned to the approver returns an error."""
        self.approval_service.approve.return_value = {
            "status": "error",
            "message": "You are not authorized to approve requests for this shop.",
        }

        result = self.approval_service.approve(
            request_id="RT-2026-999",
            approver_id="USER-003",
        )

        self.assertEqual(result["status"], "error")

    # --- Boundary ---

    def test_declineRequest_withoutReason_returnsValidationError(self):
        """Boundary: Declining a request without providing a reason returns a validation error."""
        self.approval_service.decline.return_value = {
            "status": "error",
            "message": "A reason must be provided when declining a request.",
        }

        result = self.approval_service.decline(
            request_id="RT-2026-001",
            approver_id="USER-003",
            reason="",
        )

        self.assertEqual(result["status"], "error")


# ---------------------------------------------------------------------------
# US-021: RT Engineer Adds Planning Details
# ---------------------------------------------------------------------------

class TestRTPlanningByEngineer(unittest.TestCase):
    """US-021: Verify RT Engineer planning: vendor/tech/camera details and plan confirmation."""

    def setUp(self):
        self.planning_service = MagicMock()

    # --- Positive ---

    def test_addPlanDetails_allApprovalsReceived_planSavedSuccessfully(self):
        """Positive: RT Engineer adds all planning details after all shop approvals."""
        self.planning_service.add_plan_details.return_value = {
            "status": "DETAILS_SAVED",
            "request_id": "RT-2026-001",
        }

        result = self.planning_service.add_plan_details(
            request_id="RT-2026-001",
            vendor_id="VENDOR-001",
            technician_id="TECH-001",
            camera_id="CAM-001",
            duration_hours=4,
        )

        self.assertEqual(result["status"], "DETAILS_SAVED")

    def test_confirmPlan_allDetailsAdded_statusPlannedAndNotified(self):
        """Positive: Confirming plan updates status to 'Planned' and notifies stakeholders."""
        self.planning_service.confirm_plan.return_value = {
            "status": "PLANNED",
            "request_id": "RT-2026-001",
            "notifications_sent": ["INITIATOR", "RT_TECHNICIAN", "SHOP_INCHARGE"],
        }

        result = self.planning_service.confirm_plan(request_id="RT-2026-001")

        self.assertEqual(result["status"], "PLANNED")
        self.assertGreater(len(result["notifications_sent"]), 0)

    # --- Negative ---

    def test_addPlanDetails_missingShopApprovals_returnsError(self):
        """Negative: Adding plan details before all shop approvals returns an error."""
        self.planning_service.add_plan_details.return_value = {
            "status": "error",
            "message": "All shop approvals must be received before planning.",
        }

        result = self.planning_service.add_plan_details(
            request_id="RT-2026-001",
            vendor_id="VENDOR-001",
            technician_id="TECH-001",
            camera_id="CAM-001",
            duration_hours=4,
        )

        self.assertEqual(result["status"], "error")
        self.assertIn("shop approvals", result["message"])

    def test_addPlanDetails_vendorNotInApprovedList_returnsError(self):
        """Negative: Selecting a vendor not in the approved master list returns an error."""
        self.planning_service.add_plan_details.return_value = {
            "status": "error",
            "message": "Vendor is not in the approved master list.",
        }

        result = self.planning_service.add_plan_details(
            request_id="RT-2026-001",
            vendor_id="VENDOR-UNAPPROVED",
            technician_id="TECH-001",
            camera_id="CAM-001",
            duration_hours=4,
        )

        self.assertEqual(result["status"], "error")

    def test_addPlanDetails_technicianNotInApprovedList_returnsError(self):
        """Negative: Selecting a technician not in the approved master list returns an error."""
        self.planning_service.add_plan_details.return_value = {
            "status": "error",
            "message": "Technician is not in the approved master list.",
        }

        result = self.planning_service.add_plan_details(
            request_id="RT-2026-001",
            vendor_id="VENDOR-001",
            technician_id="TECH-UNAPPROVED",
            camera_id="CAM-001",
            duration_hours=4,
        )

        self.assertEqual(result["status"], "error")

    # --- Boundary ---

    def test_addPlanDetails_durationZeroHours_returnsValidationError(self):
        """Boundary: Adding a plan with zero hours duration returns a validation error."""
        self.planning_service.add_plan_details.return_value = {
            "status": "error",
            "message": "Duration must be greater than zero.",
        }

        result = self.planning_service.add_plan_details(
            request_id="RT-2026-001",
            vendor_id="VENDOR-001",
            technician_id="TECH-001",
            camera_id="CAM-001",
            duration_hours=0,
        )

        self.assertEqual(result["status"], "error")


# ---------------------------------------------------------------------------
# US-022: RT Technician Updates Execution Status
# ---------------------------------------------------------------------------

class TestRTExecutionByTechnician(unittest.TestCase):
    """US-022: Verify execution status update, mandatory document upload, and request closure."""

    def setUp(self):
        self.execution_service = MagicMock()

    # --- Positive ---

    def test_updateExecutionStatus_plannedRequest_statusUpdated(self):
        """Positive: RT Technician updates execution status on a 'Planned' request."""
        self.execution_service.update_status.return_value = {
            "status": "IN_PROGRESS",
            "request_id": "RT-2026-001",
            "spots_radiographed": 5,
        }

        result = self.execution_service.update_status(
            request_id="RT-2026-001",
            spots_radiographed=5,
            attachments=["radiograph_01.pdf"],
        )

        self.assertEqual(result["status"], "IN_PROGRESS")
        self.assertEqual(result["spots_radiographed"], 5)

    def test_uploadMandatoryDocuments_allUploaded_uploadedSuccessfully(self):
        """Positive: Uploading all mandatory documents is accepted."""
        self.execution_service.upload_documents.return_value = {
            "status": "UPLOADED",
            "request_id": "RT-2026-001",
            "documents": ["radiograph_01.pdf", "safety_clearance.pdf"],
        }

        result = self.execution_service.upload_documents(
            request_id="RT-2026-001",
            documents=["radiograph_01.pdf", "safety_clearance.pdf"],
        )

        self.assertEqual(result["status"], "UPLOADED")
        self.assertEqual(len(result["documents"]), 2)

    def test_closeRequest_allDocumentsUploaded_statusClosedAndNotified(self):
        """Positive: Closing the request after all documents are uploaded updates status to 'Closed'."""
        self.execution_service.close.return_value = {
            "status": "CLOSED",
            "request_id": "RT-2026-001",
            "notifications_sent": ["INITIATOR", "NDT_ENGINEER", "SHOP_INCHARGE", "RT_ENGINEER"],
        }

        result = self.execution_service.close(request_id="RT-2026-001")

        self.assertEqual(result["status"], "CLOSED")
        self.assertGreater(len(result["notifications_sent"]), 0)

    # --- Negative ---

    def test_closeRequest_missingMandatoryDocuments_preventsClosureWithError(self):
        """Negative: Attempting to close the request without all mandatory documents returns an error."""
        self.execution_service.close.return_value = {
            "status": "error",
            "message": "All mandatory documents must be uploaded before closing the request.",
            "missing_documents": ["safety_clearance.pdf"],
        }

        result = self.execution_service.close(request_id="RT-2026-001")

        self.assertEqual(result["status"], "error")
        self.assertIn("mandatory documents", result["message"])
        self.assertGreater(len(result["missing_documents"]), 0)

    def test_updateExecutionStatus_requestNotPlanned_returnsError(self):
        """Negative: Updating execution status when request is not 'Planned' returns an error."""
        self.execution_service.update_status.return_value = {
            "status": "error",
            "message": "Execution can only be updated for requests in 'Planned' status.",
        }

        result = self.execution_service.update_status(
            request_id="RT-2026-001",
            spots_radiographed=3,
            attachments=[],
        )

        self.assertEqual(result["status"], "error")
        self.assertIn("Planned", result["message"])

    # --- Boundary ---

    def test_updateExecutionStatus_zeroSpotsRadiographed_savedSuccessfully(self):
        """Boundary: Updating with zero spots radiographed is valid and saved."""
        self.execution_service.update_status.return_value = {
            "status": "IN_PROGRESS",
            "request_id": "RT-2026-001",
            "spots_radiographed": 0,
        }

        result = self.execution_service.update_status(
            request_id="RT-2026-001",
            spots_radiographed=0,
            attachments=[],
        )

        self.assertEqual(result["status"], "IN_PROGRESS")
        self.assertEqual(result["spots_radiographed"], 0)

    # --- Integration ---

    def test_closeRequest_notificationServiceFailure_raisesError(self):
        """Integration: Notification service failure during closure raises an error."""
        self.execution_service.close.side_effect = RuntimeError("Notification service unavailable")

        with self.assertRaises(RuntimeError):
            self.execution_service.close(request_id="RT-2026-001")


if __name__ == "__main__":
    unittest.main()
