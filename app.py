"""EyeQ — Streamlit Web UI

Run with:
    streamlit run app.py
"""

import json
import sys
from datetime import date
from pathlib import Path

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT))

# ---------------------------------------------------------------------------
# Page config (must be first Streamlit call)
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="EyeQ",
    page_icon="👁️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# Design system — inject once, transforms every page
# ---------------------------------------------------------------------------
from tools.shared.styles import (
    SNEC_CSS, ph, section_label, stat_card, topic_bar, badge,
    user_chip, wordmark, xp_toast, domain_card,
    flashcard_q, flashcard_a, start_item, named_progress,
)
st.markdown(SNEC_CSS, unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Lazy imports (avoid slow startup for unused features)
# ---------------------------------------------------------------------------
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


# ---------------------------------------------------------------------------
# Session state initialisation
# ---------------------------------------------------------------------------
DEFAULTS = {
    "page": "Login",
    "student_id": None,
    "student_name": None,
    "chat_messages": [],
    "case_conversation": [],
    "current_case": None,
    "case_result": None,
    "review_cards": [],
    "review_index": 0,
    "review_done": False,
    "card_revealed": False,
    "case_xp_result": None,
    "case_hints_used": 0,
    "case_hint_messages": [],
}
for k, v in DEFAULTS.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ---------------------------------------------------------------------------
# PDPA notice
# ---------------------------------------------------------------------------
PDPA_NOTICE = """
**Singapore Personal Data Protection Act (PDPA) — Data Collection Notice**

This platform collects and processes:
- Your name and email address (identity and progress tracking)
- Your Q&A session transcripts (flash-card generation)
- Your quiz and case simulation scores (analytics)

Your data will not be shared with third parties or used to train AI models.
You may withdraw consent at any time by contacting the platform administrator.
"""

# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------
def _sidebar() -> None:
    with st.sidebar:
        st.markdown(wordmark(), unsafe_allow_html=True)

        if st.session_state.student_id:
            st.markdown(user_chip(st.session_state.student_name), unsafe_allow_html=True)

            pages = {
                "🏠  Dashboard":      "Dashboard",
                "💬  Chatbot Tutor":  "Chatbot",
                "🃏  Flash-cards":    "Flashcards",
                "🏥  Case Simulator": "Cases",
                "🔬  Image Quiz":     "ImageQuiz",
                "⚙️  Admin":          "Admin",
            }
            for label, key in pages.items():
                if st.button(label, use_container_width=True,
                             type="primary" if st.session_state.page == key else "secondary"):
                    st.session_state.page = key
                    st.rerun()

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

        _, __, MOCK_MODE, ___ = _claude()
        if MOCK_MODE:
            st.markdown(
                f'<div style="margin-top:1rem">{badge("Mock mode", "bd")}</div>',
                unsafe_allow_html=True,
            )


# ---------------------------------------------------------------------------
# LOGIN PAGE
# ---------------------------------------------------------------------------
def page_login() -> None:
    col_hero, col_form = st.columns([1, 1], gap="large")

    with col_hero:
        st.markdown("""
        <div class="snec-login-hero">
          <div class="snec-login-eyeball">👁️</div>
          <div class="snec-login-title">Learn to see<br>what others <em>miss.</em></div>
          <div class="snec-login-desc">
            An AI-powered ophthalmology training platform for medical students
            and junior doctors at the Singapore National Eye Centre.
          </div>
          <div class="snec-feature-grid">
            <div class="snec-feature-item">
              <div class="snec-feature-icon">💬</div>
              <div>
                <div class="snec-feature-name">Chatbot Tutor</div>
                <div class="snec-feature-desc">Structured Q&amp;A with clinical pearls</div>
              </div>
            </div>
            <div class="snec-feature-item">
              <div class="snec-feature-icon">🃏</div>
              <div>
                <div class="snec-feature-name">Flash-cards</div>
                <div class="snec-feature-desc">SM-2 spaced repetition engine</div>
              </div>
            </div>
            <div class="snec-feature-item">
              <div class="snec-feature-icon">🏥</div>
              <div>
                <div class="snec-feature-name">Case Simulator</div>
                <div class="snec-feature-desc">Interactive AI patient encounters</div>
              </div>
            </div>
            <div class="snec-feature-item">
              <div class="snec-feature-icon">🔬</div>
              <div>
                <div class="snec-feature-name">Image Quiz</div>
                <div class="snec-feature-desc">Retinal image interpretation</div>
              </div>
            </div>
          </div>
        </div>
        """, unsafe_allow_html=True)

    with col_form:
        st.markdown("<div style='padding-top:2.5rem'>", unsafe_allow_html=True)
        st.markdown(section_label("Sign in / Register"), unsafe_allow_html=True)

        name  = st.text_input("Full name",      placeholder="e.g. Tan Wei Ming")
        email = st.text_input("Email address",  placeholder="e.g. student@nus.edu.sg")

        with st.expander("📋 PDPA Data Collection Notice"):
            st.markdown(PDPA_NOTICE)

        consent = st.checkbox("I have read and consent to the above notice")

        if st.button("Enter Platform →", type="primary", use_container_width=True):
            if not name.strip():
                st.error("Please enter your full name.")
            elif not email.strip() or "@" not in email:
                st.error("Please enter a valid email address.")
            elif not consent:
                st.error("You must accept the data collection notice to continue.")
            else:
                with st.spinner("Setting up your account..."):
                    try:
                        get_or_create, has_consented, record_consent, get_profile = _identity()
                        sid = get_or_create(name.strip(), email.strip())
                        if not has_consented(sid):
                            record_consent(sid)
                        st.session_state.student_id = sid
                        st.session_state.student_name = name.strip()
                        st.session_state.page = "Dashboard"
                        st.rerun()
                    except Exception as e:
                        st.error(f"Login failed: {e}")

        st.markdown("</div>", unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# DASHBOARD PAGE
# ---------------------------------------------------------------------------
def page_dashboard() -> None:
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
            col.metric(sname, f"{_status_icons.get(status,'⚪')} {status}", help=detail)

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

        # ── Stat cards ──────────────────────────────────────────────────────
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

        # ── Due cards CTA ────────────────────────────────────────────────────
        if due_cards:
            st.markdown("<div style='height:.5rem'></div>", unsafe_allow_html=True)
            c_info, c_btn = st.columns([5, 1])
            with c_info:
                st.info(f"📚 {len(due_cards)} flash-card(s) are due for review today.")
            with c_btn:
                if st.button("Review now →", type="primary", use_container_width=True):
                    st.session_state.page = "Flashcards"
                    st.rerun()

        # ── Topic performance ────────────────────────────────────────────────
        if cards:
            from collections import defaultdict
            topic_ef: dict = defaultdict(list)
            for c in cards:
                try:
                    ef = float(c.get("easiness_factor", 2.5))
                except (ValueError, TypeError):
                    ef = 2.5
                topic_ef[c.get("topic_tag", "unknown")].append(ef)

            topic_avg   = {t: sum(v)/len(v) for t, v in topic_ef.items()}
            sorted_topics = sorted(topic_avg.items(), key=lambda x: x[1])

            st.markdown(section_label("Flash-card Mastery by Topic"), unsafe_allow_html=True)
            t_left, t_right = st.columns(2)
            half = (len(sorted_topics) + 1) // 2
            for i, (t, ef) in enumerate(sorted_topics):
                col = t_left if i < half else t_right
                with col:
                    st.markdown(topic_bar(t, ef), unsafe_allow_html=True)

        # ── Getting started ──────────────────────────────────────────────────
        if not sessions and not cards and not cases:
            st.markdown(section_label("Getting Started"), unsafe_allow_html=True)
            st.markdown(start_item(1, "Ask your first question",
                "Open Chatbot Tutor and ask anything about ophthalmology."), unsafe_allow_html=True)
            st.markdown(start_item(2, "Review your flash-cards",
                "Cards are auto-generated from every session you complete."), unsafe_allow_html=True)
            st.markdown(start_item(3, "Simulate a clinical case",
                "Interview an AI patient, request investigations, make your diagnosis."), unsafe_allow_html=True)

    except Exception as e:
        st.error(f"Could not load study data: {e}")


# ---------------------------------------------------------------------------
# CHATBOT PAGE
# ---------------------------------------------------------------------------
def page_chatbot() -> None:
    st.markdown(ph("Chatbot Tutor",
        "Ask any ophthalmology question — every answer follows: "
        "Explanation → Mechanism → Clinical Pearl → Check Your Understanding."),
        unsafe_allow_html=True)

    ask, _, MOCK_MODE, MODEL = _claude()
    if MOCK_MODE:
        st.warning("⚠️ Mock mode — responses are simulated. Add API key to `.env` for real AI.")

    # Display conversation
    for msg in st.session_state.chat_messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # End session button
    if st.session_state.chat_messages:
        col1, col2 = st.columns([4, 1])
        with col2:
            if st.button("End Session 💾", type="secondary"):
                with st.spinner("Saving session and generating flash-cards..."):
                    try:
                        from tools.chatbot.log_session import log_session
                        from tools.flashcards.generate_cards import generate_cards

                        sid = st.session_state.student_id
                        messages = st.session_state.chat_messages
                        topic = next((m["content"][:80] for m in messages if m["role"] == "user"), "")

                        session_id = log_session(
                            student_id=sid,
                            topic=topic,
                            messages=messages,
                            token_count=0,
                            model="mock" if MOCK_MODE else MODEL,
                        )
                        system_prompt = _load_kb()
                        card_count = generate_cards(sid, session_id, messages, system_prompt)

                        st.session_state.chat_messages = []
                        st.success(f"Session saved! {card_count} flash-card(s) generated.")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Failed to save session: {e}")

    # Chat input
    if prompt := st.chat_input("Ask an ophthalmology question..."):
        st.session_state.chat_messages.append({"role": "user", "content": prompt})

        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                system_prompt = _load_kb()
                # Keep only the last 10 messages — older context rarely improves answers
                # and grows the bill linearly with session length
                recent_messages = st.session_state.chat_messages[-10:]
                response = ask(
                    system_prompt=system_prompt,
                    messages=recent_messages,
                    max_tokens=1024,
                    feature="chatbot",
                )
            st.markdown(response)

        st.session_state.chat_messages.append({"role": "assistant", "content": response})
        st.rerun()


# ---------------------------------------------------------------------------
# FLASHCARDS PAGE
# ---------------------------------------------------------------------------
def page_flashcards() -> None:
    st.markdown(ph("Flash-card Review",
        "Spaced repetition — only cards you're about to forget appear today."),
        unsafe_allow_html=True)

    get_rows, _, update_row = _gsheets()
    from tools.flashcards.sm2 import next_review, due_date

    sid = st.session_state.student_id

    # Load due cards once per session
    if not st.session_state.review_cards or st.session_state.review_done:
        try:
            today = date.today().isoformat()
            all_cards = get_rows("snec_flashcards", {"student_id": sid})
            due = [c for c in all_cards if not c.get("next_due_date") or c["next_due_date"] <= today]
            st.session_state.review_cards = due
            st.session_state.review_index = 0
            st.session_state.review_done = False
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
            '  <div class="snec-card-a" style="margin-top:.5rem">Come back tomorrow for your next session.</div>'
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
            st.session_state.review_cards = []
            st.session_state.review_passed = 0
            st.rerun()
        return

    # Progress
    st.markdown(
        named_progress(f"Card {idx+1} of {len(cards)}",
                       f"{len(cards)-idx} remaining", idx / len(cards)),
        unsafe_allow_html=True,
    )

    card  = cards[idx]
    topic = card.get("topic_tag", "")

    # Card face — question
    st.markdown(flashcard_q(card["front"], topic), unsafe_allow_html=True)

    if not st.session_state.card_revealed:
        st.markdown("<div style='height:.5rem'></div>", unsafe_allow_html=True)
        if st.button("Reveal Answer  👁️", type="primary", use_container_width=True):
            st.session_state.card_revealed = True
            st.rerun()
    else:
        st.markdown("<div style='height:.5rem'></div>", unsafe_allow_html=True)
        # Card face — answer
        st.markdown(flashcard_a(card["back"]), unsafe_allow_html=True)

        st.markdown(section_label("How well did you recall this?"), unsafe_allow_html=True)
        cols  = st.columns(6)
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
                        "easiness_factor": f"{new_ef:.2f}",
                        "interval_days":   str(new_iv),
                        "repetition_count": str(new_rp),
                        "next_due_date":   due_date(new_iv),
                        "last_reviewed":   date.today().isoformat(),
                    })
                    if i >= 3:
                        st.session_state.review_passed = st.session_state.get("review_passed", 0) + 1
                    st.session_state.review_index   += 1
                    st.session_state.card_revealed   = False
                    st.rerun()


