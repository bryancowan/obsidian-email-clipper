"""CLI entry: convert .eml file to Obsidian note."""
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

from . import extract, frontmatter, markdown, parser, senders, url_builder, writer


def _default_vault() -> Path:
    """Default output directory. Resolved at call time so $HOME / env are honored."""
    env = os.environ.get("EMAIL_CLIPPER_VAULT")
    if env:
        return Path(env).expanduser()
    return Path.home() / "Obsidian" / "Reading List"


def convert(eml_path: Path, vault_dir: Path) -> Path:
    parsed = parser.parse_eml(eml_path)
    sender = senders.lookup(parsed.from_email)

    title = parsed.subject
    if sender.subject_prefix and title.startswith(sender.subject_prefix):
        title = title[len(sender.subject_prefix):].strip()

    author = sender.author_override or parsed.from_name or parsed.from_email
    authors = [author]

    if not parsed.html_body:
        raise RuntimeError(f"No HTML body found in {eml_path}; only plain-text emails not supported in v1")

    soup, vib_url = extract.preprocess(parsed.html_body)

    # Pick source URL: prefer non-tracker VIB; otherwise use sender's url_builder
    source = ""
    if vib_url and not extract.is_tracker_redirect(vib_url):
        source = vib_url
    elif sender.url_builder:
        source = url_builder.build(sender.url_builder, title, parsed.date)

    body = markdown.html_to_markdown(soup)

    description = _first_paragraph(body)

    fm = frontmatter.build(
        title=title,
        source=source,
        authors=authors,
        published=parsed.date.date(),
        created=frontmatter.now_local_date(),
        description=description,
        tags=sender.tags,
    )
    note = fm + body

    fname = writer.filename_for(title)
    return writer.write_note(vault_dir, fname, note)


def _first_paragraph(md_body: str) -> str:
    """Pick the first prose paragraph: skip headings, image-only blocks, and
    blocks whose content is dominated by markdown link/image syntax."""
    import re

    for raw in md_body.split("\n\n"):
        block = " ".join(raw.split())
        if not block:
            continue
        if block.startswith("#"):
            continue
        # Skip blocks that are just images or image-links
        if re.match(r"^\s*\[?!\[", block):
            continue
        # Strip markdown link/image syntax to test if any prose remains
        stripped = re.sub(r"!\[[^\]]*\]\([^)]*\)", "", block)
        stripped = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", stripped).strip()
        if len(stripped) < 40:
            continue
        return stripped
    return ""


def main(argv: list[str] | None = None) -> int:
    default_vault = _default_vault()
    ap = argparse.ArgumentParser(description="Convert .eml file to Obsidian note")
    ap.add_argument("eml", type=Path, help="Path to .eml file")
    ap.add_argument(
        "--vault",
        type=Path,
        default=default_vault,
        help=f"Reading List directory (default: {default_vault}, "
             "or $EMAIL_CLIPPER_VAULT)",
    )
    args = ap.parse_args(argv)

    if not args.eml.is_file():
        print(f"error: not a file: {args.eml}", file=sys.stderr)
        return 2

    out = convert(args.eml, args.vault)
    print(out)
    return 0
