## MODIFIED Requirements

### Requirement: Staff can import venues from Google Places by search query
The system SHALL provide a management command that queries Google Places Text Search for one or more caller-supplied queries and creates a `Venue` and a `VenueLocation` for each distinct place returned. The command SHALL also fetch and store a photo for each new venue where one is available (see `google-places-photo-import` capability). Queries SHALL be supplied as repeatable command arguments and SHALL NOT be derived from dish type names.

#### Scenario: Import creates venue and location per place
- **WHEN** a staff user runs the command with a query that returns places not already present
- **THEN** the system SHALL create one venue and one associated location for each such place

#### Scenario: Multiple queries in one run
- **WHEN** a staff user supplies more than one query in a single invocation
- **THEN** the system SHALL execute each query and process the combined results

#### Scenario: A place returned by two queries is imported once
- **WHEN** the same place appears in the results of two different queries in one run
- **THEN** the system SHALL create only one venue and one location for it

#### Scenario: Venue slugs stay unique
- **WHEN** an imported place's name generates a slug already taken by an existing venue
- **THEN** the system SHALL derive a distinct slug and the import SHALL succeed
