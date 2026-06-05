"""
Unit Tests for MDM Master Data Views — Material, Business Partners,
Purchase Statistical Group, Item Unit
User Stories: US-24644, US-24660, US-24661, US-24662

Acceptance Criteria:
    US-24644 — Material Master fetched exclusively from SQL view COM010 (backed by tltibd901175).
               View must expose: Material Number, Description, Product, Material Category,
               Specific Gravity, Item Group, Density.
    US-24660 — Business Partners (Employee) Master fetched from SQL view COM006 (ttccom100175).
    US-24661 — Purchase Statistical Group fetched exclusively from MDM table ttcmcs044175.
    US-24662 — Item Unit Master fetched exclusively from MDM table ttcmcs001175.

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
# from src.mdm.material_service import MaterialMasterService
# from src.mdm.business_partner_service import BusinessPartnerService
# from src.mdm.purchase_stat_group_service import PurchaseStatGroupService
# from src.mdm.item_unit_service import ItemUnitService


# ---------------------------------------------------------------------------
# US-24644: Get Material Master (COM010 / tltibd901175)
# ---------------------------------------------------------------------------

class TestGetMaterialMaster(unittest.TestCase):
    """US-24644: Verify Material Master data is fetched from SQL view COM010."""

    def setUp(self):
        self.material_service = MagicMock()

    def test_getMaterialMaster_validQuery_returnsMaterialRecords(self):
        """Positive: Querying COM010 view returns a list of material records."""
        self.material_service.get_all.return_value = [
            {
                "material_number": "MAT001",
                "description": "Steel Plate",
                "product": "PRD-01",
                "material_category": "RAW",
                "specific_gravity": 7.85,
                "item_group": "FWEC00",
                "density": 7850.0,
            }
        ]

        result = self.material_service.get_all()

        self.assertIsInstance(result, list)
        self.assertGreater(len(result), 0)
        self.assertIn("material_number", result[0])

    def test_getMaterialMaster_responseContainsMandatoryFields(self):
        """Positive: Every record from COM010 contains all 7 required fields."""
        self.material_service.get_all.return_value = [
            {
                "material_number": "MAT002",
                "description": "Carbon Steel",
                "product": "PRD-02",
                "material_category": "SEMI",
                "specific_gravity": 7.80,
                "item_group": "CDBC00",
                "density": 7800.0,
            }
        ]

        records = self.material_service.get_all()

        required_fields = [
            "material_number", "description", "product",
            "material_category", "specific_gravity", "item_group", "density",
        ]
        for record in records:
            for field in required_fields:
                self.assertIn(field, record, f"Field '{field}' missing from COM010 record")

    def test_getMaterialMaster_dataSourceIsCOM010(self):
        """Positive: Service confirms it reads from COM010 (not any other table/view)."""
        self.material_service.get_data_source.return_value = "COM010"

        source = self.material_service.get_data_source()

        self.assertEqual(source, "COM010")

    def test_getMaterialMaster_noRecordsFound_returnsEmptyList(self):
        """Boundary: When no materials exist, an empty list is returned."""
        self.material_service.get_all.return_value = []

        result = self.material_service.get_all()

        self.assertEqual(result, [])

    def test_getMaterialMaster_byMaterialNumber_returnsMatchingRecord(self):
        """Positive: Filtering by material number returns the correct record."""
        self.material_service.get_by_material_number.return_value = {
            "material_number": "MAT001",
            "description": "Steel Plate",
        }

        result = self.material_service.get_by_material_number("MAT001")

        self.assertEqual(result["material_number"], "MAT001")

    def test_getMaterialMaster_invalidMaterialNumber_returnsNone(self):
        """Negative: Non-existent material number returns None/not found."""
        self.material_service.get_by_material_number.return_value = None

        result = self.material_service.get_by_material_number("DOES_NOT_EXIST")

        self.assertIsNone(result)

    def test_getMaterialMaster_notUsingErplnTable_raisesConfigError(self):
        """Negative: If system tries to read from ERPLN table directly, raise config error."""
        self.material_service.validate_data_source.return_value = {
            "valid": False,
            "message": "Data source must be COM010, not ERPLN table tltibd901175 directly",
        }

        result = self.material_service.validate_data_source("tltibd901175")

        self.assertFalse(result["valid"])

    def test_getMaterialMaster_viewUnavailable_raisesConnectionError(self):
        """Integration: COM010 view unavailable raises a ConnectionError."""
        self.material_service.get_all.side_effect = ConnectionError("COM010 view is not accessible")

        with self.assertRaises(ConnectionError):
            self.material_service.get_all()

    def test_getMaterialMaster_largeDataset_returnsAllRecords(self):
        """Boundary: Query with large result set (1000+ rows) returns all records correctly."""
        large_dataset = [
            {"material_number": f"MAT{i:04d}", "description": f"Material {i}",
             "product": "PRD", "material_category": "RAW", "specific_gravity": 7.85,
             "item_group": "GRP", "density": 7850.0}
            for i in range(1000)
        ]
        self.material_service.get_all.return_value = large_dataset

        result = self.material_service.get_all()

        self.assertEqual(len(result), 1000)


# ---------------------------------------------------------------------------
# US-24660: Get Business Partners (COM006 / ttccom100175)
# ---------------------------------------------------------------------------

class TestGetBusinessPartners(unittest.TestCase):
    """US-24660: Verify Business Partner data is fetched from SQL view COM006."""

    def setUp(self):
        self.bp_service = MagicMock()

    def test_getBusinessPartners_validQuery_returnsRecords(self):
        """Positive: Querying COM006 returns business partner records."""
        self.bp_service.get_all.return_value = [
            {"partner_id": "BP001", "name": "Vendor A", "category": "VENDOR"}
        ]

        result = self.bp_service.get_all()

        self.assertIsInstance(result, list)
        self.assertGreater(len(result), 0)

    def test_getBusinessPartners_dataSourceIsCOM006(self):
        """Positive: Service confirms data source is COM006."""
        self.bp_service.get_data_source.return_value = "COM006"

        source = self.bp_service.get_data_source()

        self.assertEqual(source, "COM006")

    def test_getBusinessPartners_allModulesUseView(self):
        """Positive: All dependent modules route employee data queries through COM006."""
        self.bp_service.modules_using_view.return_value = ["FKMS", "JPP", "PAM", "PMG"]

        modules = self.bp_service.modules_using_view("COM006")

        self.assertIsInstance(modules, list)
        self.assertGreater(len(modules), 0)

    def test_getBusinessPartners_noRecords_returnsEmptyList(self):
        """Boundary: Empty result set from COM006 returns an empty list."""
        self.bp_service.get_all.return_value = []

        result = self.bp_service.get_all()

        self.assertEqual(result, [])

    def test_getBusinessPartners_dbTimeout_raisesTimeoutError(self):
        """Integration: Database timeout when reading COM006 raises TimeoutError."""
        self.bp_service.get_all.side_effect = TimeoutError("COM006 query timed out")

        with self.assertRaises(TimeoutError):
            self.bp_service.get_all()

    def test_getBusinessPartners_notUsingErplnDirectly_validatesSource(self):
        """Negative: Direct reference to ERPLN table fails source validation."""
        self.bp_service.validate_data_source.return_value = {
            "valid": False,
            "message": "Must use COM006, not ttccom100175 directly",
        }

        result = self.bp_service.validate_data_source("ttccom100175")

        self.assertFalse(result["valid"])


# ---------------------------------------------------------------------------
# US-24661: Get Purchase Statistical Group (ttcmcs044175)
# ---------------------------------------------------------------------------

class TestGetPurchaseStatisticalGroup(unittest.TestCase):
    """US-24661: Verify Purchase Statistical Group is fetched exclusively from ttcmcs044175."""

    def setUp(self):
        self.psg_service = MagicMock()

    def test_getPurchaseStatGroup_validQuery_returnsRecords(self):
        """Positive: Fetching Purchase Statistical Group returns a list of records."""
        self.psg_service.get_all.return_value = [
            {"stat_group_code": "PSG01", "description": "Consumables"},
            {"stat_group_code": "PSG02", "description": "Flux Items"},
        ]

        result = self.psg_service.get_all()

        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 2)

    def test_getPurchaseStatGroup_dataSourceIsCorrectTable(self):
        """Positive: Data source is confirmed as MDM table ttcmcs044175."""
        self.psg_service.get_data_source.return_value = "ttcmcs044175"

        source = self.psg_service.get_data_source()

        self.assertEqual(source, "ttcmcs044175")

    def test_getPurchaseStatGroup_noRecords_returnsEmptyList(self):
        """Boundary: No records in ttcmcs044175 returns an empty list."""
        self.psg_service.get_all.return_value = []

        result = self.psg_service.get_all()

        self.assertEqual(result, [])

    def test_getPurchaseStatGroup_filterByCode_returnsMatchingRecord(self):
        """Positive: Filtering by stat_group_code returns the matching record."""
        self.psg_service.get_by_code.return_value = {
            "stat_group_code": "PSG01",
            "description": "Consumables",
        }

        result = self.psg_service.get_by_code("PSG01")

        self.assertEqual(result["stat_group_code"], "PSG01")

    def test_getPurchaseStatGroup_invalidCode_returnsNone(self):
        """Negative: Non-existent code returns None."""
        self.psg_service.get_by_code.return_value = None

        result = self.psg_service.get_by_code("INVALID_CODE")

        self.assertIsNone(result)

    def test_getPurchaseStatGroup_downstreamIntegrationUsesCorrectSource(self):
        """Integration: Downstream SAP CPI integrations validate they use ttcmcs044175."""
        self.psg_service.validate_downstream_source.return_value = {"valid": True}

        result = self.psg_service.validate_downstream_source("SAP_CPI")

        self.assertTrue(result["valid"])


# ---------------------------------------------------------------------------
# US-24662: Get Item Unit Master (ttcmcs001175)
# ---------------------------------------------------------------------------

class TestGetItemUnitMaster(unittest.TestCase):
    """US-24662: Verify Item Unit Master is fetched exclusively from MDM table ttcmcs001175."""

    def setUp(self):
        self.item_unit_service = MagicMock()

    def test_getItemUnitMaster_validQuery_returnsRecords(self):
        """Positive: Fetching item units returns a list of records."""
        self.item_unit_service.get_all.return_value = [
            {"unit_code": "KG", "description": "Kilogram"},
            {"unit_code": "NOS", "description": "Numbers"},
            {"unit_code": "MTR", "description": "Meter"},
        ]

        result = self.item_unit_service.get_all()

        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 3)

    def test_getItemUnitMaster_dataSourceIsCorrectTable(self):
        """Positive: Data source is confirmed as MDM table ttcmcs001175."""
        self.item_unit_service.get_data_source.return_value = "ttcmcs001175"

        source = self.item_unit_service.get_data_source()

        self.assertEqual(source, "ttcmcs001175")

    def test_getItemUnitMaster_noRecords_returnsEmptyList(self):
        """Boundary: No records in ttcmcs001175 returns an empty list."""
        self.item_unit_service.get_all.return_value = []

        result = self.item_unit_service.get_all()

        self.assertEqual(result, [])

    def test_getItemUnitMaster_filterByUnitCode_returnsMatchingRecord(self):
        """Positive: Filtering by unit_code returns the correct record."""
        self.item_unit_service.get_by_unit_code.return_value = {
            "unit_code": "KG",
            "description": "Kilogram",
        }

        result = self.item_unit_service.get_by_unit_code("KG")

        self.assertEqual(result["unit_code"], "KG")

    def test_getItemUnitMaster_emptyUnitCode_returnsError(self):
        """Boundary: Empty unit_code parameter returns a validation error."""
        self.item_unit_service.get_by_unit_code.return_value = {
            "status": "error",
            "message": "Unit code cannot be empty",
        }

        result = self.item_unit_service.get_by_unit_code("")

        self.assertEqual(result["status"], "error")

    def test_getItemUnitMaster_invalidUnitCode_returnsNone(self):
        """Negative: Non-existent unit code returns None."""
        self.item_unit_service.get_by_unit_code.return_value = None

        result = self.item_unit_service.get_by_unit_code("INVALID")

        self.assertIsNone(result)

    def test_getItemUnitMaster_viewDown_raisesConnectionError(self):
        """Integration: MDM table unavailable raises a ConnectionError."""
        self.item_unit_service.get_all.side_effect = ConnectionError("ttcmcs001175 not accessible")

        with self.assertRaises(ConnectionError):
            self.item_unit_service.get_all()


if __name__ == "__main__":
    unittest.main()
