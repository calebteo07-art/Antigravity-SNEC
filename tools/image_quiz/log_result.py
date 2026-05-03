#!/usr/bin/env python3
"""Logs an image quiz result to the snec_image_results Google Sheet."""

import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from tools.shared.gsheets import append_row
from tools.shared.audit_log import log as audit_log


def log_image_result(student_id: str, image_meta: dict, result: dict) -> str:
    result_id = str(uuid.uuid4())

    append_row("snec_image_results", {
        "result_id": result_id,
        "student_id": student_id,
        "image_id": image_meta.get("image_id", ""),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "modality": image_meta.get("modality", ""),
        "student_description": result.get("_raw_description", "")[:300],
        "score": str(result.get("score", 0)),
        "correct_findings": ", ".join(result.get("correct_findings", [])),
        "missed_findings": ", ".join(result.get("missed_findings", [])),
    })

    audit_log("image_quiz_result", student_id=student_id, feature="image_quiz",
              detail=f"image_id={image_meta.get('image_id')} score={result.get('score')}/10")

    return result_id
