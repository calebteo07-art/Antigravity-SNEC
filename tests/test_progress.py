"""Tests for the XP/level/badge progress system (tools/shared/progress.py).

All functions under test are pure Python — no network calls, no Sheets.
The get_progress / update_progress Sheets integration is tested separately
via mocked gspread in test_gsheets.py.
"""

import pytest

from tools.shared.progress import LEVELS, calculate_xp_reward, get_level_info


class TestGetLevelInfo:
    def test_zero_xp_is_level_1_med_student(self):
        info = get_level_info(0)
        assert info["level_num"] == 1
        assert info["name"] == "Med Student"

    def test_every_threshold_maps_to_correct_level(self):
        for i, (threshold, name, _) in enumerate(LEVELS):
            info = get_level_info(threshold)
            assert info["level_num"] == i + 1, f"XP={threshold} should be level {i + 1}"
            assert info["name"] == name

    def test_just_below_threshold_stays_at_lower_level(self):
        # 499 XP should still be Level 1, not Level 2 (500 threshold)
        info = get_level_info(499)
        assert info["level_num"] == 1

    def test_max_level_has_no_next_threshold(self):
        info = get_level_info(15000)
        assert info["level_num"] == len(LEVELS)
        assert info["next_threshold"] is None
        assert info["xp_to_next"] == 0
        assert info["progress_pct"] == 1.0

    def test_above_max_level_stays_at_max(self):
        info = get_level_info(999_999)
        assert info["level_num"] == len(LEVELS)

    def test_progress_pct_is_between_0_and_1(self):
        info = get_level_info(750)  # between 500 (L2) and 1200 (L3)
        assert 0.0 <= info["progress_pct"] <= 1.0

    def test_xp_to_next_correct(self):
        # At 700 XP: Level 2 (500), next at 1200 → 500 XP remaining
        info = get_level_info(700)
        assert info["xp_to_next"] == 500

    def test_returns_icon(self):
        info = get_level_info(0)
        assert info["icon"]  # non-empty

    def test_returns_all_expected_keys(self):
        info = get_level_info(100)
        expected = {"level_num", "name", "icon", "threshold", "next_threshold",
                    "next_name", "xp_to_next", "progress_pct"}
        assert expected <= info.keys()


