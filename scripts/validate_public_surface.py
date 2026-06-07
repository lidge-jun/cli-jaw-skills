from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EXPECTED_SKILLS = 224
KNOWN_LONG_SKILLS = {
    "docx/SKILL.md",
    "hwp/SKILL.md",
    "pptx/SKILL.md",
    "xlsx/SKILL.md",
}


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
    for needle in ["224", "43 skills", "28 skills", "2 skills"]:
        if needle not in readme:
            raise SystemExit(f"README missing public-surface count: {needle}")
    for needle in ["canonical", "og:image", "twitter:card", "224"]:
        if needle not in docs:
            raise SystemExit(f"docs missing marker: {needle}")

    required_assets = [
        ROOT / "docs/assets/favicon.svg",
        ROOT / "docs/assets/social-preview.svg",
    ]
    missing = [str(path.relative_to(ROOT)) for path in required_assets if not path.exists()]
    if missing:
        raise SystemExit("missing docs assets: " + ", ".join(missing))

    print(f"validated {len(skills)} skills; known long Office skills are tracked")


if __name__ == "__main__":
    main()
