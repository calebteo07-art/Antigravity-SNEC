from datetime import date

import streamlit as st
from pages._shared import _gsheets
from tools.shared.styles import ph, section_label, flashcard_q, flashcard_a, named_progress


def render() -> None:
    st.markdown(ph("Flash-card Review",
        "Spaced repetition — only cards you're about to forget appear today."),
        unsafe_allow_html=True)

    get_rows, _, update_row = _gsheets()
    from tools.flashcards.sm2 import next_review, due_date

    sid = st.session_state.student_id

    if not st.session_state.review_cards or st.session_state.review_done:
        try:
            today     = date.today().isoformat()
            all_cards = get_rows("snec_flashcards", {"student_id": sid})
            due = [c for c in all_cards
                   if not c.get("next_due_date") or c["next_due_date"] <= today]
            st.session_state.review_cards = due
            st.session_state.review_index = 0
            st.session_state.review_done  = False
            st.session_state.card_revealed = False
        except Exception as e:
            st.error(f"Could not load flash-cards: {e}")
            return

    cards = st.session_state.review_cards
    idx   = st.session_state.review_index

    if not cards:
        st.markdown(
            '<div class="snec-card" style="border-color:rgba(16,185,129,.3)">'
            '  <div style="font-size:2rem;margin-bottom:.75rem">✓</div>'
            '  <div class="snec-card-q" style="font-size:1.2rem">All cards reviewed for today.</div>'
            '  <div class="snec-card-a" style="margin-top:.5rem">'
            'Come back tomorrow for your next session.</div>'
            '</div>',
            unsafe_allow_html=True,
        )
        if st.button("Refresh", use_container_width=False):
            st.session_state.review_cards = []
            st.rerun()
        return

    if idx >= len(cards):
        passed = st.session_state.get("review_passed", 0)
        total  = len(cards)
        pct    = int(passed / total * 100) if total else 0
        st.balloons()
        st.markdown(
            f'<div class="snec-card" style="border-color:rgba(6,214,192,.3)">'
            f'  <div style="font-size:2.5rem;margin-bottom:.6rem">🎉</div>'
            f'  <div class="snec-card-q">Session complete!</div>'
            f'  <div class="snec-card-a" style="margin-top:.5rem">'
            f'    {passed} of {total} cards recalled correctly &nbsp;·&nbsp; {pct}%'
            f'  </div>'
            f'</div>',
            unsafe_allow_html=True,
        )
        if st.button("Start Over", type="primary"):
            st.session_state.review_cards  = []
            st.session_state.review_passed = 0
            st.rerun()
        return

    st.markdown(
        named_progress(f"Card {idx + 1} of {len(cards)}",
                       f"{len(cards) - idx} remaining", idx / len(cards)),
        unsafe_allow_html=True,
    )

    card  = cards[idx]
    topic = card.get("topic_tag", "")

    st.markdown(flashcard_q(card["front"], topic), unsafe_allow_html=True)

    if not st.session_state.card_revealed:
        st.markdown("<div style='height:.5rem'></div>", unsafe_allow_html=True)
        if st.button("Reveal Answer  👁️", type="primary", use_container_width=True):
            st.session_state.card_revealed = True
            st.rerun()
    else:
        st.markdown("<div style='height:.5rem'></div>", unsafe_allow_html=True)
        st.markdown(flashcard_a(card["back"]), unsafe_allow_html=True)

        st.markdown(section_label("How well did you recall this?"), unsafe_allow_html=True)
        cols   = st.columns(6)
        labels = [
            ("0", "Blank",    "bd"),
            ("1", "Hint",     "bd"),
            ("2", "Saw ans",  "bm"),
            ("3", "Hard",     "bm"),
            ("4", "Hesitate", "bo"),
            ("5", "Perfect",  "bt"),
        ]
        for i, (col, (num, lbl, _)) in enumerate(zip(cols, labels)):
            with col:
                if st.button(f"{num}\n{lbl}", key=f"q{i}", use_container_width=True):
                    try:
                        ef = float(card.get("easiness_factor") or 2.5)
                        iv = int(card.get("interval_days") or 0)
                        rp = int(card.get("repetition_count") or 0)
                    except (ValueError, TypeError):
                        ef, iv, rp = 2.5, 0, 0

                    new_iv, new_ef, new_rp = next_review(i, rp, ef, iv)
                    update_row("snec_flashcards", "card_id", card["card_id"], {
                        "easiness_factor":  f"{new_ef:.2f}",
                        "interval_days":    str(new_iv),
                        "repetition_count": str(new_rp),
                        "next_due_date":    due_date(new_iv),
                        "last_reviewed":    date.today().isoformat(),
                    })
                    if i >= 3:
                        st.session_state.review_passed = (
                            st.session_state.get("review_passed", 0) + 1
                        )
                    st.session_state.review_index  += 1
                    st.session_state.card_revealed  = False
                    st.rerun()


render()
