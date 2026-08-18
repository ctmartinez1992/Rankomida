## 1. Model & Migration

- [x] 1.1 Add `rejection_reason = models.TextField(blank=True)` to `VenueSuggestion` in `catalog/models.py`
- [x] 1.2 Run `makemigrations catalog` and verify migration file

## 2. Admin — Reject View & URL

- [x] 2.1 Add custom admin URL `/admin/catalog/venuesuggestion/reject/` to `VenueSuggestionAdmin.get_urls()` and implement `reject_view`: GET renders confirmation form with supplied `ids`; validates no approved suggestions in selection; POST processes rejection and redirects to changelist
- [x] 2.2 Add `rejection_reason` to the "Context" fieldset in `VenueSuggestionAdmin` (editable, not read-only)

## 3. Admin — Changelist Action

- [x] 3.1 Implement `reject_suggestions` changelist action that collects selected IDs and redirects to the reject view URL (`/admin/catalog/venuesuggestion/reject/?ids=...`)

## 4. Template

- [x] 4.1 Create `templates/admin/catalog/venuesuggestion/reject_confirmation.html` — extends `admin/base_site.html`, lists suggestions being rejected, shows optional reason textarea, submit and cancel buttons
- [x] 4.2 Update `templates/admin/catalog/venuesuggestion/change_form.html` — add "Reject" button in object-tools block, hidden when status is already `rejected` or `approved`

## 5. Tests

- [x] 5.1 Test reject action on a single pending suggestion: sets status to rejected, stores reason, redirects to changelist
- [x] 5.2 Test bulk reject on multiple pending suggestions: all updated with same reason
- [x] 5.3 Test guard: reject action blocked when any selected suggestion is already approved
- [x] 5.4 Test reject confirmation page renders correctly (GET with ids param)
