"""Google Sheets access via gspread + Application Default Credentials."""

from __future__ import annotations

import logging
import threading
from typing import Any, Dict, List, Optional

import gspread
from google.auth import default
from google.auth.exceptions import DefaultCredentialsError

from app.config import Settings, get_settings

log = logging.getLogger(__name__)

_client: Optional[gspread.Client] = None
_client_lock = threading.Lock()


def _build_client() -> gspread.Client:
    try:
        creds, _ = default(
            scopes=[
                "https://www.googleapis.com/auth/spreadsheets",
                "https://www.googleapis.com/auth/drive",
            ]
        )
    except DefaultCredentialsError as exc:
        raise RuntimeError(
            "Google credentials not found. Set GOOGLE_APPLICATION_CREDENTIALS or use Cloud Run SA."
        ) from exc
    return gspread.authorize(creds)


def get_gspread_client() -> gspread.Client:
    global _client
    with _client_lock:
        if _client is None:
            _client = _build_client()
        return _client


def open_spreadsheet(settings: Optional[Settings] = None):
    settings = settings or get_settings()
    if not settings.spreadsheet_id:
        raise RuntimeError("SPREADSHEET_ID is not configured")
    return get_gspread_client().open_by_key(settings.spreadsheet_id)


def get_worksheet(name: str, settings: Optional[Settings] = None):
    return open_spreadsheet(settings).worksheet(name)


def header_map(row: List[str]) -> Dict[str, int]:
    return {h.strip(): i for i, h in enumerate(row) if h and h.strip()}


def row_to_dict(headers: List[str], row: List[Any]) -> Dict[str, str]:
    out: Dict[str, str] = {}
    for i, h in enumerate(headers):
        if not h:
            continue
        out[h.strip()] = (row[i] if i < len(row) else "") or ""
    return out


def append_row(sheet_name: str, values: List[Any], settings: Optional[Settings] = None) -> None:
    ws = get_worksheet(sheet_name, settings)
    ws.append_row(values, value_input_option="USER_ENTERED")


def get_all_records(sheet_name: str, settings: Optional[Settings] = None) -> List[Dict[str, str]]:
    ws = get_worksheet(sheet_name, settings)
    values = ws.get_all_values()
    if not values:
        return []
    headers = values[0]
    return [row_to_dict(headers, row) for row in values[1:] if any(cell.strip() for cell in row)]


def find_row_index(
    sheet_name: str,
    column: str,
    value: str,
    settings: Optional[Settings] = None,
) -> Optional[int]:
    ws = get_worksheet(sheet_name, settings)
    values = ws.get_all_values()
    if not values:
        return None
    hmap = header_map(values[0])
    col_idx = hmap.get(column)
    if col_idx is None:
        return None
    target = value.strip()
    for i, row in enumerate(values[1:], start=2):
        if col_idx < len(row) and (row[col_idx] or "").strip() == target:
            return i
    return None
