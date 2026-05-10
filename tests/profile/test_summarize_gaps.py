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
