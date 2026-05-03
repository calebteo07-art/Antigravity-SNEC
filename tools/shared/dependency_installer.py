#!/usr/bin/env python3
"""Agent 3: Dependency Installer - installs all required packages for the SNEC platform.

Usage:
    python tools/shared/dependency_installer.py
"""

import importlib.util
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
REQUIREMENTS_FILE = PROJECT_ROOT / "requirements.txt"

PACKAGES: dict[str, str] = {
    "anthropic": "anthropic",
    "gspread": "gspread",
    "google.auth": "google-auth",
    "googleapiclient": "google-api-python-client",
    "google_auth_oauthlib": "google-auth-oauthlib",
    "google_auth_httplib2": "google-auth-httplib2",
    "typer": "typer",
    "rich": "rich",
    "streamlit": "streamlit",
    "PIL": "Pillow",
    "pydicom": "pydicom",
    "pydantic": "pydantic",
    "reportlab": "reportlab",
    "dotenv": "python-dotenv",
}


def _is_installed(import_name: str) -> bool:
    try:
        return importlib.util.find_spec(import_name) is not None
    except (ModuleNotFoundError, ValueError):
        return False


def _print(msg: str) -> None:
    print(msg, flush=True)


def check_missing() -> list[str]:
    missing = []
    for import_name, pip_name in PACKAGES.items():
        if not _is_installed(import_name):
            missing.append(pip_name)
    return missing


def install_packages() -> bool:
    if not REQUIREMENTS_FILE.exists():
        _print(f"ERROR: {REQUIREMENTS_FILE} not found.")
        return False

    _print(f"Running: pip install -r {REQUIREMENTS_FILE.name}")
    _print("-" * 50)

    result = subprocess.run(
        [sys.executable, "-m", "pip", "install", "-r", str(REQUIREMENTS_FILE)],
        cwd=PROJECT_ROOT,
    )

    _print("-" * 50)
    return result.returncode == 0


def verify_installation() -> tuple[list[str], list[str]]:
    passed = []
    failed = []
    for import_name, pip_name in PACKAGES.items():
        if _is_installed(import_name):
            passed.append(pip_name)
        else:
            failed.append(pip_name)
    return passed, failed


def main() -> None:
    _print("\n  SNEC AI - Dependency Installer")
    _print("=" * 50)

    # Step 1: Check what's missing before install
    missing_before = check_missing()
    already_installed = len(PACKAGES) - len(missing_before)

    if not missing_before:
        _print(f"\n  All {len(PACKAGES)} packages already installed. Nothing to do.")
        _print("\n  Run python tools/shared/env_validator.py to confirm full status.\n")
        sys.exit(0)

    _print(f"\n  Already installed : {already_installed}/{len(PACKAGES)} packages")
    _print(f"  Missing           : {len(missing_before)} packages")
    _print(f"\n  Installing from   : {REQUIREMENTS_FILE.name}\n")

    # Step 2: Install
    success = install_packages()

    if not success:
        _print("\n  ERROR: pip install failed. Check the output above for details.")
        _print("  Common fixes:")
        _print("    - Make sure Python and pip are up to date: python -m pip install --upgrade pip")
        _print("    - Check your internet connection")
        _print("    - On Windows, try running this terminal as Administrator\n")
        sys.exit(1)

    # Step 3: Verify
    _print("\n  Verifying installation...\n")
    passed, failed = verify_installation()

    for pkg in passed:
        _print(f"  [OK]   {pkg}")
    for pkg in failed:
        _print(f"  [FAIL] {pkg}")

    if failed:
        _print(f"\n  {len(failed)} package(s) failed to install:")
        for pkg in failed:
            _print(f"    pip install {pkg}")
        _print()
        sys.exit(1)

    _print(f"\n  All {len(passed)} packages installed successfully.")
    _print("\n  Next step: python tools/shared/env_validator.py\n")
    sys.exit(0)


if __name__ == "__main__":
    main()
