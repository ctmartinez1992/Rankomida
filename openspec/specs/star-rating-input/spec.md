## Purpose

Define half-star score input for overall and per-criterion ratings via a CSS-only radio star widget.

## Requirements

### Requirement: Star rating field accepts only valid half-star values
The system SHALL constrain score inputs (overall and per-criterion) to the set {1, 1.5, 2, 2.5, 3, 3.5, 4, 4.5, 5}. Submissions with any other value SHALL be rejected with a validation error.

#### Scenario: Valid whole-star value accepted
- **WHEN** a user submits a rating with `overall_score = 4`
- **THEN** the submission is saved successfully

#### Scenario: Valid half-star value accepted
- **WHEN** a user submits a rating with `overall_score = 3.5`
- **THEN** the submission is saved successfully

#### Scenario: Out-of-range value rejected
- **WHEN** a user submits a rating with `overall_score = 6`
- **THEN** the form returns a validation error and the submission is not saved

#### Scenario: Decimal not on half-star boundary rejected
- **WHEN** a user submits a rating with `overall_score = 2.3`
- **THEN** the form returns a validation error and the submission is not saved

#### Scenario: Zero rejected
- **WHEN** a user submits a rating with `overall_score = 0`
- **THEN** the form returns a validation error and the submission is not saved

### Requirement: Star widget renders as radio inputs
The system SHALL render each star score field as a group of `<input type="radio">` elements, one per allowed value, within a container with `class="star-widget"`.

#### Scenario: Widget renders correct number of inputs
- **WHEN** a star rating field is rendered in a form
- **THEN** the HTML contains exactly 9 radio inputs for the 9 allowed values

#### Scenario: Pre-existing score is pre-selected
- **WHEN** a user opens the rating form for a dish they have already rated
- **THEN** the radio input corresponding to their existing score is marked `checked`

### Requirement: Star widget is operable without JavaScript
The system SHALL submit the star rating value using only native HTML form mechanics. No JavaScript SHALL be required to select a value or submit the form.

#### Scenario: Form submits without JS
- **WHEN** JavaScript is disabled in the browser and the user selects a star value and submits
- **THEN** the server receives the correct score value and saves the submission

### Requirement: Model enforces half-star constraint
`RatingCriterionScore.clean()` SHALL raise a `ValidationError` when the stored `score` is not in the set {1, 1.5, 2, 2.5, 3, 3.5, 4, 4.5, 5}.

#### Scenario: Score on valid half-star boundary passes
- **WHEN** `RatingCriterionScore.clean()` is called with `score = 1.5`
- **THEN** no `ValidationError` is raised

#### Scenario: Score outside boundary fails
- **WHEN** `RatingCriterionScore.clean()` is called with `score = 7.0`
- **THEN** a `ValidationError` is raised

### Requirement: CriteriaTemplate defaults to 1–5 range
New `CriteriaTemplate` instances SHALL default to `min_score = 1.0` and `max_score = 5.0`.

#### Scenario: Default values on new template
- **WHEN** a `CriteriaTemplate` is created without specifying `min_score` or `max_score`
- **THEN** `min_score` equals `1.0` and `max_score` equals `5.0`
