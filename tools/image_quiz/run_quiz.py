#!/usr/bin/env python3
"""Agent 15: Retinal Image Quiz — student describes a retinal image, Claude evaluates it.

Usage:
    python tools/image_quiz/run_quiz.py
"""

import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from tools.chatbot.onboarding import run_onboarding
from tools.image_quiz.evaluate_description import evaluate_description
from tools.image_quiz.log_result import log_image_result
from tools.shared.audit_log import log as audit_log
from tools.shared.claude_client import MOCK_MODE

IMAGES_DIR = PROJECT_ROOT / "images"


def _list_images() -> list[tuple[Path, dict]]:
    """Return list of (image_path, metadata) pairs from the images/ directory."""
    pairs = []
    for img_path in sorted(IMAGES_DIR.glob("*.png")) + sorted(IMAGES_DIR.glob("*.jpg")):
        meta_path = img_path.with_suffix(".json")
        if meta_path.exists():
            meta = json.loads(meta_path.read_text(encoding="utf-8"))
            pairs.append((img_path, meta))
    return pairs


def _print_separator(char: str = "─", width: int = 60) -> None:
    print("\n" + char * width + "\n")


def run_quiz(student_id: str) -> None:
    images = _list_images()

    if not images:
        print("\n  No images found in images/ directory.")
        print("  Add PNG/JPG files with matching .json metadata sidecars.\n")
        return

    if MOCK_MODE:
        print("\n  [MOCK MODE] Image evaluation uses simulated responses.")
        print("  Add ANTHROPIC_API_KEY to .env for real vision-based evaluation.\n")

    # Select image
    if len(images) == 1:
        image_path, image_meta = images[0]
        print(f"\n  Loading image: {image_path.name}")
    else:
        print("\n  Available images:\n")
        for i, (p, m) in enumerate(images, 1):
            print(f"  {i}. {p.name} [{m.get('modality', '')}] — {m.get('topic', '')}")
        while True:
            try:
                choice = input("\n  Select an image (number): ").strip()
            except (KeyboardInterrupt, EOFError):
                return
            if choice.isdigit() and 1 <= int(choice) <= len(images):
                image_path, image_meta = images[int(choice) - 1]
                break
            print("  Invalid choice.")

    _print_separator("═")
    print(f"  IMAGE QUIZ")
    print(f"  Modality : {image_meta.get('modality', 'fundus_photo').replace('_', ' ').title()}")
    print(f"  Eye      : {image_meta.get('eye', 'unknown').title()}")
    print(f"  Difficulty: {image_meta.get('difficulty', '').upper()}")
    _print_separator()
    print(f"  Please open this image and describe what you see:")
    print(f"\n  >>> {image_path.resolve()} <<<\n")
    print("  Describe systematically:")
    print("  - Optic disc (size, cup:disc ratio, rim, haemorrhages)")
    print("  - Macula (foveal reflex, drusen, haemorrhage, exudates)")
    print("  - Blood vessels (calibre, A:V ratio, crossings)")
    print("  - Periphery (any lesions)")
    print("  - Your diagnosis or differential\n")

    audit_log("image_quiz_start", student_id=student_id, feature="image_quiz",
              detail=f"image_id={image_meta.get('image_id')}")

    try:
        print("  Your description (press Enter twice when done):")
        lines = []
        while True:
            line = input("  ")
            if line == "" and lines and lines[-1] == "":
                break
            lines.append(line)
        description = "\n".join(lines).strip()
    except (KeyboardInterrupt, EOFError):
        print("\n  Quiz cancelled.")
        return

    if not description:
        print("\n  No description entered. Quiz not scored.\n")
        return

    print("\n  Evaluating your description...")
    result = evaluate_description(image_meta, description, image_path)
    result["_raw_description"] = description

    # Display results
    _print_separator("═")
    print(f"  SCORE: {result.get('score', 0)} / 10\n")

    correct = result.get("correct_findings", [])
    missed = result.get("missed_findings", [])
    incorrect = result.get("incorrect_findings", [])

    if correct:
        print("  Correctly identified:")
        for f in correct:
            print(f"    + {f}")

    if missed:
        print("\n  Missed findings:")
        for f in missed:
            print(f"    - {f}")

    if incorrect:
        print("\n  Incorrect/over-called:")
        for f in incorrect:
            print(f"    x {f}")

    print(f"\n  Feedback: {result.get('feedback', '')}")
    _print_separator("═")

    # Log result
    result_id = log_image_result(student_id, image_meta, result)
    print(f"  Result saved (ID: {result_id})\n")


def main() -> None:
    student_id = run_onboarding()
    run_quiz(student_id)


if __name__ == "__main__":
    main()
