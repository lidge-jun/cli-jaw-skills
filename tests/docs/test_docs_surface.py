"""The published documentation surface: assets and metadata, not numbers."""

from __future__ import annotations


def test_docs_assets_and_metadata_exist(surface):
    assert surface.check_docs_assets() == []


def test_measured_inventory_is_reported(skills, surface):
    counts = surface.measure(skills)
    assert counts["skills"] > 0
    assert set(counts) == {"skills", "reference_folders", "script_folders", "template_folders"}