class TestCalculateXpReward:
    def _result(self, h=8, inv=8, d=8, m=8):
        total = h + inv + d + m
        return {
            "history_score": h, "investigations_score": inv,
            "diagnosis_score": d, "management_score": m,
            "total_score": total,
        }

    # ── Base XP ──────────────────────────────────────────────────────────────

    def test_base_xp_is_score_times_10(self):
        result = self._result(h=6, inv=6, d=6, m=6)  # total 24
        xp = calculate_xp_reward(result, message_count=10, is_first_case=False,
                                 hints_used=0, cases_completed=1)
        assert xp["base_xp"] == 240

    def test_zero_score_zero_base_xp(self):
        result = self._result(h=0, inv=0, d=0, m=0)
        xp = calculate_xp_reward(result, message_count=10, is_first_case=False,
                                 hints_used=0, cases_completed=1)
        assert xp["base_xp"] == 0

    def test_perfect_score_400_base_xp(self):
        result = self._result(h=10, inv=10, d=10, m=10)
        xp = calculate_xp_reward(result, message_count=10, is_first_case=False,
                                 hints_used=0, cases_completed=1)
        assert xp["base_xp"] == 400

    # ── Per-domain perfect bonuses ────────────────────────────────────────────

    def test_perfect_history_gives_50_bonus_and_badge(self):
        result = self._result(h=10, inv=7, d=7, m=7)
        xp = calculate_xp_reward(result, message_count=10, is_first_case=False,
                                 hints_used=0, cases_completed=1)
        assert ("Perfect History", 50) in xp["bonuses"]
        assert "perfect_history" in xp["new_badges"]

    def test_perfect_investigations_gives_50_bonus_and_badge(self):
        result = self._result(h=7, inv=10, d=7, m=7)
        xp = calculate_xp_reward(result, message_count=10, is_first_case=False,
                                 hints_used=0, cases_completed=1)
        assert ("Perfect Investigations", 50) in xp["bonuses"]
        assert "perfect_investigations" in xp["new_badges"]

    def test_all_four_perfect_domains_give_200_total_bonus(self):
        result = self._result(h=10, inv=10, d=10, m=10)
        xp = calculate_xp_reward(result, message_count=10, is_first_case=False,
                                 hints_used=0, cases_completed=1)
        domain_bonus = sum(v for _, v in xp["bonuses"] if v == 50)
        assert domain_bonus == 200

    def test_imperfect_domain_gives_no_bonus(self):
        result = self._result(h=9, inv=7, d=7, m=7)
        xp = calculate_xp_reward(result, message_count=10, is_first_case=False,
                                 hints_used=0, cases_completed=1)
        bonus_names = [n for n, _ in xp["bonuses"]]
        assert "Perfect History" not in bonus_names

    # ── Flawless case bonus ───────────────────────────────────────────────────

    def test_perfect_40_40_gives_flawless_bonus_and_badge(self):
        result = self._result(h=10, inv=10, d=10, m=10)
        xp = calculate_xp_reward(result, message_count=10, is_first_case=False,
                                 hints_used=0, cases_completed=1)
        bonus_names = [n for n, _ in xp["bonuses"]]
        assert "Flawless Case!" in bonus_names
        assert "perfect_case" in xp["new_badges"]

    def test_39_40_gives_no_flawless_bonus(self):
        result = self._result(h=10, inv=10, d=10, m=9)
        xp = calculate_xp_reward(result, message_count=10, is_first_case=False,
                                 hints_used=0, cases_completed=1)
        bonus_names = [n for n, _ in xp["bonuses"]]
        assert "Flawless Case!" not in bonus_names

    # ── First case bonus ──────────────────────────────────────────────────────

    def test_first_case_bonus_100_xp(self):
        result = self._result()
        xp = calculate_xp_reward(result, message_count=10, is_first_case=True,
                                 hints_used=0, cases_completed=0)
        bonus_names = [n for n, _ in xp["bonuses"]]
        assert "First Case Bonus" in bonus_names
        assert ("First Case Bonus", 100) in xp["bonuses"]
        assert "first_case" in xp["new_badges"]

    def test_returning_student_gets_no_first_case_bonus(self):
        result = self._result()
        xp = calculate_xp_reward(result, message_count=10, is_first_case=False,
                                 hints_used=0, cases_completed=5)
        bonus_names = [n for n, _ in xp["bonuses"]]
        assert "First Case Bonus" not in bonus_names

    # ── Speed bonus ───────────────────────────────────────────────────────────

    def test_speed_bonus_at_exactly_8_messages(self):
        result = self._result()
        xp = calculate_xp_reward(result, message_count=8, is_first_case=False,
                                 hints_used=0, cases_completed=1)
        assert "speed_demon" in xp["new_badges"]
        assert any("Speed" in n for n, _ in xp["bonuses"])

    def test_speed_bonus_at_fewer_than_8_messages(self):
        result = self._result()
        xp = calculate_xp_reward(result, message_count=3, is_first_case=False,
                                 hints_used=0, cases_completed=1)
        assert "speed_demon" in xp["new_badges"]

    def test_no_speed_bonus_at_9_messages(self):
        result = self._result()
        xp = calculate_xp_reward(result, message_count=9, is_first_case=False,
                                 hints_used=0, cases_completed=1)
        assert "speed_demon" not in xp["new_badges"]

    # ── Veteran badge ─────────────────────────────────────────────────────────

    def test_veteran_badge_when_completing_5th_case(self):
        result = self._result()
        xp = calculate_xp_reward(result, message_count=10, is_first_case=False,
                                 hints_used=0, cases_completed=4)  # +1 = 5
        assert "veteran" in xp["new_badges"]

    def test_no_veteran_badge_on_4th_case(self):
        result = self._result()
        xp = calculate_xp_reward(result, message_count=10, is_first_case=False,
                                 hints_used=0, cases_completed=3)  # +1 = 4
        assert "veteran" not in xp["new_badges"]

    # ── No-hints badge ────────────────────────────────────────────────────────

    def test_no_hints_badge_when_zero_hints_used(self):
        result = self._result()
        xp = calculate_xp_reward(result, message_count=10, is_first_case=False,
                                 hints_used=0, cases_completed=1)
        assert "no_hints" in xp["new_badges"]

    def test_no_hints_badge_absent_when_hints_used(self):
        result = self._result()
        xp = calculate_xp_reward(result, message_count=10, is_first_case=False,
                                 hints_used=1, cases_completed=1)
        assert "no_hints" not in xp["new_badges"]

    # ── Hint penalties ────────────────────────────────────────────────────────

    def test_one_hint_costs_20_xp(self):
        result = self._result()
        xp = calculate_xp_reward(result, message_count=10, is_first_case=False,
                                 hints_used=1, cases_completed=1)
        assert len(xp["penalties"]) == 1
        _, penalty = xp["penalties"][0]
        assert penalty == -20

    def test_three_hints_costs_60_xp(self):
        result = self._result()
        xp = calculate_xp_reward(result, message_count=10, is_first_case=False,
                                 hints_used=3, cases_completed=1)
        _, penalty = xp["penalties"][0]
        assert penalty == -60

    def test_no_penalties_when_no_hints(self):
        result = self._result()
        xp = calculate_xp_reward(result, message_count=10, is_first_case=False,
                                 hints_used=0, cases_completed=1)
        assert xp["penalties"] == []

    # ── Total XP guard ────────────────────────────────────────────────────────

    def test_total_xp_never_negative(self):
        # Zero score + max hints — should floor at 0, not go negative
        result = self._result(h=0, inv=0, d=0, m=0)
        xp = calculate_xp_reward(result, message_count=10, is_first_case=False,
                                 hints_used=3, cases_completed=1)
        assert xp["total_xp"] >= 0

    def test_total_xp_accounts_for_all_bonuses_and_penalties(self):
        result = self._result(h=8, inv=8, d=8, m=8)  # total 32, base 320
        xp = calculate_xp_reward(result, message_count=10, is_first_case=False,
                                 hints_used=1, cases_completed=1)
        bonus_sum   = sum(v for _, v in xp["bonuses"])
        penalty_sum = sum(v for _, v in xp["penalties"])
        expected    = max(0, xp["base_xp"] + bonus_sum + penalty_sum)
        assert xp["total_xp"] == expected
