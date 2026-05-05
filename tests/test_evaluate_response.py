"""Tests for the case evaluator (tools/cases/evaluate_response.py).

Focuses on JSON parsing, code-fence stripping, total score calculation,
and the fallback behaviour when Claude returns malformed output.

All Claude calls are patched — no real API usage.
"""

import json
from unittest.mock import patch

import pytest


def _make_case():
    return {
        "case_id": "test-case-001",
        "diagnosis": "Primary open-angle glaucoma",
        "management": {"immediate": [], "follow_up": []},
        "rubric": {
            "history":        {"points": 10, "key_points": []},
            "investigations": {"points": 10, "key_points": []},
            "diagnosis":      {"points": 10, "key_points": []},
            "management":     {"points": 10, "key_points": []},
        },
        "examination_findings": {},
        "investigations": {},
    }


def _valid_response(**overrides):
    data = {
        "history_score": 8, "investigations_score": 7,
        "diagnosis_score": 9, "management_score": 7,
        "history_feedback":        "Good systematic history.",
        "investigations_feedback": "Key investigations requested.",
        "diagnosis_feedback":      "Correct diagnosis.",
        "management_feedback":     "Appropriate plan.",
        "overall_feedback":        "Well done overall.",
        **overrides,
    }
    return json.dumps(data)


def _run(mock_response: str, case=None) -> dict:
    case = case or _make_case()
    with patch("tools.cases.evaluate_response.ask", return_value=mock_response), \
         patch("tools.shared.audit_log.log"):
        from tools.cases.evaluate_response import evaluate_case
        return evaluate_case(case, [], "test-student-id")


class TestScoreParsing:
    def test_parses_all_four_domain_scores(self):
        result = _run(_valid_response())
        assert result["history_score"] == 8
        assert result["investigations_score"] == 7
        assert result["diagnosis_score"] == 9
        assert result["management_score"] == 7

    def test_total_score_is_sum_of_four_domains(self):
        result = _run(_valid_response(
            history_score=10, investigations_score=10,
            diagnosis_score=10, management_score=10,
        ))
        assert result["total_score"] == 40

    def test_total_score_with_mixed_scores(self):
        result = _run(_valid_response(
            history_score=6, investigations_score=7,
            diagnosis_score=8, management_score=9,
        ))
        assert result["total_score"] == 30

    def test_zero_scores_produce_zero_total(self):
        result = _run(_valid_response(
            history_score=0, investigations_score=0,
            diagnosis_score=0, management_score=0,
        ))
        assert result["total_score"] == 0

    def test_feedback_strings_are_preserved(self):
        result = _run(_valid_response(history_feedback="Great history taking."))
        assert result["history_feedback"] == "Great history taking."

    def test_overall_feedback_is_preserved(self):
        result = _run(_valid_response(overall_feedback="Excellent performance."))
        assert result["overall_feedback"] == "Excellent performance."


class TestCodeFenceStripping:
    def test_strips_json_code_fence(self):
        fenced = "```json\n" + _valid_response() + "\n```"
        result = _run(fenced)
        assert result["history_score"] == 8

    def test_strips_plain_code_fence(self):
        fenced = "```\n" + _valid_response() + "\n```"
        result = _run(fenced)
        assert result["diagnosis_score"] == 9

    def test_no_fence_still_parses(self):
        result = _run(_valid_response())
        assert result["total_score"] == 31


class TestFallbackBehaviour:
    def test_returns_dict_on_invalid_json(self):
        result = _run("This is not JSON at all.")
        assert isinstance(result, dict)
        assert "history_score" in result
        assert "total_score" in result

    def test_fallback_total_score_is_non_negative(self):
        result = _run("garbage response")
        assert result["total_score"] >= 0

    def test_fallback_includes_all_domain_scores(self):
        result = _run("not json")
        for key in ["history_score", "investigations_score",
                    "diagnosis_score", "management_score"]:
            assert key in result

    def test_fallback_total_equals_sum_of_fallback_scores(self):
        result = _run("not json")
        expected = (result["history_score"] + result["investigations_score"] +
                    result["diagnosis_score"] + result["management_score"])
        assert result["total_score"] == expected


class TestGenerateCards:
    """Verify _parse_cards handles Claude's various response formats."""

    def test_parse_cards_valid_json_array(self):
        from tools.flashcards.generate_cards import _parse_cards
        response = json.dumps([
            {"front": "Q1", "back": "A1", "topic_tag": "glaucoma"},
            {"front": "Q2", "back": "A2", "topic_tag": "retina"},
        ])
        cards = _parse_cards(response)
        assert len(cards) == 2
        assert cards[0]["front"] == "Q1"

    def test_parse_cards_strips_code_fence(self):
        from tools.flashcards.generate_cards import _parse_cards
        raw = '[{"front":"Q","back":"A","topic_tag":"glaucoma"}]'
        fenced = f"```json\n{raw}\n```"
        cards = _parse_cards(fenced)
        assert len(cards) == 1

    def test_parse_cards_returns_empty_on_invalid_json(self):
        from tools.flashcards.generate_cards import _parse_cards
        assert _parse_cards("not json") == []

    def test_parse_cards_filters_incomplete_cards(self):
        from tools.flashcards.generate_cards import _parse_cards
        response = json.dumps([
            {"front": "Q1", "back": "A1", "topic_tag": "glaucoma"},  # valid
            {"front": "Q2"},                                           # missing back + topic
            {"back": "A3", "topic_tag": "retina"},                    # missing front
        ])
        cards = _parse_cards(response)
        assert len(cards) == 1
        assert cards[0]["front"] == "Q1"

    def test_build_transcript_formats_roles(self):
        from tools.flashcards.generate_cards import _build_transcript
        messages = [
            {"role": "user",      "content": "What is glaucoma?"},
            {"role": "assistant", "content": "A group of optic neuropathies."},
        ]
        transcript = _build_transcript(messages)
        assert "Student: What is glaucoma?" in transcript
        assert "Tutor: A group of optic neuropathies." in transcript
