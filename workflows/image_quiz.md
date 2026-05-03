# Retinal Image Quiz — SOP

## Objective

Present a de-identified retinal image to the student, evaluate their systematic
description against ground truth findings using Claude's vision capability,
and log the result with specific feedback on missed and correct findings.

## How to Run

```
python tools/image_quiz/run_quiz.py
```

## What Happens

1. **Onboarding** — same as other features (skipped for returning students)
2. **Image selection** — student picks from available images in `images/`
3. **Description** — student opens the image file and types a systematic description
4. **Evaluation** — Claude scores on:
   - Correct key findings identified (6 pts)
   - Correct diagnosis/differential (2 pts)
   - Laterality and modality identified (1 pt)
   - Systematic approach (1 pt)
5. **Results** — score + correct/missed findings + written feedback displayed
6. **Logging** — result written to `snec_image_results` Google Sheet

## Adding New Images

1. Run the de-identification tool on the original image:
   ```
   python tools/privacy/deidentify_image.py <original_image.jpg>
   ```
2. This produces a clean PNG + JSON sidecar in `images/`
3. Edit the JSON sidecar to add ground truth findings and diagnosis
4. The image is now available in the quiz

## Image Metadata Sidecar Format

Each image requires a `.json` sidecar with the same filename stem:

```json
{
  "image_id": "img_abc123",
  "filename": "img_abc123.png",
  "modality": "fundus_photo",
  "eye": "right",
  "difficulty": "intermediate",
  "topic": "glaucoma",
  "ground_truth": {
    "diagnosis": "Glaucomatous optic neuropathy",
    "key_findings": ["Increased C:D ratio", "Disc haemorrhage"],
    "what_to_look_for": "optic disc, vessels, macula"
  },
  "de_identified": true
}
```

Valid modalities: `fundus_photo`, `oct`, `slit_lamp`, `visual_field`

## API Key Note

> Without `ANTHROPIC_API_KEY`, evaluation uses a simulated response.
> With the key, Claude uses native vision to directly analyse the image
> alongside the student's description for more accurate scoring.
