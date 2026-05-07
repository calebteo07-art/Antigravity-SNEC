#!/usr/bin/env python3
"""FastAPI backend for the EyeQ web frontend.

Bridges the React frontend to the existing tools (claude_client, onboarding,
log_session, generate_cards). Automatically runs in MOCK MODE when
ANTHROPIC_API_KEY is not set in .env — the full frontend flow works without
an API key.

Run:
    uvicorn tools.api.server:app --reload --port 8000
"""

import json
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
from tools.cases.load_case import load_case, list_available_cases
from tools.cases.evaluate_response import evaluate_case

PATIENT_SYSTEM = """You are playing the role of a patient in a clinical case simulation for ophthalmic professionals.

IMPORTANT RULES:
- Answer ONLY what the student directly asks. Do not volunteer extra information.
- Stay in character as the patient — use lay language, not medical terminology.
- If the student asks for examination findings or investigation results, provide them as an examiner would.
- If the student asks to examine you, describe findings from the case.
- When the student says they are ready to give a diagnosis or management plan, acknowledge it.
- Do NOT reveal the diagnosis or correct answers — wait for the student to conclude.

Case details for your reference (do not reveal unless asked):
{case_json}"""

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


# ── Case simulation models ─────────────────────────────────────────────────

class CasePatientInfo(BaseModel):
    name: str
    age: int
    presenting_complaint: str

class CaseInfo(BaseModel):
    case_id: str
    title: str
    difficulty: str
    topic: str
    estimated_minutes: int
    patient: CasePatientInfo

class CasesResponse(BaseModel):
    cases: list[CaseInfo]

class CaseChatRequest(BaseModel):
    student_id: str
    messages: list[ChatMessage]

class CaseChatResponse(BaseModel):
    response: str

class CaseSubmitRequest(BaseModel):
    student_id: str
    messages: list[ChatMessage]
    diagnosis: str
    management_plan: str

class DomainScore(BaseModel):
    history_score: int
    investigations_score: int
    diagnosis_score: int
    management_score: int
    history_feedback: str
    investigations_feedback: str
    diagnosis_feedback: str
    management_feedback: str
    total_score: int
    overall_feedback: str

class CaseSubmitResponse(BaseModel):
    result: DomainScore
    cards: list[Flashcard]
    mock_mode: bool


# ── Case endpoints ─────────────────────────────────────────────────────────

@app.get("/api/cases", response_model=CasesResponse)
def get_cases():
    cases = []
    for case_id in list_available_cases():
        try:
            c = load_case(case_id)
            cases.append(CaseInfo(
                case_id=c["case_id"],
                title=c["title"],
                difficulty=c["difficulty"],
                topic=c["topic"],
                estimated_minutes=c["estimated_minutes"],
                patient=CasePatientInfo(
                    name=c["patient"]["name"],
                    age=c["patient"]["age"],
                    presenting_complaint=c["patient"]["presenting_complaint"],
                ),
            ))
        except Exception:
            pass
    return CasesResponse(cases=cases)


@app.post("/api/cases/{case_id}/chat", response_model=CaseChatResponse)
def case_chat(case_id: str, body: CaseChatRequest):
    try:
        case = load_case(case_id)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Case '{case_id}' not found")

    patient_prompt = PATIENT_SYSTEM.format(case_json=json.dumps(case, indent=2))
    messages = [{"role": m.role, "content": m.content} for m in body.messages]

    response = ask(
        system_prompt=patient_prompt,
        messages=messages,
        max_tokens=512,
        feature="case",
    )
    return CaseChatResponse(response=response)


@app.post("/api/cases/{case_id}/submit", response_model=CaseSubmitResponse)
def case_submit(case_id: str, body: CaseSubmitRequest):
    try:
        case = load_case(case_id)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Case '{case_id}' not found")

    messages = [{"role": m.role, "content": m.content} for m in body.messages]
    # Append the student's final answer as a user message so the evaluator sees it
    messages.append({
        "role": "user",
        "content": f"Diagnosis: {body.diagnosis}\nManagement Plan: {body.management_plan}",
    })

    raw_result = evaluate_case(case, messages, body.student_id)

    session_id = log_session(
        student_id=body.student_id,
        topic=f"Case: {case['title']}",
        messages=messages,
        token_count=0,
        model="mock" if MOCK_MODE else MODEL,
    )
    cards = generate_and_return_cards(
        student_id=body.student_id,
        session_id=session_id,
        messages=messages,
    )

    return CaseSubmitResponse(
        result=DomainScore(**{k: raw_result[k] for k in DomainScore.model_fields}),
        cards=[Flashcard(**c) for c in cards],
        mock_mode=MOCK_MODE,
    )
