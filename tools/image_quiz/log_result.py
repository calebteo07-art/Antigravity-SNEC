#!/usr/bin/env python3
"""Logs an image quiz result to the snec_image_results Google Sheet."""

import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from tools.shared.database import SessionLocal
from tools.shared.models import ImageResult
from tools.shared.audit_log import log as audit_log


def log_image_result(student_id: str, image_meta: dict, result: dict) -> str:
    result_id = str(uuid.uuid4())

    import json
    
    with SessionLocal() as db:
        new_result = ImageResult(
            result_id=result_id,
            student_id=student_id,
            image_id=image_meta.get("image_id", ""),
            score=int(result.get("score", 0)),
            correct_findings=json.dumps(result.get("correct_findings", [])),
            missed_findings=json.dumps(result.get("missed_findings", [])),
            incorrect_findings=json.dumps(result.get("incorrect_findings", [])),
            diagnosis_correct=result.get("diagnosis_correct", False),
            feedback=result.get("feedback", "")
        )
        db.add(new_result)
        db.commit()

    audit_log("image_quiz_result", student_id=student_id, feature="image_quiz",
              detail=f"image_id={image_meta.get('image_id')} score={result.get('score')}/10")

    return result_id
