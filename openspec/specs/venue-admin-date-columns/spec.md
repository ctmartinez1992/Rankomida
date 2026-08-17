## ADDED Requirements

### Requirement: Venue model timestamps
The `Venue` model MUST have a `created_at` field (auto-set on insert) and an `updated_at` field (auto-set on every save).

#### Scenario: New venue created
- **WHEN** a `Venue` instance is saved for the first time
- **THEN** `created_at` is set to the current datetime and is never changed again

#### Scenario: Existing venue saved
- **WHEN** a `Venue` instance is saved after creation
- **THEN** `updated_at` is set to the current datetime

---

### Requirement: Admin list date columns
The `VenueAdmin` list view MUST display `created_at` and `updated_at` columns and MUST NOT display `source` as a list column.

#### Scenario: Admin venue list
- **WHEN** a staff user views the venue list in Django admin
- **THEN** the columns shown are `name`, `city`, `slug`, `is_published`, `created_at`, `updated_at`
- **THEN** `source` is NOT shown as a list column

---

### Requirement: Admin date column sorting
The `created_at` and `updated_at` columns in the venue admin list MUST be sortable by clicking the column header.

#### Scenario: Sorting by date
- **WHEN** a staff user clicks the `created_at` or `updated_at` column header
- **THEN** the list re-orders by that date field
