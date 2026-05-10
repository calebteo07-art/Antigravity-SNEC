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
