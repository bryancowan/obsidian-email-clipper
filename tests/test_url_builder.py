from datetime import datetime

from email_clipper.url_builder import bloomberg_money_stuff


def test_gamestop_slug():
    url = bloomberg_money_stuff("GameStop Doesn’t Have Enough Stock", datetime(2026, 5, 4))
    assert url == "https://www.bloomberg.com/opinion/newsletters/2026-05-04/gamestop-doesn-t-have-enough-stock"


def test_robots_slug():
    url = bloomberg_money_stuff("The Robots Make the Predictions", datetime(2026, 4, 28))
    assert url == "https://www.bloomberg.com/opinion/newsletters/2026-04-28/the-robots-make-the-predictions"


def test_apostrophe_variants_collapse_to_hyphen():
    # straight apostrophe
    assert "doesn-t" in bloomberg_money_stuff("X Doesn't Y", datetime(2026, 1, 1))
    # curly opening
    assert "doesn-t" in bloomberg_money_stuff("X Doesn‘t Y", datetime(2026, 1, 1))
