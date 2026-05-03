# Bootstrap Infrastructure — SOP

## Objective

Create all Google Sheets and Drive folders the SNEC platform needs, in one command.
Run this once before building any feature agents. It is safe to re-run — existing
resources are detected and reused rather than duplicated.

## When to Run

- Once, after credentials.json is in place and packages are installed
- If the spreadsheet or Drive folders are accidentally deleted (re-run to recreate)
- Never needs to run again after the first successful execution

## Prerequisites

Before running, confirm:
- `credentials.json` is in the project root (from GCP Console)
- All packages installed: `python tools/shared/dependency_installer.py`
- Internet connection available

## How to Run

```
python tools/shared/infrastructure_bootstrap.py
```

Run from the project root.

## What Happens

1. **OAuth login** — a browser window opens. Log in with your Google account and
   click Allow. This happens once only. The token is saved to `token.json` and
   reused on all future runs.

2. **Spreadsheet created** — a Google Spreadsheet named `SNEC AI Platform` is
   created in your Google Drive with 6 sheet tabs, each with bold column headers:
   - `snec_sessions` — chatbot session logs
   - `snec_flashcards` — flash-card spaced repetition state
   - `snec_case_results` — clinical case simulation scores
   - `snec_image_results` — retinal image quiz results
   - `snec_api_usage` — Claude API token usage and cost tracking
   - `snec_consent` — student consent records

3. **Drive folders created** — 3 folders created in your Google Drive:
   - `snec_cases/` — case JSON files
   - `snec_images/` — de-identified clinical images
   - `snec_audit/` — synced audit log copies

4. **IDs written to .env** — the spreadsheet ID and folder IDs are saved to `.env`
   so all other tools can find them automatically.

## After Running

Verify everything is working:
```
python tools/shared/env_validator.py
```
Google Sheets and Google Drive rows should now show PASS.

Open your Google Drive in a browser and confirm:
- The `SNEC AI Platform` spreadsheet is visible with 6 tabs
- The 3 folders (`snec_cases`, `snec_images`, `snec_audit`) exist

## Troubleshooting

**Browser does not open during OAuth**
The script uses a local server on a random port. If your firewall blocks it, try
temporarily disabling it or running from a different network.

**Error: Access blocked — app not verified**
Your GCP app is in Testing mode, which is fine. Click "Advanced" on the warning
screen, then "Go to SNEC AI (unsafe)" to proceed. This warning only appears because
the app has not been submitted to Google for verification — it is not a security risk
for your own personal use.

**HttpError 403 — insufficient permissions**
The OAuth token has the wrong scopes. Delete `token.json` and re-run. The browser
will ask you to grant access again with the correct scopes.

**Resource already exists**
Safe to ignore — the script detects and reuses existing resources. No duplicates
will be created.
