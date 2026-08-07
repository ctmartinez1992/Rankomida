## ADDED Requirements

### Requirement: score_as_stars filter renders star glyphs
The system SHALL provide a `score_as_stars` template filter that converts a numeric score (1–5, 0.5 steps) to a string of star glyphs. Filled positions use `★`, a half position uses `½`, and empty positions use `☆`. The output always spans 5 star positions.

#### Scenario: Whole-number score renders correctly
- **WHEN** `score_as_stars` is applied to `Decimal("3")`
- **THEN** the output is `"★★★☆☆"`

#### Scenario: Half-star score renders correctly
- **WHEN** `score_as_stars` is applied to `Decimal("3.5")`
- **THEN** the output is `"★★★½☆"`

#### Scenario: Minimum score renders correctly
- **WHEN** `score_as_stars` is applied to `Decimal("1")`
- **THEN** the output is `"★☆☆☆☆"`

#### Scenario: Maximum score renders correctly
- **WHEN** `score_as_stars` is applied to `Decimal("5")`
- **THEN** the output is `"★★★★★"`

#### Scenario: None or zero returns dash
- **WHEN** `score_as_stars` is applied to `None` or `0`
- **THEN** the output is `"–"`

#### Scenario: Out-of-range value is clamped gracefully
- **WHEN** `score_as_stars` is applied to a value outside 1–5 (e.g. a legacy 7.5 score)
- **THEN** the filter returns `"–"` rather than raising an exception

### Requirement: Star scores displayed on dish detail page
The community ratings section on the dish detail page SHALL display each submission's `overall_score` using `score_as_stars`.

#### Scenario: Submission score shown as stars
- **WHEN** a user views a dish detail page that has at least one rating
- **THEN** each rating entry shows the score as star glyphs

### Requirement: Star scores displayed on leaderboard
The leaderboard `score-badge` SHALL display each dish's `sort_score` using `score_as_stars`.

#### Scenario: Leaderboard score shown as stars
- **WHEN** a user views the leaderboard
- **THEN** each entry's score is shown as star glyphs alongside the rating count

### Requirement: Star scores displayed on profile page
The profile ratings list SHALL display each submission's `overall_score` using `score_as_stars`.

#### Scenario: Profile score shown as stars
- **WHEN** a user views a profile page with ratings
- **THEN** each rating entry shows the score as star glyphs
