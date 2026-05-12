from fastapi import APIRouter
from pydantic import BaseModel
from typing import List

from tools.shared.claude_client import ask
from tools.chatbot.log_session import log_session
from tools.flashcards.generate_cards import generate_and_return_cards
from tools.profile.get_profile import get_profile
from tools.profile.update_profile import update_profile
from tools.profile.summarize_gaps import summarize_gaps
from tools.api.constants import TUTOR_SYSTEM, get_kb, MODEL, MOCK_MODE

router = APIRouter()

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    student_id: str
    messages: List[ChatMessage]

class ChatResponse(BaseModel):
    content: str

class FlashcardDTO(BaseModel):
    card_id: str
    front: str
    back: str
    topic_tag: str

class EndSessionRequest(BaseModel):
    student_id: str
    messages: List[ChatMessage]
    topic: str = "Ophthalmology"
    token_count: int = 0

class EndSessionResponse(BaseModel):
    session_id: str
    cards: List[FlashcardDTO]
    mock_mode: bool

@router.post("/chat", response_model=ChatResponse)
def chat(body: ChatRequest):
    messages = [{"role": m.role, "content": m.content} for m in body.messages]

    system_prompt = TUTOR_SYSTEM + "\n\n---\n\n" + get_kb()
    try:
        profile = get_profile(body.student_id)
        gap_context = summarize_gaps(profile)
        if gap_context:
            system_prompt = f"## Student Weak Areas (steer toward these)\n{gap_context}\n\n{system_prompt}"
    except Exception:
        pass

    content = ask(
        system_prompt=system_prompt,
        messages=messages,
        max_tokens=2048,
        feature="chatbot",
        model=MODEL,
    )

    return ChatResponse(content=content)

@router.post("/end-session", response_model=EndSessionResponse)
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

    try:
        update_profile(body.student_id)
    except Exception:
        pass

    return EndSessionResponse(
        session_id=session_id,
        cards=[FlashcardDTO(**c) for c in cards],
        mock_mode=MOCK_MODE,
    )
