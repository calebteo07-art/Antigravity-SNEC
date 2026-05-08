# EyeQ World-Class Improvement — Design Spec

**Date:** 2026-05-08
**Status:** Approved
**Audience:** SNEC students + supervisors (internal only)

---

## Problem

EyeQ's AI interactions feel transactional (Q&A with no real back-and-forth) and there is no accountability loop to keep students returning. The result: students use the app once or twice then drift away, and supervisors have no visibility into who is struggling.

## Goal

Make EyeQ feel like a senior registrar on call 24/7 — one that remembers what you struggled with last week, challenges you to reason rather than just recite, and keeps supervisors informed without extra work on their part.

Success looks like:
- Students open EyeQ daily because it responds to *them* specifically
- Supervisors can identify at-risk students without asking
- Every AI interaction pushes the student to reason, not just recall

---

## Approach: Persistent Student Brain

A `StudentProfile` record grows with every session. Every AI call reads the profile and adapts. Every session end writes back to it. The supervisor layer reads aggregated profiles to surface cohort health.

No existing features are rewritten — they gain a profile read/write wrapper and an updated system prompt injection.

---

## Section 1 — Architecture

### New backend modules

**`tools/profile/`**
- `get_profile.py` — reads student profile from `snec_profiles` Google Sheet
- `update_profile.py` — writes updated profile fields after each session
- `summarize_gaps.py` — produces a 3-line gap context string for AI injection

**`tools/supervisor/`**
- `cohort_summary.py` — aggregates all student profiles into cohort-level stats
- `at_risk.py` — flags students who haven't logged in for 5+ days and have 2+ unresolved weak topics
- `activity_report.py` — generates the weekly Monday report (Sheet + email)

### New data stores

**`snec_profiles` Google Sheet** — one row per student (see data model below)

**`snec_supervisors` Google Sheet** — supervisor accounts and email addresses

### Integration pattern

All existing features (chat, cases, image quiz, flashcards) follow this pattern:

1. Session start: call `get_profile(student_id)` → inject gap context into system prompt
2. Session end: call `update_profile(student_id, session_results)` → update weak topics, retention scores, streak, last_active

The gap context injected into every system prompt:

> *"Student profile: weak on [topics]. Consistently misses [findings] on cases. Retention score for [topic]: [score]. Redirect toward [weak topic] where possible."*

---

## Section 2 — Adaptive AI + Socratic Mode

### System prompt changes

`ophthalmology_kb.md` gains a Socratic instruction block:

- Never give the answer directly — ask one follow-up question that makes the student reason aloud first
- Steer toward weak topics when a natural bridge exists
- After confirming a correct answer, introduce a harder related question

### Gap context injection (`server.py`)

Before every `/api/chat` call, `summarize_gaps.py` is called to produce the context string. This is prepended to the KB system prompt. If profile read fails, the session proceeds with the base prompt only (no crash, no degraded UI).

### Post-case debrief

After `/api/cases/{id}/submit`, a second AI call generates a structured debrief:

```
What you got right: ...
What you missed: ...
Why it matters clinically: ...
Focus for next time: ...
```

This is returned as a new `debrief` field in `CaseSubmitResponse` and displayed on the `SummaryScreen`.

### API failure handling

If the Gemini API returns an error (any non-200 or exception):
- The frontend displays: *"AI tutor is temporarily unavailable — please try again in a few minutes."*
- The session is blocked — no mock responses shown to real users
- Mock mode remains available for local development only, gated by `MOCK_MODE=true` in `.env`
- The error is logged to `audit_log.jsonl` with `feature`, `error_code`, and `timestamp`

---

## Section 3 — Daily Check-In + Accountability Loop

### Student: Daily Check-In (`/checkin`)

Shown on first login of each day. Takes ~60 seconds.

**Flow:**
1. Display streak, XP, and today's recommended focus topic (top weak topic from profile)
2. Fire one warm-up question on that topic via `/api/checkin/question`
3. Student answers, AI gives instant feedback (no full 4-section response — just confirm/correct + one line why)
4. Mark `checkin_done_today = true` and update `streak` and `last_active` in profile

