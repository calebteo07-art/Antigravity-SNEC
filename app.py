"""SNEC AI Learning Platform — Streamlit Web UI

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
    page_title="SNEC AI Learning Platform",
    page_icon="👁️",
    layout="wide",
    initial_sidebar_state="expanded",
)

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
        st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/8/8e/Singapore_Eye_logo.png/120px-Singapore_Eye_logo.png",
                 width=60, caption="SNEC AI")

        st.markdown("## 👁️ SNEC AI Platform")

        if st.session_state.student_id:
            st.success(f"Logged in as **{st.session_state.student_name}**")
            st.markdown("---")

            pages = {
                "🏠 Dashboard": "Dashboard",
                "💬 Chatbot Tutor": "Chatbot",
                "🃏 Flash-cards": "Flashcards",
                "🏥 Case Simulator": "Cases",
                "🔬 Image Quiz": "ImageQuiz",
                "⚙️ Admin": "Admin",
            }
            for label, key in pages.items():
                if st.button(label, use_container_width=True,
                             type="primary" if st.session_state.page == key else "secondary"):
                    st.session_state.page = key
                    st.rerun()

            st.markdown("---")
            if st.button("🚪 Log Out", use_container_width=True):
                for k, v in DEFAULTS.items():
                    st.session_state[k] = v
                st.rerun()
        else:
            st.info("Please log in to continue.")

        # Mock mode badge
        _, __, MOCK_MODE, ___ = _claude()
        if MOCK_MODE:
            st.warning("⚠️ Mock mode — add `ANTHROPIC_API_KEY` to `.env` for real AI")


# ---------------------------------------------------------------------------
# LOGIN PAGE
# ---------------------------------------------------------------------------
def page_login() -> None:
    st.title("👁️ SNEC AI Learning Platform")
    st.markdown("An AI-powered ophthalmology e-learning tool for medical students and junior doctors.")
    st.markdown("---")

    col1, col2 = st.columns([1, 1])
    with col1:
        st.subheader("Sign In / Register")
        name = st.text_input("Full name", placeholder="e.g. Tan Wei Ming")
        email = st.text_input("Email address", placeholder="e.g. student@nus.edu.sg")

        with st.expander("📋 Data Collection Notice (PDPA)"):
            st.markdown(PDPA_NOTICE)

        consent = st.checkbox("I have read and consent to the above data collection notice")

        if st.button("Enter Platform", type="primary", use_container_width=True):
            if not name.strip():
                st.error("Please enter your full name.")
            elif not email.strip() or "@" not in email:
                st.error("Please enter a valid email address.")
            elif not consent:
                st.error("You must consent to the data collection notice to use this platform.")
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

    with col2:
        st.markdown("### What you can do here")
        st.markdown("""
        | Feature | Description |
        |---|---|
        | 💬 Chatbot Tutor | Ask ophthalmology questions, get structured answers |
        | 🃏 Flash-cards | Spaced repetition review of key concepts |
        | 🏥 Case Simulator | Interactive clinical case with AI patient |
        | 🔬 Image Quiz | Describe retinal images and get scored |
        """)


# ---------------------------------------------------------------------------
# DASHBOARD PAGE
# ---------------------------------------------------------------------------
def page_dashboard() -> None:
    st.title(f"🏠 Dashboard")
    st.markdown(f"Welcome back, **{st.session_state.student_name}**.")

    # System health strip
    with st.expander("🔧 System Status", expanded=False):
        from tools.shared.health_monitor import (
            check_anthropic, check_google_sheets,
            check_google_drive, check_tmp_dir,
        )
        checks = [check_anthropic(), check_google_sheets(), check_google_drive(), check_tmp_dir()]
        cols = st.columns(len(checks))
        colors = {"PASS": "🟢", "WARN": "🟡", "FAIL": "🔴", "INFO": "🔵"}
        for col, (status, name, detail) in zip(cols, checks):
            with col:
                st.metric(label=name, value=f"{colors.get(status, '⚪')} {status}",
                          help=detail)

    st.markdown("---")

    # Study metrics
    get_rows, _, __ = _gsheets()
    sid = st.session_state.student_id

    try:
        sessions = get_rows("snec_sessions", {"student_id": sid})
        cards = get_rows("snec_flashcards", {"student_id": sid})
        cases = get_rows("snec_case_results", {"student_id": sid})
        images = get_rows("snec_image_results", {"student_id": sid})

        today = date.today().isoformat()
        due_cards = [c for c in cards if not c.get("next_due_date") or c["next_due_date"] <= today]

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Chatbot Sessions", len(sessions))
        c2.metric("Flash-cards", len(cards), delta=f"{len(due_cards)} due today" if due_cards else None)
        c3.metric("Cases Attempted", len(cases))
        c4.metric("Image Quizzes", len(images))

        # Weak topics
        if cards:
            st.markdown("### 📊 Flash-card Performance")
            from collections import defaultdict
            topic_ef: dict = defaultdict(list)
            for c in cards:
                try:
                    ef = float(c.get("easiness_factor", 2.5))
                except (ValueError, TypeError):
                    ef = 2.5
                topic_ef[c.get("topic_tag", "unknown")].append(ef)

            topic_avg = {t: sum(v) / len(v) for t, v in topic_ef.items()}
            sorted_topics = sorted(topic_avg.items(), key=lambda x: x[1])

            for topic, ef in sorted_topics:
                pct = min(100, int((ef - 1.3) / (3.0 - 1.3) * 100))
                color = "🔴" if pct < 30 else "🟡" if pct < 60 else "🟢"
                st.markdown(f"{color} **{topic}** — easiness {ef:.2f}")
                st.progress(pct / 100)

        if due_cards:
            st.info(f"📚 You have **{len(due_cards)} flash-card(s)** due for review today.")
            if st.button("Start Flash-card Review →", type="primary"):
                st.session_state.page = "Flashcards"
                st.rerun()

        if not sessions and not cards and not cases:
            st.markdown("### 👋 Getting Started")
            st.markdown("""
            1. Head to **💬 Chatbot Tutor** to ask your first ophthalmology question
            2. Flash-cards will be automatically generated at the end of each session
            3. Try a **🏥 Clinical Case** to test your diagnostic skills
            """)

    except Exception as e:
        st.error(f"Could not load study data: {e}")


# ---------------------------------------------------------------------------
# CHATBOT PAGE
# ---------------------------------------------------------------------------
def page_chatbot() -> None:
    st.title("💬 Chatbot Tutor")
    st.caption("Ask any ophthalmology question. Structured responses: Explanation → Mechanism → Clinical Pearl → Check Your Understanding")

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
                response = ask(
                    system_prompt=system_prompt,
                    messages=st.session_state.chat_messages,
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
    st.title("🃏 Flash-card Review")

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
    idx = st.session_state.review_index

    if not cards:
        st.success("✅ No cards due for review today. Come back tomorrow!")
        if st.button("Refresh"):
            st.session_state.review_cards = []
            st.rerun()
        return

    if idx >= len(cards):
        passed = st.session_state.get("review_passed", 0)
        st.balloons()
        st.success(f"🎉 Session complete! You reviewed **{len(cards)}** card(s).")
        st.metric("Score", f"{passed}/{len(cards)}", f"{int(passed/len(cards)*100)}%")
        if st.button("Start Over"):
            st.session_state.review_cards = []
            st.session_state.review_passed = 0
            st.rerun()
        return

    # Progress bar
    st.progress(idx / len(cards), text=f"Card {idx + 1} of {len(cards)}")

    card = cards[idx]
    topic = card.get("topic_tag", "")
    if topic:
        st.caption(f"Topic: **{topic}**")

    # Question
    st.markdown("### ❓ Question")
    st.info(card["front"])

    # Reveal / Answer
    if not st.session_state.card_revealed:
        if st.button("Reveal Answer 👁️", type="primary", use_container_width=True):
            st.session_state.card_revealed = True
            st.rerun()
    else:
        st.markdown("### ✅ Answer")
        st.success(card["back"])

        st.markdown("### How well did you recall this?")
        cols = st.columns(6)
        labels = ["0\nBlank", "1\nHint", "2\nSaw ans", "3\nHard", "4\nHesitate", "5\nPerfect"]

        for i, (col, label) in enumerate(zip(cols, labels)):
            with col:
                if st.button(label, key=f"q{i}", use_container_width=True):
                    # Update SM-2
                    try:
                        ef = float(card.get("easiness_factor") or 2.5)
                        iv = int(card.get("interval_days") or 0)
                        rp = int(card.get("repetition_count") or 0)
                    except (ValueError, TypeError):
                        ef, iv, rp = 2.5, 0, 0

                    new_iv, new_ef, new_rp = next_review(i, rp, ef, iv)
                    update_row("snec_flashcards", "card_id", card["card_id"], {
                        "easiness_factor": f"{new_ef:.2f}",
                        "interval_days": str(new_iv),
                        "repetition_count": str(new_rp),
                        "next_due_date": due_date(new_iv),
                        "last_reviewed": date.today().isoformat(),
                    })

                    if i >= 3:
                        st.session_state.review_passed = st.session_state.get("review_passed", 0) + 1

                    st.session_state.review_index += 1
                    st.session_state.card_revealed = False
                    st.rerun()


# ---------------------------------------------------------------------------
# CASE SIMULATOR PAGE
# ---------------------------------------------------------------------------
def page_cases() -> None:
    st.title("🏥 Clinical Case Simulator")

    ask, _, MOCK_MODE, MODEL = _claude()
    from tools.cases.load_case import list_available_cases, load_case
    from tools.cases.evaluate_response import evaluate_case
    from tools.cases.log_result import log_case_result
    from tools.flashcards.generate_cards import generate_cards

    if MOCK_MODE:
        st.warning("⚠️ Mock mode — patient responses are simulated.")

    sid = st.session_state.student_id

    # Case selection
    if st.session_state.current_case is None:
        available = list_available_cases()
        if not available:
            st.error("No cases available. Add JSON files to the `cases/` directory.")
            return

        st.subheader("Select a Case")
        case_options = {}
        for cid in available:
            try:
                c = load_case(cid)
                case_options[f"{c['title']} [{c['difficulty']}] — {c['topic']}"] = cid
            except Exception:
                case_options[cid] = cid

        chosen_label = st.selectbox("Available cases", list(case_options.keys()))
        if st.button("Start Case", type="primary"):
            case = load_case(case_options[chosen_label])
            st.session_state.current_case = case
            st.session_state.case_conversation = []
            st.session_state.case_result = None
            st.rerun()
        return

    case = st.session_state.current_case

    # Show case result if submitted
    if st.session_state.case_result:
        result = st.session_state.case_result
        st.subheader(f"📊 Results: {case['title']}")

        cols = st.columns(4)
        domains = [
            ("History", "history_score"),
            ("Investigations", "investigations_score"),
            ("Diagnosis", "diagnosis_score"),
            ("Management", "management_score"),
        ]
        for col, (label, key) in zip(cols, domains):
            col.metric(label, f"{result.get(key, 0)}/10")

        total = result.get("total_score", 0)
        colour = "🟢" if total >= 28 else "🟡" if total >= 20 else "🔴"
        st.metric("Total Score", f"{colour} {total}/40", f"{int(total/40*100)}%")

        st.markdown("### Feedback")
        for label, key in domains:
            fb = result.get(key.replace("_score", "_feedback"), "")
            if fb:
                st.markdown(f"**{label}:** {fb}")
        st.info(f"**Overall:** {result.get('overall_feedback', '')}")

        if st.button("Try Another Case"):
            st.session_state.current_case = None
            st.session_state.case_conversation = []
            st.session_state.case_result = None
            st.rerun()
        return

    # Case header in sidebar
    with st.sidebar:
        st.markdown("---")
        st.markdown(f"**Case:** {case['title']}")
        st.markdown(f"**Difficulty:** {case['difficulty']}")
        st.markdown(f"**Patient:** {case['patient']['name']}, {case['patient']['age']}y {case['patient']['gender']}")
        st.markdown(f"**Complaint:** {case['patient']['presenting_complaint']}")

    st.subheader(f"🏥 {case['title']}")
    st.caption("Interview the patient, request investigations, then submit your diagnosis and management plan.")

    # Patient system prompt
    import json as _json
    patient_prompt = f"""You are playing the role of a patient in a clinical simulation.
