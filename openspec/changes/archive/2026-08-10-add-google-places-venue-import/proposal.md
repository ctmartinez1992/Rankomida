## Why

Every venue in Rank O Mida is typed by hand in Django admin. Of the venue locations that used to exist, all but two had null coordinates and none carried a stable external identifier. Adding a dish means first transcribing a restaurant's name, address, and city from Google Maps by hand. The catalog has since been cleared, so there is now nothing to browse at all.

Google Places API (New) can supply that data directly. A management command that pulls francesinha and prego venues in Porto removes the transcription step and gives every imported storefront a durable `place_id`, coordinates, and a business status we can re-check later.

This is an admin data-entry tool. Imported venues are not visible to visitors until a staff user publishes them.

## What Changes

- Add a `import_google_places` management command in `catalog` that queries Places API (New) Text Search and upserts venues
- Store the Google `place_id` and associated storefront data on `VenueLocation`, keyed for idempotent re-runs
- Add `is_published` and `source` to `Venue`; imports write `is_published=False` so nothing reaches the public site unreviewed
- Filter the public venue list and venue detail pages to published venues only
- Add `GOOGLE_MAPS_API_KEY` configuration following the existing `os.environ.get` pattern
- Add a `--dry-run` mode that reports planned writes without touching the database

Explicitly out of scope: brand-level grouping of multi-location chains (handled manually in admin), duplicate detection against hand-created venues, quadtree tiling for exhaustive city coverage, importing Google photos, and any user-facing surfacing of Google ratings.

## Capabilities

### New Capabilities

- `google-places-venue-import`: Staff-run import of Porto venues from Google Places API (New) into `Venue` and `VenueLocation`, idempotent on `place_id`, with dry-run reporting
- `venue-publication-visibility`: A published flag on `Venue` gating which venues appear on public catalog pages

### Modified Capabilities

- (none)

## Impact

- **catalog**: new fields on `Venue` (`is_published`, `source`) and `VenueLocation` (13 Google-sourced fields), migration, new `management/commands/import_google_places.py`, a Places API client module, admin exposure of the new fields, and published-only filtering in `VenueListView` and `VenueDetailView`
- **config**: `GOOGLE_MAPS_API_KEY` in `settings.py` and `.env.example`
- **requirements**: add pinned `requests` (the project currently has no HTTP client)
- **tests**: import creates and updates rows, re-runs are idempotent, dry-run writes nothing, publication gating on public views
- **compliance**: Google Maps Platform terms permit indefinite storage of `place_id` only; storing the remaining fields permanently is a deliberate accepted risk recorded in `design.md`
