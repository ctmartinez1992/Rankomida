## 1. View Layer

- [x] 1.1 In `DishDetailView.get_queryset()`, add `Avg("rating_submissions__overall_score")` as `avg_score` and `Count("rating_submissions", distinct=True)` as `rating_count` annotations

## 2. Template

- [x] 2.1 In `templates/catalog/dish_detail.html`, add a rating summary block inside `.detail-card` that shows `dish.avg_score|floatformat:1` and `dish.rating_count` when ratings exist, or "No ratings yet" when `rating_count` is 0

## 3. Tests

- [x] 3.1 Add a test in `catalog/tests.py` verifying the dish detail view context includes `avg_score` and `rating_count` when submissions exist
- [x] 3.2 Add a test verifying `avg_score` is `None` and `rating_count` is 0 when no submissions exist
