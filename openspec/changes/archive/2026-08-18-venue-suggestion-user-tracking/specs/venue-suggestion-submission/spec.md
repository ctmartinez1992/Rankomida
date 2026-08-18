# Delta Spec: venue-suggestion-submission (user tracking)

Extends `openspec/specs/venue-suggestion-submission/spec.md`.

---

## Additional Requirements

### Authenticated submission

- When the submitting user is authenticated, `submitter_name` and `submitter_email` fields are **not shown** in the form.
- A hint is shown instead, e.g. "Submitting as \<username\>".
- `submitted_by` is set to the authenticated user when the suggestion is saved.
- All other form fields and validation behaviour are unchanged.

### Anonymous submission

- Behaviour is unchanged from the existing spec.
- `submitted_by` is left null.

### Thanks page (authenticated)

- When the submitting user is authenticated, the success page includes a message referencing their profile and a link to it: "You can track the status of your suggestion on your profile."
- When anonymous, the existing message is shown unchanged.
