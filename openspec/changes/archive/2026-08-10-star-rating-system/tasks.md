## 1. Model & Validation

- [x] 1.1 Update `CriteriaTemplate.min_score` and `max_score` defaults to `Decimal("1.0")` and `Decimal("5.0")` in `ratings/models.py`
- [x] 1.2 Replace the range check in `RatingCriterionScore.clean()` with a set-membership check against `{1, 1.5, 2, 2.5, 3, 3.5, 4, 4.5, 5}`
- [x] 1.3 Run `python manage.py makemigrations ratings` to generate the migration for the default value changes

## 2. Star Rating Field & Widget

- [x] 2.1 Create `ratings/widgets.py` with `StarRatingWidget` — renders a `<div class="star-widget" role="radiogroup">` containing 9 `<input type="radio">` + `<label>` pairs for values 1, 1.5, 2, 2.5, 3, 3.5, 4, 4.5, 5; labels must have descriptive `aria-label` (e.g. "3.5 stars")
- [x] 2.2 Add `StarRatingField(forms.ChoiceField)` in `ratings/widgets.py` — choices are the 9 half-star values; `to_python()` returns `Decimal`; uses `StarRatingWidget`
- [x] 2.3 Add CSS for `.star-widget` to `static/css/style.css` — hide radio inputs, style labels as stars, use sibling selectors to fill stars on `:checked` and `:hover` states

## 3. Form Update

- [x] 3.1 In `RatingSubmissionForm`, replace `overall_score = forms.DecimalField(...)` with `StarRatingField()`
- [x] 3.2 In `RatingSubmissionForm.__init__`, replace per-criterion `forms.DecimalField(...)` with `StarRatingField()`
- [x] 3.3 Verify `save()` still works — `StarRatingField.to_python()` returns `Decimal`, so no further changes should be needed

## 4. Template Tag

- [x] 4.1 In `ratings/templatetags/ratings_tags.py`, add `score_as_stars` filter: converts `Decimal` (1–5, 0.5 steps) to glyph string (`★★★½☆`); returns `"–"` for `None`, `0`, or out-of-range values
- [x] 4.2 Remove `score_as_percentage` filter

## 5. Templates

- [x] 5.1 Update `templates/catalog/dish_detail.html` — replace `score_as_percentage` with `score_as_stars` in community ratings section
- [x] 5.2 Update `templates/leaderboard/leaderboard.html` — replace `score_as_percentage` with `score_as_stars` in score badge
- [x] 5.3 Update `templates/accounts/profile.html` — replace `score_as_percentage` with `score_as_stars` in ratings list

## 6. Tests

- [x] 6.1 Update `ScoreAsPercentageFilterTests` → rename to `ScoreAsStarsFilterTests`; replace all 1–10 input values and expected percentage strings with 1–5 star values and expected glyph strings; add edge-case tests for out-of-range legacy values
- [x] 6.2 Update `RatingValidationTests` — change `CriteriaTemplate` fixtures to use `max_score=Decimal("5.0")`; update out-of-range test to submit `6.0` instead of `11.0`
- [x] 6.3 Update `AuthenticatedSubmissionIntegrationTests` — change all score fixtures (e.g. `8.0`, `9.0`, `6.0`) to valid 1–5 half-star values; update assertions accordingly
- [x] 6.4 Add `StarRatingFieldTests` — test that `StarRatingField` accepts all 9 valid values, rejects out-of-range values, rejects non-half-step decimals, and returns `Decimal`
- [x] 6.5 Run the full test suite and confirm all tests pass: `python manage.py test ratings`
