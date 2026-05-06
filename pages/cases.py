import json

import streamlit as st
from pages._shared import _claude
from tools.shared.styles import (
    ph, section_label, domain_card, named_progress, xp_toast,
)

_TOPIC_EMOJI = {
    "glaucoma": "👁️", "retina": "🔬", "cornea": "🌊",
    "neuro-ophthalmology": "🧠", "lens": "💎", "cataract": "💎",
}
_DIFF_STARS = {
    "beginner": "⭐", "intermediate": "⭐⭐", "advanced": "⭐⭐⭐", "expert": "⭐⭐⭐⭐",
}
_MAX_HINTS = 3


def _reset_case_state() -> None:
    st.session_state.current_case       = None
    st.session_state.case_conversation  = []
    st.session_state.case_result        = None
    st.session_state.case_xp_result     = None
    st.session_state.case_hints_used    = 0
    st.session_state.case_hint_messages = []


def _level_banner(sid: str, get_progress, get_level_info) -> None:
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


def render() -> None:
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

    # ── VIEW 1: CASE SELECTION ────────────────────────────────────────────────
    if st.session_state.current_case is None and st.session_state.case_result is None:
        st.markdown(ph("Case Simulator",
            "Interview the AI patient · Request investigations · Diagnose · Manage."),
            unsafe_allow_html=True)

        if _prog_ok:
            _level_banner(sid, get_progress, get_level_info)

        if MOCK_MODE:
            st.warning("⚠️ Mock mode — patient responses and evaluation are simulated.")

        available = list_available_cases()
        if not available:
            st.error("No cases available. Add JSON files to the `cases/` directory.")
            return

        st.markdown(section_label("Available Cases"), unsafe_allow_html=True)

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

    # ── VIEW 2: RESULTS ───────────────────────────────────────────────────────
    if st.session_state.case_result is not None:
        case   = st.session_state.current_case
        result = st.session_state.case_result
        total  = int(result.get("total_score", 0))
        pct    = int(total / 40 * 100)

        if _prog_ok and st.session_state.case_xp_result is None:
            try:
                msg_count  = sum(1 for m in st.session_state.case_conversation
                                 if m["role"] == "user")
                prog       = get_progress(sid)
                is_first   = prog["cases_completed"] == 0
                hints_used = st.session_state.get("case_hints_used", 0)
                xp_reward  = calculate_xp_reward(
                    result=result,
                    message_count=msg_count,
                    is_first_case=is_first,
                    hints_used=hints_used,
                    cases_completed=prog["cases_completed"],
                )
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

        grade = "🥇" if pct >= 90 else "🥈" if pct >= 75 else "🥉" if pct >= 60 else "📋"
        st.markdown(ph(f"{grade} {case['title']}",
            f"Case complete · {total}/40 points · {pct}%"), unsafe_allow_html=True)

        if xp.get("total_xp", 0) > 0:
            xp_col, lv_col = st.columns([1, 2], gap="large")
            with xp_col:
                st.markdown(xp_toast(xp["total_xp"]), unsafe_allow_html=True)
            with lv_col:
                if _prog_ok:
                    _level_banner(sid, get_progress, get_level_info)
                with st.expander("⚡ XP Breakdown"):
                    rows_html = (
                        f'<div style="font-size:.82rem;color:var(--txt-2)">'
                        f'Base: <b style="color:var(--txt)">{xp.get("base_xp", 0)} XP</b>'
                        f' (score × 10)</div>'
                    )
                    for bname, bval in xp.get("bonuses", []):
                        rows_html += (
                            f'<div style="font-size:.8rem;color:#6EE7B7">'
                            f'+ {bval} XP &nbsp;<span style="color:var(--txt-3)">{bname}</span></div>'
                        )
                    for pname, pval in xp.get("penalties", []):
                        rows_html += (
                            f'<div style="font-size:.8rem;color:#FCA5A5">'
                            f'{pval} XP &nbsp;<span style="color:var(--txt-3)">{pname}</span></div>'
                        )
                    rows_html += (
                        f'<div style="font-size:.86rem;font-weight:700;color:var(--accent);'
                        f'margin-top:.4rem;border-top:1px solid var(--border);padding-top:.4rem">'
                        f'Total: {xp.get("total_xp", 0):,} XP</div>'
                    )
                    st.markdown(rows_html, unsafe_allow_html=True)

        st.markdown(section_label("Performance Breakdown"), unsafe_allow_html=True)

        domains = [
            ("History",        "📝", "history_score",       "history_feedback"),
            ("Investigations", "🔬", "investigations_score", "investigations_feedback"),
            ("Diagnosis",      "🎯", "diagnosis_score",      "diagnosis_feedback"),
            ("Management",     "💊", "management_score",     "management_feedback"),
        ]
        dcols = st.columns(4)
        for col, (lbl, icon, sk, _) in zip(dcols, domains):
            with col:
                st.markdown(domain_card(lbl, icon, int(result.get(sk, 0))),
                            unsafe_allow_html=True)

        st.markdown(
            f'<div style="margin-top:.75rem">'
            f'{named_progress(f"Total  {total}/40", f"{pct}%", total / 40)}'
            f'</div>',
            unsafe_allow_html=True,
        )

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
                        f'  <div style="font-size:.62rem;color:var(--txt-3);line-height:1.35">'
                        f'    {bdesc}</div>'
                        f'</div>',
                        unsafe_allow_html=True,
                    )

        st.markdown("<div style='height:.75rem'></div>", unsafe_allow_html=True)
        a1, a2 = st.columns(2)
        with a1:
            if st.button("↩ Try Another Case", type="primary", use_container_width=True):
                _reset_case_state()
                st.rerun()
        with a2:
            if st.button("🏠 Dashboard", use_container_width=True):
                _reset_case_state()
                st.switch_page("pages/dashboard.py")
        return

    # ── VIEW 3: ACTIVE CASE ───────────────────────────────────────────────────
    case = st.session_state.current_case

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

    diff_label = _DIFF_STARS.get(case.get("difficulty", ""), "⭐⭐")
    st.markdown(ph(case["title"],
        f"{diff_label} {case.get('difficulty', '').capitalize()}  ·  "
        f"Interview the patient, request investigations, then submit."),
        unsafe_allow_html=True)
    if MOCK_MODE:
        st.warning("⚠️ Mock mode — patient responses are simulated.")

    for hint in st.session_state.get("case_hint_messages", []):
        st.markdown(
            f'<div class="snec-hint">💡 <strong>Hint:</strong> {hint}</div>',
            unsafe_allow_html=True,
        )

    patient_prompt = (
        "You are playing the role of a patient in a clinical simulation.\n"
        "Answer ONLY what the student directly asks. Use lay language.\n"
        "If asked for examination findings or investigations, provide them from the case.\n"
        "Do NOT reveal the diagnosis.\n\n"
        f"Case: {json.dumps(case, separators=(',', ':'))}"
    )

    for msg in st.session_state.case_conversation:
        role  = "user" if msg["role"] == "user" else "assistant"
        label = "You (Doctor)" if role == "user" else f"Patient ({case['patient']['name']})"
        with st.chat_message(role):
            st.markdown(f"**{label}:** {msg['content']}")

    if st.session_state.case_conversation:
        if st.button("📋 Submit for Evaluation", type="primary"):
            with st.spinner("Evaluating your performance..."):
                try:
                    result = evaluate_case(case, st.session_state.case_conversation, sid)
                    log_case_result(sid, case, result)
                    generate_cards(sid, case["case_id"], st.session_state.case_conversation)
                    st.session_state.case_result    = result
                    st.session_state.case_xp_result = None
                    st.rerun()
                except Exception as e:
                    st.error(f"Evaluation failed: {e}")

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


render()
