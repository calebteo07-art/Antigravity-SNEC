# EyeQ World-Class Features Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement the full EyeQ world-class spec: persistent student profiles, adaptive Socratic AI, daily check-in, post-case debrief, supervisor tools, and supervisor dashboard.

**Architecture:** A `StudentProfile` row in `snec_profiles` Google Sheet grows with every session. Every AI call reads the profile and injects weak-topic context. The supervisor layer reads aggregated profiles to surface cohort health. No existing features are rewritten — they gain profile read/write wrappers.

**Tech Stack:** Python 3.11, FastAPI, gspread (Google Sheets), google-genai (Gemini), React, TypeScript, Tailwind CSS, motion/react, lucide-react.

---

## File Map

**New backend files:**
- `tools/profile/__init__.py`
- `tools/profile/bootstrap_sheets.py` — creates `snec_profiles`, `snec_supervisors`, `snec_supervisor_alerts` sheets
- `tools/profile/get_profile.py` — reads student profile, resets checkin flag on new day
- `tools/profile/update_profile.py` — writes profile after sessions
- `tools/profile/summarize_gaps.py` — formats gap context string for AI injection
- `tools/supervisor/__init__.py`
- `tools/supervisor/cohort_summary.py` — aggregates all profiles into cohort stats
- `tools/supervisor/at_risk.py` — flags students with 5+ inactive days + 2+ weak topics
- `tools/supervisor/activity_report.py` — weekly report: writes to Sheets + emails supervisors
- `tests/profile/__init__.py`
- `tests/profile/test_get_profile.py`
- `tests/profile/test_update_profile.py`
- `tests/profile/test_summarize_gaps.py`
- `tests/supervisor/__init__.py`
- `tests/supervisor/test_cohort_summary.py`
- `tests/supervisor/test_at_risk.py`

**Modified backend files:**
- `workflows/ophthalmology_kb.md` — add Socratic instruction block
- `tools/shared/claude_client.py` — add mock responses for `"checkin"` and `"debrief"` features
- `tools/api/server.py` — gap injection in `/api/chat`, debrief in `/api/cases/{id}/submit`, profile writes in `/api/end-session`, new check-in endpoints, new supervisor endpoints, role in `OnboardResponse`
- `.env.template` — add `GMAIL_USER`, `GMAIL_APP_PASSWORD`, `GOOGLE_SPREADSHEET_ID` notes

**New frontend files:**
- `frontend/src/app/components/DailyCheckInScreen.tsx`
- `frontend/src/app/components/SupervisorDashboard.tsx`
- `frontend/src/app/components/CohortHeatmap.tsx`
- `frontend/src/app/components/AtRiskTable.tsx`
- `frontend/src/app/components/StudentDrillDown.tsx`

**Modified frontend files:**
- `frontend/src/app/routes.tsx` — add `/checkin`, `/supervisor` routes
- `frontend/src/app/components/DashboardScreen.tsx` — check-in gate on load
- `frontend/src/app/components/OnboardingScreen.tsx` — route supervisor to `/supervisor`
- `frontend/src/app/components/CaseSessionScreen.tsx` — show debrief section after results

---

## Task 1: Bootstrap new Google Sheets

**Files:**
- Create: `tools/profile/bootstrap_sheets.py`
- Create: `tools/profile/__init__.py`

- [ ] **Step 1: Write the failing test**

Create `tests/profile/__init__.py` (empty) and `tests/profile/test_bootstrap.py`:

```python
# tests/profile/__init__.py
# (empty)
```

```python
# tests/profile/test_bootstrap.py
import pytest
from unittest.mock import MagicMock, patch


def test_ensure_sheet_creates_if_missing():
    mock_spreadsheet = MagicMock()
    mock_spreadsheet.worksheet.side_effect = Exception("WorksheetNotFound")
    mock_spreadsheet.add_worksheet.return_value = MagicMock()

    from tools.profile.bootstrap_sheets import ensure_sheet
    with patch("tools.profile.bootstrap_sheets._get_spreadsheet", return_value=mock_spreadsheet):
        ensure_sheet("test_sheet", ["col_a", "col_b"])

    mock_spreadsheet.add_worksheet.assert_called_once()


def test_ensure_sheet_skips_if_exists():
    mock_ws = MagicMock()
    mock_spreadsheet = MagicMock()
    mock_spreadsheet.worksheet.return_value = mock_ws

    from tools.profile.bootstrap_sheets import ensure_sheet
    with patch("tools.profile.bootstrap_sheets._get_spreadsheet", return_value=mock_spreadsheet):
        ensure_sheet("test_sheet", ["col_a", "col_b"])

    mock_spreadsheet.add_worksheet.assert_not_called()
```

- [ ] **Step 2: Run test to verify it fails**

```
pytest tests/profile/test_bootstrap.py -v
```
Expected: `ModuleNotFoundError` for `tools.profile.bootstrap_sheets`

- [ ] **Step 3: Create `tools/profile/__init__.py`**

```python
# tools/profile/__init__.py
# (empty)
```

- [ ] **Step 4: Write `tools/profile/bootstrap_sheets.py`**

```python
#!/usr/bin/env python3
"""Create the snec_profiles, snec_supervisors, and snec_supervisor_alerts sheets
if they do not already exist in the project spreadsheet.

Run once during setup:
    python tools/profile/bootstrap_sheets.py
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from tools.shared.gsheets import _get_spreadsheet

SHEETS = {
    "snec_profiles": [
        "student_id", "weak_topics", "missed_findings", "retention_scores",
        "session_count", "streak", "last_active", "learning_velocity", "checkin_done_today",
    ],
    "snec_supervisors": [
        "supervisor_id", "email", "cohort", "role",
    ],
    "snec_supervisor_alerts": [
        "week_start", "active_students", "inactive_students", "weakest_topics",
        "at_risk_count", "report_json",
    ],
}


def ensure_sheet(name: str, headers: list[str]) -> None:
    spreadsheet = _get_spreadsheet()
    try:
        spreadsheet.worksheet(name)
        print(f"  [skip] '{name}' already exists.")
    except Exception:
        ws = spreadsheet.add_worksheet(title=name, rows=1000, cols=len(headers))
        ws.append_row(headers, value_input_option="RAW")
        print(f"  [created] '{name}' with {len(headers)} columns.")


if __name__ == "__main__":
    print("Bootstrapping EyeQ profile sheets...\n")
    for sheet_name, cols in SHEETS.items():
        ensure_sheet(sheet_name, cols)
    print("\nDone.")
```

- [ ] **Step 5: Run test to verify it passes**

```
pytest tests/profile/test_bootstrap.py -v
```
Expected: PASS

- [ ] **Step 6: Commit**

```bash
git add tools/profile/__init__.py tools/profile/bootstrap_sheets.py tests/profile/__init__.py tests/profile/test_bootstrap.py
git commit -m "feat: add profile sheet bootstrap script"
```

---

## Task 2: get_profile.py

**Files:**
- Create: `tools/profile/get_profile.py`
- Create: `tests/profile/test_get_profile.py`

The function reads from `snec_profiles`. If the student has no row, it creates a default profile row and returns it. It also resets `checkin_done_today` to `"false"` if `last_active` is not today.

- [ ] **Step 1: Write the failing test**

```python
# tests/profile/test_get_profile.py
import pytest
from datetime import date
from unittest.mock import patch


def _make_profile(**kwargs):
    defaults = {
        "student_id": "stu-001",
        "weak_topics": "[]",
        "missed_findings": "[]",
        "retention_scores": "{}",
        "session_count": "0",
        "streak": "0",
        "last_active": "",
        "learning_velocity": "stable",
        "checkin_done_today": "false",
    }
    defaults.update(kwargs)
    return defaults


def test_get_profile_returns_existing_row():
    profile_row = _make_profile(student_id="stu-001", streak="3")
    with patch("tools.profile.get_profile.get_rows", return_value=[profile_row]):
        from tools.profile.get_profile import get_profile
        result = get_profile("stu-001")
    assert result["streak"] == "3"


def test_get_profile_creates_default_when_missing():
    with patch("tools.profile.get_profile.get_rows", return_value=[]), \
         patch("tools.profile.get_profile.append_row") as mock_append, \
         patch("tools.profile.get_profile.update_row"):
        from tools.profile.get_profile import get_profile
        result = get_profile("stu-new")
    assert result["student_id"] == "stu-new"
    assert result["session_count"] == "0"
    mock_append.assert_called_once()


def test_get_profile_resets_checkin_on_new_day():
    yesterday = "2026-05-09"
    profile_row = _make_profile(
        student_id="stu-001",
        last_active=yesterday,
        checkin_done_today="true",
    )
    with patch("tools.profile.get_profile.get_rows", return_value=[profile_row]), \
         patch("tools.profile.get_profile.update_row") as mock_update, \
         patch("tools.profile.get_profile.date") as mock_date:
        mock_date.today.return_value = date(2026, 5, 10)
        mock_date.fromisoformat = date.fromisoformat
        from tools.profile.get_profile import get_profile
        result = get_profile("stu-001")
    mock_update.assert_called_once()
    assert result["checkin_done_today"] == "false"


def test_get_profile_does_not_reset_checkin_same_day():
    today = "2026-05-10"
    profile_row = _make_profile(
        student_id="stu-001",
        last_active=today,
        checkin_done_today="true",
    )
    with patch("tools.profile.get_profile.get_rows", return_value=[profile_row]), \
         patch("tools.profile.get_profile.update_row") as mock_update, \
         patch("tools.profile.get_profile.date") as mock_date:
        mock_date.today.return_value = date(2026, 5, 10)
        mock_date.fromisoformat = date.fromisoformat
        from tools.profile.get_profile import get_profile
        result = get_profile("stu-001")
    mock_update.assert_not_called()
    assert result["checkin_done_today"] == "true"


def test_get_profile_returns_default_on_sheet_error():
    with patch("tools.profile.get_profile.get_rows", side_effect=RuntimeError("no sheet")):
        from tools.profile.get_profile import get_profile
        result = get_profile("stu-broken")
    assert result["student_id"] == "stu-broken"
    assert result["session_count"] == "0"
```

