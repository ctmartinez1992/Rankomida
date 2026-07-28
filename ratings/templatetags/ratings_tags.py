from django import template

register = template.Library()


@register.filter
def score_as_percentage(value):
    """Convert a 1–10 score to a percentage string with 2 decimal places.

    Returns "–" for None or zero (no data).
    """
    if not value:
        return "–"
    return f"{float(value) / 10 * 100:.2f}%"
