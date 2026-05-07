"""Filename formatting + vault write."""
from __future__ import annotations

import re
from datetime import datetime
from pathlib import Path


def filename_for(title: str, when: datetime | None = None) -> str:
    """Match Web Clipper format: '{title} - {YYYY-MM-DDTHHmmss±ZZZZ}.md'.

    Example: 'GameStop - 2026-05-06T234300-0500.md'
    """
    if when is None:
        when = datetime.now().astimezone()
    # ISO-like timestamp, no colons (filesystem-safe), with timezone
    ts = when.strftime("%Y-%m-%dT%H%M%S%z")
    safe_title = _sanitize_for_filename(title)
    return f"{safe_title} - {ts}.md"


def _sanitize_for_filename(title: str) -> str:
    # Drop characters that conflict with macOS / Obsidian filenames
    cleaned = re.sub(r'[\/\\:*?"<>|]', "", title)
    return cleaned.strip()


def write_note(vault_dir: Path, filename: str, content: str) -> Path:
    vault_dir.mkdir(parents=True, exist_ok=True)
    path = vault_dir / filename
    path.write_text(content, encoding="utf-8")
    return path
