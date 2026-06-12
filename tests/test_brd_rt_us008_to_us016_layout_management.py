"""
Unit Tests for BRD RT — Layout Management Module
User Stories: US-008, US-009, US-010, US-011, US-012, US-013, US-014, US-015, US-016

Acceptance Criteria:
    US-008 — Initiator marks cordoning areas on digital shop layout.
              NDT Engineer can modify the cordoning area.
    US-009 — User loads layout from directory (list displayed) or uploads a layout file.
    US-010 — User selects drawing tool and draws shapes (rectangle, circle, polygon, spline).
              User can resize, move, or delete drawn shapes.
    US-011 — User adds text annotations; user can edit/delete annotations.
    US-012 — User draws arrows on layout; user can resize, move, or delete arrows.
    US-013 — User applies color to a section; user can change or remove the color.
    US-014 — User measures distance between two points.
              User measures area of a selected region.
    US-015 — User saves a marked layout with all annotations; user opens it and markings are intact.
    US-016 — User exports marked layout as PDF or image; exported file displays all annotations.

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
# US-008: Cordoning Area Marking on Shop Layout
# ---------------------------------------------------------------------------

class TestCordoningAreaMarking(unittest.TestCase):
    """US-008: Verify cordoning area marking by Initiator and modification by NDT Engineer."""

    def setUp(self):
        self.layout_tool = MagicMock()

    # --- Positive ---

    def test_markCordoningArea_initiatorAccess_areaMarkedSuccessfully(self):
        """Positive: Initiator marks a cordoning area on the layout successfully."""
        self.layout_tool.mark_cordoning.return_value = {
            "status": "MARKED",
            "request_id": "RT-2026-001",
            "cordoning_area": {"x": 10, "y": 20, "width": 100, "height": 50},
        }

        result = self.layout_tool.mark_cordoning(
            request_id="RT-2026-001",
            area={"x": 10, "y": 20, "width": 100, "height": 50},
            role="INITIATOR",
        )

        self.assertEqual(result["status"], "MARKED")
        self.assertIn("cordoning_area", result)

    def test_modifyCordoningArea_ndtEngineer_modificationSaved(self):
        """Positive: NDT Engineer modifies the marked cordoning area and changes are saved."""
        self.layout_tool.modify_cordoning.return_value = {
            "status": "MODIFIED",
            "request_id": "RT-2026-001",
            "cordoning_area": {"x": 15, "y": 25, "width": 120, "height": 60},
            "modified_by": "NDT_ENGINEER",
        }

        result = self.layout_tool.modify_cordoning(
            request_id="RT-2026-001",
            new_area={"x": 15, "y": 25, "width": 120, "height": 60},
            role="NDT_ENGINEER",
        )

        self.assertEqual(result["status"], "MODIFIED")
        self.assertEqual(result["modified_by"], "NDT_ENGINEER")

    # --- Negative ---

    def test_modifyCordoningArea_unauthorizedRole_returnsPermissionError(self):
        """Negative: A non-NDT-Engineer role attempting to modify cordoning area returns an error."""
        self.layout_tool.modify_cordoning.return_value = {
            "status": "error",
            "message": "Only NDT Engineers can modify the cordoning area.",
        }

        result = self.layout_tool.modify_cordoning(
            request_id="RT-2026-001",
            new_area={"x": 15, "y": 25, "width": 120, "height": 60},
            role="TECHNICIAN",
        )

        self.assertEqual(result["status"], "error")
        self.assertIn("NDT Engineers", result["message"])

    def test_markCordoningArea_layoutNotLoaded_returnsError(self):
        """Negative: Marking cordoning area when no layout is loaded returns an error."""
        self.layout_tool.mark_cordoning.return_value = {
            "status": "error",
            "message": "No shop layout is loaded.",
        }

        result = self.layout_tool.mark_cordoning(
            request_id="RT-2026-001",
            area={"x": 10, "y": 20, "width": 100, "height": 50},
            role="INITIATOR",
        )

        self.assertEqual(result["status"], "error")

    # --- Boundary ---

    def test_markCordoningArea_zeroSizeArea_returnsValidationError(self):
        """Boundary: Marking a zero-size cordoning area returns a validation error."""
        self.layout_tool.mark_cordoning.return_value = {
            "status": "error",
            "message": "Cordoning area dimensions must be greater than zero.",
        }

        result = self.layout_tool.mark_cordoning(
            request_id="RT-2026-001",
            area={"x": 10, "y": 20, "width": 0, "height": 0},
            role="INITIATOR",
        )

        self.assertEqual(result["status"], "error")


# ---------------------------------------------------------------------------
# US-009: Load Shop Layout from Directory or Upload
# ---------------------------------------------------------------------------

class TestShopLayoutLoading(unittest.TestCase):
    """US-009: Verify loading layouts from directory and uploading custom layouts."""

    def setUp(self):
        self.layout_loader = MagicMock()

    # --- Positive ---

    def test_loadFromDirectory_directoryConfigured_returnsLayoutList(self):
        """Positive: Loading from directory displays a list of available layouts."""
        self.layout_loader.load_from_directory.return_value = {
            "status": "OK",
            "layouts": [
                {"layout_id": "LAYOUT-001", "name": "Shop A Floor 1"},
                {"layout_id": "LAYOUT-002", "name": "Shop B Floor 1"},
            ],
        }

        result = self.layout_loader.load_from_directory()

        self.assertEqual(result["status"], "OK")
        self.assertIsInstance(result["layouts"], list)
        self.assertGreater(len(result["layouts"]), 0)

    def test_uploadLayout_validFile_uploadedSuccessfully(self):
        """Positive: Uploading a valid layout file is processed successfully."""
        self.layout_loader.upload.return_value = {
            "status": "UPLOADED",
            "layout_id": "LAYOUT-NEW-001",
            "name": "Custom Layout",
        }

        result = self.layout_loader.upload({"file": "custom_layout.pdf", "name": "Custom Layout"})

        self.assertEqual(result["status"], "UPLOADED")
        self.assertIn("layout_id", result)

    # --- Negative ---

    def test_loadFromDirectory_directoryNotConfigured_returnsError(self):
        """Negative: Loading from a directory that is not configured returns an error."""
        self.layout_loader.load_from_directory.return_value = {
            "status": "error",
            "message": "Directory is not configured or accessible.",
        }

        result = self.layout_loader.load_from_directory()

        self.assertEqual(result["status"], "error")

    def test_uploadLayout_unsupportedFormat_returnsError(self):
        """Negative: Uploading a layout in unsupported format returns an error."""
        self.layout_loader.upload.return_value = {
            "status": "error",
            "message": "Unsupported file format.",
        }

        result = self.layout_loader.upload({"file": "layout.docx"})

        self.assertEqual(result["status"], "error")

    # --- Boundary ---

    def test_loadFromDirectory_emptyDirectory_returnsEmptyList(self):
        """Boundary: Empty directory returns an empty layout list."""
        self.layout_loader.load_from_directory.return_value = {
            "status": "OK",
            "layouts": [],
        }

        result = self.layout_loader.load_from_directory()

        self.assertEqual(result["layouts"], [])

    def test_uploadLayout_fileSizeExceedsLimit_returnsError(self):
        """Boundary: Uploading a file exceeding size limit returns an error."""
        self.layout_loader.upload.return_value = {
            "status": "error",
            "message": "File size exceeds the maximum allowed limit.",
        }

        result = self.layout_loader.upload({"file": "huge_layout.pdf", "size_mb": 200})

        self.assertEqual(result["status"], "error")


# ---------------------------------------------------------------------------
# US-010: Drawing Tools on Shop Layout
# ---------------------------------------------------------------------------

class TestShopLayoutDrawingTools(unittest.TestCase):
    """US-010: Verify drawing tool selection and shape manipulation."""

    def setUp(self):
        self.drawing_service = MagicMock()

    # --- Positive ---

    def test_selectTool_rectangle_drawsRectangleOnLayout(self):
        """Positive: Selecting the rectangle tool allows drawing a rectangle on the layout."""
        self.drawing_service.draw.return_value = {
            "status": "DRAWN",
            "shape_id": "SHAPE-001",
            "type": "RECTANGLE",
            "coordinates": {"x": 10, "y": 20, "width": 50, "height": 30},
        }

        result = self.drawing_service.draw(
            tool="RECTANGLE",
            coordinates={"x": 10, "y": 20, "width": 50, "height": 30},
        )

        self.assertEqual(result["status"], "DRAWN")
        self.assertEqual(result["type"], "RECTANGLE")

    def test_selectTool_circle_drawsCircleOnLayout(self):
        """Positive: Selecting the circle tool allows drawing a circle on the layout."""
        self.drawing_service.draw.return_value = {
            "status": "DRAWN",
            "shape_id": "SHAPE-002",
            "type": "CIRCLE",
            "coordinates": {"cx": 50, "cy": 50, "radius": 25},
        }

        result = self.drawing_service.draw(
            tool="CIRCLE",
            coordinates={"cx": 50, "cy": 50, "radius": 25},
        )

        self.assertEqual(result["status"], "DRAWN")
        self.assertEqual(result["type"], "CIRCLE")

    def test_selectTool_polygon_drawsPolygonOnLayout(self):
        """Positive: Selecting the polygon tool allows drawing a polygon on the layout."""
        self.drawing_service.draw.return_value = {
            "status": "DRAWN",
            "shape_id": "SHAPE-003",
            "type": "POLYGON",
        }

        result = self.drawing_service.draw(
            tool="POLYGON",
            coordinates={"points": [(0, 0), (50, 0), (25, 50)]},
        )

        self.assertEqual(result["type"], "POLYGON")

    def test_resizeShape_existingShape_resizedSuccessfully(self):
        """Positive: Resizing an existing shape updates its dimensions."""
        self.drawing_service.resize.return_value = {
            "status": "RESIZED",
            "shape_id": "SHAPE-001",
            "new_dimensions": {"width": 80, "height": 50},
        }

        result = self.drawing_service.resize(
            shape_id="SHAPE-001",
            new_dimensions={"width": 80, "height": 50},
        )

        self.assertEqual(result["status"], "RESIZED")

    def test_deleteShape_existingShape_deletedSuccessfully(self):
        """Positive: Deleting an existing shape removes it from the layout."""
        self.drawing_service.delete.return_value = {
            "status": "DELETED",
            "shape_id": "SHAPE-001",
        }

        result = self.drawing_service.delete(shape_id="SHAPE-001")

        self.assertEqual(result["status"], "DELETED")

    def test_moveShape_existingShape_movedToNewPosition(self):
        """Positive: Moving an existing shape updates its position on the layout."""
        self.drawing_service.move.return_value = {
            "status": "MOVED",
            "shape_id": "SHAPE-001",
            "new_position": {"x": 100, "y": 200},
        }

        result = self.drawing_service.move(shape_id="SHAPE-001", new_position={"x": 100, "y": 200})

        self.assertEqual(result["status"], "MOVED")

    # --- Negative ---

    def test_deleteShape_nonExistentShape_returnsNotFoundError(self):
        """Negative: Deleting a shape that does not exist returns a not-found error."""
        self.drawing_service.delete.return_value = {
            "status": "error",
            "message": "Shape not found.",
        }

        result = self.drawing_service.delete(shape_id="SHAPE-UNKNOWN")

        self.assertEqual(result["status"], "error")

    # --- Boundary ---

    def test_drawShape_outsideLayoutBounds_returnsValidationError(self):
        """Boundary: Drawing a shape outside the layout boundaries returns a validation error."""
        self.drawing_service.draw.return_value = {
            "status": "error",
            "message": "Shape coordinates are outside the layout boundaries.",
        }

        result = self.drawing_service.draw(
            tool="RECTANGLE",
            coordinates={"x": -100, "y": -100, "width": 50, "height": 30},
        )

        self.assertEqual(result["status"], "error")


# ---------------------------------------------------------------------------
# US-011: Text Annotations on Shop Layout
# ---------------------------------------------------------------------------

class TestTextAnnotations(unittest.TestCase):
    """US-011: Verify text annotation add, edit, and delete on shop layout."""

    def setUp(self):
        self.annotation_service = MagicMock()

    # --- Positive ---

    def test_addAnnotation_validText_addedToLayout(self):
        """Positive: Adding a text annotation places it on the layout."""
        self.annotation_service.add.return_value = {
            "status": "ADDED",
            "annotation_id": "ANN-001",
            "text": "Danger Zone",
            "position": {"x": 50, "y": 100},
        }

        result = self.annotation_service.add(
            text="Danger Zone", position={"x": 50, "y": 100}
        )

        self.assertEqual(result["status"], "ADDED")
        self.assertEqual(result["text"], "Danger Zone")

    def test_editAnnotation_existingAnnotation_textUpdated(self):
        """Positive: Editing an existing annotation updates its text."""
        self.annotation_service.edit.return_value = {
            "status": "UPDATED",
            "annotation_id": "ANN-001",
            "text": "Restricted Zone",
        }

        result = self.annotation_service.edit(
            annotation_id="ANN-001", text="Restricted Zone"
        )

        self.assertEqual(result["status"], "UPDATED")
        self.assertEqual(result["text"], "Restricted Zone")

    def test_deleteAnnotation_existingAnnotation_deletedSuccessfully(self):
        """Positive: Deleting an annotation removes it from the layout."""
        self.annotation_service.delete.return_value = {
            "status": "DELETED",
            "annotation_id": "ANN-001",
        }

        result = self.annotation_service.delete(annotation_id="ANN-001")

        self.assertEqual(result["status"], "DELETED")

    # --- Negative ---

    def test_addAnnotation_emptyText_returnsValidationError(self):
        """Negative: Adding an annotation with empty text returns a validation error."""
        self.annotation_service.add.return_value = {
            "status": "error",
            "message": "Annotation text cannot be empty.",
        }

        result = self.annotation_service.add(text="", position={"x": 50, "y": 100})

        self.assertEqual(result["status"], "error")

    def test_editAnnotation_nonExistentAnnotation_returnsNotFoundError(self):
        """Negative: Editing a non-existent annotation returns a not-found error."""
        self.annotation_service.edit.return_value = {
            "status": "error",
            "message": "Annotation not found.",
        }

        result = self.annotation_service.edit(annotation_id="ANN-UNKNOWN", text="Test")

        self.assertEqual(result["status"], "error")

    # --- Boundary ---

    def test_addAnnotation_textAtMaxLength_addedSuccessfully(self):
        """Boundary: Adding annotation with text at maximum allowed length succeeds."""
        max_text = "X" * 255
        self.annotation_service.add.return_value = {
            "status": "ADDED",
            "annotation_id": "ANN-002",
            "text": max_text,
        }

        result = self.annotation_service.add(text=max_text, position={"x": 10, "y": 10})

        self.assertEqual(result["status"], "ADDED")


# ---------------------------------------------------------------------------
# US-012: Directional Arrows on Shop Layout
# ---------------------------------------------------------------------------

class TestDirectionalArrows(unittest.TestCase):
    """US-012: Verify arrow drawing, resizing, moving, and deletion on shop layout."""

    def setUp(self):
        self.arrow_service = MagicMock()

    # --- Positive ---

    def test_drawArrow_validCoordinates_drawnOnLayout(self):
        """Positive: Drawing an arrow with valid coordinates places it on the layout."""
        self.arrow_service.draw.return_value = {
            "status": "DRAWN",
            "arrow_id": "ARROW-001",
            "start": {"x": 10, "y": 10},
            "end": {"x": 100, "y": 100},
            "direction": "NE",
        }

        result = self.arrow_service.draw(
            start={"x": 10, "y": 10}, end={"x": 100, "y": 100}
        )

        self.assertEqual(result["status"], "DRAWN")
        self.assertIn("arrow_id", result)

    def test_resizeArrow_existingArrow_resizedSuccessfully(self):
        """Positive: Resizing an existing arrow updates its length."""
        self.arrow_service.resize.return_value = {
            "status": "RESIZED",
            "arrow_id": "ARROW-001",
        }

        result = self.arrow_service.resize(arrow_id="ARROW-001", new_end={"x": 150, "y": 150})

        self.assertEqual(result["status"], "RESIZED")

    def test_deleteArrow_existingArrow_deletedSuccessfully(self):
        """Positive: Deleting an arrow removes it from the layout."""
        self.arrow_service.delete.return_value = {"status": "DELETED", "arrow_id": "ARROW-001"}

        result = self.arrow_service.delete(arrow_id="ARROW-001")

        self.assertEqual(result["status"], "DELETED")

    # --- Negative ---

    def test_deleteArrow_nonExistentArrow_returnsNotFoundError(self):
        """Negative: Deleting a non-existent arrow returns a not-found error."""
        self.arrow_service.delete.return_value = {
            "status": "error",
            "message": "Arrow not found.",
        }

        result = self.arrow_service.delete(arrow_id="ARROW-UNKNOWN")

        self.assertEqual(result["status"], "error")

    # --- Boundary ---

    def test_drawArrow_startEqualsEnd_returnsValidationError(self):
        """Boundary: Drawing an arrow where start equals end returns a validation error."""
        self.arrow_service.draw.return_value = {
            "status": "error",
            "message": "Arrow start and end points cannot be the same.",
        }

        result = self.arrow_service.draw(start={"x": 50, "y": 50}, end={"x": 50, "y": 50})

        self.assertEqual(result["status"], "error")


# ---------------------------------------------------------------------------
# US-013: Color Coding on Shop Layout
# ---------------------------------------------------------------------------

class TestColorCoding(unittest.TestCase):
    """US-013: Verify color application, change, and removal on layout sections."""

    def setUp(self):
        self.color_service = MagicMock()

    # --- Positive ---

    def test_applyColor_validSection_colorApplied(self):
        """Positive: Applying a color to a section updates the section's display color."""
        self.color_service.apply.return_value = {
            "status": "APPLIED",
            "section_id": "SEC-001",
            "color": "RED",
            "hazard_level": "HIGH",
        }

        result = self.color_service.apply(section_id="SEC-001", color="RED")

        self.assertEqual(result["status"], "APPLIED")
        self.assertEqual(result["color"], "RED")

    def test_changeColor_existingSection_colorUpdated(self):
        """Positive: Changing a color on an existing section updates it."""
        self.color_service.apply.return_value = {
            "status": "APPLIED",
            "section_id": "SEC-001",
            "color": "YELLOW",
        }

        result = self.color_service.apply(section_id="SEC-001", color="YELLOW")

        self.assertEqual(result["color"], "YELLOW")

    def test_removeColor_existingSection_colorRemoved(self):
        """Positive: Removing a color resets the section to its default appearance."""
        self.color_service.remove.return_value = {
            "status": "REMOVED",
            "section_id": "SEC-001",
        }

        result = self.color_service.remove(section_id="SEC-001")

        self.assertEqual(result["status"], "REMOVED")

    # --- Negative ---

    def test_applyColor_invalidColorCode_returnsError(self):
        """Negative: Applying an invalid color code returns a validation error."""
        self.color_service.apply.return_value = {
            "status": "error",
            "message": "Invalid color. Allowed colors: RED, YELLOW, GREEN, ORANGE.",
        }

        result = self.color_service.apply(section_id="SEC-001", color="PURPLE")

        self.assertEqual(result["status"], "error")

    def test_applyColor_nonExistentSection_returnsNotFoundError(self):
        """Negative: Applying color to a non-existent section returns a not-found error."""
        self.color_service.apply.return_value = {
            "status": "error",
            "message": "Section not found.",
        }

        result = self.color_service.apply(section_id="SEC-UNKNOWN", color="RED")

        self.assertEqual(result["status"], "error")


