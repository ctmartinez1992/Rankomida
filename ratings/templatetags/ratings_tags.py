from decimal import Decimal, InvalidOperation

from django import template

register = template.Library()

_MAX_STARS = 5


@register.filter
def score_as_stars(value):
    """Convert a 1–5 score (0.5 steps) to a star glyph string, e.g. '★★★½☆'.

    Returns '–' for None, zero, or values outside the 1–5 range.
    """
    if not value:
        return "–"
    try:
        score = Decimal(str(value))
    except (InvalidOperation, TypeError):
        return "–"
    if score < Decimal("0.5") or score > Decimal("5"):
        return "–"

    full_stars = int(score)
    has_half = (score - full_stars) >= Decimal("0.5")
    empty_stars = _MAX_STARS - full_stars - (1 if has_half else 0)

    return "★" * full_stars + ("½" if has_half else "") + "☆" * empty_stars
