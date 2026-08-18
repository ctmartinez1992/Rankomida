## Context

The public venue detail page already shows rich `VenueLocation` facts via `templates/catalog/_venue_location_facts.html`. For 0/1 locations those facts flatten into the venue hero. For 2+ locations the same full fact list is stuffed into `.card` tiles (`minmax(260px)`), which overflows: weekday hours, type chips, phone/website/maps, and Google rating all compete in a small square.

`VenueLocation` has no slug. Dishes belong to `Venue`, not to a location. Ratings may tag a `venue_location`, but this change does not surface them on the location page.

Constraints: Django templates + CSS in `templates/base.html`; existing `--color-*` tokens; no new JS framework; no model/migration changes.

## Goals / Non-Goals

**Goals:**
- Give 2+ branch venues a dedicated location detail page for the full public fact list
- Slim 2+ location cards to scannable teasers that link through
- Keep 0/1 location venue pages unchanged (venue page remains the facts page)
- 404 unpublished parent, missing location, or venue-slug mismatch
- Redirect the location URL to venue detail when the venue has fewer than 2 locations
- Reuse the existing facts partial and catalog templatetag formatters

**Non-Goals:**
- Map embeds
- Location slugs or photos
- Dishes or ratings on the location page
- Changing venue list cards
- Public editing
- Showing internal fields (`slug`, `is_published`, `source`, `google_place_id`, timestamps, raw lat/lng text)

## Decisions

### Nested pk URL under the venue

**Decision:** `/venues/<venue-slug>/locations/<pk>/`, named `catalog:venue_location_detail`. `VenueLocation.get_absolute_url()` reverses that route.

**Why:** Locations have no slug and are not a top-level catalog entity. Nesting under the venue slug keeps unpublished-venue 404 in one lookup (`venue__slug` + `venue__is_published=True` + `pk`) and makes mismatched slugs 404.

**Alternative considered:** `/locations/<pk>/`. Rejected — loses the venue in the path and makes unpublished checks a second hop. Google place id as the URL key was rejected because it is an internal identifier.

### Single-location visits redirect

**Decision:** The route always exists. If the parent venue has fewer than 2 locations, the view redirects to `catalog:venue_detail`. Venue detail does not link to the location URL when n < 2.

**Why:** Dish-detail compact lists and community notes can always call `get_absolute_url()` without counting sibling locations. The 1-location venue page stays the canonical facts page.

**Alternative considered:** 404 when n < 2. Rejected — breaks deep links from notes. Always rendering location detail when n == 1 was rejected in explore (duplicate facts page).

### Compact teaser vs full facts

**Decision:** 2+ cards show heading (branch name, or city if blank/matching venue name), neighbourhood/city, address, non-OPERATIONAL warning, and a link to detail. Hours, type chips, phone, website, maps actions, and Google rating stay off the card and on the location page. 1-location hero still includes `_venue_location_facts.html` in full.

**Why:** The card is a chooser (“which branch?”), not a duplicate of the detail page.

**Alternative considered:** Keep Get Directions on the card. Rejected for v1 — one more action in the square; the detail page already has Directions and Google Maps.

### Location detail uses `.detail-card`

**Decision:** `templates/catalog/venue_location_detail.html` uses the existing 640px `.detail-card` (same as dish detail). Breadcrumb: All Venues → venue name → location heading. H1 is the location heading; parent venue is a subtitle link. No photo. No dish grid. Include `_venue_location_facts.html` for the fact list.

**Why:** This is a focused facts page, not a listing. Venue photo would imply every branch shares one storefront shot. Dishes remain venue-level.

**Alternative considered:** Full-width `venue-detail` wrapper. Rejected — no grid on this page, and widening would diverge from dish detail without benefit.

### View lookup

**Decision:** `VenueLocationDetailView` loads with `get_object_or_404(VenueLocation.objects.select_related("venue"), pk=pk, venue__slug=slug, venue__is_published=True)`. Then if `venue.locations.count() < 2`, redirect.

**Why:** One query for the object; a cheap count for the redirect rule. Prefetch is unnecessary because the page shows a single location.

## Risks / Trade-offs

- **Card looks empty for sparse branches** → Mitigation: still show city/address when present; omit blank teaser rows the same way facts omit blanks.
- **Redirect vs 404 confusion** → Mitigation: tests cover n==0/1 redirect, n>=2 200, unpublished/mismatch 404.
- **Dish detail N+1 if linking locations** → Mitigation: prefetch `venue__locations` on `DishDetailView` if those links are added.
- **Two copies of heading rules** → Mitigation: keep using `location_heading` for both teaser title and detail H1.

## Migration Plan

No data migration. Deploy is URL/view/template/CSS plus `get_absolute_url`. Rollback is reverting those files.

## Open Questions

None — layout, URL, redirect, and facts-only scope were decided in explore.
