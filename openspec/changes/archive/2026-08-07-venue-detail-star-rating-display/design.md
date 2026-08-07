## Context

The leaderboard already displays star glyphs via `score_as_stars_pct` and `mul` filters, with a `title` tooltip for the percentage. The venue detail page still shows `avg_score|floatformat:1` (e.g. `4.3`). Both surfaces use the same underlying value — `Avg("rating_submissions__overall_score")` on the 0.5–5.0 scale. The change is purely in the template.

## Goals / Non-Goals

**Goals:**
- Replace `{{ dish.avg_score|floatformat:1 }}` in `templates/catalog/venue_detail.html` with star glyphs and percentage tooltip, matching the leaderboard display exactly.

**Non-Goals:**
- Changing filters, views, models, or any other template.
- Applying the star display to dish detail or other catalog pages (out of scope for this change).

## Decisions

### Reuse existing filters
`score_as_stars_pct` and `mul` are already registered in `ratings_tags`. The venue detail template just needs `{% load ratings_tags %}` (already present) and the same filter chain as the leaderboard: `{{ dish.avg_score|mul:20|score_as_stars_pct }}`.

No new code needed — this is a one-line template change plus a `title` attribute.

## Risks / Trade-offs

- [None significant] This is a pure template change using already-tested filters. Risk is minimal.
