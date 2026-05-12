#!/usr/bin/env python3
"""Update a student's profile in the database after a session.

Usage:
    from tools.profile.update_profile import update_profile
    update_profile(
        student_id,
        topic="glaucoma",       # optional: topic studied/assessed
        score=0.75,             # optional: 0.0-1.0 retention score for topic
        new_missed_findings=[],  # optional: list of missed clinical findings
        checkin_done=False,     # optional: mark checkin complete
    )
"""

import json
import sys
from datetime import datetime, timezone, timedelta, date
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from tools.profile.get_profile import get_profile
from tools.shared.database import SessionLocal
from tools.shared.models import Student
from tools.shared.audit_log import log

WEAK_THRESHOLD = 0.65

def _calc_velocity(old_scores: dict, new_scores: dict) -> str:
    """Compare average retention before/after to determine learning trend."""
    if not old_scores or not new_scores:
        return "stable"
    old_avg = sum(old_scores.values()) / len(old_scores)
    new_avg = sum(new_scores.values()) / len(new_scores)
    diff = new_avg - old_avg
    if diff > 0.05:
        return "improving"
    if diff < -0.05:
        return "declining"
    return "stable"

def update_profile(
    student_id: str,
    topic: str | None = None,
    score: float | None = None,
    new_missed_findings: list[str] | None = None,
    checkin_done: bool = False,
) -> None:
    try:
        profile = get_profile(student_id)
    except Exception as exc:
        log("profile_update_error", student_id=student_id, feature="profile", detail=str(exc))
        return

    today = date.today()
    now_utc = datetime.now(timezone.utc)

    # Streak
    last_active = profile.get("last_active", "")
    try:
        last = date.fromisoformat(last_active.split("T")[0]) if last_active else None
    except ValueError:
        last = None

    current_streak = int(profile.get("streak", "0") or "0")
    if last is None or last == today:
        new_streak = max(current_streak, 1)
    elif last == today - timedelta(days=1):
        new_streak = current_streak + 1
    else:
        new_streak = 1

    # Retention scores
    try:
        retention = json.loads(profile.get("retention_scores", "{}") or "{}")
    except (json.JSONDecodeError, TypeError):
        retention = {}
    old_retention = dict(retention)

    if topic and score is not None:
        retention[topic] = round(float(score), 3)

    # Weak topics
    weak_topics = [t for t, s in retention.items() if s < WEAK_THRESHOLD]

    # Missed findings
    try:
        findings = json.loads(profile.get("missed_findings", "[]") or "[]")
    except (json.JSONDecodeError, TypeError):
        findings = []
    if new_missed_findings:
        for f in new_missed_findings:
            if f not in findings:
                findings.append(f)

    # Learning velocity
    velocity = _calc_velocity(old_retention, retention)

    # Session count
    session_count = int(profile.get("session_count", "0") or "0") + 1

    try:
        with SessionLocal() as db:
            student = db.query(Student).filter(Student.student_id == student_id).first()
            if student:
                student.session_count = session_count
                student.streak = new_streak
                student.last_active = now_utc
                student.retention_scores = json.dumps(retention)
                student.weak_topics = json.dumps(weak_topics)
                student.missed_findings = json.dumps(findings)
                student.learning_velocity = velocity
                if checkin_done:
                    student.checkin_done_today = True
                db.commit()
    except Exception as exc:
        log("profile_write_error", student_id=student_id, feature="profile", detail=str(exc))
