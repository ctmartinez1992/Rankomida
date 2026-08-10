# google-places-venue-import Specification

## Purpose
TBD - created by archiving change add-google-places-venue-import. Update Purpose after archive.
## Requirements
### Requirement: Storefront records carry a Google place identifier
`VenueLocation` SHALL store an optional `google_place_id` that is unique across all locations when present. Locations created by hand SHALL be allowed to leave it empty.

#### Scenario: Imported location stores its place id
- **WHEN** the import creates a location from a Google place
- **THEN** the location SHALL persist that place's identifier in `google_place_id`

#### Scenario: Manual location has no place id
- **WHEN** a staff user creates a `VenueLocation` in admin without a place identifier
- **THEN** the save SHALL succeed with an empty `google_place_id`

#### Scenario: Two locations cannot share a place id
- **WHEN** a location is saved with a `google_place_id` already held by a different location
- **THEN** the system SHALL reject the save

### Requirement: Storefront records store Google-sourced venue detail
`VenueLocation` SHALL store the following optional fields sourced from Google Places: business status, postal code, neighbourhood, phone, website URL, Google Maps URL, price level, primary type, full type list, opening hours, Google rating, Google user rating count, and the timestamp of the last successful sync. All SHALL be optional so that manually created locations remain valid.

#### Scenario: Import populates available detail
- **WHEN** the import processes a place whose response includes address, coordinates, phone, and opening hours
- **THEN** the location SHALL persist each of those values

#### Scenario: Missing fields are tolerated
- **WHEN** the import processes a place whose response omits phone, website, and price level
- **THEN** the location SHALL be created with those fields empty and the remaining fields populated

#### Scenario: Sync timestamp is recorded
- **WHEN** the import successfully writes a location
- **THEN** the system SHALL set that location's last-synced timestamp to the time of the write

### Requirement: Venues record their origin
`Venue` SHALL record whether it originated from a manual entry or from the Google Places import.

#### Scenario: Imported venue is marked as such
- **WHEN** the import creates a venue
- **THEN** that venue's source SHALL indicate Google Places

#### Scenario: Admin-created venue defaults to manual
- **WHEN** a staff user creates a venue in admin without specifying a source
- **THEN** that venue's source SHALL indicate manual entry

### Requirement: Staff can import venues from Google Places by search query
The system SHALL provide a management command that queries Google Places Text Search for one or more caller-supplied queries and creates a `Venue` and a `VenueLocation` for each distinct place returned. Queries SHALL be supplied as repeatable command arguments and SHALL NOT be derived from dish type names.

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

### Requirement: Import paginates within the API result ceiling
The command SHALL follow Google's page tokens to retrieve additional pages, SHALL wait before using a freshly issued page token, and SHALL stop at a configurable maximum page count not exceeding the API's three-page limit.

#### Scenario: Additional pages are retrieved
- **WHEN** a query's response includes a token indicating further results
- **THEN** the system SHALL request the next page using that token

#### Scenario: Page token is not used immediately
- **WHEN** the system receives a page token
- **THEN** it SHALL delay before issuing the paged request, and SHALL retry with backoff if the token is rejected as not yet valid

#### Scenario: Page limit is respected
- **WHEN** a staff user caps the run at one page
- **THEN** the system SHALL issue no paged follow-up requests for that query

### Requirement: Re-running the import updates rather than duplicates
The command SHALL be idempotent with respect to `google_place_id`. When a returned place matches an existing location, the system SHALL update that location's Google-sourced fields and sync timestamp instead of creating a new record.

#### Scenario: Second run creates nothing new
- **WHEN** the command runs twice with the same query and unchanged API results
- **THEN** the second run SHALL create no additional venues or locations

#### Scenario: Changed detail is refreshed
- **WHEN** a re-run returns a place whose address or business status differs from the stored values
- **THEN** the system SHALL update the stored values for that location

### Requirement: Re-syncs preserve staff curation
On updating an existing record, the command SHALL NOT modify the venue's name, slug, photo, photo attribution, or published state.

#### Scenario: Curated name survives a re-sync
- **WHEN** a staff user has renamed an imported venue and the import runs again
- **THEN** the venue SHALL retain the staff-supplied name

#### Scenario: Published venue stays published
- **WHEN** a staff user has published an imported venue and the import runs again
- **THEN** that venue SHALL remain published

### Requirement: Imported venues are created unpublished
Venues created by the import SHALL be unpublished so that no imported venue reaches the public site without staff review.

#### Scenario: New import is not publicly visible
- **WHEN** the import creates a venue
- **THEN** that venue SHALL be unpublished

### Requirement: Dry run reports planned writes without persisting them
The command SHALL support a dry-run mode that reports the venues and locations it would create and update, and SHALL make no database writes in that mode.

#### Scenario: Dry run leaves the database unchanged
- **WHEN** a staff user runs the command in dry-run mode against results containing new places
- **THEN** the venue and location counts SHALL be unchanged after the run

#### Scenario: Dry run describes intended writes
- **WHEN** a staff user runs the command in dry-run mode
- **THEN** the output SHALL identify which places would be created and which would be updated

### Requirement: Import requires configured API credentials
The system SHALL read the Google Maps API key from the environment. The command SHALL fail with a clear error and make no requests when the key is absent.

#### Scenario: Missing key aborts the run
- **WHEN** a staff user runs the command with no API key configured
- **THEN** the command SHALL exit with an error explaining that the key is required
- **AND** SHALL issue no API requests

#### Scenario: Key is never written to the repository
- **WHEN** the project ships its example environment file
- **THEN** that file SHALL document the key as a commented placeholder with no real value

### Requirement: Import failures are logged and do not abort the run
API and parsing failures for an individual place SHALL be logged and skipped so that one bad record does not discard the rest of the run. A failure of an entire query SHALL be logged and the command SHALL continue to the next query.

#### Scenario: One malformed place is skipped
- **WHEN** a single place in a response cannot be parsed
- **THEN** the system SHALL log the failure and continue processing the remaining places

#### Scenario: A failed query does not stop other queries
- **WHEN** one query's request fails and another query remains
- **THEN** the system SHALL log the failure and execute the remaining query

### Requirement: Admin exposes imported venue data
Django admin SHALL display the Google-sourced fields on the venue location inline, and SHALL allow staff to filter and search venues by published state.

#### Scenario: Location inline shows Google fields
- **WHEN** a staff user opens a venue change form
- **THEN** the location inline SHALL include the place id, business status, and the other Google-sourced fields

#### Scenario: Staff can filter unpublished venues
- **WHEN** a staff user opens the venue list in admin
- **THEN** they SHALL be able to filter that list by published state

