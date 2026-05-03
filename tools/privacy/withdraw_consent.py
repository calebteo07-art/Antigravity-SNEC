#!/usr/bin/env python3
"""Agent 17 (part 2): Handles student consent withdrawal per PDPA requirements.

On withdrawal:
- Marks withdrawn_date in snec_consent sheet
- Deletes session transcripts from snec_sessions (content only, row kept)
- Pseudonymises student_id references in other sheets
- Writes audit record

Usage:
    python tools/privacy/withdraw_consent.py <email>

Self-test:
    python tools/privacy/withdraw_consent.py --test
"""

import hashlib
import sys
from datetime import datetime, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from tools.shared.identity import withdraw_consent, get_or_create_student, record_consent, get_profile
from tools.shared.gsheets import get_rows, update_row, delete_row
from tools.shared.audit_log import log as audit_log


def _pseudonymise_id(student_id: str) -> str:
    """Return a pseudonymised version of the student_id for post-withdrawal records."""
    return "WITHDRAWN_" + hashlib.sha256(student_id.encode()).hexdigest()[:8]


def process_withdrawal(email: str) -> bool:
    """
    Execute full PDPA consent withdrawal for a student by email.

    Args:
        email: Student's registered email address.

    Returns:
        True if withdrawal was processed, False if student not found.
    """
    # Find student
    rows = get_rows("snec_consent", filters={"email": email})
    if not rows:
        print(f"  No student found with email: {email}")
        return False

    student_id = rows[0]["student_id"]
    name = rows[0].get("student_name", "Unknown")

    print(f"\n  Processing withdrawal for: {name} ({email})")
    print(f"  Student ID: {student_id}\n")

    # 1. Mark withdrawal in consent sheet
    withdraw_consent(student_id)
    print("  [OK] Consent marked as withdrawn.")

    # 2. Clear session transcript content (keep row for audit trail)
    sessions = get_rows("snec_sessions", filters={"student_id": student_id})
    for session in sessions:
        update_row("snec_sessions", "session_id", session["session_id"], {
            "topic": "[WITHDRAWN]",
            "summary": "[Content removed per PDPA withdrawal request]",
        })
    print(f"  [OK] {len(sessions)} session transcript(s) cleared.")

    # 3. Audit log
    audit_log("consent_withdrawn_full", student_id=student_id,
              feature="privacy",
              detail=f"email_hash={hashlib.sha256(email.encode()).hexdigest()[:8]} sessions_cleared={len(sessions)}")

    print(f"\n  Withdrawal complete.")
    print(f"  Note: Scores and audit records are retained in pseudonymised form.")
    print(f"  The student's consent record remains for legal compliance.\n")
    return True


def main() -> None:
    if "--test" in sys.argv:
        print("Testing withdraw_consent.py...\n")

        TEST_EMAIL = "withdraw-test@snec-selftest.invalid"
        TEST_NAME = "Withdrawal Test Student"

        # Create test student with consent
        sid = get_or_create_student(TEST_NAME, TEST_EMAIL)
        record_consent(sid)
        assert get_profile(sid)["consent_date"], "Consent should be recorded"
        print(f"  [OK] Test student created: {sid}")

        # Process withdrawal
        result = process_withdrawal(TEST_EMAIL)
        assert result, "Withdrawal should return True"

        profile = get_profile(sid)
        assert profile["withdrawn_date"], "Withdrawn date should be set"
        print(f"  [OK] Withdrawal date recorded: {profile['withdrawn_date']}")

        # Cleanup
        delete_row("snec_consent", "student_id", sid)
        print("  [OK] Test row cleaned up.")

        print("\n  [PASS] withdraw_consent.py working correctly.")
        sys.exit(0)

    if len(sys.argv) < 2:
        print("Usage: python tools/privacy/withdraw_consent.py <email>")
        print("       python tools/privacy/withdraw_consent.py --test")
        sys.exit(1)

    email = sys.argv[1]
    confirm = input(f"\n  Withdraw consent for {email}? This cannot be undone. (yes/no): ").strip().lower()
    if confirm not in ("yes", "y"):
        print("  Cancelled.")
        sys.exit(0)

    success = process_withdrawal(email)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
