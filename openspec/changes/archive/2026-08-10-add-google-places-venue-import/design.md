## Context

`catalog` models a two-level hierarchy: `Venue` (a brand) owns many `VenueLocation` (a storefront). `Dish` has an FK to `Venue`; `RatingSubmission` has an optional FK to `VenueLocation`.

The data that previously filled these tables did not apply that hierarchy consistently — Vaccarum existed as two separate `Venue` rows (Sá da Bandeira and Bonjardim) while Yuko Tavern was one `Venue` with two `VenueLocation` rows. Google Places has no concept of a brand at all: a Place is a single storefront with one `place_id`, one address, and one coordinate pair, so the import must pick a side.

Current scale: the catalog was cleared through Django admin before this change was implemented. Zero venues, locations, dishes, and rating submissions remain. The Francesinha dish type, its three criteria templates, and 101 user accounts survive. The import therefore populates an empty catalog.

Constraints from product decisions:

- The import is an admin convenience, not a user-facing feature
- Dish-targeted search only; no exhaustive city sweep
- Google content is stored permanently as a knowing exception to Google's terms

Constraints from the Places API:

- Text Search returns at most 20 results per page over at most 3 pages — a hard ceiling of 60 results per query, with no parameter to raise it
- `nextPageToken` is not immediately valid; it needs roughly 2–5 seconds before it resolves
- Billing tier is determined by the requested field mask, so the mask is a cost decision, not just a data one

## Goals / Non-Goals

**Goals:**

- Populate `Venue` and `VenueLocation` from Google Places without hand transcription
- Give every imported storefront a stable `place_id` so re-runs update rather than duplicate
- Keep imported venues invisible to visitors until a staff user reviews them
- Preserve staff edits across re-syncs
- Make a dry run show exactly what would happen, including probable duplicates

**Non-Goals:**

- Exhaustive coverage of every restaurant in Porto (quadtree tiling)
- Automatic brand grouping or automatic merging of chain locations
- Detecting or reporting duplicates against hand-created venues
- Importing or re-hosting Google photos
- Showing Google's own ratings to visitors
- User-submitted venues or dishes
- Cities other than Porto in this change (the command takes a city argument, but only Porto is exercised)

## Decisions

### 1. `place_id` lives on `VenueLocation`, and Google's fields follow it

**Choice:** `VenueLocation.google_place_id` is the unique natural key for imported storefronts. `Venue` stays a thin brand record. `Dish` keeps its FK to `Venue`, unchanged.

**Why:** A Google Place is a storefront, and storefront-scoped data (address, coordinates, phone, opening hours, business status) belongs on the storefront row. Putting `place_id` on `Venue` would mean a chain can only ever have one Google identity.

**Consequence, accepted:** `Venue` gains almost nothing from the API, and because `Dish` still points at `Venue`, ratings cannot distinguish the francesinha at Vaccarum Bonjardim from the one at Sá da Bandeira. Moving `Dish` to `VenueLocation` would fix that but touches ratings, leaderboard, and every template; it is deferred.

**Alternatives considered:** `place_id` on `Venue` with `VenueLocation` flattened to 1:1 (simpler import, discards the multi-location model and orphans `RatingSubmission.venue_location`); moving `Dish` to `VenueLocation` (truest model, materially larger refactor).

### 2. Each imported Place creates one `Venue` and one `VenueLocation`

**Choice:** The import does not attempt to group storefronts into brands. Two Vaccarum locations produce two `Venue` rows, each with one `VenueLocation`.

**Why:** Brand grouping from a display name is guesswork — "Vaccarum - Bonjardim" and "Vaccarum Francesinhas & Tapas - Sa da Bandeira" share no clean prefix. Guessing wrong creates cross-linked venues that are harder to unpick than duplicates. This also matches how the existing Vaccarum rows are already modelled.

**Alternatives considered:** Prefix or token-overlap heuristics for brand detection (fragile); a staff review queue for proposed merges (more machinery than 14 rows justify).

### 3. `Venue.is_published` defaults to `True`; the importer writes `False`

**Choice:** `BooleanField(default=True)`, mirroring `Dish.is_published`. The import passes `is_published=False` explicitly.

**Why:** A `True` default means the 14 existing venues stay visible with no data migration, while imports are invisible by default. Inverting the default would require a migration to republish existing rows and would silently hide any venue created through admin.

### 4. Re-syncs update Google fields and never touch curated fields

**Choice:** On re-run, matched by `google_place_id`, the command updates the `VenueLocation` Google fields and `last_synced_at`. It never modifies `Venue.name`, `Venue.slug`, `Venue.photo`, or `Venue.is_published` after creation.

**Why:** Once a staff user renames a venue, uploads a photo, and publishes it, a re-sync that reverts any of that is a data-loss bug. `place_id` identifies the row; curation owns the presentation.

