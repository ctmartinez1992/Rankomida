## MODIFIED Requirements

### Requirement: VenueLocation public facts
When a `VenueLocation` is rendered with full facts on the venue detail page (zero-or-one location flatten), the page SHALL show each of the following when the value is present and non-blank: `name` (only if it differs from the venue name), `city`, `neighbourhood`, `address`, `postal_code`, `phone` as a `tel:` link, `website_url` as an external link, Get Directions when latitude and longitude are set, Open in Google Maps when `google_maps_uri` is set, a warning for `business_status` when it is not `OPERATIONAL`, a humanized `price_level`, a humanized `primary_type`, filtered `types` chips, `opening_hours` weekday descriptions, and Google-labeled `google_rating` with optional `google_user_rating_count`. Two-or-more location cards SHALL NOT use this full fact list; they use compact teasers instead.

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

### Requirement: Two or more locations use a Locations segment
When a venue has two or more `VenueLocation` rows, the venue detail page SHALL keep the hero at venue level (photo if present, name, home city, location count) and SHALL render a Locations segment that lists each location as a compact teaser card. Each teaser SHALL show the location heading (branch name when it differs from the venue name, otherwise city), neighbourhood and city when present, address when present, a warning when `business_status` is not `OPERATIONAL`, and a link to that location's detail page. The teaser MUST NOT include weekday hours, type chips, phone, website, maps actions, or Google rating. The Dishes section SHALL follow the Locations segment.

#### Scenario: Two locations show a Locations segment
- **WHEN** a visitor opens a published venue with two `VenueLocation` rows
- **THEN** the page shows a Locations heading, one card per location with a link to that location's detail page, and the Dishes section after the Locations segment

#### Scenario: Hero does not dump all branch addresses when there are many
- **WHEN** a visitor opens a published venue with three `VenueLocation` rows
- **THEN** the hero shows the venue name, home city, and that there are 3 locations, and the per-branch addresses appear in the Locations cards rather than as a single flattened list in the hero

#### Scenario: Multi-location cards omit full facts
- **WHEN** a visitor opens a published venue with two locations that each have weekday hours, phone, and a Google rating
- **THEN** the venue detail page does not show those hours, phone numbers, or Google ratings in the location cards
