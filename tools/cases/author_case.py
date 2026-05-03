#!/usr/bin/env python3
"""Agent 16: Case Author — guided CLI for clinicians to write new clinical cases.

Walks through all required fields interactively, validates the schema,
and saves the case JSON to cases/ (and optionally uploads to Drive).

Usage:
    python tools/cases/author_case.py
"""

import json
import sys
import uuid
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

CASES_DIR = PROJECT_ROOT / "cases"


def _ask(prompt: str, required: bool = True) -> str:
    """Prompt for input, re-asking if required and empty."""
    while True:
        try:
            value = input(f"  {prompt}: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\n  Cancelled.")
            sys.exit(0)
        if value or not required:
            return value
        print("  (This field is required)")


def _ask_list(prompt: str, hint: str = "") -> list[str]:
    """Collect multiple items until blank line."""
    print(f"  {prompt} {hint}")
    print("  (Enter one per line, blank line to finish)")
    items = []
    while True:
        try:
            item = input("    - ").strip()
        except (KeyboardInterrupt, EOFError):
            break
        if not item:
            break
        items.append(item)
    return items


def _ask_choice(prompt: str, options: list[str]) -> str:
    opts = " / ".join(options)
    while True:
        value = _ask(f"{prompt} ({opts})").lower()
        if value in [o.lower() for o in options]:
            return value
        print(f"  Please choose one of: {opts}")


def _print_section(title: str) -> None:
    print(f"\n  {'─' * 50}")
    print(f"  {title.upper()}")
    print(f"  {'─' * 50}\n")


def build_case() -> dict:
    print("\n" + "═" * 60)
    print("  SNEC Case Author — New Clinical Case")
    print("═" * 60)
    print("  Answer each question. Press Enter to skip optional fields.")
    print("  Type Ctrl+C at any time to cancel.\n")

    case_id = f"case_{uuid.uuid4().hex[:8]}"

    _print_section("Basic Information")
    title = _ask("Case title (e.g. 'The Silent Thief')")
    difficulty = _ask_choice("Difficulty", ["beginner", "intermediate", "advanced"])
    topic = _ask_choice("Topic", ["glaucoma", "retina", "cornea", "cataract", "neuro-ophthalmology", "paediatric", "oculoplastics", "other"])
    minutes = _ask("Estimated time in minutes (e.g. 15)", required=False) or "15"

    _print_section("Patient Details")
    pt_name = _ask("Patient name (use fake name, e.g. 'Mr Tan Ah Kow')")
    pt_age = _ask("Age")
    pt_gender = _ask_choice("Gender", ["male", "female"])
    pt_occupation = _ask("Occupation", required=False)
    pt_complaint = _ask("Presenting complaint (one sentence)")

    _print_section("History")
    hpc = _ask("History of presenting complaint (2-4 sentences)")
    pmhx = _ask("Past medical history")
    family_hx = _ask("Family history", required=False)
    medications_raw = _ask("Current medications (comma-separated)", required=False)
    medications = [m.strip() for m in medications_raw.split(",")] if medications_raw else []
    social_hx = _ask("Social history", required=False)

    _print_section("Examination Findings")
    va_right = _ask("Visual acuity — Right eye (e.g. 6/6)")
    va_left = _ask("Visual acuity — Left eye")
    iop_right = _ask("IOP — Right eye (e.g. 16 mmHg)")
    iop_left = _ask("IOP — Left eye")
    ant_seg = _ask("Anterior segment findings")
    fundus_right = _ask("Fundus — Right eye")
    fundus_left = _ask("Fundus — Left eye")

    _print_section("Investigations")
    vf = _ask("Visual field findings", required=False)
    oct = _ask("OCT/imaging findings", required=False)
    other_ix = _ask("Other investigations (e.g. FFA, B-scan)", required=False)

    _print_section("Diagnosis & Management")
    diagnosis = _ask("Correct diagnosis (full description)")
    immediate_mx = _ask_list("Immediate management steps", "(3-5 steps)")
    followup_mx = _ask_list("Follow-up plan", "(2-4 points)")
    education = _ask_list("Patient education points", "(2-3 points)")

    _print_section("Marking Rubric")
    print("  Enter key points the student MUST cover for full marks in each domain.")
    history_points = _ask_list("History domain key points (4 points)")
    ix_points = _ask_list("Investigations domain key points (4 points)")
    dx_points = _ask_list("Diagnosis domain key points (3 points)")
    mx_points = _ask_list("Management domain key points (4 points)")

    case = {
        "case_id": case_id,
        "title": title,
        "difficulty": difficulty,
        "topic": topic,
        "estimated_minutes": int(minutes) if minutes.isdigit() else 15,
        "patient": {
            "name": pt_name,
            "age": int(pt_age) if pt_age.isdigit() else pt_age,
            "gender": pt_gender,
            "occupation": pt_occupation,
            "presenting_complaint": pt_complaint,
        },
        "history": {
            "hpc": hpc,
            "pmhx": pmhx,
            "family_hx": family_hx,
            "medications": medications,
            "social_hx": social_hx,
        },
        "examination_findings": {
            "va": {"right": va_right, "left": va_left},
            "iop": {"right": iop_right, "left": iop_left},
            "anterior_segment": ant_seg,
            "fundus": {"right": fundus_right, "left": fundus_left},
        },
        "investigations": {
            "visual_field": vf,
            "oct_rnfl": oct,
            "other": other_ix,
        },
        "diagnosis": diagnosis,
        "management": {
            "immediate": immediate_mx,
            "follow_up": followup_mx,
            "patient_education": education,
        },
        "rubric": {
            "history": {"points": 10, "key_points": history_points},
            "investigations": {"points": 10, "key_points": ix_points},
            "diagnosis": {"points": 10, "key_points": dx_points},
            "management": {"points": 10, "key_points": mx_points},
        },
    }

    return case


def save_case(case: dict) -> Path:
    CASES_DIR.mkdir(exist_ok=True)
    path = CASES_DIR / f"{case['case_id']}.json"
    path.write_text(json.dumps(case, indent=2, ensure_ascii=False), encoding="utf-8")
    return path


def main() -> None:
    case = build_case()

    print("\n\n  Preview:\n")
    print(f"  Title     : {case['title']}")
    print(f"  Case ID   : {case['case_id']}")
    print(f"  Topic     : {case['topic']} ({case['difficulty']})")
    print(f"  Patient   : {case['patient']['name']}, {case['patient']['age']}y")
    print(f"  Diagnosis : {case['diagnosis']}")

    confirm = _ask("\n  Save this case? (yes/no)")
    if confirm.lower() not in ("yes", "y"):
        print("  Case discarded.\n")
        sys.exit(0)

    path = save_case(case)
    print(f"\n  Case saved: {path}")

    # Optionally upload to Drive
    try:
        upload = _ask("  Upload to Google Drive snec_cases/ folder? (yes/no)", required=False)
        if upload.lower() in ("yes", "y"):
            from tools.shared.gdrive import upload_file
            file_id = upload_file(path, "cases")
            print(f"  Uploaded to Drive (ID: {file_id})")
    except Exception as e:
        print(f"  Drive upload skipped: {e}")

    print(f"\n  Done. Run the case with:")
    print(f"  python tools/cases/run_case.py --case {case['case_id']}\n")


if __name__ == "__main__":
    main()
