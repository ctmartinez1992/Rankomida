## Why

The `import_google_places` command now fetches a photo for each new venue, but there is no cap on how many photo fetches occur per run. Google Places grants a $200/month free credit; photo requests cost ~$7 per 1,000 calls. An uncapped run could silently exhaust the free tier. A `--max-photos` argument lets operators control exactly how many photo API calls a single run may make, making cost predictable.

## What Changes

- Add a `--max-photos` CLI argument to `import_google_places` (default: `20`).
- Track the number of photo fetches made during the run; skip photo fetching once the limit is reached.
- Log a warning when the limit is hit so operators know photos were skipped.
- `--max-photos 0` means no photos are fetched at all (opt-out).

## Capabilities

### New Capabilities

- `google-places-photo-limit`: A per-run cap on Places Photo API requests issued by the import command.

### Modified Capabilities

- `google-places-photo-import`: Photo fetching now respects the per-run limit.

## Impact

- `catalog/management/commands/import_google_places.py` — new `--max-photos` argument, counter in `handle()`, guard in `_fetch_and_save_photo()`.
- No changes to service layer, models, or migrations.