# ---------------------------------------------------------------------------
# CASE SIMULATOR PAGE
# ---------------------------------------------------------------------------

_TOPIC_EMOJI = {
    "glaucoma": "👁️", "retina": "🔬", "cornea": "🌊",
    "neuro-ophthalmology": "🧠", "lens": "💎", "cataract": "💎",
}
_DIFF_STARS = {
    "beginner": "⭐", "intermediate": "⭐⭐", "advanced": "⭐⭐⭐", "expert": "⭐⭐⭐⭐",
}
_MAX_HINTS = 3


def _reset_case_state() -> None:
    st.session_state.current_case = None
    st.session_state.case_conversation = []
    st.session_state.case_result = None
    st.session_state.case_xp_result = None
    st.session_state.case_hints_used = 0
    st.session_state.case_hint_messages = []


def page_cases() -> None:
    import json as _json

    ask, _, MOCK_MODE, MODEL = _claude()
    from tools.cases.load_case import list_available_cases, load_case
    from tools.cases.evaluate_response import evaluate_case
    from tools.cases.log_result import log_case_result
    from tools.flashcards.generate_cards import generate_cards

    try:
        from tools.shared.progress import (
            get_level_info, calculate_xp_reward,
            get_progress, update_progress, BADGES,
        )
        _prog_ok = True
    except Exception:
        _prog_ok = False

    sid = st.session_state.student_id

    # ── LEVEL BANNER (shared helper) ─────────────────────────────────────────
    def _level_banner() -> None:
        if not _prog_ok:
            return
        try:
            prog  = get_progress(sid)
            info  = get_level_info(prog["total_xp"])
            w     = int(info["progress_pct"] * 100)
            extra = ""
            if prog.get("streak_days", 0) > 1:
                extra += f' <span style="color:var(--gold)">· 🔥 {prog["streak_days"]}d</span>'
            nb = len(prog.get("badges", []))
            if nb:
                extra += f' <span style="color:var(--txt-3)">· 🏅 {nb}</span>'
            next_txt = (f"{info['xp_to_next']:,} XP until {info['next_name']}"
                        if info["next_threshold"] else "Maximum rank achieved")
            st.markdown(f"""
            <div style="background:var(--bg-card);border:1px solid var(--border);
                border-radius:var(--r2);padding:.85rem 1.25rem;
                display:flex;align-items:center;gap:1.2rem;margin-bottom:.9rem">
              <div style="font-size:1.75rem;line-height:1">{info['icon']}</div>
              <div style="flex:1;min-width:0">
                <div style="font-size:.84rem;font-weight:600;color:var(--txt);white-space:nowrap">
                  {info['name']}
                  <span style="color:var(--txt-3);font-weight:400;font-size:.76rem">
                    &nbsp;Lv.{info['level_num']}&nbsp;·&nbsp;{prog['total_xp']:,} XP
                  </span>{extra}
                </div>
                <div style="background:var(--bg-raised);border-radius:99px;height:5px;
                    overflow:hidden;margin:.4rem 0">
                  <div style="width:{w}%;height:100%;border-radius:99px;
                      background:linear-gradient(90deg,var(--accent),#04C4B2);
                      box-shadow:0 0 8px var(--accent-glow)"></div>
                </div>
                <div style="font-size:.68rem;color:var(--txt-3)">{next_txt}</div>
              </div>
            </div>
            """, unsafe_allow_html=True)
        except Exception:
            pass

    # ════════════════════════════════════════════════════════════════════════
    # VIEW 1 — CASE SELECTION
    # ════════════════════════════════════════════════════════════════════════
    if st.session_state.current_case is None and st.session_state.case_result is None:
        st.markdown(ph("Case Simulator",
            "Interview the AI patient · Request investigations · Diagnose · Manage."),
            unsafe_allow_html=True)
        _level_banner()

        if MOCK_MODE:
            st.warning("⚠️ Mock mode — patient responses and evaluation are simulated.")

        available = list_available_cases()
        if not available:
            st.error("No cases available. Add JSON files to the `cases/` directory.")
            return

        st.markdown(section_label("Available Cases"), unsafe_allow_html=True)

        # Case cards — up to 3 per row
        cases_data: list[dict] = []
        for cid in available:
            try:
                cases_data.append(load_case(cid))
            except Exception:
                pass

        cols = st.columns(min(len(cases_data), 3))
        for i, case in enumerate(cases_data):
            with cols[i % 3]:
                diff  = case.get("difficulty", "intermediate")
                topic = case.get("topic", "")
                stars = _DIFF_STARS.get(diff, "⭐⭐")
                emoji = _TOPIC_EMOJI.get(topic, "🏥")
                mins  = case.get("estimated_minutes", "?")

                with st.container(border=True):
                    st.markdown(f"### {emoji} {case['title']}")
                    st.markdown(f"{stars} **{diff.capitalize()}**  ·  ⏱️ ~{mins} min")
                    st.caption(f"Topic: {topic.replace('-', ' ').title()}")
                    st.markdown("**Up to 800 XP** per attempt")
                    st.markdown(
                        "**Earn bonus XP for:**\n"
                        "- Correct diagnosis & management\n"
                        "- Perfect domain scores (+50 XP each)\n"
                        "- Finishing quickly (+75 XP)\n"
                        "- Using zero hints (+badge)"
                    )
                    if st.button(
                        "▶ Start Case",
                        key=f"start_{case['case_id']}",
                        type="primary",
                        use_container_width=True,
                    ):
                        _reset_case_state()
                        st.session_state.current_case = case
                        st.rerun()

        # Badge wall
        if _prog_ok:
            try:
                prog = get_progress(sid)
                if prog.get("badges"):
                    st.markdown(section_label("Your Badges"), unsafe_allow_html=True)
                    bcols = st.columns(min(len(prog["badges"]), 6))
                    for col, bkey in zip(bcols, prog["badges"]):
                        bname, bicon, bdesc = BADGES.get(bkey, (bkey, "🏅", ""))
                        with col:
                            st.markdown(
                                f'<div style="text-align:center;background:var(--bg-raised);'
                                f'border:1px solid var(--border);border-radius:var(--r);'
                                f'padding:.8rem .5rem">'
                                f'  <div style="font-size:1.6rem;margin-bottom:.3rem">{bicon}</div>'
                                f'  <div style="font-size:.7rem;font-weight:600;color:var(--txt);'
                                f'    margin-bottom:.15rem">{bname}</div>'
                                f'  <div style="font-size:.62rem;color:var(--txt-3);line-height:1.35">'
                                f'    {bdesc}</div>'
                                f'</div>',
                                unsafe_allow_html=True,
                            )
            except Exception:
                pass
        return

    # ════════════════════════════════════════════════════════════════════════
    # VIEW 2 — RESULTS
    # ════════════════════════════════════════════════════════════════════════
    if st.session_state.case_result is not None:
        case   = st.session_state.current_case
        result = st.session_state.case_result
        total  = int(result.get("total_score", 0))
        pct    = int(total / 40 * 100)

        # Calculate and persist XP exactly once (when xp_result is still None)
        if _prog_ok and st.session_state.case_xp_result is None:
            try:
                msg_count = sum(
                    1 for m in st.session_state.case_conversation if m["role"] == "user"
                )
                prog        = get_progress(sid)
                is_first    = prog["cases_completed"] == 0
                hints_used  = st.session_state.get("case_hints_used", 0)
                xp_reward   = calculate_xp_reward(
                    result=result,
                    message_count=msg_count,
                    is_first_case=is_first,
                    hints_used=hints_used,
                    cases_completed=prog["cases_completed"],
                )
                # Only surface badges the student doesn't already own
                new_badges = [b for b in xp_reward["new_badges"] if b not in prog["badges"]]
                xp_reward["new_badges"] = new_badges
                update_progress(sid, xp_reward["total_xp"], new_badges)
                st.session_state.case_xp_result = xp_reward

                if total == 40:
                    st.snow()
                elif total >= 30:
                    st.balloons()
            except Exception as exc:
                st.session_state.case_xp_result = {
                    "total_xp": 0, "new_badges": [], "error": str(exc),
                }

        xp = st.session_state.case_xp_result or {}

        # Header
        grade = "🥇" if pct >= 90 else "🥈" if pct >= 75 else "🥉" if pct >= 60 else "📋"
        st.markdown(ph(f"{grade} {case['title']}",
            f"Case complete · {total}/40 points · {pct}%"),
            unsafe_allow_html=True)

        # XP + level row
        if xp.get("total_xp", 0) > 0:
            xp_col, lv_col = st.columns([1, 2], gap="large")
            with xp_col:
                st.markdown(xp_toast(xp["total_xp"]), unsafe_allow_html=True)
            with lv_col:
                _level_banner()
                with st.expander("⚡ XP Breakdown"):
                    rows_html = f'<div style="font-size:.82rem;color:var(--txt-2)">Base: <b style="color:var(--txt)">{xp.get("base_xp",0)} XP</b> (score × 10)</div>'
                    for bname, bval in xp.get("bonuses", []):
                        rows_html += f'<div style="font-size:.8rem;color:#6EE7B7">+ {bval} XP &nbsp;<span style="color:var(--txt-3)">{bname}</span></div>'
                    for pname, pval in xp.get("penalties", []):
                        rows_html += f'<div style="font-size:.8rem;color:#FCA5A5">{pval} XP &nbsp;<span style="color:var(--txt-3)">{pname}</span></div>'
                    rows_html += f'<div style="font-size:.86rem;font-weight:700;color:var(--accent);margin-top:.4rem;border-top:1px solid var(--border);padding-top:.4rem">Total: {xp.get("total_xp",0):,} XP</div>'
                    st.markdown(rows_html, unsafe_allow_html=True)

        st.markdown(section_label("Performance Breakdown"), unsafe_allow_html=True)

        # Domain score cards
        domains = [
            ("History",        "📝", "history_score",        "history_feedback"),
            ("Investigations", "🔬", "investigations_score",  "investigations_feedback"),
            ("Diagnosis",      "🎯", "diagnosis_score",       "diagnosis_feedback"),
            ("Management",     "💊", "management_score",      "management_feedback"),
        ]
        dcols = st.columns(4)
        for col, (lbl, icon, sk, _) in zip(dcols, domains):
            with col:
                st.markdown(domain_card(lbl, icon, int(result.get(sk, 0))),
                            unsafe_allow_html=True)

        # Total score bar
        tc = "#10B981" if total >= 30 else "#F59E0B" if total >= 20 else "#EF4444"
        st.markdown(
            f'<div style="margin-top:.75rem">'
            f'{named_progress(f"Total  {total}/40", f"{pct}%", total/40)}'
            f'</div>',
            unsafe_allow_html=True,
        )

        # Written feedback
        with st.expander("📋 Detailed Feedback", expanded=True):
            for lbl, icon, sk, fbk in domains:
                fb    = result.get(fbk, "")
                score = int(result.get(sk, 0))
                if fb:
                    if score >= 8:
                        st.success(f"**{icon} {lbl} ({score}/10):** {fb}")
                    elif score >= 5:
                        st.warning(f"**{icon} {lbl} ({score}/10):** {fb}")
                    else:
                        st.error(f"**{icon} {lbl} ({score}/10):** {fb}")
            if result.get("overall_feedback"):
                st.info(f"**Overall:** {result['overall_feedback']}")

        # New badges
        new_badges = xp.get("new_badges", [])
        if new_badges:
            st.markdown(section_label("Badges Unlocked"), unsafe_allow_html=True)
            bcols = st.columns(min(len(new_badges), 5))
            for col, bkey in zip(bcols, new_badges):
                bname, bicon, bdesc = BADGES.get(bkey, (bkey, "🏅", ""))
                with col:
                    st.markdown(
                        f'<div style="text-align:center;background:var(--accent-10);'
                        f'border:1px solid var(--accent-20);border-radius:var(--r);padding:.9rem .5rem">'
                        f'  <div style="font-size:1.7rem;margin-bottom:.3rem">{bicon}</div>'
                        f'  <div style="font-size:.72rem;font-weight:700;color:var(--accent);'
                        f'    margin-bottom:.12rem">{bname}</div>'
                        f'  <div style="font-size:.62rem;color:var(--txt-3);line-height:1.35">{bdesc}</div>'
                        f'</div>',
                        unsafe_allow_html=True,
                    )

        # Actions
        st.markdown("<div style='height:.75rem'></div>", unsafe_allow_html=True)
        a1, a2 = st.columns(2)
        with a1:
            if st.button("↩ Try Another Case", type="primary", use_container_width=True):
                _reset_case_state()
                st.rerun()
        with a2:
            if st.button("🏠 Dashboard", use_container_width=True):
                _reset_case_state()
                st.session_state.page = "Dashboard"
                st.rerun()
        return

    # ════════════════════════════════════════════════════════════════════════
    # VIEW 3 — ACTIVE CASE
    # ════════════════════════════════════════════════════════════════════════
    case = st.session_state.current_case

    # Sidebar: case info + turn counter + hints + phase checklist
    with st.sidebar:
        st.markdown("---")
        st.markdown(f"**{case['title']}**")
        diff  = case.get("difficulty", "")
        topic = case.get("topic", "")
        st.markdown(
            f"{_DIFF_STARS.get(diff, '')} {diff.capitalize()}  ·  "
            f"{_TOPIC_EMOJI.get(topic, '🏥')} {topic.replace('-', ' ').title()}"
        )
        st.markdown(
            f"**Patient:** {case['patient']['name']}, "
            f"{case['patient']['age']}y {case['patient']['gender']}"
        )
        st.caption(f"*{case['patient']['presenting_complaint']}*")

        st.markdown("---")
        turn_count = sum(1 for m in st.session_state.case_conversation if m["role"] == "user")
        st.metric("Your turns", turn_count, help="Speed bonus unlocks at ≤8 turns")

        st.markdown("**Phase Guide**")
        for phase in ["☐ History", "☐ Investigations", "☐ Diagnosis", "☐ Management"]:
            st.markdown(phase)

        # Hint system
        st.markdown("---")
        hints_used      = st.session_state.get("case_hints_used", 0)
        hints_remaining = _MAX_HINTS - hints_used
        filled   = "💡" * hints_remaining
        depleted = "⬜" * hints_used
        st.markdown(f"**Hints:** {filled}{depleted}")
        st.caption("Each hint costs 20 XP from your final reward")

        if hints_remaining > 0:
            if st.button("💡 Use a Hint", use_container_width=True):
                hint_sys = (
                    "You are a clinical tutor. A student is working through an ophthalmology case. "
                    f"The patient's presenting complaint is: {case['patient']['presenting_complaint']}. "
                    "Give a single helpful 1-sentence clinical nudge about what the student should "
                    "ask or do next, WITHOUT revealing the diagnosis. Keep it subtle."
                )
                with st.spinner("Generating hint..."):
                    hint_text = ask(
                        system_prompt=hint_sys,
                        messages=[{"role": "user", "content": "I need a hint for my next step."}],
                        max_tokens=80,
                        feature="chatbot",
                        model="claude-haiku-4-5",
                    )
                st.session_state.case_hints_used = hints_used + 1
                st.session_state.case_hint_messages.append(hint_text)
                st.rerun()
        else:
            st.caption("No hints remaining")

    # Main area header
    diff_label = _DIFF_STARS.get(case.get("difficulty",""), "⭐⭐")
    st.markdown(ph(case["title"],
        f"{diff_label} {case.get('difficulty','').capitalize()}  ·  "
        f"Interview the patient, request investigations, then submit."),
        unsafe_allow_html=True)
    if MOCK_MODE:
        st.warning("⚠️ Mock mode — patient responses are simulated.")

    # Active hints
    for hint in st.session_state.get("case_hint_messages", []):
        st.markdown(
            f'<div class="snec-hint">💡 <strong>Hint:</strong> {hint}</div>',
            unsafe_allow_html=True,
        )

    # Patient system prompt
    patient_prompt = (
        "You are playing the role of a patient in a clinical simulation.\n"
        "Answer ONLY what the student directly asks. Use lay language.\n"
        "If asked for examination findings or investigations, provide them from the case.\n"
        "Do NOT reveal the diagnosis.\n\n"
        f"Case: {_json.dumps(case, separators=(',', ':'))}"
    )

    # Conversation display
    for msg in st.session_state.case_conversation:
        role  = "user" if msg["role"] == "user" else "assistant"
        label = "You (Doctor)" if role == "user" else f"Patient ({case['patient']['name']})"
        with st.chat_message(role):
            st.markdown(f"**{label}:** {msg['content']}")

    # Submit for evaluation
    if st.session_state.case_conversation:
        if st.button("📋 Submit for Evaluation", type="primary"):
            with st.spinner("Evaluating your performance..."):
                try:
                    result = evaluate_case(case, st.session_state.case_conversation, sid)
                    log_case_result(sid, case, result)
                    generate_cards(sid, case["case_id"], st.session_state.case_conversation)
                    st.session_state.case_result  = result
                    st.session_state.case_xp_result = None  # trigger XP calc on results page
                    st.rerun()
                except Exception as e:
                    st.error(f"Evaluation failed: {e}")

    # Chat input
    if prompt := st.chat_input("Talk to the patient or request investigations..."):
        st.session_state.case_conversation.append({"role": "user", "content": prompt})
        with st.spinner("Patient responding..."):
            response = ask(
                system_prompt=patient_prompt,
                messages=st.session_state.case_conversation,
                max_tokens=512,
                feature="case",
            )
        st.session_state.case_conversation.append({"role": "assistant", "content": response})
        st.rerun()


