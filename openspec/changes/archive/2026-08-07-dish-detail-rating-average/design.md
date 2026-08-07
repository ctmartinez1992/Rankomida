## Context

Dish detail pages load via `DishDetailView` (a `DetailView` subclass in `catalog/views.py`). The queryset fetches a single `Dish` with `select_related` but no aggregations. Rating submissions are stored in `RatingSubmission.overall_score`. The leaderboard already uses `Avg` + `Count` annotations on dishes, confirming the pattern is established and performant.

## Goals / Non-Goals

**Goals:**
- Annotate `DishDetailView`'s queryset with `avg_score` and `rating_count`
- Render the summary block in `dish_detail.html` (within the existing `.detail-card`)
- Show "No ratings yet" when `rating_count` is 0

**Non-Goals:**
- Per-criterion score breakdown
- Weighted composite scoring
- Caching or async loading of the aggregate

## Decisions

**Annotate in `get_queryset`, not `get_context_data`**
The dish object itself carries the annotations, keeping the template simple (`dish.avg_score`, `dish.rating_count`). Annotating in `get_context_data` would require a separate queryset call.

**Use `overall_score` field directly**
`RatingSubmission.overall_score` is a user-submitted scalar. No criterion weighting is needed — the user confirmed overall only.

**Avg formatted to one decimal place in template**
`floatformat:1` filter handles display (e.g. 4.2). Django's `Avg` returns `None` when there are no rows, which maps to the "No ratings yet" branch.

## Risks / Trade-offs

- **Extra aggregation on every dish page load** → minimal; it's a single `Avg`+`Count` on indexed FK columns. Acceptable for current scale.
- **`Avg` returns `None` with zero submissions** → handled explicitly in template with `{% if dish.rating_count %}` guard.
