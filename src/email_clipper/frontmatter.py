"""Build YAML frontmatter matching the Obsidian Web Clipper default template exactly."""
from __future__ import annotations

from datetime import date, datetime


def _q(s: str) -> str:
    """Double-quote a YAML scalar, escaping internal double-quotes and backslashes."""
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'


def build(
    *,
    title: str,
    source: str,
    authors: list[str],
    published: date,
    created: date,
    description: str,
    tags: list[str],
) -> str:
    """Returns frontmatter (with --- fences) matching the Web Clipper format used in
    existing Reading List notes: quoted strings, bare ISO dates, empty `note:`/`related:`.
    """
    lines = ["---"]
    lines.append(f"title: {_q(title)}")
    lines.append(f"source: {_q(source)}")
    lines.append("author:")
    for a in authors:
        lines.append(f"  - {_q(f'[[{a}]]')}")
    lines.append(f"published: {published.isoformat()}")
    lines.append(f"created: {created.isoformat()}")
    lines.append(f"description: {_q(description)}")
    lines.append("tags:")
    for t in tags:
        lines.append(f"  - {_q(t)}")
    lines.append('status: "Unread"')
    lines.append("note:")
    lines.append("related:")
    lines.append("---")
    return "\n".join(lines) + "\n"


def now_local_date() -> date:
    return datetime.now().astimezone().date()
