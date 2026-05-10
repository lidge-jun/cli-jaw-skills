"""Regression tests for the dev-frontend Korea/anti-slop refresh."""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEV_FRONTEND = ROOT / "dev-frontend"


def read(relative: str) -> str:
    return (DEV_FRONTEND / relative).read_text(encoding="utf-8")


def test_dev_frontend_routes_new_references() -> None:
    skill = read("SKILL.md")

    required = [
        "references/core/korea-2026.md",
        "references/core/ux-writing-ko.md",
        "references/core/product-density.md",
        "references/core/asset-requirements.md",
        "references/core/soft-3d-asset-gates.md",
        "references/core/visual-verification.md",
    ]

    for reference in required:
        assert reference in skill


def test_soft_3d_assets_are_defined_as_visual_assets_not_copy() -> None:
    gates = read("references/core/soft-3d-asset-gates.md")

    assert "soft 3D miniature objects" in gates
    assert "It does not mean" in gates
    assert "aegyo labels" in gates
    assert "Toss-Style Exception" in gates
    assert "generic public 3D icon pack" in gates


def test_korean_and_asset_slop_are_explicitly_covered() -> None:
    anti_slop = read("references/core/anti-slop.md")

    assert "Typography Slop Signals" in anti_slop
    assert "Banned" + " Fonts" not in anti_slop
    assert "CJK-safe fallbacks" in anti_slop
    assert "2026 Product Slop" in anti_slop
    assert "Korean Slop" in anti_slop
    assert "Soft 3D / Character Asset Slop" in anti_slop
    assert "Negative letter-spacing blindly applied to Hangul" in anti_slop
    assert "Asset-free pages" in anti_slop


def test_validator_blockers_are_regression_protected() -> None:
    skill = read("SKILL.md")
    aesthetics = read("references/core/aesthetics.md")
    visual = read("references/core/visual-verification.md")
    korea = read("references/core/korea-2026.md")
    react = read("references/stacks/react.md")
    nextjs = read("references/stacks/nextjs.md")
    motion = read("references/core/motion.md")

    assert "domain-appropriate stack" in skill
    assert "44×44px is a conservative product baseline" in skill
    assert "licensing/provenance" in aesthetics
    assert "await expect(page).toHaveScreenshot" in visual
    assert "KRDS-minded" in korea
    assert "KWCAG/WCAG" in korea
    assert "Server Components When Supported By The Framework" in react
    assert "Vite, SPA-only React" in react
    assert "Proxy / Middleware By Version" in nextjs
    assert "export function proxy" in nextjs
    assert "Next.js 15 and earlier" in nextjs
    assert "transition" + ": all" not in motion
    assert "transition-all" in motion


def test_stack_references_exist_for_full_zip_validation() -> None:
    required = [
        "references/stacks/react.md",
        "references/stacks/nextjs.md",
        "references/stacks/vanilla.md",
        "references/stacks/svelte.md",
    ]

    for reference in required:
        assert (DEV_FRONTEND / reference).exists(), reference


def test_new_reference_files_stay_under_skill_line_limit() -> None:
    for path in (DEV_FRONTEND / "references").rglob("*.md"):
        lines = path.read_text(encoding="utf-8").splitlines()
        assert len(lines) <= 500, f"{path.relative_to(ROOT)} has {len(lines)} lines"
