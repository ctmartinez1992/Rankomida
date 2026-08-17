## 1. catalog/models.py — Add timestamps

- [x] 1.1 Add `created_at = models.DateTimeField(auto_now_add=True)` and `updated_at = models.DateTimeField(auto_now=True)` to `DishType`
- [x] 1.2 Add `created_at = models.DateTimeField(auto_now_add=True)` and `updated_at = models.DateTimeField(auto_now=True)` to `Dish`
- [x] 1.3 Add `updated_at = models.DateTimeField(auto_now=True)` to `SavedDish` (keep existing `saved_at`)

## 2. ratings/models.py — Add timestamps

- [x] 2.1 Add `created_at = models.DateTimeField(auto_now_add=True)` and `updated_at = models.DateTimeField(auto_now=True)` to `CriteriaTemplate`
- [x] 2.2 Add `created_at = models.DateTimeField(auto_now_add=True)` and `updated_at = models.DateTimeField(auto_now=True)` to `RatingCriterionScore`

## 3. accounts/models.py — Add timestamps

- [x] 3.1 Add `created_at = models.DateTimeField(auto_now_add=True)` and `updated_at = models.DateTimeField(auto_now=True)` to `UserProfile`

## 4. Migrations

- [x] 4.1 Hand-write `catalog/migrations/0012_dishtype_dish_saveddish_timestamps.py` (covers DishType, Dish, SavedDish)
- [x] 4.2 Hand-write `ratings/migrations/0007_criteriatemplate_ratingcriterionscore_timestamps.py` (covers CriteriaTemplate, RatingCriterionScore)
- [x] 4.3 Hand-write `accounts/migrations/0003_userprofile_timestamps.py` (covers UserProfile)

## 5. Admin — readonly_fields updates

- [x] 5.1 In `DishTypeAdmin`: add `readonly_fields = ("created_at", "updated_at")` and append both to `fields`
- [x] 5.2 In `DishAdmin`: add `readonly_fields = ("created_at", "updated_at")` and append both to `fields`
- [x] 5.3 In `SavedDishAdmin`: add `updated_at` to `readonly_fields` and append to any explicit fields list if present

## 6. Verification

- [x] 6.1 Run `python manage.py migrate` and confirm no errors
- [x] 6.2 Run `python manage.py test` and confirm all tests pass
