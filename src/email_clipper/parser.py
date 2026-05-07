"""Parse .eml file into a ParsedEmail dataclass."""
from __future__ import annotations

import email
from dataclasses import dataclass
from datetime import datetime
from email import policy
from email.utils import getaddresses, parsedate_to_datetime
from pathlib import Path


@dataclass
class ParsedEmail:
    subject: str
    from_email: str
    from_name: str
    date: datetime
    html_body: str | None
    text_body: str | None
    raw_path: Path


def parse_eml(path: Path) -> ParsedEmail:
    with open(path, "rb") as f:
        msg = email.message_from_binary_file(f, policy=policy.default)

    subject = (msg.get("Subject") or "").strip()

    from_header = msg.get("From") or ""
    addrs = getaddresses([from_header])
    from_name, from_email = (addrs[0] if addrs else ("", ""))

    date_header = msg.get("Date")
    date = parsedate_to_datetime(date_header) if date_header else datetime.now()

    html_body: str | None = None
    text_body: str | None = None
    for part in msg.walk():
        ctype = part.get_content_type()
        disp = part.get("Content-Disposition") or ""
        if "attachment" in disp.lower():
            continue
        if ctype == "text/html" and html_body is None:
            html_body = part.get_content()
        elif ctype == "text/plain" and text_body is None:
            text_body = part.get_content()

    return ParsedEmail(
        subject=subject,
        from_email=from_email,
        from_name=from_name,
        date=date,
        html_body=html_body,
        text_body=text_body,
        raw_path=path,
    )
