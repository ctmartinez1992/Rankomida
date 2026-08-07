## Why

The current pill-button approach for filter and sort controls occupies significant horizontal space and wraps awkwardly on small screens. Replacing them with labelled `<select>` dropdowns reduces visual clutter, makes controls self-documenting, and aligns with standard HTML form conventions across the app.

## What Changes

- The dish-type filter pill buttons on the profile ratings fragment are replaced by a labelled `<select>` dropdown.
- The sort pill buttons on the profile ratings fragment are replaced by a labelled `<select>` dropdown.
- The sort pill buttons on the community notes fragment (dish detail page) are replaced by a labelled `<select>` dropdown.
- HTMX interaction switches from `hx-get` on `<button>` to `hx-get` + `hx-trigger="change"` on `<select>`.
- The `.community-notes-sort` pill-row CSS is replaced with a `.filter-bar` flex row that hosts label+select pairs.

## Capabilities

### New Capabilities

- `filter-sort-dropdowns`: `<select>`-based filter and sort controls with external labels for ratings and community notes fragments.

### Modified Capabilities

- `profile-dishtype-filter`: The dish-type filter UI changes from pill buttons to a `<select>` dropdown; all existing behavioural requirements remain unchanged.

## Impact

- `templates/catalog/_community_notes.html` — sort control markup
- `templates/accounts/_profile_ratings.html` — dish-type filter and sort control markup
- `templates/base.html` — inline CSS: add `.filter-bar` + `select` styles; remove `.community-notes-sort .btn-active` pill override
