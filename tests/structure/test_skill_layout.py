"""Skill layout: the shapes every skill has to have."""

from __future__ import annotations


def test_every_skill_resolves_to_a_readable_file(skills):
    for skill in skills:
        assert skill.path.is_file(), f"{skill.skill_id}: {skill.path} is not a file"
        assert skill.path.read_text(encoding="utf-8").strip(), f"{skill.skill_id}: SKILL.md is empty"


def test_skill_bodies_stay_within_the_readability_limit(skills, surface):
    assert surface.check_line_limit(skills) == []


def test_line_limit_exemptions_all_exist(repo_root, surface):
    for relative in surface.LONG_SKILL_EXEMPTIONS:
        assert (repo_root / relative).exists(), f"exemption for a file that does not exist: {relative}"


def test_bundles_live_under_their_skill_directory(skills):
    for skill in (s for s in skills if s.is_bundle):
        assert skill.path.is_relative_to(skill.path.parents[-2]), skill.skill_id
