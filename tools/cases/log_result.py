#!/usr/bin/env python3
"""Logs a case simulation result to the snec_case_results Google Sheet.

Usage (from run_case.py):
    from tools.cases.log_result import log_case_result
    log_case_result(student_id, case, result)
"""

import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from tools.shared.gsheets import append_row
from tools.shared.audit_log import log as audit_log


def log_case_result(student_id: str, case: dict, result: dict) -> str:
    """
    Write case simulation scores and feedback to snec_case_results.

    Returns:
        result_id UUID string.
    """
    result_id = str(uuid.uuid4())

    append_row("snec_case_results", {
        "result_id": result_id,
        "student_id": student_id,
        "case_id": case["case_id"],
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "history_score": str(result.get("history_score", 0)),
        "investigations_score": str(result.get("investigations_score", 0)),
        "diagnosis_score": str(result.get("diagnosis_score", 0)),
        "management_score": str(result.get("management_score", 0)),
        "total_score": str(result.get("total_score", 0)),
        "feedback_summary": result.get("overall_feedback", "")[:500],
    })

    audit_log("case_result_logged", student_id=student_id, feature="cases",
              detail=f"result_id={result_id} case={case['case_id']}")

    return result_id
