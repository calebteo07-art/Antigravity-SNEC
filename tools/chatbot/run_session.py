#!/usr/bin/env python3
"""Agent 10: Tutor Chatbot — runs an interactive ophthalmology Q&A session.

Handles onboarding, conversation loop, session logging, and triggers
flash-card generation at the end of each session.

Usage:
    python tools/chatbot/run_session.py
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from tools.chatbot.onboarding import run_onboarding
from tools.chatbot.log_session import log_session
from tools.shared.claude_client import ask, MOCK_MODE, MODEL
from tools.shared.audit_log import log as audit_log

KB_FILE = PROJECT_ROOT / "workflows" / "ophthalmology_kb.md"
MAX_TOKENS = 1024
EXIT_COMMANDS = {"exit", "quit", "bye", "q"}


def _load_system_prompt() -> str:
    if not KB_FILE.exists():
        return "You are an ophthalmology tutor at SNEC. Answer questions clearly and educationally."
    return KB_FILE.read_text(encoding="utf-8")


def _print_separator() -> None:
    print("\n" + "─" * 60 + "\n")


def run_session(student_id: str) -> None:
    """Run one full chatbot session for the given student."""
    system_prompt = _load_system_prompt()
    messages: list[dict] = []
    token_count = 0

    if MOCK_MODE:
        print("\n  [MOCK MODE] Running without API key — responses are simulated.")
        print("  Add ANTHROPIC_API_KEY to .env for real AI responses.\n")

    print("  Type your ophthalmology question below.")
    print(f"  Type '{next(iter(EXIT_COMMANDS))}' to end the session.\n")

    audit_log("session_start", student_id=student_id, feature="chatbot", detail="")
    topic = ""

    while True:
        try:
            user_input = input("  You: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\n  Session interrupted.")
            break

        if not user_input:
            continue

        if user_input.lower() in EXIT_COMMANDS:
            print("\n  Ending session...")
            break

        # Record first message as topic
        if not topic:
            topic = user_input

        messages.append({"role": "user", "content": user_input})

        response = ask(
            system_prompt=system_prompt,
            messages=messages,
            max_tokens=MAX_TOKENS,
            feature="chatbot",
        )

        messages.append({"role": "assistant", "content": response})

        _print_separator()
        print(f"  Tutor:\n\n{response}")
        _print_separator()

    if not messages:
        print("\n  No messages recorded. Session not saved.\n")
        return

    # Log session to Sheets
    print("  Saving session...")
    session_id = log_session(
        student_id=student_id,
        topic=topic,
        messages=messages,
        token_count=token_count,
        model="mock" if MOCK_MODE else MODEL,
    )
    print(f"  Session saved (ID: {session_id})")

    # Trigger flash-card generation
    print("  Generating flash-cards from this session...")
    try:
        from tools.flashcards.generate_cards import generate_cards
        card_count = generate_cards(student_id, session_id, messages, system_prompt)
        print(f"  {card_count} flash-card(s) generated.\n")
    except Exception as e:
        print(f"  Flash-card generation failed: {e}\n")

    audit_log("session_end", student_id=student_id, feature="chatbot",
              detail=f"session_id={session_id} messages={len(messages)}")


def main() -> None:
    student_id = run_onboarding()
    run_session(student_id)


if __name__ == "__main__":
    main()
