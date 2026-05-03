#!/usr/bin/env python3
"""Agent 22: Schema Migration — detects and repairs missing columns in Google Sheets.

Compares each sheet's current headers against the expected schema,
adds any missing columns, and reports changes. Safe to run repeatedly.

Usage:
    python tools/shared/schema_migration.py
    python tools/shared/schema_migration.py --dry-run    # show changes without applying
"""

import sys
from pathlib import Path

from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
load_dotenv(PROJECT_ROOT / ".env")
sys.path.insert(0, str(PROJECT_ROOT))

console = Console()

# Expected schema — source of truth for all sheet headers
EXPECTED_SCHEMA: dict[str, list[str]] = {
    "snec_sessions": [
        "session_id", "student_id", "timestamp", "topic",
        "summary", "token_count", "model",
    ],
    "snec_flashcards": [
        "card_id", "student_id", "front", "back", "topic_tag",
        "easiness_factor", "interval_days", "repetition_count",
        "next_due_date", "last_reviewed", "created_from_session_id",
    ],
    "snec_case_results": [
        "result_id", "student_id", "case_id", "timestamp",
        "history_score", "investigations_score", "diagnosis_score",
        "management_score", "total_score", "feedback_summary",
    ],
    "snec_image_results": [
        "result_id", "student_id", "image_id", "timestamp", "modality",
        "student_description", "score", "correct_findings", "missed_findings",
    ],
    "snec_api_usage": [
        "timestamp", "feature", "model",
        "input_tokens", "output_tokens", "cached_tokens", "estimated_cost_usd",
    ],
    "snec_consent": [
        "student_id", "student_name", "email",
        "consent_date", "pdpa_version", "withdrawn_date",
    ],
}


def check_and_migrate(dry_run: bool = False) -> None:
    from tools.shared.gsheets import _get_spreadsheet
    from tools.shared.audit_log import log as audit_log

    ss = _get_spreadsheet()

    table = Table(show_header=True, header_style="bold", box=None, padding=(0, 1))
    table.add_column("Sheet", min_width=22)
    table.add_column("Status", width=8)
    table.add_column("Detail")

    any_changes = False

    for sheet_name, expected_cols in EXPECTED_SCHEMA.items():
        try:
            ws = ss.worksheet(sheet_name)
        except Exception:
            table.add_row(sheet_name, "[red]MISSING[/red]", "Sheet tab not found — run bootstrap")
            continue

        current_headers = ws.row_values(1)
        missing_cols = [c for c in expected_cols if c not in current_headers]

        if not missing_cols:
            table.add_row(sheet_name, "[green]OK[/green]",
                          f"{len(current_headers)} columns — schema matches")
            continue

        any_changes = True
        detail = f"Adding: {', '.join(missing_cols)}"

        if dry_run:
            table.add_row(sheet_name, "[yellow]WOULD ADD[/yellow]", detail)
            continue

        # Add missing columns to the right of existing headers
        next_col = len(current_headers) + 1
        for col_name in missing_cols:
            ws.update_cell(1, next_col, col_name)
            next_col += 1

        # Bold the newly added headers
        try:
            import gspread
            ss_data = ss.fetch_sheet_metadata()
            sheet_id = next(
                s["properties"]["sheetId"]
                for s in ss_data["sheets"]
                if s["properties"]["title"] == sheet_name
            )
            from tools.shared.gsheets import _get_spreadsheet as _gs
            body = {
                "requests": [{
                    "repeatCell": {
                        "range": {"sheetId": sheet_id, "startRowIndex": 0, "endRowIndex": 1},
                        "cell": {"userEnteredFormat": {"textFormat": {"bold": True}}},
                        "fields": "userEnteredFormat.textFormat.bold",
                    }
                }]
            }
            ss.batch_update(body)
        except Exception:
            pass

        table.add_row(sheet_name, "[green]UPDATED[/green]", detail)
        audit_log("schema_migrated", student_id="system", feature="migration",
                  detail=f"sheet={sheet_name} added={missing_cols}")

    console.print(Panel(
        table,
        title=f"Agent 22 - Schema Migration{'(dry run)' if dry_run else ''}",
        border_style="blue",
    ))

    if dry_run and any_changes:
        console.print("[yellow]Dry run complete. Run without --dry-run to apply changes.[/yellow]\n")
    elif any_changes:
        console.print("[green]Migration complete.[/green]\n")
    else:
        console.print("[green]All sheets match expected schema. No changes needed.[/green]\n")


def main() -> None:
    dry_run = "--dry-run" in sys.argv
    check_and_migrate(dry_run)


if __name__ == "__main__":
    main()
