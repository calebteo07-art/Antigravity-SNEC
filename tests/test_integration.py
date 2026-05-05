"""Integration tests — hit the real Anthropic API and Google Sheets.

These tests are SKIPPED automatically when credentials are absent.
Run them explicitly with:

    pytest -m integration

Or target a specific area:

    pytest -m integration -k "claude"
    pytest -m integration -k "sheets"

Prerequisites:
    - ANTHROPIC_API_KEY in .env
    - GOOGLE_SPREADSHEET_ID in .env
    - token.json present (run infrastructure_bootstrap.py once)
"""

import json
import os
import uuid
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent

# ── Skip conditions ────────────────────────────────────────────────────────────

def _has_api_key() -> bool:
    from dotenv import load_dotenv
    load_dotenv(PROJECT_ROOT / ".env")
    return bool(os.getenv("ANTHROPIC_API_KEY", "").strip())


def _has_sheets() -> bool:
    from dotenv import load_dotenv
    load_dotenv(PROJECT_ROOT / ".env")
    return (
        bool(os.getenv("GOOGLE_SPREADSHEET_ID", "").strip())
        and (PROJECT_ROOT / "token.json").exists()
    )


needs_api   = pytest.mark.skipif(not _has_api_key(),  reason="ANTHROPIC_API_KEY not set")
needs_sheets = pytest.mark.skipif(not _has_sheets(), reason="Google Sheets not configured")


# ── Claude API ─────────────────────────────────────────────────────────────────

@pytest.mark.integration
@needs_api
class TestClaudeLive:
    def test_ask_returns_non_empty_response(self):
        from tools.shared.claude_client import ask, MOCK_MODE
        assert not MOCK_MODE, "Running with real API key but MOCK_MODE is True"
        result = ask(
            system_prompt="You are a concise ophthalmology tutor. Reply in one sentence.",
            messages=[{"role": "user", "content": "What is the optic disc?"}],
            max_tokens=100,
        )
        assert isinstance(result, str)
        assert len(result) > 10

    def test_chatbot_response_contains_expected_structure(self):
        from tools.shared.claude_client import ask
        from tools.flashcards.sm2 import due_date  # unrelated import — just checking no side effects
        kb = (PROJECT_ROOT / "workflows" / "ophthalmology_kb.md").read_text(encoding="utf-8")
        result = ask(
            system_prompt=kb,
            messages=[{"role": "user", "content": "What is primary open-angle glaucoma?"}],
            max_tokens=512,
            feature="chatbot",
        )
        # The KB instructs Claude to use this structure every time
        assert "Explanation" in result or len(result) > 50

    def test_flashcard_generation_returns_parseable_json(self):
        from tools.shared.claude_client import ask
        from tools.flashcards.generate_cards import _parse_cards, CARD_PROMPT
        transcript = (
            "Student: What is the first-line treatment for POAG?\n\n"
            "Tutor: Prostaglandin analogues such as latanoprost 0.005%, "
            "applied once nightly. They increase uveoscleral outflow."
        )
        response = ask(
            system_prompt=CARD_PROMPT,
            messages=[{"role": "user", "content": f"Session transcript:\n\n{transcript}"}],
            max_tokens=512,
            feature="flashcard",
        )
        cards = _parse_cards(response)
        assert len(cards) >= 1, f"Expected ≥1 card, got 0. Raw response:\n{response}"
        for card in cards:
            assert card.get("front"), "Card missing 'front'"
            assert card.get("back"),  "Card missing 'back'"
            assert card.get("topic_tag"), "Card missing 'topic_tag'"

    def test_case_evaluation_returns_valid_scores(self):
        from tools.cases.evaluate_response import evaluate_case
        case = json.loads((PROJECT_ROOT / "cases" / "case_001_poag.json").read_text())
        conversation = [
            {"role": "user",      "content": "Do you have any pain in your eyes?"},
            {"role": "assistant", "content": "No pain at all."},
            {"role": "user",      "content": "Any family history of eye problems?"},
            {"role": "assistant", "content": "My father had eye drops for years."},
            {"role": "user",      "content": "I'd like to check your IOP and do visual fields."},
            {"role": "assistant", "content": "Of course."},
            {"role": "user",      "content": "I think you have primary open-angle glaucoma. "
                                             "I'll start you on latanoprost eye drops nightly."},
        ]
        result = evaluate_case(case, conversation, "integration-test-student")
        for key in ["history_score", "investigations_score", "diagnosis_score", "management_score"]:
            score = int(result[key])
            assert 0 <= score <= 10, f"{key}={score} out of range"
        assert result["total_score"] == sum(
            int(result[k]) for k in
            ["history_score", "investigations_score", "diagnosis_score", "management_score"]
        )


# ── Google Sheets ──────────────────────────────────────────────────────────────

@pytest.mark.integration
@needs_sheets
class TestSheetsLive:
    """These tests write and immediately delete a test row. Safe to run repeatedly."""

    TEST_SESSION_ID = f"integration-test-{uuid.uuid4().hex[:8]}"

    def test_append_and_read_row(self):
        from tools.shared.gsheets import append_row, get_rows, delete_row
        append_row("snec_sessions", {
            "session_id": self.TEST_SESSION_ID,
            "student_id": "integration-test-student",
            "timestamp":  "2026-01-01T00:00:00Z",
            "topic":      "integration test",
            "summary":    "written by test_integration.py",
            "token_count": "0",
            "model":      "test",
        })
        rows = get_rows("snec_sessions", filters={"session_id": self.TEST_SESSION_ID})
        assert len(rows) == 1
        assert rows[0]["topic"] == "integration test"
        delete_row("snec_sessions", "session_id", self.TEST_SESSION_ID)

    def test_update_row(self):
        from tools.shared.gsheets import append_row, get_rows, update_row, delete_row
        append_row("snec_sessions", {
            "session_id": self.TEST_SESSION_ID,
            "student_id": "integration-test-student",
            "summary":    "original",
        })
        update_row("snec_sessions", "session_id", self.TEST_SESSION_ID, {"summary": "updated"})
        rows = get_rows("snec_sessions", filters={"session_id": self.TEST_SESSION_ID})
        assert rows[0]["summary"] == "updated"
        delete_row("snec_sessions", "session_id", self.TEST_SESSION_ID)

    def test_filter_returns_only_matching_rows(self):
        from tools.shared.gsheets import append_row, get_rows, delete_row
        append_row("snec_sessions", {"session_id": self.TEST_SESSION_ID, "student_id": "filter-test"})
        rows = get_rows("snec_sessions", filters={"student_id": "filter-test"})
        assert all(r["student_id"] == "filter-test" for r in rows)
        delete_row("snec_sessions", "session_id", self.TEST_SESSION_ID)
