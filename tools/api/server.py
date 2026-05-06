#!/usr/bin/env python3
"""FastAPI backend for the EyeQ web frontend.

Bridges the React frontend to the existing tools (claude_client, onboarding,
log_session, generate_cards). Automatically runs in MOCK MODE when
ANTHROPIC_API_KEY is not set in .env — the full frontend flow works without
an API key.

Run:
    uvicorn tools.api.server:app --reload --port 8000
"""

import re
import sys
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from tools.shared.claude_client import ask, MOCK_MODE, MODEL
from tools.shared.identity import get_or_create_student, has_consented, record_consent
from tools.chatbot.log_session import log_session
from tools.flashcards.generate_cards import generate_and_return_cards

KB_PATH = PROJECT_ROOT / "workflows" / "ophthalmology_kb.md"
_KB_TEXT: Optional[str] = None

def _kb() -> str:
    global _KB_TEXT
    if _KB_TEXT is None:
        _KB_TEXT = KB_PATH.read_text(encoding="utf-8")
    return _KB_TEXT


def _parse_tutor_response(text: str) -> dict:
    """Parse the 4-section AI response into structured fields."""
    result = {
        "explanation": "",
        "mechanism": "",
        "clinicalPearl": "",
        "checkUnderstanding": "",
        "raw": text,
    }

    # Matches both "**Section:**" and "**Section** —" styles, with optional numbering
    pattern = re.compile(
        r"(?:\d+\.\s*)?\*\*(Explanation|Mechanism|Clinical Pearl|Check Your Understanding)\*\*[\s:—]+",
        re.IGNORECASE,
    )
    matches = list(pattern.finditer(text))

    key_map = {
        "explanation": "explanation",
        "mechanism": "mechanism",
        "clinical pearl": "clinicalPearl",
        "check your understanding": "checkUnderstanding",
    }

    for i, match in enumerate(matches):
        header = match.group(1).lower()
        key = key_map.get(header)
        if not key:
            continue
        start = match.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        result[key] = text[start:end].strip()

    # Fallback: if no sections parsed, put full text in explanation
    if not any(result[k] for k in ("explanation", "mechanism", "clinicalPearl", "checkUnderstanding")):
        result["explanation"] = text.strip()

    return result


app = FastAPI(title="EyeQ API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Request / Response models ──────────────────────────────────────────────

class OnboardRequest(BaseModel):
    full_name: str
    email: str

class OnboardResponse(BaseModel):
    student_id: str
    mock_mode: bool

class ChatMessage(BaseModel):
    role: str   # "user" | "assistant"
    content: str

class ChatRequest(BaseModel):
    student_id: str
    messages: list[ChatMessage]

class ChatResponse(BaseModel):
    explanation: str
    mechanism: str
    clinicalPearl: str
    checkUnderstanding: str
    raw: str

class EndSessionRequest(BaseModel):
    student_id: str
    messages: list[ChatMessage]
    topic: str = "Ophthalmology"
    token_count: int = 0

class Flashcard(BaseModel):
    card_id: str
    front: str
    back: str
    topic_tag: str

class EndSessionResponse(BaseModel):
    session_id: str
    cards: list[Flashcard]
    mock_mode: bool


# ── Endpoints ──────────────────────────────────────────────────────────────

@app.post("/api/onboard", response_model=OnboardResponse)
def onboard(body: OnboardRequest):
    if not body.full_name.strip() or not body.email.strip():
        raise HTTPException(status_code=400, detail="full_name and email are required")

    student_id = get_or_create_student(body.full_name.strip(), body.email.strip().lower())
    if not has_consented(student_id):
        record_consent(student_id)

    return OnboardResponse(student_id=student_id, mock_mode=MOCK_MODE)


@app.post("/api/chat", response_model=ChatResponse)
def chat(body: ChatRequest):
    messages = [{"role": m.role, "content": m.content} for m in body.messages]

    raw = ask(
        system_prompt=_kb(),
        messages=messages,
        max_tokens=1024,
        feature="chatbot",
        model=MODEL,
    )

    return ChatResponse(**_parse_tutor_response(raw))


@app.post("/api/end-session", response_model=EndSessionResponse)
def end_session(body: EndSessionRequest):
    messages = [{"role": m.role, "content": m.content} for m in body.messages]
    model_name = "mock" if MOCK_MODE else MODEL

    session_id = log_session(
        student_id=body.student_id,
        topic=body.topic,
        messages=messages,
        token_count=body.token_count,
        model=model_name,
    )

    cards = generate_and_return_cards(
        student_id=body.student_id,
        session_id=session_id,
        messages=messages,
    )

    return EndSessionResponse(
        session_id=session_id,
        cards=[Flashcard(**c) for c in cards],
        mock_mode=MOCK_MODE,
    )


@app.get("/api/status")
def status():
    return {"status": "ok", "mock_mode": MOCK_MODE}
