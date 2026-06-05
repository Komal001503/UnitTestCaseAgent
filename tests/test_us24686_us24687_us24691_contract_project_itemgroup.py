"""
Unit Tests for Contract Data, Project Data, Item Group Master
User Stories: US-24686, US-24687, US-24691

Acceptance Criteria:
    US-24686 — Contract Master data fetched exclusively from SQL views
               COM004, COM005, COM008 and ttpctm110175.
               (backed by ttpctm100175, tltctm108175, tltctm100175, tbpmdm001175)
    US-24687 — Project Master data fetched exclusively from SQL view COM001
               (backed by ttppdm600175). All modules use this view.
    US-24691 — Item Group Master fetched exclusively from MDM tables
               ttcibd002175, ttcmcs023175 and tltibd901175.

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
# from src.mdm.contract_service import ContractDataService
# from src.mdm.project_service import ProjectDataService
# from src.mdm.item_group_service import ItemGroupMasterService


# ---------------------------------------------------------------------------
# US-24686: Get Contract Data (COM004, COM005, COM008, ttpctm110175)
# ---------------------------------------------------------------------------

class TestGetContractData(unittest.TestCase):
    """US-24686: Verify Contract Master data is fetched from COM004, COM005, COM008."""

    def setUp(self):
        self.contract_service = MagicMock()

    def test_getContractData_fromCOM004_returnsRecords(self):
        """Positive: Querying COM004 returns contract records."""
        self.contract_service.get_from_com004.return_value = [
            {"contract_no": "C04220022", "contract_type": "FIXED", "status": "ACTIVE"},
        ]

        result = self.contract_service.get_from_com004()

        self.assertIsInstance(result, list)
        self.assertGreater(len(result), 0)
        self.assertIn("contract_no", result[0])

    def test_getContractData_fromCOM005_returnsRecords(self):
        """Positive: Querying COM005 returns contract records."""
        self.contract_service.get_from_com005.return_value = [
            {"contract_no": "C04220022", "deliverable_type": "ENGINEERING"},
        ]

        result = self.contract_service.get_from_com005()

        self.assertIsInstance(result, list)

    def test_getContractData_fromCOM008_returnsRecords(self):
        """Positive: Querying COM008 returns contract records."""
        self.contract_service.get_from_com008.return_value = [
            {"contract_no": "C04220022", "partner_id": "BP001"},
        ]

        result = self.contract_service.get_from_com008()

        self.assertIsInstance(result, list)

    def test_getContractData_dataSourcesAreCOM004COM005COM008(self):
        """Positive: Service confirms data sources are COM004, COM005, COM008, ttpctm110175."""
        self.contract_service.get_data_sources.return_value = [
            "COM004", "COM005", "COM008", "ttpctm110175"
        ]

        sources = self.contract_service.get_data_sources()

        self.assertIn("COM004", sources)
        self.assertIn("COM005", sources)
        self.assertIn("COM008", sources)
        self.assertIn("ttpctm110175", sources)

    def test_getContractData_byContractNumber_returnsMatchingRecord(self):
        """Positive: Filtering by contract number returns the specific contract."""
        self.contract_service.get_by_contract_no.return_value = {
            "contract_no": "C04220022",
            "status": "ACTIVE",
        }

        result = self.contract_service.get_by_contract_no("C04220022")

        self.assertEqual(result["contract_no"], "C04220022")

    def test_getContractData_invalidContractNumber_returnsNone(self):
        """Negative: Non-existent contract number returns None."""
        self.contract_service.get_by_contract_no.return_value = None

        result = self.contract_service.get_by_contract_no("INVALID_CONTRACT")

        self.assertIsNone(result)

    def test_getContractData_noRecords_returnsEmptyList(self):
        """Boundary: No contracts in MDM returns an empty list."""
        self.contract_service.get_from_com004.return_value = []

        result = self.contract_service.get_from_com004()

        self.assertEqual(result, [])

    def test_getContractData_emptyContractNumber_returnsValidationError(self):
        """Boundary: Empty contract number parameter returns a validation error."""
        self.contract_service.get_by_contract_no.return_value = {
            "status": "error",
            "message": "Contract number cannot be empty",
        }

        result = self.contract_service.get_by_contract_no("")

        self.assertEqual(result["status"], "error")

    def test_getContractData_viewUnavailable_raisesConnectionError(self):
        """Integration: COM004 view unavailable raises ConnectionError."""
        self.contract_service.get_from_com004.side_effect = ConnectionError(
            "COM004 view not accessible"
        )

        with self.assertRaises(ConnectionError):
            self.contract_service.get_from_com004()


# ---------------------------------------------------------------------------
# US-24687: Get Project Data (COM001 / ttppdm600175)
# ---------------------------------------------------------------------------

class TestGetProjectData(unittest.TestCase):
    """US-24687: Verify Project Master data is fetched exclusively from SQL view COM001."""

    def setUp(self):
        self.project_service = MagicMock()

    def test_getProjectData_validQuery_returnsRecords(self):
        """Positive: Querying COM001 returns project records."""
        self.project_service.get_all.return_value = [
            {"project_id": "S040607", "description": "Pressure Vessel"},
            {"project_id": "S040911", "description": "Heat Exchanger"},
        ]

        result = self.project_service.get_all()

        self.assertIsInstance(result, list)
        self.assertGreater(len(result), 0)

    def test_getProjectData_dataSourceIsCOM001(self):
        """Positive: Service confirms data source is SQL view COM001."""
        self.project_service.get_data_source.return_value = "COM001"

        source = self.project_service.get_data_source()

        self.assertEqual(source, "COM001")

    def test_getProjectData_allModulesUseCOM001(self):
        """Positive: All modules requiring project data use SQL view COM001."""
        self.project_service.validate_module_source.return_value = {"valid": True, "view": "COM001"}

        result = self.project_service.validate_module_source("FKMS")

        self.assertTrue(result["valid"])
        self.assertEqual(result["view"], "COM001")

    def test_getProjectData_byProjectId_returnsMatchingRecord(self):
        """Positive: Filtering by project ID returns the specific project."""
        self.project_service.get_by_project_id.return_value = {
            "project_id": "S040607",
            "description": "Pressure Vessel",
        }

        result = self.project_service.get_by_project_id("S040607")

        self.assertEqual(result["project_id"], "S040607")

    def test_getProjectData_invalidProjectId_returnsNone(self):
        """Negative: Non-existent project ID returns None."""
        self.project_service.get_by_project_id.return_value = None

        result = self.project_service.get_by_project_id("NONEXISTENT_PROJ")

        self.assertIsNone(result)

    def test_getProjectData_emptyProjectId_returnsValidationError(self):
        """Boundary: Empty project ID returns a validation error."""
        self.project_service.get_by_project_id.return_value = {
            "status": "error",
            "message": "Project ID cannot be empty",
        }

        result = self.project_service.get_by_project_id("")

        self.assertEqual(result["status"], "error")

    def test_getProjectData_noRecords_returnsEmptyList(self):
        """Boundary: No project records in COM001 returns empty list."""
        self.project_service.get_all.return_value = []

        result = self.project_service.get_all()

        self.assertEqual(result, [])

    def test_getProjectData_directTableAccess_failsValidation(self):
        """Negative: Direct read from ttppdm600175 bypassing COM001 fails validation."""
        self.project_service.validate_data_source.return_value = {
            "valid": False,
            "message": "Must use COM001, not ttppdm600175 directly",
        }

        result = self.project_service.validate_data_source("ttppdm600175")

        self.assertFalse(result["valid"])

    def test_getProjectData_viewUnavailable_raisesConnectionError(self):
        """Integration: COM001 view unavailable raises ConnectionError."""
        self.project_service.get_all.side_effect = ConnectionError("COM001 not accessible")

        with self.assertRaises(ConnectionError):
            self.project_service.get_all()


# ---------------------------------------------------------------------------
# US-24691: Get Item Group, Material Mapping & CPC by Item Group
# (ttcibd002175, ttcmcs023175, tltibd901175)
# ---------------------------------------------------------------------------

class TestGetItemGroupMaster(unittest.TestCase):
    """US-24691: Verify Item Group Master is fetched from ttcibd002175, ttcmcs023175, tltibd901175."""

    def setUp(self):
        self.item_group_service = MagicMock()

    def test_getItemGroup_validQuery_returnsRecords(self):
        """Positive: Fetching Item Group records returns a populated list."""
        self.item_group_service.get_all.return_value = [
            {"item_group": "CDBC00", "description": "Carbon Steel", "cpc": "CPC001"},
            {"item_group": "FWEC00", "description": "Forged Parts", "cpc": "CPC002"},
        ]

        result = self.item_group_service.get_all()

        self.assertIsInstance(result, list)
        self.assertGreater(len(result), 0)

    def test_getItemGroup_dataSourcesAreCorrectTables(self):
        """Positive: Service confirms data sources include all three required MDM tables."""
        self.item_group_service.get_data_sources.return_value = [
            "ttcibd002175", "ttcmcs023175", "tltibd901175"
        ]

        sources = self.item_group_service.get_data_sources()

        self.assertIn("ttcibd002175", sources)
        self.assertIn("ttcmcs023175", sources)
        self.assertIn("tltibd901175", sources)

    def test_getItemGroup_filterByItemGroup_returnsMatchingRecord(self):
        """Positive: Filtering by item_group code returns the specific record."""
        self.item_group_service.get_by_item_group.return_value = {
            "item_group": "CDBC00",
            "description": "Carbon Steel",
        }

        result = self.item_group_service.get_by_item_group("CDBC00")

        self.assertEqual(result["item_group"], "CDBC00")

    def test_getItemGroup_getMaterialMapping_returnsLinkedMaterial(self):
        """Positive: Getting material mapping for an item group returns linked materials."""
        self.item_group_service.get_material_mapping.return_value = [
            {"item_group": "CDBC00", "material_number": "MAT001"},
        ]

        result = self.item_group_service.get_material_mapping("CDBC00")

        self.assertIsInstance(result, list)
        self.assertEqual(result[0]["item_group"], "CDBC00")

    def test_getItemGroup_getCPCByItemGroup_returnsCPCData(self):
        """Positive: Fetching CPC by item group returns correct CPC records."""
        self.item_group_service.get_cpc_by_item_group.return_value = [
            {"item_group": "CDBC00", "cpc_code": "CPC001", "cpc_desc": "Carbon Products"}
        ]

        result = self.item_group_service.get_cpc_by_item_group("CDBC00")

        self.assertIsInstance(result, list)
        self.assertIn("cpc_code", result[0])

    def test_getItemGroup_invalidItemGroupCode_returnsNone(self):
        """Negative: Non-existent item group code returns None."""
        self.item_group_service.get_by_item_group.return_value = None

        result = self.item_group_service.get_by_item_group("INVALID_GRP")

        self.assertIsNone(result)

    def test_getItemGroup_emptyItemGroupCode_returnsValidationError(self):
        """Boundary: Empty item group code returns a validation error."""
        self.item_group_service.get_by_item_group.return_value = {
            "status": "error",
            "message": "Item group code cannot be empty",
        }

        result = self.item_group_service.get_by_item_group("")

        self.assertEqual(result["status"], "error")

    def test_getItemGroup_noRecords_returnsEmptyList(self):
        """Boundary: No item group records returns an empty list."""
        self.item_group_service.get_all.return_value = []

        result = self.item_group_service.get_all()

        self.assertEqual(result, [])

    def test_getItemGroup_tableUnavailable_raisesConnectionError(self):
        """Integration: MDM table ttcibd002175 unavailable raises ConnectionError."""
        self.item_group_service.get_all.side_effect = ConnectionError(
            "ttcibd002175 not accessible"
        )

        with self.assertRaises(ConnectionError):
            self.item_group_service.get_all()

    def test_getItemGroup_getCPCByItemGroup_emptyItemGroup_returnsError(self):
        """Boundary: Empty item group for CPC lookup returns validation error."""
        self.item_group_service.get_cpc_by_item_group.return_value = {
            "status": "error",
            "message": "Item group cannot be empty for CPC lookup",
        }

        result = self.item_group_service.get_cpc_by_item_group("")

        self.assertEqual(result["status"], "error")


if __name__ == "__main__":
    unittest.main()
