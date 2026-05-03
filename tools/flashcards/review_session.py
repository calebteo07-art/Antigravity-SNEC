#!/usr/bin/env python3
"""Agent 12: Flash-card Review — runs an SM-2 spaced repetition review session.

Pulls cards due today for a student, presents them one by one, asks the student
to self-rate their recall, and updates the SM-2 schedule in Google Sheets.

Usage:
    python tools/flashcards/review_session.py
"""

import sys
from datetime import date
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from tools.chatbot.onboarding import run_onboarding
from tools.shared.gsheets import get_rows, update_row
from tools.shared.audit_log import log as audit_log
from tools.flashcards.sm2 import next_review, due_date

QUALITY_GUIDE = """
  How well did you recall this?

  5 - Perfect, immediate recall
  4 - Correct with slight hesitation
  3 - Correct but required effort
  2 - Incorrect — but remembered on seeing answer
  1 - Incorrect — even with answer it was unclear
  0 - Complete blank
"""


def _get_due_cards(student_id: str) -> list[dict]:
    """Return all cards due today or overdue for this student."""
    today = date.today().isoformat()
    rows = get_rows("snec_flashcards", filters={"student_id": student_id})
    return [
        r for r in rows
        if not r.get("next_due_date") or r["next_due_date"] <= today
    ]


def _print_separator(char: str = "─", width: int = 60) -> None:
    print("\n" + char * width + "\n")


def run_review(student_id: str) -> None:
    """Run one full review session for the given student."""
    cards = _get_due_cards(student_id)

    if not cards:
        print("\n  No cards due for review today. Come back tomorrow!\n")
        audit_log("review_none_due", student_id=student_id, feature="flashcards", detail="")
        return

    total = len(cards)
    print(f"\n  You have {total} card(s) due for review.")
    print("  Type 'exit' at any time to stop.\n")
    audit_log("review_start", student_id=student_id, feature="flashcards",
              detail=f"cards_due={total}")

    reviewed = 0
    passed = 0

    for i, card in enumerate(cards, 1):
        _print_separator()
        print(f"  Card {i} of {total}  [{card.get('topic_tag', '')}]")
        print(f"\n  Q: {card['front']}\n")

        try:
            input("  Press Enter to reveal the answer...")
        except (KeyboardInterrupt, EOFError):
            break

        print(f"\n  A: {card['back']}\n")
        print(QUALITY_GUIDE)

        # Get quality rating
        while True:
            try:
                raw = input("  Your rating (0-5): ").strip()
            except (KeyboardInterrupt, EOFError):
                raw = "exit"

            if raw.lower() == "exit":
                print("\n  Review stopped early.")
                break

            if raw.isdigit() and 0 <= int(raw) <= 5:
                quality = int(raw)
                break
            print("  Please enter a number from 0 to 5.")
        else:
            # exit typed
            break

        # Calculate new SM-2 values
        try:
            easiness = float(card.get("easiness_factor") or 2.5)
            interval = int(card.get("interval_days") or 0)
            repetitions = int(card.get("repetition_count") or 0)
        except (ValueError, TypeError):
            easiness, interval, repetitions = 2.5, 0, 0

        new_interval, new_easiness, new_reps = next_review(quality, repetitions, easiness, interval)
        new_due = due_date(new_interval)
        today_str = date.today().isoformat()

        update_row("snec_flashcards", "card_id", card["card_id"], {
            "easiness_factor": f"{new_easiness:.2f}",
            "interval_days": str(new_interval),
            "repetition_count": str(new_reps),
            "next_due_date": new_due,
            "last_reviewed": today_str,
        })

        reviewed += 1
        if quality >= 3:
            passed += 1
            print(f"\n  Next review in {new_interval} day(s).")
        else:
            print(f"\n  Review again tomorrow (needs more practice).")

        audit_log("card_reviewed", student_id=student_id, feature="flashcards",
                  detail=f"card_id={card['card_id']} quality={quality} next={new_due}")

    _print_separator("═")
    if reviewed > 0:
        pct = round(passed / reviewed * 100)
        print(f"  Session complete: {reviewed}/{total} cards reviewed, {pct}% passed.")
    else:
        print("  No cards were reviewed this session.")
    print()

    audit_log("review_end", student_id=student_id, feature="flashcards",
              detail=f"reviewed={reviewed} passed={passed}")


def main() -> None:
    student_id = run_onboarding()
    run_review(student_id)


if __name__ == "__main__":
    main()
