"""Per-sender configs. Maps From-address to publication-specific rules."""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class SenderConfig:
    name: str
    subject_prefix: str = ""
    tags: list[str] = field(default_factory=lambda: ["clippings"])
    author_override: str | None = None
    url_builder: str | None = None


SENDERS: dict[str, SenderConfig] = {
    "noreply@news.bloomberg.com": SenderConfig(
        name="Money Stuff",
        subject_prefix="Money Stuff: ",
        tags=["clippings", "MoneyStuff", "bloomberg"],
        author_override="Matt Levine",
        url_builder="bloomberg_money_stuff",
    ),
}


def lookup(from_email: str) -> SenderConfig:
    return SENDERS.get(from_email.lower().strip(), SenderConfig(name="Generic"))
