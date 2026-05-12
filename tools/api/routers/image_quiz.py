import json
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from tools.image_quiz.evaluate_description import evaluate_description
from tools.image_quiz.log_result import log_image_result
from tools.api.constants import IMAGES_DIR, MOCK_MODE

router = APIRouter()

class ImageQuizSubmitRequest(BaseModel):
    student_id: str
    image_id: str
    description: str

class ImageQuizResultResponse(BaseModel):
    score: int
    correct_findings: list[str]
    missed_findings: list[str]
    incorrect_findings: list[str]
    diagnosis_correct: bool
    feedback: str
    mock_mode: bool

@router.post("/submit", response_model=ImageQuizResultResponse)
def image_quiz_submit(body: ImageQuizSubmitRequest):
    meta_path = IMAGES_DIR / f"{body.image_id}.json"
    if not meta_path.exists():
        raise HTTPException(status_code=404, detail="Image not found")

    with open(meta_path, "r", encoding="utf-8") as f:
        meta = json.load(f)

    result = evaluate_description(
        student_id=body.student_id,
        image_meta=meta,
        student_description=body.description,
    )

    log_image_result(body.student_id, meta, result)

    return ImageQuizResultResponse(
        score=result.get("score", 0),
        correct_findings=result.get("correct_findings", []),
        missed_findings=result.get("missed_findings", []),
        incorrect_findings=result.get("incorrect_findings", []),
        diagnosis_correct=result.get("diagnosis_correct", False),
        feedback=result.get("feedback", ""),
        mock_mode=MOCK_MODE,
    )
