## Why

The venue detail Locations cards dump every public `VenueLocation` fact (hours, types, phone, maps, Google rating) into a 260px square. That layout does not scale for multi-branch venues. Visitors need a dedicated location page so the cards can stay scannable teasers.

## What Changes

- Add a public `VenueLocation` detail page at `/venues/<venue-slug>/locations/<pk>/`.
- **0 or 1 location:** keep the current venue-detail behaviour (flatten full facts onto the venue hero). Visiting the location URL redirects to venue detail.
- **2+ locations:** keep the Locations segment, but each card becomes a compact teaser (heading, place line, address, closed warning, link) instead of the full fact list.
- Location detail shows the same visitor-facing facts currently used in the flattened hero. Dishes stay on the venue. No photo, no map embed.
- Hide the same internal fields as venue detail (`slug`, `is_published`, `source`, `google_place_id`, timestamps, raw coordinates).
- Unpublished parent venue, missing location, or venue-slug mismatch returns 404.

## Capabilities

### New Capabilities

- `venue-location-detail`: Public location detail URL, field visibility, single-location redirect, unpublished/mismatch 404, and facts-only (no dishes)

### Modified Capabilities

- `venue-detail-display`: 2+ location cards SHALL be compact teasers with a link to location detail, not the full public fact list. 0/1 flatten behaviour is unchanged.

## Impact

- `catalog/urls.py` — nested location detail route
- `catalog/views.py` — `VenueLocationDetailView` (404 / 1-location redirect)
- `catalog/models.py` — `VenueLocation.get_absolute_url()`; no migration
- `templates/catalog/venue_detail.html` — compact 2+ cards
- `templates/catalog/venue_location_detail.html` — new detail page
- Compact location teaser partial (or flag on the existing facts partial)
- `templates/base.html` — small card/link styles if needed
- `templates/catalog/dish_detail.html` and `_community_notes.html` — optional links via `get_absolute_url` (redirects when n==1)
- `catalog/tests.py` — 2+ card compactness, location detail facts, 404, unpublished, redirect
- Reuse existing `catalog` templatetag formatters
- Out of scope: map embeds, location slugs, location photos, dishes on the location page
