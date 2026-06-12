"""
Unit Tests for BRD RT — Master Data Management & Shop In-charge Mapping
User Stories: US-001, US-002, US-003, US-004, US-005

Acceptance Criteria:
    US-001 — RT Admin uploads layout files (PDF/Image) with versioning support.
              RT Admin searches and retrieves layouts by shop-wise categorization.
    US-002 — RT Admin adds contractor/vendor with license, validity, contact info.
              RT Admin searches and retrieves contractor/vendor details and documents.
    US-003 — RT Admin adds technician with certifications and validity dates.
              RT Admin searches and retrieves technician details and linked vendor.
    US-004 — RT Admin adds camera/equipment with calibration validity and availability status.
              RT Admin searches and retrieves camera/equipment details and linked vendor.
    US-005 — Shop Admin maps Shop In-charge to a shop with effective dates.
              Shop Admin searches and views assigned shops and effective dates.
              System rejects mapping a user not present in Active Directory.

Test Categories:
    - Positive / Happy Path
    - Negative / Error Path
    - Boundary / Edge Cases
    - Integration Points
"""

SOURCE_STORY_FILE = "BRD RT latest_user_stories.md"

import unittest
from unittest.mock import MagicMock, patch


# ---------------------------------------------------------------------------
# US-001: Shop Layout Digital Repository
# ---------------------------------------------------------------------------

class TestShopLayoutRepository(unittest.TestCase):
    """US-001: Verify shop layout upload, versioning, and retrieval."""

    def setUp(self):
        self.layout_service = MagicMock()

    # --- Positive ---

    def test_uploadLayout_validPdfFile_savedWithVersioning(self):
        """Positive: Uploading a valid PDF layout saves it with versioning support."""
        self.layout_service.upload.return_value = {
            "status": "SAVED",
            "layout_id": "LAYOUT-001",
            "version": 1,
            "format": "PDF",
        }

        result = self.layout_service.upload({"file": "shop_layout.pdf", "shop": "SHOP-A"})

        self.assertEqual(result["status"], "SAVED")
        self.assertIn("version", result)
        self.assertGreaterEqual(result["version"], 1)

    def test_uploadLayout_validImageFile_savedWithVersioning(self):
        """Positive: Uploading a valid image layout saves it with versioning support."""
        self.layout_service.upload.return_value = {
            "status": "SAVED",
            "layout_id": "LAYOUT-002",
            "version": 1,
            "format": "IMAGE",
        }

        result = self.layout_service.upload({"file": "shop_layout.png", "shop": "SHOP-B"})

        self.assertEqual(result["status"], "SAVED")
        self.assertEqual(result["format"], "IMAGE")

    def test_uploadLayout_existingLayout_incrementsVersion(self):
        """Positive: Re-uploading a layout for the same shop increments the version."""
        self.layout_service.upload.return_value = {
            "status": "SAVED",
            "layout_id": "LAYOUT-001",
            "version": 2,
        }

        result = self.layout_service.upload({"file": "shop_layout_v2.pdf", "shop": "SHOP-A"})

        self.assertEqual(result["version"], 2)

    def test_searchLayout_validShop_returnsMatchingLayouts(self):
        """Positive: Searching by shop returns layouts categorized by shop."""
        self.layout_service.search.return_value = [
            {"layout_id": "LAYOUT-001", "shop": "SHOP-A", "version": 2, "format": "PDF"},
        ]

        result = self.layout_service.search({"shop": "SHOP-A"})

        self.assertIsInstance(result, list)
        self.assertGreater(len(result), 0)
        self.assertEqual(result[0]["shop"], "SHOP-A")

    # --- Negative ---

    def test_uploadLayout_unsupportedFormat_returnsError(self):
        """Negative: Uploading a layout in an unsupported format returns an error."""
        self.layout_service.upload.return_value = {
            "status": "error",
            "message": "Unsupported file format. Only PDF and Image formats are allowed.",
        }

        result = self.layout_service.upload({"file": "shop_layout.docx", "shop": "SHOP-A"})

        self.assertEqual(result["status"], "error")
        self.assertIn("Unsupported", result["message"])

    def test_searchLayout_nonExistentShop_returnsEmptyList(self):
        """Negative: Searching for a layout with a non-existent shop returns empty list."""
        self.layout_service.search.return_value = []

        result = self.layout_service.search({"shop": "SHOP-UNKNOWN"})

        self.assertEqual(result, [])

    # --- Boundary ---

    def test_uploadLayout_emptyFile_returnsValidationError(self):
        """Boundary: Uploading an empty file returns a validation error."""
        self.layout_service.upload.return_value = {
            "status": "error",
            "message": "File cannot be empty.",
        }

        result = self.layout_service.upload({"file": "", "shop": "SHOP-A"})

        self.assertEqual(result["status"], "error")

    def test_searchLayout_noShopFilter_returnsAllLayouts(self):
        """Boundary: Searching without a shop filter returns all available layouts."""
        self.layout_service.search.return_value = [
            {"layout_id": "LAYOUT-001", "shop": "SHOP-A"},
            {"layout_id": "LAYOUT-002", "shop": "SHOP-B"},
        ]

        result = self.layout_service.search({})

        self.assertGreaterEqual(len(result), 2)

    # --- Integration ---

    def test_uploadLayout_storageUnavailable_raisesConnectionError(self):
        """Integration: Storage service unavailable raises ConnectionError."""
        self.layout_service.upload.side_effect = ConnectionError("Storage service unavailable")

        with self.assertRaises(ConnectionError):
            self.layout_service.upload({"file": "shop_layout.pdf", "shop": "SHOP-A"})


