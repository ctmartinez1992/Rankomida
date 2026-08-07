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


@register.filter
def mul(value, arg):
    """Multiply value by arg. Used in templates for percentage conversion."""
    try:
        return float(value) * float(arg)
    except (TypeError, ValueError):
        return ""


@register.filter
def score_as_stars_pct(value):
    """Convert a 0–100 percentage to a star glyph string (10 points per half-star).

    Bracket mapping:
      96–100  → ★★★★★
      86–95   → ★★★★½☆
      76–85   → ★★★★☆☆
      66–75   → ★★★½☆☆
      56–65   → ★★★☆☆☆
      46–55   → ★★½☆☆☆
      36–45   → ★★☆☆☆☆
      26–35   → ★½☆☆☆☆
      16–25   → ★☆☆☆☆☆
      5–15    → ½☆☆☆☆☆
      0–4     → –

    Returns '–' for None or values outside 0–100.
    """
    if value is None:
        return "–"
    try:
        pct = float(value)
    except (TypeError, ValueError):
        return "–"
    if pct < 0 or pct > 100:
        return "–"

    if pct >= 96:
        half_stars = 10
    elif pct >= 86:
        half_stars = 9
    elif pct >= 76:
        half_stars = 8
    elif pct >= 66:
        half_stars = 7
    elif pct >= 56:
        half_stars = 6
    elif pct >= 46:
        half_stars = 5
    elif pct >= 36:
        half_stars = 4
    elif pct >= 26:
        half_stars = 3
    elif pct >= 16:
        half_stars = 2
    elif pct >= 5:
        half_stars = 1
    else:
        return "–"

    full_stars = half_stars // 2
    has_half = half_stars % 2 == 1
    empty_stars = _MAX_STARS - full_stars - (1 if has_half else 0)

    return "★" * full_stars + ("½" if has_half else "") + "☆" * empty_stars
