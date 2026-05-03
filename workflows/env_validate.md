# Environment Validation — SOP

## Objective

Verify the local development environment is correctly configured before any other tool is run. This is the **first workflow to execute** in a fresh checkout and after any credential or dependency change.

## When to Run

- On first checkout of this repository
- After pulling changes that add new packages to `requirements.txt`
- When any tool fails with an `ImportError` or authentication error
- After rotating `credentials.json` or `token.json`
- Before starting a significant work session (optional but recommended)

## How to Run

```
python tools/shared/env_validator.py
```

Run from the project root. The script auto-detects its location.

## Interpreting Results

| Status | Meaning | Action Required |
|---|---|---|
| PASS | Check succeeded | None |
| WARN | Non-blocking (e.g., API key not yet purchased) | Address before using that feature |
| FAIL | Blocking problem | Follow the "Next Steps" action hint |
| SKIP | Prerequisite not yet in place | Not an error — follow the hint when ready |

Exit code is `0` unless there are FAIL items. WARN and SKIP do not block.

## Steps to Follow

1. Run the validator. Read the full output before taking action.
2. For each **FAIL** item: follow its Next Steps action exactly.
3. For **WARN** on `ANTHROPIC_API_KEY`: record as a known pending item. Do not run chatbot, flash-card, or case features until the key is obtained and added to `.env`.
4. For **SKIP** on `token.json`: expected until the first OAuth run. When Google features are needed, the OAuth flow will be documented in `workflows/google_oauth.md`.
5. Re-run the validator after fixing each FAIL to confirm the fix worked.
6. Do not proceed to any feature workflow until all FAIL items are resolved.

## Common First-Run Fixes

```
# 1. Create .env from template
copy .env.example .env          # Windows
cp .env.example .env            # macOS/Linux

# 2. Install all packages (once requirements.txt exists)
pip install -r requirements.txt
```

## Edge Cases

**credentials.json is a service account key**
The platform uses OAuth 2.0 (user-delegated access), not service accounts. Go to GCP Console → APIs & Services → Credentials → OAuth 2.0 Client IDs → Desktop app. Download that file, not the service account JSON.

**SSL or proxy error during Anthropic live ping**
Usually a corporate proxy or antivirus intercepting HTTPS. The ping returns WARN rather than FAIL — the key format was still validated. Note the proxy config and inform your network admin if needed.

**Google connectivity fails with 403**
The OAuth token scopes are insufficient. Delete `token.json` and re-run the OAuth flow. The correct scopes are:
- `https://www.googleapis.com/auth/spreadsheets`
- `https://www.googleapis.com/auth/drive.file`

**All packages show FAIL**
Fresh Python environment. Run `pip install -r requirements.txt` then re-validate.

**Python version error**
This project requires Python ≥ 3.8. Check with `python --version`.

## Output

A status table printed to stdout, one row per check, followed by a numbered Next Steps list for anything not PASS. Exit code `1` if any FAIL items exist.
