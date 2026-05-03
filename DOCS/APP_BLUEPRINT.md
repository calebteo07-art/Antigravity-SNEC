# SNEC AI Medical E-Learning Platform — Product Architecture Blueprint

**Version:** 1.0
**Date:** 2026-05-03
**Organisation:** Singapore National Eye Centre (SNEC)
**Framework:** WAT (Workflows · Agents · Tools)
**AI Backbone:** Anthropic Claude API — `claude-sonnet-4-6`
**Status:** Design-ready for implementation

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Overall System Architecture](#2-overall-system-architecture)
3. [Feature 1 — AI Chatbot Tutor / Clarifier (Core)](#3-feature-1--ai-chatbot-tutor--clarifier-core)
4. [Feature 2 — Spaced Repetition Flash-Card Engine](#4-feature-2--spaced-repetition-flash-card-engine)
5. [Feature 3 — Clinical Case Simulator](#5-feature-3--clinical-case-simulator)
6. [Feature 4 — Retinal Image Annotation & Quiz](#6-feature-4--retinal-image-annotation--quiz)
7. [Data Privacy & Ethics](#7-data-privacy--ethics)
8. [Tech Stack Summary](#8-tech-stack-summary)
9. [Directory Layout](#9-directory-layout)
10. [Dependency Map & Build Sequence](#10-dependency-map--build-sequence)

---

## 1. Executive Summary

This document specifies the complete product architecture for an AI-powered medical e-learning platform built for SNEC. The target users are medical students and junior doctors learning ophthalmology. The platform is built as a WAT (Workflows, Agents, Tools) system: markdown SOPs in `workflows/` define intent, Python scripts in `tools/` perform deterministic execution, and the Anthropic Claude API acts as the orchestrating intelligence.

**The four features and their rationale:**

| # | Feature | Rationale |
|---|---------|-----------|
| 1 | AI Chatbot Tutor / Clarifier | Core Q&A engine; handles conceptual queries, drug dosing, and disease pathophysiology at any hour |
| 2 | Spaced Repetition Flash-Card Engine | Encodes knowledge into long-term memory — the evidence-backed gap between Q&A understanding and exam recall |
| 3 | Clinical Case Simulator | Bridges theoretical knowledge to clinical reasoning under realistic time pressure |
| 4 | Retinal Image Annotation & Quiz | Ophthalmology is an image-heavy discipline; students must learn to read fundus photos and OCT scans |

All four features share a single student identity layer and persist data to Google Sheets (structured records) and Google Drive (files). The Chatbot Tutor is the semantic hub: it feeds content into the Flash-Card engine, provides explanations during Case Simulation, and evaluates student descriptions in the Image Quiz.

---

## 2. Overall System Architecture

### 2.1 High-Level Data Flow

```
Student (CLI / Streamlit Web UI)
        │
        ▼
┌───────────────────────────────────────────────────────┐
│                    AGENT LAYER                        │
│  Claude claude-sonnet-4-6 (orchestrator)              │
│  Reads workflow SOPs → decides which tools to call    │
└──────┬──────────┬──────────┬──────────┬───────────────┘
       │          │          │          │
       ▼          ▼          ▼          ▼
  tools/       tools/     tools/     tools/
  chatbot/   flashcards/  cases/   image_quiz/
       │          │          │          │
       └──────────┴──────────┴──────────┘
                       │
                       ▼
              ┌────────────────┐
              │  Shared Layer  │
              │  identity.py   │
              │  audit_log.py  │
              │  gdrive.py     │
              │  gsheets.py    │
              └────────┬───────┘
                       │
         ┌─────────────┼──────────────┐
         ▼             ▼              ▼
   Google Sheets   Google Drive    .tmp/
   (progress,      (images,        (local
    session logs,   case files,     processing
    SRS state)      exports)        buffers)
```

### 2.2 Shared Services

All four features depend on five shared service modules:

| Module | File | Responsibility |
|--------|------|----------------|
| Identity | `tools/shared/identity.py` | Student ID, cohort assignment, consent status |
| Audit Logger | `tools/shared/audit_log.py` | Append-only JSONL event log, written to `.tmp/` and synced to Drive |
| Google Sheets Client | `tools/shared/gsheets.py` | CRUD wrapper using `gspread` |
| Google Drive Client | `tools/shared/gdrive.py` | Upload/download wrapper using `google-api-python-client` |
| Claude Client | `tools/shared/claude_client.py` | Anthropic SDK wrapper with prompt caching and retry logic |

### 2.3 WAT Integration Pattern

Every feature follows the same WAT pattern:

```
workflows/<feature_name>.md      ← SOP: objective, inputs, steps, edge cases
tools/<feature_name>/<script>.py ← Deterministic execution script
Agent (Claude)                    ← Reads workflow, calls correct tool, handles errors
```

The agent never executes business logic itself. It reads the SOP, determines what tool to call, calls it, checks the output, and either proceeds or invokes the error-handling path described in the SOP.

---

## 3. Feature 1 — AI Chatbot Tutor / Clarifier (Core)

### 3.1 Feature Rationale

Medical students encounter dense, unfamiliar content at all hours. A Chatbot Tutor that can explain glaucoma pathophysiology, compare beta-blockers vs. prostaglandin analogues, or walk through the differential for a red eye provides on-demand scaffolding that no textbook or human tutor can match for availability and patience. It is the platform's semantic core: all other features call back to it for explanations.

### 3.2 User Experience

**Scenario — Junior doctor at 11 pm:**

1. Student opens the CLI or Streamlit web interface.
2. Types: `"Why does acute angle-closure glaucoma cause a mid-dilated pupil?"`
3. The Chatbot responds with a structured explanation: mechanism, anatomical context, clinical pearl, and one follow-up question to deepen understanding.
4. Student asks a follow-up. The Chatbot maintains full conversation context within the session.
5. At session end, a session summary card (key concepts covered, recommended flash-cards) is written to Google Sheets.

**Response format contract (every response):**

```
## Explanation
[Core answer in plain language]

## Mechanism / Detail
[Pathophysiology or pharmacological detail]

## Clinical Pearl
[What an experienced clinician would add]

## Check Your Understanding
[One Socratic follow-up question]
```

### 3.3 Technical Stack

| Component | Choice | Reason |
|-----------|--------|--------|
| AI model | `claude-sonnet-4-6` | Best-in-class reasoning at affordable cost; 200k context for long sessions |
| Prompt caching | `anthropic` SDK `cache_control` on system prompt | System prompt is large (ophthalmology KB); caching reduces cost ~80% |
| Session memory | In-process `list[dict]` for `messages` param | Stateless per session; no external DB needed for MVP |
| Persistent history | `gspread` → Google Sheets | Session summaries written as rows; free, auditable |
| Web UI (Phase 2) | `streamlit` | Minimal Python-native UI; no frontend build step |
| CLI (Phase 1) | `typer` | Clean CLI with type hints |
| Content KB | `workflows/ophthalmology_kb.md` | Embedded in system prompt via prompt cache |

**Claude API call pattern (`tools/chatbot/run_session.py`):**

```python
SYSTEM_PROMPT = open("workflows/ophthalmology_kb.md").read()

response = client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=1024,
    system=[
        {
            "type": "text",
            "text": SYSTEM_PROMPT,
            "cache_control": {"type": "ephemeral"}   # prompt cache
        }
    ],
    messages=conversation_history
)
```

**Dependencies:**

```
anthropic>=0.40.0
typer>=0.12.0
streamlit>=1.35.0       # Phase 2 only
gspread>=6.0.0
google-auth-oauthlib>=1.2.0
python-dotenv>=1.0.0
```

### 3.4 Workflow SOP — `workflows/chatbot_session.md`

- **Objective:** Deliver accurate ophthalmology Q&A with Socratic follow-up.
- **Inputs:** `student_id`, `session_topic` (optional), `question`.
- **Steps:** Load KB → construct messages → call Claude → validate response format → log to Sheets → return to student.
- **Edge cases:** Model refuses (safety filter) → log refusal, rephrase prompt with clinical context flag. Response exceeds token budget → split into two turns. Google Sheets write fails → buffer to `.tmp/session_buffer.jsonl` and retry on next session start.
- **Output:** Formatted response string + session summary row written to `snec_sessions` Google Sheet.

### 3.5 Implementation Roadmap

**Phase 1 — MVP (Weeks 1–4)**

- [ ] `tools/shared/claude_client.py` — Anthropic SDK wrapper with retry, prompt caching, token logging
- [ ] `tools/shared/gsheets.py` — `gspread` CRUD: append row, read range
- [ ] `tools/shared/identity.py` — student ID, consent check (file-backed for MVP)
- [ ] `tools/shared/audit_log.py` — JSONL append writer
- [ ] `workflows/ophthalmology_kb.md` — curated SNEC ophthalmology knowledge base (1000–3000 tokens)
- [ ] `workflows/chatbot_session.md` — SOP
- [ ] `tools/chatbot/run_session.py` — CLI session runner (`typer`)
- [ ] `tools/chatbot/log_session.py` — write session summary to Google Sheets
- [ ] Manual test: 20 sample questions across glaucoma, retina, cornea, neuro-ophthalmology

**Phase 2 — Enhancement (Weeks 5–8)**

- [ ] `tools/chatbot/web_ui.py` — `streamlit` interface replacing CLI
- [ ] Multi-turn session persistence: write full conversation to Drive as JSON
- [ ] Topic tagging: Claude classifies each Q&A pair into a taxonomy node (used by Flash-Card engine)
- [ ] Confidence indicator: Claude appends `[CONFIDENCE: high/medium/low]` token; UI renders accordingly
- [ ] Rate-limit guardrail: cap 30 questions/student/day in Google Sheets

**Phase 3 — Scale / Advanced (Weeks 9–16)**

- [ ] Retrieval-Augmented Generation (RAG): chunk SNEC clinical guidelines using `langchain-text-splitters`, embed with `voyage-3`, store in `chromadb`; retrieve top-3 chunks per query
- [ ] Voice input: `openai-whisper` transcription → text → Chatbot pipeline
- [ ] Multilingual: Claude's native Chinese/Malay capability; language selector in UI
- [ ] Analytics dashboard: Streamlit page showing cohort-level topic heatmap from Sheets data

---

## 4. Feature 2 — Spaced Repetition Flash-Card Engine

### 4.1 Feature Rationale

Q&A understanding does not translate to exam recall without repeated retrieval practice. Spaced repetition (SRS) is the most evidence-backed method for long-term retention of medical facts. By generating flash-cards automatically from Chatbot sessions, this feature closes the encoding gap: what the student learns in conversation, they will remember for clinical exams. It also creates a virtuous loop — students who practise cards return to the Chatbot with better questions.

### 4.2 User Experience

1. After any Chatbot session, the system automatically generates 3–5 flash-cards from the conversation (drug names, anatomical facts, diagnostic criteria).
2. Students open the `/review` command each morning. The SM-2 algorithm presents only the cards due today.
3. Each card shows the question side. Student self-rates recall: `1 (forgot)` · `2 (hard)` · `3 (ok)` · `4 (easy)`.
4. Cards answered `1` are re-shown within the same session. Cards answered `4` recur in 10+ days.
5. Progress (streak, cards mastered, weak topics) is visible in Google Sheets or the Streamlit dashboard.
6. At any point, student can type `explain` after a card to invoke the Chatbot Tutor inline.

### 4.3 Technical Stack

| Component | Choice | Reason |
|-----------|--------|--------|
| SRS algorithm | SM-2 (pure Python implementation) | Battle-tested, royalty-free, implementable in ~60 lines |
| Card store | Google Sheets (`snec_flashcards` sheet) | One row per card: `student_id, card_id, front, back, topic_tag, easiness, interval, repetitions, next_due` |
| Card generation | `claude-sonnet-4-6` via `tools/shared/claude_client.py` | Extracts cloze-style Q&A pairs from session transcript |
| CLI interface | `typer` + `rich` | Rich provides coloured card rendering in terminal |
| Scheduling state | Google Sheets (row updates) | No additional DB; SM-2 state lives in the sheet |

**SM-2 state columns in Google Sheets:**

```
card_id | student_id | front | back | topic_tag | easiness_factor | interval_days | repetition_count | next_due_date | last_reviewed | created_from_session_id
```

**Card generation prompt pattern (`tools/flashcards/generate_cards.py`):**

```python
CARD_GEN_PROMPT = """
You are a medical flash-card author for ophthalmology students.
Given the following Q&A conversation transcript, generate between 3 and 5
flash-cards in JSON format. Each card must have:
  "front": a concise question (max 20 words)
  "back": a concise answer (max 40 words)
  "topic_tag": one of [glaucoma, retina, cornea, lens, neuro-ophthalmology,
               pharmacology, anatomy, examination-technique, other]

Return ONLY a JSON array. No prose before or after.
"""
```

**Dependencies:**

```
anthropic>=0.40.0
gspread>=6.0.0
typer>=0.12.0
rich>=13.0.0
python-dotenv>=1.0.0
```

### 4.4 Workflow SOP — `workflows/flashcard_review.md`

- **Objective:** Surface due flash-cards, collect ratings, update SM-2 state, trigger Chatbot on `explain`.
- **Inputs:** `student_id`, `review_date`.
- **Steps:** Pull due cards from Sheets → present each card → collect rating → run SM-2 update → write updated row → if `explain` invoked, call `tools/chatbot/run_session.py` with card's `front` as seed question.
- **Edge cases:** Sheets write fails → buffer to `.tmp/srs_buffer.jsonl`. No due cards → display streak count and earliest next-due date. Student rates all cards `1` → trigger notification to cohort supervisor (Phase 2).

### 4.5 Implementation Roadmap

**Phase 1 — MVP (Weeks 3–5)**

- [ ] `tools/flashcards/sm2.py` — Pure Python SM-2: `calculate_next_interval(easiness, interval, repetitions, quality) -> (new_easiness, new_interval, new_repetitions)`
- [ ] `tools/flashcards/generate_cards.py` — Calls Claude, parses JSON array, appends rows to `snec_flashcards` sheet
- [ ] `tools/flashcards/review_session.py` — Fetches due cards, runs review loop, writes updated state
- [ ] `workflows/flashcard_review.md` — SOP
- [ ] Integration hook in `tools/chatbot/run_session.py`: after session ends, call `generate_cards.py` with session transcript
- [ ] Test: generate cards from 5 sample transcripts; verify SM-2 interval calculations against reference implementation

**Phase 2 — Enhancement (Weeks 6–9)**

- [ ] Streamlit review UI with card-flip animation (`st.session_state` state machine)
- [ ] Weak-topic report: weekly email digest listing topics with mean quality < 2.5
- [ ] Duplicate detection: embed card front with `voyage-3`; cosine-compare against existing cards; skip if similarity > 0.92
- [ ] Manual card creation: student can author custom cards from the UI

**Phase 3 — Scale / Advanced (Weeks 10–16)**

- [ ] Adaptive difficulty: Claude generates a harder variant card when student rates original `4` three times in a row
- [ ] Cohort leaderboard (opt-in): anonymised streak ranking for friendly competition
- [ ] Export to Anki `.apkg` format using `genanki` library

---

## 5. Feature 3 — Clinical Case Simulator

### 5.1 Feature Rationale

Medical education research consistently shows that passive information acquisition must be complemented by active clinical reasoning practice. Case simulation forces students to integrate knowledge under realistic time pressure, make differential diagnosis decisions, and justify management plans — the exact cognitive demands of clinical exams and real consultations. This feature transforms the Chatbot from an answer machine into a clinical tutor who challenges and evaluates.

### 5.2 User Experience

1. Student launches `/case` and selects a difficulty level: `junior | registrar | fellow`.
2. The system presents a realistic patient vignette: `"65M, DM, presents with 3-week gradual blurring of vision OD. VA 6/18. IOP 24 mmHg OU. Fundus: cup-disc ratio 0.8 OD..."`
3. Student works through four structured steps:
   - **History:** Student requests additional history; system provides it on request.
   - **Investigations:** Student orders investigations; system reveals results sequentially.
   - **Diagnosis:** Student states primary diagnosis and differentials.
   - **Management:** Student proposes management plan.
4. After each student input, Claude evaluates the response and provides scored feedback: `[Correct / Partially correct / Incorrect] + Explanation`.
5. At case end, Claude generates a detailed debrief: what was done well, what was missed, learning points, relevant SNEC guidelines referenced.
6. Case score and learning points are written to Google Sheets. Missed diagnoses seed new Flash-Cards automatically.

### 5.3 Technical Stack

| Component | Choice | Reason |
|-----------|--------|--------|
| Case engine | `claude-sonnet-4-6` with structured system prompt | Claude plays dual role: case presenter and evaluator |
| Case library | Google Drive folder `snec_cases/` (JSON files per case) | Cases are structured data; Drive provides easy curation by SNEC faculty |
| Case format | JSON schema (see below) | Deterministic case loading; separates content from engine |
| State machine | `tools/cases/case_state.py` — Python dataclass | Tracks phase (history/investigations/diagnosis/management) |
| Scoring | `claude-sonnet-4-6` with rubric in system prompt | Rubric-based evaluation; consistent across students |
| Output | Google Sheets `snec_case_results` + Drive debrief PDF | Results queryable in Sheets; PDF debrief per student |

**Case JSON schema (`snec_cases/<case_id>.json`):**

```json
{
  "case_id": "glaucoma_001",
  "title": "Normal Tension Glaucoma in Diabetic Patient",
  "difficulty": "registrar",
  "topic_tags": ["glaucoma", "diabetic-retinopathy"],
  "presentation": "65-year-old male with...",
  "available_history": {
    "family_history": "Father had glaucoma",
    "medications": "Metformin, Amlodipine",
    "review_of_systems": "No headaches, no halos"
  },
  "investigations": {
    "visual_fields": "Arcuate scotoma OD on Humphrey 24-2",
    "OCT_RNFL": "Inferior RNFL thinning OD",
    "gonioscopy": "Open angles OU, no PAS"
  },
  "correct_diagnosis": "Normal tension glaucoma OD",
  "acceptable_differentials": ["Low tension glaucoma", "NTG"],
  "management_key_points": [
    "Nocturnal hypotension workup",
    "Target IOP 30% reduction from baseline",
    "Prostaglandin analogue first-line"
  ],
  "learning_points": [
    "NTG diagnosis requires IOP consistently ≤21 on diurnal curve",
    "Vascular dysregulation plays a role — consider BP monitoring"
  ],
  "snec_guideline_reference": "SNEC Glaucoma Management Protocol v3.2"
}
```

**Dependencies:**

```
anthropic>=0.40.0
gspread>=6.0.0
google-api-python-client>=2.120.0
google-auth-oauthlib>=1.2.0
typer>=0.12.0
rich>=13.0.0
pydantic>=2.6.0
reportlab>=4.0.0        # Phase 2: PDF debrief generation
python-dotenv>=1.0.0
```

### 5.4 Workflow SOP — `workflows/case_simulation.md`

- **Objective:** Run an interactive clinical case, evaluate student at each phase, produce scored debrief.
- **Inputs:** `student_id`, `case_id` (or `difficulty` for random selection), `session_mode` (exam | learning).
- **Steps:** Load case JSON from Drive → initialise state machine → run phase loop → call Claude evaluator after each student input → generate debrief → write score row to Sheets → trigger Flash-Card generation from missed diagnoses.
- **Edge cases:** Case JSON malformed → log error, offer next available case. Claude evaluation is ambiguous → flag for faculty review in a `flagged_responses` sheet. Student abandons mid-case → save partial state to `.tmp/<student_id>_case_progress.json` and offer resume on next launch.

### 5.5 Implementation Roadmap

**Phase 1 — MVP (Weeks 4–7)**

- [ ] `tools/cases/load_case.py` — Downloads case JSON from Drive, validates against schema using `pydantic`
- [ ] `tools/cases/case_state.py` — Dataclass: `phase`, `student_responses`, `scores`, `elapsed_time`
- [ ] `tools/cases/run_case.py` — Main loop: present → collect input → evaluate → advance phase
- [ ] `tools/cases/evaluate_response.py` — Calls Claude with rubric, returns `{verdict, score, explanation}`
- [ ] `tools/cases/generate_debrief.py` — Calls Claude to synthesise full debrief from state
- [ ] `tools/cases/log_result.py` — Writes to `snec_case_results` Google Sheet
- [ ] Seed case library: 5 cases (2 glaucoma, 1 retina, 1 cornea, 1 neuro-ophthalmology) in Drive
- [ ] `workflows/case_simulation.md` — SOP

**Phase 2 — Enhancement (Weeks 8–11)**

- [ ] PDF debrief generation via `reportlab`: cover page, phase-by-phase scorecard, learning points, guideline references
- [ ] Timed exam mode: countdown timer enforced per phase; time-pressure metric recorded in Sheets
- [ ] Faculty case authoring tool: `tools/cases/author_case.py` — guided CLI that helps faculty create validated JSON cases
- [ ] Case recommendation engine: after each case, Claude recommends next case based on weak topics (reads Flash-Card SRS state from Sheets)

**Phase 3 — Scale / Advanced (Weeks 12–16)**

- [ ] Branching cases: case JSON supports `branches` — management decisions lead to different patient trajectories
- [ ] Cohort analytics: aggregate score distributions per topic exportable to Google Slides via Slides API
- [ ] Standardised patient voice: TTS narration of case presentation using `google-cloud-texttospeech`

---

## 6. Feature 4 — Retinal Image Annotation & Quiz

### 6.1 Feature Rationale

Ophthalmology is uniquely image-dependent. A student who can articulate glaucoma pathophysiology but cannot recognise a cup-disc ratio of 0.9 on a fundus photo is clinically underprepared. No other specialty demands this level of visual pattern recognition so early in training. This feature embeds de-identified retinal images (fundus photos, OCT scans, slit-lamp photos) directly into the learning workflow, using Claude's native vision capability to evaluate student descriptions and generate annotated feedback.

### 6.2 User Experience

1. Student launches `/image-quiz` and selects a modality: `fundus | OCT | slit-lamp | visual-field`.
2. A de-identified image is displayed (Streamlit: `st.image`; CLI: filepath reference).
3. Student is asked: `"Describe what you see in this image. What is the likely diagnosis?"`
4. Student types their description. Claude evaluates it against the ground-truth annotation and highlights what was correct and what was missed (e.g., `"You identified the cup-disc ratio correctly but missed the superior RNFL haemorrhage at 11 o'clock"`).
5. Claude reveals the annotated image (arrows/labels rendered by `Pillow`) and explains all findings.
6. Student rates their confidence. Score and topic tag are written to Sheets. Missed findings seed Flash-Cards.

### 6.3 Technical Stack

| Component | Choice | Reason |
|-----------|--------|--------|
| Vision model | `claude-sonnet-4-6` (natively multimodal) | No separate vision API needed; same model for text and image reasoning |
| Image store | Google Drive folder `snec_images/` | De-identified images stored with metadata JSON sidecar |
| Image encoding | Base64 encoding → Claude `image` content block | Standard Anthropic API image input pattern |
| Image annotation rendering | `Pillow` (PIL) | Draw bounding boxes and labels onto image copies in `.tmp/` |
| Image metadata | JSON sidecar per image | Links image to ground truth; never contains PII |
| Streamlit display | `st.image` with caption | Native image rendering in web UI |

**Claude vision call pattern (`tools/image_quiz/evaluate_description.py`):**

```python
import base64

def evaluate_description(image_path: str, student_description: str, ground_truth: dict) -> dict:
    with open(image_path, "rb") as f:
        image_b64 = base64.standard_b64encode(f.read()).decode("utf-8")

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        system=EVALUATOR_SYSTEM_PROMPT,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": "image/jpeg",
                            "data": image_b64
                        }
                    },
                    {
                        "type": "text",
                        "text": f"Ground truth findings: {ground_truth}\n\nStudent description: {student_description}\n\nEvaluate the student's description."
                    }
                ]
            }
        ]
    )
    return parse_evaluation(response.content[0].text)
```

**Image metadata sidecar schema (`snec_images/<image_id>_meta.json`):**

```json
{
  "image_id": "fundus_glaucoma_042",
  "modality": "fundus",
  "diagnosis_tags": ["glaucoma", "NTG"],
  "findings": [
    "Cup-disc ratio 0.85 OD",
    "Superior RNFL haemorrhage at 11 o'clock",
    "Inferior neuroretinal rim thinning"
  ],
  "difficulty": "registrar",
  "de_identification_method": "SNEC IRB Protocol 2024-031: metadata stripped, date shifted, MRN removed",
  "source": "SNEC anonymised teaching library",
  "consent_reference": "SNEC patient consent form v2.1 — educational use"
}
```

**Dependencies:**

```
anthropic>=0.40.0
Pillow>=10.0.0
gspread>=6.0.0
google-api-python-client>=2.120.0
google-auth-oauthlib>=1.2.0
typer>=0.12.0
streamlit>=1.35.0
python-dotenv>=1.0.0
```

### 6.4 Workflow SOP — `workflows/image_quiz.md`

- **Objective:** Present retinal image, collect student description, evaluate against ground truth, display annotated feedback.
- **Inputs:** `student_id`, `modality` (optional), `difficulty` (optional).
- **Steps:** Pull eligible image from Drive → encode to base64 → display to student → collect description → call Claude vision evaluator → render annotated image to `.tmp/` → display annotated feedback → log score to Sheets → trigger Flash-Card generation for missed findings.
- **Edge cases:** Image too large for Claude API (>5 MB) → use Pillow to resize to max 1920px wide before encoding. Claude cannot confidently evaluate → flag for faculty review. Drive API quota exceeded → fall back to locally cached images in `.tmp/image_cache/`.

### 6.5 Implementation Roadmap

**Phase 1 — MVP (Weeks 5–8)**

- [ ] `tools/image_quiz/fetch_image.py` — Downloads image and sidecar JSON from Drive to `.tmp/`
- [ ] `tools/image_quiz/encode_image.py` — Resizes if needed (Pillow), base64-encodes
- [ ] `tools/image_quiz/evaluate_description.py` — Calls Claude vision API, returns structured evaluation
- [ ] `tools/image_quiz/annotate_image.py` — Uses Pillow to draw findings labels onto image copy
- [ ] `tools/image_quiz/log_result.py` — Writes score + findings coverage to `snec_image_results` sheet
- [ ] Seed image library: 10 de-identified images (4 fundus, 3 OCT, 2 slit-lamp, 1 visual field) with metadata JSON
- [ ] `workflows/image_quiz.md` — SOP
- [ ] Test: verify base64 round-trip, Claude response parsing, Pillow annotation rendering

**Phase 2 — Enhancement (Weeks 9–12)**

- [ ] Streamlit UI: `st.image` side-by-side (original | annotated) revealed after student submission
- [ ] Region-of-interest click quiz: student clicks on the abnormality before typing — coordinates logged for heat-map analytics
- [ ] Image difficulty calibration: after 50+ attempts, auto-recalibrate difficulty tag based on mean score
- [ ] Image deduplication: check `.tmp/image_served_log.jsonl` to avoid serving same image within 7 days

**Phase 3 — Scale / Advanced (Weeks 13–16)**

- [ ] OCT layer segmentation overlay: `torch` + lightweight pre-trained model for automated RNFL segmentation; Claude explains automated findings
- [ ] Image-linked case simulator: investigations phase in Feature 3 can surface actual images from this library
- [ ] Faculty upload portal: Streamlit admin page for guided de-identified image upload with consent checkbox

---

## 7. Data Privacy & Ethics

### 7.1 Regulatory Framework

| Regulation | Applicability | Key Obligations |
|------------|---------------|-----------------|
| Singapore PDPA (2012, amended 2020) | Primary — all student and patient data | Consent before collection; purpose limitation; data breach notification within 3 days |
| Singapore Health Records | Patient images from SNEC clinical systems | Health records are sensitive personal data under PDPA; require explicit consent for educational use |
| HIPAA (US) | Not primary jurisdiction; align where practical | Business associate agreements for US-hosted cloud services; minimum necessary access |
| MOH Singapore Guidelines on AI in Healthcare | Advisory | Human oversight for any AI-generated clinical content |

### 7.2 Data Classification

| Data Type | Classification | Storage | Retention |
|-----------|---------------|---------|-----------|
| Student identity (name, email, NUSNET ID) | Personal — Sensitive | Google Sheets (access-controlled) | Programme duration + 1 year |
| Student Q&A transcripts | Personal — Educational | Google Drive (per-student folder, private) | 2 years |
| Flash-card SRS state | Personal — Educational | Google Sheets | 2 years |
| Case simulation results | Personal — Educational | Google Sheets + Drive | 2 years |
| Clinical images (fundus, OCT) | Patient — Sensitive (de-identified) | Google Drive `snec_images/` | Indefinite (teaching library) |
| Audit logs | System | `.tmp/audit_log.jsonl` synced to Drive | 7 years (MOH retention) |
| API keys | Secret | `.env` (gitignored) | Rotate every 90 days |

### 7.3 De-identification Protocol for Clinical Images

All clinical images must pass through `tools/privacy/deidentify_image.py` before entering Google Drive. This tool:

1. Strips all DICOM metadata using `pydicom` — removes patient name, MRN, date of birth, accession number, study date.
2. Pixel-level scrubbing: uses Pillow to black-out any burned-in text regions via a configurable bounding-box mask.
3. Date shifting: study date replaced with a shifted date (offset stored only in SNEC's IRB records, never in the platform).
4. Assigns a new `image_id` UUID with no link to the original clinical ID.
5. Records the de-identification action in `tools/shared/audit_log.py` with: `{timestamp, original_modality, snec_irb_ref, operator_id, deidentification_method}`.
6. Requires a `consent_reference` field (pointing to the signed SNEC patient consent form) before the image can be committed to the Drive library.

**Required libraries:**

```
pydicom>=2.4.0
Pillow>=10.0.0
```

### 7.4 Student Consent Flow

At first login, `tools/shared/identity.py` checks for a consent record in the `snec_consent` Google Sheet. If absent:

1. Student is presented with the PDPA consent notice (plain language, <300 words).
2. Consent is logged as a timestamped row: `{student_id, consent_version, timestamp, ip_hash}`. IP is SHA-256 hashed before storage — the raw IP is never stored.
3. Students may withdraw consent at any time via `tools/privacy/withdraw_consent.py`. Withdrawal triggers: (a) deletion of all session transcripts, (b) pseudonymisation of Q&A logs (`student_id` replaced with `REDACTED_<hash>`), (c) retention of aggregate analytics only.
4. Consent version is pinned to the consent form version. If the form is updated, students are re-prompted on next login.

### 7.5 Audit Logging

Every tool call that touches personal data emits an audit event via `tools/shared/audit_log.py`:

```python
audit_log.write({
    "timestamp": datetime.utcnow().isoformat(),
    "event_type": "chatbot_session_start | flashcard_generated | case_result_written | image_served",
    "student_id_hash": sha256(student_id + SALT).hexdigest(),  # pseudonymised
    "tool": "tools/chatbot/run_session.py",
    "data_accessed": ["snec_sessions", "anthropic_api"],
    "outcome": "success | failure"
})
```

Audit logs are:
- Written locally to `.tmp/audit_log.jsonl` (append-only)
- Synced to a restricted Google Drive folder `snec_audit/` after each session
- Never contain raw student IDs, names, or clinical content — only pseudonymised hashes
- Retained for 7 years per MOH record-keeping guidelines

### 7.6 Claude API Data Handling

- Anthropic's Claude API does not use submitted data to train models when accessed via API (Anthropic usage policy as of 2025 — verify this policy remains current before each data ingestion phase).
- No student PII or de-identified clinical images should be submitted to the Claude API without confirming this policy is current.
- System prompts must explicitly instruct Claude: `"You are operating in a medical educational context. Do not store, repeat, or reproduce any patient identifiers or personally identifying information that appears in your context."`
- All Claude API calls are logged (token counts, model version, timestamp) to `snec_api_usage` Google Sheet for cost tracking and anomaly detection.

### 7.7 Access Controls

| Role | Access Scope |
|------|-------------|
| Student | Own session data, own flash-cards, own case results, image quiz scores |
| Faculty | Cohort-level aggregate analytics (anonymised); case library authoring; image library upload |
| SNEC IT Admin | All audit logs; de-identification operator; API key rotation |
| Claude Code Agent | Programmatic access scoped by OAuth to specific Sheets/Drive folders only |

Google Drive and Sheets sharing is managed at the folder level. OAuth tokens (`token.json`) are generated with minimum required scopes:

```python
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",   # Sheets read/write
    "https://www.googleapis.com/auth/drive.file",     # Only files created by this app
    # NOT drive (full Drive access) — never request broad scope
]
```

---

## 8. Tech Stack Summary

### 8.1 Consolidated Dependency List

```
# Core AI
anthropic>=0.40.0                   # Claude API SDK — all features

# Google Integration
gspread>=6.0.0                      # Google Sheets CRUD
google-api-python-client>=2.120.0   # Drive, Slides APIs
google-auth-oauthlib>=1.2.0         # OAuth 2.0 flow
google-auth-httplib2>=0.2.0         # HTTP transport

# CLI & UI
typer>=0.12.0                       # CLI interface
rich>=13.0.0                        # Terminal formatting / card rendering
streamlit>=1.35.0                   # Web UI (Phase 2+)

# Image Processing
Pillow>=10.0.0                      # Annotation rendering, resizing, de-identification
pydicom>=2.4.0                      # DICOM metadata stripping

# Case Validation
pydantic>=2.6.0                     # Case JSON schema validation

# PDF Generation
reportlab>=4.0.0                    # Case debrief PDFs (Phase 2)

# Environment
python-dotenv>=1.0.0                # .env loading

# Phase 3 optional
chromadb>=0.5.0                     # Local vector store for RAG
langchain-text-splitters>=0.2.0     # Chunk SNEC guidelines for RAG
genanki>=0.13.0                     # Anki export for flash-cards
# torch / nnU-Net                   # OCT segmentation (Phase 3 — evaluate separately)
```

### 8.2 Model Selection Rationale

| Task | Model | Reason |
|------|-------|--------|
| Chatbot Q&A (all turns) | `claude-sonnet-4-6` | Best reasoning/cost ratio; 200k context; natively multimodal |
| Flash-card generation | `claude-sonnet-4-6` | Structured JSON output; ophthalmology knowledge depth |
| Case evaluation / debrief | `claude-sonnet-4-6` | Rubric-adherence and detailed explanation generation |
| Image description evaluation | `claude-sonnet-4-6` | Native vision — no separate model or API |
| Embeddings for RAG (Phase 3) | `voyage-3` via Anthropic | Best-in-class retrieval embeddings; same vendor |

**No GPT-4 or other provider models are used.** Claude is the single AI dependency, simplifying API key management and ensuring consistent behaviour.

### 8.3 Storage Matrix

| Data | Storage | Format | Access Pattern |
|------|---------|--------|---------------|
| Session transcripts | Google Drive (per-student) | JSON | Write-once; read for card generation |
| Flash-card SRS state | Google Sheets `snec_flashcards` | Rows | Read-heavy (daily); update after each rating |
| Case library | Google Drive `snec_cases/` | JSON | Read-only by app; faculty write via authoring tool |
| Case results | Google Sheets `snec_case_results` | Rows | Write per session; read for analytics |
| Clinical images | Google Drive `snec_images/` | JPEG/PNG + JSON sidecar | Read by app; faculty write via upload tool |
| Image quiz results | Google Sheets `snec_image_results` | Rows | Write per quiz; read for analytics |
| Audit logs | `.tmp/` → Drive `snec_audit/` | JSONL | Append-only; admin read |
| API usage | Google Sheets `snec_api_usage` | Rows | Write per call; admin read |
| Consent records | Google Sheets `snec_consent` | Rows | Write at first login; read at every session start |

---

## 9. Directory Layout

```
SNEC_AI_CHATBOT/
│
├── CLAUDE.md                           # WAT framework agent instructions
├── .env.example                        # Template — copy to .env
├── .env                                # Secrets — gitignored
├── credentials.json                    # Google OAuth client — gitignored
├── token.json                          # Google OAuth token — gitignored
├── requirements.txt                    # All Python dependencies
│
├── DOCS/
│   └── APP_BLUEPRINT.md                # This document
│
├── workflows/
│   ├── ophthalmology_kb.md             # SNEC ophthalmology knowledge base (system prompt)
│   ├── chatbot_session.md              # SOP: Chatbot Tutor
│   ├── flashcard_review.md             # SOP: Spaced Repetition review
│   ├── case_simulation.md              # SOP: Clinical Case Simulator
│   └── image_quiz.md                   # SOP: Retinal Image Quiz
│
├── tools/
│   │
│   ├── shared/
│   │   ├── claude_client.py            # Anthropic SDK wrapper (caching, retry, logging)
│   │   ├── gsheets.py                  # gspread CRUD wrapper
│   │   ├── gdrive.py                   # Drive upload/download wrapper
│   │   ├── identity.py                 # Student ID, consent check
│   │   └── audit_log.py               # Append-only JSONL audit writer
│   │
│   ├── chatbot/
│   │   ├── run_session.py              # Main CLI session runner
│   │   ├── log_session.py              # Write session summary to Sheets
│   │   └── web_ui.py                   # Streamlit UI (Phase 2)
│   │
│   ├── flashcards/
│   │   ├── sm2.py                      # SM-2 algorithm (pure Python)
│   │   ├── generate_cards.py           # Claude → JSON cards → Sheets
│   │   └── review_session.py           # Due-card fetch, review loop, state update
│   │
│   ├── cases/
│   │   ├── load_case.py                # Drive download + pydantic validation
│   │   ├── case_state.py               # Dataclass: phase, responses, scores
│   │   ├── run_case.py                 # Main case loop
│   │   ├── evaluate_response.py        # Claude rubric evaluator
│   │   ├── generate_debrief.py         # Claude debrief synthesiser
│   │   ├── log_result.py               # Write result to Sheets + Drive PDF
│   │   └── author_case.py              # Faculty case authoring CLI (Phase 2)
│   │
│   ├── image_quiz/
│   │   ├── fetch_image.py              # Drive → .tmp/ download
│   │   ├── encode_image.py             # Pillow resize + base64 encode
│   │   ├── evaluate_description.py     # Claude vision evaluator
│   │   ├── annotate_image.py           # Pillow annotation renderer
│   │   └── log_result.py               # Write score to Sheets
│   │
│   └── privacy/
│       ├── deidentify_image.py         # DICOM strip + pixel scrub + audit
│       └── withdraw_consent.py         # PDPA withdrawal handler
│
└── .tmp/                               # Gitignored processing directory
    ├── .gitkeep
    ├── audit_log.jsonl                 # Local audit buffer
    ├── srs_buffer.jsonl                # Flash-card write buffer (Sheets failure fallback)
    ├── session_buffer.jsonl            # Session write buffer
    └── image_cache/                    # Locally cached images (Drive fallback)
```

---

## 10. Dependency Map & Build Sequence

### 10.1 Build Order

```
Layer 0 — Shared Infrastructure (build first — everything depends on this)
  tools/shared/audit_log.py
  tools/shared/claude_client.py
  tools/shared/gsheets.py
  tools/shared/gdrive.py
  tools/shared/identity.py

Layer 1 — Feature 1 Core (Chatbot — other features call this)
  workflows/ophthalmology_kb.md
  workflows/chatbot_session.md
  tools/chatbot/run_session.py
  tools/chatbot/log_session.py

Layer 2 — Feature 2 (Flash-Cards — requires Layer 1 for card generation trigger)
  tools/flashcards/sm2.py
  tools/flashcards/generate_cards.py
  tools/flashcards/review_session.py
  workflows/flashcard_review.md

Layer 3 — Feature 3 (Cases — requires Layer 1 for evaluation; Layer 2 for missed-diagnosis cards)
  tools/cases/load_case.py
  tools/cases/case_state.py
  tools/cases/evaluate_response.py
  tools/cases/run_case.py
  tools/cases/generate_debrief.py
  tools/cases/log_result.py
  workflows/case_simulation.md

Layer 4 — Feature 4 (Images — requires Layer 1 for evaluation; Layer 2 for missed-finding cards)
  tools/image_quiz/fetch_image.py
  tools/image_quiz/encode_image.py
  tools/image_quiz/evaluate_description.py
  tools/image_quiz/annotate_image.py
  tools/image_quiz/log_result.py
  workflows/image_quiz.md

Layer 5 — Privacy Tools (build in parallel with Layer 1; must be complete before any real data ingestion)
  tools/privacy/deidentify_image.py
  tools/privacy/withdraw_consent.py
```

### 10.2 Cross-Feature Data Flows

```
Chatbot Session ends
    │
    ├── → generate_cards.py (Flash-Card Engine) — cards seeded from session topics
    └── → log_session.py → snec_sessions Sheets row

Flash-Card review — student rates card as "forgot" (quality 1)
    └── → chatbot run_session triggered with card front as seed question

Case Simulation — student misses a diagnosis
    ├── → generate_cards.py — missed diagnosis becomes flash-card
    └── → log_result.py → snec_case_results Sheets row + Drive PDF

Image Quiz — student misses a finding
    ├── → generate_cards.py — missed finding becomes flash-card
    └── → log_result.py → snec_image_results Sheets row
```

### 10.3 Master Phased Roadmap

| Week | Milestone |
|------|-----------|
| 1–2 | Layer 0: shared infrastructure, Google OAuth, audit logging |
| 3–4 | Feature 1 MVP: Chatbot CLI, ophthalmology KB, session logging |
| 4–5 | Feature 2 MVP: SM-2, card generation, review CLI |
| 5–7 | Feature 3 MVP: case library (5 cases), case runner, evaluator |
| 6–8 | Feature 4 MVP: image library (10 images), vision quiz, annotation |
| 7–8 | Privacy tools: de-identification pipeline, consent flow |
| 9–11 | Phase 2 enhancements across all features (Streamlit UI, PDF debriefs) |
| 12–16 | Phase 3 advanced features (RAG, branching cases, OCT segmentation) |

---

*Document version 1.0 — generated 2026-05-03.*
*Owner: SNEC AI Education Team.*
*Review cycle: quarterly or on major feature completion.*
