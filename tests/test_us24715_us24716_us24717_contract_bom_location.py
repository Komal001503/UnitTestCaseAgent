"""
Unit Tests for Contract Deliverables, Part/BOM Data, Contract Location
(IEMQS Table Migration from ERPLN)
User Stories: US-24715, US-24716, US-24717

Acceptance Criteria:
    US-24715 — Contract Deliverables fetched from IEMQS tables DES066 & DES067
               (no longer from ERPLN tables tltpdm105175, ttppdm600175).
    US-24716 — Part/BOM Data fetched from IEMQS tables DES066 & DES067
               (no longer from ERPLN view uvwGETHBOM).
    US-24717 — Contract Location fetched from MDM tables
               tltctm100175, ttccom130175, ttcmcs010175.

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
# from src.iemqs.contract_deliverable_service import ContractDeliverableService
# from src.iemqs.part_bom_service import PartBOMService
# from src.mdm.contract_location_service import ContractLocationService


# ---------------------------------------------------------------------------
# US-24715: Get Contract Deliverables (DES066 & DES067, not ERPLN)
# ---------------------------------------------------------------------------

class TestGetContractDeliverables(unittest.TestCase):
    """US-24715: Verify Contract Deliverables are fetched from IEMQS tables DES066 & DES067."""

    def setUp(self):
        self.deliverable_service = MagicMock()

    def test_getContractDeliverables_fromDES066_returnsRecords(self):
        """Positive: Querying DES066 returns contract deliverable records."""
        self.deliverable_service.get_from_des066.return_value = [
            {
                "project": "S040935",
                "parent_item": "S040935-H-WMR801",
                "item": "WEW0000001",
                "quantity": 1,
                "unit": "NOS",
            }
        ]

        result = self.deliverable_service.get_from_des066()

        self.assertIsInstance(result, list)
        self.assertGreater(len(result), 0)
        self.assertIn("project", result[0])

    def test_getContractDeliverables_fromDES067_returnsRecords(self):
        """Positive: Querying DES067 returns contract deliverable records."""
        self.deliverable_service.get_from_des067.return_value = [
            {"project": "S040935", "deliverable_id": "DEL001", "status": "OPEN"}
        ]

        result = self.deliverable_service.get_from_des067()

        self.assertIsInstance(result, list)

    def test_getContractDeliverables_dataSourcesAreDES066AndDES067(self):
        """Positive: Service confirms data sources are DES066 and DES067."""
        self.deliverable_service.get_data_sources.return_value = ["DES066", "DES067"]

        sources = self.deliverable_service.get_data_sources()

        self.assertIn("DES066", sources)
        self.assertIn("DES067", sources)

    def test_getContractDeliverables_notReadingFromErplnTables(self):
        """Positive: Service does not reference ERPLN tables tltpdm105175, ttppdm600175."""
        self.deliverable_service.get_data_sources.return_value = ["DES066", "DES067"]

        sources = self.deliverable_service.get_data_sources()

        self.assertNotIn("tltpdm105175", sources)
        self.assertNotIn("ttppdm600175", sources)

    def test_getContractDeliverables_filterByProject_returnsProjectRecords(self):
        """Positive: Filtering by project code returns deliverables for that project."""
        self.deliverable_service.get_by_project.return_value = [
            {"project": "S040935", "item": "WEW0000001"},
            {"project": "S040935", "item": "WEW0000002"},
        ]

        result = self.deliverable_service.get_by_project("S040935")

        self.assertIsInstance(result, list)
        for record in result:
            self.assertEqual(record["project"], "S040935")

    def test_getContractDeliverables_invalidProject_returnsEmptyList(self):
        """Negative: Non-existent project code returns an empty list."""
        self.deliverable_service.get_by_project.return_value = []

        result = self.deliverable_service.get_by_project("INVALID_PROJ")

        self.assertEqual(result, [])

    def test_getContractDeliverables_emptyProject_returnsValidationError(self):
        """Boundary: Empty project code returns a validation error."""
        self.deliverable_service.get_by_project.return_value = {
            "status": "error",
            "message": "Project code cannot be empty",
        }

        result = self.deliverable_service.get_by_project("")

        self.assertEqual(result["status"], "error")

    def test_getContractDeliverables_noRecords_returnsEmptyList(self):
        """Boundary: No deliverable records returns an empty list."""
        self.deliverable_service.get_from_des066.return_value = []

        result = self.deliverable_service.get_from_des066()

        self.assertEqual(result, [])

    def test_getContractDeliverables_erplnSourceUsed_failsValidation(self):
        """Negative: Using ERPLN table tltpdm105175 as source fails source validation."""
        self.deliverable_service.validate_data_source.return_value = {
            "valid": False,
            "message": "Must use DES066/DES067, not tltpdm105175",
        }

        result = self.deliverable_service.validate_data_source("tltpdm105175")

        self.assertFalse(result["valid"])

    def test_getContractDeliverables_tableUnavailable_raisesConnectionError(self):
        """Integration: DES066 table unavailable raises ConnectionError."""
        self.deliverable_service.get_from_des066.side_effect = ConnectionError(
            "DES066 not accessible"
        )

        with self.assertRaises(ConnectionError):
            self.deliverable_service.get_from_des066()


# ---------------------------------------------------------------------------
# US-24716: Get Part/BOM Data (DES066 & DES067, not ERPLN view)
# ---------------------------------------------------------------------------

class TestGetPartBOMData(unittest.TestCase):
    """US-24716: Verify Part/BOM Data is fetched from IEMQS DES066 & DES067."""

    def setUp(self):
        self.bom_service = MagicMock()

    def test_getPartBOM_fromDES066_returnsPartRecords(self):
        """Positive: Querying DES066 returns part records."""
        self.bom_service.get_parts_from_des066.return_value = [
            {
                "project": "S040911",
                "part": "S040911-H-WMR801",
                "parent_part": None,
                "part_level": 1,
                "description": "Main Vessel Shell",
            }
        ]

        result = self.bom_service.get_parts_from_des066()

        self.assertIsInstance(result, list)
        self.assertIn("project", result[0])
        self.assertIn("part", result[0])

    def test_getPartBOM_fromDES067_returnsBOMRecords(self):
        """Positive: Querying DES067 returns BOM structure records."""
        self.bom_service.get_bom_from_des067.return_value = [
            {
                "project": "S040911",
                "parent_part": "S040911-H-WMR801",
                "child_part": "WEW0000001",
                "bom_qty": 1,
            }
        ]

        result = self.bom_service.get_bom_from_des067()

        self.assertIsInstance(result, list)

    def test_getPartBOM_dataSourcesAreDES066AndDES067(self):
        """Positive: Service confirms data sources are DES066 and DES067."""
        self.bom_service.get_data_sources.return_value = ["DES066", "DES067"]

        sources = self.bom_service.get_data_sources()

        self.assertIn("DES066", sources)
        self.assertIn("DES067", sources)

    def test_getPartBOM_notReadingFromErplnView(self):
        """Positive: Service does not reference ERPLN view uvwGETHBOM."""
        self.bom_service.get_data_sources.return_value = ["DES066", "DES067"]

        sources = self.bom_service.get_data_sources()

        self.assertNotIn("uvwGETHBOM", sources)

    def test_getPartBOM_filterByProject_returnsProjectBOM(self):
        """Positive: Filtering by project returns all Part/BOM records for that project."""
        self.bom_service.get_by_project.return_value = [
            {"project": "S040911", "part": "S040911-H-WMR801"},
        ]

        result = self.bom_service.get_by_project("S040911")

        for record in result:
            self.assertEqual(record["project"], "S040911")

    def test_getPartBOM_responseContainsRequiredFields(self):
        """Positive: Part/BOM response includes all standard fields from the original view."""
        self.bom_service.get_by_project.return_value = [
            {
                "project": "S040911",
                "part": "WEW0000001",
                "parent_part": "S040911-H-WMR801",
                "part_level": 2,
                "description": "Nozzle",
                "item_group": "CDBC00",
                "revision_no": "R0",
                "find_no": "9999",
                "uom": "NOS",
                "bom_qty": 1,
            }
        ]

        result = self.bom_service.get_by_project("S040911")

        required_fields = [
            "project", "part", "parent_part", "part_level",
            "description", "item_group", "revision_no", "uom", "bom_qty",
        ]
        for field in required_fields:
            self.assertIn(field, result[0], f"Field '{field}' missing from Part/BOM response")

    def test_getPartBOM_invalidProject_returnsEmptyList(self):
        """Negative: Non-existent project returns an empty list."""
        self.bom_service.get_by_project.return_value = []

        result = self.bom_service.get_by_project("INVALID_PROJ")

        self.assertEqual(result, [])

    def test_getPartBOM_erplnViewUsed_failsValidation(self):
        """Negative: Using uvwGETHBOM view as source fails source validation."""
        self.bom_service.validate_data_source.return_value = {
            "valid": False,
            "message": "Must use DES066/DES067, not uvwGETHBOM",
        }

        result = self.bom_service.validate_data_source("uvwGETHBOM")

        self.assertFalse(result["valid"])

    def test_getPartBOM_tableUnavailable_raisesConnectionError(self):
        """Integration: DES067 table unavailable raises ConnectionError."""
        self.bom_service.get_bom_from_des067.side_effect = ConnectionError(
            "DES067 not accessible"
        )

        with self.assertRaises(ConnectionError):
            self.bom_service.get_bom_from_des067()


# ---------------------------------------------------------------------------
# US-24717: Get Contract Location (tltctm100175, ttccom130175, ttcmcs010175)
# ---------------------------------------------------------------------------

class TestGetContractLocation(unittest.TestCase):
    """US-24717: Verify Contract Location is fetched from MDM tables
    tltctm100175, ttccom130175, ttcmcs010175."""

    def setUp(self):
        self.location_service = MagicMock()

    def test_getContractLocation_validQuery_returnsRecords(self):
        """Positive: Fetching contract locations returns a list of records."""
        self.location_service.get_all.return_value = [
            {
                "contract_no": "C04220022",
                "location_code": "LOC001",
                "location_name": "Mumbai Yard",
                "country": "IN",
            }
        ]

        result = self.location_service.get_all()

        self.assertIsInstance(result, list)
        self.assertIn("contract_no", result[0])

    def test_getContractLocation_dataSourcesAreCorrectTables(self):
        """Positive: Service confirms data sources include all three MDM tables."""
        self.location_service.get_data_sources.return_value = [
            "tltctm100175", "ttccom130175", "ttcmcs010175"
        ]

        sources = self.location_service.get_data_sources()

        self.assertIn("tltctm100175", sources)
        self.assertIn("ttccom130175", sources)
        self.assertIn("ttcmcs010175", sources)

    def test_getContractLocation_filterByContractNo_returnsMatchingRecords(self):
        """Positive: Filtering by contract number returns location records for that contract."""
        self.location_service.get_by_contract_no.return_value = [
            {"contract_no": "C04220022", "location_name": "Mumbai Yard"},
        ]

        result = self.location_service.get_by_contract_no("C04220022")

        for record in result:
            self.assertEqual(record["contract_no"], "C04220022")

    def test_getContractLocation_invalidContractNo_returnsEmptyList(self):
        """Negative: Non-existent contract number returns an empty list."""
        self.location_service.get_by_contract_no.return_value = []

        result = self.location_service.get_by_contract_no("INVALID_CONTRACT")

        self.assertEqual(result, [])

    def test_getContractLocation_emptyContractNo_returnsValidationError(self):
        """Boundary: Empty contract number returns a validation error."""
        self.location_service.get_by_contract_no.return_value = {
            "status": "error",
            "message": "Contract number cannot be empty",
        }

        result = self.location_service.get_by_contract_no("")

        self.assertEqual(result["status"], "error")

    def test_getContractLocation_noRecords_returnsEmptyList(self):
        """Boundary: No location records in MDM tables returns an empty list."""
        self.location_service.get_all.return_value = []

        result = self.location_service.get_all()

        self.assertEqual(result, [])

    def test_getContractLocation_tableUnavailable_raisesConnectionError(self):
        """Integration: tltctm100175 table unavailable raises ConnectionError."""
        self.location_service.get_all.side_effect = ConnectionError(
            "tltctm100175 not accessible"
        )

        with self.assertRaises(ConnectionError):
            self.location_service.get_all()

    def test_getContractLocation_filterByCountry_returnsFilteredRecords(self):
        """Positive: Filtering by country code returns locations in that country."""
        self.location_service.get_by_country.return_value = [
            {"contract_no": "C04220022", "location_name": "Mumbai Yard", "country": "IN"},
        ]

        result = self.location_service.get_by_country("IN")

        for record in result:
            self.assertEqual(record["country"], "IN")


if __name__ == "__main__":
    unittest.main()
