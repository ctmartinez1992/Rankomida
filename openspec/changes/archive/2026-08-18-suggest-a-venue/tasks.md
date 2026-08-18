## 1. Model & Migration

- [x] 1.1 Add `VenueSuggestion` model to `catalog/models.py` with all fields: `name`, `city`, `address`, `website_url`, `notes`, `submitter_name`, `submitter_email`, `search_query`, `status` (choices: pending/approved/rejected/duplicate, default pending), `promoted_venue` (FK to `Venue`, null/blank), `created_at`, `updated_at`
- [x] 1.2 Run `makemigrations catalog` and verify migration file is correct

## 2. Form

- [x] 2.1 Create `VenueSuggestionForm` in `catalog/forms.py` with fields: `name`, `city`, `address`, `website_url`, `notes`, `submitter_name`, `submitter_email` (all except `search_query` which is set by the view)

## 3. Views & URLs

- [x] 3.1 Create `VenueSuggestionCreateView` (GET/POST) in `catalog/views.py` — pre-populates `name` from `?q=`, stores `?q=` as `search_query` on the model, redirects to thanks URL on success
- [x] 3.2 Add URL patterns to `catalog/urls.py`: `venues/suggest/` (name=`suggest_venue`) and `venues/suggest/thanks/` (name=`suggest_venue_thanks`)

## 4. Templates

- [x] 4.1 Create `templates/catalog/suggest_venue.html` — extends `base.html`, renders the suggestion form with field labels and validation errors
- [x] 4.2 Create `templates/catalog/suggest_venue_success.html` — extends `base.html`, shows confirmation message and link back to venue list
- [x] 4.3 Update `templates/catalog/venue_list.html` — add "Suggest a venue →" link (with `?q={{ search_q }}`) inside the empty-results block, only when `search_q` or a filter is active and results are empty

## 5. Admin — Changelist & Change Page

- [x] 5.1 Register `VenueSuggestionAdmin` in `catalog/admin.py` with `list_display`, `list_filter`, `search_fields`, `readonly_fields` (`search_query`, `promoted_venue`, `created_at`, `updated_at`), and default ordering (`-created_at`)

## 6. Admin — Promote to new Venue Action

- [x] 6.1 Implement `promote_to_new_venue` as a changelist action on `VenueSuggestionAdmin` — validates single selection, creates `Venue` (`is_published=False`, `source="manual"`) and `VenueLocation`, sets `suggestion.status="approved"` and `promoted_venue`, redirects to Venue change page
- [x] 6.2 Add a "Promote to new Venue" button on the suggestion change page (via `change_view` override or custom template) that triggers the same logic for the current object

## 7. Admin — Add as Location of Existing Venue Action

- [x] 7.1 Add custom admin URL `/admin/catalog/venuesuggestion/<id>/add-location/` and view that renders an intermediate form with a `Venue` model choice field
- [x] 7.2 On POST of the intermediate form: create `VenueLocation` under selected venue, set `suggestion.status="approved"` and `promoted_venue`, redirect to VenueLocation change page
- [x] 7.3 Add "Add as location of existing Venue" button on the suggestion change page linking to the custom URL from 7.1

## 8. Tests

- [x] 8.1 Test `VenueSuggestionCreateView`: GET renders form; `?q=` pre-fills name; valid POST creates suggestion and redirects; invalid POST re-renders with errors
- [x] 8.2 Test `promote_to_new_venue` action: creates Venue + VenueLocation, marks suggestion approved, blocks multi-selection
- [x] 8.3 Test add-as-location flow: intermediate form renders; POST creates VenueLocation under selected venue, marks suggestion approved
