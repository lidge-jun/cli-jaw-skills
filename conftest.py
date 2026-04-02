"""Shared pytest configuration for office skill tests."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import tempfile
from pathlib import Path

import pytest

SKILLS_REF = Path(__file__).resolve().parent
OFFICECLI_DEFAULT = Path.home() / ".local" / "bin" / "officecli"


# ---------------------------------------------------------------------------
# Markers
# ---------------------------------------------------------------------------

def pytest_configure(config: pytest.Config) -> None:
    config.addinivalue_line("markers", "slow: marks tests as slow")
    config.addinivalue_line("markers", "cjk: CJK text roundtrip tests")
    config.addinivalue_line("markers", "regression: regression tests against fixture files")
    config.addinivalue_line("markers", "officecli: requires officecli binary")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _find_officecli() -> Path | None:
    if OFFICECLI_DEFAULT.exists():
        return OFFICECLI_DEFAULT
    path = shutil.which("officecli")
    return Path(path) if path else None


def run_officecli(*args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    """Run officecli with the given arguments and return CompletedProcess."""
    cli = _find_officecli()
    if cli is None:
        pytest.skip("officecli not installed")
    cmd = [str(cli), *args]
    return subprocess.run(
        cmd, capture_output=True, text=True, timeout=30, check=check,
    )


def run_officecli_json(*args: str, check: bool = True) -> dict:
    """Run officecli with --json flag and return parsed JSON."""
    result = run_officecli(*args, "--json", check=check)
    output = result.stdout.strip()
    if not output:
        output = result.stderr.strip()
    return json.loads(output)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def officecli_bin() -> Path:
    """Return path to officecli binary, skip if not installed."""
    cli = _find_officecli()
    if cli is None:
        pytest.skip("officecli not installed")
    return cli


@pytest.fixture
def tmp_docx(tmp_path: Path) -> Path:
    """Create a temporary blank .docx via officecli, yield path."""
    p = tmp_path / "test.docx"
    run_officecli("create", str(p))
    return p


@pytest.fixture
def tmp_xlsx(tmp_path: Path) -> Path:
    """Create a temporary blank .xlsx via officecli, yield path."""
    p = tmp_path / "test.xlsx"
    run_officecli("create", str(p))
    return p


@pytest.fixture
def tmp_pptx(tmp_path: Path) -> Path:
    """Create a temporary blank .pptx via officecli, yield path."""
    p = tmp_path / "test.pptx"
    run_officecli("create", str(p))
    return p
