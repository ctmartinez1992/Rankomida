## Why

Leaderboard scores are currently shown as raw numbers (e.g. `4.3`), which is not immediately meaningful to users. Displaying scores as star ratings — with the exact percentage available on hover — makes rankings instantly scannable and communicates quality in a familiar, intuitive format.

## What Changes

- The leaderboard score badge renders as star glyphs (★ / ½ / ☆) instead of a raw numeric score.
- A tooltip on hover shows the exact percentage (e.g. "87%"), derived from the score scaled to 0–100.
- The star bracket mapping follows a 10-point-per-half-star scheme: 96–100 = 5 stars, 86–95 = 4.5 stars, 76–85 = 4 stars, etc.
- A new `score_as_stars_pct` template filter is added to `ratings/templatetags/ratings_tags.py` that accepts a 0–100 value and returns the appropriate star glyph string.
- The leaderboard template is updated to convert `sort_score` to a percentage and pass it through the new filter, with the percentage shown in a `title` attribute for hover.

## Capabilities

### New Capabilities
- `leaderboard-star-rating`: Display of leaderboard scores as star glyphs with percentage tooltip on hover.

### Modified Capabilities

## Impact

- `ratings/templatetags/ratings_tags.py` — new `score_as_stars_pct` filter added.
- `templates/leaderboard/leaderboard.html` — score badge updated to use star display with hover tooltip.
- No model, migration, or URL changes required.
