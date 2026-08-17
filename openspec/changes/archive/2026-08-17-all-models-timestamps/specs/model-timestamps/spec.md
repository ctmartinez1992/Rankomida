## ADDED Requirements

### Requirement: Universal model timestamps
Every project model MUST have a `created_at` field (auto-set on insert) and an `updated_at` field (auto-set on every save), with the exception that `SavedDish` uses its existing `saved_at` field in place of `created_at`.

#### Scenario: New record created for any covered model
- **WHEN** a `DishType`, `Dish`, `CriteriaTemplate`, `RatingCriterionScore`, or `UserProfile` instance is saved for the first time
- **THEN** `created_at` is set to the current datetime and never changed again

#### Scenario: Existing record saved for any covered model
- **WHEN** any covered model instance is saved after initial creation
- **THEN** `updated_at` is set to the current datetime

#### Scenario: SavedDish record saved
- **WHEN** a `SavedDish` instance is saved
- **THEN** `updated_at` is set to the current datetime
- **THEN** `saved_at` continues to represent the original creation datetime (unchanged)

---

### Requirement: All models timestamp coverage
After this change, every model in the project (`DishType`, `Venue`, `VenueLocation`, `Dish`, `SavedDish`, `CriteriaTemplate`, `RatingSubmission`, `RatingCriterionScore`, `UserProfile`) MUST have either `created_at` or an equivalent auto-creation timestamp field, and an `updated_at` auto-update field.
