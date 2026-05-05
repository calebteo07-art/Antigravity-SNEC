"""Tests for the audit logger (tools/shared/audit_log.py).

The autouse `isolated_audit_log` fixture in conftest.py redirects
LOG_FILE to tmp_path for every test, so no test touches the real log.
"""

import json
from datetime import datetime
from pathlib import Path
from unittest.mock import patch

import pytest

import tools.shared.audit_log as al
from tools.shared.audit_log import _hash_id, log, read_recent


class TestHashId:
    def test_raw_id_does_not_appear_in_hash(self):
        result = _hash_id("student-abc-123")
        assert "student-abc-123" not in result

    def test_hash_length_is_16(self):
        assert len(_hash_id("any-id")) == 16

    def test_hash_is_deterministic(self):
        assert _hash_id("same-id") == _hash_id("same-id")

    def test_different_ids_produce_different_hashes(self):
        assert _hash_id("student-a") != _hash_id("student-b")


class TestLog:
    def test_creates_log_file(self, tmp_path):
        log_file = al.LOG_FILE   # already redirected by autouse fixture
        log("test_event")
        assert log_file.exists()

    def test_writes_valid_json(self, tmp_path):
        log("test_event", student_id="s1", feature="chatbot", detail="hello")
        entry = json.loads(al.LOG_FILE.read_text().strip())
        assert entry["event_type"] == "test_event"
        assert entry["feature"] == "chatbot"
        assert entry["detail"] == "hello"

    def test_student_id_is_hashed_not_raw(self, tmp_path):
        log("event", student_id="raw-student-id-xyz")
        entry = json.loads(al.LOG_FILE.read_text().strip())
        assert "raw-student-id-xyz" not in entry["student_id"]
        assert len(entry["student_id"]) == 16

    def test_appends_multiple_entries(self, tmp_path):
        log("event_1")
        log("event_2")
        log("event_3")
        lines = al.LOG_FILE.read_text().strip().splitlines()
        assert len(lines) == 3
        types = [json.loads(l)["event_type"] for l in lines]
        assert types == ["event_1", "event_2", "event_3"]

    def test_timestamp_is_valid_iso(self, tmp_path):
        log("event")
        entry = json.loads(al.LOG_FILE.read_text().strip())
        datetime.fromisoformat(entry["timestamp"])  # raises ValueError if invalid

    def test_creates_log_in_tmp_path_directory(self, tmp_path):
        # The autouse fixture already redirects LOG_FILE to tmp_path.
        # Verify the file is created on first write even though it didn't exist.
        assert not al.LOG_FILE.exists()
        log("event")
        assert al.LOG_FILE.exists()

    def test_default_student_id_is_system(self, tmp_path):
        log("event")
        entry = json.loads(al.LOG_FILE.read_text().strip())
        assert entry["student_id"] == _hash_id("system")

    def test_all_required_keys_present(self, tmp_path):
        log("event", student_id="s", feature="f", detail="d")
        entry = json.loads(al.LOG_FILE.read_text().strip())
        assert {"timestamp", "event_type", "student_id", "feature", "detail"} <= entry.keys()


class TestReadRecent:
    def test_returns_empty_list_when_no_file(self, tmp_path):
        # LOG_FILE doesn't exist yet (nothing written)
        result = read_recent(10)
        assert result == []

    def test_returns_all_entries_when_fewer_than_n(self, tmp_path):
        log("e1")
        log("e2")
        result = read_recent(10)
        assert len(result) == 2

    def test_limits_to_last_n_entries(self, tmp_path):
        for i in range(10):
            log(f"event_{i}")
        result = read_recent(3)
        assert len(result) == 3
        assert result[-1]["event_type"] == "event_9"

    def test_entries_are_dicts(self, tmp_path):
        log("event")
        result = read_recent(5)
        assert all(isinstance(r, dict) for r in result)
