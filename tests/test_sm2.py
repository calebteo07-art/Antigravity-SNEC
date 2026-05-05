"""Tests for the SM-2 spaced repetition algorithm (tools/flashcards/sm2.py).

SM-2 is pure Python with no external dependencies — these tests run
completely offline and cover the algorithm's core invariants.
"""

from datetime import date, timedelta

import pytest

from tools.flashcards.sm2 import due_date, next_review


class TestNextReview:
    # ── First two reviews have fixed intervals per SM-2 spec ────────────────

    def test_first_review_sets_interval_to_1(self):
        interval, _, reps = next_review(quality=5, repetitions=0, easiness=2.5, interval=0)
        assert interval == 1
        assert reps == 1

    def test_second_review_sets_interval_to_6(self):
        interval, _, reps = next_review(quality=5, repetitions=1, easiness=2.5, interval=1)
        assert interval == 6
        assert reps == 2

    def test_third_review_multiplies_by_easiness(self):
        # SM-2 multiplies by the *updated* easiness, not the input value.
        # quality=5, easiness=2.5 → new_easiness=2.6, so interval = round(6 * 2.6) = 16
        interval, new_ef, reps = next_review(quality=5, repetitions=2, easiness=2.5, interval=6)
        assert interval == round(6 * new_ef)
        assert reps == 3

    # ── Failure resets the schedule ──────────────────────────────────────────

    def test_quality_below_3_resets_repetitions(self):
        _, _, reps = next_review(quality=2, repetitions=10, easiness=2.5, interval=30)
        assert reps == 0

    def test_quality_below_3_resets_interval_to_1(self):
        interval, _, _ = next_review(quality=2, repetitions=10, easiness=2.5, interval=30)
        assert interval == 1

    def test_quality_exactly_3_does_not_reset(self):
        _, _, reps = next_review(quality=3, repetitions=5, easiness=2.5, interval=10)
        assert reps == 6

    # ── Easiness factor behaviour ────────────────────────────────────────────

    def test_perfect_recall_increases_easiness(self):
        _, new_ef, _ = next_review(quality=5, repetitions=0, easiness=2.5, interval=0)
        assert new_ef > 2.5

    def test_hard_recall_decreases_easiness(self):
        _, new_ef, _ = next_review(quality=3, repetitions=0, easiness=2.5, interval=0)
        assert new_ef < 2.5

    def test_easiness_floor_is_1_3(self):
        ef = 2.5
        for _ in range(50):
            _, ef, _ = next_review(quality=0, repetitions=0, easiness=ef, interval=1)
        assert ef >= 1.3

    def test_easiness_floor_holds_exactly_at_repeated_zeroes(self):
        _, ef, _ = next_review(quality=0, repetitions=0, easiness=1.3, interval=1)
        assert ef >= 1.3

    # ── Input clamping ───────────────────────────────────────────────────────

    def test_quality_above_5_clamped_to_5(self):
        iv1, ef1, r1 = next_review(quality=5,  repetitions=0, easiness=2.5, interval=0)
        iv2, ef2, r2 = next_review(quality=99, repetitions=0, easiness=2.5, interval=0)
        assert iv1 == iv2 and abs(ef1 - ef2) < 1e-9 and r1 == r2

    def test_quality_below_0_clamped_to_0(self):
        iv1, ef1, r1 = next_review(quality=0,   repetitions=3, easiness=2.5, interval=15)
        iv2, ef2, r2 = next_review(quality=-10, repetitions=3, easiness=2.5, interval=15)
        assert iv1 == iv2 and abs(ef1 - ef2) < 1e-9 and r1 == r2

    # ── Return type ──────────────────────────────────────────────────────────

    def test_returns_three_tuple(self):
        result = next_review(quality=4, repetitions=0, easiness=2.5, interval=0)
        assert len(result) == 3

    def test_interval_is_int(self):
        interval, _, _ = next_review(quality=4, repetitions=0, easiness=2.5, interval=0)
        assert isinstance(interval, int)

    def test_repetitions_is_int(self):
        _, _, reps = next_review(quality=4, repetitions=0, easiness=2.5, interval=0)
        assert isinstance(reps, int)


class TestDueDate:
    def test_zero_interval_returns_today(self):
        assert due_date(0) == date.today().isoformat()

    def test_interval_adds_correct_days(self):
        expected = (date.today() + timedelta(days=7)).isoformat()
        assert due_date(7) == expected

    def test_returns_iso_format_string(self):
        result = due_date(3)
        # Should parse without error
        date.fromisoformat(result)

    def test_large_interval(self):
        expected = (date.today() + timedelta(days=365)).isoformat()
        assert due_date(365) == expected
