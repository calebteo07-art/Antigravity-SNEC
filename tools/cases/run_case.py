#!/usr/bin/env python3
"""Agent 13 + 14: Clinical Case Simulator and Evaluator.

Loads a clinical case, runs a multi-turn diagnostic dialogue where the student
interviews the virtual patient, then evaluates and scores their performance.

Usage:
    python tools/cases/run_case.py
    python tools/cases/run_case.py --case case_001_poag
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from tools.chatbot.onboarding import run_onboarding
from tools.cases.load_case import load_case, list_available_cases
from tools.cases.evaluate_response import evaluate_case
from tools.cases.log_result import log_case_result
from tools.shared.claude_client import ask, MOCK_MODE
from tools.shared.audit_log import log as audit_log
from tools.flashcards.generate_cards import generate_cards

EXIT_COMMANDS = {"exit", "quit", "done", "q", "submit"}

PATIENT_SYSTEM = """You are playing the role of a patient in a clinical case simulation for ophthalmology students.

IMPORTANT RULES:
- Answer ONLY what the student directly asks. Do not volunteer extra information.
- Stay in character as the patient — use lay language, not medical terminology.
- If the student asks for examination findings or investigation results, provide them as an examiner would.
- If the student asks to examine you, describe findings from the case.
- When the student says they are ready to give a diagnosis or management plan, acknowledge it.
- Do NOT reveal the diagnosis or correct answers — wait for the student to conclude.

Case details for your reference (do not reveal unless asked):
{case_json}"""


def _print_separator(char: str = "─", width: int = 60) -> None:
    print("\n" + char * width + "\n")


def _select_case() -> dict:
    """Let student pick a case or use command-line argument."""
    available = list_available_cases()
    if not available:
        print("\n  No cases available. Place case JSON files in .tmp/cases/")
        sys.exit(1)

    # Check for --case argument
    if "--case" in sys.argv:
        idx = sys.argv.index("--case")
        if idx + 1 < len(sys.argv):
            return load_case(sys.argv[idx + 1])

    if len(available) == 1:
        case = load_case(available[0])
        print(f"\n  Loading case: {case['title']} ({case['difficulty']})")
        return case

    print("\n  Available cases:\n")
    for i, cid in enumerate(available, 1):
        case = load_case(cid)
        print(f"  {i}. {case['title']} [{case['difficulty']}] — {case['topic']}")

    while True:
        try:
            choice = input("\n  Select a case (number): ").strip()
        except (KeyboardInterrupt, EOFError):
            sys.exit(0)

        if choice.isdigit() and 1 <= int(choice) <= len(available):
            return load_case(available[int(choice) - 1])
        print("  Invalid choice.")


def run_simulation(student_id: str, case: dict) -> None:
    """Run one full case simulation for the given student."""
    import json

    patient_prompt = PATIENT_SYSTEM.format(case_json=json.dumps(case, indent=2))
    conversation: list[dict] = []

    if MOCK_MODE:
        print("\n  [MOCK MODE] Patient responses are simulated.")
        print("  Add ANTHROPIC_API_KEY to .env for a real AI patient.\n")

    _print_separator("═")
    print(f"  CASE: {case['title']}")
    print(f"  Difficulty: {case['difficulty'].upper()}  |  Topic: {case['topic'].upper()}")
    print(f"  Estimated time: {case['estimated_minutes']} minutes")
    _print_separator()
    print(f"  Patient: {case['patient']['name']}, {case['patient']['age']}y {case['patient']['gender']}")
    print(f"  Presenting complaint: {case['patient']['presenting_complaint']}")
    _print_separator()
    print("  Take a full history, request examinations and investigations,")
    print("  then state your diagnosis and management plan.")
    print(f"  Type '{next(iter(EXIT_COMMANDS))}' when you are ready to submit.\n")

    audit_log("case_start", student_id=student_id, feature="cases",
              detail=f"case_id={case['case_id']}")

    while True:
        try:
            user_input = input("  You: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\n  Session interrupted.")
            break

        if not user_input:
            continue

        if user_input.lower() in EXIT_COMMANDS:
            print("\n  Submitting case for evaluation...")
            break

        conversation.append({"role": "user", "content": user_input})

        response = ask(
            system_prompt=patient_prompt,
            messages=conversation,
            max_tokens=512,
            feature="case",
        )
        conversation.append({"role": "assistant", "content": response})

        _print_separator()
        print(f"  Patient: {response}")
        _print_separator()

    if not conversation:
        print("\n  No interactions recorded. Case not evaluated.\n")
        return

    # Evaluate
    print("\n  Evaluating your performance...\n")
    result = evaluate_case(case, conversation, student_id)

    # Display results
    _print_separator("═")
    print("  CASE EVALUATION RESULTS\n")
    print(f"  {'Domain':<22} {'Score':>6} {'/ Max':>6}")
    print("  " + "─" * 36)
    domains = [
        ("History Taking", "history_score"),
        ("Investigations", "investigations_score"),
        ("Diagnosis", "diagnosis_score"),
        ("Management", "management_score"),
    ]
    for label, key in domains:
        score = result.get(key, 0)
        print(f"  {label:<22} {score:>6} {'/ 10':>6}")
    print("  " + "─" * 36)
    print(f"  {'TOTAL':<22} {result.get('total_score', 0):>6} {'/ 40':>6}")
    _print_separator()

    print("  FEEDBACK\n")
    for label, key in domains:
        fb_key = key.replace("_score", "_feedback")
        print(f"  {label}: {result.get(fb_key, '')}")
    print()
    print(f"  Overall: {result.get('overall_feedback', '')}")
    _print_separator("═")

    # Log to Sheets
    result_id = log_case_result(student_id, case, result)
    print(f"  Result saved (ID: {result_id})")

    # Seed missed items as flash-cards
    print("  Generating flash-cards from missed topics...")
    try:
        card_count = generate_cards(student_id, result_id, conversation,
                                    system_prompt=f"Case: {case['title']}")
        print(f"  {card_count} flash-card(s) generated.\n")
    except Exception as e:
        print(f"  Flash-card generation failed: {e}\n")


def main() -> None:
    student_id = run_onboarding()
    case = _select_case()
    run_simulation(student_id, case)


if __name__ == "__main__":
    main()
