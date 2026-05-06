import streamlit as st
from tools.shared.styles import ph


def render() -> None:
    st.markdown(ph("Admin", "System maintenance tools — for platform administrators."),
                unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        with st.expander("💰 Cost Monitor", expanded=True):
            st.number_input("Alert threshold (USD/month)", value=20.0, step=5.0)
            if st.button("Run Cost Report"):
                with st.spinner("Loading usage data..."):
                    try:
                        from tools.shared.gsheets import get_rows
                        rows = get_rows("snec_api_usage")
                        if not rows:
                            st.info("No API usage recorded yet.")
                        else:
                            total_cost  = sum(float(r.get("estimated_cost_usd", 0) or 0) for r in rows)
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
                        from tools.shared.schema_migration import EXPECTED_SCHEMA
                        from tools.shared.gsheets import _get_spreadsheet
                        ss      = _get_spreadsheet()
                        results = []
                        for sheet_name, expected in EXPECTED_SCHEMA.items():
                            try:
                                ws      = ss.worksheet(sheet_name)
                                current = ws.row_values(1)
                                missing = [c for c in expected if c not in current]
                                results.append((sheet_name,
                                                "✅ OK" if not missing else f"⚠️ Missing: {missing}"))
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


render()
