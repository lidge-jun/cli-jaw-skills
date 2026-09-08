"""Shared fixtures for the cli-jaw-skills suite.

The suite is split by concern -- structure, frontmatter, registry, docs, content, office
-- the way ../opencodex splits its tests by domain behind one runner. Everything that
needs to know what a skill IS imports it from scripts/validate_public_surface.py rather
than re-deriving it, so the CI gate and the tests cannot drift apart.

The import goes through importlib because scripts/ is not a package and adding an
__init__.py to a directory of standalone tools would be worse than one explicit loader.
"""

from __future__ import annotations

import importlib.util
import shutil
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]


def _load_validator():
    spec = importlib.util.spec_from_file_location(
        "validate_public_surface", REPO_ROOT / "scripts" / "validate_public_surface.py"
    )
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    # Register before executing: @dataclass resolves its own module out of sys.modules,
    # and a module loaded by path alone is not there yet.
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


validator = _load_validator()


@pytest.fixture(scope="session")
def repo_root() -> Path:
    """Tests take the root from here instead of counting parent directories, so moving a
    test between folders cannot silently repoint it."""
    return REPO_ROOT


@pytest.fixture(scope="session")
def skills():
    """Every skill the registry defines, including bundles whose SKILL.md sits deeper."""
    return validator.discover_skills()


@pytest.fixture(scope="session")
def registry(repo_root: Path) -> dict:
    import json

    return json.loads((repo_root / "registry.json").read_text(encoding="utf-8"))["skills"]


@pytest.fixture(scope="session")
def surface():
    """The validator module itself, for tests that exercise its checks directly."""
    return validator


# officecli helpers and format fixtures live in the ROOT conftest.py, which predates this
# split and is already wired for the office suites. tests/office/test_cjk_regression.py
# imports them from there; re-defining them here would give the repository two versions of
# the same helper.


def officecli_available() -> bool:
    return shutil.which("officecli") is not None or (Path.home() / ".local" / "bin" / "officecli").exists()


def pytest_collection_modifyitems(config, items):
    """Skip binary-dependent suites instead of failing them.

    A contributor without officecli should get a clean run with a stated reason, not a
    wall of red from a dependency the repository never claimed to require.
    """
    if officecli_available():
        return
    skip = pytest.mark.skip(reason="officecli binary is not installed")
    for item in items:
        if "officecli" in item.keywords or "/office/" in str(item.fspath):
            item.add_marker(skip)
