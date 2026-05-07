import tempfile
import textwrap
import unittest
from pathlib import Path

from scripts.export_tests_to_text import (
    parse_test_file,
    group_by_user_story,
    render_text,
    _extract_user_stories,
    _extract_test_type,
)


SAMPLE_TEST_FILE = textwrap.dedent('''\
    """
    Unit Tests for Sample Module
    User Stories: US-100, US-101
    """
    import unittest
    from unittest.mock import MagicMock


    class TestSampleFeature(unittest.TestCase):
        """US-100: Verify sample feature."""

        def setUp(self):
            self.service = MagicMock()

        def test_sample_validInput_returnsSuccess(self):
            """Positive: Valid input returns success."""
            pass

        def test_sample_invalidInput_returnsError(self):
            """Negative: Invalid input returns error."""
            pass

        def test_sample_emptyInput_returnsValidationError(self):
            """Boundary: Empty input returns validation error."""
            pass


    class TestAnotherFeature(unittest.TestCase):
        """US-101: Verify another feature."""

        def test_another_serviceDown_raisesTimeout(self):
            """Integration: Service timeout raises error."""
            pass
''')


class TestExtractUserStories(unittest.TestCase):
    def test_extractUserStories_multipleIDs_returnsSortedUnique(self):
        text = "US-001 / US-004 / US-007 / US-001"
        result = _extract_user_stories(text)
        self.assertEqual(result, ["US-001", "US-004", "US-007"])

    def test_extractUserStories_noIDs_returnsEmptyList(self):
        result = _extract_user_stories("no story references here")
        self.assertEqual(result, [])


class TestExtractTestType(unittest.TestCase):
    def test_extractTestType_positive_returnsPositive(self):
        self.assertEqual(_extract_test_type("Positive: it works"), "Positive")

    def test_extractTestType_negative_returnsNegative(self):
        self.assertEqual(_extract_test_type("Negative: it fails"), "Negative")

    def test_extractTestType_boundary_returnsBoundary(self):
        self.assertEqual(_extract_test_type("Boundary: edge case"), "Boundary")

    def test_extractTestType_integration_returnsIntegration(self):
        self.assertEqual(_extract_test_type("Integration: service call"), "Integration")

    def test_extractTestType_noPrefix_returnsGeneral(self):
        self.assertEqual(_extract_test_type("just a description"), "General")


class TestParseTestFile(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.test_file = Path(self.tmpdir) / "test_sample.py"
        self.test_file.write_text(SAMPLE_TEST_FILE, encoding="utf-8")

    def test_parseTestFile_sampleFile_extractsAllClasses(self):
        classes = parse_test_file(self.test_file)
        self.assertEqual(len(classes), 2)

    def test_parseTestFile_sampleFile_extractsCorrectTestCount(self):
        classes = parse_test_file(self.test_file)
        total_tests = sum(len(c["tests"]) for c in classes)
        self.assertEqual(total_tests, 4)

    def test_parseTestFile_sampleFile_extractsUserStories(self):
        classes = parse_test_file(self.test_file)
        self.assertEqual(classes[0]["user_stories"], ["US-100"])
        self.assertEqual(classes[1]["user_stories"], ["US-101"])

    def test_parseTestFile_sampleFile_extractsTestTypes(self):
        classes = parse_test_file(self.test_file)
        types = [t["test_type"] for t in classes[0]["tests"]]
        self.assertIn("Positive", types)
        self.assertIn("Negative", types)
        self.assertIn("Boundary", types)


class TestGroupByUserStory(unittest.TestCase):
    def test_groupByUserStory_twoStories_groupsCorrectly(self):
        classes = [
            {"class_name": "A", "user_stories": ["US-100"], "tests": [{"m": 1}]},
            {"class_name": "B", "user_stories": ["US-100", "US-101"], "tests": [{"m": 2}]},
        ]
        grouped = group_by_user_story(classes)
        self.assertIn("US-100", grouped)
        self.assertIn("US-101", grouped)
        self.assertEqual(len(grouped["US-100"]), 2)
        self.assertEqual(len(grouped["US-101"]), 1)


class TestRenderText(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.test_file = Path(self.tmpdir) / "test_sample.py"
        self.test_file.write_text(SAMPLE_TEST_FILE, encoding="utf-8")

    def test_renderText_sampleFile_containsUserStoryHeaders(self):
        classes = parse_test_file(self.test_file)
        grouped = group_by_user_story(classes)
        text = render_text(grouped)

        self.assertIn("USER STORY: US-100", text)
        self.assertIn("USER STORY: US-101", text)

    def test_renderText_sampleFile_containsTestMethodNames(self):
        classes = parse_test_file(self.test_file)
        grouped = group_by_user_story(classes)
        text = render_text(grouped)

        self.assertIn("test_sample_validInput_returnsSuccess", text)
        self.assertIn("test_another_serviceDown_raisesTimeout", text)

    def test_renderText_sampleFile_containsSummary(self):
        classes = parse_test_file(self.test_file)
        grouped = group_by_user_story(classes)
        text = render_text(grouped)

        self.assertIn("SUMMARY", text)
        self.assertIn("TOTAL TEST CASES:", text)


if __name__ == "__main__":
    unittest.main()
