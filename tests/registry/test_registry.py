"""registry.json and the tree have to agree about what exists."""

from __future__ import annotations


def test_registry_is_internally_valid(skills, surface):
    assert surface.check_registry(skills) == []


def test_every_registry_entry_resolves(registry, repo_root):
    missing = [
        skill_id
        for skill_id, meta in registry.items()
        if not (repo_root / meta.get("entry", f"{skill_id}/SKILL.md")).exists()
    ]
    assert missing == [], f"registry entries with no SKILL.md: {missing}"


def test_bundle_entries_are_found_by_discovery(skills):
    """The six plugin bundles were invisible to a */SKILL.md glob, which is what made
    them look like orphaned registry entries."""
    found = {s.skill_id for s in skills}
    for bundle in ("static-analysis", "terraform", "differential-review",
                   "insecure-defaults", "modern-python", "property-based-testing"):
        assert bundle in found, f"{bundle} was not discovered"


def test_unregistered_directories_are_the_declared_vendored_ones(skills, surface):
    unregistered = {s.skill_id for s in skills if not s.registered}
    assert unregistered == surface.VENDORED_UNREGISTERED
