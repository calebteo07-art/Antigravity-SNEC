import json

import streamlit as st
from pages._shared import _claude, PROJECT_ROOT
from tools.shared.styles import ph, section_label


def render() -> None:
    st.markdown(ph("Image Quiz",
        "Describe the retinal image systematically — you'll be scored on what you identify, "
        "miss, and over-call."),
        unsafe_allow_html=True)

    _, __, MOCK_MODE, ___ = _claude()
    if MOCK_MODE:
        st.warning("⚠️ Mock mode — evaluation uses simulated scoring.")

    from tools.image_quiz.evaluate_description import evaluate_description
    from tools.image_quiz.log_result import log_image_result

    images_dir   = PROJECT_ROOT / "images"
    image_files  = list(images_dir.glob("*.png")) + list(images_dir.glob("*.jpg"))
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
        f"{m.get('modality', '').replace('_', ' ').title()} — {img.stem}": (img, m)
        for img, m in images_with_meta
    }
    chosen             = st.selectbox("Select an image", list(options.keys()))
    img_path, img_meta = options[chosen]

    col_img, col_form = st.columns([1, 1], gap="large")

    with col_img:
        modality   = img_meta.get("modality", "").replace("_", " ").title()
        eye        = img_meta.get("eye", "").title()
        difficulty = img_meta.get("difficulty", "").upper()
        caption    = "  ·  ".join(filter(None, [modality, f"{eye} eye" if eye else "", difficulty]))
        st.image(str(img_path), caption=caption, use_container_width=True)

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
        description = st.text_area(
            "", height=220,
            placeholder="The optic disc shows a cup-to-disc ratio of approximately..."
        )

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
                            f'  <div style="font-family:var(--serif);font-size:2.5rem;'
                            f'    color:{sc};line-height:1">'
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


render()