- [ ] **Step 2: Run test to verify it fails**

```
pytest tests/profile/test_get_profile.py -v
```
Expected: `ImportError` — module not found

- [ ] **Step 3: Write `tools/profile/get_profile.py`**

```python
#!/usr/bin/env python3
"""Read a student's profile from the snec_profiles Google Sheet.

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

from tools.shared.gsheets import get_rows, append_row, update_row
from tools.shared.audit_log import log

SHEET = "snec_profiles"

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
    Return the student's profile dict. Creates a default row if missing.
    Resets checkin_done_today if last_active is not today.

    Never raises — returns a default profile on any Sheets error.
    """
    try:
        rows = get_rows(SHEET, filters={"student_id": student_id})
    except Exception as exc:
        log("profile_read_error", student_id=student_id, feature="profile", detail=str(exc))
        return _default_profile(student_id)

    if not rows:
        profile = _default_profile(student_id)
        try:
            append_row(SHEET, profile)
        except Exception as exc:
            log("profile_create_error", student_id=student_id, feature="profile", detail=str(exc))
        return profile

    profile = rows[0]

    # Reset checkin flag if this is a new day
    last_active_str = profile.get("last_active", "")
    if last_active_str:
        try:
            last_active_date = date.fromisoformat(last_active_str)
            if last_active_date != date.today():
                profile["checkin_done_today"] = "false"
                try:
                    update_row(SHEET, "student_id", student_id, {"checkin_done_today": "false"})
                except Exception as exc:
                    log("profile_reset_error", student_id=student_id, feature="profile", detail=str(exc))
        except ValueError:
            pass

    return profile
```

- [ ] **Step 4: Run tests to verify they pass**

```
pytest tests/profile/test_get_profile.py -v
```
Expected: all PASS

- [ ] **Step 5: Commit**

```bash
git add tools/profile/get_profile.py tests/profile/test_get_profile.py
git commit -m "feat: add get_profile tool"
```

---

## Task 3: update_profile.py

**Files:**
- Create: `tools/profile/update_profile.py`
- Create: `tests/profile/test_update_profile.py`

Updates streak, session_count, last_active, retention_scores (if topic+score given), weak_topics (retention < 0.65), missed_findings, learning_velocity, and checkin_done_today.

- [ ] **Step 1: Write the failing test**

```python
# tests/profile/test_update_profile.py
import json
import pytest
from datetime import date
from unittest.mock import patch, MagicMock


def _profile(**kwargs):
    defaults = {
        "student_id": "stu-001",
        "weak_topics": "[]",
        "missed_findings": "[]",
        "retention_scores": "{}",
        "session_count": "2",
        "streak": "1",
        "last_active": "2026-05-09",
        "learning_velocity": "stable",
        "checkin_done_today": "false",
    }
    defaults.update(kwargs)
    return defaults


def test_update_profile_increments_session_count():
    profile = _profile()
    with patch("tools.profile.update_profile.get_profile", return_value=profile), \
         patch("tools.profile.update_profile.update_row") as mock_update, \
         patch("tools.profile.update_profile.date") as mock_date:
        mock_date.today.return_value = date(2026, 5, 10)
        mock_date.fromisoformat = date.fromisoformat
        from tools.profile.update_profile import update_profile
        update_profile("stu-001")
    call_kwargs = mock_update.call_args[0][3]
    assert call_kwargs["session_count"] == "3"


def test_update_profile_increments_streak_from_yesterday():
    profile = _profile(last_active="2026-05-09", streak="4")
    with patch("tools.profile.update_profile.get_profile", return_value=profile), \
         patch("tools.profile.update_profile.update_row") as mock_update, \
         patch("tools.profile.update_profile.date") as mock_date:
        mock_date.today.return_value = date(2026, 5, 10)
        mock_date.fromisoformat = date.fromisoformat
        from tools.profile.update_profile import update_profile
        update_profile("stu-001")
    call_kwargs = mock_update.call_args[0][3]
    assert call_kwargs["streak"] == "5"


def test_update_profile_resets_streak_after_gap():
    profile = _profile(last_active="2026-05-07", streak="10")
    with patch("tools.profile.update_profile.get_profile", return_value=profile), \
         patch("tools.profile.update_profile.update_row") as mock_update, \
         patch("tools.profile.update_profile.date") as mock_date:
        mock_date.today.return_value = date(2026, 5, 10)
        mock_date.fromisoformat = date.fromisoformat
        from tools.profile.update_profile import update_profile
        update_profile("stu-001")
    call_kwargs = mock_update.call_args[0][3]
    assert call_kwargs["streak"] == "1"


def test_update_profile_updates_retention_scores():
    profile = _profile(retention_scores='{"glaucoma": 0.8}')
    with patch("tools.profile.update_profile.get_profile", return_value=profile), \
         patch("tools.profile.update_profile.update_row") as mock_update, \
         patch("tools.profile.update_profile.date") as mock_date:
        mock_date.today.return_value = date(2026, 5, 10)
        mock_date.fromisoformat = date.fromisoformat
        from tools.profile.update_profile import update_profile
        update_profile("stu-001", topic="retina", score=0.5)
    call_kwargs = mock_update.call_args[0][3]
    scores = json.loads(call_kwargs["retention_scores"])
    assert scores["retina"] == 0.5
    assert scores["glaucoma"] == 0.8


def test_update_profile_marks_weak_topics():
    profile = _profile(retention_scores='{"glaucoma": 0.8, "retina": 0.4}')
    with patch("tools.profile.update_profile.get_profile", return_value=profile), \
         patch("tools.profile.update_profile.update_row") as mock_update, \
         patch("tools.profile.update_profile.date") as mock_date:
        mock_date.today.return_value = date(2026, 5, 10)
        mock_date.fromisoformat = date.fromisoformat
        from tools.profile.update_profile import update_profile
        update_profile("stu-001")
    call_kwargs = mock_update.call_args[0][3]
    weak = json.loads(call_kwargs["weak_topics"])
    assert "retina" in weak
    assert "glaucoma" not in weak


def test_update_profile_appends_missed_findings():
    profile = _profile(missed_findings='["disc haemorrhage"]')
    with patch("tools.profile.update_profile.get_profile", return_value=profile), \
         patch("tools.profile.update_profile.update_row") as mock_update, \
         patch("tools.profile.update_profile.date") as mock_date:
        mock_date.today.return_value = date(2026, 5, 10)
        mock_date.fromisoformat = date.fromisoformat
        from tools.profile.update_profile import update_profile
        update_profile("stu-001", new_missed_findings=["RNFL thinning"])
    call_kwargs = mock_update.call_args[0][3]
    findings = json.loads(call_kwargs["missed_findings"])
    assert "disc haemorrhage" in findings
    assert "RNFL thinning" in findings


def test_update_profile_noop_on_sheet_error():
    with patch("tools.profile.update_profile.get_profile", side_effect=RuntimeError("no sheet")):
        from tools.profile.update_profile import update_profile
        update_profile("stu-001")  # must not raise
```

- [ ] **Step 2: Run test to verify it fails**

```
pytest tests/profile/test_update_profile.py -v
```
Expected: `ImportError`

- [ ] **Step 3: Write `tools/profile/update_profile.py`**

```python
#!/usr/bin/env python3
"""Update a student's profile in the snec_profiles Google Sheet after a session.

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
from datetime import date, timedelta
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from tools.profile.get_profile import get_profile
from tools.shared.gsheets import update_row
from tools.shared.audit_log import log

SHEET = "snec_profiles"
WEAK_THRESHOLD = 0.65


def _calc_streak(last_active_str: str, today: date) -> int:
    if not last_active_str:
        return 1
    try:
        last = date.fromisoformat(last_active_str)
    except ValueError:
        return 1
    if last == today:
        return None  # already counted today — don't change
    if last == today - timedelta(days=1):
        return None  # will be incremented by caller
    return 1  # streak broken


def _calc_velocity(old_scores: dict, new_scores: dict) -> str:
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
    """
    Update the student's profile. Never raises — logs errors to audit_log.
    """
    try:
        profile = get_profile(student_id)
    except Exception as exc:
        log("profile_update_error", student_id=student_id, feature="profile", detail=str(exc))
        return

    today = date.today()
    today_str = today.isoformat()

    # Streak
    last_active = profile.get("last_active", "")
    try:
        last = date.fromisoformat(last_active) if last_active else None
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

    updates = {
        "session_count": str(session_count),
        "streak": str(new_streak),
        "last_active": today_str,
        "retention_scores": json.dumps(retention),
        "weak_topics": json.dumps(weak_topics),
        "missed_findings": json.dumps(findings),
        "learning_velocity": velocity,
    }
    if checkin_done:
        updates["checkin_done_today"] = "true"

    try:
        update_row(SHEET, "student_id", student_id, updates)
    except Exception as exc:
        log("profile_write_error", student_id=student_id, feature="profile", detail=str(exc))
```

