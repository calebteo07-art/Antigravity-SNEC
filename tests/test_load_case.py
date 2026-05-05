"""Tests for the case loader (tools/cases/load_case.py).

Covers local file loading, missing-case errors, and the list helper.
The real sample case (case_001_poag.json) is used for one integration
check to verify the schema hasn't accidentally broken.
"""

import json
from pathlib import Path
from unittest.mock import patch

import pytest

from tools.cases.load_case import list_available_cases, load_case


class TestLoadCase:
    def test_loads_local_json(self, tmp_path):
        data = {"case_id": "test_001", "title": "Test", "difficulty": "beginner"}
        (tmp_path / "test_001.json").write_text(json.dumps(data), encoding="utf-8")

        with patch("tools.cases.load_case.LOCAL_CASES_DIR", tmp_path):
            result = load_case("test_001")

        assert result["case_id"] == "test_001"
        assert result["title"] == "Test"

    def test_raises_file_not_found_for_missing_case(self, tmp_path):
        with patch("tools.cases.load_case.LOCAL_CASES_DIR", tmp_path):
            with pytest.raises(FileNotFoundError, match="not found"):
                load_case("does_not_exist")

    def test_returns_parsed_dict_not_string(self, tmp_path):
        data = {"case_id": "c1", "patient": {"age": 60}}
        (tmp_path / "c1.json").write_text(json.dumps(data), encoding="utf-8")

        with patch("tools.cases.load_case.LOCAL_CASES_DIR", tmp_path):
            result = load_case("c1")

        assert isinstance(result, dict)
        assert result["patient"]["age"] == 60

    def test_error_message_includes_case_id(self, tmp_path):
        with patch("tools.cases.load_case.LOCAL_CASES_DIR", tmp_path):
            with pytest.raises(FileNotFoundError, match="mystery_case"):
                load_case("mystery_case")


class TestListAvailableCases:
    def test_lists_json_files_as_case_ids(self, tmp_path):
        (tmp_path / "case_001.json").write_text("{}")
        (tmp_path / "case_002.json").write_text("{}")

        with patch("tools.cases.load_case.LOCAL_CASES_DIR", tmp_path):
            cases = list_available_cases()

        assert set(cases) == {"case_001", "case_002"}

    def test_ignores_non_json_files(self, tmp_path):
        (tmp_path / "case_001.json").write_text("{}")
        (tmp_path / "notes.txt").write_text("ignore me")
        (tmp_path / "readme.md").write_text("ignore me too")

        with patch("tools.cases.load_case.LOCAL_CASES_DIR", tmp_path):
            cases = list_available_cases()

        assert cases == ["case_001"]

    def test_returns_empty_list_when_directory_missing(self, tmp_path):
        with patch("tools.cases.load_case.LOCAL_CASES_DIR", tmp_path / "no_such_dir"):
            assert list_available_cases() == []

    def test_returns_empty_list_when_no_json_files(self, tmp_path):
        with patch("tools.cases.load_case.LOCAL_CASES_DIR", tmp_path):
            assert list_available_cases() == []


class TestRealSampleCase:
    def test_case_001_poag_loads_and_has_required_fields(self):
        case = load_case("case_001_poag")
        required = ["case_id", "title", "difficulty", "patient",
                    "examination_findings", "investigations", "diagnosis",
                    "management", "rubric"]
        for field in required:
            assert field in case, f"Missing field: {field}"

    def test_case_001_patient_has_name_age_gender(self):
        case = load_case("case_001_poag")
        patient = case["patient"]
        assert patient.get("name")
        assert isinstance(patient.get("age"), int)
        assert patient.get("gender")

    def test_case_001_rubric_has_four_domains(self):
        case = load_case("case_001_poag")
        rubric = case["rubric"]
        for domain in ["history", "investigations", "diagnosis", "management"]:
            assert domain in rubric, f"Missing rubric domain: {domain}"
