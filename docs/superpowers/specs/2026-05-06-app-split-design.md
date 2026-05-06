# Design: Split app.py into Feature Modules

**Date:** 2026-05-06  
**Goal:** Reduce per-session token cost by breaking the 1161-line `app.py` monolith into focused page modules. Migrate routing from manual `session_state.page` to Streamlit's native `st.navigation()`.

---

## Motivation

`app.py` is 52 KB. Every session where Claude reads it pays the full cost. Splitting into 7 page files (~50–420 lines each) means a session working on the chatbot only ever needs to read `chatbot.py` (~70 lines) plus the thin `app.py` orchestrator (~50 lines).

---

## File Structure

```
app.py                    # ~50 lines: config, CSS, session init, auth gate, router
pages/
  __init__.py             # empty
  _shared.py              # _load_kb(), PDPA_NOTICE, _gsheets(), _identity(), _claude()
  login.py                # render()
  dashboard.py            # render()
  chatbot.py              # render()
  flashcards.py           # render()
  cases.py                # render(), _reset_case_state(), module-level constants
  image_quiz.py           # render()
  admin.py                # render()
```

---

## app.py (orchestrator)

Responsibilities:
1. `st.set_page_config()` — must remain the first Streamlit call
2. Import and inject `SNEC_CSS` via `st.markdown(..., unsafe_allow_html=True)`
3. Initialise session state from `DEFAULTS` dict
4. Render sidebar: wordmark, user chip, mock-mode badge, logout button
5. Auth gate + `st.navigation()` call (see below)

`DEFAULTS` dict stays in `app.py` so logout (which resets all keys) can reference it directly.

---

## Auth Gate

```python
if not st.session_state.student_id:
    pg = st.navigation([
        st.Page(login.render, title="Sign In", icon="👁️")
    ])
else:
    pg = st.navigation([
        st.Page(dashboard.render,    title="Dashboard",      icon="🏠", default=True),
        st.Page(chatbot.render,      title="Chatbot Tutor",  icon="💬"),
        st.Page(flashcards.render,   title="Flash-cards",    icon="🃏"),
        st.Page(cases.render,        title="Case Simulator", icon="🏥"),
        st.Page(image_quiz.render,   title="Image Quiz",     icon="🔬"),
        st.Page(admin.render,        title="Admin",          icon="⚙️"),
    ])
pg.run()
```

When not logged in, Streamlit renders only the login page — no nav sidebar entries for locked pages.

---

## pages/_shared.py

Exports used by multiple page modules:

| Symbol | Used by |
|--------|---------|
| `_load_kb()` | `chatbot.py`, `cases.py` |
| `PDPA_NOTICE` | `login.py` |
| `_gsheets()` | `dashboard.py`, `flashcards.py`, `admin.py` |
| `_identity()` | `login.py` |
| `_claude()` | `chatbot.py`, `cases.py`, `image_quiz.py` |

`_load_kb()` keeps `@st.cache_resource` — this is the only reason it exists as a wrapper rather than a direct import.

---

## Page Modules

Each module exports exactly one public symbol: `render()`. Internal helpers (e.g. `_reset_case_state()`, `_level_banner()`, module-level constants `_TOPIC_EMOJI`, `_DIFF_STARS`, `_MAX_HINTS`) remain private to their module.

Logic inside each `render()` is **unchanged** from `app.py` — this is a pure relocation, not a rewrite.

### Sidebar during active case (cases.py)

`page_cases()` currently writes case-specific info into `st.sidebar` during the active case view. This still works — page modules can write to `st.sidebar` alongside the content `app.py` writes there. Streamlit merges all sidebar calls in render order.

---

## Session State

`DEFAULTS` and all `st.session_state` keys are unchanged. Pages access `st.session_state` directly as before. No props are passed between `app.py` and page modules.

---

## What Does Not Change

- All business logic inside page functions — pure file relocation
- `tools/` directory — completely unaffected
- `st.session_state` keys and values
- CSS / design system (`tools/shared/styles.py`)
- Streamlit `run` command: still `streamlit run app.py`

---

## Out of Scope

- Refactoring logic inside any page function
- Removing unused shadcn components (separate task)
- Splitting `tools/shared/styles.py`
