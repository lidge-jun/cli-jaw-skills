"""Write the published skill-surface figures from the tree.

The counts in README.md and docs/index.html used to be asserted by CI, which meant a
number going stale turned the build red without anything being broken. They are generated
here instead: run this after adding or removing a skill and commit the result. Nothing
fails if you forget -- the numbers are documentation, not an invariant.
"""

from __future__ import annotations

import importlib.util
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _validator():
    spec = importlib.util.spec_from_file_location(
        "validate_public_surface", ROOT / "scripts" / "validate_public_surface.py"
    )
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def main() -> int:
    validator = _validator()
    counts = validator.measure(validator.discover_skills())

    substitutions = {
        "README.md": [
            (r"(skills-)\d+(-111827)", counts["skills"]),
            (r"(alt=\")\d+( skills\")", counts["skills"]),
            (r"(reference_assets-)\d+(-2563eb)", counts["reference_folders"]),
            (r"(alt=\")\d+( skills with references\")", counts["reference_folders"]),
            (r"(\| Skill library \| )\d+( top-level)", counts["skills"]),
            (r"(\| Reference material \| )\d+( skills include)", counts["reference_folders"]),
            (r"(\| Helper scripts \| )\d+( skills include)", counts["script_folders"]),
            (r"(\| Templates \| )\d+( skills include)", counts["template_folders"]),
        ],
        "docs/index.html": [
            (r"(<h1>)\d+( inspectable skills)", counts["skills"]),
            (r"(<strong>)\d+(</strong><span>skills</span>)", counts["skills"]),
            (r"(<strong>)\d+(</strong><span>with references</span>)", counts["reference_folders"]),
            (r"(<strong>)\d+(</strong><span>with scripts</span>)", counts["script_folders"]),
            (r"(<strong>)\d+(</strong><span>with templates</span>)", counts["template_folders"]),
            (r"(<td>Reference folders</td><td>)\d+( skills</td>)", counts["reference_folders"]),
        ],
    }

    changed = []
    for relative, rules in substitutions.items():
        path = ROOT / relative
        text = original = path.read_text(encoding="utf-8")
        for pattern, value in rules:
            text = re.sub(pattern, lambda m, v=value: f"{m.group(1)}{v}{m.group(2)}", text)
        if text != original:
            path.write_text(text, encoding="utf-8")
            changed.append(relative)

    summary = ", ".join(f"{k}={v}" for k, v in counts.items())
    print(f"measured {summary}")
    print("updated " + ", ".join(changed) if changed else "no changes needed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
