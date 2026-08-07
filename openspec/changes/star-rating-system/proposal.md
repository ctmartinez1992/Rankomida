## Why

The current rating system uses a 1–10 decimal scale entered through a plain number input, which is cognitively awkward and lacks visual feedback. Replacing it with a 1–5 half-star widget gives users a familiar, expressive interface that maps naturally to how people think about quality.

## What Changes

- The `overall_score` and all per-criterion score fields replace plain number inputs with an interactive CSS-only star rating widget
- Scores are constrained to half-star increments: 1, 1.5, 2, 2.5, 3, 3.5, 4, 4.5, 5
- `CriteriaTemplate.min_score` / `max_score` defaults change from 1.0/10.0 to 1.0/5.0
- `RatingCriterionScore.clean()` validation tightened to only accept the nine allowed half-star values
- The `score_as_percentage` template filter is replaced by a `score_as_stars` filter that renders star glyphs (e.g. ★★★½)
- All templates that display scores are updated to use the new filter
- No data migration — existing rows keep their stored values

## Capabilities

### New Capabilities

- `star-rating-input`: CSS-only half-star widget for submitting ratings (1–5 in 0.5 steps), rendered via a custom Django widget and field
- `star-score-display`: Template filter and display helpers that render stored scores as star glyphs across leaderboard, dish detail, and profile pages

### Modified Capabilities

<!-- No existing specs are affected at the requirement level -->

## Impact

- **`ratings/models.py`** — `CriteriaTemplate` defaults and `RatingCriterionScore.clean()` validation
- **`ratings/forms.py`** — `RatingSubmissionForm` field types
- **`ratings/widgets.py`** — new file
- **`ratings/templatetags/ratings_tags.py`** — filter replacement
- **`static/css/style.css`** — star widget CSS
- **`templates/ratings/rating_form.html`**, **`templates/catalog/dish_detail.html`**, **`templates/leaderboard/leaderboard.html`**, **`templates/accounts/profile.html`** — updated to use new filter
- **`ratings/tests.py`** — all 1–10 fixtures replaced with 1–5 values; new tests added
- New migration for `CriteriaTemplate` default changes