# ---------------------------------------------------------------------------
# IMAGE QUIZ PAGE
# ---------------------------------------------------------------------------
def page_image_quiz() -> None:
    st.markdown(ph("Image Quiz",
        "Describe the retinal image systematically — you'll be scored on what you identify, "
        "miss, and over-call."),
        unsafe_allow_html=True)

    _, __, MOCK_MODE, ___ = _claude()
    if MOCK_MODE:
        st.warning("⚠️ Mock mode — evaluation uses simulated scoring.")

    from tools.image_quiz.evaluate_description import evaluate_description
    from tools.image_quiz.log_result import log_image_result

    images_dir = PROJECT_ROOT / "images"
    image_files = list(images_dir.glob("*.png")) + list(images_dir.glob("*.jpg"))
    images_with_meta = []
    for img in sorted(image_files):
        meta_path = img.with_suffix(".json")
        if meta_path.exists():
            try:
                meta = json.loads(meta_path.read_text(encoding="utf-8"))
                images_with_meta.append((img, meta))
            except Exception:
                pass

    if not images_with_meta:
        st.error("No images found in `images/` directory. Add PNG/JPG files with matching JSON metadata.")
        return

    options = {
        f"{m.get('modality','').replace('_',' ').title()} — {img.stem}": (img, m)
        for img, m in images_with_meta
    }
    chosen    = st.selectbox("Select an image", list(options.keys()))
    img_path, img_meta = options[chosen]

    col_img, col_form = st.columns([1, 1], gap="large")

    with col_img:
        modality   = img_meta.get("modality", "").replace("_", " ").title()
        eye        = img_meta.get("eye", "").title()
        difficulty = img_meta.get("difficulty", "").upper()
        caption    = "  ·  ".join(filter(None, [modality, f"{eye} eye" if eye else "", difficulty]))
        st.image(str(img_path), caption=caption, use_container_width=True)

        # Findings checklist guide
        st.markdown(
            '<div style="background:var(--bg-raised);border:1px solid var(--border);'
            'border-radius:var(--r);padding:.85rem 1rem;margin-top:.5rem">'
            '<div style="font-size:.66rem;font-weight:700;text-transform:uppercase;'
            'letter-spacing:.1em;color:var(--txt-3);margin-bottom:.6rem">Systematic Approach</div>'
            '<div style="display:grid;gap:.35rem">'
            + "".join(
                f'<div style="display:flex;gap:.5rem;align-items:flex-start">'
                f'  <span style="color:var(--accent);font-size:.75rem;margin-top:.1rem">◆</span>'
                f'  <span style="font-size:.78rem;color:var(--txt-2)">{item}</span>'
                f'</div>'
                for item in [
                    "<b style='color:var(--txt)'>Optic disc</b> — size, C:D ratio, rim, haemorrhages",
                    "<b style='color:var(--txt)'>Macula</b> — foveal reflex, drusen, exudates",
                    "<b style='color:var(--txt)'>Blood vessels</b> — calibre, A:V ratio, crossings",
                    "<b style='color:var(--txt)'>Periphery</b> — lesions, detachment",
                    "<b style='color:var(--txt)'>Diagnosis</b> — primary diagnosis &amp; differentials",
                ]
            )
            + '</div></div>',
            unsafe_allow_html=True,
        )

    with col_form:
        st.markdown(section_label("Your Description"), unsafe_allow_html=True)
        description = st.text_area("", height=220,
                                   placeholder="The optic disc shows a cup-to-disc ratio of approximately...")

        if st.button("Submit for Evaluation →", type="primary", use_container_width=True):
            if not description.strip():
                st.error("Please enter a description before submitting.")
            else:
                with st.spinner("Evaluating your description..."):
                    try:
                        result = evaluate_description(img_meta, description.strip(), img_path)
                        result["_raw_description"] = description.strip()
                        log_image_result(st.session_state.student_id, img_meta, result)

                        score = result.get("score", 0)
                        sc    = "#10B981" if score >= 7 else "#F59E0B" if score >= 4 else "#EF4444"

                        st.markdown(
                            f'<div style="background:var(--bg-raised);border:1px solid {sc}33;'
                            f'border-radius:var(--r2);padding:1rem 1.25rem;margin-bottom:.75rem">'
                            f'  <div style="font-size:.66rem;font-weight:700;text-transform:uppercase;'
                            f'    letter-spacing:.1em;color:var(--txt-3);margin-bottom:.25rem">Score</div>'
                            f'  <div style="font-family:var(--serif);font-size:2.5rem;color:{sc};line-height:1">'
                            f'    {score}<span style="font-size:1rem;color:var(--txt-3)">/10</span></div>'
                            f'</div>',
                            unsafe_allow_html=True,
                        )

                        correct   = result.get("correct_findings", [])
                        missed    = result.get("missed_findings", [])
                        incorrect = result.get("incorrect_findings", [])

                        if correct:
                            st.success("**Identified:** " + " · ".join(f"✓ {f}" for f in correct))
                        if missed:
                            st.warning("**Missed:** " + " · ".join(f"✗ {f}" for f in missed))
                        if incorrect:
                            st.error("**Over-called:** " + " · ".join(f"✗ {f}" for f in incorrect))
                        if result.get("feedback"):
                            st.info(result["feedback"])
                    except Exception as e:
                        st.error(f"Evaluation failed: {e}")


