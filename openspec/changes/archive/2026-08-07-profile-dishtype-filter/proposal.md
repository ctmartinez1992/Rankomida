# Proposal: Profile DishType Filter

## Summary

Add a DishType filter to the user profile ratings list. Users can narrow their visible ratings to a specific dish type (e.g. only Francesinhas or only Pregos), in addition to the existing sort controls.

## Problem

The profile page shows all of a user's ratings in a flat list. As the number of rated dishes grows, there is no way to browse by category. A user who wants to see only their Francesinha ratings must scroll through all submissions.

## Proposed Solution

Add a DishType filter bar to the `ProfileRatingsFragmentView` HTMX fragment. The filter:

- Displays only DishTypes for which the user actually has ratings (dynamic, not all active types).
- Includes an "All" option as the default (no filter).
- Passes the selected `dish_type` slug as a query param alongside the existing `sort` and `page` params.
- Is fully driven by HTMX, consistent with the existing sort bar.

## Scope

- `accounts/views.py` — extend `ProfileRatingsFragmentView` to accept and apply a `dish_type` query param.
- `templates/accounts/_profile_ratings.html` — add filter buttons above the sort bar.
- No changes to models, migrations, URLs, or other apps.

## Out of Scope

- Venue filtering.
- Combining multiple dish types at once.
- Persisting the selected filter across sessions.
