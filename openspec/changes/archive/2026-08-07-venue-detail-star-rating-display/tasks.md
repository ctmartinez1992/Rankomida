## 1. Template Update

- [x] 1.1 Replace `{{ dish.avg_score|floatformat:1 }}` in `templates/catalog/venue_detail.html` with `{{ dish.avg_score|mul:20|score_as_stars_pct }}` and add a `title` attribute showing the rounded percentage (e.g. `"86%"`)
