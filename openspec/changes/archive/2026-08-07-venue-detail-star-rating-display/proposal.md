## Why

Dish scores on the venue detail page display as raw decimal numbers (e.g. `4.3`), which is inconsistent with the leaderboard — which now shows star glyphs with a percentage tooltip. Aligning both surfaces creates a consistent visual language for dish quality across the app.

## What Changes

- The score badge on the venue detail page renders as star glyphs (★ / ½ / ☆) instead of a raw decimal.
- A percentage tooltip (via `title` attribute) is shown on hover, e.g. `"86%"`.
- Uses the same `score_as_stars_pct` and `mul` filters introduced in the leaderboard change.

## Capabilities

### New Capabilities

### Modified Capabilities
- `leaderboard-star-rating`: Extend star glyph display to the venue detail page — same bracket mapping and hover tooltip behaviour now applies to `avg_score` on dish cards.

## Impact

- `templates/catalog/venue_detail.html` — score badge updated to use star display with hover tooltip.
- No new filters, model changes, or migrations required.
