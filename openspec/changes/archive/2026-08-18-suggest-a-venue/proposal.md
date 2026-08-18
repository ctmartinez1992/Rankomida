## Why

Users searching for a venue that doesn't exist in the catalog have no way to contribute it. A "suggest a venue" flow captures community knowledge and feeds an admin curation queue, reducing the friction between discovery and catalog growth.

## What Changes

- When a venue search returns no results, a contextual "Suggest a venue" call-to-action appears.
- A new public form at `/venues/suggest/` lets any visitor submit a missing venue (name, city, address, website, notes, optional contact info). The name field is pre-filled from the search query via `?q=`.
- A new `VenueSuggestion` model in the `catalog` app stores submissions with status tracking (`pending`, `approved`, `rejected`, `duplicate`).
- A dedicated admin changelist for `VenueSuggestion` with two promotion paths:
  - **"Promote to new Venue"** — creates a `Venue` + `VenueLocation` from the suggestion data and marks it approved.
  - **"Add as location of existing Venue"** — via an intermediate admin form, creates a `VenueLocation` under a selected existing `Venue` and marks the suggestion approved.

## Capabilities

### New Capabilities

- `venue-suggestion-submission`: Public form and view that lets any visitor submit a missing venue, pre-filled from the search "no results" context.
- `venue-suggestion-admin`: Admin changelist and custom actions to review, promote, or reject venue suggestions.

### Modified Capabilities

<!-- None — suggestions are a separate model; no existing spec-level requirements change. -->

## Impact

- **New model**: `catalog.VenueSuggestion` — new migration required.
- **New URLs + views**: `GET/POST /venues/suggest/`, `GET /venues/suggest/thanks/`.
- **New templates**: `catalog/suggest_venue.html`, `catalog/suggest_venue_success.html`.
- **Template change**: `catalog/venue_list.html` — "Suggest a venue" link when result set is empty.
- **Admin change**: `catalog/admin.py` — new `VenueSuggestionAdmin` with custom actions and intermediate promotion form.
- **No breaking changes.**
