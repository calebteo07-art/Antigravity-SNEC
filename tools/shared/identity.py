#!/usr/bin/env python3
"""Shared student identity manager — handles student IDs, consent, and profiles.

Every feature that needs to know who the student is imports this module.
Student IDs are UUIDs generated on first registration and stored in the
snec_consent sheet. Raw email is stored in Sheets (not in audit logs).

Usage (from other tools):
    from tools.shared.identity import get_or_create_student, has_consented, record_consent

Self-test:
    python tools/shared/identity.py
"""

import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from tools.shared.gsheets import append_row, get_rows, update_row, delete_row
from tools.shared.audit_log import log

PDPA_VERSION = "1.0"
SHEET = "snec_consent"


def get_or_create_student(name: str, email: str) -> str:
    """
    Look up a student by email. Create a new record if they don't exist yet.

    Args:
        name:  Student's full name.
        email: Student's email address (used as unique identifier).

    Returns:
        student_id: UUID string for this student.
    """
    existing = get_rows(SHEET, filters={"email": email})
    if existing:
        student_id = existing[0]["student_id"]
        log("student_lookup", student_id=student_id, feature="identity", detail="returning student")
        return student_id

    student_id = str(uuid.uuid4())
    append_row(SHEET, {
        "student_id": student_id,
        "student_name": name,
        "email": email,
        "consent_date": "",
        "pdpa_version": "",
        "withdrawn_date": "",
    })
    log("student_created", student_id=student_id, feature="identity", detail="new student registered")
    return student_id


def has_consented(student_id: str) -> bool:
    """
    Check whether a student has given PDPA consent.

    Returns:
        True if consent_date is recorded and withdrawn_date is empty.
    """
    rows = get_rows(SHEET, filters={"student_id": student_id})
    if not rows:
        return False
    row = rows[0]
    return bool(row.get("consent_date")) and not bool(row.get("withdrawn_date"))


def record_consent(student_id: str) -> None:
    """
    Record that a student has given PDPA consent.
    Sets consent_date and pdpa_version in the snec_consent sheet.
    """
    now = datetime.now(timezone.utc).isoformat()
    update_row(SHEET, "student_id", student_id, {
        "consent_date": now,
        "pdpa_version": PDPA_VERSION,
        "withdrawn_date": "",
    })
    log("consent_recorded", student_id=student_id, feature="identity",
        detail=f"pdpa_version={PDPA_VERSION}")


def withdraw_consent(student_id: str) -> None:
    """
    Record that a student has withdrawn PDPA consent.
    Sets withdrawn_date. Does not delete the row (required for audit trail).
    """
    now = datetime.now(timezone.utc).isoformat()
    update_row(SHEET, "student_id", student_id, {"withdrawn_date": now})
    log("consent_withdrawn", student_id=student_id, feature="identity", detail="")


def get_profile(student_id: str) -> dict | None:
    """
    Return the student's full profile row, or None if not found.
    """
    rows = get_rows(SHEET, filters={"student_id": student_id})
    return rows[0] if rows else None


if __name__ == "__main__":
    print("Testing identity.py...\n")

    TEST_EMAIL = "identity-test@snec-selftest.invalid"
    TEST_NAME = "Test Student"

    # Create student
    print("  Creating test student...")
    sid = get_or_create_student(TEST_NAME, TEST_EMAIL)
    assert sid, "Expected a student_id"
    print(f"  [OK] student_id: {sid}")

    # Idempotent — calling again returns same ID
    sid2 = get_or_create_student(TEST_NAME, TEST_EMAIL)
    assert sid == sid2, "Second call should return same student_id"
    print("  [OK] get_or_create is idempotent.")

    # No consent yet
    assert not has_consented(sid), "Should not have consent yet"
    print("  [OK] No consent initially.")

    # Record consent
    record_consent(sid)
    assert has_consented(sid), "Should have consent after recording"
    print("  [OK] Consent recorded.")

    # Get profile
    profile = get_profile(sid)
    assert profile["student_name"] == TEST_NAME
    assert profile["email"] == TEST_EMAIL
    print(f"  [OK] Profile: {profile}")

    # Withdraw consent
    withdraw_consent(sid)
    assert not has_consented(sid), "Should not have consent after withdrawal"
    print("  [OK] Consent withdrawn.")

    # Clean up test row
    delete_row(SHEET, "student_id", sid)
    print("  [OK] Test row cleaned up.")

    print("\n  [PASS] identity.py working correctly.")
    sys.exit(0)
