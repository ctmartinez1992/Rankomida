## Why

The Django admin for venues currently shows a `source` column that provides low-value information for day-to-day operations. Operators need visibility into when venues were created and last updated so they can quickly audit recent additions and changes without opening individual records.

## What Changes

- Add `created_at` and `updated_at` timestamp fields to the `Venue` model
- Update `VenueAdmin` list display to show `created_at` and `updated_at` instead of `source`
- Enable sorting on both date columns in the admin list view
- Remove `source` from the admin list display (it remains on the model and edit form)

## Capabilities

### New Capabilities
- `venue-admin-date-columns`: Venue admin list view shows created/updated timestamps with sort support

### Modified Capabilities

## Impact

- `catalog/models.py` — `Venue` model gains two new auto-populated timestamp fields
- `catalog/admin.py` — `VenueAdmin.list_display` updated; `source` removed, date columns added
- A new migration required to add the columns to the database
