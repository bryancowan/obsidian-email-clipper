"""HTML → Markdown conversion + post-trim of newsletter chrome."""
from __future__ import annotations

import re

from bs4 import BeautifulSoup
from markdownify import markdownify

# Lines that mark the START of the trailing footer block.
# Each is matched at the start of a line (after stripping). Earliest match wins.
FOOTER_MARKERS = [
    r"^Follow Us\b",
    r"You received this message because",
    r"^Unsubscribe\b",
    r"Like getting this newsletter\?",
    r"Want to sponsor this newsletter\?",
    r"Bloomberg L\.P\.\s+\d",
    r"^\[!\[Listen to the Money Stuff Podcast\]",  # Money Stuff trailing podcast banner
    r"^\*\*Follow topics and authors\*\*",         # The Verge-style trailing footer
]


def html_to_markdown(soup: BeautifulSoup) -> str:
    md = markdownify(
        str(soup),
        heading_style="ATX",
        bullets="-",
        escape_asterisks=False,
        escape_underscores=False,
        strip=["meta", "link"],
    )
    return _post_clean(md)


def _post_clean(md: str) -> str:
    md = _trim_leading_chrome(md)
    md = _trim_trailing_footer(md)
    md = _collapse_blank_lines(md)
    return md.strip() + "\n"


def _trim_leading_chrome(md: str) -> str:
    """Drop everything before the first ATX h2 heading, which is the article title
    in newsletter-style emails (Bloomberg, etc.). Preserves the heading itself."""
    lines = md.splitlines()
    for i, line in enumerate(lines):
        if line.startswith("## "):
            return "\n".join(lines[i:])
    return md


def _trim_trailing_footer(md: str) -> str:
    """Drop everything from the first footer-marker line onward."""
    lines = md.splitlines()
    pat = re.compile("|".join(FOOTER_MARKERS), re.I | re.M)
    for i, line in enumerate(lines):
        if pat.search(line.strip()):
            return "\n".join(lines[:i])
    return md


def _collapse_blank_lines(md: str) -> str:
    return re.sub(r"\n{3,}", "\n\n", md)
