## ADDED Requirements

### Requirement: Venues have a published state
`Venue` SHALL carry a published flag that defaults to published, so that venues created before this capability and venues created by hand in admin remain visible without further action.

#### Scenario: Existing venues stay visible
- **WHEN** the published flag is introduced to a database of existing venues
- **THEN** every existing venue SHALL be published

#### Scenario: Admin-created venue defaults to published
- **WHEN** a staff user creates a venue in admin without changing the published flag
- **THEN** that venue SHALL be published

### Requirement: Public venue list shows published venues only
The public venue list SHALL exclude unpublished venues, and its city filter options SHALL be derived only from published venues.

#### Scenario: Unpublished venue is absent from the list
- **WHEN** a visitor opens the venue list and an unpublished venue exists
- **THEN** that venue SHALL NOT appear in the list

#### Scenario: City options ignore unpublished venues
- **WHEN** the only venue in a given city is unpublished
- **THEN** that city SHALL NOT be offered as a filter option

#### Scenario: Search and sort respect publication
- **WHEN** a visitor searches or sorts the venue list
- **THEN** the results SHALL contain only published venues

### Requirement: Public venue detail is unavailable for unpublished venues
The public venue detail page SHALL NOT serve unpublished venues.

#### Scenario: Unpublished venue detail is not found
- **WHEN** a visitor requests the detail page of an unpublished venue
- **THEN** the system SHALL respond as not found

#### Scenario: Published venue detail is served
- **WHEN** a visitor requests the detail page of a published venue
- **THEN** the system SHALL render that venue

### Requirement: Staff can publish a venue
Staff SHALL be able to change a venue's published state from Django admin, and publishing SHALL make the venue immediately available on the public pages.

#### Scenario: Publishing reveals the venue
- **WHEN** a staff user publishes a previously unpublished venue
- **THEN** that venue SHALL appear on the public venue list and its detail page SHALL be served

#### Scenario: Unpublishing hides the venue
- **WHEN** a staff user unpublishes a venue
- **THEN** that venue SHALL no longer appear on the public venue list
