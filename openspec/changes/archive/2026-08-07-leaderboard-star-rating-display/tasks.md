## 1. Template Filter

- [x] 1.1 Add `score_as_stars_pct` filter to `ratings/templatetags/ratings_tags.py` — accepts a 0–100 numeric value and returns the star glyph string using the 10-point-per-half-star bracket mapping
- [x] 1.2 Add `mul` filter to `ratings/templatetags/ratings_tags.py` — multiplies a value by a given argument (e.g. `{{ score|mul:20 }}`) to enable percentage conversion in templates

## 2. Leaderboard Template

- [x] 2.1 Update the score badge in `templates/leaderboard/leaderboard.html` to convert `sort_score` to a percentage using the `mul` filter and render it through `score_as_stars_pct`
- [x] 2.2 Add a `title` attribute to the score badge element containing the rounded percentage (e.g. `"87%"`) for the hover tooltip

## 3. Tests

- [x] 3.1 Add unit tests for `score_as_stars_pct` in `ratings/tests.py` covering: boundary values (0, 4, 5, 15, 16, 95, 96, 100), `None` input, and mid-range values
- [x] 3.2 Verify existing `score_as_stars` tests still pass (no regressions)
