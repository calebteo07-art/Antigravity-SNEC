"""Shared pytest fixtures for the SNEC AI test suite."""

import sys
from pathlib import Path
from unittest.mock import patch

import pytest

# Ensure project root is importable
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


@pytest.fixture(autouse=True)
def isolated_audit_log(tmp_path):
    """Redirect all audit log writes to a temp directory for every test.

    Prevents test runs from polluting .tmp/audit_log.jsonl and ensures
    each test sees a clean log state.
    """
    with patch("tools.shared.audit_log.LOG_FILE", tmp_path / "test_audit_log.jsonl"):
        yield


@pytest.fixture(autouse=True)
def reset_gsheets_cache():
    """Clear the gspread connection cache before and after every test.

    _get_spreadsheet() caches a live connection. Resetting it ensures
    tests that patch _get_spreadsheet don't accidentally reuse a previous
    real connection.
    """
    try:
        import tools.shared.gsheets as gs
        gs._client = None
        gs._spreadsheet = None
    except Exception:
        pass
    yield
    try:
        import tools.shared.gsheets as gs
        gs._client = None
        gs._spreadsheet = None
    except Exception:
        pass
