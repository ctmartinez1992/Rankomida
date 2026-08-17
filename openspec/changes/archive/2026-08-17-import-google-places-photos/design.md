## Context

`import_google_places` already calls the Places API (New) Text Search endpoint. The `FIELD_MASK` constant controls which billing SKU applies. Photos are returned as metadata objects containing a `name` (resource path) from which a photo binary can be fetched via a separate `GET` to the Places Photo endpoint. The current code never requests photos and never touches `Venue.photo`, `photo_credit`, or `photo_source_url`.

## Goals / Non-Goals

**Goals:**
- Request photo metadata from the Places API alongside existing fields.
- Fetch the first available photo binary and save it to `Venue.photo`.
- Populate `photo_credit` ("Google Maps") and `photo_source_url` (the venue's `googleMapsUri`) per the image-attribution spec.
- Skip photo fetch when the venue already has a photo (staff curation wins).
- Treat photo failure as non-fatal: log a warning and continue.

**Non-Goals:**
- Downloading more than one photo per venue.
- Re-fetching a photo on subsequent re-syncs (the existing guard handles this).
- Adding new model fields; all fields already exist.
- Handling authorAttributions beyond using the "Google Maps" credit.

## Decisions

### 1. Use a separate Photos API request, not embed the photo in the search response

The Places API (New) does not inline image binaries in Text Search. It returns a `photos` array of resource name strings (`places/*/photos/*`). A second `GET` to `https://places.googleapis.com/v1/{name}/media?key=...&maxWidthPx=800&skipHttpRedirect=true` returns a JSON object with a `photoUri` field (a signed, short-lived URL). We then `GET` that URI to download the actual binary.

**Alternatives considered:**
- `skipHttpRedirect=false` — would redirect directly to the image, but this makes it harder to distinguish API errors from photo fetch errors and loses the URI for reference.

### 2. Only fetch photo when venue has no existing photo

On re-syncs, staff may have replaced the Google photo with a curated one. Checking `bool(venue.photo)` before fetching avoids overwriting it and skips the API cost.

### 3. Store as Django `ImageField` via `ContentFile`

Django's `ImageField.save(name, ContentFile(bytes))` correctly writes to the configured `MEDIA_ROOT` and updates the field path. This is consistent with how the rest of the catalog saves images.

### 4. Photo credit set to "Google Maps"

The Places API Terms of Service require attribution. Using the static string "Google Maps" is the minimal compliant form. `photo_source_url` is set to the place's `googleMapsUri` so the attribution overlay links back to the place on Google Maps.

### 5. Photo fetch lives in `google_places.py`, not inline in the command

Keeps the service layer testable in isolation and consistent with the existing `search_text` function.

## Risks / Trade-offs

- **Billing**: Each photo fetch incurs a Places Photo request. ~60 places × 2 requests (media metadata + photo binary) adds cost per import run. Mitigation: the skip-if-photo-exists guard limits cost to first-time imports only.
- **Slow imports**: Photo fetches add latency. Mitigation: failure is non-fatal; a single slow request blocks only one place, not the run.
- **Signed URL expiry**: The `photoUri` is time-limited. Mitigation: we fetch immediately after receiving it in the same request cycle.
- **Pillow not installed**: `ImageField.save` requires Pillow. Mitigation: Pillow is already a production dependency (listed in requirements).
