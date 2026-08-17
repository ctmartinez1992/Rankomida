## Why

The `import_google_places` management command builds venue records from Google Places API data but never requests or saves photos. As a result, staff must manually upload venue photos after every import, even though the Places API (New) provides photo references that can be fetched as actual image files.

## What Changes

- Add `places.photos` to the `FIELD_MASK` in `google_places.py` so photo metadata is returned per place.
- After creating or updating a `VenueLocation`, fetch the first available photo from the Places Photo endpoint and save it to the `Venue.photo` field.
- Only write the photo when the venue does not already have one (respects staff curation).
- Set `photo_credit` to "Google Maps" and `photo_source_url` to the `googleMapsUri` of the venue, consistent with the image-attribution spec.
- The photo download is best-effort: a failure logs a warning and does not abort the import.

## Capabilities

### New Capabilities

- `google-places-photo-import`: Fetching a venue photo from the Places Photo API and persisting it to `Venue.photo` during import, with credit attribution.

### Modified Capabilities

- `google-places-venue-import`: The import command gains photo-fetching behaviour. The field mask, service layer, and command logic all change.

## Impact

- `catalog/services/google_places.py` — new `FIELD_MASK` entry, new `fetch_photo()` function.
- `catalog/management/commands/import_google_places.py` — photo fetch call in `_process()`.
- No new model fields; uses existing `Venue.photo`, `photo_credit`, `photo_source_url`.
- New runtime dependency: `requests` (already used), `Pillow` (already required for `ImageField`).
- Billing: each photo fetch is a separate Places Photo request; this is noted in the design.
