## Why

Dish detail pages currently show no aggregate rating information — visitors see individual community notes but have no quick sense of how a dish is rated overall. Displaying the average score and rating count gives users an immediate signal of community consensus.

## What Changes

- `DishDetailView` annotates its queryset with `avg_score` (average of `overall_score`) and `rating_count`
- `dish_detail.html` renders a rating summary block showing the average score and count, or "No ratings yet" when no submissions exist

## Capabilities

### New Capabilities

- `dish-rating-summary`: Display average overall score and total rating count on the dish detail page, with a "No ratings yet" fallback

### Modified Capabilities

<!-- none -->

## Impact

- `catalog/views.py` — `DishDetailView.get_queryset()` (add `Avg` + `Count` annotations)
- `templates/catalog/dish_detail.html` — new rating summary block in the detail card
- No new models, URLs, migrations, or dependencies
