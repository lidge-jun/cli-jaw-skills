from __future__ import annotations

import json

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EXPECTED_SKILLS = 227
KNOWN_LONG_SKILLS = {
    "docx/SKILL.md",
    "hwp/SKILL.md",
    "pptx/SKILL.md",
    "xlsx/SKILL.md",
}


def validate_registry() -> None:
    """Registry integrity: every entry resolves to a SKILL.md, requires uses the
    normalized schema (bins/env/system), and no description is truncated."""
    registry = json.loads((ROOT / "registry.json").read_text(encoding="utf-8"))["skills"]
    allowed_requires = {"bins", "env", "system"}
    problems = []
    for skill_id, meta in registry.items():
        entry = meta.get("entry", f"{skill_id}/SKILL.md")
        if not (ROOT / entry).exists():
            problems.append(f"{skill_id}: missing SKILL.md at {entry}")
        requires = meta.get("requires")
        if isinstance(requires, dict):
            unknown = set(requires) - allowed_requires
            if unknown:
                problems.append(f"{skill_id}: non-normalized requires keys {sorted(unknown)}")
        if str(meta.get("description", "")).endswith("..."):
            problems.append(f"{skill_id}: truncated description")
    if problems:
        raise SystemExit("registry integrity failures:\n" + "\n".join(problems))


def main() -> None:
    skills = sorted(ROOT.glob("*/SKILL.md"))
    if len(skills) != EXPECTED_SKILLS:
        raise SystemExit(f"expected {EXPECTED_SKILLS} skills, found {len(skills)}")

    over_limit = []
    for skill in skills:
        lines = skill.read_text(encoding="utf-8").splitlines()
        relative = str(skill.relative_to(ROOT))
        if len(lines) > 500 and relative not in KNOWN_LONG_SKILLS:
            over_limit.append(f"{relative}:{len(lines)}")

    if over_limit:
        raise SystemExit("unexpected new SKILL.md line-limit drift: " + ", ".join(over_limit))

    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    docs = (ROOT / "docs/index.html").read_text(encoding="utf-8")
    for needle in ["227", "47 skills", "28 skills", "2 skills"]:

        if needle not in readme:
            raise SystemExit(f"README missing public-surface count: {needle}")
    for needle in ["canonical", "og:image", "twitter:card", "227"]:
        if needle not in docs:
            raise SystemExit(f"docs missing marker: {needle}")

    required_assets = [
        ROOT / "docs/assets/favicon.svg",
        ROOT / "docs/assets/social-preview.svg",
    ]
    missing = [str(path.relative_to(ROOT)) for path in required_assets if not path.exists()]
    if missing:
        raise SystemExit("missing docs assets: " + ", ".join(missing))

    validate_registry()

    print(f"validated {len(skills)} skills; known long Office skills are tracked")


if __name__ == "__main__":
    main()
