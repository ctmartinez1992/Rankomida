## Why

`VenueLocation` records can be created manually or imported from Google Places and updated over time. There is currently no way to know when a location was first added or last modified without digging through migrations or logs. Adding `created_at` and `updated_at` mirrors the pattern already established for `Venue` in the previous change.

## What Changes

- Add `created_at` (`auto_now_add`) and `updated_at` (`auto_now`) fields to the `VenueLocation` model
- Generate and apply a migration for the new fields

## Capabilities

### New Capabilities
- `venue-location-timestamps`: `VenueLocation` records carry creation and last-updated timestamps

### Modified Capabilities

## Impact

- `catalog/models.py` — `VenueLocation` model gains two new auto-populated timestamp fields
- New migration required to add the columns to the database
