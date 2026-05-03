#!/usr/bin/env python3
"""Agent 2: Infrastructure Bootstrap - creates all Google Sheets and Drive folders for the SNEC platform.

Usage:
    python tools/shared/infrastructure_bootstrap.py

What it does:
    1. Runs Google OAuth flow (opens browser once, saves token.json for future runs)
    2. Creates a Google Spreadsheet named 'SNEC AI Platform' with 6 sheet tabs
    3. Creates 3 Google Drive folders (snec_cases, snec_images, snec_audit)
    4. Writes the IDs of created resources into .env so other tools can find them
"""

import json
import sys
from pathlib import Path

from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
CREDENTIALS_FILE = PROJECT_ROOT / "credentials.json"
TOKEN_FILE = PROJECT_ROOT / "token.json"
ENV_FILE = PROJECT_ROOT / ".env"

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.file",
]

SPREADSHEET_NAME = "SNEC AI Platform"

# Sheet tabs and their column headers
SHEETS: list[tuple[str, list[str]]] = [
    ("snec_sessions", [
        "session_id", "student_id", "timestamp", "topic",
        "summary", "token_count", "model",
    ]),
    ("snec_flashcards", [
        "card_id", "student_id", "front", "back", "topic_tag",
        "easiness_factor", "interval_days", "repetition_count",
        "next_due_date", "last_reviewed", "created_from_session_id",
    ]),
    ("snec_case_results", [
        "result_id", "student_id", "case_id", "timestamp",
        "history_score", "investigations_score", "diagnosis_score",
        "management_score", "total_score", "feedback_summary",
    ]),
    ("snec_image_results", [
        "result_id", "student_id", "image_id", "timestamp", "modality",
        "student_description", "score", "correct_findings", "missed_findings",
    ]),
    ("snec_api_usage", [
        "timestamp", "feature", "model",
        "input_tokens", "output_tokens", "cached_tokens", "estimated_cost_usd",
    ]),
    ("snec_consent", [
        "student_id", "student_name", "email",
        "consent_date", "pdpa_version", "withdrawn_date",
    ]),
]

DRIVE_FOLDERS = ["snec_cases", "snec_images", "snec_audit"]

console = Console()


# ---------------------------------------------------------------------------
# Auth
# ---------------------------------------------------------------------------

