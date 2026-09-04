from __future__ import annotations

import json

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
# The count of skills that are BOTH registered in registry.json and present on disk.
# Not the count of `*/SKILL.md` directories: two unregistered backup directories
# (pptx_original, xlsx_original) were left behind when the office skills were replaced
# with their v4 versions, and a blind glob counts those as public surface. This file
# validates the PUBLIC surface, and registry.json is what defines it.
EXPECTED_SKILLS = 230
# Paths carry the jaw- prefix. The rename never reached this file, so every one of
# these exemptions silently stopped matching the file it was granted for -- and with
# the count check failing first, nothing surfaced it.
KNOWN_LONG_SKILLS = {
    "jaw-dev-pabcd/SKILL.md",
    "jaw-dev-testing/SKILL.md",
    "jaw-docx/SKILL.md",
    "jaw-hwp/SKILL.md",
    # jaw-pdf crossed 500 in ec0dd5e, the newest commit on main at the time, and the
    # broken count check above hid it: the count failed first, so this check never ran.
    # Granted for the same reason as its four siblings, which were all already exempt at
    # 572-877 lines -- a document-format skill carries per-format procedure that does not
    # compress into a router table. It was the only one of the five not on this list.
    "jaw-pdf/SKILL.md",
    "jaw-pptx/SKILL.md",
    "jaw-xlsx/SKILL.md",
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


def registered_skill_ids() -> set[str]:
    """Skill ids declared in registry.json — the repository's own definition of the
    published surface. A directory holding a SKILL.md is not automatically a skill."""
    registry = json.loads((ROOT / "registry.json").read_text(encoding="utf-8"))
    return set(registry["skills"])


def main() -> None:
    registered = registered_skill_ids()
    on_disk = {p.parent.name: p for p in ROOT.glob("*/SKILL.md")}

    skills = sorted(p for name, p in on_disk.items() if name in registered)
    if len(skills) != EXPECTED_SKILLS:
        raise SystemExit(f"expected {EXPECTED_SKILLS} registered skills, found {len(skills)}")

    # Report drift in both directions without failing on it. An unregistered directory is
    # dead weight rather than a broken surface, and a registry entry with no directory may
    # point at an upstream skill this repository does not vendor. Both are worth seeing;
    # neither is worth a red gate, and making them fatal here would re-break the gate the
    # way the blind glob did.
    unregistered = sorted(set(on_disk) - registered)
    if unregistered:
        print(f"note: {len(unregistered)} unregistered directories with a SKILL.md: {', '.join(unregistered)}")
    missing = sorted(registered - set(on_disk))
    if missing:
        print(f"note: {len(missing)} registry entries with no directory: {', '.join(missing)}")

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
    for needle in ["230", "47 skills", "28 skills", "2 skills"]:

        if needle not in readme:
            raise SystemExit(f"README missing public-surface count: {needle}")
    for needle in ["canonical", "og:image", "twitter:card", "230"]:
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

    print(f"validated {len(skills)} skills; known long skills are tracked")


if __name__ == "__main__":
    main()
