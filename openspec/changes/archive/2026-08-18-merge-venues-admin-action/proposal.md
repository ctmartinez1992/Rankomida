## Why

Google Places import creates a separate `Venue` row for each location of a chain, but many of these are the same real-world venue with multiple branches. Admins need a way to consolidate these duplicates into one `Venue` with multiple `VenueLocation` rows.

## What Changes

- New admin action "Merge selected venues into one" on the `Venue` changelist
- Intermediate confirmation page where the admin picks the surviving venue
- Atomic merge operation: locations and dishes are reassigned to the survivor; duplicate dishes (same name) are collapsed with their ratings merged; non-survivor venues are deleted

## Capabilities

### New Capabilities

- `venue-merge-admin-action`: Admin action to merge multiple Venue rows into one, consolidating their VenueLocations, Dishes, RatingSubmissions, and SavedDishes into a chosen survivor venue

### Modified Capabilities

<!-- No existing spec-level requirements are changing -->

## Impact

- `catalog/admin.py` — new action, custom URL, intermediate view, merge logic
- `templates/admin/catalog/venue/merge_confirmation.html` — new template
- `ratings` app data is affected at runtime (RatingSubmission and RatingCriterionScore rows may be deleted or reassigned during merge)
- `catalog` app data is affected at runtime (VenueLocation, Dish, SavedDish rows reassigned or deleted)
- No model changes or migrations required
