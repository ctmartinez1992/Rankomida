## ADDED Requirements

### Requirement: User can save a dish to their list
The system SHALL allow an authenticated user to save a published dish to a single personal saved list. Saving the same dish again SHALL be a no-op (at most one save per user and dish).

#### Scenario: Authenticated user saves a dish
- **WHEN** a logged-in user submits a save action for a published dish they have not already saved and have not rated
- **THEN** the system SHALL create a saved entry for that user and dish

#### Scenario: Saving an already-saved dish is idempotent
- **WHEN** a logged-in user submits a save action for a dish already on their saved list
- **THEN** the system SHALL keep a single saved entry and SHALL NOT create a duplicate

#### Scenario: Anonymous user cannot save
- **WHEN** an anonymous user attempts to save a dish
- **THEN** the system SHALL require login before completing the save

### Requirement: User can unsave a dish
The system SHALL allow an authenticated user to remove a dish from their saved list.

#### Scenario: Unsave from dish detail
- **WHEN** a logged-in user submits an unsave action for a dish on their saved list
- **THEN** the system SHALL remove that saved entry

#### Scenario: Unsave from the saved list page
- **WHEN** a logged-in user unsaves a dish from `/saved/`
- **THEN** the system SHALL remove that saved entry and return the user to the saved list (or equivalent `next` destination)

### Requirement: Dedicated private saved list page
The system SHALL provide a login-required page at `/saved/` that lists only the current user’s saved published dishes, ordered by most recently saved first. The saved list SHALL NOT appear on public profiles.

#### Scenario: Owner views saved list
- **WHEN** a logged-in user opens `/saved/`
- **THEN** the system SHALL show that user’s saved published dishes and SHALL NOT show other users’ saves

#### Scenario: Anonymous user opens saved list
- **WHEN** an anonymous user requests `/saved/`
- **THEN** the system SHALL require login

#### Scenario: Empty saved list
- **WHEN** a logged-in user with no saved dishes opens `/saved/`
- **THEN** the system SHALL show an empty state

### Requirement: Dish detail exposes save controls
The dish detail page SHALL let an authenticated user save or unsave the dish. If the user already has a rating submission for that dish, the page SHALL NOT offer Save. Anonymous users SHALL be directed to log in to save (or otherwise cannot complete a save without authentication).

#### Scenario: Unsaved dish shows Save
- **WHEN** a logged-in user who has neither saved nor rated the dish views dish detail
- **THEN** the page SHALL offer a Save action

#### Scenario: Saved dish shows Unsave
- **WHEN** a logged-in user who has saved but not rated the dish views dish detail
- **THEN** the page SHALL offer an Unsave action

#### Scenario: Already-rated dish hides Save
- **WHEN** a logged-in user who already rated the dish views dish detail
- **THEN** the page SHALL NOT offer a Save action

### Requirement: Rating a dish removes it from the saved list
When a user successfully creates or updates a rating submission for a dish, the system SHALL remove that dish from the user’s saved list if present.

#### Scenario: First rating auto-removes saved dish
- **WHEN** a logged-in user successfully submits a rating for a dish that is on their saved list
- **THEN** the system SHALL delete the saved entry for that user and dish

#### Scenario: Rating when not saved is unaffected
- **WHEN** a logged-in user successfully submits a rating for a dish that is not on their saved list
- **THEN** the rating SHALL succeed and the saved list SHALL remain unchanged

### Requirement: Navigation links to the saved list
Authenticated users SHALL see a navigation link to `/saved/`.

#### Scenario: Logged-in nav includes Saved
- **WHEN** an authenticated user views any page using the site chrome
- **THEN** the navigation SHALL include a link to the saved list page
