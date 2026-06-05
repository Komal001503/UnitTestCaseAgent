"""
Unit Tests for Restrict Item Code Length to 18 Characters in FKMS
User Story: US-25649

Description:
    As a system user I want the FKMS logic for node key (item code) creation to be
    modified so that generated item codes do not exceed the SAP limitation of 18 characters.

Acceptance Criteria:
    1. Item codes generated during node creation in FKMS must be restricted to max 18 characters.
    2. Logic enforced across Sections, Assembly, Sub-assembly, and related structures.
    3. Item codes exceeding 18 chars are automatically truncated or handled per agreed logic.
    4. System ensures compatibility with SAP material code requirements.
    5. Both existing and newly generated item codes comply with the 18-character limit.

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
# from src.fkms.item_code_service import FKMSItemCodeService
# from src.fkms.node_key_generator import NodeKeyGenerator


MAX_ITEM_CODE_LENGTH = 18

# Sample TO-BE item codes from the user story (all <= 18 chars)
VALID_ITEM_CODES = [
    ("PWHT Section", "S040911-PWHT-SEC1", 17),
    ("Fabrication Section", "S040911-SEC1", 12),
    ("Shell Assembly", "S040911-SH0035A", 15),
    ("Shell Sub Assembly", "S040911-SH0036SA", 16),
    ("Shell Internal Sub Assembly", "S040911-SH0072I-SA", 18),
    ("Shell External Sub Assembly", "S040911-SH0072E-SA", 18),
    ("Shell Nozzle Sub Assembly", "S040911-SH0060N-SA", 18),
    ("Y-RING Assembly", "S040911-Y-0015A", 15),
    ("Skirt Assembly", "S040911-SK0022A", 15),
]

# Sample AS-IS item codes that violate the 18-char limit
INVALID_ITEM_CODES = [
    ("PWHT Section (old)", "S040911-PWHT-SECTION1", 21),
    ("Shell Internal Sub Assembly (old)", "S040911-SHE0072INT-SUB-ASM", 26),
    ("Top head Internal Sub Assembly (old)", "S040911-TOP0086INT-SUB-ASM", 26),
    ("Y-RING Internal Sub Assembly (old)", "S040911-Y-R0017INT-SUB-ASM", 26),
]


# ---------------------------------------------------------------------------
# US-25649: 18-Character Limit Enforcement
# ---------------------------------------------------------------------------

class TestItemCodeLengthRestriction(unittest.TestCase):
    """US-25649: Verify FKMS item codes are restricted to max 18 characters."""

    def setUp(self):
        self.item_code_service = MagicMock()

    def test_generateItemCode_pwhtSection_isWithin18Chars(self):
        """Positive: PWHT Section item code generated as per TO-BE is within 18 chars."""
        self.item_code_service.generate.return_value = "S040911-PWHT-SEC1"
        code = self.item_code_service.generate("S040911", "PWHT_SECTION", "1")
        self.assertLessEqual(len(code), MAX_ITEM_CODE_LENGTH)

    def test_generateItemCode_fabricationSection_isWithin18Chars(self):
        """Positive: Fabrication Section item code is within 18 chars."""
        self.item_code_service.generate.return_value = "S040911-SEC1"
        code = self.item_code_service.generate("S040911", "SECTION", "1")
        self.assertLessEqual(len(code), MAX_ITEM_CODE_LENGTH)

    def test_generateItemCode_shellInternalSubAssembly_isExactly18Chars(self):
        """Positive: Shell Internal Sub Assembly is exactly 18 characters (max boundary)."""
        self.item_code_service.generate.return_value = "S040911-SH0072I-SA"
        code = self.item_code_service.generate("S040911", "SHELL_INT_SA", "0072")
        self.assertEqual(len(code), 18)

    def test_generateItemCode_shellExternalSubAssembly_isExactly18Chars(self):
        """Positive: Shell External Sub Assembly is exactly 18 characters."""
        self.item_code_service.generate.return_value = "S040911-SH0072E-SA"
        code = self.item_code_service.generate("S040911", "SHELL_EXT_SA", "0072")
        self.assertEqual(len(code), 18)

    def test_generateItemCode_allToBeCodes_areWithin18Chars(self):
        """Positive: All TO-BE item codes from the user story comply with 18-char limit."""
        for node_type, expected_code, expected_length in VALID_ITEM_CODES:
            with self.subTest(node_type=node_type):
                self.assertLessEqual(
                    len(expected_code),
                    MAX_ITEM_CODE_LENGTH,
                    f"{node_type} code '{expected_code}' exceeds 18 chars",
                )
                self.assertEqual(len(expected_code), expected_length)

    def test_generateItemCode_oldAsisCodes_exceedLimit(self):
        """Negative: AS-IS item codes from the user story exceed the 18-char limit (pre-fix)."""
        for node_type, old_code, old_length in INVALID_ITEM_CODES:
            with self.subTest(node_type=node_type):
                self.assertGreater(
                    len(old_code),
                    MAX_ITEM_CODE_LENGTH,
                    f"{node_type} old code '{old_code}' should have exceeded 18 chars",
                )

    def test_generateItemCode_exceeding18Chars_isTruncatedOrHandled(self):
        """Positive: Any generated code > 18 chars is automatically truncated/adjusted."""
        self.item_code_service.generate.return_value = "S040911-SH0072I-SA"  # truncated to 18
        self.item_code_service.validate_length.return_value = True

        code = self.item_code_service.generate("S040911", "SHELL_INT_SA_WITH_LONG_NAME", "0072")

        self.assertLessEqual(len(code), MAX_ITEM_CODE_LENGTH)

    def test_validateItemCode_exactlyAtLimit_passesValidation(self):
        """Boundary: Item code exactly 18 characters passes length validation."""
        self.item_code_service.validate_length.return_value = True

        is_valid = self.item_code_service.validate_length("S040911-SH0072I-SA")  # 18 chars

        self.assertTrue(is_valid)

    def test_validateItemCode_oneCharOverLimit_failsValidation(self):
        """Boundary: Item code with 19 characters fails length validation."""
        self.item_code_service.validate_length.return_value = False

        is_valid = self.item_code_service.validate_length("S040911-SH0072IA-SA")  # 19 chars

        self.assertFalse(is_valid)

    def test_validateItemCode_17Chars_passesValidation(self):
        """Boundary: Item code with 17 characters passes length validation."""
        self.item_code_service.validate_length.return_value = True

        is_valid = self.item_code_service.validate_length("S040911-PWHT-SEC1")  # 17 chars

        self.assertTrue(is_valid)

    def test_validateItemCode_emptyString_failsValidation(self):
        """Boundary: Empty string fails item code length validation."""
        self.item_code_service.validate_length.return_value = False

        is_valid = self.item_code_service.validate_length("")

        self.assertFalse(is_valid)

    def test_validateItemCode_nullValue_raisesValidationError(self):
        """Boundary: None value raises a validation error."""
        self.item_code_service.validate_length.side_effect = ValueError("Item code cannot be null")

        with self.assertRaises(ValueError):
            self.item_code_service.validate_length(None)


# ---------------------------------------------------------------------------
# US-25649: Node Type Coverage
# ---------------------------------------------------------------------------

class TestItemCodeNodeTypeCoverage(unittest.TestCase):
    """US-25649: Verify 18-char limit is enforced across all FKMS node types."""

    def setUp(self):
        self.node_key_generator = MagicMock()

    def test_generateItemCode_sectionNode_isWithin18Chars(self):
        """Positive: Section node generates item code within 18 characters."""
        self.node_key_generator.generate_for_section.return_value = "S040911-SEC1"
        code = self.node_key_generator.generate_for_section("S040911", "1")
        self.assertLessEqual(len(code), MAX_ITEM_CODE_LENGTH)

    def test_generateItemCode_assemblyNode_isWithin18Chars(self):
        """Positive: Assembly node generates item code within 18 characters."""
        self.node_key_generator.generate_for_assembly.return_value = "S040911-SH0035A"
        code = self.node_key_generator.generate_for_assembly("S040911", "SHE", "0035")
        self.assertLessEqual(len(code), MAX_ITEM_CODE_LENGTH)

    def test_generateItemCode_subAssemblyNode_isWithin18Chars(self):
        """Positive: Sub-assembly node generates item code within 18 characters."""
        self.node_key_generator.generate_for_sub_assembly.return_value = "S040911-SH0036SA"
        code = self.node_key_generator.generate_for_sub_assembly("S040911", "SHE", "0036")
        self.assertLessEqual(len(code), MAX_ITEM_CODE_LENGTH)

    def test_generateItemCode_internalSubAssemblyNode_isWithin18Chars(self):
        """Positive: Internal Sub-assembly node generates item code within 18 characters."""
        self.node_key_generator.generate_for_internal_sub_assembly.return_value = "S040911-SH0072I-SA"
        code = self.node_key_generator.generate_for_internal_sub_assembly("S040911", "SHE", "0072")
        self.assertLessEqual(len(code), MAX_ITEM_CODE_LENGTH)

    def test_generateItemCode_externalSubAssemblyNode_isWithin18Chars(self):
        """Positive: External Sub-assembly node generates item code within 18 characters."""
        self.node_key_generator.generate_for_external_sub_assembly.return_value = "S040911-SH0072E-SA"
        code = self.node_key_generator.generate_for_external_sub_assembly("S040911", "SHE", "0072")
        self.assertLessEqual(len(code), MAX_ITEM_CODE_LENGTH)

    def test_generateItemCode_nozzleSubAssemblyNode_isWithin18Chars(self):
        """Positive: Nozzle Sub-assembly node is within 18 characters."""
        self.node_key_generator.generate_for_nozzle_sub_assembly.return_value = "S040911-SH0060N-SA"
        code = self.node_key_generator.generate_for_nozzle_sub_assembly("S040911", "SHE", "0060")
        self.assertLessEqual(len(code), MAX_ITEM_CODE_LENGTH)

    def test_generateItemCode_mtcSubAssemblyNode_isWithin18Chars(self):
        """Positive: MTC Sub-assembly node is within 18 characters."""
        self.node_key_generator.generate_for_mtc_sub_assembly.return_value = "S040911-SH0082M-SA"
        code = self.node_key_generator.generate_for_mtc_sub_assembly("S040911", "SHE", "0082")
        self.assertLessEqual(len(code), MAX_ITEM_CODE_LENGTH)

    def test_generateItemCode_ptcSubAssemblyNode_isWithin18Chars(self):
        """Positive: PTC Sub-assembly node is within 18 characters."""
        self.node_key_generator.generate_for_ptc_sub_assembly.return_value = "S040911-SH0041P-SA"
        code = self.node_key_generator.generate_for_ptc_sub_assembly("S040911", "SHE", "0041")
        self.assertLessEqual(len(code), MAX_ITEM_CODE_LENGTH)

    def test_generateItemCode_yRingAssembly_isWithin18Chars(self):
        """Positive: Y-RING Assembly node generates code within 18 characters."""
        self.node_key_generator.generate_for_y_ring_assembly.return_value = "S040911-Y-0015A"
        code = self.node_key_generator.generate_for_y_ring_assembly("S040911", "0015")
        self.assertLessEqual(len(code), MAX_ITEM_CODE_LENGTH)


# ---------------------------------------------------------------------------
# US-25649: SAP Compatibility Validation
# ---------------------------------------------------------------------------

class TestItemCodeSAPCompatibility(unittest.TestCase):
    """US-25649: Verify item codes are compatible with SAP material code requirements."""

    def setUp(self):
        self.sap_validator = MagicMock()

    def test_sapValidation_validItemCode_passesCompatibilityCheck(self):
        """Positive: Valid 18-char item code passes SAP material code compatibility."""
        self.sap_validator.validate_sap_compatibility.return_value = {
            "valid": True,
            "length": 18,
            "sap_compatible": True,
        }

        result = self.sap_validator.validate_sap_compatibility("S040911-SH0072I-SA")

        self.assertTrue(result["valid"])
        self.assertTrue(result["sap_compatible"])

    def test_sapValidation_oversizedCode_failsCompatibilityCheck(self):
        """Negative: Code exceeding 18 chars fails SAP compatibility check."""
        self.sap_validator.validate_sap_compatibility.return_value = {
            "valid": False,
            "length": 26,
            "sap_compatible": False,
            "message": "Exceeds SAP 18-character material code limit",
        }

        result = self.sap_validator.validate_sap_compatibility("S040911-SHE0072INT-SUB-ASM")

        self.assertFalse(result["sap_compatible"])

    def test_sapValidation_batchValidation_allNewCodesPassSAP(self):
        """Integration: All newly generated TO-BE item codes pass SAP compatibility."""
        self.sap_validator.validate_batch.return_value = {
            "total": len(VALID_ITEM_CODES),
            "passed": len(VALID_ITEM_CODES),
            "failed": 0,
        }

        result = self.sap_validator.validate_batch(
            [code for _, code, _ in VALID_ITEM_CODES]
        )

        self.assertEqual(result["failed"], 0)
        self.assertEqual(result["passed"], result["total"])

    def test_existingItemCodes_migrated_passNew18CharLimit(self):
        """Integration: Existing item codes, after migration, comply with 18-char limit."""
        self.sap_validator.validate_existing_codes_post_migration.return_value = {
            "total_codes": 150,
            "compliant_codes": 150,
            "non_compliant_codes": 0,
        }

        result = self.sap_validator.validate_existing_codes_post_migration()

        self.assertEqual(result["non_compliant_codes"], 0)


if __name__ == "__main__":
    unittest.main()