- [ ] **Step 4: Run tests to verify they pass**

```
pytest tests/profile/test_update_profile.py -v
```
Expected: all PASS

- [ ] **Step 5: Commit**

```bash
git add tools/profile/update_profile.py tests/profile/test_update_profile.py
git commit -m "feat: add update_profile tool"
```

---

## Task 4: summarize_gaps.py

**Files:**
- Create: `tools/profile/summarize_gaps.py`
- Create: `tests/profile/test_summarize_gaps.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/profile/test_summarize_gaps.py
import json
from tools.profile.summarize_gaps import summarize_gaps


def test_summarize_gaps_empty_profile():
    profile = {
        "weak_topics": "[]",
        "missed_findings": "[]",
        "retention_scores": "{}",
    }
    result = summarize_gaps(profile)
    assert result == ""


def test_summarize_gaps_with_weak_topics():
    profile = {
        "weak_topics": '["glaucoma", "retina"]',
        "missed_findings": "[]",
        "retention_scores": '{"glaucoma": 0.4, "retina": 0.5}',
    }
    result = summarize_gaps(profile)
    assert "glaucoma" in result
    assert "retina" in result
    assert "weak" in result.lower()


def test_summarize_gaps_with_missed_findings():
    profile = {
        "weak_topics": "[]",
        "missed_findings": '["disc haemorrhage", "RNFL thinning"]',
        "retention_scores": "{}",
    }
    result = summarize_gaps(profile)
    assert "disc haemorrhage" in result
    assert "RNFL thinning" in result


def test_summarize_gaps_full_profile():
    profile = {
        "weak_topics": '["glaucoma"]',
        "missed_findings": '["disc haemorrhage"]',
        "retention_scores": '{"glaucoma": 0.4}',
    }
    result = summarize_gaps(profile)
    assert "glaucoma" in result
    assert "disc haemorrhage" in result
    assert len(result) > 20
```

- [ ] **Step 2: Run test to verify it fails**

```
pytest tests/profile/test_summarize_gaps.py -v
```
Expected: `ImportError`

- [ ] **Step 3: Write `tools/profile/summarize_gaps.py`**

```python
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
```

- [ ] **Step 4: Run tests to verify they pass**

```
pytest tests/profile/test_summarize_gaps.py -v
```
Expected: all PASS

- [ ] **Step 5: Commit**

```bash
git add tools/profile/summarize_gaps.py tests/profile/test_summarize_gaps.py
git commit -m "feat: add summarize_gaps tool"
```

---

## Task 5: Socratic KB + gap injection + profile writes

**Files:**
- Modify: `workflows/ophthalmology_kb.md` (add Socratic block after Role section)
- Modify: `tools/shared/claude_client.py` (add mock responses)
- Modify: `tools/api/server.py` (gap injection in `/api/chat`, profile writes in `/api/end-session` and `/api/cases/{id}/submit`)

- [ ] **Step 1: Add Socratic instruction block to `workflows/ophthalmology_kb.md`**

Insert this block directly after the `## Role` section (after the line "If a question is outside ophthalmology, redirect the student politely."):

```markdown
## Socratic Teaching Mode

When responding to students:
- Never give the answer directly. Ask one focused follow-up question that makes the student reason aloud first.
- After the student answers correctly, introduce a harder related question before moving on.
- When a natural bridge exists, steer toward the student's weak topics (listed above in the gap context, if present).
- Keep questions specific and clinical — not vague ("What do you think?") but targeted ("What would you expect to find on gonioscopy in this patient?").

---
```

- [ ] **Step 2: Add mock responses to `tools/shared/claude_client.py`**

In `_MOCK_RESPONSES`, add entries for `"checkin"` and `"debrief"`:

```python
    "checkin": (
        "What is the most common cause of painless, gradual visual field loss in a 65-year-old?"
    ),
    "debrief": (
        "**What you got right:** Correctly identified the presenting symptom as insidious peripheral vision loss. "
        "Good history of family risk factors.\n\n"
        "**What you missed:** Did not ask about medication history (steroids can cause secondary glaucoma). "
        "Investigation plan lacked pachymetry.\n\n"
        "**Why it matters clinically:** Corneal thickness affects IOP measurement accuracy — thin corneas underestimate IOP.\n\n"
        "**Focus for next time:** Review the full glaucoma investigation panel: HVF, OCT RNFL, gonioscopy, pachymetry."
    ),
```

- [ ] **Step 3: Add gap injection to `/api/chat` in `tools/api/server.py`**

Add imports at the top of `server.py` (after the existing imports):

```python
from tools.profile.get_profile import get_profile
from tools.profile.update_profile import update_profile
from tools.profile.summarize_gaps import summarize_gaps
```

Replace the existing `/api/chat` endpoint:

```python
@app.post("/api/chat", response_model=ChatResponse)
def chat(body: ChatRequest):
    messages = [{"role": m.role, "content": m.content} for m in body.messages]

    system_prompt = _kb()
    try:
        profile = get_profile(body.student_id)
        gap_context = summarize_gaps(profile)
        if gap_context:
            system_prompt = f"## Student Context\n{gap_context}\n\n---\n\n{system_prompt}"
    except Exception:
        pass  # proceed with base prompt

    raw = ask(
        system_prompt=system_prompt,
        messages=messages,
        max_tokens=1024,
        feature="chatbot",
        model=MODEL,
    )

    return ChatResponse(**_parse_tutor_response(raw))
```

- [ ] **Step 4: Add profile write to `/api/end-session`**

Replace the existing `end_session` function:

```python
@app.post("/api/end-session", response_model=EndSessionResponse)
def end_session(body: EndSessionRequest):
    messages = [{"role": m.role, "content": m.content} for m in body.messages]
    model_name = "mock" if MOCK_MODE else MODEL

    session_id = log_session(
        student_id=body.student_id,
        topic=body.topic,
        messages=messages,
        token_count=body.token_count,
        model=model_name,
    )

    cards = generate_and_return_cards(
        student_id=body.student_id,
        session_id=session_id,
        messages=messages,
    )

    try:
        update_profile(body.student_id)
    except Exception:
        pass

    return EndSessionResponse(
        session_id=session_id,
        cards=[Flashcard(**c) for c in cards],
        mock_mode=MOCK_MODE,
    )
```

- [ ] **Step 5: Add profile write to `/api/cases/{case_id}/submit`**

Replace the existing `case_submit` function:

```python
@app.post("/api/cases/{case_id}/submit", response_model=CaseSubmitResponse)
def case_submit(case_id: str, body: CaseSubmitRequest):
    try:
        case = load_case(case_id)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Case '{case_id}' not found")

    messages = [{"role": m.role, "content": m.content} for m in body.messages]
    messages.append({
        "role": "user",
        "content": f"Diagnosis: {body.diagnosis}\nManagement Plan: {body.management_plan}",
    })

    raw_result = evaluate_case(case, messages, body.student_id)

    session_id = log_session(
        student_id=body.student_id,
        topic=f"Case: {case['title']}",
        messages=messages,
        token_count=0,
        model="mock" if MOCK_MODE else MODEL,
    )
    cards = generate_and_return_cards(
        student_id=body.student_id,
        session_id=session_id,
        messages=messages,
    )

    # Update profile: retention score = total_score / 40
    try:
        retention_score = raw_result.get("total_score", 0) / 40
        missed = []
        for domain in ("history_feedback", "investigations_feedback", "diagnosis_feedback", "management_feedback"):
            feedback = raw_result.get(domain, "")
            if feedback and any(word in feedback.lower() for word in ("miss", "forgot", "lack", "no mention")):
                missed.append(f"{domain.replace('_feedback', '')} gap in {case['topic']}")
        update_profile(
            body.student_id,
            topic=case["topic"],
            score=retention_score,
            new_missed_findings=missed,
        )
    except Exception:
        pass

    return CaseSubmitResponse(
        result=DomainScore(**{k: raw_result[k] for k in DomainScore.model_fields}),
        cards=[Flashcard(**c) for c in cards],
        mock_mode=MOCK_MODE,
    )
```

- [ ] **Step 6: Verify server starts without error**

```
cd C:\Users\caleb\OneDrive\Desktop\SNEC_AI_CHATBOT
uvicorn tools.api.server:app --reload --port 8000
```
Expected: server starts, no import errors. Press Ctrl+C.

- [ ] **Step 7: Run existing tests to confirm nothing broke**

```
pytest tests/ -v
```
Expected: all prior tests still PASS

- [ ] **Step 8: Commit**

```bash
git add workflows/ophthalmology_kb.md tools/shared/claude_client.py tools/api/server.py
git commit -m "feat: add socratic KB, gap context injection, and profile writes"
```

---

## Task 6: Post-case debrief

**Files:**
- Modify: `tools/api/server.py` — add debrief AI call + field to `CaseSubmitResponse`
- Modify: `frontend/src/app/components/CaseSessionScreen.tsx` — display debrief section

- [ ] **Step 1: Add `debrief` to `CaseSubmitResponse` and generate it in `case_submit`**

In `server.py`, update `CaseSubmitResponse`:

```python
class CaseSubmitResponse(BaseModel):
    result: DomainScore
    cards: list[Flashcard]
    mock_mode: bool
    debrief: str | None = None
```

In the `case_submit` function, add the debrief call just before the `return` statement (after the profile update block):

