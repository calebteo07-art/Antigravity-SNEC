#!/usr/bin/env python3
"""Agent 18: Health Monitor — checks all integrations are working correctly.

Run this before a study session or after any system change to confirm
everything is healthy. Reports PASS/WARN/FAIL per component.

Usage:
    python tools/shared/health_monitor.py
"""

import importlib.util
import json
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
load_dotenv(PROJECT_ROOT / ".env")
sys.path.insert(0, str(PROJECT_ROOT))

console = Console()

STATUS_COLORS = {"PASS": "green", "WARN": "yellow", "FAIL": "bold red", "INFO": "dim cyan"}


def _row(status: str, check: str, detail: str) -> tuple:
    return (status, check, detail)


def check_anthropic() -> tuple:
    import os
    key = os.getenv("ANTHROPIC_API_KEY", "").strip()
    if not key:
        return _row("WARN", "Anthropic API", "No API key — running in mock mode")

    req = urllib.request.Request(
        "https://api.anthropic.com/v1/models",
        headers={"x-api-key": key, "anthropic-version": "2023-06-01"},
    )
    try:
        with urllib.request.urlopen(req, timeout=8) as resp:
            return _row("PASS", "Anthropic API", f"HTTP {resp.status} - reachable")
    except urllib.error.HTTPError as e:
        return _row("FAIL", "Anthropic API", f"HTTP {e.code} - key may be invalid")
    except Exception as e:
        return _row("WARN", "Anthropic API", f"Network error: {e}")


def check_google_sheets() -> tuple:
    try:
        from tools.shared.gsheets import _get_spreadsheet
        ss = _get_spreadsheet()
        tabs = [ws.title for ws in ss.worksheets()]
        return _row("PASS", "Google Sheets", f"{len(tabs)} tabs accessible")
    except Exception as e:
        return _row("FAIL", "Google Sheets", str(e)[:80])


def check_google_drive() -> tuple:
    try:
        from tools.shared.gdrive import list_files
        files = list_files("audit")
        return _row("PASS", "Google Drive", f"snec_audit/ accessible ({len(files)} files)")
    except Exception as e:
        return _row("FAIL", "Google Drive", str(e)[:80])


def check_tmp_dir() -> tuple:
    tmp = PROJECT_ROOT / ".tmp"
    sentinel = tmp / ".health_check"
    try:
        tmp.mkdir(exist_ok=True)
        sentinel.write_text("ok", encoding="utf-8")
        sentinel.unlink()
        return _row("PASS", ".tmp/ directory", "Writable")
    except OSError as e:
        return _row("FAIL", ".tmp/ directory", str(e))


def check_audit_log() -> tuple:
    log_file = PROJECT_ROOT / ".tmp" / "audit_log.jsonl"
    if not log_file.exists():
        return _row("INFO", "Audit log", "No entries yet — starts on first use")
    lines = log_file.read_text(encoding="utf-8").strip().splitlines()
    if not lines:
        return _row("INFO", "Audit log", "File exists but empty")
    try:
        last = json.loads(lines[-1])
        ts = last.get("timestamp", "unknown")
        return _row("PASS", "Audit log", f"{len(lines)} entries, last at {ts[:19]}")
    except Exception:
        return _row("WARN", "Audit log", "File may be corrupted — check .tmp/audit_log.jsonl")


def check_cases() -> tuple:
    cases_dir = PROJECT_ROOT / "cases"
    if not cases_dir.exists():
        return _row("WARN", "Case library", "cases/ directory missing")
    cases = list(cases_dir.glob("*.json"))
    if not cases:
        return _row("WARN", "Case library", "No cases found — run author_case.py to create one")
    return _row("PASS", "Case library", f"{len(cases)} case(s) available")


def check_images() -> tuple:
    images_dir = PROJECT_ROOT / "images"
    if not images_dir.exists():
        return _row("WARN", "Image library", "images/ directory missing")
    images = list(images_dir.glob("*.png")) + list(images_dir.glob("*.jpg"))
    sidecars = list(images_dir.glob("*.json"))
    if not images:
        return _row("WARN", "Image library", "No images found")
    return _row("PASS", "Image library", f"{len(images)} image(s), {len(sidecars)} sidecar(s)")


def main() -> None:
    console.print(Panel(
        f"Running at {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}",
        title="Agent 18 - SNEC Health Monitor",
        border_style="blue",
    ))

    checks = [
        check_anthropic(),
        check_google_sheets(),
        check_google_drive(),
        check_tmp_dir(),
        check_audit_log(),
        check_cases(),
        check_images(),
    ]

    table = Table(show_header=True, header_style="bold", box=None, padding=(0, 1))
    table.add_column("Status", width=6)
    table.add_column("Component", min_width=22)
    table.add_column("Detail")

    for status, check, detail in checks:
        color = STATUS_COLORS.get(status, "white")
        table.add_row(f"[{color}]{status}[/{color}]", check, detail)

    console.print(Panel(table, title="System Health", border_style="blue"))

    failures = [c for c in checks if c[0] == "FAIL"]
    warnings = [c for c in checks if c[0] == "WARN"]

    if failures:
        console.print(f"[bold red]{len(failures)} FAIL(s) detected. Address before use.[/bold red]")
        sys.exit(1)
    elif warnings:
        console.print(f"[yellow]{len(warnings)} WARN(s) — system usable but some features limited.[/yellow]")
    else:
        console.print("[green]All checks passed.[/green]")

    sys.exit(0)


if __name__ == "__main__":
    main()
