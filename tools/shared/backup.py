#!/usr/bin/env python3
"""Agent 21: Backup Agent — syncs local audit log to Google Drive snec_audit/ folder.

Uploads .tmp/audit_log.jsonl to Drive with a timestamp in the filename,
then optionally trims the local file to keep only recent entries.

Usage:
    python tools/shared/backup.py
    python tools/shared/backup.py --keep 1000    # keep last 1000 lines locally
"""

import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
load_dotenv(PROJECT_ROOT / ".env")
sys.path.insert(0, str(PROJECT_ROOT))

console = Console()

AUDIT_LOG = PROJECT_ROOT / ".tmp" / "audit_log.jsonl"
DEFAULT_KEEP_LINES = 500


def run_backup(keep_lines: int = DEFAULT_KEEP_LINES) -> None:
    from tools.shared.gdrive import upload_file, list_files
    from tools.shared.audit_log import log as audit_log

    console.print(Panel("", title="Agent 21 - Backup Agent", border_style="blue"))

    # Check audit log exists
    if not AUDIT_LOG.exists() or AUDIT_LOG.stat().st_size == 0:
        console.print("  [yellow]Audit log is empty — nothing to back up.[/yellow]\n")
        return

    lines = AUDIT_LOG.read_text(encoding="utf-8").strip().splitlines()
    console.print(f"  Audit log entries : {len(lines)}")

    # Create timestamped backup copy in .tmp/
    ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    backup_name = f"audit_log_{ts}.jsonl"
    backup_path = PROJECT_ROOT / ".tmp" / backup_name
    shutil.copy2(AUDIT_LOG, backup_path)

    # Upload to Drive
    console.print(f"  Uploading {backup_name} to snec_audit/...")
    try:
        file_id = upload_file(backup_path, "audit")
        console.print(f"  [green]Uploaded successfully (ID: {file_id})[/green]")
    except Exception as e:
        console.print(f"  [red]Upload failed: {e}[/red]")
        backup_path.unlink(missing_ok=True)
        sys.exit(1)

    # Clean up local backup copy
    backup_path.unlink(missing_ok=True)

    # Trim local audit log if over keep_lines
    if len(lines) > keep_lines:
        kept = lines[-keep_lines:]
        AUDIT_LOG.write_text("\n".join(kept) + "\n", encoding="utf-8")
        trimmed = len(lines) - keep_lines
        console.print(f"  Trimmed local log: removed {trimmed} old entries, kept {keep_lines}")
    else:
        console.print(f"  Local log retained: {len(lines)} entries (under {keep_lines} limit)")

    # List recent backups in Drive
    try:
        files = list_files("audit")
        console.print(f"\n  Backups in Drive ({len(files)} total):")
        for f in files[:5]:
            console.print(f"    {f['name']}")
        if len(files) > 5:
            console.print(f"    ... and {len(files) - 5} more")
    except Exception:
        pass

    audit_log("backup_completed", student_id="system", feature="backup",
              detail=f"file={backup_name} entries={len(lines)}")

    console.print(f"\n  [green]Backup complete.[/green]\n")


def main() -> None:
    keep = DEFAULT_KEEP_LINES
    if "--keep" in sys.argv:
        idx = sys.argv.index("--keep")
        if idx + 1 < len(sys.argv):
            try:
                keep = int(sys.argv[idx + 1])
            except ValueError:
                pass

    run_backup(keep)


if __name__ == "__main__":
    main()