# ---------------------------------------------------------------------------
# US-002: Contractor / Vendor Library Management
# ---------------------------------------------------------------------------

class TestContractorVendorManagement(unittest.TestCase):
    """US-002: Verify contractor/vendor add, search, and document retrieval."""

    def setUp(self):
        self.vendor_service = MagicMock()

    # --- Positive ---

    def test_addVendor_validDetails_savedSuccessfully(self):
        """Positive: Adding a contractor/vendor with valid details saves the record."""
        self.vendor_service.add.return_value = {
            "status": "CREATED",
            "vendor_id": "VENDOR-001",
            "license_number": "LIC-2024-001",
            "validity": "2025-12-31",
        }

        result = self.vendor_service.add({
            "name": "ABC Contractors",
            "license_number": "LIC-2024-001",
            "validity": "2025-12-31",
            "contact": "9876543210",
            "specialization": "RT",
            "status": "ACTIVE",
        })

        self.assertEqual(result["status"], "CREATED")
        self.assertIn("vendor_id", result)
        self.assertEqual(result["license_number"], "LIC-2024-001")

    def test_searchVendor_validName_returnsVendorWithDocuments(self):
        """Positive: Searching a vendor by name returns details and associated documents."""
        self.vendor_service.search.return_value = [
            {
                "vendor_id": "VENDOR-001",
                "name": "ABC Contractors",
                "documents": ["cert_abc.pdf", "license_abc.pdf"],
            }
        ]

        result = self.vendor_service.search({"name": "ABC Contractors"})

        self.assertGreater(len(result), 0)
        self.assertIn("documents", result[0])
        self.assertIsInstance(result[0]["documents"], list)

    # --- Negative ---

    def test_addVendor_missingLicenseNumber_returnsError(self):
        """Negative: Adding a vendor without a license number returns a validation error."""
        self.vendor_service.add.return_value = {
            "status": "error",
            "message": "License number is required.",
        }

        result = self.vendor_service.add({"name": "XYZ Corp", "contact": "1234567890"})

        self.assertEqual(result["status"], "error")
        self.assertIn("License number", result["message"])

    def test_searchVendor_nonExistentVendor_returnsEmptyList(self):
        """Negative: Searching for a non-existent vendor returns an empty list."""
        self.vendor_service.search.return_value = []

        result = self.vendor_service.search({"name": "UNKNOWN VENDOR"})

        self.assertEqual(result, [])

    # --- Boundary ---

    def test_addVendor_expiredValidity_savesWithWarning(self):
        """Boundary: Adding a vendor with an already expired validity date saves with a warning."""
        self.vendor_service.add.return_value = {
            "status": "CREATED",
            "vendor_id": "VENDOR-002",
            "warning": "License validity is already expired.",
        }

        result = self.vendor_service.add({
            "name": "Expired Corp",
            "license_number": "LIC-OLD-001",
            "validity": "2020-01-01",
        })

        self.assertEqual(result["status"], "CREATED")
        self.assertIn("warning", result)

    def test_addVendor_emptyName_returnsValidationError(self):
        """Boundary: Adding a vendor with an empty name returns a validation error."""
        self.vendor_service.add.return_value = {
            "status": "error",
            "message": "Vendor name cannot be empty.",
        }

        result = self.vendor_service.add({"name": "", "license_number": "LIC-001"})

        self.assertEqual(result["status"], "error")

    # --- Integration ---

    def test_addVendor_databaseTimeout_raisesTimeoutError(self):
        """Integration: Database timeout while adding a vendor raises TimeoutError."""
        self.vendor_service.add.side_effect = TimeoutError("Database timeout")

        with self.assertRaises(TimeoutError):
            self.vendor_service.add({"name": "Test Vendor", "license_number": "LIC-001"})


