"""HTML pre-processing: strip tracking pixels, locate 'View in browser' URL, find article body bounds."""
from __future__ import annotations

import re

from bs4 import BeautifulSoup, Tag

VIB_TEXT = re.compile(r"view\s+(in|on)\s+(your\s+)?browser", re.I)


def find_view_in_browser_url(soup: BeautifulSoup) -> str | None:
    for a in soup.find_all("a"):
        if VIB_TEXT.search(a.get_text(" ", strip=True)):
            href = a.get("href", "").strip()
            return href or None
    return None


def is_tracker_redirect(url: str) -> bool:
    """True if the URL is opaque sender-side click tracking we can't decode without HTTP."""
    if not url:
        return True
    return any(
        host in url
        for host in (
            "links.message.bloomberg.com",
            "link.mail.bloombergbusiness.com",
            "click.email.bloomberg.com",
            "links.email.bloomberg.com",
        )
    )


def strip_tracking_pixels(soup: BeautifulSoup) -> None:
    for img in list(soup.find_all("img")):
        try:
            w = int(img.get("width", "0") or 0)
            h = int(img.get("height", "0") or 0)
        except ValueError:
            w = h = 0
        src = (img.get("src") or "").lower()
        if (w == 1 and h == 1) or "pixel" in src or "open?" in src or "track" in src:
            img.decompose()


def strip_scripts_and_styles(soup: BeautifulSoup) -> None:
    for el in soup.find_all(["script", "style", "meta", "link", "head"]):
        el.decompose()


def unwrap_layout_tables(soup: BeautifulSoup) -> None:
    """Bloomberg/Iterable use table-based email layout. Markdownify converts these
    to markdown tables, mangling the article. Replace table/tr/td with div so the
    content reads as normal block flow."""
    for tag_name in ("table", "tbody", "thead", "tfoot", "tr", "td", "th", "colgroup", "col", "center"):
        for el in soup.find_all(tag_name):
            el.name = "div"
            # drop layout-only attributes
            for attr in list(el.attrs):
                if attr in ("style", "class", "align", "valign", "bgcolor", "border", "cellpadding",
                            "cellspacing", "width", "height", "colspan", "rowspan", "role"):
                    del el.attrs[attr]


def preprocess(html: str) -> tuple[BeautifulSoup, str | None]:
    """Returns (cleaned soup, view-in-browser url or None)."""
    soup = BeautifulSoup(html, "html.parser")
    vib = find_view_in_browser_url(soup)
    strip_scripts_and_styles(soup)
    strip_tracking_pixels(soup)
    unwrap_layout_tables(soup)
    return soup, vib
