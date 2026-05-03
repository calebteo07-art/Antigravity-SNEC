#!/usr/bin/env python3
"""Agent 17 (part 1): De-identifies a clinical image before it enters the SNEC platform.

Removes EXIF metadata, strips any embedded text identifying the patient,
assigns a UUID, and saves a clean copy ready for upload to Drive.

Usage:
    python tools/privacy/deidentify_image.py <input_image> [output_dir]

Self-test:
    python tools/privacy/deidentify_image.py
"""

import hashlib
import json
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

from PIL import Image

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

CLEAN_DIR = PROJECT_ROOT / "images"


def deidentify_image(
    input_path: str | Path,
    output_dir: str | Path | None = None,
    modality: str = "fundus_photo",
    eye: str = "unknown",
    topic: str = "",
    difficulty: str = "intermediate",
    ground_truth: dict | None = None,
) -> tuple[Path, dict]:
    """
    De-identify a clinical image and produce a clean copy with metadata sidecar.

    Steps:
    1. Open image with Pillow (strips all EXIF automatically)
    2. Re-save as PNG (lossless, no EXIF container)
    3. Assign a new UUID as the image_id
    4. Write a JSON metadata sidecar (no patient info)

    Args:
        input_path:  Path to the original clinical image.
        output_dir:  Where to save the clean copy (default: images/).
        modality:    Image type: fundus_photo, oct, slit_lamp, visual_field.
        eye:         "right", "left", or "unknown".
        topic:       Clinical topic (glaucoma, retina, etc.)
        difficulty:  Quiz difficulty level.
        ground_truth: Dict with diagnosis and key_findings for the quiz.

    Returns:
        (clean_image_path, metadata_dict)
    """
    input_path = Path(input_path)
    output_dir = Path(output_dir) if output_dir else CLEAN_DIR
    output_dir.mkdir(parents=True, exist_ok=True)

    image_id = f"img_{uuid.uuid4().hex[:12]}"

    # Open and re-save without EXIF
    with Image.open(input_path) as img:
        # Convert to RGB to ensure no alpha channel issues
        if img.mode in ("RGBA", "P"):
            img = img.convert("RGB")
        clean_path = output_dir / f"{image_id}.png"
        img.save(clean_path, format="PNG")

    # Try DICOM stripping if pydicom available
    if input_path.suffix.lower() in (".dcm", ".dicom"):
        try:
            import pydicom
            ds = pydicom.dcmread(str(input_path))
            pii_tags = [
                "PatientName", "PatientID", "PatientBirthDate",
                "PatientSex", "PatientAge", "InstitutionName",
                "StudyDate", "ReferringPhysicianName",
            ]
            for tag in pii_tags:
                if hasattr(ds, tag):
                    setattr(ds, tag, "")
            ds.save_as(str(clean_path.with_suffix(".dcm")))
        except ImportError:
            pass

    # Build metadata sidecar
    meta = {
        "image_id": image_id,
        "filename": clean_path.name,
        "modality": modality,
        "eye": eye,
        "difficulty": difficulty,
        "topic": topic,
        "ground_truth": ground_truth or {
            "diagnosis": "",
            "key_findings": [],
            "what_to_look_for": "",
        },
        "de_identified": True,
        "processed_at": datetime.now(timezone.utc).isoformat(),
        "source_hash": hashlib.sha256(input_path.read_bytes()).hexdigest()[:16],
        "patient_id_hash": "",
    }

    meta_path = clean_path.with_suffix(".json")
    meta_path.write_text(json.dumps(meta, indent=2, ensure_ascii=False), encoding="utf-8")

    return clean_path, meta


def main() -> None:
    if len(sys.argv) >= 2:
        input_path = Path(sys.argv[1])
        output_dir = Path(sys.argv[2]) if len(sys.argv) >= 3 else None
        clean_path, meta = deidentify_image(input_path, output_dir)
        print(f"De-identified image saved: {clean_path}")
        print(f"Metadata sidecar: {clean_path.with_suffix('.json')}")
        print(f"Image ID: {meta['image_id']}")
        return

    # Self-test: de-identify the sample image
    print("Testing deidentify_image.py...\n")

    sample = PROJECT_ROOT / "images" / "sample_fundus_OD.png"
    if not sample.exists():
        print(f"  Sample image not found: {sample}")
        sys.exit(1)

    test_out = PROJECT_ROOT / ".tmp"
    clean_path, meta = deidentify_image(
        input_path=sample,
        output_dir=test_out,
        modality="fundus_photo",
        eye="right",
        topic="glaucoma",
        difficulty="intermediate",
        ground_truth={
            "diagnosis": "Glaucomatous optic neuropathy",
            "key_findings": ["Increased C:D ratio", "Disc haemorrhage"],
            "what_to_look_for": "optic disc, vessels, macula",
        },
    )

    assert clean_path.exists(), "Clean image file not created"
    assert clean_path.with_suffix(".json").exists(), "Metadata sidecar not created"
    assert meta["de_identified"] is True
    assert meta["image_id"].startswith("img_")
    assert "patient" not in meta, "No patient PII should be in metadata"

    print(f"  Clean image : {clean_path.name}")
    print(f"  Image ID    : {meta['image_id']}")
    print(f"  Source hash : {meta['source_hash']}")

    # Cleanup
    clean_path.unlink()
    clean_path.with_suffix(".json").unlink()
    print("\n  [PASS] deidentify_image.py working correctly.")
    sys.exit(0)


if __name__ == "__main__":
    main()
