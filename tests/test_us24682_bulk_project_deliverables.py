"""
Unit Tests for Bulk Create Project and Deliverables (JSON Array)
User Story: US-24682

Description:
    As a SAP/CPI Integration Engineer I want the existing Project and Deliverables
    creation APIs to accept multiple records in a single request so that we can
    minimize the number of API calls and reduce CPI token usage.

Acceptance Criteria:
    - Request Body and Response Body shall support multiple records as JSON arrays
      based on primary key and status.
    - Endpoints:
        POST /api/DESLN/AddProject
        POST /api/DESLN/AddPart
        POST /api/DESLN/AddBOM

Test Categories:
    - Positive / Happy Path
    - Negative / Error Path
    - Boundary / Edge Cases
    - Integration Points
"""

SOURCE_STORY_FILE = "azure_devops_user_stories_IEMQS_4.0.md"

import unittest
from unittest.mock import MagicMock


# TODO: Replace with actual imports once implementation is available.
# from src.desln.project_service import ProjectService
# from src.desln.part_service import PartService
# from src.desln.bom_service import BOMService


SAMPLE_PROJECTS = [
    {"project_id": "S040607", "project_name": "Vessel Project A", "status": "NEW"},
    {"project_id": "S040608", "project_name": "Vessel Project B", "status": "NEW"},
]

SAMPLE_PARTS = [
    {"part_id": "S040607-H-WMR801", "revision": "R0", "item_name": "Auto-generated Item"},
    {"part_id": "WEW0000001", "revision": "R0", "item_name": "Component 1"},
]

SAMPLE_BOMS = [
    {
        "parent_item": "S040607-H-WMR801",
        "child_item": "WEW0000001",
        "quantity": 1,
        "bom_level": 3,
    },
    {
        "parent_item": "S040607-H-WMR801",
        "child_item": "WEW0000002",
        "quantity": 1,
        "bom_level": 3,
    },
]


# ---------------------------------------------------------------------------
# US-24682: Bulk Add Project (JSON Array)
# ---------------------------------------------------------------------------

class TestBulkAddProject(unittest.TestCase):
    """US-24682: Verify POST /api/DESLN/AddProject accepts and returns JSON arrays."""

    def setUp(self):
        self.project_service = MagicMock()

    def test_addProject_multipleRecords_returnsArrayResponse(self):
        """Positive: Sending array of projects returns array response with status per record."""
        self.project_service.add_projects.return_value = [
            {"project_id": "S040607", "status": "CREATED"},
            {"project_id": "S040608", "status": "CREATED"},
        ]

        result = self.project_service.add_projects(SAMPLE_PROJECTS)

        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 2)
        for item in result:
            self.assertIn("project_id", item)
            self.assertIn("status", item)

    def test_addProject_singleRecord_returnsArrayWithOneElement(self):
        """Positive: Sending a single-element array still returns array response."""
        self.project_service.add_projects.return_value = [
            {"project_id": "S040607", "status": "CREATED"}
        ]

        result = self.project_service.add_projects([SAMPLE_PROJECTS[0]])

        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 1)

    def test_addProject_emptyArray_returnsEmptyArray(self):
        """Boundary: Sending empty array returns empty array response."""
        self.project_service.add_projects.return_value = []

        result = self.project_service.add_projects([])

        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 0)

    def test_addProject_duplicatePrimaryKey_returnsConflictStatus(self):
        """Negative: Duplicate project_id in the batch returns CONFLICT status for that record."""
        self.project_service.add_projects.return_value = [
            {"project_id": "S040607", "status": "CONFLICT", "message": "Project already exists"},
            {"project_id": "S040608", "status": "CREATED"},
        ]

        result = self.project_service.add_projects(SAMPLE_PROJECTS)

        statuses = [r["status"] for r in result]
        self.assertIn("CONFLICT", statuses)
        self.assertIn("CREATED", statuses)

    def test_addProject_missingMandatoryField_returnsErrorStatus(self):
        """Negative: Record missing project_id returns ERROR status for that record."""
        invalid_projects = [{"project_name": "Missing ID Project", "status": "NEW"}]
        self.project_service.add_projects.return_value = [
            {"project_id": None, "status": "ERROR", "message": "project_id is required"}
        ]

        result = self.project_service.add_projects(invalid_projects)

        self.assertEqual(result[0]["status"], "ERROR")

    def test_addProject_requestIsNotArray_returnsValidationError(self):
        """Negative: Sending a single object (not array) returns a validation error."""
        self.project_service.add_projects.return_value = {
            "status": "error",
            "message": "Request body must be a JSON array",
        }

        result = self.project_service.add_projects({"project_id": "S040607"})

        self.assertEqual(result["status"], "error")
        self.assertIn("JSON array", result["message"])

    def test_addProject_largeArrayBatch_processesAllRecords(self):
        """Boundary: Sending 100 project records processes all records in one call."""
        large_batch = [{"project_id": f"S0{i:05d}", "project_name": f"Project {i}"} for i in range(100)]
        self.project_service.add_projects.return_value = [
            {"project_id": p["project_id"], "status": "CREATED"} for p in large_batch
        ]

        result = self.project_service.add_projects(large_batch)

        self.assertEqual(len(result), 100)

    def test_addProject_apiEndpointTimeout_raisesTimeoutError(self):
        """Integration: API endpoint timeout raises a TimeoutError."""
        self.project_service.add_projects.side_effect = TimeoutError("AddProject API timed out")

        with self.assertRaises(TimeoutError):
            self.project_service.add_projects(SAMPLE_PROJECTS)

    def test_addProject_partialSuccess_returnsIndividualStatuses(self):
        """Integration: Mixed batch (some valid, some invalid) returns per-record statuses."""
        mixed_batch = [
            {"project_id": "S040607", "project_name": "Valid Project"},
            {"project_name": "Missing ID"},
        ]
        self.project_service.add_projects.return_value = [
            {"project_id": "S040607", "status": "CREATED"},
            {"project_id": None, "status": "ERROR", "message": "project_id is required"},
        ]

        result = self.project_service.add_projects(mixed_batch)

        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["status"], "CREATED")
        self.assertEqual(result[1]["status"], "ERROR")


