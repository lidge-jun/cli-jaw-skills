"""XLSX skill tests — officecli create/set/view/validate cycle + fixture regression."""

from __future__ import annotations

from pathlib import Path

import pytest

from conftest import run_officecli, run_officecli_json

FIXTURES = Path(__file__).resolve().parent / "fixtures"


# ---------------------------------------------------------------------------
# Create → Set → View → Validate cycle
# ---------------------------------------------------------------------------

@pytest.mark.officecli
class TestXlsxCycle:
    def test_create_set_view_validate(self, tmp_xlsx: Path) -> None:
        """Full lifecycle: create → set cell → view → validate."""
        result = run_officecli_json("set", str(tmp_xlsx), "/Sheet1/A1",
                                   "--prop", "value=Hello pytest")
        assert result["success"] is True

        view = run_officecli("view", str(tmp_xlsx), "text")
        assert "Hello pytest" in view.stdout

        val = run_officecli_json("validate", str(tmp_xlsx))
        assert val["success"] is True
        assert val["data"]["count"] == 0

    def test_multiple_cells(self, tmp_xlsx: Path) -> None:
        """Set multiple cells and verify."""
        run_officecli("set", str(tmp_xlsx), "/Sheet1/A1", "--prop", "value=Name")
        run_officecli("set", str(tmp_xlsx), "/Sheet1/B1", "--prop", "value=Age")
        run_officecli("set", str(tmp_xlsx), "/Sheet1/A2", "--prop", "value=Alice")
        run_officecli("set", str(tmp_xlsx), "/Sheet1/B2", "--prop", "value=30")

        view = run_officecli("view", str(tmp_xlsx), "text")
        for text in ["Name", "Age", "Alice", "30"]:
            assert text in view.stdout

        val = run_officecli_json("validate", str(tmp_xlsx))
        assert val["success"] is True
        assert val["data"]["count"] == 0

    def test_numeric_cell(self, tmp_xlsx: Path) -> None:
        """Numeric values should round-trip."""
        run_officecli("set", str(tmp_xlsx), "/Sheet1/A1", "--prop", "value=42.5")
        view = run_officecli("view", str(tmp_xlsx), "text")
        assert "42.5" in view.stdout

        val = run_officecli_json("validate", str(tmp_xlsx))
        assert val["success"] is True
        assert val["data"]["count"] == 0

    def test_validate_after_edits(self, tmp_xlsx: Path) -> None:
        """Document should remain valid after multiple edits."""
        for i in range(1, 6):
            run_officecli("set", str(tmp_xlsx), f"/Sheet1/A{i}",
                          "--prop", f"value=Row {i}")
        val = run_officecli_json("validate", str(tmp_xlsx))
        assert val["success"] is True
        assert val["data"]["count"] == 0


# ---------------------------------------------------------------------------
# Cell formatting roundtrip
# ---------------------------------------------------------------------------

@pytest.mark.officecli
class TestXlsxFormatting:
    def test_bold_cell(self, tmp_xlsx: Path) -> None:
        """Set bold formatting on a cell."""
        run_officecli("set", str(tmp_xlsx), "/Sheet1/A1",
                      "--prop", "value=Bold", "--prop", "bold=true")

        view = run_officecli("view", str(tmp_xlsx), "text")
        assert "Bold" in view.stdout

        val = run_officecli_json("validate", str(tmp_xlsx))
        assert val["success"] is True
        assert val["data"]["count"] == 0


# ---------------------------------------------------------------------------
# Fixture regression
# ---------------------------------------------------------------------------

@pytest.mark.regression
@pytest.mark.officecli
class TestXlsxFixtureValidation:
    """Validate existing fixture files — expect schema-level issues for some."""

    OPENABLE_FIXTURES = [
        ("formula_errors.xlsx", None),
        ("formula_uncached.xlsx", None),
        ("korean_identifier_stress.xlsx", None),
        ("multi_sheet.xlsx", None),
        ("wide_columns_ad.xlsx", None),
    ]

    @pytest.mark.parametrize("filename,_", OPENABLE_FIXTURES, ids=[f[0] for f in OPENABLE_FIXTURES])
    def test_openable_fixture(self, filename: str, _: object) -> None:
        """These fixtures should open and validate (possibly with minor schema issues)."""
        fixture = FIXTURES / filename
        if not fixture.exists():
            pytest.skip(f"Fixture {filename} not found")
        val = run_officecli_json("validate", str(fixture), check=False)
        assert val["success"] is True

    def test_broken_refs_fails(self) -> None:
        """broken_refs.xlsx should fail validation."""
        fixture = FIXTURES / "broken_refs.xlsx"
        if not fixture.exists():
            pytest.skip("Fixture not found")
        val = run_officecli_json("validate", str(fixture), check=False)
        assert val["success"] is False
