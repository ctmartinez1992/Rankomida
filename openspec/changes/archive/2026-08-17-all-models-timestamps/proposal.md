## Why

`Venue` and `VenueLocation` now carry `created_at` / `updated_at` timestamps. The remaining six models — `DishType`, `Dish`, `SavedDish`, `CriteriaTemplate`, `RatingCriterionScore`, and `UserProfile` — do not. Consistent timestamps across all models enable auditing, ordering by recency, and future API exposure without model-by-model exceptions.

## What Changes

- Add `created_at` (`auto_now_add`) and `updated_at` (`auto_now`) to `DishType`, `Dish`, `CriteriaTemplate`, `RatingCriterionScore`, and `UserProfile`
- Add `updated_at` (`auto_now`) only to `SavedDish` — it already has `saved_at` which serves as `created_at`
- Generate and apply migrations for `catalog`, `ratings`, and `accounts`

## Capabilities

### New Capabilities
- `model-timestamps`: All project models carry `created_at` and `updated_at` (or equivalent) timestamp fields

### Modified Capabilities

## Impact

- `catalog/models.py` — `DishType`, `Dish`, `SavedDish` updated
- `ratings/models.py` — `CriteriaTemplate`, `RatingCriterionScore` updated
- `accounts/models.py` — `UserProfile` updated
- New migrations for `catalog` (0012), `ratings` (check latest), and `accounts` (check latest)
