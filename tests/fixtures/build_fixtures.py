"""Generate synthetic .eml fixtures for tests.

Run from repo root:  python tests/fixtures/build_fixtures.py

The fixtures imitate the structure of real newsletter emails
(table-based HTML layout, tracking-redirect links, "View in browser"
header, "Follow Us" / "Unsubscribe" footer) without using any
third-party copyrighted content.
"""
from __future__ import annotations

from email.message import EmailMessage
from email.utils import format_datetime
from datetime import datetime, timezone
from pathlib import Path

OUT = Path(__file__).parent

BLOOMBERG_HTML = """\
<html><body>
<table id="wrapper"><tr><td>

<!-- top chrome: brand strip + view-in-browser -->
<table><tr>
  <td><img src="https://example.invalid/pixel.gif" width="1" height="1"></td>
  <td><img src="https://example.invalid/sponsor-banner.png" alt="Sponsor"></td>
  <td><a href="https://links.message.bloomberg.com/s/c/OPAQUE_TOKEN_VIB">View in browser</a></td>
</tr></table>

<!-- article body -->
<table><tr><td>
  <h2>Test Newsletter Story</h2>
  <p>This is the opening paragraph of a synthetic newsletter, long enough to be
  picked up as the description by the first-paragraph heuristic in the converter.
  It also contains an inline <a href="https://links.message.bloomberg.com/s/c/OPAQUE_TOKEN_INLINE">tracker link</a>
  to confirm those are preserved verbatim in v1.</p>

  <p>A second paragraph with a <strong>bold phrase</strong> and an <em>italic phrase</em>.</p>

  <ul>
    <li>First bullet</li>
    <li>Second bullet</li>
  </ul>

  <h2>Second Section</h2>
  <p>Content under the second heading.</p>
</td></tr></table>

<!-- footer chrome -->
<table><tr><td>
  Follow Us
  <a href="https://links.message.bloomberg.com/s/c/OPAQUE_TWITTER"><img src="https://example.invalid/twitter.png"></a>
  <br>
  You received this message because you are subscribed to the Test newsletter.
  <br>
  <a href="https://links.message.bloomberg.com/s/c/OPAQUE_UNSUB">Unsubscribe</a>
  | Test Publisher Inc. 1 Test Street, Testville
</td></tr></table>

</td></tr></table>
</body></html>
"""

BLOOMBERG_TEXT = """\
Test Newsletter Story

This is the opening paragraph of a synthetic newsletter.

Follow Us | Unsubscribe
"""


def build_bloomberg_fixture() -> EmailMessage:
    msg = EmailMessage()
    msg["From"] = "Matt Levine <noreply@news.bloomberg.com>"
    msg["To"] = "test@example.invalid"
    msg["Subject"] = "Money Stuff: Test Newsletter Story"
    msg["Date"] = format_datetime(datetime(2026, 5, 4, 18, 11, 33, tzinfo=timezone.utc))
    msg["Message-ID"] = "<synthetic-1@example.invalid>"
    msg.set_content(BLOOMBERG_TEXT)
    msg.add_alternative(BLOOMBERG_HTML, subtype="html")
    return msg


def build_generic_fixture() -> EmailMessage:
    """A non-Bloomberg sender to exercise the generic fallback path."""
    msg = EmailMessage()
    msg["From"] = "Some Author <newsletter@example.invalid>"
    msg["To"] = "test@example.invalid"
    msg["Subject"] = "An Article About Things"
    msg["Date"] = format_datetime(datetime(2026, 5, 6, 12, 0, 0, tzinfo=timezone.utc))
    msg["Message-ID"] = "<synthetic-2@example.invalid>"
    msg.set_content("plain text fallback")
    msg.add_alternative(
        "<html><body><h2>An Article About Things</h2>"
        "<p>The opening paragraph contains enough prose to qualify as a description "
        "for the resulting Obsidian note's frontmatter field.</p>"
        "<p>Follow Us</p>"
        "</body></html>",
        subtype="html",
    )
    return msg


if __name__ == "__main__":
    (OUT / "bloomberg_money_stuff.eml").write_bytes(bytes(build_bloomberg_fixture()))
    (OUT / "generic_newsletter.eml").write_bytes(bytes(build_generic_fixture()))
    print(f"Wrote fixtures to {OUT}/")
