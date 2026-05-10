#!/usr/bin/env python3
"""Flag students who meet the at-risk threshold:
no login in 5+ days AND 2+ unresolved weak topics.

Usage:
    from tools.supervisor.at_risk import get_at_risk
    students = get_at_risk()
"""

import json
import sys
from datetime import date, timedelta
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from tools.shared.gsheets import get_rows
from tools.shared.audit_log import log

INACTIVE_THRESHOLD_DAYS = 5
WEAK_TOPIC_THRESHOLD = 2


def get_at_risk() -> list[dict]:
    """
    Returns list of dicts:
        {student_id, last_active, days_inactive, weak_topics, weak_count}
    """
    try:
        profiles = get_rows("snec_profiles")
    except Exception as exc:
        log("at_risk_error", feature="supervisor", detail=str(exc))
        return []

    today = date.today()
    at_risk = []

    for p in profiles:
        last_active_str = p.get("last_active", "")
        if not last_active_str:
            continue
        try:
            last = date.fromisoformat(last_active_str)
            days_inactive = (today - last).days
        except ValueError:
            continue

        try:
            weak = json.loads(p.get("weak_topics", "[]") or "[]")
        except (json.JSONDecodeError, TypeError):
            weak = []

        if days_inactive >= INACTIVE_THRESHOLD_DAYS and len(weak) >= WEAK_TOPIC_THRESHOLD:
            at_risk.append({
                "student_id": p["student_id"],
                "last_active": last_active_str,
                "days_inactive": days_inactive,
                "weak_topics": weak,
                "weak_count": len(weak),
            })

    return at_risk