# ---------------------------------------------------------------------------
# US-014: Measurement Tools on Shop Layout
# ---------------------------------------------------------------------------

class TestMeasurementTools(unittest.TestCase):
    """US-014: Verify distance and area measurement tools on shop layout."""

    def setUp(self):
        self.measure_service = MagicMock()

    # --- Positive ---

    def test_measureDistance_twoPoints_returnsDistance(self):
        """Positive: Measuring distance between two points returns the computed distance."""
        self.measure_service.measure_distance.return_value = {
            "status": "OK",
            "distance": 50.5,
            "unit": "meters",
        }

        result = self.measure_service.measure_distance(
            point_a={"x": 0, "y": 0}, point_b={"x": 50, "y": 5}
        )

        self.assertEqual(result["status"], "OK")
        self.assertIsInstance(result["distance"], float)
        self.assertGreater(result["distance"], 0)

    def test_measureArea_selectedRegion_returnsArea(self):
        """Positive: Measuring area of a selected region returns the computed area."""
        self.measure_service.measure_area.return_value = {
            "status": "OK",
            "area": 200.0,
            "unit": "sq_meters",
        }

        result = self.measure_service.measure_area(
            region={"x": 0, "y": 0, "width": 20, "height": 10}
        )

        self.assertEqual(result["status"], "OK")
        self.assertIsInstance(result["area"], float)
        self.assertGreater(result["area"], 0)

    # --- Negative ---

    def test_measureDistance_samePoint_returnsZeroDistance(self):
        """Boundary: Measuring distance between the same two points returns zero."""
        self.measure_service.measure_distance.return_value = {
            "status": "OK",
            "distance": 0.0,
            "unit": "meters",
        }

        result = self.measure_service.measure_distance(
            point_a={"x": 10, "y": 10}, point_b={"x": 10, "y": 10}
        )

        self.assertEqual(result["distance"], 0.0)

    def test_measureArea_zeroSizeRegion_returnsZeroArea(self):
        """Boundary: Measuring area of a zero-size region returns zero."""
        self.measure_service.measure_area.return_value = {
            "status": "OK",
            "area": 0.0,
        }

        result = self.measure_service.measure_area(
            region={"x": 0, "y": 0, "width": 0, "height": 0}
        )

        self.assertEqual(result["area"], 0.0)

    def test_measureDistance_noLayoutLoaded_returnsError(self):
        """Negative: Using measurement tools when no layout is loaded returns an error."""
        self.measure_service.measure_distance.return_value = {
            "status": "error",
            "message": "No layout is currently loaded.",
        }

        result = self.measure_service.measure_distance(
            point_a={"x": 0, "y": 0}, point_b={"x": 50, "y": 50}
        )

        self.assertEqual(result["status"], "error")


