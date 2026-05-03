#!/usr/bin/env python3
"""SNEC environment validator - run before any other tool.

Usage:
    python tools/shared/env_validator.py
"""

import importlib.util
import json
import os
import sys
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from pathlib import Path

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False

try:
    from dotenv import dotenv_values
    DOTENV_AVAILABLE = True
except ImportError:
    DOTENV_AVAILABLE = False

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

PACKAGES: dict[str, str] = {
    "anthropic": "anthropic",
    "gspread": "gspread",
    "google.auth": "google-auth",
    "googleapiclient": "google-api-python-client",
    "google_auth_oauthlib": "google-auth-oauthlib",
    "google_auth_httplib2": "google-auth-httplib2",
    "typer": "typer",
    "rich": "rich",
    "streamlit": "streamlit",
    "PIL": "Pillow",
    "pydicom": "pydicom",
    "pydantic": "pydantic",
    "reportlab": "reportlab",
    "dotenv": "python-dotenv",
}


@dataclass
class CheckResult:
    status: str  # PASS | WARN | FAIL | SKIP
    label: str
    detail: str
    action: str = ""


def _parse_env_file(path: Path) -> dict[str, str]:
    result: dict[str, str] = {}
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return result
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip()
        if len(value) >= 2 and value[0] in ('"', "'") and value[-1] == value[0]:
            value = value[1:-1]
        result[key] = value
    return result


