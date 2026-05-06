import streamlit as st
from pages._shared import PDPA_NOTICE, _identity
from tools.shared.styles import section_label


def render() -> None:
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

        name  = st.text_input("Full name",     placeholder="e.g. Tan Wei Ming")
        email = st.text_input("Email address", placeholder="e.g. student@nus.edu.sg")

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
                        st.session_state.student_id   = sid
                        st.session_state.student_name = name.strip()
                        st.rerun()
                    except Exception as e:
                        st.error(f"Login failed: {e}")

        st.markdown("</div>", unsafe_allow_html=True)


render()