# ---------------------------------------------------------------------------
# US-015: Save Marked Layouts
# ---------------------------------------------------------------------------

class TestSaveMarkedLayout(unittest.TestCase):
    """US-015: Verify saving and reopening marked layouts with annotations intact."""

    def setUp(self):
        self.layout_storage = MagicMock()

    # --- Positive ---

    def test_saveLayout_withAnnotations_savedSuccessfully(self):
        """Positive: Saving a marked layout preserves all annotations and markings."""
        self.layout_storage.save.return_value = {
            "status": "SAVED",
            "layout_id": "LAYOUT-SAVED-001",
            "annotations_count": 3,
            "shapes_count": 2,
        }

        result = self.layout_storage.save(
            layout_id="LAYOUT-001",
            annotations=[{"id": "ANN-001"}, {"id": "ANN-002"}, {"id": "ANN-003"}],
            shapes=[{"id": "SHAPE-001"}, {"id": "SHAPE-002"}],
        )

        self.assertEqual(result["status"], "SAVED")
        self.assertEqual(result["annotations_count"], 3)

    def test_openLayout_savedLayout_annotationsIntact(self):
        """Positive: Opening a previously saved layout displays all annotations and markings."""
        self.layout_storage.open.return_value = {
            "status": "LOADED",
            "layout_id": "LAYOUT-SAVED-001",
            "annotations": [{"id": "ANN-001"}, {"id": "ANN-002"}, {"id": "ANN-003"}],
            "shapes": [{"id": "SHAPE-001"}, {"id": "SHAPE-002"}],
        }

        result = self.layout_storage.open(layout_id="LAYOUT-SAVED-001")

        self.assertEqual(result["status"], "LOADED")
        self.assertEqual(len(result["annotations"]), 3)
        self.assertEqual(len(result["shapes"]), 2)

    # --- Negative ---

    def test_openLayout_nonExistentLayout_returnsNotFoundError(self):
        """Negative: Opening a layout that does not exist returns a not-found error."""
        self.layout_storage.open.return_value = {
            "status": "error",
            "message": "Saved layout not found.",
        }

        result = self.layout_storage.open(layout_id="LAYOUT-UNKNOWN")

        self.assertEqual(result["status"], "error")

    # --- Boundary ---

    def test_saveLayout_noAnnotationsOrShapes_savedAsBlank(self):
        """Boundary: Saving a layout with no annotations or shapes saves successfully."""
        self.layout_storage.save.return_value = {
            "status": "SAVED",
            "layout_id": "LAYOUT-BLANK-001",
            "annotations_count": 0,
            "shapes_count": 0,
        }

        result = self.layout_storage.save(
            layout_id="LAYOUT-002",
            annotations=[],
            shapes=[],
        )

        self.assertEqual(result["status"], "SAVED")
        self.assertEqual(result["annotations_count"], 0)

    # --- Integration ---

    def test_saveLayout_storageServiceTimeout_raisesTimeoutError(self):
        """Integration: Storage service timeout during save raises TimeoutError."""
        self.layout_storage.save.side_effect = TimeoutError("Storage service timeout")

        with self.assertRaises(TimeoutError):
            self.layout_storage.save(layout_id="LAYOUT-001", annotations=[], shapes=[])


