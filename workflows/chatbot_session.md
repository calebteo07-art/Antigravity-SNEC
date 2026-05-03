# Chatbot Tutor Session — SOP

## Objective

Run an interactive ophthalmology Q&A session for a student. Handle onboarding
for new students, conduct the tutoring conversation, log the session, and
automatically generate flash-cards at the end.

## How to Run

```
python tools/chatbot/run_session.py
```

## What Happens

1. **Onboarding** (`tools/chatbot/onboarding.py`)
   - New students: enter name + email, read PDPA notice, give consent
   - Returning students: identity confirmed silently, skip to session

2. **Tutoring session** (`tools/chatbot/run_session.py`)
   - Student types ophthalmology questions in plain language
   - Tutor responds with: Explanation → Mechanism → Clinical Pearl → Check Your Understanding
   - Session continues until student types `exit`

3. **Session logging** (`tools/chatbot/log_session.py`)
   - Session summary written to `snec_sessions` Google Sheet
   - Includes: session_id, student_id, timestamp, topic, summary, token count, model

4. **Flash-card generation** (`tools/flashcards/generate_cards.py`)
   - Claude extracts 3-5 high-yield Q&A pairs from the session transcript
   - Cards written to `snec_flashcards` sheet with SM-2 default values
   - Cards become due for review on the student's next login

## API Key Note

> Without `ANTHROPIC_API_KEY` set in `.env`, the session runs in **MOCK MODE**.
> The tutor returns realistic canned ophthalmology responses so the full flow
> can be tested. Add the API key to `.env` to enable real AI responses.

## Topics Covered

The knowledge base (`workflows/ophthalmology_kb.md`) covers:
- Glaucoma (POAG, AACG, NTG, secondary)
- Retinal diseases (DR, AMD, RD, vascular occlusions)
- Corneal diseases (keratoconus, Fuchs, keratitis, dry eye)
- Cataract and complications
- Common ophthalmic medications
- Clinical examination techniques

## Troubleshooting

**Session ends without saving**
The student typed `exit` before asking any questions. Sessions with no messages
are not saved — this is correct behaviour.

**Flash-card generation returns 0 cards**
Claude's response could not be parsed as JSON. Check `.tmp/audit_log.jsonl`
for a `cards_parse_failed` event with the session_id. This is rare in live mode
but can happen with very short sessions (< 1 exchange).

**Onboarding loops on consent**
Only `yes` or `no` are accepted. Any other input repeats the prompt.
