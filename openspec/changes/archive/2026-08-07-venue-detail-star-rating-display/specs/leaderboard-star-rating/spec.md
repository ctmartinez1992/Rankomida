## MODIFIED Requirements

### Requirement: Leaderboard scores display as star glyphs
The system SHALL display dish scores as a star glyph string (using ★, ½, and ☆ characters) rather than a raw numeric value on both the leaderboard and the venue detail page. The star representation SHALL be derived from a 0–100 percentage scale using the following bracket mapping:

| Percentage range | Stars displayed |
|-----------------|-----------------|
| 96–100          | ★★★★★           |
| 86–95           | ★★★★½           |
| 76–85           | ★★★★            |
| 66–75           | ★★★½            |
| 56–65           | ★★★             |
| 46–55           | ★★½             |
| 36–45           | ★★              |
| 26–35           | ★½              |
| 16–25           | ★               |
| 5–15            | ½               |
| 0–4             | –               |

The percentage SHALL be computed as `avg_score / 5 × 100`, where `avg_score` is the average overall rating on the 0.5–5.0 scale.

#### Scenario: Score renders as full stars on leaderboard
- **WHEN** a dish has an `avg_score` that maps to 96–100%
- **THEN** the leaderboard displays ★★★★★ for that entry

#### Scenario: Score renders as half stars on leaderboard
- **WHEN** a dish has an `avg_score` that maps to 86–95%
- **THEN** the leaderboard displays ★★★★½ for that entry

#### Scenario: Score renders empty marker for very low scores
- **WHEN** a dish has an `avg_score` that maps to 0–4%
- **THEN** the display shows – for that entry

#### Scenario: Score renders as stars on venue detail
- **WHEN** a dish on the venue detail page has an `avg_score`
- **THEN** the score badge displays star glyphs derived from the same bracket mapping

### Requirement: Star rating shows percentage on hover
The star rating display SHALL include a tooltip (via the HTML `title` attribute) showing the exact percentage value (e.g. `"87%"`) when the user hovers over the score. This applies to both the leaderboard and the venue detail page.

The percentage SHALL be rounded to the nearest whole number.

#### Scenario: Hover reveals percentage on leaderboard
- **WHEN** the user hovers over a star rating badge in the leaderboard
- **THEN** a tooltip appears showing the percentage value (e.g. "87%")

#### Scenario: Hover reveals percentage on venue detail
- **WHEN** the user hovers over a star rating badge on the venue detail page
- **THEN** a tooltip appears showing the percentage value (e.g. "87%")

### Requirement: score_as_stars_pct template filter
A `score_as_stars_pct` template filter SHALL be provided in `ratings/templatetags/ratings_tags.py`. It SHALL accept a numeric value in the 0–100 range and return the appropriate star glyph string according to the bracket mapping defined above.

#### Scenario: Filter returns correct stars for boundary values
- **WHEN** the filter receives a value of 96
- **THEN** it returns ★★★★★

#### Scenario: Filter returns dash for None or zero
- **WHEN** the filter receives `None` or `0`
- **THEN** it returns –