def _ping_anthropic(api_key: str) -> tuple[bool, str]:
    req = urllib.request.Request(
        "https://api.anthropic.com/v1/models",
        headers={
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=8) as resp:
            return True, f"HTTP {resp.status} - API reachable"
    except urllib.error.HTTPError as e:
        if e.code == 401:
            return False, "HTTP 401 - key rejected by Anthropic"
        return False, f"HTTP {e.code} - unexpected response"
    except Exception as e:
        return False, f"Network error: {e}"


class EnvValidator:
    def __init__(self) -> None:
        self._env: dict[str, str] = {}

    def _load_env(self) -> None:
        env_path = PROJECT_ROOT / ".env"
        if not env_path.exists():
            return
        if DOTENV_AVAILABLE:
            self._env = {k: v for k, v in dotenv_values(env_path).items() if v is not None}
        else:
            self._env = _parse_env_file(env_path)

    def check_dot_env_file(self) -> CheckResult:
        path = PROJECT_ROOT / ".env"
        if path.exists():
            return CheckResult("PASS", ".env file", "Found")
        return CheckResult(
            "FAIL", ".env file", "File not found",
            action="copy .env.example to .env"
        )

    def check_anthropic_key(self) -> list[CheckResult]:
        results: list[CheckResult] = []
        key = self._env.get("ANTHROPIC_API_KEY", "").strip()

        if not key:
            results.append(CheckResult(
                "WARN", "ANTHROPIC_API_KEY", "Not set - add to .env when ready",
                action="Add ANTHROPIC_API_KEY=sk-ant-... to .env"
            ))
            return results

        if not key.startswith("sk-ant-"):
            results.append(CheckResult(
                "FAIL", "ANTHROPIC_API_KEY", "Present but invalid format (expected sk-ant-...)",
                action="Replace with a valid Anthropic API key"
            ))
            return results

        preview = key[:16] + "..."
        results.append(CheckResult("PASS", "ANTHROPIC_API_KEY", f"Format valid ({preview})"))

        ok, msg = _ping_anthropic(key)
        if ok:
            results.append(CheckResult("PASS", "Anthropic live ping", msg))
        else:
            status = "FAIL" if "401" in msg or "rejected" in msg else "WARN"
            results.append(CheckResult(
                status, "Anthropic live ping", msg,
                action="Verify key at console.anthropic.com" if status == "FAIL" else ""
            ))

        return results

    def check_credentials_json(self) -> CheckResult:
        path = PROJECT_ROOT / "credentials.json"
        if not path.exists():
            return CheckResult(
                "SKIP", "credentials.json", "Not found",
                action="Download from GCP Console -> APIs & Services -> OAuth 2.0 Client IDs"
            )
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except Exception as e:
            return CheckResult("FAIL", "credentials.json", f"Invalid JSON: {e}")

        flow_type = next((k for k in ("installed", "web") if k in data), None)
        if not flow_type:
            return CheckResult(
                "FAIL", "credentials.json",
                "Missing 'installed' or 'web' key - looks like a service account key",
                action="Download an OAuth 2.0 Desktop app credential, not a service account"
            )

        if not data[flow_type].get("client_id"):
            return CheckResult("FAIL", "credentials.json", "Missing client_id field")

        return CheckResult("PASS", "credentials.json", f"Valid ({flow_type} app)")

    def check_token_json(self) -> CheckResult:
        path = PROJECT_ROOT / "token.json"
        if not path.exists():
            return CheckResult(
                "SKIP", "token.json", "Not yet generated",
                action="Run OAuth flow once via tools/shared/gdrive.py to create token.json"
            )
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except Exception as e:
            return CheckResult("FAIL", "token.json", f"Invalid JSON: {e}")

        if not (data.get("token") or data.get("refresh_token") or data.get("access_token")):
            return CheckResult(
                "WARN", "token.json", "Unexpected format - no token fields found",
                action="Delete token.json and re-run OAuth flow"
            )
        return CheckResult("PASS", "token.json", "Found with token fields")

    def check_google_connectivity(self) -> list[CheckResult]:
        creds_path = PROJECT_ROOT / "credentials.json"
        token_path = PROJECT_ROOT / "token.json"

        if not (creds_path.exists() and token_path.exists()):
            return [
                CheckResult("SKIP", "Google Sheets", "Waiting on credentials.json + token.json"),
                CheckResult("SKIP", "Google Drive", "Waiting on credentials.json + token.json"),
            ]

        try:
            from google.oauth2.credentials import Credentials
            from googleapiclient.discovery import build
        except ImportError:
            return [
                CheckResult("SKIP", "Google Sheets", "Install google-api-python-client to test"),
                CheckResult("SKIP", "Google Drive", "Install google-api-python-client to test"),
            ]

        results: list[CheckResult] = []
        try:
            creds = Credentials.from_authorized_user_file(str(token_path))
        except Exception as e:
            return [
                CheckResult("FAIL", "Google Sheets", f"Could not load token.json: {e}"),
                CheckResult("FAIL", "Google Drive", f"Could not load token.json: {e}"),
            ]

        try:
            # Sheets API has no list() — use Drive to list spreadsheet files instead
            drive_svc = build("drive", "v3", credentials=creds, cache_discovery=False)
            drive_svc.files().list(
                q="mimeType='application/vnd.google-apps.spreadsheet'",
                pageSize=1, fields="files(id)"
            ).execute()
            results.append(CheckResult("PASS", "Google Sheets", "Connected"))
        except Exception as e:
            results.append(CheckResult(
                "FAIL", "Google Sheets", str(e),
                action="Check OAuth scopes or delete token.json and re-authorise"
            ))

        try:
            svc = build("drive", "v3", credentials=creds, cache_discovery=False)
            svc.files().list(pageSize=1, fields="files(id)").execute()
            results.append(CheckResult("PASS", "Google Drive", "Connected"))
        except Exception as e:
            results.append(CheckResult(
                "FAIL", "Google Drive", str(e),
                action="Check OAuth scopes or delete token.json and re-authorise"
            ))

        return results

    def check_packages(self) -> list[CheckResult]:
        results: list[CheckResult] = []
        for import_name, pip_name in PACKAGES.items():
            try:
                found = importlib.util.find_spec(import_name) is not None
            except (ModuleNotFoundError, ValueError):
                found = False
            if found:
                results.append(CheckResult("PASS", f"pkg: {pip_name}", "Installed"))
            else:
                results.append(CheckResult(
                    "FAIL", f"pkg: {pip_name}", "Not installed",
                    action=f"pip install {pip_name}"
                ))
        return results

    def check_tmp_dir(self) -> CheckResult:
        tmp = PROJECT_ROOT / ".tmp"
        if not tmp.is_dir():
            return CheckResult(
                "FAIL", ".tmp/ directory", "Does not exist",
                action="mkdir .tmp"
            )
        sentinel = tmp / ".validator_write_test"
        try:
            sentinel.write_text("ok", encoding="utf-8")
            sentinel.unlink()
            return CheckResult("PASS", ".tmp/ directory", "Writable")
        except OSError as e:
            return CheckResult("FAIL", ".tmp/ directory", f"Not writable: {e}")

    def run_all(self) -> list[CheckResult]:
        self._load_env()
        results: list[CheckResult] = []

        results.append(self.check_dot_env_file())
        results.extend(self.check_anthropic_key())
        results.append(self.check_credentials_json())
        results.append(self.check_token_json())
        results.extend(self.check_google_connectivity())
        results.extend(self.check_packages())
        results.append(self.check_tmp_dir())

        return results


class Renderer:
    STATUS_COLORS = {
        "PASS": "green",
        "WARN": "yellow",
        "FAIL": "bold red",
        "SKIP": "dim cyan",
    }

    def render(self, results: list[CheckResult]) -> None:
        if RICH_AVAILABLE:
            self._render_rich(results)
        else:
            self._render_plain(results)

    def _render_rich(self, results: list[CheckResult]) -> None:
        console = Console()

        table = Table(show_header=True, header_style="bold", box=None, padding=(0, 1))
        table.add_column("Status", width=6)
        table.add_column("Check", min_width=28)
        table.add_column("Detail")

        for r in results:
            color = self.STATUS_COLORS.get(r.status, "white")
            table.add_row(
                f"[{color}]{r.status}[/{color}]",
                r.label,
                r.detail,
            )

        console.print(Panel(table, title="SNEC AI - Environment Validation", border_style="blue"))

        actions = [(i + 1, r) for i, r in enumerate(results) if r.action]
        if actions:
            lines = "\n".join(f"  {n}. {r.action}" for n, r in actions)
            console.print(Panel(lines, title="Next Steps", border_style="yellow"))

    def _render_plain(self, results: list[CheckResult]) -> None:
        col1 = max(len(r.status) for r in results)
        col2 = max(len(r.label) for r in results)
        col3 = max(len(r.detail) for r in results)
        sep = f"+{'-' * (col1 + 2)}+{'-' * (col2 + 2)}+{'-' * (col3 + 2)}+"

        print("\n  SNEC AI - Environment Validation\n")
        print(sep)
        print(f"| {'Status'.ljust(col1)} | {'Check'.ljust(col2)} | {'Detail'.ljust(col3)} |")
        print(sep)
        for r in results:
            print(f"| {r.status.ljust(col1)} | {r.label.ljust(col2)} | {r.detail.ljust(col3)} |")
        print(sep)

        actions = [r for r in results if r.action]
        if actions:
            print("\n  Next Steps:\n")
            for i, r in enumerate(actions, 1):
                print(f"  {i}. {r.action}")
        print()


def main() -> None:
    results = EnvValidator().run_all()
    Renderer().render(results)
    has_failures = any(r.status == "FAIL" for r in results)
    sys.exit(1 if has_failures else 0)


if __name__ == "__main__":
    main()
