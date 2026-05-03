#!/usr/bin/env python3
"""Shared Google Drive wrapper — all Drive file operations in the SNEC platform go through here.

Usage (from other tools):
    from tools.shared.gdrive import upload_file, download_file, list_files

Self-test:
    python tools/shared/gdrive.py
"""

import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
import io

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
load_dotenv(PROJECT_ROOT / ".env")

TOKEN_FILE = PROJECT_ROOT / "token.json"
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.file",
]

FOLDER_KEYS = {
    "cases": "GOOGLE_FOLDER_CASES",
    "images": "GOOGLE_FOLDER_IMAGES",
    "audit": "GOOGLE_FOLDER_AUDIT",
}

_service = None


def _get_service():
    """Return authenticated Drive service, reusing connection if open."""
    global _service

    if _service is not None:
        return _service

    if not TOKEN_FILE.exists():
        raise RuntimeError(
            "token.json not found. "
            "Run python tools/shared/infrastructure_bootstrap.py to authenticate."
        )

    creds = Credentials.from_authorized_user_file(str(TOKEN_FILE), SCOPES)
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
        TOKEN_FILE.write_text(creds.to_json(), encoding="utf-8")

    _service = build("drive", "v3", credentials=creds, cache_discovery=False)
    return _service


def _get_folder_id(folder_key: str) -> str:
    """Resolve a folder key (cases/images/audit) to a Drive folder ID from .env."""
    env_var = FOLDER_KEYS.get(folder_key)
    if not env_var:
        raise ValueError(
            f"Unknown folder key '{folder_key}'. Valid keys: {list(FOLDER_KEYS)}"
        )
    folder_id = os.getenv(env_var, "").strip()
    if not folder_id:
        raise RuntimeError(
            f"{env_var} not set in .env. "
            "Run python tools/shared/infrastructure_bootstrap.py first."
        )
    return folder_id


def upload_file(local_path: str | Path, folder_key: str) -> str:
    """
    Upload a local file to the specified Drive folder.

    Args:
        local_path:  Path to the local file to upload.
        folder_key:  "cases", "images", or "audit"

    Returns:
        The Drive file ID of the uploaded file.
    """
    local_path = Path(local_path)
    if not local_path.exists():
        raise FileNotFoundError(f"File not found: {local_path}")

    folder_id = _get_folder_id(folder_key)
    svc = _get_service()

    metadata = {
        "name": local_path.name,
        "parents": [folder_id],
    }
    media = MediaFileUpload(str(local_path), resumable=False)
    result = svc.files().create(
        body=metadata, media_body=media, fields="id"
    ).execute()
    return result["id"]


def download_file(file_id: str, local_path: str | Path) -> Path:
    """
    Download a Drive file by its ID to a local path.

    Args:
        file_id:    Drive file ID.
        local_path: Where to save the file locally.

    Returns:
        Path to the downloaded file.
    """
    local_path = Path(local_path)
    local_path.parent.mkdir(parents=True, exist_ok=True)

    svc = _get_service()
    request = svc.files().get_media(fileId=file_id)

    with local_path.open("wb") as f:
        downloader = MediaIoBaseDownload(f, request)
        done = False
        while not done:
            _, done = downloader.next_chunk()

    return local_path


def list_files(folder_key: str) -> list[dict]:
    """
    List all files in a Drive folder.

    Args:
        folder_key: "cases", "images", or "audit"

    Returns:
        List of dicts with keys: id, name, mimeType, createdTime
    """
    folder_id = _get_folder_id(folder_key)
    svc = _get_service()

    results = svc.files().list(
        q=f"'{folder_id}' in parents and trashed=false",
        fields="files(id, name, mimeType, createdTime)",
        orderBy="createdTime desc",
    ).execute()

    return results.get("files", [])


def delete_file(file_id: str) -> None:
    """Delete a Drive file by ID. Used for test cleanup."""
    _get_service().files().delete(fileId=file_id).execute()


if __name__ == "__main__":
    print("Testing gdrive.py...\n")

    # Create a temp test file
    test_file = PROJECT_ROOT / ".tmp" / "gdrive_test.txt"
    test_file.write_text("gdrive self-test content", encoding="utf-8")

    # Upload
    print("  Uploading test file to snec_audit/...")
    file_id = upload_file(test_file, "audit")
    print(f"  [OK] Uploaded. File ID: {file_id}")

    # List
    print("  Listing files in snec_audit/...")
    files = list_files("audit")
    names = [f["name"] for f in files]
    assert "gdrive_test.txt" in names, f"Test file not found in listing: {names}"
    print(f"  [OK] Found in listing: {names[:3]}")

    # Download
    download_path = PROJECT_ROOT / ".tmp" / "gdrive_test_download.txt"
    print("  Downloading file back...")
    download_file(file_id, download_path)
    content = download_path.read_text(encoding="utf-8")
    assert content == "gdrive self-test content"
    print(f"  [OK] Downloaded content matches.")

    # Clean up
    print("  Deleting test file from Drive...")
    delete_file(file_id)
    test_file.unlink(missing_ok=True)
    download_path.unlink(missing_ok=True)
    print("  [OK] Cleaned up.")

    print("\n  [PASS] gdrive.py working correctly.")
    sys.exit(0)
