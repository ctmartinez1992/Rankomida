## ADDED Requirements

### Requirement: Public location detail URL
The system SHALL serve a public detail page for a `VenueLocation` at `/venues/<venue-slug>/locations/<pk>/`. The location SHALL belong to the venue identified by the slug, and that venue SHALL be published.

#### Scenario: Published multi-location venue serves the page
- **WHEN** a visitor requests the location URL for a published venue that has two or more `VenueLocation` rows
- **THEN** the system renders that location's detail page

#### Scenario: Unpublished parent venue is not found
- **WHEN** a visitor requests the location URL of a location whose parent venue is unpublished
- **THEN** the system SHALL respond as not found

#### Scenario: Venue slug mismatch is not found
- **WHEN** a visitor requests a valid location pk under a different published venue's slug
- **THEN** the system SHALL respond as not found

#### Scenario: Missing location is not found
- **WHEN** a visitor requests a location pk that does not exist
- **THEN** the system SHALL respond as not found

### Requirement: Single-location visits redirect to the venue
When the parent venue has fewer than two `VenueLocation` rows, a request to the location URL SHALL redirect to that venue's public detail page instead of rendering location detail.

#### Scenario: One location redirects to venue detail
- **WHEN** a visitor requests the location URL of a published venue that has exactly one `VenueLocation`
- **THEN** the system redirects to the venue detail page

#### Scenario: Venue page does not link the location URL when there is one location
- **WHEN** a visitor opens a published venue with exactly one `VenueLocation`
- **THEN** the venue detail page does not contain a link to the location detail URL

### Requirement: Location detail shows public facts only
The location detail page SHALL display a heading for the location (branch `name` when it differs from the venue name, otherwise city), a link to the parent venue, and the same visitor-facing location facts used on the one-location venue hero: `city`, `neighbourhood`, `address`, `postal_code`, `phone` as a `tel:` link, `website_url` as an external link, Get Directions when latitude and longitude are set, Open in Google Maps when `google_maps_uri` is set, a warning for `business_status` when it is not `OPERATIONAL`, a humanized `price_level`, a humanized `primary_type`, filtered `types` chips, `opening_hours` weekday descriptions, and Google-labeled `google_rating` with optional `google_user_rating_count`. Blank fields SHALL be omitted. The page MUST NOT list dishes.

#### Scenario: Fully populated location shows facts
- **WHEN** a visitor opens location detail for a branch that has address, phone, website, maps URI, coordinates, neighbourhood, postal code, price level, primary type, types, weekday hours, and a Google rating
- **THEN** each of those facts is visible, phone is a `tel:` link, website and Google Maps open in a new tab, Get Directions is present, and the parent venue name links to venue detail

#### Scenario: Blank fields are omitted
- **WHEN** a visitor opens location detail for a branch that has city and address but empty phone, website, hours, price, types, and Google rating
- **THEN** the page shows city and address and does not render empty labeled rows for the missing fields

#### Scenario: Dishes are not listed
- **WHEN** a visitor opens location detail for a venue that has published dishes
- **THEN** the response does not contain a Dishes heading or those dish names as a listing on the location page

#### Scenario: Breadcrumb returns to the venue
- **WHEN** a visitor opens location detail
- **THEN** the page includes a breadcrumb link to the parent venue detail page

### Requirement: Internal fields are not shown on location detail
The public location detail page MUST NOT display `slug`, `is_published`, `source`, `google_place_id`, `last_synced_at`, `created_at`, `updated_at`, or raw latitude/longitude text.

#### Scenario: Internal identifiers omitted
- **WHEN** a visitor opens location detail for a location that has a `google_place_id` and coordinates
- **THEN** the response body does not contain the place id as visible text and does not print the raw coordinate numbers as a labeled fact
