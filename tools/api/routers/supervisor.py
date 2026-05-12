from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Any

from tools.supervisor.cohort_summary import cohort_summary as _cohort_summary
from tools.supervisor.at_risk import get_at_risk as _get_at_risk

router = APIRouter()

class SupervisorSummaryResponse(BaseModel):
    cohort: dict
    at_risk: List[dict]

@router.get("/summary", response_model=SupervisorSummaryResponse)
def get_supervisor_summary():
    cohort = _cohort_summary()
    at_risk = _get_at_risk()
    return SupervisorSummaryResponse(cohort=cohort, at_risk=at_risk)
