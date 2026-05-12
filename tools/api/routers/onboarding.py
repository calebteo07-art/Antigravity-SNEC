from fastapi import APIRouter
from pydantic import BaseModel

from tools.shared.identity import get_or_create_student, has_consented, record_consent
from tools.api.constants import MOCK_MODE

router = APIRouter()

class OnboardRequest(BaseModel):
    full_name: str
    email: str

class OnboardResponse(BaseModel):
    student_id: str
    mock_mode: bool
    role: str = "student"

@router.post("", response_model=OnboardResponse)
def onboard(body: OnboardRequest):
    email = body.email.strip().lower()
    student_id = get_or_create_student(body.full_name.strip(), email)
    if not has_consented(student_id):
        record_consent(student_id)

    role = "student"
    try:
        from tools.shared.database import SessionLocal
        from tools.shared.models import Student
        with SessionLocal() as db:
            student = db.query(Student).filter(Student.student_id == student_id).first()
            if student:
                role = student.role
    except Exception:
        pass

    return OnboardResponse(student_id=student_id, mock_mode=MOCK_MODE, role=role)
