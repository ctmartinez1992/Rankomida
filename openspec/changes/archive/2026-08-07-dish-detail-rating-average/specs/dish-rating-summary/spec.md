## ADDED Requirements

### Requirement: Dish detail shows average rating and count
The dish detail page SHALL display the average `overall_score` and total number of ratings for the dish, computed from all `RatingSubmission` records for that dish.

#### Scenario: Dish has ratings
- **WHEN** a user views a dish detail page that has one or more rating submissions
- **THEN** the page SHALL display the average overall score (rounded to one decimal place) and the total rating count

#### Scenario: Dish has no ratings
- **WHEN** a user views a dish detail page that has zero rating submissions
- **THEN** the page SHALL display "No ratings yet" in place of the score and count