Answer ONLY what the student directly asks. Use lay language.
If asked for examination findings or investigations, provide them from the case.
Do NOT reveal the diagnosis.

Case: {_json.dumps(case, indent=2)}"""

    # Conversation display
    for msg in st.session_state.case_conversation:
        role = "user" if msg["role"] == "user" else "assistant"
        label = "You (Doctor)" if role == "user" else f"Patient ({case['patient']['name']})"
        with st.chat_message(role):
            st.markdown(f"**{label}:** {msg['content']}")

    # Submit button
    if st.session_state.case_conversation:
        if st.button("📋 Submit Case for Evaluation", type="primary"):
            with st.spinner("Evaluating your performance..."):
                try:
                    result = evaluate_case(case, st.session_state.case_conversation, sid)
                    log_case_result(sid, case, result)
                    generate_cards(sid, case["case_id"], st.session_state.case_conversation)
                    st.session_state.case_result = result
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
    st.title("🔬 Retinal Image Quiz")
    st.caption("Describe the retinal image systematically and receive scored feedback.")

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

    options = {f"{m.get('modality','').replace('_',' ').title()} — {img.name}": (img, m)
               for img, m in images_with_meta}
    chosen = st.selectbox("Select an image", list(options.keys()))
    img_path, img_meta = options[chosen]

    col1, col2 = st.columns([1, 1])

    with col1:
        st.image(str(img_path), caption=f"{img_meta.get('modality','').replace('_',' ').title()} | {img_meta.get('eye','').title()} eye | {img_meta.get('difficulty','').upper()}", use_container_width=True)

    with col2:
        st.markdown("### Describe this image systematically:")
        st.markdown("""
        - **Optic disc** — size, cup:disc ratio, rim, haemorrhages
        - **Macula** — foveal reflex, drusen, exudates, haemorrhage
        - **Blood vessels** — calibre, A:V ratio, crossings
        - **Periphery** — any lesions
        - **Diagnosis** — your differential
        """)

        description = st.text_area("Your description", height=200,
                                   placeholder="The optic disc shows...")

        if st.button("Submit Description", type="primary", use_container_width=True):
            if not description.strip():
                st.error("Please enter a description before submitting.")
            else:
                with st.spinner("Evaluating your description..."):
                    try:
                        result = evaluate_description(img_meta, description.strip(), img_path)
                        result["_raw_description"] = description.strip()
                        log_image_result(st.session_state.student_id, img_meta, result)

                        score = result.get("score", 0)
                        colour = "🟢" if score >= 7 else "🟡" if score >= 4 else "🔴"
                        st.metric("Score", f"{colour} {score}/10")

                        correct = result.get("correct_findings", [])
                        missed = result.get("missed_findings", [])
                        incorrect = result.get("incorrect_findings", [])

                        if correct:
                            st.success("**Correctly identified:**\n" + "\n".join(f"✓ {f}" for f in correct))
                        if missed:
                            st.warning("**Missed findings:**\n" + "\n".join(f"✗ {f}" for f in missed))
                        if incorrect:
                            st.error("**Over-called:**\n" + "\n".join(f"✗ {f}" for f in incorrect))

                        st.info(f"**Feedback:** {result.get('feedback', '')}")
                    except Exception as e:
                        st.error(f"Evaluation failed: {e}")


# ---------------------------------------------------------------------------
# ADMIN PAGE
# ---------------------------------------------------------------------------
def page_admin() -> None:
    st.title("⚙️ Admin")
    st.caption("System maintenance tools — for platform administrators.")

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