**New API endpoints:**
- `GET /api/checkin/question?student_id=` — returns one warm-up question targeting weak topic
- `POST /api/checkin/answer` — evaluates answer, returns feedback, updates profile

**`checkin_done_today` reset mechanism:** `get_profile()` compares `last_active` to today's date on every login. If they differ, it resets `checkin_done_today` to `false` before returning the profile. No cron job required.

**New frontend component:** `DailyCheckInScreen.tsx`

### Supervisor: Weekly Accountability Report

Runs every Monday. Triggered by a Windows Task Scheduler job (or cron on Linux) calling `python tools/supervisor/activity_report.py`. Can also be triggered manually for testing.

**Report contents:**
- Total active students this week
- Students not seen in 7+ days (list with names and last active date)
- Cohort-wide weakest topics (bottom 3 by average retention score)
- At-risk count (students meeting the at-risk threshold)

**Delivery:**
- Written to `snec_supervisor_alerts` Google Sheet (new tab per week)
- Emailed to every supervisor in `snec_supervisors` — mandatory, no opt-out

**At-risk flag:**
- Criteria: no login in 5+ days **AND** 2+ weak topics unresolved
- Visible immediately on supervisor dashboard (not just in weekly report)
- Email alert sent same-day when a student first crosses the threshold

**Email sender:** Gmail API via existing Google OAuth credentials in `credentials.json`

---

## Section 4 — Supervisor Dashboard

### New frontend route: `/supervisor`

Protected route — accessible only to accounts with `role: supervisor` (stored in `snec_supervisors`).

**Dashboard sections:**

**Cohort Overview**
- Topic heatmap: each ophthalmology topic, coloured by average retention score across all students
- Active this week vs. total enrolled
- At-risk count (click to expand list)

**At-Risk Students**
- Table: name, days since last session, weak topic count, last active date
- Click row → per-student drill-down

**Per-Student Drill-Down**
- Session history (date, feature used, topic, score if applicable)
- Flashcard retention trend (line chart, 30 days)
- Case scores (last 5 cases, domain breakdown)
- Current weak topics + missed findings

**New API endpoints:**
- `GET /api/supervisor/cohort` — cohort summary
- `GET /api/supervisor/at-risk` — at-risk student list
- `GET /api/supervisor/student/{student_id}` — full per-student data

**New frontend components:** `SupervisorDashboard.tsx`, `CohortHeatmap.tsx`, `AtRiskTable.tsx`, `StudentDrillDown.tsx`

---

## Data Model

### `snec_profiles` (Google Sheet, one row per student)

| Column | Type | Notes |
|---|---|---|
| `student_id` | string | FK to `snec_students` |
| `weak_topics` | JSON array | Topics with retention < 0.65 |
| `missed_findings` | JSON array | Clinical findings missed on cases/image quiz |
| `retention_scores` | JSON object | `{ "topic": float }` |
| `session_count` | int | Total sessions |
| `streak` | int | Consecutive days active |
| `last_active` | ISO date string | Updated on every login |
| `learning_velocity` | string | `improving` / `stable` / `declining` — calculated by `update_profile.py` by comparing average retention score across last 3 sessions vs. the 3 before that: >5% up = improving, >5% down = declining, otherwise stable |
| `checkin_done_today` | bool | Reset to false each day |

### `snec_supervisors` (Google Sheet, new)

| Column | Type | Notes |
|---|---|---|
| `supervisor_id` | string | Unique ID |
| `email` | string | Mandatory — used for all alerts |
| `cohort` | JSON array | List of student_ids this supervisor oversees |
| `role` | string | Always `supervisor` — used for route protection |

---

## Error Handling Summary

| Scenario | Behaviour |
|---|---|
| Profile read fails | Session proceeds with base prompt, no user-facing error |
| Profile write fails | Logged to `audit_log.jsonl`, retried next session |
| Gemini API error | Frontend shows error message, session blocked, logged |
| Email send fails | Logged to `audit_log.jsonl`, Sheet write still proceeds |
| Case debrief AI call fails | `debrief` field returns `null`, UI omits debrief section gracefully |

---

## Out of Scope

- Social features (leaderboards, peer challenges) — valid future addition, not in this spec
- Mobile app or PWA
- LMS / EMR integration
- Multi-institution support (SNEC-internal only)
