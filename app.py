"""EyeQ — Streamlit entry point.

Run with: streamlit run app.py
"""
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT))

import streamlit as st
from tools.shared.styles import SNEC_CSS, user_chip, wordmark, badge
from tools.shared.claude_client import MOCK_MODE

st.set_page_config(
    page_title="EyeQ",
    page_icon="👁️",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(SNEC_CSS, unsafe_allow_html=True)

DEFAULTS = {
    "student_id":         None,
    "student_name":       None,
    "chat_messages":      [],
    "case_conversation":  [],
    "current_case":       None,
    "case_result":        None,
    "review_cards":       [],
    "review_index":       0,
    "review_done":        False,
    "card_revealed":      False,
    "case_xp_result":     None,
    "case_hints_used":    0,
    "case_hint_messages": [],
}
for k, v in DEFAULTS.items():
    if k not in st.session_state:
        st.session_state[k] = v

# Sidebar — custom content sits above the nav widget
with st.sidebar:
    st.markdown(wordmark(), unsafe_allow_html=True)
    if st.session_state.student_id:
        st.markdown(user_chip(st.session_state.student_name), unsafe_allow_html=True)
        st.markdown("<div style='height:.5rem'></div>", unsafe_allow_html=True)
        if st.button("↩  Log Out", use_container_width=True):
            for k, v in DEFAULTS.items():
                st.session_state[k] = v
            st.rerun()
    else:
        st.markdown(
            '<div style="font-size:.8rem;color:var(--txt-3);padding:.5rem 0">'
            'Sign in to access the platform.</div>',
            unsafe_allow_html=True,
        )
    if MOCK_MODE:
        st.markdown(
            f'<div style="margin-top:1rem">{badge("Mock mode", "bd")}</div>',
            unsafe_allow_html=True,
        )

# Auth gate + navigation
if not st.session_state.student_id:
    pg = st.navigation([
        st.Page("pages/login.py", title="Sign In", icon="👁️"),
    ])
else:
    pg = st.navigation([
        st.Page("pages/dashboard.py",  title="Dashboard",      icon="🏠", default=True),
        st.Page("pages/chatbot.py",    title="Chatbot Tutor",  icon="💬"),
        st.Page("pages/flashcards.py", title="Flash-cards",    icon="🃏"),
        st.Page("pages/cases.py",      title="Case Simulator", icon="🏥"),
        st.Page("pages/image_quiz.py", title="Image Quiz",     icon="🔬"),
        st.Page("pages/admin.py",      title="Admin",          icon="⚙️"),
    ])

pg.run()
