#!/usr/bin/env python3
"""Aggregate all student profiles into cohort-level statistics.

Usage:
    from tools.supervisor.cohort_summary import cohort_summary
    summary = cohort_summary()
"""

import json
import sys
from collections import Counter
from datetime import date, timedelta
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from tools.shared.gsheets import get_rows
from tools.shared.audit_log import log


def cohort_summary() -> dict:
    """
    Returns:
        {
            "total": int,
            "active_this_week": int,
            "inactive_7_plus_days": list[dict],  # {student_id, last_active, days_inactive}
            "weakest_topics": list[str],           # top 3 by frequency across all profiles
            "at_risk_count": int,
        }
    """
    try:
        profiles = get_rows("snec_profiles")
    except Exception as exc:
        log("cohort_summary_error", feature="supervisor", detail=str(exc))
        return {
            "total": 0, "active_this_week": 0,
            "inactive_7_plus_days": [], "weakest_topics": [], "at_risk_count": 0,
        }

    today = date.today()
    active_this_week = 0
    inactive_7_plus = []
    topic_counter: Counter = Counter()
    at_risk_count = 0

    for p in profiles:
        last_active_str = p.get("last_active", "")
        days_inactive = None
        if last_active_str:
            try:
                last = date.fromisoformat(last_active_str)
                days_inactive = (today - last).days
                if days_inactive < 7:
                    active_this_week += 1
                else:
                    inactive_7_plus.append({
                        "student_id": p["student_id"],
                        "last_active": last_active_str,
                        "days_inactive": days_inactive,
                    })
            except ValueError:
                pass

        try:
            weak = json.loads(p.get("weak_topics", "[]") or "[]")
        except (json.JSONDecodeError, TypeError):
            weak = []

        topic_counter.update(weak)

        # At-risk: 5+ days inactive AND 2+ weak topics
        if days_inactive is not None and days_inactive >= 5 and len(weak) >= 2:
            at_risk_count += 1

    weakest = [topic for topic, _ in topic_counter.most_common(3)]

    return {
        "total": len(profiles),
        "active_this_week": active_this_week,
        "inactive_7_plus_days": inactive_7_plus,
        "weakest_topics": weakest,
        "at_risk_count": at_risk_count,
    }
