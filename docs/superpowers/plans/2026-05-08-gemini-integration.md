# Gemini API Integration Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the Anthropic Claude API with the Google Gemini API in `tools/shared/claude_client.py` while keeping the public interface (`ask`, `ask_with_image`, `MODEL`, `MODEL_SMALL`) identical so all 7 callers remain untouched.

**Architecture:** Rewrite only the internals of `claude_client.py`. Add a pure helper `_to_gemini_history()` that converts Anthropic-style message dicts (`"assistant"` role) to Gemini-style (`"model"` role). Vision calls use `PIL.Image` inline instead of base64. Mock mode triggers on missing `GEMINI_API_KEY`.

**Tech Stack:** `google-generativeai>=0.8.0`, `Pillow` (already installed), `pytest`

---

## File Map

| Action | Path | Responsibility |
|--------|------|----------------|
| Modify | `requirements.txt` | Swap `anthropic` → `google-generativeai` |
| Modify | `.env.example` | Swap `ANTHROPIC_API_KEY` → `GEMINI_API_KEY` |
| Create | `tests/__init__.py` | Make tests a package |
| Create | `tests/shared/__init__.py` | Make tests/shared a package |
| Create | `tests/shared/test_claude_client.py` | Unit tests for conversion + mock mode |
| Modify | `tools/shared/claude_client.py` | Rewrite internals to use Gemini SDK |

---

### Task 1: Update requirements.txt

**Files:**
- Modify: `requirements.txt`

- [ ] **Step 1: Replace the anthropic dependency**

Open `requirements.txt` and change line 6 from:
```
anthropic>=0.40.0
```
to:
```
google-generativeai>=0.8.0
```

- [ ] **Step 2: Install the new dependency**

```bash
pip install -r requirements.txt
```

Expected: `google-generativeai` installs successfully. You may see a note that `anthropic` is no longer listed — that is expected.

- [ ] **Step 3: Commit**

```bash
git add requirements.txt
git commit -m "chore: replace anthropic with google-generativeai"
```

---

### Task 2: Update .env.example

**Files:**
- Modify: `.env.example`

- [ ] **Step 1: Swap the API key variable**

Open `.env.example` and replace:
```
# Anthropic
ANTHROPIC_API_KEY=
```
with:
```
# Google Gemini
GEMINI_API_KEY=

# Optional model overrides (defaults to gemini-2.0-flash)
# GEMINI_MODEL=gemini-2.0-flash
# GEMINI_MODEL_SMALL=gemini-2.0-flash
```

- [ ] **Step 2: Add GEMINI_API_KEY to your actual .env**

Open `.env` (not committed to git) and add:
```
GEMINI_API_KEY=<paste your key here>
```

Remove the `ANTHROPIC_API_KEY` line if present.

- [ ] **Step 3: Commit**

```bash
git add .env.example
git commit -m "chore: update env template for Gemini API key"
```

---

### Task 3: Create test file with failing tests

**Files:**
- Create: `tests/__init__.py`
- Create: `tests/shared/__init__.py`
- Create: `tests/shared/test_claude_client.py`

- [ ] **Step 1: Create the package init files**

Create `tests/__init__.py` — empty file.
Create `tests/shared/__init__.py` — empty file.

- [ ] **Step 2: Write the failing tests**

Create `tests/shared/test_claude_client.py`:

