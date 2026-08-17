## Why

The import command already caps photo fetches with `--max-photos`, but text search page requests have no ceiling beyond Google's hard 3-page limit. A single run can make up to 46+ HTTP calls to Google (6 search + 20 photo-meta + 20 photo-binary with defaults). There is no way for an operator to set a hard cap across *all* Google API requests in one run, making it impossible to guarantee cost will stay within budget. A single `--max-requests` argument gives operators a single knob to control total spend regardless of how many queries or photos a run involves.

## What Changes

- Add a `RequestBudget` class to `catalog/services/google_places.py` that tracks remaining API calls and provides a `consume(n)` method.
- Thread an optional `budget` parameter through `search_text()` (checked before each page POST) and `fetch_photo()` (checked before its two GETs).
- Add `--max-requests` CLI argument to `import_google_places` (default: `60`). `0` means unlimited.
- When the budget is exhausted during a search, `search_text` stops yielding further pages (no error — just stops). When exhausted during a photo fetch, `fetch_photo` raises `PlacesError` so the photo is gracefully skipped.
- Log a warning when the budget is first exhausted.
- Remove `--max-photos` in favour of `--max-requests` as the single control. **BREAKING**: `--max-photos` is removed.

## Capabilities

### New Capabilities

- `google-api-request-budget`: A per-run cap on total Google Maps API HTTP requests across text search and photo fetching.

### Modified Capabilities

- `google-places-venue-import`: Import command gains `--max-requests` and loses `--max-photos`.
- `google-places-photo-import`: `fetch_photo` respects the shared budget.
- `google-places-photo-limit`: Superseded by `google-api-request-budget`; `--max-photos` removed.

## Impact

- `catalog/services/google_places.py` — new `RequestBudget` class; `search_text` and `fetch_photo` accept optional `budget` kwarg.
- `catalog/management/commands/import_google_places.py` — replace `--max-photos` with `--max-requests`; construct `RequestBudget` in `handle()` and pass to service calls.
- Tests updated to use `--max-requests` instead of `--max-photos`.