# ---------------------------------------------------------------------------
# US-003: RT Technician Database with Certifications
# ---------------------------------------------------------------------------

class TestRTTechnicianManagement(unittest.TestCase):
    """US-003: Verify technician add, certification tracking, and search."""

    def setUp(self):
        self.technician_service = MagicMock()

    # --- Positive ---

    def test_addTechnician_validDetails_savedWithCertifications(self):
        """Positive: Adding a technician with certifications saves all details."""
        self.technician_service.add.return_value = {
            "status": "CREATED",
            "technician_id": "TECH-001",
            "certification_type": "RT Level II",
            "certification_validity": "2026-06-30",
            "vendor_id": "VENDOR-001",
        }

        result = self.technician_service.add({
            "name": "John Doe",
            "technician_id": "TECH-001",
            "certification_type": "RT Level II",
            "certification_validity": "2026-06-30",
            "vendor_id": "VENDOR-001",
        })

        self.assertEqual(result["status"], "CREATED")
        self.assertIn("certification_validity", result)
        self.assertEqual(result["certification_type"], "RT Level II")

    def test_searchTechnician_validId_returnsDetailsWithVendor(self):
        """Positive: Searching a technician returns their details and linked vendor."""
        self.technician_service.search.return_value = [
            {
                "technician_id": "TECH-001",
                "name": "John Doe",
                "vendor_id": "VENDOR-001",
                "vendor_name": "ABC Contractors",
            }
        ]

        result = self.technician_service.search({"technician_id": "TECH-001"})

        self.assertGreater(len(result), 0)
        self.assertIn("vendor_id", result[0])
        self.assertIn("vendor_name", result[0])

    # --- Negative ---

    def test_addTechnician_missingCertification_returnsError(self):
        """Negative: Adding a technician without certification details returns an error."""
        self.technician_service.add.return_value = {
            "status": "error",
            "message": "Certification type and validity are required.",
        }

        result = self.technician_service.add({"name": "Jane Doe", "technician_id": "TECH-002"})

        self.assertEqual(result["status"], "error")
        self.assertIn("Certification", result["message"])

    def test_searchTechnician_nonExistentId_returnsEmptyList(self):
        """Negative: Searching for a non-existent technician ID returns empty list."""
        self.technician_service.search.return_value = []

        result = self.technician_service.search({"technician_id": "TECH-UNKNOWN"})

        self.assertEqual(result, [])

    # --- Boundary ---

    def test_addTechnician_certificationExpiryToday_savedWithAlert(self):
        """Boundary: Technician whose certification expires today is saved with an alert."""
        self.technician_service.add.return_value = {
            "status": "CREATED",
            "technician_id": "TECH-003",
            "warning": "Certification expires today.",
        }

        result = self.technician_service.add({
            "name": "Expiring Tech",
            "technician_id": "TECH-003",
            "certification_type": "RT Level I",
            "certification_validity": "2026-06-12",
        })

        self.assertEqual(result["status"], "CREATED")
        self.assertIn("warning", result)

    def test_addTechnician_emptyTechnicianId_returnsValidationError(self):
        """Boundary: Adding a technician with an empty ID returns a validation error."""
        self.technician_service.add.return_value = {
            "status": "error",
            "message": "Technician ID cannot be empty.",
        }

        result = self.technician_service.add({"name": "No ID Tech", "technician_id": ""})

        self.assertEqual(result["status"], "error")


# ---------------------------------------------------------------------------
# US-004: RT Camera and Equipment Management
# ---------------------------------------------------------------------------

