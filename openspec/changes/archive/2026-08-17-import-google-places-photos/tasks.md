## 1. Service Layer

- [x] 1.1 Add `places.photos` to `FIELD_MASK` in `catalog/services/google_places.py`
- [x] 1.2 Add `PHOTO_BASE_URL` constant (`https://places.googleapis.com/v1/{name}/media`) and `fetch_photo(photo_name, api_key, max_width=800, session=None)` function that GETs the media endpoint with `skipHttpRedirect=true`, extracts `photoUri`, then downloads and returns the raw bytes; raises `PlacesError` on any failure

## 2. Command Integration

- [x] 2.1 In `_process()` in `import_google_places.py`, after a venue is created (not on update or when venue already has a photo), extract the first entry from `place.get("photos") or []` and call `fetch_photo()`
- [x] 2.2 Save the fetched bytes to `venue.photo` via `venue.photo.save(filename, ContentFile(bytes), save=False)`, set `venue.photo_credit = "Google Maps"` and `venue.photo_source_url = place.get("googleMapsUri", "")`, then call `venue.save()`
- [x] 2.3 Wrap the photo fetch+save in a try/except that logs a warning and continues on any `PlacesError` or `requests.RequestException`
- [x] 2.4 Skip the photo block entirely when `venue.photo` is already set (re-sync guard)
- [x] 2.5 Skip the photo block in dry-run mode

## 3. Tests

- [x] 3.1 Add unit tests for `fetch_photo()` in `catalog/tests/test_google_places_service.py` (or equivalent): success path, non-200 response raises `PlacesError`, network error raises `PlacesError`
- [x] 3.2 Add/extend command tests to cover: new venue with photo metadata saves photo+credit+source_url, new venue without photo metadata saves no photo, existing venue with photo skips fetch, photo fetch failure logs warning and does not abort import, dry-run does not call fetch_photo
