## Why

Admins reviewing venue suggestions need a first-class way to explicitly decline them and record why (e.g. "venue already exists", "outside our scope", "duplicate of X"). Currently, rejection requires manually editing the status field on the change form — no reason can be stored, and there is no streamlined bulk action for it.

## What Changes

- New `rejection_reason` field on `VenueSuggestion` to persist the admin's stated reason for declining a suggestion.
- **"Reject suggestion(s)"** admin action, available in both the changelist (bulk) and as a button on the individual change page.
- Both paths route through an intermediate confirmation form where the admin optionally enters a reason before confirming.
- `rejection_reason` is surfaced read-only on the change page when a suggestion has been rejected.
- Reject action is blocked with a clear error if any selected suggestion is already approved.

## Capabilities

### New Capabilities

<!-- None -->

### Modified Capabilities

- `venue-suggestion-admin`: adds reject action, rejection reason field, and associated intermediate form.

## Impact

- **Model change**: `rejection_reason = TextField(blank=True)` on `catalog.VenueSuggestion` — new migration required.
- **Admin change**: `catalog/admin.py` — new reject action, custom URL + view, updated fieldset.
- **New admin template**: `admin/catalog/venuesuggestion/reject_confirmation.html`
- **Template change**: `admin/catalog/venuesuggestion/change_form.html` — add "Reject" button.
- **No breaking changes.**
