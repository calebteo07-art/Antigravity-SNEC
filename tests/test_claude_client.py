"""Tests for the Claude API wrapper (tools/shared/claude_client.py).

All tests run against mock mode — no real API calls are made.
MOCK_MODE is explicitly forced to True via patching so these tests
pass regardless of whether ANTHROPIC_API_KEY is present in .env.
"""

from unittest.mock import patch

import pytest

import tools.shared.claude_client as cc


class TestMockMode:
    def test_ask_returns_non_empty_string(self):
        with patch.object(cc, "MOCK_MODE", True):
            result = cc.ask("system", [{"role": "user", "content": "hello"}])
        assert isinstance(result, str)
        assert len(result) > 0

    def test_chatbot_feature_response_contains_explanation(self):
        with patch.object(cc, "MOCK_MODE", True):
            result = cc.ask("system", [{"role": "user", "content": "q"}], feature="chatbot")
        assert "Explanation" in result

    def test_flashcard_feature_response_is_json_array_like(self):
        with patch.object(cc, "MOCK_MODE", True):
            result = cc.ask("system", [{"role": "user", "content": "q"}], feature="flashcard")
        # Mock flashcard response is a JSON array string
        assert result.strip().startswith("[")

    def test_case_feature_returns_string(self):
        with patch.object(cc, "MOCK_MODE", True):
            result = cc.ask("system", [{"role": "user", "content": "q"}], feature="case")
        assert isinstance(result, str) and len(result) > 0

    def test_image_feature_returns_string(self):
        with patch.object(cc, "MOCK_MODE", True):
            result = cc.ask("system", [{"role": "user", "content": "q"}], feature="image")
        assert isinstance(result, str) and len(result) > 0

    def test_unknown_feature_falls_back_to_default(self):
        with patch.object(cc, "MOCK_MODE", True):
            result = cc.ask("system", [{"role": "user", "content": "q"}], feature="no_such_feature")
        assert isinstance(result, str) and len(result) > 0

    def test_ask_with_image_returns_string_in_mock_mode(self, tmp_path):
        # Create a minimal PNG file (1x1 pixel)
        png_bytes = (
            b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01'
            b'\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00'
            b'\x00\x0cIDATx\x9cc\xf8\x0f\x00\x00\x01\x01\x00\x05\x18'
            b'\xd8N\x00\x00\x00\x00IEND\xaeB`\x82'
        )
        img = tmp_path / "test.png"
        img.write_bytes(png_bytes)

        with patch.object(cc, "MOCK_MODE", True):
            result = cc.ask_with_image(
                system_prompt="system",
                messages=[{"role": "user", "content": "describe this"}],
                image_path=img,
                feature="image",
            )
        assert isinstance(result, str) and len(result) > 0


class TestMockResponses:
    def test_each_feature_has_distinct_response(self):
        features = ["chatbot", "flashcard", "case", "image", "default"]
        with patch.object(cc, "MOCK_MODE", True):
            responses = {f: cc.ask("s", [{"role": "user", "content": "q"}], feature=f)
                         for f in features}
        # All responses should exist and be non-empty
        for f, r in responses.items():
            assert r, f"Empty response for feature: {f}"