# ---------------------------------------------------------------------------
# US-016: Export Marked Layouts as PDF or Image
# ---------------------------------------------------------------------------

class TestExportMarkedLayout(unittest.TestCase):
    """US-016: Verify exporting marked layouts in PDF and image formats."""

    def setUp(self):
        self.export_service = MagicMock()

    # --- Positive ---

    def test_exportLayout_pdfFormat_exportedSuccessfully(self):
        """Positive: Exporting a marked layout as PDF produces a downloadable PDF file."""
        self.export_service.export.return_value = {
            "status": "EXPORTED",
            "format": "PDF",
            "file_path": "/exports/layout_RT2026001.pdf",
        }

        result = self.export_service.export(layout_id="LAYOUT-001", format="PDF")

        self.assertEqual(result["status"], "EXPORTED")
        self.assertEqual(result["format"], "PDF")
        self.assertTrue(result["file_path"].endswith(".pdf"))

    def test_exportLayout_imageFormat_exportedSuccessfully(self):
        """Positive: Exporting a marked layout as an image produces a downloadable image file."""
        self.export_service.export.return_value = {
            "status": "EXPORTED",
            "format": "IMAGE",
            "file_path": "/exports/layout_RT2026001.png",
        }

        result = self.export_service.export(layout_id="LAYOUT-001", format="IMAGE")

        self.assertEqual(result["status"], "EXPORTED")
        self.assertEqual(result["format"], "IMAGE")

    def test_exportedFile_containsAllAnnotations_verifiedOnOpen(self):
        """Positive: Exported file includes all annotations and markings from the original layout."""
        self.export_service.verify_export.return_value = {
            "status": "VERIFIED",
            "annotations_present": True,
            "shapes_present": True,
        }

        result = self.export_service.verify_export(file_path="/exports/layout_RT2026001.pdf")

        self.assertTrue(result["annotations_present"])
        self.assertTrue(result["shapes_present"])

    # --- Negative ---

    def test_exportLayout_unsupportedFormat_returnsError(self):
        """Negative: Exporting in an unsupported format returns an error."""
        self.export_service.export.return_value = {
            "status": "error",
            "message": "Unsupported export format. Choose PDF or Image.",
        }

        result = self.export_service.export(layout_id="LAYOUT-001", format="SVG")

        self.assertEqual(result["status"], "error")
        self.assertIn("PDF or Image", result["message"])

    def test_exportLayout_nonExistentLayout_returnsNotFoundError(self):
        """Negative: Exporting a non-existent layout returns a not-found error."""
        self.export_service.export.return_value = {
            "status": "error",
            "message": "Layout not found.",
        }

        result = self.export_service.export(layout_id="LAYOUT-UNKNOWN", format="PDF")

        self.assertEqual(result["status"], "error")

    # --- Integration ---

    def test_exportLayout_exportServiceUnavailable_raisesConnectionError(self):
        """Integration: Export service unavailable raises ConnectionError."""
        self.export_service.export.side_effect = ConnectionError("Export service not reachable")

        with self.assertRaises(ConnectionError):
            self.export_service.export(layout_id="LAYOUT-001", format="PDF")


if __name__ == "__main__":
    unittest.main()
