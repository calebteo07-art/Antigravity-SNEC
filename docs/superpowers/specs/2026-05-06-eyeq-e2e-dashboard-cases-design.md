# EyeQ — E2E Verification, Dashboard & Case Simulation Design

**Date:** 2026-05-06  
**Status:** Approved

---

## Overview

Three sequential milestones:
1. Verify the existing end-to-end flow works
2. Add a simple Home/Dashboard screen
3. Add Case Simulation to the frontend

---

## Milestone 1 — End-to-End Verification

### Goal
Confirm the existing flow (Onboarding → Chat → End Session → Flashcards → Summary) works correctly with both servers running.

### Steps
1. Start backend: `uvicorn tools.api.server:app --reload --port 8000`
2. Start frontend: `pnpm dev` inside `frontend/`
3. Walk through the full flow manually and verify each API call succeeds
4. Fix any broken calls, missing fields, or crashes

### API endpoints to verify
| Endpoint | Called by |
|---|---|
| `POST /api/onboard` | OnboardingScreen |
| `POST /api/chat` | ChatScreen |
| `POST /api/end-session` | ChatScreen (on exit) |
| `GET /api/status` | Optional health check |

### New endpoints to add (needed for Milestone 3)
| Endpoint | Purpose |
|---|---|
| `GET /api/cases` | Returns list of available cases from `.tmp/cases/` |
| `POST /api/cases/{case_id}/chat` | Returns virtual patient response for a given case |
| `POST /api/cases/{case_id}/submit` | Scores student's diagnosis + management plan |

---

## Milestone 2 — Dashboard Screen

### Goal
Give students a home screen to pick their learning mode after login.

### Route
`/dashboard` — Onboarding redirects here after successful login (instead of `/chat`)

### Layout
- Student name at the top: "Welcome back, [name]"
- Three large mode buttons:
  - **Chat Tutor** → `/chat`
  - **Case Simulation** → `/cases`
  - **Flashcards** → `/flashcards`
- Matches existing dark theme, fonts, and color tokens

### Files changed
- `frontend/app/routes.tsx` — add `/dashboard` route
- `frontend/app/components/DashboardScreen.tsx` — new component
- `frontend/app/components/OnboardingScreen.tsx` — redirect to `/dashboard` instead of `/chat`

---

## Milestone 3 — Case Simulation Frontend

### Goal
Bring the command-line case simulator into the web UI.

### Routes
- `/cases` — Case list screen
- `/cases/:caseId` — Case session screen

### Case List Screen
- Fetches cases from `GET /api/cases`
- Renders each case as a card showing: title, difficulty badge, topic
- Clicking a card navigates to `/cases/:caseId`

### Case Session Screen
Split layout:

**Left panel (read-only)**
- Patient name, age, chief complaint, vitals
- Always visible during the session

**Right main area**
- Chat window — student types questions, virtual patient responds via `POST /api/cases/{case_id}/chat`
- Input field + Send button at the bottom

**Submit flow**
- "Submit My Answer" button opens a form with two fields: Diagnosis, Management Plan
- On submit, calls `POST /api/cases/{case_id}/submit`
- Backend scores on 4 domains (History, Investigations, Diagnosis, Management), 10 pts each
- Results card shown inline: score per domain + feedback text

**After results**
- "Generate Flashcards" button seeds missed clinical points as flashcards (reuses existing `generate_and_return_cards` logic)

### Files added
- `frontend/app/components/CaseListScreen.tsx`
- `frontend/app/components/CaseSessionScreen.tsx`
- `frontend/app/routes.tsx` — add `/cases` and `/cases/:caseId`

### Backend files changed
- `tools/api/server.py` — add `/api/cases`, `/api/cases/{case_id}/chat`, `/api/cases/{case_id}/submit`
- `tools/cases/run_case.py` — expose patient response and evaluation logic as importable functions

---

## Data Flow Summary

```
Student logs in
  → POST /api/onboard
  → /dashboard

Student picks Chat
  → /chat → POST /api/chat (per message)
  → POST /api/end-session (on exit)
  → /flashcards → /summary

Student picks Cases
  → /cases → GET /api/cases
  → /cases/:id → POST /api/cases/:id/chat (per message)
  → Submit → POST /api/cases/:id/submit
  → Results + flashcard generation
```

---

## Out of Scope (this iteration)
- Image Quiz frontend
- Flashcard review loop (SM-2 scheduling)
- More than one case file
- Authentication / sessions beyond student_id
