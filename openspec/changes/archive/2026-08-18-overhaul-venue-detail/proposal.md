## Why

The public venue detail page only shows name, city, and a thin location list (address + directions). Google Places import and venue merge now store rich `VenueLocation` data — phone, hours, price, neighbourhood, Google rating, maps URI, types — that visitors never see. After merge, some venues have multiple branches, so a single bullet list no longer scales.

## What Changes

- Overhaul the public venue detail page so every visitor-facing `Venue` and `VenueLocation` field has a designed UI.
- **0 or 1 location:** flatten all location facts onto the venue hero. No "Locations" heading.
- **2+ locations:** keep the hero venue-level (photo, name, home city, location count) and add a **Locations** segment of cards, one per `VenueLocation`.
- Omit blank fields rather than rendering empty labeled rows.
- Humanize Google enums (price level, business status, primary type) and attribute Google ratings so they cannot be confused with Rankomida dish scores.
- Hide internal fields from the public page: `slug`, `is_published`, `source`, `google_place_id`, timestamps, raw coordinates.
- Reuse a shared location-facts partial so the flattened and multi-location layouts cannot drift.
- Widen the venue detail layout to the full container so a location card grid fits; dish detail is unchanged.

## Capabilities

### New Capabilities

- `venue-detail-display`: Public venue detail layout, field visibility, empty-field omission, and the 0/1 flatten vs 2+ Locations-segment rule

### Modified Capabilities

<!-- No existing spec-level requirements are changing. Photo attribution, dish star scores, and unpublished-venue 404 stay as specified. -->

## Impact

- `templates/catalog/venue_detail.html` — rebuilt around flattened vs Locations-segment layouts
- `templates/catalog/_venue_location_facts.html` — new shared partial for one location's public facts
- `templates/base.html` — venue-detail CSS (location cards, chips, fact list, action links); `.detail-card` max-width stays for dish detail
- `catalog/views.py` — prefetch locations on `VenueDetailView`
- New formatter helpers (model properties or a `catalog` templatetag) for price, status, types, and weekday hours
- `catalog/tests.py` — coverage for 0 / 1 / 2+ location pages
- No model or migration changes
- Out of scope: location detail URLs, map embeds, editing, dish-detail location list, venue list cards
