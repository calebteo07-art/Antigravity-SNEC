#!/usr/bin/env python3
"""Agent 11: Flash-card Generator — extracts Q&A pairs from a session and saves them to Sheets.

Called automatically at the end of each chatbot session.
Uses Claude (or mock) to extract 3-5 cloze-style Q&A pairs from the conversation.

Usage (from run_session.py):
    from tools.flashcards.generate_cards import generate_cards
    card_count = generate_cards(student_id, session_id, messages, system_prompt)

Self-test:
    python tools/flashcards/generate_cards.py
"""

import json
import sys
import uuid
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from tools.shared.claude_client import ask, MODEL_SMALL
from tools.shared.database import SessionLocal
from tools.shared.models import Flashcard
from tools.shared.audit_log import log as audit_log
from tools.flashcards.sm2 import due_date

CARD_PROMPT = """You are extracting flash-cards from an ophthalmology tutoring session.

Review the conversation below and extract 3 to 5 high-yield Q&A pairs.

Rules:
- Each card must test ONE specific clinical fact
- Questions should be concise and specific (not "tell me about X")
- Answers should be 1-3 sentences maximum
- Tag each card with the most relevant topic (e.g. glaucoma, retina, cornea, cataract, medications)
- Do NOT include cards about the learning process itself — only clinical content

Return ONLY a JSON array, no other text:
[
  {"front": "question", "back": "answer", "topic_tag": "topic"},
  ...
]"""


def _build_transcript(messages: list[dict]) -> str:
    """Convert message list to a readable transcript string."""
    lines = []
    for m in messages:
        role = "Student" if m["role"] == "user" else "Tutor"
        lines.append(f"{role}: {m['content']}")
    return "\n\n".join(lines)


def _parse_cards(response: str) -> list[dict]:
    """Parse JSON card array from Claude's response. Returns empty list on failure."""
    text = response.strip()

    # Strip markdown code fences if present
    if text.startswith("```"):
        lines = text.splitlines()
        text = "\n".join(lines[1:-1] if lines[-1].strip() == "```" else lines[1:])

    try:
        cards = json.loads(text)
        if isinstance(cards, list):
            return [
                c for c in cards
                if isinstance(c, dict)
                and c.get("front") and c.get("back") and c.get("topic_tag")
            ]
    except json.JSONDecodeError:
        pass
    return []


def generate_cards(
    student_id: str,
    session_id: str,
    messages: list[dict],
    system_prompt: str = "",
) -> int:
    """Generate flash-cards and save to Sheets. Returns count saved."""
    return len(generate_and_return_cards(student_id, session_id, messages))


def generate_and_return_cards(
    student_id: str,
    session_id: str,
    messages: list[dict],
) -> list[dict]:
    """
    Generate flash-cards from a completed session, save to snec_flashcards, and return them.

    Args:
        student_id:  Student UUID.
        session_id:  Session UUID.
        messages:    Full conversation history from the session.

    Returns:
        List of saved card dicts with keys: card_id, front, back, topic_tag.
    """
    transcript = _build_transcript(messages[-20:])

    response = ask(
        system_prompt=CARD_PROMPT,
        messages=[{"role": "user", "content": f"Session transcript:\n\n{transcript}"}],
        max_tokens=512,
        feature="flashcard",
        model=MODEL_SMALL,
    )

    cards = _parse_cards(response)
    if not cards:
        audit_log("cards_parse_failed", student_id=student_id, feature="flashcards",
                  detail=f"session_id={session_id} response_len={len(response)}")
        return []

    saved = []
    with SessionLocal() as db:
        for card in cards:
            card_id = str(uuid.uuid4())
            new_card = Flashcard(
                card_id=card_id,
                student_id=student_id,
                session_id=session_id,
                front=card["front"],
                back=card["back"],
                topic_tag=card["topic_tag"],
                easiness_factor=2.5,
                interval=0,
                repetition=0
            )
            db.add(new_card)
            saved.append({"card_id": card_id, "front": card["front"], "back": card["back"], "topic_tag": card["topic_tag"]})
        db.commit()

    audit_log("cards_generated", student_id=student_id, feature="flashcards",
              detail=f"session_id={session_id} count={len(saved)}")
    return saved


if __name__ == "__main__":
    print("Testing generate_cards.py...\n")

    TEST_STUDENT = "generate-cards-test-student"
    TEST_SESSION = "generate-cards-test-session"

    sample_messages = [
        {"role": "user", "content": "What is the first-line treatment for primary open-angle glaucoma?"},
        {"role": "assistant", "content": (
            "**Explanation:** Prostaglandin analogues (e.g. latanoprost) are first-line for POAG.\n\n"
            "**Mechanism:** They increase uveoscleral outflow of aqueous humour.\n\n"
            "**Clinical Pearl:** Applied once daily in the evening for maximum efficacy.\n\n"
            "**Check Your Understanding:** What is the target IOP reduction with prostaglandins?"
        )},
    ]

    print("  Generating cards from sample session...")
    count = generate_cards(TEST_STUDENT, TEST_SESSION, sample_messages)
    print(f"  Cards generated: {count}")
    assert count > 0, "Expected at least 1 card"

    # Verify in SQLite
    from tools.shared.database import SessionLocal
    from tools.shared.models import Flashcard
    with SessionLocal() as db:
        rows = db.query(Flashcard).filter(Flashcard.session_id == TEST_SESSION).all()
        print(f"  Cards in DB: {len(rows)}")
        for row in rows:
            print(f"    Q: {row.front}")
            print(f"    A: {row.back}")

        # Clean up
        db.query(Flashcard).filter(Flashcard.session_id == TEST_SESSION).delete()
        db.commit()
    print("  Test cards cleaned up.")

    print("\n  [PASS] generate_cards.py working correctly.")
    sys.exit(0)
