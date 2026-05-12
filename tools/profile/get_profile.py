#!/usr/bin/env python3
"""Read a student's profile from the database.

Returns a default profile dict if the student has no row (and creates the row).
Resets checkin_done_today if last_active is not today.

Usage:
    from tools.profile.get_profile import get_profile
    profile = get_profile(student_id)
"""

import sys
from datetime import date
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from tools.shared.database import SessionLocal
from tools.shared.models import Student
from tools.shared.audit_log import log

_DEFAULTS = {
    "weak_topics": "[]",
    "missed_findings": "[]",
    "retention_scores": "{}",
    "session_count": "0",
    "streak": "0",
    "last_active": "",
    "learning_velocity": "stable",
    "checkin_done_today": "false",
}

def _default_profile(student_id: str) -> dict:
    return {"student_id": student_id, **_DEFAULTS}

def get_profile(student_id: str) -> dict:
    """
    Return the student's profile dict.
    Resets checkin_done_today if last_active is not today.
    """
    try:
        with SessionLocal() as db:
            student = db.query(Student).filter(Student.student_id == student_id).first()
            if not student:
                return _default_profile(student_id)

            # Reset checkin flag if this is a new day
            last_active_date = student.last_active.date() if student.last_active else None
            if last_active_date and last_active_date != date.today():
                student.checkin_done_today = False
                db.commit()
                db.refresh(student)

            return {
                "student_id": student.student_id,
                "weak_topics": student.weak_topics,
                "missed_findings": student.missed_findings,
                "retention_scores": student.retention_scores,
                "session_count": str(student.session_count),
                "streak": str(student.streak),
                "last_active": student.last_active.isoformat() if student.last_active else "",
                "learning_velocity": student.learning_velocity,
                "checkin_done_today": "true" if student.checkin_done_today else "false",
            }
    except Exception as exc:
        log("profile_read_error", student_id=student_id, feature="profile", detail=str(exc))
        return _default_profile(student_id)
