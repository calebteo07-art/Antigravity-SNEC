# Install Dependencies — SOP

## Objective

Install all Python packages required by the SNEC platform in one command.
Run this once after first checkout, or whenever new packages are added to requirements.txt.

## When to Run

- After first cloning the repository
- After any change to requirements.txt
- When env_validator.py reports packages as FAIL

## How to Run

```
python tools/shared/dependency_installer.py
```

Run from the project root.

## What It Does

1. Checks which of the 14 required packages are already installed
2. Runs `pip install -r requirements.txt` to install everything missing
3. Verifies each package can be found after installation
4. Reports any failures with exact fix commands

## After Running

Run the environment validator to confirm all checks pass:

```
python tools/shared/env_validator.py
```

All package rows should now show PASS. The only remaining non-PASS items will be:
- ANTHROPIC_API_KEY (WARN) - until you purchase an API key
- credentials.json (SKIP) - until you set up Google OAuth
- token.json (SKIP) - until you run the OAuth flow

## Troubleshooting

**pip install fails with permission error**
Run the terminal as Administrator (Windows) or use `pip install --user`.

**A package installs but still shows FAIL in env_validator**
The package may have installed into a different Python environment. Confirm you are
running both scripts with the same Python: `python --version` and `which python`.

**Corporate network blocks pip**
Use a local mirror or ask your IT team to whitelist pypi.org.
