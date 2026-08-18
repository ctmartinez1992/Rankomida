## 1. Admin Action Wiring

- [x] 1.1 Add `merge_venues` action function to `catalog/admin.py` that validates at least 2 venues are selected, stores the selected IDs in the session, and redirects to the custom merge confirmation URL
- [x] 1.2 Add `get_urls()` to `VenueAdmin` returning a custom route (`merge/`) pointing to a `merge_view` method, and register the action in `VenueAdmin.actions`

## 2. Confirmation Page

- [x] 2.1 Implement the `merge_view` GET handler: resolve venues from session-stored IDs, compute summary (location counts, dish counts, conflicting dish names), pass to template context
- [x] 2.2 Create `templates/admin/catalog/venue/merge_confirmation.html` extending `admin/base_site.html` with: radio list of venues (name, city, dish count, location count), conflict summary section, hidden selected IDs, CSRF token, Confirm and Cancel buttons

## 3. Merge Logic

- [x] 3.1 Implement the `merge_view` POST handler: read survivor ID and selected IDs from POST, call `perform_merge` inside `transaction.atomic`, show success message, redirect to venue changelist
- [x] 3.2 Implement `perform_merge(survivor, venues_to_delete)`: for each non-survivor venue, reassign all `VenueLocation` rows to survivor
- [x] 3.3 In `perform_merge`, for each dish in non-survivor venues: if no name match in survivor, reassign `dish.venue = survivor`; if name match exists, merge into survivor dish and delete the non-survivor dish
- [x] 3.4 In the dish-merge path: for each `RatingSubmission` on the non-survivor dish, reassign to survivor dish if user has no existing submission there, else delete the non-survivor submission (cascades `RatingCriterionScore`)
- [x] 3.5 In the dish-merge path: for each `SavedDish` on the non-survivor dish, reassign to survivor dish if user has not already saved it, else delete the duplicate
- [x] 3.6 After all dishes and locations are handled, delete non-survivor `Venue` rows

## 4. Tests

- [x] 4.1 Test happy path: 3 venues with no dish name conflicts → all locations and dishes reassigned to survivor, non-survivors deleted
- [x] 4.2 Test dish name conflict: non-survivor dish with same name as survivor dish → dishes collapsed, non-conflicting `RatingSubmission` reassigned, conflicting user submission (user already rated survivor dish) deleted
- [x] 4.3 Test `SavedDish` merge: same-name dish collapse reassigns non-conflicting saved dishes and deletes duplicates
- [x] 4.4 Test cancel: POST with cancel action → no data changed
- [x] 4.5 Test single venue guard: selecting 1 venue triggers error message, no redirect
