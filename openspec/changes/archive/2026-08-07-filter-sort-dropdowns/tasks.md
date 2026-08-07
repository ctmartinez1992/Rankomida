## 1. CSS

- [x] 1.1 Add `.filter-bar` flex row style to `base.html` (gap, margin-bottom, align-items)
- [x] 1.2 Add `select` element styles to `base.html` (border, border-radius, padding, font, background, cursor)
- [x] 1.3 Remove `.community-notes-sort .btn-active` CSS rule from `base.html`
- [x] 1.4 Replace `.community-notes-sort` flex styles with `.filter-bar` (or repurpose selectors)

## 2. Community Notes Fragment

- [x] 2.1 Replace sort pill-button loop in `_community_notes.html` with a `.filter-bar` div containing a `<label>` and `<select hx-get hx-trigger="change" hx-target hx-swap>`
- [x] 2.2 Ensure selected `<option>` matches `current_sort` on render

## 3. Profile Ratings Fragment

- [x] 3.1 Replace dish-type pill-button block in `_profile_ratings.html` with a `.filter-bar` div containing `<label>` and `<select>` with HTMX attributes
- [x] 3.2 Ensure "All" option is present (value="") and selected when no dish_type active
- [x] 3.3 Ensure each DishType option's value is `dt.slug` and pre-selected when it matches `current_dish_type`
- [x] 3.4 Replace sort pill-button loop with a `.filter-bar` div containing `<label>` and `<select>` preserving `current_dish_type` in the HTMX request
- [x] 3.5 Ensure selected sort option matches `current_sort` on render
- [x] 3.6 Keep dish-type filter hidden when `dish_types|length <= 1`

## 4. Verification

- [x] 4.1 Run `python manage.py test` and confirm all tests pass
