"""jaw-diagram's visual story contract, and the rules it must not have eaten.

Two jobs. The first is that the contract exists where the skill says it does: an agent that reads
SKILL.md and never opens a reference still meets the decisions that change what it draws.

The second is preservation, and it is the reason the assertions below name rule text rather than
topic words. Asserting that SKILL.md still contains "DOMPurify" proves nothing: the word survives
deleting the element list it introduces. So each check names something that disappears exactly when
its rule does.

What this file cannot do is decide whether a real diagram has a point. No test can. Thesis quality,
invented-versus-observed data, CJK tofu, label collision and sanitizer behaviour stay with human
review and with public/js/diagram/ in the consuming repository.
"""

from __future__ import annotations

from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
DIAGRAM = ROOT / "jaw-diagram"
SKILL = DIAGRAM / "SKILL.md"
STORY = DIAGRAM / "reference" / "visual-story.md"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


# Every decision ID, mapped to each file that must carry it. Two are deliberately dual-homed
# because they govern both the must-read body and the recipes; the rest have one home. A home
# listed here is a home the diff actually writes.
DECISION_HOMES = {
    "DIAGRAM-CLAIM-01": [SKILL],
    "DIAGRAM-SCOPE-01": [SKILL],
    "DIAGRAM-EVIDENCE-01": [STORY],
    "DIAGRAM-SEQ-01": [SKILL, STORY],
    "DIAGRAM-HANDOFF-01": [SKILL, STORY],
    "DIAGRAM-SLOP-01": [STORY],
    "DIAGRAM-RENDER-01": [SKILL],
    "DIAGRAM-A11Y-01": [SKILL],
    "DIAGRAM-FRESH-01": [STORY],
}


def test_visual_story_reference_exists() -> None:
    assert STORY.is_file(), "reference/visual-story.md is missing"
    assert read(STORY).strip(), "reference/visual-story.md is empty"


def test_skill_routes_the_visual_story_reference() -> None:
    skill = read(SKILL)
    assert '"visual-story.md' in skill, "frontmatter references do not list visual-story.md"
    assert "reference/visual-story.md" in skill, "the body never links reference/visual-story.md"


@pytest.mark.parametrize("decision,homes", sorted(DECISION_HOMES.items()))
def test_each_decision_is_stated_in_every_home(decision, homes) -> None:
    for home in homes:
        assert decision in read(home), f"{decision} missing from {home.relative_to(ROOT)}"


def test_must_read_decisions_are_reachable_without_the_reference() -> None:
    """An agent that reads only SKILL.md still has to name a claim, justify drawing at all,
    sequence overview before detail, hand off to prose, and look at what rendered."""
    skill = read(SKILL)
    for decision in ("DIAGRAM-CLAIM-01", "DIAGRAM-SCOPE-01", "DIAGRAM-SEQ-01",
                     "DIAGRAM-HANDOFF-01", "DIAGRAM-RENDER-01", "DIAGRAM-A11Y-01"):
        assert decision in skill, f"{decision} is not reachable from SKILL.md alone"


def test_the_accessible_name_example_carries_a_takeaway() -> None:
    """The old template shipped a title of "Diagram Title", so a meaningless accessible name
    looked compliant."""
    skill = read(SKILL)
    assert ">Diagram Title<" not in skill
    assert "states the takeaway" in skill


def test_count_triggers_do_not_by_themselves_order_a_diagram() -> None:
    after = read(SKILL).split("Proactive generation", 1)[1][:1400]
    assert "DIAGRAM-SCOPE-01" in after


def test_anti_slop_catalogue_names_its_cases() -> None:
    story = read(STORY)
    for case in ("card", "Cycling colour", "no claim", "Restating"):
        assert case in story, f"the anti-slop catalogue never names: {case}"


def test_evidence_classes_are_enumerated_and_invention_is_refused() -> None:
    story = read(STORY)
    for klass in ("Observed", "User-supplied", "Assumed", "Illustrative"):
        assert klass in story
    assert "Never invent" in story


# ---------------------------------------------------------------------------
# Preservation. Each string is the rule, not a word near the rule.
# ---------------------------------------------------------------------------

SECURITY_RULES = [
    "`@import` rules \u2192 stripped",
    "`@font-face` blocks \u2192 stripped",
    "External `url()` \u2192 replaced with `none`",
    "`<foreignObject>`",
    "`<animate>`, `<set>`, `<animateTransform>`, `<animateMotion>`",
    "Nested `<svg>`",
    "`xlink:href`",
    "All `on*` event handlers",
    "apply only to inline SVG rendered in the main document",
]

