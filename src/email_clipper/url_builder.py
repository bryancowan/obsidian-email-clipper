"""Construct canonical newsletter URLs when none is found in the email."""
from __future__ import annotations

from datetime import datetime

from slugify import slugify


def bloomberg_money_stuff(title: str, date: datetime) -> str:
    """
    Construct the canonical Bloomberg Money Stuff URL from the title and email date.

    Bloomberg's slug format is lowercase, ASCII-folded, with apostrophes replaced
    by hyphens and whitespace collapsed.

        "GameStop Doesn't Have Enough Stock", 2026-05-04
        -> https://www.bloomberg.com/opinion/newsletters/2026-05-04/gamestop-doesn-t-have-enough-stock
    """
    date_str = date.strftime("%Y-%m-%d")
    # Bloomberg replaces apostrophes (straight + curly) with hyphens, not strips them
    normalized = title.replace("’", "-").replace("‘", "-").replace("'", "-")
    slug = slugify(normalized, lowercase=True)
    return f"https://www.bloomberg.com/opinion/newsletters/{date_str}/{slug}"


BUILDERS = {
    "bloomberg_money_stuff": bloomberg_money_stuff,
}


def build(builder_name: str, title: str, date: datetime) -> str:
    return BUILDERS[builder_name](title, date)
