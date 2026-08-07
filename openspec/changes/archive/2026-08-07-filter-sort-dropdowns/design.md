## Context

Filter and sort controls across the app currently use pill buttons rendered via `{% for %}` loops. Each button fires an HTMX `hx-get` request. The "active" option is visually highlighted with `btn-active`. There are two fragments affected:

- **`_profile_ratings.html`**: two pill rows — dish-type filter + sort order
- **`_community_notes.html`**: one pill row — sort order only

The goal is to replace both with compact, labelled `<select>` dropdowns that use `hx-trigger="change"`.

## Goals / Non-Goals

**Goals:**
- Replace all pill-button filter/sort rows with `<select>` dropdowns
- Labels live outside the `<select>` in a flex row (user's stated preference)
- Preserve all existing HTMX behaviour (same query params, same targets, same swap)
- Style the dropdowns consistently with the existing form inputs in the app

**Non-Goals:**
- Custom JS dropdown components or styled select libraries
- Changing the backend query param names or view logic
- Changing pagination controls

## Decisions

### Decision: Label outside `<select>`, not as a disabled first option

Labels (`<label>` elements) sit beside the `<select>` in a `.filter-bar` flex container. This is cleaner than a disabled placeholder option and plays better with screen readers.

```
<div class="filter-bar">
  <label for="sort-select">Sort by</label>
  <select id="sort-select" hx-get="..." hx-trigger="change" ...>
    <option value="newest">Newest</option>
    ...
  </select>
</div>
```

### Decision: Native `<select>` element, no JS widget

The existing app uses no JS UI library. Native `<select>` is consistent, accessible, and zero-dependency. The downside (limited cross-browser styling) is acceptable for this app's style.

### Decision: `hx-trigger="change"` replaces `hx-get` on buttons

`<select>` has no `click` event equivalent for triggering on option selection — `change` is the correct event. The rest of the HTMX attributes (`hx-target`, `hx-swap`) remain identical.

### Decision: CSS lives in `base.html` inline `<style>` block

All app CSS is currently inline in `base.html`. Adding `.filter-bar` and `select` styles there is consistent. The old `.community-notes-sort .btn-active` rule is removed; `.community-notes-sort` itself can be repurposed as `.filter-bar` or removed entirely.

## Risks / Trade-offs

- **Native select styling is limited on some browsers** → Acceptable; the app does not target custom-styled dropdowns elsewhere.
- **Change fires on every option change** → This matches the existing pill behaviour (every click fires immediately). No new UX surprise.
