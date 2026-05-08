# Gemini API Integration Design

**Date:** 2026-05-08
**Status:** Approved

## Objective

Replace the Anthropic Claude API with the Google Gemini API across all features of the SNEC AI Chatbot (chatbot, flashcards, clinical cases, image quiz).

## Scope

### Files changed

| File | Change |
|---|---|
| `tools/shared/claude_client.py` | Internals rewritten to use `google-generativeai` SDK; public interface (`ask`, `ask_with_image`, `MODEL`, `MODEL_SMALL`) unchanged |
| `requirements.txt` | Replace `anthropic>=0.40.0` with `google-generativeai>=0.8.0` |
| `.env.example` | Replace `ANTHROPIC_API_KEY` with `GEMINI_API_KEY` |

### Files unchanged

All 7 importers of `claude_client` are untouched:
- `tools/cases/run_case.py`
- `tools/api/server.py`
- `app.py`
- `pages/_shared.py`
- `tools/flashcards/generate_cards.py`
- `tools/cases/evaluate_response.py`
- `tools/image_quiz/evaluate_description.py`

## Architecture

### Provider

- SDK: `google-generativeai`
- Default model (`MODEL`): `gemini-2.0-flash`
- Small model (`MODEL_SMALL`): `gemini-2.0-flash` (free tier; no differentiated small model)
- Both overridable via `GEMINI_MODEL` / `GEMINI_MODEL_SMALL` env vars

### Mock mode

Triggered when `GEMINI_API_KEY` is absent from the environment. All existing mock responses remain identical.

### Conversation format conversion

Anthropic uses `"assistant"` as the AI role; Gemini uses `"model"`. The client converts history automatically before each API call. Callers pass `{"role": "assistant", ...}` as before.

### System prompt

Passed as `system_instruction` on the `GenerativeModel` constructor. Anthropic's `cache_control` block is dropped (not supported on Gemini free tier).

### Vision (`ask_with_image`)

Images are opened with `PIL.Image` (already a project dependency via Pillow) and passed inline with the text content. Gemini accepts multimodal content natively — no base64 encoding required.

### Error handling

Exceptions propagate naturally, consistent with the current design. Callers already handle JSON parse failures with fallback dicts.

## Data flow

```
Caller (chatbot / flashcards / cases / image_quiz)
    └── ask() or ask_with_image()          # same interface as before
            └── google.generativeai
                    └── Gemini API (gemini-2.0-flash)
```

## Environment

`.env` requires:
```
GEMINI_API_KEY=<your key>
```

Optional overrides:
```
GEMINI_MODEL=gemini-2.0-flash
GEMINI_MODEL_SMALL=gemini-2.0-flash
```

## Testing

The self-test at the bottom of `claude_client.py` is updated to verify:
- Mock mode returns canned responses when `GEMINI_API_KEY` is absent
- Live mode returns non-empty strings from the Gemini API
