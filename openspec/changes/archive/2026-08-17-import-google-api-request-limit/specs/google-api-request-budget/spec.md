## ADDED Requirements

### Requirement: A shared request budget caps all Google API calls per import run
The system SHALL provide a `RequestBudget` class in the service layer that tracks how many HTTP requests to the Google Maps API have been made in a run. `search_text` and `fetch_photo` SHALL accept an optional `budget` argument and consult it before issuing each request. When the budget is exhausted `search_text` SHALL stop yielding further pages and `fetch_photo` SHALL raise `PlacesError`. A limit of `0` SHALL mean unlimited.

#### Scenario: Search stops paging when budget is exhausted
- **WHEN** the budget is exhausted after the first search page
- **THEN** `search_text` SHALL stop and yield no further pages

#### Scenario: Photo fetch is refused when budget is exhausted
- **WHEN** the budget has no remaining capacity before a photo fetch
- **THEN** `fetch_photo` SHALL raise `PlacesError` without making any HTTP request

#### Scenario: Zero limit means unlimited
- **WHEN** `RequestBudget` is constructed with limit `0`
- **THEN** every `consume()` call SHALL succeed regardless of how many requests have been made
