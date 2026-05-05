"""Tests for the student identity module (tools/shared/identity.py).

gsheets is fully mocked — no real Sheets connection needed.
"""

from unittest.mock import patch, MagicMock

import pytest


# ── Helpers ────────────────────────────────────────────────────────────────────

def _row(consent_date="", withdrawn_date="", student_id="test-sid", email="test@test.com"):
    return [{
        "student_id":     student_id,
        "student_name":   "Test User",
        "email":          email,
        "consent_date":   consent_date,
        "pdpa_version":   "1.0" if consent_date else "",
        "withdrawn_date": withdrawn_date,
    }]


# ── has_consented ──────────────────────────────────────────────────────────────

class TestHasConsented:
    def test_true_when_consent_date_set_and_not_withdrawn(self):
        with patch("tools.shared.identity.get_rows", return_value=_row(consent_date="2026-01-01T00:00:00+00:00")):
            from tools.shared.identity import has_consented
            assert has_consented("test-sid") is True

    def test_false_when_consent_date_empty(self):
        with patch("tools.shared.identity.get_rows", return_value=_row(consent_date="")):
            from tools.shared.identity import has_consented
            assert has_consented("test-sid") is False

    def test_false_when_withdrawn(self):
        with patch("tools.shared.identity.get_rows",
                   return_value=_row(consent_date="2026-01-01", withdrawn_date="2026-02-01")):
            from tools.shared.identity import has_consented
            assert has_consented("test-sid") is False

    def test_false_when_student_not_found(self):
        with patch("tools.shared.identity.get_rows", return_value=[]):
            from tools.shared.identity import has_consented
            assert has_consented("unknown-sid") is False


# ── get_or_create_student ──────────────────────────────────────────────────────

class TestGetOrCreateStudent:
    def test_returns_existing_student_id(self):
        existing = _row(student_id="existing-uuid-123")
        with patch("tools.shared.identity.get_rows", return_value=existing), \
             patch("tools.shared.identity.log"):
            from tools.shared.identity import get_or_create_student
            sid = get_or_create_student("Name", "test@test.com")
        assert sid == "existing-uuid-123"

    def test_does_not_create_row_for_existing_student(self):
        existing = _row(student_id="existing-uuid-123")
        with patch("tools.shared.identity.get_rows", return_value=existing), \
             patch("tools.shared.identity.append_row") as mock_append, \
             patch("tools.shared.identity.log"):
            from tools.shared.identity import get_or_create_student
            get_or_create_student("Name", "test@test.com")
        mock_append.assert_not_called()

    def test_creates_new_row_for_new_student(self):
        with patch("tools.shared.identity.get_rows", return_value=[]), \
             patch("tools.shared.identity.append_row") as mock_append, \
             patch("tools.shared.identity.log"):
            from tools.shared.identity import get_or_create_student
            get_or_create_student("New User", "new@test.com")
        mock_append.assert_called_once()

    def test_new_student_id_is_uuid_format(self):
        import re
        uuid_pattern = re.compile(
            r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"
        )
        with patch("tools.shared.identity.get_rows", return_value=[]), \
             patch("tools.shared.identity.append_row"), \
             patch("tools.shared.identity.log"):
            from tools.shared.identity import get_or_create_student
            sid = get_or_create_student("User", "user@test.com")
        assert uuid_pattern.match(sid), f"Not a UUID: {sid}"

    def test_same_email_returns_same_id(self):
        existing = _row(student_id="stable-uuid")
        with patch("tools.shared.identity.get_rows", return_value=existing), \
             patch("tools.shared.identity.log"):
            from tools.shared.identity import get_or_create_student
            sid1 = get_or_create_student("User", "same@test.com")
            sid2 = get_or_create_student("User", "same@test.com")
        assert sid1 == sid2 == "stable-uuid"


# ── record_consent ─────────────────────────────────────────────────────────────

class TestRecordConsent:
    def test_calls_update_row_with_consent_date(self):
        with patch("tools.shared.identity.update_row") as mock_update, \
             patch("tools.shared.identity.log"):
            from tools.shared.identity import record_consent
            record_consent("test-sid")

        mock_update.assert_called_once()
        _, _, _, updates = mock_update.call_args[0]
        assert updates["consent_date"]            # non-empty
        assert updates["pdpa_version"] == "1.0"
        assert updates["withdrawn_date"] == ""

    def test_clears_withdrawn_date_on_re_consent(self):
        with patch("tools.shared.identity.update_row") as mock_update, \
             patch("tools.shared.identity.log"):
            from tools.shared.identity import record_consent
            record_consent("test-sid")

        _, _, _, updates = mock_update.call_args[0]
        assert updates["withdrawn_date"] == ""


# ── withdraw_consent ───────────────────────────────────────────────────────────

class TestWithdrawConsent:
    def test_sets_withdrawn_date(self):
        with patch("tools.shared.identity.update_row") as mock_update, \
             patch("tools.shared.identity.log"):
            from tools.shared.identity import withdraw_consent
            withdraw_consent("test-sid")

        mock_update.assert_called_once()
        _, _, _, updates = mock_update.call_args[0]
        assert updates["withdrawn_date"]   # non-empty ISO timestamp


# ── get_profile ────────────────────────────────────────────────────────────────

class TestGetProfile:
    def test_returns_profile_dict_when_found(self):
        row = _row(student_id="s1")
        with patch("tools.shared.identity.get_rows", return_value=row):
            from tools.shared.identity import get_profile
            profile = get_profile("s1")
        assert profile is not None
        assert profile["student_id"] == "s1"

    def test_returns_none_when_not_found(self):
        with patch("tools.shared.identity.get_rows", return_value=[]):
            from tools.shared.identity import get_profile
            assert get_profile("nobody") is None
