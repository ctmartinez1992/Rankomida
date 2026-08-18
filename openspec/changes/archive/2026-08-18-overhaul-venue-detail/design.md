## Context

The public venue detail page (`templates/catalog/venue_detail.html`, `VenueDetailView`) is a thin hero: photo, name, `venue.city`, then a bullet list of locations (name, city, address, Get Directions). Dish cards below already show Rankomida stars and are out of scope.

`VenueLocation` already stores the Google Places payload: address, neighbourhood, postal code, phone, website, maps URI, coordinates, business status, price level, primary type, types, opening hours (`regularOpeningHours` JSON with `weekdayDescriptions`), and Google rating/count. After venue merge, one `Venue` can have many locations (chain branches). None of that richness is designed into the public page.

Constraints: Django templates + CSS in `templates/base.html`; existing `--color-*` tokens; no new JS framework; no model/migration changes.

## Goals / Non-Goals

**Goals:**
- Show every visitor-facing Venue and VenueLocation field with a coherent UI
- Flatten location facts onto the venue hero when there are 0 or 1 locations
- Show a Locations segment of cards when there are 2+ locations
- Omit blank fields; humanize Google enums; label Google ratings distinctly from Rankomida dish scores
- Keep dish cards, photo attribution, and unpublished-venue 404 behaviour unchanged

**Non-Goals:**
- Location detail URLs or a separate location page
- Map embeds
- Public editing
- Changing the compact location list on dish detail
- Changing venue list cards
- Showing internal fields (`slug`, `is_published`, `source`, `google_place_id`, `last_synced_at`, `created_at`, `updated_at`, raw lat/lng text)

## Decisions

### Layout branches on location count

**Decision:** `n = number of prefetched locations`. `n == 0` or `n == 1` flattens into the hero with no "Locations" heading. `n >= 2` keeps the hero venue-level (photo, name, home city, "N locations") and renders a Locations section of cards before Dishes.

**Why:** A single-branch restaurant should read as one place, not a list of one. Chains need a scannable segment. Count is the only rule; no staff flag.

**Alternative considered:** Always show a Locations heading. Rejected — a heading over one address is noise, and the product request is explicit.

### Shared location-facts partial

**Decision:** `templates/catalog/_venue_location_facts.html` renders one location's public facts. The 1-location hero includes it inline; each 2+ card includes it.

**Why:** Flattened and card layouts must not drift. One place to omit blanks and format links.

**Alternative considered:** Duplicate markup in `venue_detail.html`. Rejected — two copies of the field rules.

### Formatters as a catalog templatetag (not model methods)

**Decision:** Add `catalog/templatetags/catalog_tags.py` with filters/simple tags for:
- price level → € / €€ / €€€ / €€€€ / Free
- business status → warning label only when not `OPERATIONAL`
- primary type → title-cased (`restaurant` → Restaurant)
- types → chips excluding `establishment`, `point_of_interest`, `food`, and the primary type
- opening hours → `opening_hours["weekdayDescriptions"]` when present

**Why:** Presentation belongs in the template layer. `VenueLocation` stays a data model. Filters are unit-testable without rendering the whole page.

**Alternative considered:** Properties on `VenueLocation`. Rejected — mixes display with persistence and is harder to keep out of admin.

Price mapping:

- `PRICE_LEVEL_FREE` → Free
- `PRICE_LEVEL_INEXPENSIVE` → €
- `PRICE_LEVEL_MODERATE` → €€
- `PRICE_LEVEL_EXPENSIVE` → €€€
- `PRICE_LEVEL_VERY_EXPENSIVE` → €€€€
- unknown / blank → omit

### Google rating is numeric and labeled, not Rankomida stars

**Decision:** Show `google_rating` as a number with a "Google" label and optional review count. Do not use `score_as_stars_pct`.

**Why:** Rankomida stars are the product's own dish scores. Reusing the glyph language would imply Google's 4.3 is a Rankomida score.

**Alternative considered:** Star glyphs with a Google caption. Rejected — too easy to misread next to dish cards that use the same stars.

### Maps actions: keep Directions, add Google Maps when URI exists

**Decision:** Keep the existing Get Directions link when lat/lng exist. Add Open in Google Maps when `google_maps_uri` is set. Raw coordinates are never printed.

**Why:** Directions is the current behaviour and is useful for navigation. `google_maps_uri` is the canonical Places page (reviews, photos). They are complementary.

### Venue city vs location city

**Decision:**
- 0 locations: show `venue.city`
- 1 location: show the location's city/neighbourhood/address line; do not also print `venue.city` as a duplicate if it matches the location city
- 2+ locations: show `venue.city` in the hero as the home city; each card shows its own city

**Why:** Imported single-location venues almost always share the same city on both models. Duplicating it is clutter.

### Branch name

**Decision:** Show `location.name` only when it is non-blank and differs (case-insensitive) from `venue.name`. On 2+ cards it is the card title; if blank, fall back to city.

**Why:** Merge stamps original venue names onto locations. For an unmerged Google import, `location.name` is often empty and the venue name is already the `<h1>`.

### CSS: venue detail uses the full container; `.detail-card` stays 640px for dishes

**Decision:** Add a `venue-detail` wrapper (or equivalent class on the venue page) that is full container width (960px). Location cards reuse `.card` / `.card-grid`. New tokens are not introduced. `.detail-card { max-width: 640px }` remains for dish detail.

**Why:** A three-column location grid cannot fit in 640px. Widening `.detail-card` globally would stretch dish detail.

### Prefetch in the view

**Decision:** `VenueDetailView.get_queryset()` uses `prefetch_related("locations")`. The template iterates the prefetched list; no extra `location_count` annotation required.

**Why:** Avoids N+1 and a second count query. `locations.all` in the template uses the prefetch cache.

## Risks / Trade-offs

- **Sparse locations look empty** → Mitigation: omit every blank field so a manual venue with only city does not render a skeleton of labels.
- **Google `types` are noisy** → Mitigation: drop generic types and the primary type; if nothing remains, omit the chip row.
- **`opening_hours` shape may lack `weekdayDescriptions`** → Mitigation: only render when that key is a non-empty list; ignore `periods` / `openNow` for v1.
- **Closed venues still published** → Mitigation: warning chip for non-`OPERATIONAL` status; publication remains a staff decision (`venue-publication-visibility`).
- **Hero width change is page-local** → Mitigation: do not alter `.detail-card`; scope width to the venue detail template.

## Migration Plan

No data migration. Deploy is a template/CSS/view/templatetag change. Rollback is reverting those files.

## Open Questions

None — field show/hide list and the 0/1 vs 2+ layout rule were decided in the proposal.
