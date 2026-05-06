from pathlib import Path
import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parent.parent

PDPA_NOTICE = """
**Singapore Personal Data Protection Act (PDPA) — Data Collection Notice**

This platform collects and processes:
- Your name and email address (identity and progress tracking)
- Your Q&A session transcripts (flash-card generation)
- Your quiz and case simulation scores (analytics)

Your data will not be shared with third parties or used to train AI models.
You may withdraw consent at any time by contacting the platform administrator.
"""


@st.cache_resource
def _load_kb() -> str:
    kb = PROJECT_ROOT / "workflows" / "ophthalmology_kb.md"
    return kb.read_text(encoding="utf-8") if kb.exists() else "You are an ophthalmology tutor at SNEC."


def _gsheets():
    from tools.shared.gsheets import get_rows, append_row, update_row
    return get_rows, append_row, update_row


def _identity():
    from tools.shared.identity import get_or_create_student, has_consented, record_consent, get_profile
    return get_or_create_student, has_consented, record_consent, get_profile


def _claude():
    from tools.shared.claude_client import ask, ask_with_image, MOCK_MODE, MODEL
    return ask, ask_with_image, MOCK_MODE, MODEL
