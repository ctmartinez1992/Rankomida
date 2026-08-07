## MODIFIED Requirements

### Requirement: Dish-type filter is rendered as a dropdown
The dish-type filter SHALL be rendered as a native `<select>` element with an external label, replacing the former pill-button row. All filtering logic, visibility rules, and state-preservation behaviour remain unchanged.

#### Scenario: Filter hidden when single type
- **WHEN** the viewed user has ratings for only one DishType
- **THEN** the dish-type filter control SHALL NOT be rendered

#### Scenario: Filter shows only rated active types
- **WHEN** the dish-type filter is rendered
- **THEN** it SHALL list only DishTypes that are `is_active=True` and for which the viewed user has at least one rating, plus an "All" option

#### Scenario: All option selected by default
- **WHEN** no `dish_type` query param is present
- **THEN** the "All" option SHALL be selected in the dropdown

#### Scenario: Known slug pre-selected
- **WHEN** `dish_type` matches a known slug in the dropdown
- **THEN** that option SHALL be pre-selected

#### Scenario: Unknown slug falls back to All
- **WHEN** `dish_type` does not match any known slug
- **THEN** the filter SHALL behave as if no dish_type was specified (show all ratings)