```python
import pytest
import tools.shared.claude_client as cc


# --- _to_gemini_history ---

def test_to_gemini_history_converts_assistant_to_model():
    messages = [
        {"role": "user", "content": "Hello"},
        {"role": "assistant", "content": "Hi there"},
        {"role": "user", "content": "Question?"},
    ]
    history, last = cc._to_gemini_history(messages)
    assert last == "Question?"
    assert history[0] == {"role": "user", "parts": ["Hello"]}
    assert history[1] == {"role": "model", "parts": ["Hi there"]}


def test_to_gemini_history_single_message():
    messages = [{"role": "user", "content": "Hello"}]
    history, last = cc._to_gemini_history(messages)
    assert history == []
    assert last == "Hello"


def test_to_gemini_history_empty():
    history, last = cc._to_gemini_history([])
    assert history == []
    assert last == ""


# --- ask() mock mode ---

def test_ask_mock_returns_chatbot_response(monkeypatch):
    monkeypatch.setattr(cc, "MOCK_MODE", True)
    result = cc.ask(
        system_prompt="You are an ophthalmology tutor.",
        messages=[{"role": "user", "content": "Explain glaucoma."}],
        feature="chatbot",
    )
    assert isinstance(result, str)
    assert len(result) > 10


def test_ask_mock_returns_flashcard_response(monkeypatch):
    monkeypatch.setattr(cc, "MOCK_MODE", True)
    result = cc.ask(
        system_prompt="Generate flashcards.",
        messages=[{"role": "user", "content": "Glaucoma cards."}],
        feature="flashcard",
    )
    assert isinstance(result, str)
    assert "front" in result  # mock flashcard JSON contains "front"


# --- ask_with_image() mock mode ---

def test_ask_with_image_mock_returns_image_response(monkeypatch, tmp_path):
    monkeypatch.setattr(cc, "MOCK_MODE", True)
    # Create a tiny valid PNG so the path exists (not read in mock mode)
    fake_img = tmp_path / "test.png"
    fake_img.write_bytes(b"")
    result = cc.ask_with_image(
        system_prompt="You are an ophthalmology examiner.",
        messages=[{"role": "user", "content": "Describe this image."}],
        image_path=fake_img,
        feature="image",
    )
    assert isinstance(result, str)
    assert len(result) > 10


# --- live mode (skipped without real key) ---

def test_ask_live_mode_returns_string():
    if cc.MOCK_MODE:
        pytest.skip("GEMINI_API_KEY not set — skipping live test")
    result = cc.ask(
        system_prompt="You are a helpful assistant. Answer in one sentence.",
        messages=[{"role": "user", "content": "What is glaucoma?"}],
        feature="default",
    )
    assert isinstance(result, str)
    assert len(result) > 10
```

- [ ] **Step 3: Run the tests — confirm they fail**

```bash
pytest tests/shared/test_claude_client.py -v
```

Expected: several failures because `_to_gemini_history` does not exist yet and the internals still call `anthropic`.

---

### Task 4: Rewrite claude_client.py internals

**Files:**
- Modify: `tools/shared/claude_client.py`

- [ ] **Step 1: Replace the entire file with the Gemini implementation**

