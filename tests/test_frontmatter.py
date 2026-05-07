from datetime import date

from email_clipper.frontmatter import build


def test_frontmatter_matches_template_shape():
    fm = build(
        title="GameStop Doesn’t Have Enough Stock",
        source="https://www.bloomberg.com/opinion/newsletters/2026-05-04/gamestop-doesn-t-have-enough-stock",
        authors=["Matt Levine"],
        published=date(2026, 5, 4),
        created=date(2026, 5, 7),
        description="Some prose description",
        tags=["clippings", "MoneyStuff", "bloomberg"],
    )
    expected = (
        '---\n'
        'title: "GameStop Doesn’t Have Enough Stock"\n'
        'source: "https://www.bloomberg.com/opinion/newsletters/2026-05-04/gamestop-doesn-t-have-enough-stock"\n'
        'author:\n'
        '  - "[[Matt Levine]]"\n'
        'published: 2026-05-04\n'
        'created: 2026-05-07\n'
        'description: "Some prose description"\n'
        'tags:\n'
        '  - "clippings"\n'
        '  - "MoneyStuff"\n'
        '  - "bloomberg"\n'
        'status: "Unread"\n'
        'note:\n'
        'related:\n'
        '---\n'
    )
    assert fm == expected


def test_quotes_and_backslashes_escaped():
    fm = build(
        title='He said "hello" \\path',
        source="",
        authors=["A"],
        published=date(2026, 1, 1),
        created=date(2026, 1, 1),
        description="",
        tags=["clippings"],
    )
    assert 'title: "He said \\"hello\\" \\\\path"' in fm
