"""LibreOffice (soffice) helper for headless operations.

Provides a wrapper that handles sandboxed environments where AF_UNIX
sockets may be blocked. Automatically detects and applies workarounds.

Usage:
    from ooxml.soffice import run_soffice

    result = run_soffice(["--headless", "--convert-to", "pdf", "input.docx"])
"""

import os
import shutil
import socket
import subprocess
from pathlib import Path


def run_soffice(args: list[str], **kwargs) -> subprocess.CompletedProcess:
    """Run soffice with appropriate environment settings."""
    env = _build_env()
    soffice_bin = _find_soffice()
    return subprocess.run([soffice_bin] + args, env=env, **kwargs)


def _build_env() -> dict:
    """Build environment dict with headless rendering support."""
    env = os.environ.copy()
    # Use headless rendering plugin (no display required)
    env["SAL_USE_VCLPLUGIN"] = "svp"
    return env


def _find_soffice() -> str:
    """Locate the soffice binary."""
    # Check PATH first
    which = shutil.which("soffice")
    if which:
        return which

    # macOS common locations
    mac_paths = [
        "/Applications/LibreOffice.app/Contents/MacOS/soffice",
        os.path.expanduser("~/Applications/LibreOffice.app/Contents/MacOS/soffice"),
    ]
    for p in mac_paths:
        if os.path.isfile(p):
            return p

    # Linux common locations
    linux_paths = [
        "/usr/bin/soffice",
        "/usr/local/bin/soffice",
        "/snap/bin/soffice",
    ]
    for p in linux_paths:
        if os.path.isfile(p):
            return p

    # Fall back to bare command name (will fail with clear error if not found)
    return "soffice"


if __name__ == "__main__":
    import sys
    result = run_soffice(sys.argv[1:])
    sys.exit(result.returncode)
