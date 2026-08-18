# Spec: venue-suggestion-admin

## Purpose

Give admins a structured workflow to review pending venue suggestions and promote them into the live catalog as either a new `Venue` or a new `VenueLocation` on an existing `Venue`.

---

## Requirements

### Changelist

- `VenueSuggestion` is registered in the Django admin.
- Changelist columns: `name`, `city`, `status`, `search_query`, `created_at`.
- Filterable by: `status`.
- Searchable by: `name`, `city`, `submitter_email`.
- Default ordering: `created_at` descending (newest first).

### Status lifecycle

- New suggestions arrive with `status="pending"`.
- Admins can manually set `status` to `rejected` or `duplicate` via the change form.
- `status` is set to `"approved"` automatically by either promotion action.

### Action: Promote to new Venue

- Available as a **changelist action** ("Promote to new Venue").
- **Only works on a single selected suggestion.** If more than one is selected, the action fails with a user-facing error message.
- Also available as a **button on the suggestion change page**.
- Behaviour on execution:
  1. Creates a `Venue` with `name`, `city`, `source="manual"`, `is_published=False`.
  2. Creates a `VenueLocation` with `venue=new_venue`, `city`, `address`, `website_url` from the suggestion.
  3. Sets `suggestion.status = "approved"` and `suggestion.promoted_venue = new_venue`.
  4. Redirects the admin to the new `Venue` change page.

### Action: Add as location of existing Venue

- Available as a **button on the suggestion change page** only (not in the changelist actions dropdown).
- Clicking navigates to an intermediate admin page showing:
  - Suggestion summary (read-only: name, city, address).
  - A dropdown to select an existing `Venue` (all venues, ordered by name).
  - Submit and Cancel buttons.
- Behaviour on submit:
  1. Creates a `VenueLocation` with `venue=selected_venue`, `city`, `address`, `website_url` from the suggestion.
  2. Sets `suggestion.status = "approved"` and `suggestion.promoted_venue = selected_venue`.
  3. Redirects the admin to the new `VenueLocation` change page.

### Change page (read-only fields)

- `search_query`, `promoted_venue`, `created_at`, `updated_at` are read-only.
- `promoted_venue` displays as a link to the related `Venue` change page once set.

---

## Out of Scope

- Email notification to submitter on status change
- Bulk promotion of multiple suggestions
- Merging duplicate suggestions
