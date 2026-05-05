#!/usr/bin/env python3
"""Agent 9: Onboarding — first-run student setup with PDPA consent flow.

Called automatically at the start of a chatbot session if the student
has not yet registered or given consent. Should not be called directly.

Usage (from run_session.py):
    from tools.chatbot.onboarding import run_onboarding
    student_id = run_onboarding()
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from tools.shared.identity import get_or_create_student, has_consented, record_consent
from tools.shared.audit_log import log


PDPA_NOTICE = """
╔══════════════════════════════════════════════════════════════════════╗
║                 EyeQ — Data Collection Notice                        ║
╠══════════════════════════════════════════════════════════════════════╣
║                                                                      ║
║  This platform collects and processes the following personal data:   ║
║                                                                      ║
║  • Your name and email address (for identity and progress tracking)  ║
║  • Your Q&A session transcripts (for flash-card generation)          ║
║  • Your quiz and case simulation scores (for analytics)              ║
║                                                                      ║
║  Your data is governed by the Singapore Personal Data Protection      ║
║  Act (PDPA) 2012. It will not be shared with third parties and       ║
║  will not be used to train AI models.                                ║
║                                                                      ║
║  You may withdraw consent at any time by contacting the platform     ║
║  administrator. Withdrawal will pseudonymise your historical data.   ║
║                                                                      ║
╚══════════════════════════════════════════════════════════════════════╝
"""


def run_onboarding() -> str:
    """
    Run the full onboarding flow for a new or returning student.

    - New students: collect name + email, show PDPA notice, record consent.
    - Returning students who already consented: skip straight through.
    - Returning students who withdrew consent: ask them to re-consent.

    Returns:
        student_id (UUID string)
    """
    print("\n  Welcome to EyeQ\n")

    # Collect identity
    print("  Please enter your details to continue.")
    name = input("  Full name: ").strip()
    email = input("  Email address: ").strip()

    if not name or not email:
        print("\n  Name and email are required. Exiting.")
        sys.exit(1)

    student_id = get_or_create_student(name, email)

    # Check consent
    if has_consented(student_id):
        print(f"\n  Welcome back, {name}.")
        log("onboarding_returning", student_id=student_id, feature="onboarding", detail="consent already on record")
        return student_id

    # Show PDPA notice and ask for consent
    print(PDPA_NOTICE)
    while True:
        answer = input("  Do you consent to the above? (yes / no): ").strip().lower()
        if answer in ("yes", "y"):
            record_consent(student_id)
            print(f"\n  Thank you, {name}. Consent recorded.")
            log("onboarding_new", student_id=student_id, feature="onboarding", detail="consent given")
            return student_id
        elif answer in ("no", "n"):
            print("\n  Consent is required to use this platform. Exiting.")
            log("onboarding_declined", student_id=student_id, feature="onboarding", detail="consent declined")
            sys.exit(0)
        else:
            print("  Please type 'yes' or 'no'.")
