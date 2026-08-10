"""Import Porto venues from Google Places API (New) Text Search.

Staff tool. Imported venues are created unpublished and reviewed in admin before
they reach the public site.
"""

from __future__ import annotations

import logging
from decimal import Decimal, InvalidOperation
from typing import Any

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone
from django.utils.text import slugify

from catalog.models import Venue, VenueLocation
from catalog.services.google_places import MAX_PAGES, PlacesError, search_text

logger = logging.getLogger(__name__)

DEFAULT_QUERIES = ["francesinha porto", "prego porto"]
DEFAULT_CITY = "Porto"

_COORD_PRECISION = Decimal("0.000001")
_RATING_PRECISION = Decimal("0.1")

# Deliberately excludes administrative_area_level_2: for Portuguese addresses that
# is the municipality, which only duplicates `city`.
_NEIGHBOURHOOD_TYPES = ("sublocality_level_1", "sublocality")


class Command(BaseCommand):
    help = "Import venues from Google Places API (New) Text Search."

    def add_arguments(self, parser):
        parser.add_argument(
            "--query",
            action="append",
            dest="queries",
            metavar="TEXT",
            help=(
                "Text Search query; repeatable. "
                f"Defaults to {' and '.join(repr(q) for q in DEFAULT_QUERIES)}."
            ),
        )
        parser.add_argument(
            "--city",
            default=DEFAULT_CITY,
            help=f"City to fall back on when Google omits one (default: {DEFAULT_CITY}).",
        )
        parser.add_argument(
            "--max-pages",
            type=int,
            default=MAX_PAGES,
            help=f"Pages to request per query, capped at Google's limit of {MAX_PAGES}.",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Report what would be written without touching the database.",
        )

    def handle(self, *args, **options):
        api_key = getattr(settings, "GOOGLE_MAPS_API_KEY", "")
        if not api_key:
            raise CommandError(
                "GOOGLE_MAPS_API_KEY is not set. Add it to your environment or .env "
                "before running this command."
            )

        queries = options["queries"] or list(DEFAULT_QUERIES)
        city_fallback = options["city"]
        max_pages = options["max_pages"]
        dry_run = options["dry_run"]

        if dry_run:
            self.stdout.write(self.style.WARNING("Dry run — no database writes."))

        seen_place_ids: set[str] = set()
        created = updated = skipped = 0

        for query in queries:
            self.stdout.write(f"Query: {query!r}")
            try:
                places = list(
                    search_text(
                        query,
                        api_key=api_key,
                        max_pages=max_pages,
                    )
                )
            except PlacesError as exc:
                logger.error("places.query_failed query=%r error=%s", query, exc)
                self.stderr.write(self.style.ERROR(f"  Query failed: {exc}"))
                continue

            for place in places:
                place_id = (place or {}).get("id")
                if not place_id:
                    skipped += 1
                    logger.warning("places.skip reason=missing_id")
                    continue
                if place_id in seen_place_ids:
                    continue
                seen_place_ids.add(place_id)

                try:
                    outcome = self._process(place, city_fallback, dry_run)
                except Exception as exc:  # one bad place must not lose the batch
                    skipped += 1
                    logger.exception(
                        "places.skip reason=processing_error place_id=%s error=%s",
                        place_id,
                        exc,
                    )
                    self.stderr.write(self.style.ERROR(f"  Skipped {place_id}: {exc}"))
                    continue

                if outcome == "created":
                    created += 1
                else:
                    updated += 1

        self.stdout.write("")
        verb = "Would create" if dry_run else "Created"
        self.stdout.write(
            self.style.SUCCESS(
                f"{verb} {created}, "
                f"{'would update' if dry_run else 'updated'} {updated}, "
                f"skipped {skipped}."
            )
        )

    def _process(self, place: dict[str, Any], city_fallback: str, dry_run: bool) -> str:
        fields = _map_place(place, city_fallback)
        place_id = fields["google_place_id"]
        existing = VenueLocation.objects.filter(google_place_id=place_id).first()

        if existing is not None:
            self.stdout.write(f"  update: {existing.venue.name}")
            if not dry_run:
                self._apply_location_fields(existing, fields)
            return "updated"

        name = fields.pop("_name")
        self.stdout.write(f"  create: {name}")
        if not dry_run:
            with transaction.atomic():
                venue = Venue.objects.create(
                    name=name,
                    slug=_unique_slug(name),
                    city=fields["city"],
                    is_published=False,
                    source=Venue.SOURCE_GOOGLE,
                )
                location = VenueLocation(venue=venue)
                self._apply_location_fields(location, fields)
        return "created"

    @staticmethod
    def _apply_location_fields(location: VenueLocation, fields: dict[str, Any]) -> None:
        """Write Google-sourced fields only; `name` stays whatever staff set."""
        for key, value in fields.items():
            if key.startswith("_"):
                continue
            setattr(location, key, value)
        location.last_synced_at = timezone.now()
        location.save()


def _map_place(place: dict[str, Any], city_fallback: str) -> dict[str, Any]:
    components = place.get("addressComponents") or []
    city = _component(components, "locality") or city_fallback
    name = _text(place.get("displayName")) or ""
    if not name:
        raise ValueError("place has no display name")

    location = place.get("location") or {}
    hours = place.get("regularOpeningHours")

    return {
        "_name": name[:200],
        "google_place_id": place["id"],
        "city": city[:120],
        "address": (place.get("formattedAddress") or "")[:255],
        "latitude": _decimal(location.get("latitude"), _COORD_PRECISION),
        "longitude": _decimal(location.get("longitude"), _COORD_PRECISION),
        "postal_code": (_component(components, "postal_code") or "")[:20],
        "neighbourhood": _neighbourhood(components)[:120],
        "business_status": (place.get("businessStatus") or "")[:32],
        "phone": (place.get("nationalPhoneNumber") or "")[:40],
        "website_url": (place.get("websiteUri") or "")[:500],
        "google_maps_uri": (place.get("googleMapsUri") or "")[:500],
        "price_level": (place.get("priceLevel") or "")[:32],
        "primary_type": (place.get("primaryType") or "")[:80],
        "types": place.get("types") or [],
        "opening_hours": hours if isinstance(hours, dict) else None,
        "google_rating": _decimal(place.get("rating"), _RATING_PRECISION),
        "google_user_rating_count": place.get("userRatingCount"),
    }


def _text(value: Any) -> str:
    if isinstance(value, dict):
        return value.get("text") or ""
    return value or ""


def _component(components: list[dict[str, Any]], wanted: str) -> str:
    for component in components:
        if wanted in (component.get("types") or []):
            return component.get("longText") or component.get("shortText") or ""
    return ""


def _neighbourhood(components: list[dict[str, Any]]) -> str:
    for wanted in _NEIGHBOURHOOD_TYPES:
        found = _component(components, wanted)
        if found:
            return found
    return ""


def _decimal(value: Any, precision: Decimal) -> Decimal | None:
    if value is None:
        return None
    try:
        return Decimal(str(value)).quantize(precision)
    except (InvalidOperation, ValueError):
        return None


def _unique_slug(name: str) -> str:
    base = slugify(name)[:210] or "venue"
    candidate = base
    suffix = 2
    taken = set(Venue.objects.filter(slug__startswith=base).values_list("slug", flat=True))
    while candidate in taken:
        candidate = f"{base}-{suffix}"
        suffix += 1
    return candidate
