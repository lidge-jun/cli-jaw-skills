"""DOCX skill tests — officecli create/add/view/validate cycle + fixture regression."""

from __future__ import annotations

from pathlib import Path

import pytest

from conftest import run_officecli, run_officecli_json

FIXTURES = Path(__file__).resolve().parent / "fixtures"


# ---------------------------------------------------------------------------
# Create → Add → View → Validate cycle
# ---------------------------------------------------------------------------

@pytest.mark.officecli
class TestDocxCycle:
    def test_create_add_view_validate(self, tmp_docx: Path) -> None:
        """Full lifecycle: create blank → add paragraph → view text → validate."""
        # Add paragraph
        result = run_officecli_json("add", str(tmp_docx), "/body",
                                   "--type", "paragraph",
                                   "--prop", "text=Hello pytest")
        assert result["success"] is True

        # View text
        view = run_officecli("view", str(tmp_docx), "text")
        assert "Hello pytest" in view.stdout

        # Validate
        val = run_officecli_json("validate", str(tmp_docx))
        assert val["success"] is True
        assert val["data"]["count"] == 0

    def test_multi_paragraph(self, tmp_docx: Path) -> None:
        """Add multiple paragraphs and verify ordering."""
        for i, text in enumerate(["First", "Second", "Third"], 1):
            run_officecli("add", str(tmp_docx), "/body",
                          "--type", "paragraph", "--prop", f"text={text}")

        view = run_officecli("view", str(tmp_docx), "text")
        output = view.stdout
        for text in ["First", "Second", "Third"]:
            assert text in output
        # Verify ordering
        assert output.index("First") < output.index("Second") < output.index("Third")

        val = run_officecli_json("validate", str(tmp_docx))
        assert val["success"] is True
        assert val["data"]["count"] == 0

    def test_add_bold_run(self, tmp_docx: Path) -> None:
        """Add paragraph then a bold run inside it."""
        run_officecli("add", str(tmp_docx), "/body",
                      "--type", "paragraph", "--prop", "text=Normal text")
        run_officecli("add", str(tmp_docx), "/body/p[1]",
                      "--type", "run", "--prop", "text= Bold text",
                      "--prop", "bold=true")

        view = run_officecli("view", str(tmp_docx), "text")
        assert "Bold text" in view.stdout

        val = run_officecli_json("validate", str(tmp_docx))
        assert val["success"] is True
        assert val["data"]["count"] == 0


# ---------------------------------------------------------------------------
# CJK roundtrip
# ---------------------------------------------------------------------------

@pytest.mark.cjk
@pytest.mark.officecli
class TestDocxCJK:
    def test_korean_roundtrip(self, tmp_docx: Path) -> None:
        """Create → add Korean text → view → assert Korean preserved."""
        text = "대한민국 만세"
        run_officecli("add", str(tmp_docx), "/body",
                      "--type", "paragraph", "--prop", f"text={text}")

        view = run_officecli("view", str(tmp_docx), "text")
        assert text in view.stdout

        val = run_officecli_json("validate", str(tmp_docx))
        assert val["success"] is True
        assert val["data"]["count"] == 0

    def test_korean_raw_xml(self, tmp_docx: Path) -> None:
        """Korean text should appear in raw XML output."""
        text = "안녕하세요 세계"
        run_officecli("add", str(tmp_docx), "/body",
                      "--type", "paragraph", "--prop", f"text={text}")

        val = run_officecli_json("validate", str(tmp_docx))
        assert val["success"] is True
        assert val["data"]["count"] == 0

        raw = run_officecli("raw", str(tmp_docx))
        assert "안녕하세요" in raw.stdout


# ---------------------------------------------------------------------------
# Fixture regression — validate known-good files
# ---------------------------------------------------------------------------

@pytest.mark.regression
@pytest.mark.officecli
class TestDocxFixtureValidation:
    """Validate existing fixture files against officecli validate."""

    VALID_FIXTURES = [
        "comments.docx",
        "comment_field_code_boundary.docx",
        "comment_hyperlink_boundary.docx",
        "comment_mid_run_exact.docx",
        "comment_multi_t_single_run.docx",
        "headings_report.docx",
        "tracked_changes.docx",
        "tracked_changes_header_footer.docx",
    ]

    @pytest.mark.parametrize("filename", VALID_FIXTURES)
    def test_valid_fixture(self, filename: str) -> None:
        fixture = FIXTURES / filename
        if not fixture.exists():
            pytest.skip(f"Fixture {filename} not found")
        val = run_officecli_json("validate", str(fixture))
        assert val["success"] is True
        assert val["data"]["count"] == 0, f"Unexpected errors: {val['data']['errors']}"

    def test_broken_rels_fails_validation(self) -> None:
        """broken_rels.docx should fail validation (missing parts)."""
        fixture = FIXTURES / "broken_rels.docx"
        if not fixture.exists():
            pytest.skip("Fixture broken_rels.docx not found")
        val = run_officecli_json("validate", str(fixture), check=False)
        assert val["success"] is False