def get_credentials() -> Credentials:
    """Run OAuth flow or refresh existing token."""
    creds = None

    if TOKEN_FILE.exists():
        creds = Credentials.from_authorized_user_file(str(TOKEN_FILE), SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            console.print("  Refreshing existing token...")
            creds.refresh(Request())
        else:
            console.print("  Opening browser for Google login...")
            console.print("  [dim]Grant access to Google Sheets and Drive when prompted.[/dim]\n")
            flow = InstalledAppFlow.from_client_secrets_file(str(CREDENTIALS_FILE), SCOPES)
            creds = flow.run_local_server(port=0)

        TOKEN_FILE.write_text(creds.to_json(), encoding="utf-8")
        console.print("  [green]token.json saved.[/green]\n")

    return creds


# ---------------------------------------------------------------------------
# Sheets
# ---------------------------------------------------------------------------

def find_existing_spreadsheet(sheets_svc, name: str) -> str | None:
    """Return spreadsheet ID if one with this name already exists, else None."""
    result = sheets_svc.spreadsheets().list(pageSize=50).execute()
    for item in result.get("files", []):
        if item.get("name") == name:
            return item["id"]
    return None


def create_spreadsheet(sheets_svc, drive_svc) -> tuple[str, bool]:
    """
    Create the SNEC AI Platform spreadsheet with all 6 tabs.
    Returns (spreadsheet_id, was_created). If it already exists, returns existing ID.
    """
    # Check Drive for existing spreadsheet by name
    query = f"name='{SPREADSHEET_NAME}' and mimeType='application/vnd.google-apps.spreadsheet' and trashed=false"
    existing = drive_svc.files().list(q=query, fields="files(id,name)").execute()
    files = existing.get("files", [])
    if files:
        return files[0]["id"], False

    # Build the spreadsheet body with all sheets defined upfront
    sheet_defs = [{"properties": {"title": name}} for name, _ in SHEETS]
    body = {
        "properties": {"title": SPREADSHEET_NAME},
        "sheets": sheet_defs,
    }
    result = sheets_svc.spreadsheets().create(body=body).execute()
    spreadsheet_id = result["spreadsheetId"]

    # Write headers to each sheet
    data = []
    for sheet_name, headers in SHEETS:
        data.append({
            "range": f"{sheet_name}!A1",
            "values": [headers],
        })

    sheets_svc.spreadsheets().values().batchUpdate(
        spreadsheetId=spreadsheet_id,
        body={"valueInputOption": "RAW", "data": data},
    ).execute()

    # Bold the header rows
    bold_requests = []
    sheet_list = sheets_svc.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
    sheet_id_map = {s["properties"]["title"]: s["properties"]["sheetId"] for s in sheet_list["sheets"]}

    for sheet_name, _ in SHEETS:
        sid = sheet_id_map.get(sheet_name)
        if sid is not None:
            bold_requests.append({
                "repeatCell": {
                    "range": {"sheetId": sid, "startRowIndex": 0, "endRowIndex": 1},
                    "cell": {"userEnteredFormat": {"textFormat": {"bold": True}}},
                    "fields": "userEnteredFormat.textFormat.bold",
                }
            })

    if bold_requests:
        sheets_svc.spreadsheets().batchUpdate(
            spreadsheetId=spreadsheet_id,
            body={"requests": bold_requests},
        ).execute()

    return spreadsheet_id, True


# ---------------------------------------------------------------------------
# Drive
# ---------------------------------------------------------------------------

def get_or_create_folder(drive_svc, name: str) -> tuple[str, bool]:
    """Return (folder_id, was_created). Reuses existing folder if found."""
    query = f"name='{name}' and mimeType='application/vnd.google-apps.folder' and trashed=false"
    result = drive_svc.files().list(q=query, fields="files(id,name)").execute()
    files = result.get("files", [])
    if files:
        return files[0]["id"], False

    metadata = {
        "name": name,
        "mimeType": "application/vnd.google-apps.folder",
    }
    folder = drive_svc.files().create(body=metadata, fields="id").execute()
    return folder["id"], True


# ---------------------------------------------------------------------------
# .env writer
# ---------------------------------------------------------------------------

def write_env_ids(spreadsheet_id: str, folder_ids: dict[str, str]) -> None:
    """Append or update resource IDs in .env file."""
    if not ENV_FILE.exists():
        console.print(f"  [yellow]Warning: .env not found. Creating it now.[/yellow]")
        ENV_FILE.write_text("", encoding="utf-8")

    existing = ENV_FILE.read_text(encoding="utf-8")

    new_entries = {
        "GOOGLE_SPREADSHEET_ID": spreadsheet_id,
        "GOOGLE_FOLDER_CASES": folder_ids.get("snec_cases", ""),
        "GOOGLE_FOLDER_IMAGES": folder_ids.get("snec_images", ""),
        "GOOGLE_FOLDER_AUDIT": folder_ids.get("snec_audit", ""),
    }

    lines = existing.splitlines()
    updated_keys: set[str] = set()
    new_lines: list[str] = []

    for line in lines:
        key = line.split("=")[0].strip() if "=" in line else ""
        if key in new_entries:
            new_lines.append(f"{key}={new_entries[key]}")
            updated_keys.add(key)
        else:
            new_lines.append(line)

    # Append any keys not already in the file
    for key, value in new_entries.items():
        if key not in updated_keys:
            new_lines.append(f"{key}={value}")

    ENV_FILE.write_text("\n".join(new_lines) + "\n", encoding="utf-8")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    console.print(Panel(
        "Sets up Google Sheets and Drive folders for the SNEC AI Platform.",
        title="Agent 2 - Infrastructure Bootstrap",
        border_style="blue",
    ))

    # Check credentials exist
    if not CREDENTIALS_FILE.exists():
        console.print("[bold red]ERROR:[/bold red] credentials.json not found.")
        console.print("Download it from GCP Console -> APIs & Services -> Credentials -> OAuth 2.0 Client IDs")
        sys.exit(1)

    # Step 1: Auth
    console.print("[bold]Step 1/3:[/bold] Authenticating with Google...")
    try:
        creds = get_credentials()
        console.print("  [green]Authentication successful.[/green]\n")
    except Exception as e:
        console.print(f"[bold red]Auth failed:[/bold red] {e}")
        console.print("Delete token.json and try again.")
        sys.exit(1)

    sheets_svc = build("sheets", "v4", credentials=creds, cache_discovery=False)
    drive_svc = build("drive", "v3", credentials=creds, cache_discovery=False)

    # Step 2: Spreadsheet
    console.print("[bold]Step 2/3:[/bold] Creating Google Spreadsheet...")
    try:
        spreadsheet_id, created = create_spreadsheet(sheets_svc, drive_svc)
        status = "[green]Created[/green]" if created else "[yellow]Already exists - reusing[/yellow]"
        console.print(f"  {status}: {SPREADSHEET_NAME}")
        console.print(f"  ID: {spreadsheet_id}")
        if created:
            for sheet_name, headers in SHEETS:
                console.print(f"    + {sheet_name} ({len(headers)} columns)")
        console.print()
    except HttpError as e:
        console.print(f"[bold red]Sheets error:[/bold red] {e}")
        sys.exit(1)

    # Step 3: Drive folders
    console.print("[bold]Step 3/3:[/bold] Creating Google Drive folders...")
    folder_ids: dict[str, str] = {}
    try:
        for folder_name in DRIVE_FOLDERS:
            folder_id, created = get_or_create_folder(drive_svc, folder_name)
            folder_ids[folder_name] = folder_id
            status = "[green]Created[/green]" if created else "[yellow]Already exists - reusing[/yellow]"
            console.print(f"  {status}: {folder_name}/ (ID: {folder_id})")
        console.print()
    except HttpError as e:
        console.print(f"[bold red]Drive error:[/bold red] {e}")
        sys.exit(1)

    # Write IDs to .env
    write_env_ids(spreadsheet_id, folder_ids)
    console.print("[green]Resource IDs written to .env[/green]\n")

    # Summary table
    table = Table(show_header=True, header_style="bold", box=None, padding=(0, 1))
    table.add_column("Resource")
    table.add_column("Name")
    table.add_column("ID")

    table.add_row("Spreadsheet", SPREADSHEET_NAME, spreadsheet_id)
    for name, fid in folder_ids.items():
        table.add_row("Drive folder", f"{name}/", fid)

    console.print(Panel(table, title="Created Resources", border_style="green"))
    console.print("\n  Next step: [bold]python tools/shared/env_validator.py[/bold]\n")


if __name__ == "__main__":
    main()
