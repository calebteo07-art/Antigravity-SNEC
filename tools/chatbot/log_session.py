#!/usr/bin/env python3
"""Logs a completed chatbot session to the snec_sessions Google Sheet.

Called at the end of run_session.py. Not called directly.

Usage (from run_session.py):
    from tools.chatbot.log_session import log_session
    log_session(student_id, topic, messages, token_count, model)
"""

import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from tools.shared.gsheets import append_row
from tools.shared.audit_log import log as audit_log


def log_session(
    student_id: str,
    topic: str,
    messages: list[dict],
    token_count: int = 0,
    model: str = "mock",
) -> str:
    """
    Write a session summary row to snec_sessions sheet.

    Args:
        student_id:  Student UUID.
        topic:       Topic the student asked about (first user message, truncated).
        messages:    Full conversation history (used to build summary).
        token_count: Total tokens used (0 in mock mode).
        model:       Model name used.

    Returns:
        session_id: UUID for this session.
    """
    session_id = str(uuid.uuid4())
    timestamp = datetime.now(timezone.utc).isoformat()

    # Build a short summary from the last assistant message
    last_assistant = next(
        (m["content"] for m in reversed(messages) if m["role"] == "assistant"),
        "No response recorded."
    )
    summary = last_assistant[:200].replace("\n", " ") + ("..." if len(last_assistant) > 200 else "")

    append_row("snec_sessions", {
        "session_id": session_id,
        "student_id": student_id,
        "timestamp": timestamp,
        "topic": topic[:100],
        "summary": summary,
        "token_count": str(token_count),
        "model": model,
    })

    audit_log("session_logged", student_id=student_id, feature="chatbot",
              detail=f"session_id={session_id} tokens={token_count}")

    return session_id
