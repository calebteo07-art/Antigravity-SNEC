from collections import defaultdict
from datetime import date

import streamlit as st
from pages._shared import _gsheets
from tools.shared.styles import ph, section_label, stat_card, topic_bar, start_item


def render() -> None:
    name = st.session_state.student_name
    st.markdown(ph("Dashboard", f"Welcome back, {name}."), unsafe_allow_html=True)

    with st.expander("System Status", expanded=False):
        from tools.shared.health_monitor import (
            check_anthropic, check_google_sheets,
            check_google_drive, check_tmp_dir,
        )
        checks = [check_anthropic(), check_google_sheets(), check_google_drive(), check_tmp_dir()]
        _status_icons = {"PASS": "🟢", "WARN": "🟡", "FAIL": "🔴", "INFO": "🔵"}
        hcols = st.columns(len(checks))
        for col, (status, sname, detail) in zip(hcols, checks):
            col.metric(sname, f"{_status_icons.get(status, '⚪')} {status}", help=detail)

    get_rows, _, __ = _gsheets()
    sid = st.session_state.student_id

    try:
        sessions = get_rows("snec_sessions",      {"student_id": sid})
        cards    = get_rows("snec_flashcards",    {"student_id": sid})
        cases    = get_rows("snec_case_results",  {"student_id": sid})
        images   = get_rows("snec_image_results", {"student_id": sid})

        today     = date.today().isoformat()
        due_cards = [c for c in cards if not c.get("next_due_date") or c["next_due_date"] <= today]
        due_txt   = f"{len(due_cards)} due today" if due_cards else "all caught up"

        st.markdown(section_label("Activity Overview"), unsafe_allow_html=True)
        s1, s2, s3, s4 = st.columns(4)
        with s1:
            st.markdown(stat_card("Chatbot Sessions", str(len(sessions)),
                                  "total Q&A sessions", "c-teal"), unsafe_allow_html=True)
        with s2:
            st.markdown(stat_card("Flash-cards", str(len(cards)),
                                  due_txt, "c-gold"), unsafe_allow_html=True)
        with s3:
            st.markdown(stat_card("Cases Attempted", str(len(cases)),
                                  "clinical simulations", "c-ok"), unsafe_allow_html=True)
        with s4:
            st.markdown(stat_card("Image Quizzes", str(len(images)),
                                  "retinal images reviewed", "c-blue"), unsafe_allow_html=True)

        if due_cards:
            st.markdown("<div style='height:.5rem'></div>", unsafe_allow_html=True)
            c_info, c_btn = st.columns([5, 1])
            with c_info:
                st.info(f"📚 {len(due_cards)} flash-card(s) are due for review today.")
            with c_btn:
                if st.button("Review now →", type="primary", use_container_width=True):
                    st.switch_page("pages/flashcards.py")

        if cards:
            topic_ef: dict = defaultdict(list)
            for c in cards:
                try:
                    ef = float(c.get("easiness_factor", 2.5))
                except (ValueError, TypeError):
                    ef = 2.5
                topic_ef[c.get("topic_tag", "unknown")].append(ef)

            topic_avg     = {t: sum(v) / len(v) for t, v in topic_ef.items()}
            sorted_topics = sorted(topic_avg.items(), key=lambda x: x[1])

            st.markdown(section_label("Flash-card Mastery by Topic"), unsafe_allow_html=True)
            t_left, t_right = st.columns(2)
            half = (len(sorted_topics) + 1) // 2
            for i, (t, ef) in enumerate(sorted_topics):
                col = t_left if i < half else t_right
                with col:
                    st.markdown(topic_bar(t, ef), unsafe_allow_html=True)

        if not sessions and not cards and not cases:
            st.markdown(section_label("Getting Started"), unsafe_allow_html=True)
            st.markdown(start_item(1, "Ask your first question",
                "Open Chatbot Tutor and ask anything about ophthalmology."), unsafe_allow_html=True)
            st.markdown(start_item(2, "Review your flash-cards",
                "Cards are auto-generated from every session you complete."), unsafe_allow_html=True)
            st.markdown(start_item(3, "Simulate a clinical case",
                "Interview an AI patient, request investigations, make your diagnosis."),
                unsafe_allow_html=True)

    except Exception as e:
        st.error(f"Could not load study data: {e}")


render()
