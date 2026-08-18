# Delta Spec: venue-suggestion-admin (user tracking)

Extends `openspec/specs/venue-suggestion-admin/spec.md`.

---

## Additional Requirements

- `submitted_by` is shown in the changelist `list_display` (alongside `name`, `city`, `status`).
- `submitted_by` is a read-only field on the suggestion change page, displayed in the "Submitter" section alongside `submitter_name` and `submitter_email`.
