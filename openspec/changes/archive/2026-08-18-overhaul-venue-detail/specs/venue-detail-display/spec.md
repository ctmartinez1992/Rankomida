## ADDED Requirements

### Requirement: Visitor-facing venue fields on the detail page
The public venue detail page SHALL display the venue `name` and, when present, the venue `photo` with existing hover attribution. It SHALL display `venue.city` when the venue has no locations, and as the home-city subtitle when the venue has two or more locations.

#### Scenario: Venue with photo and name
- **WHEN** a visitor opens a published venue that has a name and a photo
- **THEN** the page shows the venue name as the primary heading and the photo with attribution behaviour unchanged from image-attribution

#### Scenario: Venue with no locations shows city
- **WHEN** a visitor opens a published venue that has zero `VenueLocation` rows
- **THEN** the page shows `venue.city` and does not render a Locations heading

### Requirement: Internal fields are not shown
The public venue detail page MUST NOT display `slug`, `is_published`, `source`, `google_place_id`, `last_synced_at`, `created_at`, `updated_at`, or raw latitude/longitude text.

#### Scenario: Internal identifiers omitted
- **WHEN** a visitor opens a venue whose location has a `google_place_id` and coordinates
- **THEN** the response body does not contain the place id as visible text and does not print the raw coordinate numbers as a labeled fact

### Requirement: VenueLocation public facts
When a `VenueLocation` is rendered on the venue detail page, the page SHALL show each of the following when the value is present and non-blank: `name` (only if it differs from the venue name), `city`, `neighbourhood`, `address`, `postal_code`, `phone` as a `tel:` link, `website_url` as an external link, Get Directions when latitude and longitude are set, Open in Google Maps when `google_maps_uri` is set, a warning for `business_status` when it is not `OPERATIONAL`, a humanized `price_level`, a humanized `primary_type`, filtered `types` chips, `opening_hours` weekday descriptions, and Google-labeled `google_rating` with optional `google_user_rating_count`.

#### Scenario: Fully populated location shows facts
- **WHEN** a visitor views a venue with one location that has address, phone, website, maps URI, coordinates, neighbourhood, postal code, price level, primary type, types, weekday hours, and a Google rating
- **THEN** each of those facts is visible, phone is a `tel:` link, website and Google Maps open in a new tab, and Get Directions is present

#### Scenario: Blank fields are omitted
- **WHEN** a visitor views a venue with one location that has city and address but empty phone, website, hours, price, types, and Google rating
- **THEN** the page shows city and address and does not render empty labeled rows for the missing fields

#### Scenario: Branch name hidden when it matches venue name
- **WHEN** a visitor views a venue named "Café Santiago" whose only location is also named "Café Santiago"
- **THEN** the location name is not repeated as a separate label under the venue heading

#### Scenario: Non-operational status is a warning
- **WHEN** a location has `business_status` `CLOSED_TEMPORARILY` or `CLOSED_PERMANENTLY`
- **THEN** a warning indicating the closed state is visible

#### Scenario: Operational status is not a badge
- **WHEN** a location has `business_status` `OPERATIONAL` or blank
- **THEN** the page does not show an "Operational" status badge

#### Scenario: Google rating is labeled and not Rankomida stars
- **WHEN** a location has `google_rating` 4.3 and `google_user_rating_count` 12000
- **THEN** the page shows a numeric 4.3 attributed to Google with the review count and does not render that score with Rankomida dish star glyphs

#### Scenario: Price level is humanized
- **WHEN** a location has `price_level` `PRICE_LEVEL_MODERATE`
- **THEN** the page shows €€ and does not show the raw enum string

### Requirement: Zero or one location flattens onto the detail page
When a venue has zero or one `VenueLocation`, all visitor-facing venue and location information SHALL appear on the venue detail hero. The page MUST NOT render a "Locations" segment or heading.

#### Scenario: Zero locations has no Locations segment
- **WHEN** a visitor opens a published venue with no `VenueLocation` rows
- **THEN** the page shows the venue hero (photo if present, name, city) followed by the Dishes section and contains no "Locations" heading

#### Scenario: One location is inlined in the hero
- **WHEN** a visitor opens a published venue with exactly one `VenueLocation`
- **THEN** that location's public facts are rendered in the venue hero, there is no "Locations" heading, and the Dishes section follows

### Requirement: Two or more locations use a Locations segment
When a venue has two or more `VenueLocation` rows, the venue detail page SHALL keep the hero at venue level (photo if present, name, home city, location count) and SHALL render a Locations segment that lists each location as its own card with the same public facts used in the flattened layout. The Dishes section SHALL follow the Locations segment.

#### Scenario: Two locations show a Locations segment
- **WHEN** a visitor opens a published venue with two `VenueLocation` rows
- **THEN** the page shows a Locations heading, one card per location with that location's public facts, and the Dishes section after the Locations segment

#### Scenario: Hero does not dump all branch addresses when there are many
- **WHEN** a visitor opens a published venue with three `VenueLocation` rows
- **THEN** the hero shows the venue name, home city, and that there are 3 locations, and the per-branch addresses appear in the Locations cards rather than as a single flattened list in the hero

### Requirement: Dish cards remain unchanged
The Dishes section on the venue detail page SHALL continue to list published dishes for the venue with photo, name, dish type, and Rankomida star score or "No ratings yet".

#### Scenario: Dishes still listed after the venue facts
- **WHEN** a visitor opens a published venue that has published dishes
- **THEN** those dishes appear in a card grid after the venue (and Locations, if any) content with the existing star-score display
