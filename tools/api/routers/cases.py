import json
from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Optional

from tools.cases.load_case import load_case, list_available_cases
from tools.cases.evaluate_response import evaluate_case
from tools.shared.claude_client import ask
from tools.api.constants import PATIENT_SYSTEM, MODEL, MOCK_MODE
from tools.api.routers.chat import FlashcardDTO

router = APIRouter()

class ChatMessage(BaseModel):
    role: str
    content: str

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
    cases: List[CaseInfo]

class CaseChatRequest(BaseModel):
    student_id: str
    messages: List[ChatMessage]

class CaseChatResponse(BaseModel):
    response: str

class CaseSubmitRequest(BaseModel):
    student_id: str
    messages: List[ChatMessage]
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
    cards: List[FlashcardDTO]
    mock_mode: bool
    debrief: Optional[str] = None

@router.get("", response_model=CasesResponse)
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

@router.post("/{case_id}/chat", response_model=CaseChatResponse)
def case_chat(case_id: str, body: CaseChatRequest):
    case_data = load_case(case_id)
    case_json = json.dumps(case_data, indent=2)
    sys_prompt = PATIENT_SYSTEM.format(case_json=case_json)

    messages = [{"role": m.role, "content": m.content} for m in body.messages]
    content = ask(
        system_prompt=sys_prompt,
        messages=messages,
        max_tokens=1024,
        feature="case_chat",
        model=MODEL,
    )
    return CaseChatResponse(response=content)

@router.post("/{case_id}/submit", response_model=CaseSubmitResponse)
def case_submit(case_id: str, body: CaseSubmitRequest):
    case_data = load_case(case_id)
    messages = [{"role": m.role, "content": m.content} for m in body.messages]

    result, cards = evaluate_case(
        student_id=body.student_id,
        case_id=case_id,
        case_data=case_data,
        messages=messages,
        student_diagnosis=body.diagnosis,
        student_management=body.management_plan,
    )

    debrief_prompt = (
        "You are an examiner giving a brief, encouraging final debrief to a student "
        "who just completed a clinical case simulation. Keep it to 3 sentences maximum."
    )
    debrief = ask(
        system_prompt=debrief_prompt,
        messages=[{"role": "user", "content": f"Score: {result['total_score']}/40\nFeedback: {result['overall_feedback']}"}],
        max_tokens=200,
        feature="case_submit",
        model=MODEL,
    )

    domain_score = DomainScore(
        history_score=result.get("history_score", 0),
        investigations_score=result.get("investigations_score", 0),
        diagnosis_score=result.get("diagnosis_score", 0),
        management_score=result.get("management_score", 0),
        history_feedback=result.get("history_feedback", ""),
        investigations_feedback=result.get("investigations_feedback", ""),
        diagnosis_feedback=result.get("diagnosis_feedback", ""),
        management_feedback=result.get("management_feedback", ""),
        total_score=result.get("total_score", 0),
        overall_feedback=result.get("overall_feedback", ""),
    )

    flashcards = [FlashcardDTO(**c) for c in cards]

    return CaseSubmitResponse(
        result=domain_score,
        cards=flashcards,
        mock_mode=MOCK_MODE,
        debrief=debrief,
    )
