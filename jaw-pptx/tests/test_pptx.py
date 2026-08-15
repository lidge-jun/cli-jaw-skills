"""PPTX skill tests — officecli create/add/view/validate cycle + fixture regression."""

from __future__ import annotations

from pathlib import Path

import pytest

from conftest import run_officecli, run_officecli_json

FIXTURES = Path(__file__).resolve().parent / "fixtures"


# ---------------------------------------------------------------------------
# Create → Add slide → Add shape → View → Validate cycle
# ---------------------------------------------------------------------------

@pytest.mark.officecli
class TestPptxCycle:
    def test_create_add_view_validate(self, tmp_pptx: Path) -> None:
        """Full lifecycle: create → add slide → add shape → view → validate."""
        # Add slide
        result = run_officecli_json("add", str(tmp_pptx), "/",
                                   "--type", "slide")
        assert result["success"] is True

        # Add textbox shape
        result = run_officecli_json("add", str(tmp_pptx), "/slide[1]",
                                   "--type", "shape",
                                   "--prop", "type=textbox",
                                   "--prop", "text=Hello pytest")
        assert result["success"] is True

        # View text
        view = run_officecli("view", str(tmp_pptx), "text")
        assert "Hello pytest" in view.stdout

        # Validate
        val = run_officecli_json("validate", str(tmp_pptx))
        assert val["success"] is True
        assert val["data"]["count"] == 0

    def test_multiple_shapes(self, tmp_pptx: Path) -> None:
        """Add multiple shapes to a slide."""
        run_officecli("add", str(tmp_pptx), "/", "--type", "slide")
        for text in ["Shape A", "Shape B", "Shape C"]:
            run_officecli("add", str(tmp_pptx), "/slide[1]",
                          "--type", "shape",
                          "--prop", "type=textbox",
                          "--prop", f"text={text}")

        view = run_officecli("view", str(tmp_pptx), "text")
        for text in ["Shape A", "Shape B", "Shape C"]:
            assert text in view.stdout

        val = run_officecli_json("validate", str(tmp_pptx))
        assert val["success"] is True
        assert val["data"]["count"] == 0

    def test_multiple_slides(self, tmp_pptx: Path) -> None:
        """Add multiple slides, each with content."""
        for i in range(1, 4):
            run_officecli("add", str(tmp_pptx), "/", "--type", "slide")
            run_officecli("add", str(tmp_pptx), f"/slide[{i}]",
                          "--type", "shape",
                          "--prop", "type=textbox",
                          "--prop", f"text=Slide {i}")

        view = run_officecli("view", str(tmp_pptx), "text")
        for i in range(1, 4):
            assert f"Slide {i}" in view.stdout

        val = run_officecli_json("validate", str(tmp_pptx))
        assert val["success"] is True
        assert val["data"]["count"] == 0


# ---------------------------------------------------------------------------
# CJK on slides
# ---------------------------------------------------------------------------

@pytest.mark.cjk
@pytest.mark.officecli
class TestPptxCJK:
    def test_korean_slide_title(self, tmp_pptx: Path) -> None:
        """Create slide with Korean text in shape → verify in output."""
        text = "프레젠테이션 제목"
        run_officecli("add", str(tmp_pptx), "/", "--type", "slide")
        run_officecli("add", str(tmp_pptx), "/slide[1]",
                      "--type", "shape",
                      "--prop", "type=textbox",
                      "--prop", f"text={text}")

        view = run_officecli("view", str(tmp_pptx), "text")
        assert text in view.stdout

        val = run_officecli_json("validate", str(tmp_pptx))
        assert val["success"] is True
        assert val["data"]["count"] == 0


# ---------------------------------------------------------------------------
# Fixture regression
# ---------------------------------------------------------------------------

@pytest.mark.regression
@pytest.mark.officecli
class TestPptxFixtureValidation:
    """Validate existing pptx fixtures."""

    OPENABLE_FIXTURES = [
        "basic_slides.pptx",
        "blank_layout_named_nonstandard.pptx",
        "blankless_minimal_deck.pptx",
        "duplicate_media_chart_deck.pptx",
        "orphan_media.pptx",
    ]

    @pytest.mark.parametrize("filename", OPENABLE_FIXTURES)
    def test_openable_fixture(self, filename: str) -> None:
        """These fixtures should open and validate (possibly with known issues)."""
        fixture = FIXTURES / filename
        if not fixture.exists():
            pytest.skip(f"Fixture {filename} not found")
        val = run_officecli_json("validate", str(fixture), check=False)
        assert val["success"] is True

    BROKEN_FIXTURES = [
        "broken_layout.pptx",
        "notes_reuse_conflict.pptx",
    ]

    @pytest.mark.parametrize("filename", BROKEN_FIXTURES)
    def test_broken_fixture(self, filename: str) -> None:
        """These fixtures are intentionally broken and should fail validation."""
        fixture = FIXTURES / filename
        if not fixture.exists():
            pytest.skip(f"Fixture {filename} not found")
        val = run_officecli_json("validate", str(fixture), check=False)
        assert val["success"] is False