```python
    # Generate structured debrief
    debrief_text: str | None = None
    try:
        debrief_prompt = (
            "You are an ophthalmology clinical educator reviewing a student's case performance. "
            "Write a structured debrief in exactly this format:\n\n"
            "**What you got right:** ...\n\n"
            "**What you missed:** ...\n\n"
            "**Why it matters clinically:** ...\n\n"
            "**Focus for next time:** ...\n\n"
            "Be specific and clinical. Do not repeat the scores — focus on insight."
        )
        debrief_messages = [
            {
                "role": "user",
                "content": (
                    f"Case: {case['title']}\n"
                    f"Diagnosis submitted: {body.diagnosis}\n"
                    f"Management submitted: {body.management_plan}\n"
                    f"Score: {raw_result.get('total_score', 0)}/40\n"
                    f"Overall feedback: {raw_result.get('overall_feedback', '')}"
                ),
            }
        ]
        debrief_text = ask(
            system_prompt=debrief_prompt,
            messages=debrief_messages,
            max_tokens=512,
            feature="debrief",
        )
    except Exception:
        debrief_text = None

    return CaseSubmitResponse(
        result=DomainScore(**{k: raw_result[k] for k in DomainScore.model_fields}),
        cards=[Flashcard(**c) for c in cards],
        mock_mode=MOCK_MODE,
        debrief=debrief_text,
    )
```

- [ ] **Step 2: Add debrief state and display in `CaseSessionScreen.tsx`**

Add `debrief` state after the existing `cards` state (line 60):

```tsx
  const [debrief, setDebrief] = useState<string | null>(null);
```

In `handleSubmit`, update the result extraction (replace the existing `setResult(data.result)` and `setCards(data.cards)` block):

```tsx
      const data = await res.json();
      setResult(data.result);
      setCards(data.cards);
      setDebrief(data.debrief ?? null);
      setShowSubmitForm(false);
```

In the results panel, add the debrief section after the overall_feedback teal box and before the "Generate Flashcards" button:

```tsx
              {debrief && (
                <div className="px-4 py-4 rounded-xl bg-indigo-500/10 border border-indigo-500/20 mb-4">
                  <p className="text-slate-400 mb-2" style={{ fontSize: "0.65rem", fontWeight: 700, letterSpacing: "0.1em", textTransform: "uppercase" }}>
                    Debrief
                  </p>
                  <div className="text-slate-300 whitespace-pre-wrap" style={{ fontSize: "0.8125rem", lineHeight: 1.7 }}>
                    {debrief.split(/\*\*(.*?)\*\*/g).map((part, i) =>
                      i % 2 === 1 ? (
                        <strong key={i} className="text-white">{part}</strong>
                      ) : (
                        <span key={i}>{part}</span>
                      )
                    )}
                  </div>
                </div>
              )}
```

- [ ] **Step 3: Verify server starts and TypeScript compiles**

```
uvicorn tools.api.server:app --reload --port 8000
```
Press Ctrl+C once running.

```
cd frontend && pnpm tsc --noEmit
```
Expected: no type errors.

- [ ] **Step 4: Commit**

```bash
git add tools/api/server.py frontend/src/app/components/CaseSessionScreen.tsx
git commit -m "feat: add post-case debrief AI call and display"
```

---

## Task 7: Daily check-in API

**Files:**
- Modify: `tools/api/server.py` — add check-in models + 3 endpoints

- [ ] **Step 1: Add check-in models and endpoints to `server.py`**

Add the models after the existing case models (before the `# ── Case endpoints` comment):

```python
# ── Check-in models ────────────────────────────────────────────────────────

class CheckinStatusResponse(BaseModel):
    checkin_done_today: bool
    streak: int
    weak_topic: str | None

class CheckinQuestionResponse(BaseModel):
    question: str
    topic: str

class CheckinAnswerRequest(BaseModel):
    student_id: str
    question: str
    answer: str
    topic: str

class CheckinAnswerResponse(BaseModel):
    correct: bool
    feedback: str
```

Add the check-in endpoints after the `/api/status` endpoint:

```python
# ── Check-in endpoints ─────────────────────────────────────────────────────

@app.get("/api/checkin/status", response_model=CheckinStatusResponse)
def checkin_status(student_id: str):
    try:
        profile = get_profile(student_id)
    except Exception:
        return CheckinStatusResponse(checkin_done_today=True, streak=0, weak_topic=None)

    done = str(profile.get("checkin_done_today", "false")).lower() == "true"
    streak = int(profile.get("streak", "0") or "0")
    try:
        import json as _json
        weak = _json.loads(profile.get("weak_topics", "[]") or "[]")
        weak_topic = weak[0] if weak else None
    except Exception:
        weak_topic = None

    return CheckinStatusResponse(
        checkin_done_today=done,
        streak=streak,
        weak_topic=weak_topic,
    )


@app.get("/api/checkin/question", response_model=CheckinQuestionResponse)
def checkin_question(student_id: str):
    try:
        profile = get_profile(student_id)
        import json as _json
        weak = _json.loads(profile.get("weak_topics", "[]") or "[]")
        topic = weak[0] if weak else "Ophthalmology"
    except Exception:
        topic = "Ophthalmology"

    system = (
        "You are an ophthalmology tutor running a 60-second warm-up check-in. "
        "Generate ONE concise clinical question targeting the given topic. "
        "Return only the question text — no preamble, no numbering."
    )
    question = ask(
        system_prompt=system,
        messages=[{"role": "user", "content": f"Topic: {topic}"}],
        max_tokens=120,
        feature="checkin",
    )
    return CheckinQuestionResponse(question=question.strip(), topic=topic)


@app.post("/api/checkin/answer", response_model=CheckinAnswerResponse)
def checkin_answer(body: CheckinAnswerRequest):
    system = (
        "You are an ophthalmology tutor evaluating a warm-up answer. "
        "Respond in this exact format:\n"
        "CORRECT: true or false\n"
        "FEEDBACK: one sentence — confirm correct answer or correct the error, plus one line why it matters.\n"
        "Do not use markdown."
    )
    raw = ask(
        system_prompt=system,
        messages=[{
            "role": "user",
            "content": (
                f"Question: {body.question}\n"
                f"Student answer: {body.answer}"
            ),
        }],
        max_tokens=150,
        feature="checkin",
    )

    correct = "true" in raw.lower().split("correct:")[-1][:10]
    feedback_parts = raw.split("FEEDBACK:")
    feedback = feedback_parts[-1].strip() if len(feedback_parts) > 1 else raw.strip()

    try:
        update_profile(body.student_id, checkin_done=True)
    except Exception:
        pass

    return CheckinAnswerResponse(correct=correct, feedback=feedback)
```

- [ ] **Step 2: Verify the server starts cleanly**

```
uvicorn tools.api.server:app --reload --port 8000
```
Press Ctrl+C once running. No errors expected.

- [ ] **Step 3: Commit**

```bash
git add tools/api/server.py
git commit -m "feat: add daily check-in API endpoints"
```

---

## Task 8: Daily check-in frontend

**Files:**
- Create: `frontend/src/app/components/DailyCheckInScreen.tsx`
- Modify: `frontend/src/app/components/DashboardScreen.tsx`
- Modify: `frontend/src/app/routes.tsx`

- [ ] **Step 1: Create `DailyCheckInScreen.tsx`**

