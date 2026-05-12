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

from tools.shared.database import SessionLocal
from tools.shared.models import Student
from tools.shared.audit_log import log

PDPA_VERSION = "1.0"


def get_or_create_student(name: str, email: str) -> str:
    """
    Look up a student by email. Create a new record if they don't exist yet.

    Args:
        name:  Student's full name.
        email: Student's email address (used as unique identifier).

    Returns:
        student_id: UUID string for this student.
    """
    with SessionLocal() as db:
        existing = db.query(Student).filter(Student.email == email).first()
        if existing:
            log("student_lookup", student_id=existing.student_id, feature="identity", detail="returning student")
            return existing.student_id

        new_student = Student(
            student_name=name,
            email=email
        )
        db.add(new_student)
        db.commit()
        db.refresh(new_student)
        log("student_created", student_id=new_student.student_id, feature="identity", detail="new student registered")
        return new_student.student_id



def has_consented(student_id: str) -> bool:
    """
    Check whether a student has given PDPA consent.

    Returns:
        True if consent_date is recorded and withdrawn_date is empty.
    """
    with SessionLocal() as db:
        student = db.query(Student).filter(Student.student_id == student_id).first()
        if not student:
            return False
        return bool(student.consent_date) and not bool(student.withdrawn_date)


def record_consent(student_id: str) -> None:
    """
    Record that a student has given PDPA consent.
    Sets consent_date and pdpa_version in the snec_consent sheet.
    """
    now = datetime.now(timezone.utc)
    with SessionLocal() as db:
        student = db.query(Student).filter(Student.student_id == student_id).first()
        if student:
            student.consent_date = now
            student.pdpa_version = PDPA_VERSION
            student.withdrawn_date = None
            db.commit()
            
    log("consent_recorded", student_id=student_id, feature="identity",
        detail=f"pdpa_version={PDPA_VERSION}")


def withdraw_consent(student_id: str) -> None:
    """
    Record that a student has withdrawn PDPA consent.
    Sets withdrawn_date. Does not delete the row (required for audit trail).
    """
    now = datetime.now(timezone.utc)
    with SessionLocal() as db:
        student = db.query(Student).filter(Student.student_id == student_id).first()
        if student:
            student.withdrawn_date = now
            db.commit()
    log("consent_withdrawn", student_id=student_id, feature="identity", detail="")


def get_profile(student_id: str) -> dict | None:
    """
    Return the student's full profile row, or None if not found.
    """
    with SessionLocal() as db:
        student = db.query(Student).filter(Student.student_id == student_id).first()
        if not student:
            return None
        
        # Convert SQLAlchemy model to dict for backward compatibility
        return {
            "student_id": student.student_id,
            "student_name": student.student_name,
            "email": student.email,
            "consent_date": student.consent_date.isoformat() if student.consent_date else "",
            "withdrawn_date": student.withdrawn_date.isoformat() if student.withdrawn_date else "",
            "weak_topics": student.weak_topics,
            "missed_findings": student.missed_findings,
            "retention_scores": student.retention_scores,
            "session_count": student.session_count,
            "streak": student.streak,
            "last_active": student.last_active.isoformat() if student.last_active else "",
            "learning_velocity": student.learning_velocity,
            "checkin_done_today": str(student.checkin_done_today).lower()
        }


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
    with SessionLocal() as db:
        db.query(Student).filter(Student.student_id == sid).delete()
        db.commit()
    print("  [OK] Test row cleaned up.")

    print("\n  [PASS] identity.py working correctly.")
    sys.exit(0)
