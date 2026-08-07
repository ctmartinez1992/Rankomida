## Purpose

Define how profile rating entries display comment text and submission timestamps.

## Requirements

### Requirement: Profile rating entry shows comment text
Each rating entry in the profile ratings list SHALL display the comment text when the `RatingSubmission.comment` field is non-empty, truncated to a maximum of 100 words.

#### Scenario: Comment is present
- **WHEN** a `RatingSubmission` has a non-empty `comment` value
- **THEN** the profile ratings list SHALL render the comment text below the dish/venue name, truncated to 100 words

#### Scenario: Comment is empty
- **WHEN** a `RatingSubmission` has an empty `comment` value (empty string or blank)
- **THEN** the profile ratings list SHALL render no comment element for that entry

### Requirement: Profile rating entry shows submission time
Each rating entry in the profile ratings list SHALL display both the date and time of submission.

#### Scenario: Date and time display
- **WHEN** a rating entry is rendered
- **THEN** the submission timestamp SHALL be formatted as `d M Y, H:i` (e.g. `12 Jul 2026, 14:32`)