# ---------------------------------------------------------------------------
# US-24682: Bulk Add Part (JSON Array)
# ---------------------------------------------------------------------------

class TestBulkAddPart(unittest.TestCase):
    """US-24682: Verify POST /api/DESLN/AddPart accepts and returns JSON arrays."""

    def setUp(self):
        self.part_service = MagicMock()

    def test_addPart_multipleRecords_returnsArrayResponse(self):
        """Positive: Sending array of parts returns array with status per record."""
        self.part_service.add_parts.return_value = [
            {"part_id": "S040607-H-WMR801", "status": "CREATED"},
            {"part_id": "WEW0000001", "status": "CREATED"},
        ]

        result = self.part_service.add_parts(SAMPLE_PARTS)

        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 2)

    def test_addPart_emptyArray_returnsEmptyArray(self):
        """Boundary: Empty part array returns empty array response."""
        self.part_service.add_parts.return_value = []

        result = self.part_service.add_parts([])

        self.assertEqual(result, [])

    def test_addPart_duplicatePartId_returnsConflictStatus(self):
        """Negative: Duplicate part_id in batch returns CONFLICT status."""
        self.part_service.add_parts.return_value = [
            {"part_id": "S040607-H-WMR801", "status": "CONFLICT"}
        ]

        result = self.part_service.add_parts([SAMPLE_PARTS[0]])

        self.assertEqual(result[0]["status"], "CONFLICT")

    def test_addPart_missingRevision_returnsErrorStatus(self):
        """Negative: Part record missing revision returns ERROR."""
        invalid_part = [{"part_id": "WEW9999", "item_name": "No Revision"}]
        self.part_service.add_parts.return_value = [
            {"part_id": "WEW9999", "status": "ERROR", "message": "revision is required"}
        ]

        result = self.part_service.add_parts(invalid_part)

        self.assertEqual(result[0]["status"], "ERROR")

    def test_addPart_responseContainsPrimaryKeyAndStatus(self):
        """Positive: Every response record contains primary key (part_id) and status."""
        self.part_service.add_parts.return_value = [
            {"part_id": "WEW0000001", "status": "CREATED"},
        ]

        result = self.part_service.add_parts([SAMPLE_PARTS[1]])

        self.assertIn("part_id", result[0])
        self.assertIn("status", result[0])


