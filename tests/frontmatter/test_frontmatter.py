"""Frontmatter: parseable, complete, and agreeing with the skill id."""

from __future__ import annotations


def test_every_skill_has_parseable_frontmatter(skills, surface):
    assert surface.check_frontmatter(skills) == []


def test_names_agree_with_ids_and_are_unique(skills, surface):
    assert surface.check_names(skills) == []


def test_parser_consumes_folded_block_scalars(surface):
    text = '---\nname: x\ndescription: >-\n  first line\n  second line\n---\nbody\n'
    parsed = surface.parse_frontmatter(text)
    assert parsed["description"] == "first line second line"


def test_parser_rejects_a_missing_block(surface):
    assert surface.parse_frontmatter("no frontmatter here\n") is None


def test_parser_skips_nested_blocks_without_misreading_them(surface):
    text = '---\nname: x\ndescription: y\nmetadata:\n  version: "1.0"\n---\n'
    parsed = surface.parse_frontmatter(text)
    assert parsed["name"] == "x" and "version" not in parsed
