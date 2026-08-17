## ADDED Requirements

### Requirement: VenueLocation model timestamps
The `VenueLocation` model MUST have a `created_at` field (auto-set on insert) and an `updated_at` field (auto-set on every save).

#### Scenario: New location created
- **WHEN** a `VenueLocation` instance is saved for the first time
- **THEN** `created_at` is set to the current datetime and is never changed again

#### Scenario: Existing location saved
- **WHEN** a `VenueLocation` instance is saved after creation
- **THEN** `updated_at` is set to the current datetime

---

### Requirement: Admin inline readonly display
The `VenueLocationInline` in Django admin MUST expose `created_at` and `updated_at` as read-only fields.

#### Scenario: Venue detail page in admin
- **WHEN** a staff user views a venue detail page
- **THEN** each location inline shows `created_at` and `updated_at` as non-editable fields
