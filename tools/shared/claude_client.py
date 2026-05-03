#!/usr/bin/env python3
"""Shared Claude API wrapper — all Anthropic API calls in the SNEC platform go through here.

Automatically runs in MOCK_MODE when ANTHROPIC_API_KEY is not set, returning
structured fake responses so all features can be built and tested without an API key.
Switch to live mode by adding ANTHROPIC_API_KEY to .env.

Usage (from other tools):
    from tools.shared.claude_client import ask, ask_with_image

Self-test:
    python tools/shared/claude_client.py
"""

import base64
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
load_dotenv(PROJECT_ROOT / ".env")

MODEL = "claude-sonnet-4-6"
API_KEY = os.getenv("ANTHROPIC_API_KEY", "").strip()
MOCK_MODE = not API_KEY

# Canned mock responses keyed by feature — realistic enough to test downstream logic
_MOCK_RESPONSES: dict[str, str] = {
    "chatbot": (
        "**Explanation:** Glaucoma is a group of eye conditions that damage the optic nerve, "
        "often caused by elevated intraocular pressure.\n\n"
        "**Mechanism:** Increased IOP compresses retinal ganglion cell axons at the lamina cribrosa, "
        "leading to progressive axonal death and visual field loss.\n\n"
        "**Clinical Pearl:** Normal-tension glaucoma occurs despite IOP within the normal range (10-21 mmHg), "
        "suggesting vascular and other factors also play a role.\n\n"
        "**Check Your Understanding:** What is the first-line treatment for open-angle glaucoma?"
    ),
    "flashcard": (
        '[{"front": "What is the most common type of glaucoma?", '
        '"back": "Primary open-angle glaucoma (POAG)", "topic_tag": "glaucoma"}, '
        '{"front": "Normal IOP range", "back": "10-21 mmHg", "topic_tag": "glaucoma"}, '
        '{"front": "First-line treatment for POAG", '
        '"back": "Prostaglandin analogue eye drops (e.g. latanoprost)", "topic_tag": "glaucoma"}]'
    ),
    "case": (
        "HISTORY: 65-year-old male presenting with gradual peripheral vision loss over 2 years. "
        "No pain. Family history of glaucoma.\n\n"
        "SCORE: History 8/10, Investigations 7/10, Diagnosis 9/10, Management 8/10\n\n"
        "FEEDBACK: Good systematic approach. Consider asking about medication history earlier. "
        "Correct diagnosis of POAG. Management plan appropriate — include follow-up interval."
    ),
    "image": (
        "FINDINGS: Optic disc shows increased cup-to-disc ratio (0.7). "
        "Superior and inferior notching of the neuroretinal rim. "
        "Peripapillary atrophy present. No obvious haemorrhages identified.\n\n"
        "DIAGNOSIS: Appearances consistent with glaucomatous optic neuropathy. "
        "Recommend visual field testing and OCT RNFL analysis."
    ),
    "default": "[MOCK] This is a mock response. Add ANTHROPIC_API_KEY to .env to use the real Claude API.",
}


def _mock_response(feature: str = "default") -> str:
    return _MOCK_RESPONSES.get(feature, _MOCK_RESPONSES["default"])


def ask(
    system_prompt: str,
    messages: list[dict],
    max_tokens: int = 1024,
    feature: str = "default",
) -> str:
    """
    Send a conversation to Claude and return the response text.

    Args:
        system_prompt: The system prompt (cached for cost efficiency in live mode).
        messages:      Conversation history as list of {"role": "user"/"assistant", "content": str}.
        max_tokens:    Maximum tokens in the response.
        feature:       Feature name for mock routing: "chatbot", "flashcard", "case", "image".

    Returns:
        Response text as a string.
    """
    if MOCK_MODE:
        return _mock_response(feature)

    import anthropic
    client = anthropic.Anthropic(api_key=API_KEY)

    response = client.messages.create(
        model=MODEL,
        max_tokens=max_tokens,
        system=[
            {
                "type": "text",
                "text": system_prompt,
                "cache_control": {"type": "ephemeral"},
            }
        ],
        messages=messages,
    )
    return response.content[0].text


def ask_with_image(
    system_prompt: str,
    messages: list[dict],
    image_path: str | Path,
    max_tokens: int = 1024,
    feature: str = "image",
) -> str:
    """
    Send a conversation with an image attachment to Claude.

    Args:
        system_prompt: The system prompt.
        messages:      Conversation history.
        image_path:    Path to a local image file (JPG, PNG, GIF, WEBP).
        max_tokens:    Maximum tokens in the response.
        feature:       Feature name for mock routing.

    Returns:
        Response text as a string.
    """
    if MOCK_MODE:
        return _mock_response(feature)

    import anthropic

    image_path = Path(image_path)
    suffix = image_path.suffix.lower()
    media_type_map = {
        ".jpg": "image/jpeg", ".jpeg": "image/jpeg",
        ".png": "image/png", ".gif": "image/gif", ".webp": "image/webp",
    }
    media_type = media_type_map.get(suffix, "image/jpeg")
    image_data = base64.standard_b64encode(image_path.read_bytes()).decode("utf-8")

    # Attach image to the last user message
    enriched_messages = list(messages)
    last_user = next(
        (i for i in range(len(enriched_messages) - 1, -1, -1)
         if enriched_messages[i]["role"] == "user"), None
    )
    if last_user is not None:
        original_content = enriched_messages[last_user]["content"]
        enriched_messages[last_user] = {
            "role": "user",
            "content": [
                {"type": "image", "source": {"type": "base64", "media_type": media_type, "data": image_data}},
                {"type": "text", "text": original_content},
            ],
        }

    import anthropic
    client = anthropic.Anthropic(api_key=API_KEY)

    response = client.messages.create(
        model=MODEL,
        max_tokens=max_tokens,
        system=[{"type": "text", "text": system_prompt, "cache_control": {"type": "ephemeral"}}],
        messages=enriched_messages,
    )
    return response.content[0].text


if __name__ == "__main__":
    print("Testing claude_client.py...\n")

    mode = "MOCK" if MOCK_MODE else "LIVE"
    print(f"  Mode: {mode}")

    # Test ask()
    print("  Testing ask() - chatbot feature...")
    response = ask(
        system_prompt="You are an ophthalmology tutor.",
        messages=[{"role": "user", "content": "Explain glaucoma."}],
        feature="chatbot",
    )
    assert len(response) > 10, "Response too short"
    print(f"  [OK] Response ({len(response)} chars): {response[:80]}...")

    # Test ask() - flashcard feature
    print("  Testing ask() - flashcard feature...")
    response = ask(
        system_prompt="You are a flash-card generator.",
        messages=[{"role": "user", "content": "Generate cards for glaucoma."}],
        feature="flashcard",
    )
    assert len(response) > 10
    print(f"  [OK] Response ({len(response)} chars): {response[:80]}...")

    if MOCK_MODE:
        print("\n  Running in MOCK mode — no API calls made.")
        print("  Add ANTHROPIC_API_KEY to .env to test live mode.")
    else:
        print("\n  Running in LIVE mode — real API calls used.")

    print("\n  [PASS] claude_client.py working correctly.")
    sys.exit(0)