```tsx
// frontend/src/app/components/DailyCheckInScreen.tsx
import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router";
import { motion, AnimatePresence } from "motion/react";
import { HolographicEyeLogo } from "./HolographicEyeLogo";
import { Flame, CheckCircle, XCircle, ArrowRight } from "lucide-react";

const API = "http://localhost:8000";

interface QuestionData {
  question: string;
  topic: string;
}

type Phase = "loading" | "question" | "result" | "done";

export function DailyCheckInScreen() {
  const navigate = useNavigate();
  const studentId = sessionStorage.getItem("eyeq_student_id") || "anonymous";

  const [streak, setStreak] = useState(0);
  const [weakTopic, setWeakTopic] = useState<string | null>(null);
  const [question, setQuestion] = useState<QuestionData | null>(null);
  const [answer, setAnswer] = useState("");
  const [phase, setPhase] = useState<Phase>("loading");
  const [correct, setCorrect] = useState<boolean | null>(null);
  const [feedback, setFeedback] = useState("");
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    (async () => {
      try {
        const statusRes = await fetch(`${API}/api/checkin/status?student_id=${studentId}`);
        const status = await statusRes.json();
        setStreak(status.streak ?? 0);
        setWeakTopic(status.weak_topic ?? null);

        const qRes = await fetch(`${API}/api/checkin/question?student_id=${studentId}`);
        const q = await qRes.json();
        setQuestion(q);
        setPhase("question");
      } catch {
        // If we can't load the check-in, skip straight to dashboard
        navigate("/dashboard");
      }
    })();
  }, [studentId, navigate]);

  const handleSubmit = async () => {
    if (!answer.trim() || !question) return;
    setSubmitting(true);
    try {
      const res = await fetch(`${API}/api/checkin/answer`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          student_id: studentId,
          question: question.question,
          answer: answer.trim(),
          topic: question.topic,
        }),
      });
      const data = await res.json();
      setCorrect(data.correct);
      setFeedback(data.feedback);
      setPhase("result");
    } catch {
      setFeedback("Could not evaluate — please try again.");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#0D1B2A] flex items-center justify-center px-4 py-12">
      <motion.div
        className="w-full max-w-lg"
        initial={{ opacity: 0, y: 24 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        {/* Header */}
        <div className="flex items-center gap-3 mb-8">
          <HolographicEyeLogo size={36} animated />
          <div>
            <h1 className="text-white" style={{ fontSize: "1.25rem", fontWeight: 700 }}>
              Daily Check-In
            </h1>
            {streak > 0 && (
              <div className="flex items-center gap-1.5 mt-0.5">
                <Flame size={13} className="text-orange-400" />
                <span className="text-orange-400" style={{ fontSize: "0.75rem", fontWeight: 600 }}>
                  {streak}-day streak
                </span>
              </div>
            )}
          </div>
        </div>

        {/* Focus topic */}
        {weakTopic && phase !== "loading" && (
          <div className="mb-5 px-4 py-3 rounded-xl bg-[#14B8A6]/10 border border-[#14B8A6]/20">
            <p className="text-[#14B8A6]" style={{ fontSize: "0.8rem" }}>
              Today's focus: <strong>{weakTopic}</strong>
            </p>
          </div>
        )}

        {/* Loading */}
        {phase === "loading" && (
          <div className="flex items-center justify-center h-40">
            <div className="w-8 h-8 border-2 border-[#14B8A6] border-t-transparent rounded-full animate-spin" />
          </div>
        )}

        {/* Question */}
        <AnimatePresence>
          {phase === "question" && question && (
            <motion.div
              key="question"
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: 20 }}
            >
              <div className="mb-6 px-5 py-5 rounded-2xl bg-white/[0.05] border border-white/10">
                <p className="text-slate-400 mb-3" style={{ fontSize: "0.7rem", fontWeight: 600, letterSpacing: "0.1em", textTransform: "uppercase" }}>
                  Warm-up question
                </p>
                <p className="text-white" style={{ fontSize: "1rem", lineHeight: 1.6 }}>
                  {question.question}
                </p>
              </div>

              <textarea
                value={answer}
                onChange={(e) => setAnswer(e.target.value)}
                placeholder="Type your answer…"
                rows={3}
                className="w-full px-4 py-3 mb-4 rounded-xl bg-white/[0.05] border border-white/15 text-white placeholder-slate-600 outline-none focus:border-[#14B8A6]/50 resize-none"
                style={{ fontSize: "0.9rem", lineHeight: 1.5 }}
                onKeyDown={(e) => {
                  if (e.key === "Enter" && (e.ctrlKey || e.metaKey)) handleSubmit();
                }}
              />

              <button
                onClick={handleSubmit}
                disabled={!answer.trim() || submitting}
                className="w-full py-3 rounded-xl bg-[#14B8A6] text-white font-semibold disabled:opacity-50 disabled:cursor-not-allowed hover:bg-[#0D9488] transition-colors"
                style={{ fontSize: "0.9375rem" }}
              >
                {submitting ? "Checking…" : "Submit Answer"}
              </button>

              <button
                onClick={() => navigate("/dashboard")}
                className="w-full mt-3 py-2 text-slate-600 hover:text-slate-400 transition-colors"
                style={{ fontSize: "0.8rem" }}
              >
                Skip for today
              </button>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Result */}
        <AnimatePresence>
          {phase === "result" && (
            <motion.div
              key="result"
              initial={{ opacity: 0, scale: 0.96 }}
              animate={{ opacity: 1, scale: 1 }}
              className="text-center"
            >
              <div className="flex justify-center mb-4">
                {correct ? (
                  <CheckCircle size={48} className="text-green-400" />
                ) : (
                  <XCircle size={48} className="text-red-400" />
                )}
              </div>
              <p className="text-white mb-2" style={{ fontSize: "1.1rem", fontWeight: 600 }}>
                {correct ? "Correct!" : "Not quite"}
              </p>
              <p className="text-slate-300 mb-8" style={{ fontSize: "0.9rem", lineHeight: 1.6 }}>
                {feedback}
              </p>
              <button
                onClick={() => navigate("/dashboard")}
                className="flex items-center gap-2 mx-auto px-6 py-3 rounded-xl bg-[#14B8A6] text-white font-semibold hover:bg-[#0D9488] transition-colors"
                style={{ fontSize: "0.9375rem" }}
              >
                Continue to Dashboard
                <ArrowRight size={16} />
              </button>
            </motion.div>
          )}
        </AnimatePresence>
      </motion.div>
    </div>
  );
}
```

- [ ] **Step 2: Add check-in gate to `DashboardScreen.tsx`**

Add the following `useEffect` hook inside the `DashboardScreen` component, right after the `userData` block (before the `return` statement):

```tsx
  const [checkinChecked, setCheckinChecked] = React.useState(false);

  React.useEffect(() => {
    const studentId = sessionStorage.getItem("eyeq_student_id");
    if (!studentId) { setCheckinChecked(true); return; }

    fetch(`http://localhost:8000/api/checkin/status?student_id=${studentId}`)
      .then((r) => r.json())
      .then((data) => {
        if (!data.checkin_done_today) {
          navigate("/checkin");
        } else {
          setCheckinChecked(true);
        }
      })
      .catch(() => setCheckinChecked(true));
  }, [navigate]);

  if (!checkinChecked) return null;
```

- [ ] **Step 3: Add `React` import to `DashboardScreen.tsx`**

Change the first line from:
```tsx
import React from "react";
```
to (already imported, just verify it exists — if not, add it).

- [ ] **Step 4: Add `/checkin` route to `routes.tsx`**

```tsx
import { DailyCheckInScreen } from "./components/DailyCheckInScreen";
```

Add after the `/dashboard` route:
```tsx
  {
    path: "/checkin",
    Component: DailyCheckInScreen,
  },
```

- [ ] **Step 5: TypeScript compile check**

```
cd frontend && pnpm tsc --noEmit
```
Expected: no errors.

- [ ] **Step 6: Commit**

```bash
git add frontend/src/app/components/DailyCheckInScreen.tsx frontend/src/app/components/DashboardScreen.tsx frontend/src/app/routes.tsx
git commit -m "feat: add daily check-in screen and dashboard gate"
```

---

## Task 9: Supervisor backend tools

**Files:**
- Create: `tools/supervisor/__init__.py`
- Create: `tools/supervisor/cohort_summary.py`
- Create: `tools/supervisor/at_risk.py`
- Create: `tools/supervisor/activity_report.py`
- Create: `tests/supervisor/__init__.py`
- Create: `tests/supervisor/test_cohort_summary.py`
- Create: `tests/supervisor/test_at_risk.py`
- Modify: `.env.template` (add email config keys)

- [ ] **Step 1: Write the failing tests**

```python
# tests/supervisor/__init__.py
# (empty)
```

```python
# tests/supervisor/test_cohort_summary.py
import json
from unittest.mock import patch


def _profile(sid, weak_topics, last_active, retention_scores="{}"):
    return {
        "student_id": sid,
        "weak_topics": json.dumps(weak_topics),
        "missed_findings": "[]",
        "retention_scores": retention_scores,
        "session_count": "5",
        "streak": "2",
        "last_active": last_active,
        "learning_velocity": "stable",
        "checkin_done_today": "false",
    }


def test_cohort_summary_active_count():
    profiles = [
        _profile("s1", ["glaucoma"], "2026-05-09"),
        _profile("s2", ["retina"], "2026-05-03"),
        _profile("s3", [], "2026-05-10"),
    ]
    with patch("tools.supervisor.cohort_summary.get_rows", return_value=profiles), \
         patch("tools.supervisor.cohort_summary.date") as mock_date:
        from datetime import date as real_date
        mock_date.today.return_value = real_date(2026, 5, 10)
        mock_date.fromisoformat = real_date.fromisoformat
        mock_date.side_effect = lambda *a, **kw: real_date(*a, **kw)
        from tools.supervisor.cohort_summary import cohort_summary
        result = cohort_summary()
    assert result["total"] == 3
    assert result["active_this_week"] == 2  # s1 (1 day ago) and s3 (today)


def test_cohort_summary_weakest_topics():
    profiles = [
        _profile("s1", ["glaucoma", "retina"], "2026-05-10"),
        _profile("s2", ["glaucoma"], "2026-05-10"),
        _profile("s3", ["cornea"], "2026-05-10"),
    ]
    with patch("tools.supervisor.cohort_summary.get_rows", return_value=profiles), \
         patch("tools.supervisor.cohort_summary.date") as mock_date:
        from datetime import date as real_date
        mock_date.today.return_value = real_date(2026, 5, 10)
        mock_date.fromisoformat = real_date.fromisoformat
        mock_date.side_effect = lambda *a, **kw: real_date(*a, **kw)
        from tools.supervisor.cohort_summary import cohort_summary
        result = cohort_summary()
    assert result["weakest_topics"][0] == "glaucoma"  # appears in 2 profiles
```

```python
# tests/supervisor/test_at_risk.py
import json
from unittest.mock import patch
from datetime import date


def _profile(sid, weak_topics, last_active):
    return {
        "student_id": sid,
        "weak_topics": json.dumps(weak_topics),
        "last_active": last_active,
    }


def test_at_risk_flags_inactive_with_weak_topics():
    profiles = [
        _profile("s1", ["glaucoma", "retina"], "2026-05-04"),  # 6 days ago, 2 weak
        _profile("s2", ["glaucoma"], "2026-05-04"),              # 6 days ago, 1 weak
        _profile("s3", ["glaucoma", "retina"], "2026-05-09"),   # 1 day ago, 2 weak
    ]
    with patch("tools.supervisor.at_risk.get_rows", return_value=profiles), \
         patch("tools.supervisor.at_risk.date") as mock_date:
        mock_date.today.return_value = date(2026, 5, 10)
        mock_date.fromisoformat = date.fromisoformat
        from tools.supervisor.at_risk import get_at_risk
        result = get_at_risk()
    assert len(result) == 1
    assert result[0]["student_id"] == "s1"


