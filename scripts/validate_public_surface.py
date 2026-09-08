"""Validate the cli-jaw skill library's public surface.

What this checks and what it deliberately does not.

The old version asserted counts: a hardcoded skill total, and greps for the literal
strings "230", "28 skills", "2 skills" in README.md and docs/index.html. Every one of
those fires when a number goes stale, never when a skill is broken, so adding a skill
turned CI red until three documents were hand-edited. A grep also only asks whether a
string appears somewhere in a file, which is not a check that the number is true.

What replaced them are invariants that can only fail when something is actually wrong:
frontmatter parses and carries a name and description, the declared name agrees with the
skill id, no two skills claim the same name, every registry entry resolves to a real
SKILL.md, and the documentation assets exist. Counts are still measured -- they are
printed as output, and `--json` emits them for the generator that writes the published
figures -- but nothing fails because a number moved.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

# Document-format skills carry per-format procedure that does not compress into a router
# table. The cap is a readability rule for ordinary skills, and these are the standing
# exceptions rather than a drift-tracking list.
LONG_SKILL_EXEMPTIONS = {
    "jaw-dev-pabcd/SKILL.md",
    "jaw-dev-testing/SKILL.md",
    "jaw-docx/SKILL.md",
    "jaw-hwp/SKILL.md",
    "jaw-pdf/SKILL.md",
    "jaw-pptx/SKILL.md",
    "jaw-xlsx/SKILL.md",
}
LINE_LIMIT = 500

# Upstream originals kept beside their jaw- adaptations. They stay OUT of registry.json:
# their frontmatter declares "license: Proprietary. LICENSE.txt has complete terms" and no
# LICENSE.txt is present, so publishing them into an installable catalogue would be wrong.
# Named here so the exclusion is visible in code rather than silently tolerated.
VENDORED_UNREGISTERED = {"pptx_original", "xlsx_original"}


@dataclass
class Skill:
    """A skill as the registry defines it, plus the file that actually holds it."""

    skill_id: str
    path: Path
    registered: bool
    frontmatter: dict[str, str] = field(default_factory=dict)

    @property
    def is_bundle(self) -> bool:
        """True when SKILL.md sits below the skill directory.

        A bundle packages several skills (`static-analysis/skills/codeql/SKILL.md`), so
        its frontmatter names the INNER skill -- `codeql`, not `static-analysis`. The
        name check accounts for that instead of failing on it.
        """
        return self.path.parent.name != self.skill_id


def parse_frontmatter(text: str) -> dict[str, str] | None:
    """Read a SKILL.md frontmatter block into a flat mapping.

    Hand-rolled because the repository has no YAML dependency and adding one for four
    keys is not worth it. Two shapes matter beyond `key: value`: nested blocks (the
    `metadata` and `capabilities` maps some skills carry) are skipped rather than
    misparsed, and folded block scalars (`description: >-` with the text on indented
    continuation lines, twelve files today) are consumed. Without that second case the
    value reads as the literal ">-", which is non-empty and would let a genuinely empty
    description pass.
    """
    match = re.match(r"^---\n(.*?)\n---", text, re.S)
    if match is None:
        return None

    data: dict[str, str] = {}
    lines = match.group(1).split("\n")
    index = 0
    while index < len(lines):
        line = lines[index]
        index += 1
        if not line.strip() or line.startswith((" ", "\t", "#")):
            continue
        key, sep, value = line.partition(":")
        if not sep:
            continue
        key = key.strip()
        value = value.strip()
        if value in {">", ">-", "|", "|-"}:
            folded = []
            while index < len(lines) and (not lines[index].strip() or lines[index].startswith((" ", "\t"))):
                folded.append(lines[index].strip())
                index += 1
            value = " ".join(part for part in folded if part)
        data[key] = value.strip().strip('"').strip("'")
    return data


def discover_skills() -> list[Skill]:
    """Every skill, found the way registry.json defines them.

    A blind `*/SKILL.md` glob misses bundles, whose SKILL.md sits one level down and
    whose registry entry already names the real path. The old file globbed in one
    function and honored `entry` in another, so six real skills looked orphaned.
    """
    registry = json.loads((ROOT / "registry.json").read_text(encoding="utf-8"))["skills"]
    skills: list[Skill] = []
    seen: set[Path] = set()

    for skill_id, meta in registry.items():
        entry = ROOT / meta.get("entry", f"{skill_id}/SKILL.md")
        if entry.exists():
            skills.append(Skill(skill_id, entry, registered=True))
            seen.add(entry)

    for path in sorted(ROOT.glob("*/SKILL.md")):
        if path not in seen:
            skills.append(Skill(path.parent.name, path, registered=False))

    for skill in skills:
        skill.frontmatter = parse_frontmatter(skill.path.read_text(encoding="utf-8")) or {}
    return sorted(skills, key=lambda s: s.skill_id)


def check_frontmatter(skills: list[Skill]) -> list[str]:
    problems = []
    for skill in skills:
        relative = skill.path.relative_to(ROOT)
        if not skill.frontmatter:
            problems.append(f"{relative}: no parseable frontmatter block")
            continue
        if not skill.frontmatter.get("name"):
            problems.append(f"{relative}: frontmatter has no name")
        if not skill.frontmatter.get("description"):
            problems.append(f"{relative}: frontmatter has no description")
    return problems


def check_names(skills: list[Skill]) -> list[str]:
    """The declared name has to agree with the id the rest of the system uses.

    For a bundle that means the registry key against its directory, because the file
    itself names the inner skill.
    """
    problems = []
    seen: dict[str, str] = {}
    for skill in skills:
        relative = skill.path.relative_to(ROOT)
        declared = skill.frontmatter.get("name", "")
        if skill.is_bundle:
            if skill.path.parts[len(ROOT.parts)] != skill.skill_id:
                problems.append(f"{relative}: bundle entry does not live under {skill.skill_id}/")
        elif declared and declared != skill.skill_id:
            problems.append(f"{relative}: declares name '{declared}' in directory '{skill.skill_id}'")
        key = declared or skill.skill_id
        if key in seen and seen[key] != str(relative):
            problems.append(f"duplicate skill name '{key}': {seen[key]} and {relative}")
        seen.setdefault(key, str(relative))
    return problems


def check_line_limit(skills: list[Skill]) -> list[str]:
    problems = []
    for skill in skills:
        relative = str(skill.path.relative_to(ROOT))
        if relative in LONG_SKILL_EXEMPTIONS:
            continue
        length = len(skill.path.read_text(encoding="utf-8").splitlines())
        if length > LINE_LIMIT:
            problems.append(
                f"{relative}: {length} lines exceeds the {LINE_LIMIT}-line readability limit "
                "(add it to LONG_SKILL_EXEMPTIONS with a reason if the length is justified)"
            )
    return problems


def check_registry(skills: list[Skill]) -> list[str]:
    """Registry integrity, and correspondence with what is on disk."""
    registry = json.loads((ROOT / "registry.json").read_text(encoding="utf-8"))["skills"]
    allowed_requires = {"bins", "env", "system"}
    problems = []

    for skill_id, meta in registry.items():
        entry = meta.get("entry", f"{skill_id}/SKILL.md")
        if not (ROOT / entry).exists():
            problems.append(f"{skill_id}: registry entry points at a missing {entry}")
        requires = meta.get("requires")
        if isinstance(requires, dict):
            unknown = set(requires) - allowed_requires
            if unknown:
                problems.append(f"{skill_id}: non-normalized requires keys {sorted(unknown)}")
        if str(meta.get("description", "")).endswith("..."):
            problems.append(f"{skill_id}: truncated description")

    unregistered = {s.skill_id for s in skills if not s.registered}
    unexpected = sorted(unregistered - VENDORED_UNREGISTERED)
    if unexpected:
        problems.append(
            "unregistered skill directories: " + ", ".join(unexpected)
            + " (register them, or add them to VENDORED_UNREGISTERED with the reason)"
        )
    stale = sorted(VENDORED_UNREGISTERED - unregistered)
    if stale:
        problems.append(f"VENDORED_UNREGISTERED lists skills that are no longer unregistered: {', '.join(stale)}")
    return problems


def check_docs_assets() -> list[str]:
    problems = []
    for asset in ("docs/assets/favicon.svg", "docs/assets/social-preview.svg"):
        if not (ROOT / asset).exists():
            problems.append(f"missing docs asset: {asset}")
    docs = (ROOT / "docs/index.html").read_text(encoding="utf-8")
    for marker in ('rel="canonical"', 'property="og:image"', 'name="twitter:card"'):
        if marker not in docs:
            problems.append(f"docs/index.html is missing {marker}")
    return problems


# Private development records belong in lidge-jun/cli-jaw-internal. This repository is
# public and is consumed as a submodule, so anything committed here is disclosed the
# moment it is pushed.
#
# The rule exists because 29 such files lived at this repository's root for some time
# without anything noticing. cli-jaw's own check:private-boundary matches whole path
# segments against the index of the repository it runs in, and until recently never
# enumerated submodule contents -- so it reported clean while these sat inside one. A
# gate in the consuming repository cannot be relied on to police this one.
#
# Segments rather than substrings: a skill legitimately named "deployment-planning"
# must not trip a rule aimed at "_plan".
PRIVATE_SEGMENTS = re.compile(r"^(?:devlog(?:[._-].*)?|cli-jaw-internal|_plan|_fin|\.jwc)$", re.IGNORECASE)


def check_private_records() -> list[str]:
    """Tracked files whose path names a private-records directory."""
    tracked = subprocess.run(
        ["git", "ls-files", "-z"],
        cwd=ROOT, capture_output=True, text=True, check=True,
    ).stdout.split("\0")
    offenders = [
        path for path in tracked
        if path and any(PRIVATE_SEGMENTS.match(segment) for segment in path.split("/"))
    ]
    if not offenders:
        return []
    shown = "\n    ".join(offenders[:10])
    more = f"\n    ... and {len(offenders) - 10} more" if len(offenders) > 10 else ""
    return [
        f"{len(offenders)} private development record(s) tracked in this public repository; "
        f"they belong in cli-jaw-internal:\n    {shown}{more}"
    ]


REFERENCE_PATH = re.compile(r"`((?:references?|scripts)/[^`\s]+)`")


def report_unresolved_paths(skills: list[Skill]) -> dict[str, int]:
    """Backtick-quoted local paths that do not resolve, as a cleanup worklist.

    A warning on purpose. Measured across the tree there are ~138 of these in 15 skills,
    most of them prose that names a file the skill does not ship. That is worth seeing and
    worth cleaning, but it is not evidence that anything regressed, so it never fails.
    Glob forms are skipped because `scripts/*.py` is a pattern, not a path.
    """
    unresolved: dict[str, int] = {}
    for skill in skills:
        directory = skill.path.parent
        count = 0
        for candidate in REFERENCE_PATH.findall(skill.path.read_text(encoding="utf-8")):
            if any(ch in candidate for ch in "*?[]"):
                continue
            if not (directory / candidate).exists():
                count += 1
        if count:
            unresolved[skill.skill_id] = count
    return unresolved


def measure(skills: list[Skill]) -> dict[str, int]:
    """The published figures, measured rather than asserted."""
    directories = [d for d in ROOT.iterdir() if d.is_dir() and not d.name.startswith(".")]
    return {
        "skills": len([s for s in skills if s.registered]),
        "reference_folders": len([d for d in directories if (d / "references").is_dir() or (d / "reference").is_dir()]),
        "script_folders": len([d for d in directories if (d / "scripts").is_dir()]),
        "template_folders": len([d for d in directories if (d / "templates").is_dir()]),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="emit the measured inventory as JSON")
    args = parser.parse_args()

    skills = discover_skills()
    problems = (
        check_frontmatter(skills)
        + check_names(skills)
        + check_line_limit(skills)
        + check_registry(skills)
        + check_docs_assets()
        + check_private_records()
    )

    counts = measure(skills)
    if args.json:
        print(json.dumps(counts, indent=2))
        return 0

    if problems:
        print("public surface is invalid:", file=sys.stderr)
        for problem in problems:
            print(f"  - {problem}", file=sys.stderr)
        return 1

    unresolved = report_unresolved_paths(skills)
    if unresolved:
        total = sum(unresolved.values())
        worst = ", ".join(f"{k} ({v})" for k, v in sorted(unresolved.items(), key=lambda kv: -kv[1])[:5])
        print(f"note: {total} unresolved reference paths in {len(unresolved)} skills; largest: {worst}")

    print(
        f"validated {counts['skills']} registered skills "
        f"({counts['reference_folders']} with references, {counts['script_folders']} with scripts, "
        f"{counts['template_folders']} with templates)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
