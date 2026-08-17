## ADDED Requirements

### Requirement: Import photo fetching is capped per run
The import command SHALL accept a `--max-photos` argument (default `20`) that limits the total number of Places Photo API requests issued in a single run. When the limit is reached the command SHALL log a warning, skip photo fetching for remaining venues, and continue processing other fields normally. `--max-photos 0` SHALL disable photo fetching entirely for that run.

#### Scenario: Photos stop being fetched once limit is reached
- **WHEN** the import creates more new venues than the `--max-photos` value
- **THEN** only the first `--max-photos` venues SHALL have a photo saved
- **AND** the command SHALL log a warning that the photo limit was reached

#### Scenario: Zero disables all photo fetching
- **WHEN** the import is run with `--max-photos 0`
- **THEN** no photo API requests SHALL be made and no venues SHALL have photos saved

#### Scenario: Limit does not affect venue or location creation
- **WHEN** the photo limit is reached mid-run
- **THEN** remaining places SHALL still be imported as venues and locations without photos
