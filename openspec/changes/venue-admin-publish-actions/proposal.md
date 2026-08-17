## Why

Staff must open each venue individually to toggle its published state. When bulk-importing or reviewing many venues, this is slow and error-prone. Bulk publish/unpublish admin actions let staff update many venues at once from the changelist.

## What Changes

- Add a **Publish selected venues** action to `VenueAdmin` that sets `is_published = True` for all selected rows in a single queryset `update()`.
- Add an **Unpublish selected venues** action to `VenueAdmin` that sets `is_published = False` for all selected rows in a single queryset `update()`.
- Each action displays a success message reporting how many venues were affected.

## Capabilities

### New Capabilities

- `venue-admin-bulk-publish`: Bulk publish and unpublish admin actions for the Venue changelist.

### Modified Capabilities

- `venue-publication-visibility`: The requirement "Staff can publish a venue" now covers bulk operations in addition to per-record edits. No scenario-level behavior changes — existing scenarios remain valid.

## Impact

- `catalog/admin.py` — the only file changed.
- No migrations, no model changes, no API changes.