THEME_RULES = [
    "window.__jawTokens",
    "--text-dim",
    "--surface",
    "matchMedia('prefers-color-scheme')",
]

CJK_RULES = [
    "fontFamily",
    "Noto Sans KR",
    "inherits `font-family` from the jaw host",
]


@pytest.mark.parametrize("rule", SECURITY_RULES)
def test_inline_svg_security_rules_survive(rule) -> None:
    assert rule in read(SKILL), f"a sanitizer rule vanished from SKILL.md: {rule}"


@pytest.mark.parametrize("rule", THEME_RULES)
def test_theme_rules_survive(rule) -> None:
    assert rule in read(SKILL), f"a theme rule vanished from SKILL.md: {rule}"


@pytest.mark.parametrize("rule", CJK_RULES)
def test_cjk_and_font_rules_survive(rule) -> None:
    assert rule in read(SKILL), f"a CJK or font rule vanished from SKILL.md: {rule}"


@pytest.mark.parametrize("fence", ["diagram-file", "diagram-html", "chart-json", "structured-renderers"])
def test_renderer_routing_rows_survive(fence) -> None:
    """Matched inside table rows, so deleting a routing row cannot be masked by the same word
    surviving somewhere in prose."""
    rows = [line for line in read(SKILL).splitlines()
            if line.startswith("|") and line.count("|") >= 3 and fence in line]
    assert rows, f"no routing table row still routes {fence}"


def test_skill_body_stays_within_the_shared_line_limit(surface) -> None:
    """Read from the validator rather than hardcoded, so the two cannot drift."""
    assert len(read(SKILL).splitlines()) <= surface.LINE_LIMIT


# ---------------------------------------------------------------------------
# Operative content. The review that landed this file called ID-presence checks cosmetic:
# gut the instruction, keep the ID string, and they pass. These name what each decision
# actually tells an agent to do, so deleting the instruction fails even if the ID survives.
# ---------------------------------------------------------------------------


def test_evidence_rule_is_in_the_body_not_only_the_recipe() -> None:
    """Inventing data is a correctness rule, so it cannot live only in a reference an agent
    may never open."""
    skill = read(SKILL)
    assert "Never invent data" in skill
    assert "observed, user-supplied, assumed, or illustrative" in skill
    assert "does not start at zero" in skill


def test_evidence_classes_have_an_appearance_rule_each() -> None:
    """The four classes are useless without saying how each one shows up in the figure."""
    story = read(STORY)
    rows = [l for l in story.splitlines() if l.startswith("|") and l.count("|") >= 4]
    for klass in ("Observed", "User-supplied", "Assumed", "Illustrative"):
        assert any(klass in r for r in rows), f"{klass} has no row stating how it appears"
    assert "unit" in story and "source" in story


def test_a_missing_claim_means_no_diagram() -> None:
    """CLAIM-01 is only operative if it says what to do when there is no claim."""
    skill = read(SKILL)
    assert "skip the diagram" in skill


def test_accessible_names_cover_canvas_and_widgets_too() -> None:
    """The SVG sample was fixed first; the canvas sample kept a subject-only label."""
    skill = read(SKILL)
    assert 'aria-label="Chart description"' not in skill
    assert "canvas or widget `aria-label`" in skill


def test_colour_is_not_the_only_channel() -> None:
    """A11Y-01 claimed redundant encoding while pointing at a file that only bans rainbow
    cycling. The rule has to be stated where it is claimed."""
    skill = read(SKILL)
    assert "Never let a distinction live in color alone" in skill
    assert "label, shape, or position" in skill


def test_fresh_reader_check_is_something_an_agent_can_perform() -> None:
    """An agent cannot show a figure to a stranger. The check has to be a self-check."""
    story = read(STORY)
    assert "run on yourself" in story
    assert "Cover everything except the figure and its caption" in story
    assert "Compare it with the claim you wrote before drawing" in story


def test_anti_slop_catalogue_says_what_to_do_instead() -> None:
    """A list of bad patterns with no alternative is scolding, not routing."""
    story = read(STORY)
    table = [l for l in story.splitlines() if l.startswith("|") and l.count("|") >= 4]
    body = [l for l in table if "Why it fails" not in l and set(l) - set("|- ")]
    assert len(body) >= 5, "the anti-slop catalogue lost its cases"
    for row in body:
        assert len(row.split("|")[3].strip()) > 12, f"no alternative offered: {row[:60]}"


def test_one_takeaway_sequencing_is_in_the_body() -> None:
    skill = read(SKILL)
    assert "One takeaway per figure" in skill
    assert "named" in skill.split("One takeaway per figure", 1)[1][:400]
