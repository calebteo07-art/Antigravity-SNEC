import json
from fastapi import APIRouter
from pydantic import BaseModel

from tools.shared.claude_client import ask
from tools.api.constants import MOCK_MODE

router = APIRouter()

class FlashcardCheckRequest(BaseModel):
    student_id: str
    question: str
    student_answer: str
    correct_answer: str

class FlashcardCheckResponse(BaseModel):
    feedback: str
    score: int
    mock_mode: bool

@router.post("/check", response_model=FlashcardCheckResponse)
def flashcard_check(body: FlashcardCheckRequest):
    system = (
        "You are an ophthalmology tutor evaluating a student's active recall attempt. "
        "Compare the student's answer to the correct answer. "
        "Return ONLY valid JSON with no other text:\n"
        '{"score": <0-10>, "feedback": "<2 concise sentences: what they got right, then what they missed or got wrong>"}'
    )
    raw = ask(
        system_prompt=system,
        messages=[{
            "role": "user",
            "content": (
                f"Question: {body.question}\n\n"
                f"Correct answer: {body.correct_answer}\n\n"
                f"Student answer: {body.student_answer}"
            ),
        }],
        max_tokens=2048,
        feature="flashcard",
    )
    text = raw.strip()
    if text.startswith("```"):
        lines = text.splitlines()
        text = "\n".join(lines[1:-1] if lines[-1].strip() == "```" else lines[1:])
    try:
        parsed = json.loads(text)
        return FlashcardCheckResponse(
            feedback=parsed.get("feedback", raw[:300]),
            score=int(parsed.get("score", 5)),
            mock_mode=MOCK_MODE,
        )
    except Exception:
        return FlashcardCheckResponse(feedback=raw[:300], score=5, mock_mode=MOCK_MODE)
