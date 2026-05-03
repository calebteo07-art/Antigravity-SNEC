# Clinical Case Simulation — SOP

## Objective

Run an interactive clinical case simulation where the student interviews a
virtual patient, requests investigations, states a diagnosis, and proposes
a management plan. Claude evaluates performance against a structured rubric.

## How to Run

```
python tools/cases/run_case.py
```

To load a specific case directly:
```
python tools/cases/run_case.py --case case_001_poag
```

## What Happens

1. **Onboarding** — same as chatbot session (skipped for returning students)
2. **Case selection** — student picks from available cases in `.tmp/cases/`
3. **Simulation** — student interviews the virtual patient by typing questions.
   The AI responds as the patient using only the case information provided.
4. **Submission** — student types `exit` or `submit` when ready
5. **Evaluation** (Agent 14) — Claude scores on 4 domains, 10 points each:
   - History taking
   - Investigations requested
   - Diagnosis
   - Management plan
6. **Results displayed** — scores and domain-specific feedback shown immediately
7. **Logging** — result written to `snec_case_results` Google Sheet
8. **Flash-cards** — missed clinical points seeded as flash-cards automatically

## Adding New Cases

Place case JSON files in `.tmp/cases/` using the schema from `case_001_poag.json`
as a template. Required fields: case_id, title, difficulty, topic, patient,
history, examination_findings, investigations, diagnosis, management, rubric.

Cases can also be uploaded to the `snec_cases/` Google Drive folder.
Agent 16 (Case Author) automates case creation.

## API Key Note

> Without `ANTHROPIC_API_KEY`, the patient gives canned responses and the
> evaluation returns placeholder scores. Add the API key for a realistic
> interactive experience.

## Scoring Guide

| Score | Meaning |
|---|---|
| 36-40 | Excellent — ready for clinical practice |
| 28-35 | Good — minor gaps to address |
| 20-27 | Satisfactory — review flagged topics |
| < 20 | Needs improvement — repeat case after studying |