def test_at_risk_empty_when_all_active():
    profiles = [
        _profile("s1", ["glaucoma", "retina"], "2026-05-09"),
        _profile("s2", ["glaucoma", "retina"], "2026-05-10"),
    ]
    with patch("tools.supervisor.at_risk.get_rows", return_value=profiles), \
         patch("tools.supervisor.at_risk.date") as mock_date:
        mock_date.today.return_value = date(2026, 5, 10)
        mock_date.fromisoformat = date.fromisoformat
        from tools.supervisor.at_risk import get_at_risk
        result = get_at_risk()
    assert result == []
```

- [ ] **Step 2: Run tests to verify they fail**

```
pytest tests/supervisor/ -v
```
Expected: `ImportError`

- [ ] **Step 3: Create `tools/supervisor/__init__.py`**

```python
# tools/supervisor/__init__.py
# (empty)
```

- [ ] **Step 4: Write `tools/supervisor/cohort_summary.py`**

```python
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
    week_ago = today - timedelta(days=7)
    five_days_ago = today - timedelta(days=5)
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
                if days_inactive <= 7:
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
```

- [ ] **Step 5: Write `tools/supervisor/at_risk.py`**

```python
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
```

- [ ] **Step 6: Write `tools/supervisor/activity_report.py`**

```python
#!/usr/bin/env python3
"""Generate the weekly supervisor activity report.

Writes to the snec_supervisor_alerts Google Sheet and emails all supervisors
in snec_supervisors.

Usage:
    python tools/supervisor/activity_report.py
    -- or --
    from tools.supervisor.activity_report import generate_report
    generate_report()
"""

import json
import os
import smtplib
import sys
from datetime import date, timedelta
from email.mime.text import MIMEText
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from dotenv import load_dotenv
load_dotenv(PROJECT_ROOT / ".env")

from tools.shared.gsheets import get_rows, append_row
from tools.shared.audit_log import log
from tools.supervisor.cohort_summary import cohort_summary
from tools.supervisor.at_risk import get_at_risk

GMAIL_USER = os.getenv("GMAIL_USER", "").strip()
GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD", "").strip()


def _build_email_body(summary: dict, at_risk: list[dict], week_start: str) -> str:
    lines = [
        f"EyeQ Supervisor Report — Week of {week_start}",
        "=" * 50,
        f"Total enrolled students: {summary['total']}",
        f"Active this week: {summary['active_this_week']}",
        f"At-risk students: {summary['at_risk_count']}",
        "",
        f"Cohort-wide weakest topics: {', '.join(summary['weakest_topics']) or 'None'}",
        "",
    ]

    if at_risk:
        lines.append("AT-RISK STUDENTS (5+ days inactive, 2+ weak topics):")
        for s in at_risk:
            lines.append(
                f"  - {s['student_id']} — last active {s['last_active']} "
                f"({s['days_inactive']} days ago), weak: {', '.join(s['weak_topics'])}"
            )
    else:
        lines.append("No students currently at risk.")

    if summary["inactive_7_plus_days"]:
        lines.append("")
        lines.append("STUDENTS NOT SEEN IN 7+ DAYS:")
        for s in summary["inactive_7_plus_days"]:
            lines.append(f"  - {s['student_id']} — last active {s['last_active']}")

    lines.append("")
    lines.append("This report is generated automatically every Monday.")
    return "\n".join(lines)


def _send_emails(subject: str, body: str, supervisor_emails: list[str]) -> None:
    if not GMAIL_USER or not GMAIL_APP_PASSWORD:
        log("email_skipped", feature="supervisor", detail="GMAIL_USER or GMAIL_APP_PASSWORD not set")
        return

    for email in supervisor_emails:
        try:
            msg = MIMEText(body)
            msg["Subject"] = subject
            msg["From"] = GMAIL_USER
            msg["To"] = email

            with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
                smtp.login(GMAIL_USER, GMAIL_APP_PASSWORD)
                smtp.send_message(msg)

            log("email_sent", feature="supervisor", detail=f"report sent to {email}")
        except Exception as exc:
            log("email_error", feature="supervisor", detail=f"{email}: {exc}")


def generate_report() -> dict:
    """Generate and deliver the weekly report. Returns the summary dict."""
    week_start = (date.today() - timedelta(days=date.today().weekday())).isoformat()

    summary = cohort_summary()
    at_risk = get_at_risk()

    # Write to Sheets
    try:
        append_row("snec_supervisor_alerts", {
            "week_start": week_start,
            "active_students": str(summary["active_this_week"]),
            "inactive_students": str(len(summary["inactive_7_plus_days"])),
            "weakest_topics": json.dumps(summary["weakest_topics"]),
            "at_risk_count": str(summary["at_risk_count"]),
            "report_json": json.dumps({"summary": summary, "at_risk": at_risk}),
        })
    except Exception as exc:
        log("report_sheet_error", feature="supervisor", detail=str(exc))

    # Email supervisors
    try:
        supervisors = get_rows("snec_supervisors")
        emails = [s["email"] for s in supervisors if s.get("email")]
    except Exception:
        emails = []

    subject = f"EyeQ Weekly Supervisor Report — {week_start}"
    body = _build_email_body(summary, at_risk, week_start)
    _send_emails(subject, body, emails)

    return summary


if __name__ == "__main__":
    print("Generating weekly supervisor report...\n")
    result = generate_report()
    print(f"Done. {result['total']} students, {result['at_risk_count']} at risk.")
```

- [ ] **Step 7: Update `.env.template`**

Add to the bottom of `.env.template`:

```
# Google Spreadsheet (set by running infrastructure_bootstrap.py)
GOOGLE_SPREADSHEET_ID=

# Gmail SMTP (for supervisor weekly reports)
# Use a Gmail App Password (not your main password): https://myaccount.google.com/apppasswords
GMAIL_USER=
GMAIL_APP_PASSWORD=
```

- [ ] **Step 8: Run supervisor tests**

```
pytest tests/supervisor/ -v
```
Expected: all PASS

- [ ] **Step 9: Commit**

```bash
git add tools/supervisor/__init__.py tools/supervisor/cohort_summary.py tools/supervisor/at_risk.py tools/supervisor/activity_report.py tests/supervisor/__init__.py tests/supervisor/test_cohort_summary.py tests/supervisor/test_at_risk.py .env.template
git commit -m "feat: add supervisor backend tools (cohort_summary, at_risk, activity_report)"
```

---

## Task 10: Supervisor API endpoints + role-based onboard

**Files:**
- Modify: `tools/api/server.py`

- [ ] **Step 1: Add supervisor models and endpoints to `server.py`**

Update `OnboardResponse` to include `role`:

```python
class OnboardResponse(BaseModel):
    student_id: str
    mock_mode: bool
    role: str = "student"
```

Update the `onboard` endpoint to check `snec_supervisors`:

```python
@app.post("/api/onboard", response_model=OnboardResponse)
def onboard(body: OnboardRequest):
    if not body.full_name.strip() or not body.email.strip():
        raise HTTPException(status_code=400, detail="full_name and email are required")

    email = body.email.strip().lower()
    student_id = get_or_create_student(body.full_name.strip(), email)
    if not has_consented(student_id):
        record_consent(student_id)

    # Check if this email belongs to a supervisor
    role = "student"
    try:
        from tools.shared.gsheets import get_rows as _get_rows
        supervisors = _get_rows("snec_supervisors", filters={"email": email})
        if supervisors:
            role = "supervisor"
    except Exception:
        pass

    return OnboardResponse(student_id=student_id, mock_mode=MOCK_MODE, role=role)
```

Add supervisor imports and models after the check-in models:

```python
# ── Supervisor imports ─────────────────────────────────────────────────────

from tools.supervisor.cohort_summary import cohort_summary as _cohort_summary
from tools.supervisor.at_risk import get_at_risk as _get_at_risk


# ── Supervisor models ──────────────────────────────────────────────────────

class CohortSummaryResponse(BaseModel):
    total: int
    active_this_week: int
    inactive_7_plus_days: list[dict]
    weakest_topics: list[str]
    at_risk_count: int

class AtRiskResponse(BaseModel):
    students: list[dict]

class StudentProfileResponse(BaseModel):
    student_id: str
    weak_topics: list[str]
    missed_findings: list[str]
    retention_scores: dict
    session_count: int
    streak: int
    last_active: str
    learning_velocity: str
    checkin_done_today: bool
```

Add supervisor endpoints after the check-in endpoints:

```python
# ── Supervisor endpoints ───────────────────────────────────────────────────

@app.get("/api/supervisor/cohort", response_model=CohortSummaryResponse)
def supervisor_cohort():
    try:
        result = _cohort_summary()
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
    return CohortSummaryResponse(**result)


@app.get("/api/supervisor/at-risk", response_model=AtRiskResponse)
def supervisor_at_risk():
    try:
        students = _get_at_risk()
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
    return AtRiskResponse(students=students)