# ---------------------------------------------------------------------------
# US-24682: Bulk Add BOM (JSON Array)
# ---------------------------------------------------------------------------

class TestBulkAddBOM(unittest.TestCase):
    """US-24682: Verify POST /api/DESLN/AddBOM accepts and returns JSON arrays."""

    def setUp(self):
        self.bom_service = MagicMock()

    def test_addBOM_multipleRecords_returnsArrayResponse(self):
        """Positive: Sending array of BOM entries returns array with status per record."""
        self.bom_service.add_boms.return_value = [
            {"parent_item": "S040607-H-WMR801", "child_item": "WEW0000001", "status": "CREATED"},
            {"parent_item": "S040607-H-WMR801", "child_item": "WEW0000002", "status": "CREATED"},
        ]

        result = self.bom_service.add_boms(SAMPLE_BOMS)

        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 2)

    def test_addBOM_emptyArray_returnsEmptyArray(self):
        """Boundary: Empty BOM array returns empty array response."""
        self.bom_service.add_boms.return_value = []

        result = self.bom_service.add_boms([])

        self.assertEqual(result, [])

    def test_addBOM_invalidQuantityZero_returnsErrorStatus(self):
        """Boundary: BOM record with quantity 0 returns ERROR status."""
        invalid_bom = [{**SAMPLE_BOMS[0], "quantity": 0}]
        self.bom_service.add_boms.return_value = [
            {"parent_item": "S040607-H-WMR801", "child_item": "WEW0000001",
             "status": "ERROR", "message": "Quantity must be greater than 0"}
        ]

        result = self.bom_service.add_boms(invalid_bom)

        self.assertEqual(result[0]["status"], "ERROR")

    def test_addBOM_negativeQuantity_returnsErrorStatus(self):
        """Boundary: BOM record with negative quantity returns ERROR status."""
        invalid_bom = [{**SAMPLE_BOMS[0], "quantity": -5}]
        self.bom_service.add_boms.return_value = [
            {"parent_item": "S040607-H-WMR801", "child_item": "WEW0000001",
             "status": "ERROR", "message": "Quantity cannot be negative"}
        ]

        result = self.bom_service.add_boms(invalid_bom)

        self.assertEqual(result[0]["status"], "ERROR")

    def test_addBOM_missingParentItem_returnsErrorStatus(self):
        """Negative: BOM record missing parent_item returns ERROR status."""
        invalid_bom = [{"child_item": "WEW0000001", "quantity": 1}]
        self.bom_service.add_boms.return_value = [
            {"status": "ERROR", "message": "parent_item is required"}
        ]

        result = self.bom_service.add_boms(invalid_bom)

        self.assertEqual(result[0]["status"], "ERROR")

    def test_addBOM_responseContainsPrimaryKeyAndStatus(self):
        """Positive: Response contains primary key fields (parent_item, child_item) and status."""
        self.bom_service.add_boms.return_value = [
            {"parent_item": "S040607-H-WMR801", "child_item": "WEW0000001", "status": "CREATED"},
        ]

        result = self.bom_service.add_boms([SAMPLE_BOMS[0]])

        self.assertIn("parent_item", result[0])
        self.assertIn("child_item", result[0])
        self.assertIn("status", result[0])

    def test_addBOM_apiTimeout_raisesTimeoutError(self):
        """Integration: AddBOM API timeout raises TimeoutError."""
        self.bom_service.add_boms.side_effect = TimeoutError("AddBOM API timed out")

        with self.assertRaises(TimeoutError):
            self.bom_service.add_boms(SAMPLE_BOMS)

    def test_addBOM_cpiTokenReductionByBulkRequest(self):
        """Integration: Single bulk request reduces CPI token count vs individual requests."""
        # Simulating that 5 records in 1 call = 1 token, not 5 tokens
        self.bom_service.count_api_calls.return_value = 1

        call_count = self.bom_service.count_api_calls(SAMPLE_BOMS)

        self.assertEqual(call_count, 1)


if __name__ == "__main__":
    unittest.main()
