## 1. Configuration

- [x] 1.1 Add `GOOGLE_MAPS_API_KEY = os.environ.get('GOOGLE_MAPS_API_KEY', '')` to `config/settings.py`, following the existing reCAPTCHA pattern
- [x] 1.2 Add a commented `GOOGLE_MAPS_API_KEY=` placeholder to `.env.example` with a note that the import command requires it
- [x] 1.3 Add pinned `requests` to `requirements.txt`

## 2. Data model

- [x] 2.1 Add `is_published` (default `True`) and `source` (`manual` / `google`, default `manual`) to `Venue`
- [x] 2.2 Add `google_place_id` (unique, nullable) to `VenueLocation`
- [x] 2.3 Add the remaining Google fields to `VenueLocation`: `business_status`, `postal_code`, `neighbourhood`, `phone`, `website_url`, `google_maps_uri`, `price_level`, `primary_type`, `types`, `opening_hours`, `google_rating`, `google_user_rating_count`, `last_synced_at`
- [x] 2.4 Create and apply the migration (`0009`). The 14 existing venues were deleted in admin before this ran, so the published default is covered by test 7.10 instead

## 3. Places API client

- [x] 3.1 Add `catalog/services/google_places.py` with a Text Search call against `places.googleapis.com/v1/places:searchText`
- [x] 3.2 Define the field mask as a single module constant (id, displayName, formattedAddress, addressComponents, location, businessStatus, primaryType, types, priceLevel, regularOpeningHours, nationalPhoneNumber, websiteUri, googleMapsUri, rating, userRatingCount, nextPageToken)
- [x] 3.3 Send `languageCode=pt-PT` and `regionCode=PT`; support `pageSize` and `pageToken`
- [x] 3.4 Implement pagination with a delay before using a fresh page token and retry with backoff when the token is rejected as not yet valid
- [x] 3.5 Raise a typed error on HTTP and payload failures; never log the API key

## 4. Import command

- [x] 4.1 Create `catalog/management/` and `catalog/management/commands/` packages
- [x] 4.2 Add `import_google_places.py` with `--query` (repeatable, defaults to "francesinha porto" and "prego porto"), `--city` (default Porto), `--max-pages` (default 3), and `--dry-run`
- [x] 4.3 Fail with `CommandError` before any request when the API key is unset
- [x] 4.4 Map a place to model fields: display name to venue name, unique slug from the name, `locality` to city with `--city` as fallback, `sublocality` (or `administrative_area_level_2`) to neighbourhood, postal code from address components
- [x] 4.5 Upsert on `google_place_id`: create venue plus location when absent, update only the Google fields and `last_synced_at` when present
- [x] 4.6 Set `is_published=False` and `source='google'` on creation only; never alter them on update
- [x] 4.7 Never modify `Venue.name`, `slug`, `photo`, or photo attribution on update
- [x] 4.8 Deduplicate places within a single run so a place returned by two queries is processed once
- [~] 4.9 Flag probable duplicates against venues with no `google_place_id` — removed: the catalog was cleared, so there is nothing to match against
- [x] 4.10 In dry-run mode, report planned creates and updates without writing
- [x] 4.11 Log and skip individual place failures; log and continue past a failed query
- [x] 4.12 Print a closing summary of created, updated, and skipped counts

## 5. Public visibility

- [x] 5.1 Filter `VenueListView` to `is_published=True`, including the `cities` context queryset
- [x] 5.2 Filter `VenueDetailView` to `is_published=True`

## 6. Admin

- [x] 6.1 Add `is_published` and `source` to `VenueAdmin` fields, `list_display`, and `list_filter`
- [x] 6.2 Expose the Google fields on `VenueLocationInline`, with `google_place_id` and `last_synced_at` read-only

## 7. Tests

- [x] 7.1 Import creates venue and location from a mocked response, unpublished, with fields mapped
- [x] 7.2 Re-running against the same mocked response creates nothing and refreshes changed fields
- [x] 7.3 Re-run preserves a staff-edited venue name and a staff-set published state
- [x] 7.4 Dry run leaves venue and location counts unchanged
- [x] 7.5 Slug collision with an existing venue produces a distinct slug
- [x] 7.6 A place returned by two queries is imported once
- [x] 7.7 Missing API key exits with an error and issues no requests
- [x] 7.8 A malformed place is skipped and the rest of the batch still imports
- [~] 7.9 Probable duplicate is reported and still imported — removed alongside 4.9
- [x] 7.10 Venue list and detail exclude unpublished venues; city options ignore them
- [x] 7.11 A failed query is logged and the remaining queries still run

## 8. Verification

- [x] 8.1 Run `--dry-run` against the live API and review the planned writes (62 places, no writes made)
- [x] 8.2 Run for real (62 created, all unpublished), re-run to confirm idempotency (62 updated, 0 created), and confirm `/venues/` shows no imported venue and their detail pages 404
