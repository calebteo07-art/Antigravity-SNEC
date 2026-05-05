"""Tests for the Google Sheets CRUD wrapper (tools/shared/gsheets.py).

All tests patch _get_spreadsheet() so no real Google credentials or
network connection are needed.
"""

from unittest.mock import MagicMock, call, patch

import pytest

from tools.shared.gsheets import append_row, get_rows, update_row


# ── Shared fixtures ────────────────────────────────────────────────────────────

@pytest.fixture
def headers():
    return ["session_id", "student_id", "timestamp", "topic", "summary"]


@pytest.fixture
def mock_sheet(headers):
    ws = MagicMock()
    ws.row_values.return_value = headers
    ws.get_all_records.return_value = [
        {"session_id": "s1", "student_id": "stu1", "timestamp": "2026-01-01",
         "topic": "glaucoma", "summary": "first session"},
        {"session_id": "s2", "student_id": "stu2", "timestamp": "2026-01-02",
         "topic": "retina", "summary": "second session"},
    ]
    return ws


@pytest.fixture
def mock_ss(mock_sheet):
    ss = MagicMock()
    ss.worksheet.return_value = mock_sheet
    return ss


# ── get_rows ───────────────────────────────────────────────────────────────────

class TestGetRows:
    def test_returns_all_rows_with_no_filter(self, mock_ss):
        with patch("tools.shared.gsheets._get_spreadsheet", return_value=mock_ss):
            rows = get_rows("snec_sessions")
        assert len(rows) == 2

    def test_filter_by_single_column(self, mock_ss):
        with patch("tools.shared.gsheets._get_spreadsheet", return_value=mock_ss):
            rows = get_rows("snec_sessions", filters={"student_id": "stu1"})
        assert len(rows) == 1
        assert rows[0]["session_id"] == "s1"

    def test_returns_empty_list_when_no_match(self, mock_ss):
        with patch("tools.shared.gsheets._get_spreadsheet", return_value=mock_ss):
            rows = get_rows("snec_sessions", filters={"student_id": "nobody"})
        assert rows == []

    def test_multiple_filters_are_anded(self, mock_ss, mock_sheet):
        mock_sheet.get_all_records.return_value = [
            {"student_id": "stu1", "topic": "glaucoma", "session_id": "s1"},
            {"student_id": "stu1", "topic": "retina",   "session_id": "s2"},
            {"student_id": "stu2", "topic": "glaucoma", "session_id": "s3"},
        ]
        with patch("tools.shared.gsheets._get_spreadsheet", return_value=mock_ss):
            rows = get_rows("snec_sessions",
                            filters={"student_id": "stu1", "topic": "glaucoma"})
        assert len(rows) == 1
        assert rows[0]["session_id"] == "s1"

    def test_filter_value_coerced_to_string(self, mock_ss, mock_sheet):
        # Sheet values are strings; filter value 123 (int) should still match "123"
        mock_sheet.get_all_records.return_value = [
            {"card_id": "c1", "interval_days": "7"},
        ]
        with patch("tools.shared.gsheets._get_spreadsheet", return_value=mock_ss):
            rows = get_rows("snec_flashcards", filters={"interval_days": 7})
        assert len(rows) == 1


# ── append_row ─────────────────────────────────────────────────────────────────

class TestAppendRow:
    def test_appends_values_in_header_order(self, mock_ss, mock_sheet, headers):
        with patch("tools.shared.gsheets._get_spreadsheet", return_value=mock_ss):
            append_row("snec_sessions", {
                "session_id": "abc",
                "student_id": "xyz",
                "timestamp":  "2026-01-01",
                "topic":      "cornea",
                "summary":    "test",
            })
        mock_sheet.append_row.assert_called_once_with(
            ["abc", "xyz", "2026-01-01", "cornea", "test"],
            value_input_option="RAW",
        )

    def test_missing_keys_default_to_empty_string(self, mock_ss, mock_sheet):
        mock_sheet.row_values.return_value = ["a", "b", "c"]
        with patch("tools.shared.gsheets._get_spreadsheet", return_value=mock_ss):
            append_row("snec_sessions", {"a": "val_a"})   # b and c missing
        mock_sheet.append_row.assert_called_once_with(
            ["val_a", "", ""],
            value_input_option="RAW",
        )

    def test_extra_keys_are_ignored(self, mock_ss, mock_sheet):
        mock_sheet.row_values.return_value = ["a", "b"]
        with patch("tools.shared.gsheets._get_spreadsheet", return_value=mock_ss):
            append_row("snec_sessions", {"a": "1", "b": "2", "z": "ignored"})
        mock_sheet.append_row.assert_called_once_with(["1", "2"], value_input_option="RAW")

    def test_values_are_stringified(self, mock_ss, mock_sheet):
        mock_sheet.row_values.return_value = ["score"]
        with patch("tools.shared.gsheets._get_spreadsheet", return_value=mock_ss):
            append_row("snec_sessions", {"score": 42})   # int, not string
        mock_sheet.append_row.assert_called_once_with(["42"], value_input_option="RAW")


# ── update_row ─────────────────────────────────────────────────────────────────

class TestUpdateRow:
    def test_updates_correct_cell(self, mock_ss, mock_sheet):
        mock_sheet.row_values.return_value = ["session_id", "student_id", "summary"]
        mock_cell = MagicMock()
        mock_cell.row = 3
        mock_sheet.find.return_value = mock_cell

        with patch("tools.shared.gsheets._get_spreadsheet", return_value=mock_ss):
            result = update_row("snec_sessions", "session_id", "abc", {"summary": "updated"})

        assert result is True
        # summary is column index 3 (1-based)
        mock_sheet.update_cell.assert_called_once_with(3, 3, "updated")

    def test_returns_false_when_row_not_found(self, mock_ss, mock_sheet):
        mock_sheet.row_values.return_value = ["session_id", "summary"]
        mock_sheet.find.return_value = None

        with patch("tools.shared.gsheets._get_spreadsheet", return_value=mock_ss):
            result = update_row("snec_sessions", "session_id", "missing", {"summary": "x"})

        assert result is False
        mock_sheet.update_cell.assert_not_called()

    def test_raises_value_error_for_invalid_match_column(self, mock_ss, mock_sheet):
        mock_sheet.row_values.return_value = ["session_id", "summary"]

        with patch("tools.shared.gsheets._get_spreadsheet", return_value=mock_ss):
            with pytest.raises(ValueError, match="not found in sheet"):
                update_row("snec_sessions", "nonexistent_col", "val", {"summary": "x"})

    def test_updates_multiple_columns(self, mock_ss, mock_sheet):
        mock_sheet.row_values.return_value = ["id", "col_a", "col_b", "col_c"]
        mock_cell = MagicMock()
        mock_cell.row = 2
        mock_sheet.find.return_value = mock_cell

        with patch("tools.shared.gsheets._get_spreadsheet", return_value=mock_ss):
            update_row("sheet", "id", "x", {"col_a": "v1", "col_c": "v3"})

        calls = mock_sheet.update_cell.call_args_list
        assert call(2, 2, "v1") in calls   # col_a is column 2
        assert call(2, 4, "v3") in calls   # col_c is column 4
