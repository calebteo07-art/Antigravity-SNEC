#!/usr/bin/env python3
"""Format a student's gap context string for injection into the AI system prompt.

Usage:
    from tools.profile.summarize_gaps import summarize_gaps
    context = summarize_gaps(profile)  # returns "" if no gaps
"""

import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


def summarize_gaps(profile: dict) -> str:
    """
    Return a 1-3 sentence gap context string, or "" if the student has no gaps.

    This string is prepended to the AI system prompt so the tutor can redirect
    toward weak areas during normal conversation.
    """
    try:
        weak = json.loads(profile.get("weak_topics", "[]") or "[]")
        findings = json.loads(profile.get("missed_findings", "[]") or "[]")
        scores = json.loads(profile.get("retention_scores", "{}") or "{}")
    except (json.JSONDecodeError, TypeError):
        return ""

    if not weak and not findings:
        return ""

    parts = []

    if weak:
        topic_list = ", ".join(weak[:3])
        score_detail = "; ".join(
            f"{t}: {scores.get(t, 0):.0%}" for t in weak[:3] if t in scores
        )
        parts.append(f"Student is weak on: {topic_list}.")
        if score_detail:
            parts.append(f"Retention scores — {score_detail}.")

    if findings:
        finding_list = ", ".join(findings[:3])
        parts.append(f"Consistently misses: {finding_list}.")

    if weak:
        parts.append(f"Where natural, redirect toward {weak[0]} to reinforce understanding.")

    return " ".join(parts)
