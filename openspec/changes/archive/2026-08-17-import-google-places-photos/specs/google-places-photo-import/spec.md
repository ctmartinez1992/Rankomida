## ADDED Requirements

### Requirement: Import fetches and stores a venue photo from Google Places
When creating a new venue the import SHALL request photo metadata from Google Places, download the first available photo, and persist it to `Venue.photo`, `Venue.photo_credit`, and `Venue.photo_source_url`. If the venue already has a photo, the import SHALL skip the fetch entirely.

#### Scenario: New venue receives a Google photo
- **WHEN** the import creates a new venue from a Google place that includes photo metadata
- **THEN** the venue SHALL have a non-empty `photo` file, `photo_credit` equal to "Google Maps", and `photo_source_url` equal to the place's `googleMapsUri`

#### Scenario: Venue without photo metadata is created without photo
- **WHEN** the import creates a new venue from a Google place that returns no photo metadata
- **THEN** the venue SHALL be created with an empty `photo`, `photo_credit`, and `photo_source_url`

#### Scenario: Existing venue with a photo is not overwritten
- **WHEN** the import updates an existing venue that already has a non-empty `photo`
- **THEN** the import SHALL leave `photo`, `photo_credit`, and `photo_source_url` unchanged

#### Scenario: Photo fetch failure does not abort the import
- **WHEN** the photo download request fails (network error, non-200 response)
- **THEN** the import SHALL log a warning, skip saving the photo, and continue processing remaining places