### 5. Two-tier search terms, supplied as arguments rather than derived from `DishType`

**Choice:** `--query` is repeatable and defaults to `["francesinha porto", "prego porto"]`.

**Why:** Deriving queries from `DishType.name` looks tidy but the third dish type is "Smoke", which as a search term returns barbecue restaurants and tobacconists. Explicit queries keep the operator in control and make the cost of a run predictable.

### 6. Field mask is fixed and explicit

**Choice:** One field mask constant covering `id`, `displayName`, `formattedAddress`, `addressComponents`, `location`, `businessStatus`, `primaryType`, `types`, `priceLevel`, `regularOpeningHours`, `nationalPhoneNumber`, `websiteUri`, `googleMapsUri`, `rating`, `userRatingCount`, and `nextPageToken`.

**Why:** The mask drives the billing tier, so it should be a single reviewable constant rather than something assembled at call time. Requesting everything once per place is cheaper than a cheap enumeration pass followed by per-place detail calls at this volume.

### 7. Dry run reports planned writes, with no duplicate detection

**Choice:** `--dry-run` prints the creates and updates it would perform and writes nothing. The command does no fuzzy matching against hand-created venues.

**Why:** Duplicate flagging was designed for a catalog holding 14 curated venues that a "francesinha porto" search would mostly return again. That catalog was cleared before implementation, so the first import lands in an empty table and has nothing to collide with. Name-similarity matching against an empty set is dead weight; if curated venues accumulate later and a re-sync starts producing duplicates, this is worth revisiting as its own change.

**Alternatives considered:** Keeping the difflib check dormant for future use (carries a requirement and a test for behaviour nothing exercises).

### 8. `city` comes from address components; `neighbourhood` only from a true sublocality

**Choice:** Read `locality` from `addressComponents` for `city`, falling back to `--city` when absent. Read `neighbourhood` from `sublocality_level_1` or `sublocality` only, leaving it empty when neither is present.

**Why:** `Venue.city` drives the existing city filter on `/venues/`, so it needs to be consistent. Neighbourhood is stored because it is free at import time and is the natural next filter axis for a Porto-only product.

The first live run originally fell back to `administrative_area_level_2` when no sublocality was present, which set `neighbourhood` equal to `city` on 61 of 62 imported rows — Portuguese addresses from Places carry the municipality at that level, not a district. An empty field is more honest than a duplicated one, so the fallback was removed. Real Porto districts (Cedofeita, Bonfim, Foz) would need reverse geocoding from the stored coordinates, which is a separate API and a separate change.

## Risks / Trade-offs

- **[Risk] Storing Google content permanently violates Google Maps Platform terms.** `place_id` is exempt from caching restrictions and may be stored indefinitely; `formattedAddress` and coordinates are capped at 30 consecutive days; other Places content is not meant to be cached at all. This change stores everything permanently as a deliberate decision for a small non-commercial project. Mitigation if the position changes: `last_synced_at` already provides the timestamp an expiry job would need, and `place_id` alone is enough to re-fetch everything else.
- **[Risk] Duplicate venues if curated rows accumulate later.** The command has no duplicate detection, so a venue added by hand and later returned by a search will import a second time. Mitigation: the catalog is empty today, and imports are unpublished and therefore invisible to visitors; merging stays a manual admin task.
- **[Risk] Stale rows as restaurants close.** Mitigation: `business_status` is captured, so a permanently-closed venue is detectable; acting on it is left to a later change.
- **[Risk] API key committed or leaked.** Mitigation: key is read from the environment only, `.env` is already gitignored, and only `.env.example` gains a commented placeholder.
- **[Trade-off] 60-result ceiling per query.** Two queries cap the import at 120 places before deduplication. Accepted: that is more Porto francesinha venues than the catalog can absorb near-term, and more queries can be added by argument.
- **[Trade-off] `Dish` still hangs off `Venue`.** Per-storefront dish ratings remain impossible. Accepted for now; revisit if chains become common in the catalog.

## Migration Plan

1. Add fields and migration. `Venue.is_published` defaults `True`, so existing rows and pages are unaffected.
2. Ship the published-only filtering on public views while every venue is still published — no visible change.
3. Add the command, client, and settings. Run with `--dry-run` first and review the duplicate report.
4. Run for real; imported venues land unpublished and are reviewed in admin.
5. Rollback: reverse the migration to drop the new fields, and remove the command and client. No existing data depends on them.

## Open Questions

- Whether to surface `google_rating` and `google_user_rating_count` anywhere in admin as a curation-priority signal. Stored by this change, displayed by none.
- Whether a future change should move `Dish` to `VenueLocation`. Revisit when a chain with genuinely different food per branch enters the catalog.
