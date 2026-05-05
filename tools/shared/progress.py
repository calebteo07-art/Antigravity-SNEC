#!/usr/bin/env python3
"""Student progress tracking — XP, levels, and badges for the case simulator."""

import json
import sys
from datetime import date
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# ─── Level thresholds: (min_xp, display_name, icon) ──────────────────────────
LEVELS = [
    (0,     "Med Student",      "🎓"),
    (500,   "House Officer",    "👨‍⚕️"),
    (1200,  "Medical Officer",  "🩺"),
    (2500,  "Registrar",        "📋"),
    (5000,  "Senior Registrar", "⭐"),
    (9000,  "Fellow",           "🏆"),
    (15000, "Consultant",       "👑"),
]

# ─── Badge registry: key → (display_name, emoji, description) ────────────────
BADGES: dict[str, tuple[str, str, str]] = {
    "first_case":             ("First Diagnosis",     "🏥", "Completed your very first clinical case"),
    "perfect_history":        ("Perfect Historian",   "📝", "Scored 10/10 on the history domain"),
    "perfect_investigations": ("Sharp Investigator",  "🔬", "Scored 10/10 on investigations"),
    "perfect_diagnosis":      ("Diagnostician",       "🎯", "Scored 10/10 on diagnosis"),
    "perfect_management":     ("Treatment Maestro",   "💊", "Scored 10/10 on management"),
    "perfect_case":           ("Flawless",            "✨", "Achieved a perfect 40/40 score"),
    "speed_demon":            ("Speed Demon",         "⚡", "Solved a case in 8 or fewer exchanges"),
    "veteran":                ("Case Veteran",        "🎖️", "Completed 5 or more cases"),
    "no_hints":               ("Unsupported",         "🧠", "Solved a case without using any hints"),
}


def get_level_info(total_xp: int) -> dict:
    """Return the student's current level and progress toward the next one."""
    current_idx = 0
    for i, (threshold, _, __) in enumerate(LEVELS):
        if total_xp >= threshold:
            current_idx = i

    threshold, name, icon = LEVELS[current_idx]
    next_idx = current_idx + 1

    if next_idx < len(LEVELS):
        next_threshold, next_name, _ = LEVELS[next_idx]
        xp_into_level = total_xp - threshold
        xp_span = next_threshold - threshold
        progress_pct = min(1.0, xp_into_level / xp_span)
        xp_to_next = next_threshold - total_xp
    else:
        next_threshold = None
        next_name = "Max level"
        xp_to_next = 0
        progress_pct = 1.0

    return {
        "level_num": current_idx + 1,
        "name": name,
        "icon": icon,
        "threshold": threshold,
        "next_threshold": next_threshold,
        "next_name": next_name,
        "xp_to_next": xp_to_next,
        "progress_pct": progress_pct,
    }


def calculate_xp_reward(
    result: dict,
    message_count: int,
    is_first_case: bool,
    hints_used: int,
    cases_completed: int,
) -> dict:
    """
    Calculate XP earned for a completed case.

    Returns:
        {base_xp, bonuses [(name, xp)], penalties [(name, xp)], total_xp, new_badges [str]}
    """
    total_score = int(result.get("total_score", 0))
    h   = int(result.get("history_score", 0))
    inv = int(result.get("investigations_score", 0))
    d   = int(result.get("diagnosis_score", 0))
    m   = int(result.get("management_score", 0))

    base_xp  = total_score * 10   # 0–400
    bonuses  = []
    penalties = []
    new_badges: list[str] = []

    # Perfect domain bonuses
    if h == 10:
        bonuses.append(("Perfect History", 50))
        new_badges.append("perfect_history")
    if inv == 10:
        bonuses.append(("Perfect Investigations", 50))
        new_badges.append("perfect_investigations")
    if d == 10:
        bonuses.append(("Perfect Diagnosis", 50))
        new_badges.append("perfect_diagnosis")
    if m == 10:
        bonuses.append(("Perfect Management", 50))
        new_badges.append("perfect_management")

    # Perfect case
    if total_score == 40:
        bonuses.append(("Flawless Case!", 200))
        new_badges.append("perfect_case")

    # First case ever
    if is_first_case:
        bonuses.append(("First Case Bonus", 100))
        new_badges.append("first_case")

    # Speed: ≤8 student messages
    if message_count <= 8:
        bonuses.append(("Speed Demon (≤8 turns)", 75))
        new_badges.append("speed_demon")

    # Veteran: 5+ cases completed after this one
    if cases_completed + 1 >= 5:
        new_badges.append("veteran")

    # No hints bonus
    if hints_used == 0:
        new_badges.append("no_hints")

    # Hint penalty
    if hints_used > 0:
        pen = hints_used * 20
        penalties.append((f"{hints_used} hint(s) used", -pen))

    bonus_total   = sum(b[1] for b in bonuses)
    penalty_total = sum(p[1] for p in penalties)
    total_xp      = max(0, base_xp + bonus_total + penalty_total)

    return {
        "base_xp":   base_xp,
        "bonuses":   bonuses,
        "penalties": penalties,
        "total_xp":  total_xp,
        "new_badges": new_badges,
    }


def get_progress(student_id: str) -> dict:
    """Fetch student progress from Google Sheets. Returns zeroed defaults if not found."""
    default = {
        "student_id":      student_id,
        "total_xp":        0,
        "cases_completed": 0,
        "badges":          [],
        "last_case_date":  "",
        "streak_days":     0,
    }
    try:
        from tools.shared.gsheets import get_rows
        rows = get_rows("snec_progress", {"student_id": student_id})
        if rows:
            row = rows[0]
            raw = row.get("badges", "[]")
            try:
                badges = json.loads(raw) if raw else []
            except (json.JSONDecodeError, TypeError):
                badges = []
            return {
                "student_id":      student_id,
                "total_xp":        int(row.get("total_xp", 0) or 0),
                "cases_completed": int(row.get("cases_completed", 0) or 0),
                "badges":          badges,
                "last_case_date":  row.get("last_case_date", ""),
                "streak_days":     int(row.get("streak_days", 0) or 0),
            }
    except Exception:
        pass
    return default


def update_progress(student_id: str, xp_earned: int, new_badges: list[str]) -> dict:
    """Add XP and new badges to the student's record. Returns the updated progress."""
    current = get_progress(student_id)

    all_badges = list(set(current["badges"] + new_badges))

    # Streak logic
    today = date.today().isoformat()
    last  = current.get("last_case_date", "")
    streak = int(current.get("streak_days", 0))
    if last == today:
        pass
    elif last:
        try:
            delta = (date.today() - date.fromisoformat(last)).days
            streak = streak + 1 if delta == 1 else 1
        except ValueError:
            streak = 1
    else:
        streak = 1

    new_total_xp = current["total_xp"] + xp_earned
    new_cases    = current["cases_completed"] + 1

    updated = {
        "student_id":      student_id,
        "total_xp":        new_total_xp,
        "cases_completed": new_cases,
        "badges":          all_badges,
        "last_case_date":  today,
        "streak_days":     streak,
    }

    try:
        from tools.shared.gsheets import get_rows, append_row, update_row
        rows = get_rows("snec_progress", {"student_id": student_id})
        row_data = {
            "student_id":      student_id,
            "total_xp":        str(new_total_xp),
            "cases_completed": str(new_cases),
            "badges":          json.dumps(all_badges),
            "last_case_date":  today,
            "streak_days":     str(streak),
        }
        if rows:
            update_row("snec_progress", "student_id", student_id, row_data)
        else:
            append_row("snec_progress", row_data)
    except Exception:
        pass

    return updated