```python
#!/usr/bin/env python3
"""Shared AI client — all Gemini API calls in the SNEC platform go through here.

Automatically runs in MOCK_MODE when GEMINI_API_KEY is not set, returning
structured fake responses so all features can be built and tested without an API key.
Switch to live mode by adding GEMINI_API_KEY to .env.

Usage (from other tools):
    from tools.shared.claude_client import ask, ask_with_image

Self-test:
    python tools/shared/claude_client.py
"""

import os
import sys
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
load_dotenv(PROJECT_ROOT / ".env")

MODEL       = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
MODEL_SMALL = os.getenv("GEMINI_MODEL_SMALL", "gemini-2.0-flash")
API_KEY     = os.getenv("GEMINI_API_KEY", "").strip()
MOCK_MODE   = not API_KEY

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
    "default": "[MOCK] This is a mock response. Add GEMINI_API_KEY to .env to use the real Gemini API.",
}


def _mock_response(feature: str = "default") -> str:
    return _MOCK_RESPONSES.get(feature, _MOCK_RESPONSES["default"])


def _to_gemini_history(messages: list[dict]) -> tuple[list[dict], str]:
    """Convert Anthropic-format messages to Gemini chat history + last message text.

    Anthropic uses "assistant"; Gemini uses "model". All messages except the last
    become history; the last user message is returned separately for send_message().
    """
    if not messages:
        return [], ""
    history = [
        {"role": "model" if m["role"] == "assistant" else "user", "parts": [m["content"]]}
        for m in messages[:-1]
    ]
    return history, messages[-1]["content"]


def ask(
    system_prompt: str,
    messages: list[dict],
    max_tokens: int = 1024,
    feature: str = "default",
    model: str | None = None,
) -> str:
    """
    Send a conversation to Gemini and return the response text.

    Args:
        system_prompt: The system prompt.
        messages:      Conversation history as list of {"role": "user"/"assistant", "content": str}.
        max_tokens:    Maximum tokens in the response.
        feature:       Feature name for mock routing: "chatbot", "flashcard", "case", "image".
        model:         Override model (defaults to MODEL). Pass MODEL_SMALL for cheap tasks.

    Returns:
        Response text as a string.
    """
    if MOCK_MODE:
        return _mock_response(feature)

    import google.generativeai as genai

    genai.configure(api_key=API_KEY)
    history, last_message = _to_gemini_history(messages)
    gmodel = genai.GenerativeModel(
        model_name=model or MODEL,
        system_instruction=system_prompt,
        generation_config={"max_output_tokens": max_tokens},
    )
    chat = gmodel.start_chat(history=history)
    response = chat.send_message(last_message)
    return response.text


def ask_with_image(
    system_prompt: str,
    messages: list[dict],
    image_path: str | Path,
    max_tokens: int = 1024,
    feature: str = "image",
) -> str:
    """
    Send a conversation with an image attachment to Gemini.

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

    import google.generativeai as genai
    import PIL.Image

    genai.configure(api_key=API_KEY)

    last_user_text = next(
        (m["content"] for m in reversed(messages) if m["role"] == "user"), ""
    )
    img = PIL.Image.open(Path(image_path))

    gmodel = genai.GenerativeModel(
        model_name=MODEL,
        system_instruction=system_prompt,
        generation_config={"max_output_tokens": max_tokens},
    )
    response = gmodel.generate_content([last_user_text, img])
    return response.text


if __name__ == "__main__":
    print("Testing claude_client.py (Gemini backend)...\n")

    mode = "MOCK" if MOCK_MODE else "LIVE"
    print(f"  Mode: {mode}")

    print("  Testing ask() - chatbot feature...")
    response = ask(
        system_prompt="You are an ophthalmology tutor.",
        messages=[{"role": "user", "content": "Explain glaucoma."}],
        feature="chatbot",
    )
    assert len(response) > 10, "Response too short"
    print(f"  [OK] Response ({len(response)} chars): {response[:80]}...")

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
        print("  Add GEMINI_API_KEY to .env to test live mode.")
    else:
        print("\n  Running in LIVE mode — real Gemini API calls used.")

    print("\n  [PASS] claude_client.py working correctly.")
    sys.exit(0)
```

---

### Task 5: Run tests — confirm they pass

**Files:** (none changed)

- [ ] **Step 1: Run the full test suite**

```bash
pytest tests/shared/test_claude_client.py -v
```

Expected output (with no `GEMINI_API_KEY` set):
```
tests/shared/test_claude_client.py::test_to_gemini_history_converts_assistant_to_model PASSED
tests/shared/test_claude_client.py::test_to_gemini_history_single_message PASSED
tests/shared/test_claude_client.py::test_to_gemini_history_empty PASSED
tests/shared/test_claude_client.py::test_ask_mock_returns_chatbot_response PASSED
tests/shared/test_claude_client.py::test_ask_mock_returns_flashcard_response PASSED
tests/shared/test_claude_client.py::test_ask_with_image_mock_returns_image_response PASSED
tests/shared/test_claude_client.py::test_ask_live_mode_returns_string SKIPPED
```

If any test fails, check that the function signatures in the implementation exactly match those in the tests.

- [ ] **Step 2: Run the self-test script**

```bash
python tools/shared/claude_client.py
```

Expected:
```
Testing claude_client.py (Gemini backend)...
  Mode: MOCK   (or LIVE if GEMINI_API_KEY is set)
  Testing ask() - chatbot feature...
  [OK] Response (...
  [PASS] claude_client.py working correctly.
```

---

### Task 6: Final commit

**Files:** (none changed — committing all modified files)

- [ ] **Step 1: Stage and commit everything**

```bash
git add tools/shared/claude_client.py tests/__init__.py tests/shared/__init__.py tests/shared/test_claude_client.py
git commit -m "feat: replace Claude with Gemini API in claude_client"
```

- [ ] **Step 2: Verify the app still boots**

```bash
streamlit run app.py
```

Expected: Streamlit starts without import errors. All pages load. In mock mode (no API key), features return canned responses as before. In live mode (with `GEMINI_API_KEY` set), features call Gemini.
