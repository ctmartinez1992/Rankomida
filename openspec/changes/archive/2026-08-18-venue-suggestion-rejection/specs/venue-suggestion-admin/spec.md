# Delta Spec: venue-suggestion-admin (rejection workflow)

Extends `openspec/specs/venue-suggestion-admin/spec.md`.

---

## Additional Requirements

### Model

- `VenueSuggestion` has a `rejection_reason` field (`TextField`, optional).

### Action: Reject suggestion(s)

- Available as a **changelist action** ("Reject suggestion(s)") — supports bulk selection (1 or more).
- Also available as a **button on the suggestion change page** (single object).
- Both paths navigate to an intermediate confirmation page that:
  - Lists the suggestion(s) being rejected (name, city).
  - Provides an optional "Reason" textarea (a single reason applies to all selected).
  - Has "Confirm rejection" and "Cancel" buttons.
- On confirm:
  - Sets `status="rejected"` and `rejection_reason` on each selected suggestion.
  - Redirects to the changelist with a success message: "N suggestion(s) rejected."
- **Guard**: if any selected suggestion already has `status="approved"`, the action is blocked and an error message is shown listing the affected names. No changes are made.

### Change page

- `rejection_reason` is shown in the "Context" fieldset (editable, not read-only).
- The "Reject" button is not shown when `status` is already `"rejected"` or `"approved"`.
