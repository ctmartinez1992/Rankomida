## Purpose

Define optional source attribution for catalog images.

## Requirements

### Requirement: Optional photo attribution fields

DishType, Venue, and Dish SHALL each store an optional human-readable `photo_credit` and an optional `photo_source_url` alongside their existing `photo` field. Attribution MUST NOT be required when a photo is present.

#### Scenario: Save photo without attribution
- **WHEN** a staff user saves a Dish (or Venue or DishType) with a photo and empty credit and source URL
- **THEN** the save succeeds

#### Scenario: Save credit and source URL
- **WHEN** a staff user sets `photo_credit` to a non-empty string and `photo_source_url` to a valid URL on a catalog entity
- **THEN** both values are persisted and available when rendering that entity's photo

### Requirement: Admin editing of photo attribution

Django admin for DishType, Venue, and Dish SHALL expose `photo_credit` and `photo_source_url` next to the `photo` field.

#### Scenario: Admin shows attribution fields
- **WHEN** a staff user opens the change form for a Dish, Venue, or DishType
- **THEN** the form includes fields for photo, photo credit, and photo source URL

### Requirement: Hover attribution on public images

Every catalog page that displays an entity photo SHALL show attribution on hover when that entity has a credit and/or source URL. If a source URL is present, the overlay MUST include a link to that URL (link text is the credit when present, otherwise "Source"). If neither credit nor URL is set, the image SHALL render without attribution overlay chrome.

#### Scenario: Hover shows credit and link
- **WHEN** a visitor views a page with a photo that has both credit and source URL
- **THEN** hovering the image reveals the credit as a link to the source URL opening in a new tab

#### Scenario: Photo without attribution
- **WHEN** a visitor views a page with a photo that has empty credit and empty source URL
- **THEN** the image renders without an attribution overlay

#### Scenario: Venue photo on dish-by-type list
- **WHEN** a visitor views the dish-by-type list and a card shows the venue photo
- **THEN** hover attribution uses that venue's credit and source URL
