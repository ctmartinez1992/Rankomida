from decimal import Decimal

from django import forms
from django.utils.html import mark_safe

HALF_STAR_CHOICES = [
    Decimal("0.5"),
    Decimal("1"),
    Decimal("1.5"),
    Decimal("2"),
    Decimal("2.5"),
    Decimal("3"),
    Decimal("3.5"),
    Decimal("4"),
    Decimal("4.5"),
    Decimal("5"),
]

# Star positions from 5 down to 1, each with a full (right half) + half (left half) pair.
# DOM is rendered high→low so that CSS `input:checked ~ label` fills visually leftward.
_STAR_PAIRS = [(5, 4.5), (4, 3.5), (3, 2.5), (2, 1.5), (1, 0.5)]


class StarRatingWidget(forms.Widget):
    """
    CSS-only half-star rating widget (0.5–5 in 0.5 steps).

    Renders radio inputs in reverse DOM order (5→0.5) inside a flex-direction:row-reverse
    container. Each star position has a full-value radio (right half) and a half-value
    radio (left half). The CSS `input:checked ~ label` trick fills the correct stars.
    """

    def render(self, name, value, attrs=None, renderer=None):
        current = Decimal(str(value)) if value else None

        def _id(v):
            return f"id_{name}_{str(v).replace('.', '_')}"

        def _checked(v):
            return ' checked' if current == Decimal(str(v)) else ''

        parts = []
        for full_val, half_val in _STAR_PAIRS:
            full_d = Decimal(str(full_val))
            half_d = Decimal(str(half_val))
            full_label = f"{full_val} star{'s' if full_val != 1 else ''}"
            half_label = f"{half_val} stars"
            parts += [
                f'<input type="radio" name="{name}" id="{_id(full_val)}" value="{full_d}"{_checked(full_val)}>',
                f'<label for="{_id(full_val)}" class="star-full" aria-label="{full_label}" title="{full_label}"></label>',
                f'<input type="radio" name="{name}" id="{_id(half_val)}" value="{half_d}"{_checked(half_val)}>',
                f'<label for="{_id(half_val)}" class="star-half" aria-label="{half_label}" title="{half_label}"></label>',
            ]

        return mark_safe(
            f'<div class="star-widget" role="radiogroup" aria-label="{name} star rating">'
            + ''.join(parts)
            + '</div>'
        )

    def value_from_datadict(self, data, files, name):
        return data.get(name)


class StarRatingField(forms.Field):
    """Form field that accepts half-star values (0.5–5 in 0.5 steps) and returns Decimal."""

    VALID_VALUES = {str(v): v for v in HALF_STAR_CHOICES}

    def __init__(self, *args, **kwargs):
        kwargs.setdefault('widget', StarRatingWidget)
        super().__init__(*args, **kwargs)

    def to_python(self, value):
        if value in (None, ''):
            return None
        str_val = str(value).strip()
        if str_val in self.VALID_VALUES:
            return self.VALID_VALUES[str_val]
        raise forms.ValidationError(
            "Select a star rating between 0.5 and 5 (half-stars allowed)."
        )

    def validate(self, value):
        super().validate(value)
        if value is not None and value not in HALF_STAR_CHOICES:
            raise forms.ValidationError(
                "Select a star rating between 0.5 and 5 (half-stars allowed)."
            )