# ---------------------------------------------------------------------------
# ADMIN PAGE
# ---------------------------------------------------------------------------
def page_admin() -> None:
    st.markdown(ph("Admin", "System maintenance tools — for platform administrators."),
                unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        with st.expander("💰 Cost Monitor", expanded=True):
            threshold = st.number_input("Alert threshold (USD/month)", value=20.0, step=5.0)
            if st.button("Run Cost Report"):
                with st.spinner("Loading usage data..."):
                    try:
                        from tools.shared.gsheets import get_rows
                        rows = get_rows("snec_api_usage")
                        if not rows:
                            st.info("No API usage recorded yet.")
                        else:
                            total_cost = sum(float(r.get("estimated_cost_usd", 0) or 0) for r in rows)
                            total_calls = len(rows)
                            st.metric("Total API calls", total_calls)
                            st.metric("Total cost (USD)", f"${total_cost:.4f}")
                    except Exception as e:
                        st.error(str(e))

        with st.expander("💾 Backup Audit Log"):
            keep = st.number_input("Keep N lines locally", value=500, step=100)
            if st.button("Run Backup"):
                with st.spinner("Uploading audit log to Drive..."):
                    try:
                        from tools.shared.backup import run_backup
                        run_backup(int(keep))
                        st.success("Backup complete.")
                    except Exception as e:
                        st.error(str(e))

    with col2:
        with st.expander("🗂️ Schema Check", expanded=True):
            dry_run = st.checkbox("Dry run (preview only)", value=True)
            if st.button("Check Schema"):
                with st.spinner("Checking sheet schemas..."):
                    try:
                        from tools.shared.schema_migration import check_and_migrate, EXPECTED_SCHEMA
                        from tools.shared.gsheets import _get_spreadsheet
                        ss = _get_spreadsheet()
                        results = []
                        for sheet_name, expected in EXPECTED_SCHEMA.items():
                            try:
                                ws = ss.worksheet(sheet_name)
                                current = ws.row_values(1)
                                missing = [c for c in expected if c not in current]
                                results.append((sheet_name, "✅ OK" if not missing else f"⚠️ Missing: {missing}"))
                            except Exception:
                                results.append((sheet_name, "❌ Not found"))

                        for name, status in results:
                            st.markdown(f"**{name}:** {status}")
                    except Exception as e:
                        st.error(str(e))

        with st.expander("🔧 Full Health Check"):
            if st.button("Run Health Check"):
                with st.spinner("Checking all systems..."):
                    try:
                        from tools.shared.health_monitor import (
                            check_anthropic, check_google_sheets,
                            check_google_drive, check_tmp_dir,
                            check_audit_log, check_cases, check_images,
                        )
                        checks = [
                            check_anthropic(), check_google_sheets(),
                            check_google_drive(), check_tmp_dir(),
                            check_audit_log(), check_cases(), check_images(),
                        ]
                        icons = {"PASS": "✅", "WARN": "⚠️", "FAIL": "❌", "INFO": "ℹ️"}
                        for status, name, detail in checks:
                            st.markdown(f"{icons.get(status, '❓')} **{name}:** {detail}")
                    except Exception as e:
                        st.error(str(e))


# ---------------------------------------------------------------------------
# Router
# ---------------------------------------------------------------------------
_sidebar()

page = st.session_state.page

if page == "Login" or not st.session_state.student_id:
    page_login()
elif page == "Dashboard":
    page_dashboard()
elif page == "Chatbot":
    page_chatbot()
elif page == "Flashcards":
    page_flashcards()
elif page == "Cases":
    page_cases()
elif page == "ImageQuiz":
    page_image_quiz()
elif page == "Admin":
    page_admin()
