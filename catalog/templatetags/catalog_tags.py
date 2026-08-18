from django import template

register = template.Library()

_PRICE_LEVELS = {
    "PRICE_LEVEL_FREE": "Free",
    "PRICE_LEVEL_INEXPENSIVE": "€",
    "PRICE_LEVEL_MODERATE": "€€",
    "PRICE_LEVEL_EXPENSIVE": "€€€",
    "PRICE_LEVEL_VERY_EXPENSIVE": "€€€€",
}

_GENERIC_TYPES = frozenset({"establishment", "point_of_interest", "food"})

_STATUS_LABELS = {
    "CLOSED_TEMPORARILY": "Closed temporarily",
    "CLOSED_PERMANENTLY": "Closed permanently",
}


def _humanize_enum(value: str) -> str:
    text = value.replace("_", " ").strip().lower()
    return text.title() if text else ""


@register.filter
def price_level_display(value):
    if not value:
        return ""
    return _PRICE_LEVELS.get(str(value).strip(), "")


@register.filter
def business_status_label(value):
    if not value:
        return ""
    status = str(value).strip()
    if not status or status == "OPERATIONAL":
        return ""
    return _STATUS_LABELS.get(status, _humanize_enum(status))


@register.filter
def humanize_place_type(value):
    if not value:
        return ""
    return _humanize_enum(str(value))


@register.filter
def public_place_types(types, primary_type=""):
    if not types:
        return []
    primary = (primary_type or "").strip().lower()
    result = []
    seen = set()
    for raw in types:
        key = str(raw).strip().lower()
        if not key or key in _GENERIC_TYPES or key == primary or key in seen:
            continue
        seen.add(key)
        label = _humanize_enum(key)
        if label:
            result.append(label)
    return result


@register.filter
def weekday_hours(opening_hours):
    if not isinstance(opening_hours, dict):
        return []
    descriptions = opening_hours.get("weekdayDescriptions")
    if not isinstance(descriptions, list):
        return []
    return [line for line in descriptions if line]


@register.filter
def location_heading(location, venue):
    name = (getattr(location, "name", None) or "").strip()
    venue_name = (getattr(venue, "name", None) or "").strip()
    if name and name.casefold() != venue_name.casefold():
        return name
    return ""


@register.filter
def tel_href(phone):
    if not phone:
        return ""
    digits = "".join(ch for ch in str(phone) if ch.isdigit() or ch == "+")
    return f"tel:{digits}" if digits else ""
