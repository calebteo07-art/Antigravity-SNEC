#!/usr/bin/env python3
"""SM-2 spaced repetition algorithm for the SNEC flash-card engine.

SM-2 calculates how many days to wait before showing a card again,
based on how well the student answered (quality score 0-5).

Reference: SuperMemo SM-2 algorithm (Wozniak, 1987)

Usage (from other tools):
    from tools.flashcards.sm2 import next_review

Self-test:
    python tools/flashcards/sm2.py
"""

import sys
from datetime import date, timedelta


def next_review(
    quality: int,
    repetitions: int,
    easiness: float,
    interval: int,
) -> tuple[int, float, int]:
    """
    Calculate the next review schedule using SM-2.

    Args:
        quality:    Student's answer quality, 0-5:
                    5 = perfect recall
                    4 = correct with slight hesitation
                    3 = correct with difficulty
                    2 = incorrect but remembered on seeing answer
                    1 = incorrect, remembered with hint
                    0 = complete blackout
        repetitions: Number of times card has been reviewed successfully (>=3).
        easiness:    Easiness factor, starts at 2.5, minimum 1.3.
        interval:    Current interval in days.

    Returns:
        (new_interval, new_easiness, new_repetitions)
    """
    # Clamp quality to valid range
    quality = max(0, min(5, quality))

    # Update easiness factor
    new_easiness = easiness + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02))
    new_easiness = max(1.3, new_easiness)

    if quality < 3:
        # Failed — reset repetitions, review again soon
        new_repetitions = 0
        new_interval = 1
    else:
        # Passed — advance the schedule
        new_repetitions = repetitions + 1
        if new_repetitions == 1:
            new_interval = 1
        elif new_repetitions == 2:
            new_interval = 6
        else:
            new_interval = round(interval * new_easiness)

    return new_interval, new_easiness, new_repetitions


def due_date(interval: int) -> str:
    """Return ISO date string for next review, `interval` days from today."""
    return (date.today() + timedelta(days=interval)).isoformat()


if __name__ == "__main__":
    print("Testing sm2.py...\n")

    # First review — perfect recall
    interval, easiness, reps = next_review(5, 0, 2.5, 0)
    assert interval == 1 and reps == 1
    print(f"  Review 1 (quality=5): interval={interval}d, easiness={easiness:.2f}, reps={reps}")

    # Second review
    interval, easiness, reps = next_review(5, reps, easiness, interval)
    assert interval == 6 and reps == 2
    print(f"  Review 2 (quality=5): interval={interval}d, easiness={easiness:.2f}, reps={reps}")

    # Third review
    interval, easiness, reps = next_review(4, reps, easiness, interval)
    assert interval > 6 and reps == 3
    print(f"  Review 3 (quality=4): interval={interval}d, easiness={easiness:.2f}, reps={reps}")

    # Failed review — resets
    interval, easiness, reps = next_review(1, reps, easiness, interval)
    assert interval == 1 and reps == 0
    print(f"  Review 4 (quality=1): interval={interval}d, easiness={easiness:.2f}, reps={reps}")

    # Easiness never drops below 1.3
    for _ in range(20):
        _, easiness, _ = next_review(0, 0, easiness, 1)
    assert easiness >= 1.3
    print(f"  Easiness floor held at: {easiness:.2f}")

    print("\n  [PASS] sm2.py working correctly.")
    sys.exit(0)
