## ADDED Requirements

### Requirement: Merge Action Available
An admin action "Merge selected venues into one" SHALL be available on the `Venue` changelist in Django admin.

#### Scenario: Action requires at least two venues
- **WHEN** fewer than 2 venues are selected and the merge action is triggered
- **THEN** an error message is shown and no merge is performed

### Requirement: Intermediate Confirmation Page
Before any data is modified, the admin SHALL be shown a confirmation page.

#### Scenario: Confirmation page shows survivor selection
- **WHEN** the admin triggers the merge action on 2+ venues
- **THEN** they are shown a form with a radio input to select which venue survives, displaying each venue's name, city, location count, and dish count

#### Scenario: Confirmation page shows impact summary
- **WHEN** the confirmation page is rendered
- **THEN** it shows how many locations will be combined, how many dishes will be reassigned, and how many dishes will be auto-merged due to name conflicts

#### Scenario: Cancel aborts with no changes
- **WHEN** the admin clicks Cancel on the confirmation page
- **THEN** no data is modified and the admin is returned to the venue changelist

### Requirement: Atomic Merge Operation
The merge SHALL execute atomically; if any step fails the entire operation is rolled back.

#### Scenario: VenueLocations reassigned
- **WHEN** the merge is confirmed
- **THEN** all `VenueLocation` rows belonging to non-survivor venues are reassigned to the survivor

#### Scenario: Non-conflicting dishes reassigned
- **WHEN** the merge is confirmed and a non-survivor dish's name does not match any dish in the survivor
- **THEN** that dish's `venue` FK is updated to the survivor

#### Scenario: Conflicting dishes collapsed
- **WHEN** the merge is confirmed and a non-survivor dish's name matches a dish in the survivor
- **THEN** the non-survivor dish is deleted after its ratings and saved-dish records are merged into the survivor dish

#### Scenario: Rating reassignment on dish collapse
- **WHEN** a non-survivor dish is collapsed into a survivor dish and the submitting user does NOT already have a rating on the survivor dish
- **THEN** the `RatingSubmission` (and its `RatingCriterionScore` rows) is reassigned to the survivor dish

#### Scenario: Rating dropped on user conflict
- **WHEN** a non-survivor dish is collapsed into a survivor dish and the submitting user ALREADY has a rating on the survivor dish
- **THEN** the non-survivor `RatingSubmission` (and its `RatingCriterionScore` rows) is deleted

#### Scenario: SavedDish reassignment on dish collapse
- **WHEN** a non-survivor dish is collapsed into a survivor dish and the user has NOT already saved the survivor dish
- **THEN** the `SavedDish` row is reassigned to the survivor dish

#### Scenario: SavedDish dropped on user conflict
- **WHEN** a non-survivor dish is collapsed into a survivor dish and the user HAS already saved the survivor dish
- **THEN** the duplicate `SavedDish` row is deleted

#### Scenario: Non-survivor venues deleted
- **WHEN** all locations and dishes have been reassigned
- **THEN** the non-survivor `Venue` rows are deleted