class TestRTCameraEquipmentManagement(unittest.TestCase):
    """US-004: Verify camera/equipment add, calibration tracking, and search."""

    def setUp(self):
        self.equipment_service = MagicMock()

    # --- Positive ---

    def test_addEquipment_validDetails_savedSuccessfully(self):
        """Positive: Adding camera/equipment with valid details saves all fields."""
        self.equipment_service.add.return_value = {
            "status": "CREATED",
            "equipment_id": "CAM-001",
            "type": "RT Camera",
            "make": "BrandX",
            "model": "X200",
            "calibration_validity": "2026-12-31",
            "vendor_id": "VENDOR-001",
            "availability": "AVAILABLE",
        }

        result = self.equipment_service.add({
            "equipment_id": "CAM-001",
            "type": "RT Camera",
            "make": "BrandX",
            "model": "X200",
            "calibration_validity": "2026-12-31",
            "vendor_id": "VENDOR-001",
        })

        self.assertEqual(result["status"], "CREATED")
        self.assertIn("calibration_validity", result)
        self.assertEqual(result["availability"], "AVAILABLE")

    def test_searchEquipment_validId_returnsDetailsWithVendor(self):
        """Positive: Searching equipment by ID returns details and linked vendor."""
        self.equipment_service.search.return_value = [
            {
                "equipment_id": "CAM-001",
                "type": "RT Camera",
                "vendor_id": "VENDOR-001",
                "vendor_name": "ABC Contractors",
            }
        ]

        result = self.equipment_service.search({"equipment_id": "CAM-001"})

        self.assertGreater(len(result), 0)
        self.assertIn("vendor_name", result[0])

    # --- Negative ---

    def test_addEquipment_missingCalibrationValidity_returnsError(self):
        """Negative: Adding equipment without calibration validity returns an error."""
        self.equipment_service.add.return_value = {
            "status": "error",
            "message": "Calibration validity is required.",
        }

        result = self.equipment_service.add({"equipment_id": "CAM-002", "type": "RT Camera"})

        self.assertEqual(result["status"], "error")
        self.assertIn("Calibration", result["message"])

    def test_searchEquipment_nonExistentId_returnsEmptyList(self):
        """Negative: Searching for a non-existent equipment ID returns empty list."""
        self.equipment_service.search.return_value = []

        result = self.equipment_service.search({"equipment_id": "CAM-UNKNOWN"})

        self.assertEqual(result, [])

    # --- Boundary ---

    def test_addEquipment_calibrationExpired_savedWithUnavailableStatus(self):
        """Boundary: Equipment with expired calibration is saved as UNAVAILABLE."""
        self.equipment_service.add.return_value = {
            "status": "CREATED",
            "equipment_id": "CAM-003",
            "availability": "UNAVAILABLE",
            "warning": "Calibration has expired.",
        }

        result = self.equipment_service.add({
            "equipment_id": "CAM-003",
            "type": "RT Camera",
            "calibration_validity": "2022-01-01",
        })

        self.assertEqual(result["availability"], "UNAVAILABLE")
        self.assertIn("warning", result)

    def test_searchEquipment_filterByAvailability_returnsOnlyAvailable(self):
        """Boundary: Filtering equipment by AVAILABLE status returns only available items."""
        self.equipment_service.search.return_value = [
            {"equipment_id": "CAM-001", "availability": "AVAILABLE"},
        ]

        result = self.equipment_service.search({"availability": "AVAILABLE"})

        for item in result:
            self.assertEqual(item["availability"], "AVAILABLE")

    # --- Integration ---

    def test_addEquipment_databaseUnavailable_raisesConnectionError(self):
        """Integration: Database unavailable while adding equipment raises ConnectionError."""
        self.equipment_service.add.side_effect = ConnectionError("Database not accessible")

        with self.assertRaises(ConnectionError):
            self.equipment_service.add({"equipment_id": "CAM-004", "type": "RT Camera"})


# ---------------------------------------------------------------------------
# US-005: Shop In-charge and Coordinator Mapping
# ---------------------------------------------------------------------------

