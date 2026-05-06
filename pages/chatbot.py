import streamlit as st
from pages._shared import _load_kb, _claude
from tools.shared.styles import ph


def render() -> None:
    st.markdown(ph("Chatbot Tutor",
        "Ask any ophthalmology question — every answer follows: "
        "Explanation → Mechanism → Clinical Pearl → Check Your Understanding."),
        unsafe_allow_html=True)

    ask, _, MOCK_MODE, MODEL = _claude()
    if MOCK_MODE:
        st.warning("⚠️ Mock mode — responses are simulated. Add API key to `.env` for real AI.")

    for msg in st.session_state.chat_messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if st.session_state.chat_messages:
        col1, col2 = st.columns([4, 1])
        with col2:
            if st.button("End Session 💾", type="secondary"):
                with st.spinner("Saving session and generating flash-cards..."):
                    try:
                        from tools.chatbot.log_session import log_session
                        from tools.flashcards.generate_cards import generate_cards

                        sid      = st.session_state.student_id
                        messages = st.session_state.chat_messages
                        topic    = next((m["content"][:80] for m in messages if m["role"] == "user"), "")

                        session_id = log_session(
                            student_id=sid,
                            topic=topic,
                            messages=messages,
                            token_count=0,
                            model="mock" if MOCK_MODE else MODEL,
                        )
                        system_prompt = _load_kb()
                        card_count    = generate_cards(sid, session_id, messages, system_prompt)

                        st.session_state.chat_messages = []
                        st.success(f"Session saved! {card_count} flash-card(s) generated.")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Failed to save session: {e}")

    if prompt := st.chat_input("Ask an ophthalmology question..."):
        st.session_state.chat_messages.append({"role": "user", "content": prompt})

        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                system_prompt   = _load_kb()
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


render()
