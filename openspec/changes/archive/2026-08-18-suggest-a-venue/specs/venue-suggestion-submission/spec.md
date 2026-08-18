# Spec: venue-suggestion-submission

## Purpose

Allow any site visitor to suggest a venue that is missing from the catalog, triggered from the "no results" state of the venue search.

---

## Requirements

### Access

- The suggestion form is publicly accessible — no authentication required.
- The form is reachable at `/venues/suggest/`.

### Pre-fill from search context

- When the venue list returns no results and the user had a search query, the "no results" message includes a link to the suggestion form with the search term passed as `?q=<search_q>`.
- The form pre-populates the `name` field from the `?q=` query parameter.
- The `?q=` value is also stored as `search_query` on the submitted `VenueSuggestion` for admin context.

### Form fields

| Field | Required | Notes |
|---|---|---|
| `name` | Yes | Venue name |
| `city` | Yes | City of the venue |
| `address` | No | Street address |
| `website_url` | No | Must be a valid URL if provided |
| `notes` | No | Free text — additional context for the admin |
| `submitter_name` | No | Visitor's name |
| `submitter_email` | No | Must be a valid email if provided |

### Submission behaviour

- On valid POST: create a `VenueSuggestion` with `status="pending"` and redirect to `/venues/suggest/thanks/`.
- On invalid POST: re-render the form with validation errors.
- On GET: render the blank form (pre-filled from `?q=` if present).

### Success page

- `/venues/suggest/thanks/` renders a confirmation message and a link back to the venue list.

### Venue list integration

- The "Suggest a venue" call-to-action is shown **only when the result set is empty** (after any active search/filter).
- It is not shown when the full unfiltered list is displayed.

---

## Out of Scope

- Spam protection / reCAPTCHA (can be layered on later using the `form-recaptcha` spec)
- Duplicate detection at submission time
- Email confirmation to the submitter
- Authentication gates