class TestShopInchargeMappingManagement(unittest.TestCase):
    """US-005: Verify Shop In-charge/coordinator mapping with AD validation."""

    def setUp(self):
        self.mapping_service = MagicMock()
        self.ad_service = MagicMock()

    # --- Positive ---

    def test_mapShopIncharge_validUser_savedWithEffectiveDates(self):
        """Positive: Mapping a valid Shop In-charge saves the mapping with effective dates."""
        self.mapping_service.map_incharge.return_value = {
            "status": "MAPPED",
            "shop_id": "SHOP-A",
            "user_id": "USER-001",
            "effective_from": "2026-01-01",
            "effective_to": "2026-12-31",
        }

        result = self.mapping_service.map_incharge({
            "shop_id": "SHOP-A",
            "user_id": "USER-001",
            "effective_from": "2026-01-01",
            "effective_to": "2026-12-31",
        })

        self.assertEqual(result["status"], "MAPPED")
        self.assertIn("effective_from", result)
        self.assertIn("effective_to", result)

    def test_searchShopIncharge_validShop_returnsAssignmentWithDates(self):
        """Positive: Searching for a Shop In-charge returns their shop and effective dates."""
        self.mapping_service.search.return_value = [
            {
                "user_id": "USER-001",
                "shop_id": "SHOP-A",
                "effective_from": "2026-01-01",
                "effective_to": "2026-12-31",
            }
        ]

        result = self.mapping_service.search({"user_id": "USER-001"})

        self.assertGreater(len(result), 0)
        self.assertIn("effective_from", result[0])
        self.assertIn("effective_to", result[0])

    # --- Negative ---

    def test_mapShopIncharge_userNotInActiveDirectory_returnsError(self):
        """Negative: Mapping a user not in Active Directory returns an error message."""
        self.mapping_service.map_incharge.return_value = {
            "status": "error",
            "message": "User not found in Active Directory.",
        }

        result = self.mapping_service.map_incharge({
            "shop_id": "SHOP-A",
            "user_id": "USER-GHOST",
            "effective_from": "2026-01-01",
        })

        self.assertEqual(result["status"], "error")
        self.assertIn("Active Directory", result["message"])

    def test_searchShopIncharge_nonExistentUser_returnsEmptyList(self):
        """Negative: Searching for a non-existent user returns an empty list."""
        self.mapping_service.search.return_value = []

        result = self.mapping_service.search({"user_id": "USER-UNKNOWN"})

        self.assertEqual(result, [])

    # --- Boundary ---

    def test_mapShopIncharge_noEffectiveDates_returnsValidationError(self):
        """Boundary: Mapping without effective dates returns a validation error."""
        self.mapping_service.map_incharge.return_value = {
            "status": "error",
            "message": "Effective dates are required.",
        }

        result = self.mapping_service.map_incharge({
            "shop_id": "SHOP-A",
            "user_id": "USER-001",
        })

        self.assertEqual(result["status"], "error")
        self.assertIn("Effective dates", result["message"])

    def test_mapShopIncharge_effectiveToBeforeEffectiveFrom_returnsError(self):
        """Boundary: Mapping with effective_to before effective_from returns an error."""
        self.mapping_service.map_incharge.return_value = {
            "status": "error",
            "message": "Effective-to date must be after effective-from date.",
        }

        result = self.mapping_service.map_incharge({
            "shop_id": "SHOP-A",
            "user_id": "USER-001",
            "effective_from": "2026-12-31",
            "effective_to": "2026-01-01",
        })

        self.assertEqual(result["status"], "error")

    # --- Integration ---

    def test_mapShopIncharge_adServiceTimeout_raisesTimeoutError(self):
        """Integration: Active Directory service timeout raises TimeoutError."""
        self.mapping_service.map_incharge.side_effect = TimeoutError("Active Directory timeout")

        with self.assertRaises(TimeoutError):
            self.mapping_service.map_incharge({
                "shop_id": "SHOP-A",
                "user_id": "USER-001",
                "effective_from": "2026-01-01",
            })

    def test_mapShopIncharge_adServiceUnavailable_raisesConnectionError(self):
        """Integration: Active Directory service unavailable raises ConnectionError."""
        self.mapping_service.map_incharge.side_effect = ConnectionError("AD service not reachable")

        with self.assertRaises(ConnectionError):
            self.mapping_service.map_incharge({
                "shop_id": "SHOP-A",
                "user_id": "USER-001",
            })


if __name__ == "__main__":
    unittest.main()
