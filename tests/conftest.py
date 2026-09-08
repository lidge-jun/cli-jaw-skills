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
import subprocess
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


def officecli_available() -> bool:
    return shutil.which("officecli") is not None


def run_officecli(*args: str, check: bool = True) -> subprocess.CompletedProcess:
    """Invoke the officecli binary.

    tests/office/test_cjk_regression.py has imported this helper from a conftest since it
    was written, but no conftest existed anywhere in the repository -- the file could not
    be collected at all. This is that helper.
    """
    binary = shutil.which("officecli")
    if binary is None:
        pytest.skip("officecli binary is not installed")
    return subprocess.run([binary, *args], capture_output=True, text=True, check=check)


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


def run_officecli_json(*args: str) -> dict:
    """officecli invocation whose stdout is JSON.

    Same story as run_officecli: imported by the CJK suite since it was written, never
    defined anywhere. The suite skips without the binary, so this only has to be correct
    on a machine that has it.
    """
    import json

    result = run_officecli(*args, "--json", check=False)
    if result.returncode != 0:
        pytest.fail(f"officecli {' '.join(args)} exited {result.returncode}: {result.stderr.strip()}")
    return json.loads(result.stdout or "{}")


@pytest.fixture
def tmp_docx(tmp_path: Path) -> Path:
    return _blank_office_file(tmp_path, "docx")


@pytest.fixture
def tmp_xlsx(tmp_path: Path) -> Path:
    return _blank_office_file(tmp_path, "xlsx")


@pytest.fixture
def tmp_pptx(tmp_path: Path) -> Path:
    return _blank_office_file(tmp_path, "pptx")


@pytest.fixture
def tmp_hwp(tmp_path: Path) -> Path:
    return _blank_office_file(tmp_path, "hwp")


def _blank_office_file(tmp_path: Path, suffix: str) -> Path:
    """A new document of the requested format, created by officecli itself."""
    target = tmp_path / f"sample.{suffix}"
    run_officecli("new", str(target))
    return target