@app.get("/api/supervisor/student/{student_id}", response_model=StudentProfileResponse)
def supervisor_student(student_id: str):
    try:
        import json as _json
        profile = get_profile(student_id)
    except Exception as exc:
        raise HTTPException(status_code=404, detail=str(exc))

    try:
        import json as _json
        return StudentProfileResponse(
            student_id=profile["student_id"],
            weak_topics=_json.loads(profile.get("weak_topics", "[]") or "[]"),
            missed_findings=_json.loads(profile.get("missed_findings", "[]") or "[]"),
            retention_scores=_json.loads(profile.get("retention_scores", "{}") or "{}"),
            session_count=int(profile.get("session_count", "0") or "0"),
            streak=int(profile.get("streak", "0") or "0"),
            last_active=profile.get("last_active", ""),
            learning_velocity=profile.get("learning_velocity", "stable"),
            checkin_done_today=str(profile.get("checkin_done_today", "false")).lower() == "true",
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
```

- [ ] **Step 2: Update `OnboardingScreen.tsx` to route supervisors to `/supervisor`**

In `OnboardingScreen.tsx`, update the `handleSubmit` success block:

```tsx
      const data = await res.json();
      sessionStorage.setItem("eyeq_user", JSON.stringify({ fullName, email }));
      sessionStorage.setItem("eyeq_student_id", data.student_id);
      sessionStorage.setItem("eyeq_role", data.role ?? "student");
      if (data.role === "supervisor") {
        navigate("/supervisor");
      } else {
        navigate("/dashboard");
      }
```

- [ ] **Step 3: Verify server starts cleanly**

```
uvicorn tools.api.server:app --reload --port 8000
```
Press Ctrl+C. No errors expected.

- [ ] **Step 4: TypeScript compile check**

```
cd frontend && pnpm tsc --noEmit
```

- [ ] **Step 5: Commit**

```bash
git add tools/api/server.py frontend/src/app/components/OnboardingScreen.tsx
git commit -m "feat: add supervisor API endpoints and role-based routing on login"
```

---

## Task 11: Supervisor frontend

**Files:**
- Create: `frontend/src/app/components/CohortHeatmap.tsx`
- Create: `frontend/src/app/components/AtRiskTable.tsx`
- Create: `frontend/src/app/components/StudentDrillDown.tsx`
- Create: `frontend/src/app/components/SupervisorDashboard.tsx`
- Modify: `frontend/src/app/routes.tsx`

- [ ] **Step 1: Create `CohortHeatmap.tsx`**

```tsx
// frontend/src/app/components/CohortHeatmap.tsx
import React from "react";

interface Props {
  topics: string[];
  retentionByTopic: Record<string, number>;
}

function scoreToColor(score: number | undefined): string {
  if (score === undefined) return "#1e293b";
  if (score >= 0.75) return "#14B8A6";
  if (score >= 0.5) return "#F59E0B";
  return "#F87171";
}

export function CohortHeatmap({ topics, retentionByTopic }: Props) {
  if (topics.length === 0) {
    return (
      <p className="text-slate-500 text-sm">No topic data yet.</p>
    );
  }

  return (
    <div className="flex flex-wrap gap-2">
      {topics.map((topic) => {
        const score = retentionByTopic[topic];
        return (
          <div
            key={topic}
            className="px-3 py-2 rounded-lg text-xs font-medium"
            style={{
              background: `${scoreToColor(score)}22`,
              border: `1px solid ${scoreToColor(score)}66`,
              color: scoreToColor(score),
            }}
            title={score !== undefined ? `${Math.round(score * 100)}%` : "No data"}
          >
            {topic}
            {score !== undefined && (
              <span className="ml-1.5 opacity-70">{Math.round(score * 100)}%</span>
            )}
          </div>
        );
      })}
    </div>
  );
}
```

- [ ] **Step 2: Create `AtRiskTable.tsx`**

```tsx
// frontend/src/app/components/AtRiskTable.tsx
import React from "react";
import { AlertTriangle } from "lucide-react";

interface AtRiskStudent {
  student_id: string;
  last_active: string;
  days_inactive: number;
  weak_topics: string[];
  weak_count: number;
}

interface Props {
  students: AtRiskStudent[];
  onSelectStudent: (id: string) => void;
}

export function AtRiskTable({ students, onSelectStudent }: Props) {
  if (students.length === 0) {
    return (
      <p className="text-slate-500 text-sm">No at-risk students. All good.</p>
    );
  }

  return (
    <div className="overflow-x-auto">
      <table className="w-full text-sm">
        <thead>
          <tr className="text-slate-500 text-left border-b border-white/10">
            <th className="pb-2 pr-4 font-semibold" style={{ fontSize: "0.7rem", letterSpacing: "0.08em", textTransform: "uppercase" }}>Student</th>
            <th className="pb-2 pr-4 font-semibold" style={{ fontSize: "0.7rem", letterSpacing: "0.08em", textTransform: "uppercase" }}>Days Inactive</th>
            <th className="pb-2 pr-4 font-semibold" style={{ fontSize: "0.7rem", letterSpacing: "0.08em", textTransform: "uppercase" }}>Last Active</th>
            <th className="pb-2 font-semibold" style={{ fontSize: "0.7rem", letterSpacing: "0.08em", textTransform: "uppercase" }}>Weak Topics</th>
          </tr>
        </thead>
        <tbody>
          {students.map((s) => (
            <tr
              key={s.student_id}
              onClick={() => onSelectStudent(s.student_id)}
              className="border-b border-white/5 hover:bg-white/[0.03] cursor-pointer transition-colors"
            >
              <td className="py-3 pr-4">
                <div className="flex items-center gap-2">
                  <AlertTriangle size={13} className="text-red-400 flex-shrink-0" />
                  <span className="text-white font-mono text-xs truncate max-w-[120px]">{s.student_id.slice(0, 8)}…</span>
                </div>
              </td>
              <td className="py-3 pr-4">
                <span className="text-red-400 font-semibold">{s.days_inactive}d</span>
              </td>
              <td className="py-3 pr-4 text-slate-400">{s.last_active}</td>
              <td className="py-3">
                <div className="flex flex-wrap gap-1">
                  {s.weak_topics.slice(0, 3).map((t) => (
                    <span key={t} className="px-2 py-0.5 rounded-full bg-red-500/15 text-red-400 text-xs">{t}</span>
                  ))}
                  {s.weak_topics.length > 3 && (
                    <span className="text-slate-600 text-xs">+{s.weak_topics.length - 3}</span>
                  )}
                </div>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
```

- [ ] **Step 3: Create `StudentDrillDown.tsx`**

```tsx
// frontend/src/app/components/StudentDrillDown.tsx
import React, { useEffect, useState } from "react";
import { motion } from "motion/react";
import { X, TrendingUp, TrendingDown, Minus } from "lucide-react";

const API = "http://localhost:8000";

interface StudentProfile {
  student_id: string;
  weak_topics: string[];
  missed_findings: string[];
  retention_scores: Record<string, number>;
  session_count: number;
  streak: number;
  last_active: string;
  learning_velocity: string;
  checkin_done_today: boolean;
}

interface Props {
  studentId: string;
  onClose: () => void;
}

function VelocityIcon({ velocity }: { velocity: string }) {
  if (velocity === "improving") return <TrendingUp size={14} className="text-green-400" />;
  if (velocity === "declining") return <TrendingDown size={14} className="text-red-400" />;
  return <Minus size={14} className="text-slate-400" />;
}

export function StudentDrillDown({ studentId, onClose }: Props) {
  const [profile, setProfile] = useState<StudentProfile | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetch(`${API}/api/supervisor/student/${studentId}`)
      .then((r) => { if (!r.ok) throw new Error("Not found"); return r.json(); })
      .then((data) => { setProfile(data); setLoading(false); })
      .catch(() => { setError("Could not load student profile."); setLoading(false); });
  }, [studentId]);

  return (
    <motion.div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm px-4"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      onClick={onClose}
    >
      <motion.div
        className="w-full max-w-lg bg-[#0D1B2A] border border-white/15 rounded-2xl overflow-hidden shadow-2xl"
        initial={{ scale: 0.95, y: 20 }}
        animate={{ scale: 1, y: 0 }}
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex items-center justify-between px-6 py-4 border-b border-white/10">
          <p className="text-white font-semibold">Student Profile</p>
          <button onClick={onClose} className="text-slate-500 hover:text-white transition-colors">
            <X size={18} />
          </button>
        </div>

        <div className="px-6 py-5 overflow-y-auto max-h-[70vh]">
          {loading && (
            <div className="flex justify-center py-8">
              <div className="w-6 h-6 border-2 border-[#14B8A6] border-t-transparent rounded-full animate-spin" />
            </div>
          )}
          {error && <p className="text-red-400 text-sm">{error}</p>}
          {profile && (
            <div className="space-y-5">
              <div className="grid grid-cols-3 gap-3">
                {[
                  { label: "Sessions", value: profile.session_count },
                  { label: "Streak", value: `${profile.streak}d` },
                  { label: "Last Active", value: profile.last_active || "Never" },
                ].map(({ label, value }) => (
                  <div key={label} className="px-3 py-3 rounded-xl bg-white/[0.04] border border-white/10 text-center">
                    <p className="text-slate-500 mb-1" style={{ fontSize: "0.65rem", letterSpacing: "0.08em", textTransform: "uppercase" }}>{label}</p>
                    <p className="text-white font-semibold" style={{ fontSize: "0.9rem" }}>{value}</p>
                  </div>
                ))}
              </div>

              <div className="flex items-center gap-2">
                <VelocityIcon velocity={profile.learning_velocity} />
                <span className="text-slate-400 text-sm capitalize">{profile.learning_velocity}</span>
              </div>

              <div>
                <p className="text-slate-500 mb-2" style={{ fontSize: "0.7rem", letterSpacing: "0.08em", textTransform: "uppercase", fontWeight: 600 }}>
                  Weak Topics
                </p>
                {profile.weak_topics.length === 0 ? (
                  <p className="text-slate-600 text-sm">None — all topics above threshold.</p>
                ) : (
                  <div className="flex flex-wrap gap-2">
                    {profile.weak_topics.map((t) => {
                      const score = profile.retention_scores[t];
                      return (
                        <span key={t} className="px-2.5 py-1 rounded-full bg-red-500/15 border border-red-500/30 text-red-400 text-xs">
                          {t}{score !== undefined ? ` — ${Math.round(score * 100)}%` : ""}
                        </span>
                      );
                    })}
                  </div>
                )}
              </div>

              <div>
                <p className="text-slate-500 mb-2" style={{ fontSize: "0.7rem", letterSpacing: "0.08em", textTransform: "uppercase", fontWeight: 600 }}>
                  Missed Findings
                </p>
                {profile.missed_findings.length === 0 ? (
                  <p className="text-slate-600 text-sm">None recorded.</p>
                ) : (
                  <ul className="space-y-1">
                    {profile.missed_findings.map((f, i) => (
                      <li key={i} className="text-slate-400 text-sm flex items-start gap-2">
                        <span className="text-slate-600 mt-0.5">•</span>
                        {f}
                      </li>
                    ))}
                  </ul>
                )}
              </div>
            </div>
          )}
        </div>
      </motion.div>
    </motion.div>
  );
}
```

- [ ] **Step 4: Create `SupervisorDashboard.tsx`**

```tsx
// frontend/src/app/components/SupervisorDashboard.tsx
import React, { useEffect, useState } from "react";
import { motion, AnimatePresence } from "motion/react";
import { HolographicEyeLogo } from "./HolographicEyeLogo";
import { CohortHeatmap } from "./CohortHeatmap";
import { AtRiskTable } from "./AtRiskTable";
import { StudentDrillDown } from "./StudentDrillDown";
import { Users, AlertTriangle, Activity, LogOut } from "lucide-react";
import { useNavigate } from "react-router";

const API = "http://localhost:8000";

interface CohortData {
  total: number;
  active_this_week: number;
  inactive_7_plus_days: unknown[];
  weakest_topics: string[];
  at_risk_count: number;
}

interface AtRiskStudent {
  student_id: string;
  last_active: string;
  days_inactive: number;
  weak_topics: string[];
  weak_count: number;
}

export function SupervisorDashboard() {
  const navigate = useNavigate();
  const [cohort, setCohort] = useState<CohortData | null>(null);
  const [atRisk, setAtRisk] = useState<AtRiskStudent[]>([]);
  const [selectedStudent, setSelectedStudent] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    Promise.all([
      fetch(`${API}/api/supervisor/cohort`).then((r) => r.json()),
      fetch(`${API}/api/supervisor/at-risk`).then((r) => r.json()),
    ])
      .then(([cohortData, atRiskData]) => {
        setCohort(cohortData);
        setAtRisk(atRiskData.students ?? []);
        setLoading(false);
      })
      .catch(() => {
        setError("Could not load supervisor data. Is the backend running?");
        setLoading(false);
      });
  }, []);

  return (
    <div className="min-h-screen bg-[#0D1B2A] px-6 py-8 relative">
      {/* Header */}
      <div className="flex items-center justify-between mb-8 max-w-5xl mx-auto">
        <div className="flex items-center gap-3">
          <HolographicEyeLogo size={36} animated />
          <div>
            <h1 className="text-white" style={{ fontSize: "1.25rem", fontWeight: 700 }}>
              Supervisor Dashboard
            </h1>
            <p className="text-[#14B8A6]" style={{ fontSize: "0.7rem", letterSpacing: "0.12em" }}>
              EYEQ MEDICAL EDUCATION
            </p>
          </div>
        </div>
        <button
          onClick={() => { sessionStorage.clear(); navigate("/"); }}
          className="flex items-center gap-1.5 text-slate-500 hover:text-slate-300 transition-colors"
          style={{ fontSize: "0.8rem" }}
        >
          <LogOut size={14} />
          Sign out
        </button>
      </div>

      {loading && (
        <div className="flex justify-center py-20">
          <div className="w-8 h-8 border-2 border-[#14B8A6] border-t-transparent rounded-full animate-spin" />
        </div>
      )}

      {error && (
        <p className="text-red-400 text-center py-20">{error}</p>
      )}

      {cohort && (
        <div className="max-w-5xl mx-auto space-y-6">
          {/* KPI row */}
          <div className="grid grid-cols-3 gap-4">
            {[
              { icon: Users, label: "Total Students", value: cohort.total, color: "#14B8A6" },
              { icon: Activity, label: "Active This Week", value: cohort.active_this_week, color: "#818CF8" },
              { icon: AlertTriangle, label: "At Risk", value: cohort.at_risk_count, color: cohort.at_risk_count > 0 ? "#F87171" : "#4ADE80" },
            ].map(({ icon: Icon, label, value, color }) => (
              <motion.div
                key={label}
                className="px-5 py-5 rounded-2xl bg-white/[0.04] border border-white/10"
                initial={{ opacity: 0, y: 16 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.4 }}
              >
                <div className="flex items-center gap-2 mb-3">
                  <Icon size={16} style={{ color }} />
                  <p className="text-slate-400" style={{ fontSize: "0.75rem", fontWeight: 600 }}>{label}</p>
                </div>
                <p className="text-white" style={{ fontSize: "2rem", fontWeight: 700, color }}>{value}</p>
              </motion.div>
            ))}
          </div>

          {/* Heatmap */}
          <div className="px-5 py-5 rounded-2xl bg-white/[0.04] border border-white/10">
            <h2 className="text-white mb-4" style={{ fontSize: "0.9rem", fontWeight: 600 }}>
              Cohort Topic Weaknesses
            </h2>
            <CohortHeatmap
              topics={cohort.weakest_topics}
              retentionByTopic={{}}
            />
            {cohort.weakest_topics.length === 0 && (
              <p className="text-slate-500 text-sm">No weak topics recorded yet.</p>
            )}
          </div>

          {/* At-risk table */}
          <div className="px-5 py-5 rounded-2xl bg-white/[0.04] border border-white/10">
            <h2 className="text-white mb-4" style={{ fontSize: "0.9rem", fontWeight: 600 }}>
              At-Risk Students
            </h2>
            <AtRiskTable students={atRisk} onSelectStudent={setSelectedStudent} />
          </div>
        </div>
      )}

      {/* Student drill-down modal */}
      <AnimatePresence>
        {selectedStudent && (
          <StudentDrillDown
            studentId={selectedStudent}
            onClose={() => setSelectedStudent(null)}
          />
        )}
      </AnimatePresence>
    </div>
  );
}
```

- [ ] **Step 5: Add `/supervisor` route to `routes.tsx`**

```tsx
import { SupervisorDashboard } from "./components/SupervisorDashboard";
```

Add after the `/checkin` route:
```tsx
  {
    path: "/supervisor",
    Component: SupervisorDashboard,
  },
```

- [ ] **Step 6: TypeScript compile check**

```
cd frontend && pnpm tsc --noEmit
```
Expected: no errors.

- [ ] **Step 7: Run all backend tests**

```
pytest tests/ -v
```
Expected: all PASS.

- [ ] **Step 8: Commit**

```bash
git add frontend/src/app/components/CohortHeatmap.tsx frontend/src/app/components/AtRiskTable.tsx frontend/src/app/components/StudentDrillDown.tsx frontend/src/app/components/SupervisorDashboard.tsx frontend/src/app/routes.tsx
git commit -m "feat: add supervisor dashboard (heatmap, at-risk table, student drill-down)"
```

---

## Self-Review Checklist

**Spec coverage:**

| Spec requirement | Task |
|---|---|
| `tools/profile/get_profile.py` | Task 2 |
| `tools/profile/update_profile.py` | Task 3 |
| `tools/profile/summarize_gaps.py` | Task 4 |
| `tools/supervisor/cohort_summary.py` | Task 9 |
| `tools/supervisor/at_risk.py` | Task 9 |
| `tools/supervisor/activity_report.py` | Task 9 |
| `snec_profiles` / `snec_supervisors` sheets | Task 1 |
| Socratic instruction block in KB | Task 5 |
| Gap context injection in `/api/chat` | Task 5 |
| Profile writes in `/api/end-session` | Task 5 |
| Profile writes in `/api/cases/{id}/submit` | Task 5 |
| Post-case debrief field + display | Task 6 |
| `GET /api/checkin/status` | Task 7 |
| `GET /api/checkin/question` | Task 7 |
| `POST /api/checkin/answer` | Task 7 |
| `DailyCheckInScreen.tsx` | Task 8 |
| Dashboard check-in gate | Task 8 |
| `GET /api/supervisor/cohort` | Task 10 |
| `GET /api/supervisor/at-risk` | Task 10 |
| `GET /api/supervisor/student/{id}` | Task 10 |
| Role-based routing (supervisor → `/supervisor`) | Task 10 |
| `SupervisorDashboard.tsx` | Task 11 |
| `CohortHeatmap.tsx` | Task 11 |
| `AtRiskTable.tsx` | Task 11 |
| `StudentDrillDown.tsx` | Task 11 |
| Error handling (profile fail → base prompt) | Task 5 |
| Error handling (Gemini error → frontend message) | Existing in server.py |
| Email delivery for weekly report | Task 9 |
| Profile write fails → audit_log | Tasks 2, 3 |
| `checkin_done_today` reset mechanism | Task 2 |
| `learning_velocity` calculation | Task 3 |
| Gmail SMTP config in `.env.template` | Task 9 |

All spec requirements are covered. No gaps found.
