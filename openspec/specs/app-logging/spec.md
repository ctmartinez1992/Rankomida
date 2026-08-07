## Purpose
Define the application's logging behavior and app-level logging expectations.

## Requirements

### Requirement: Django logging configuration
The project SHALL have a `LOGGING` dict in `config/settings.py` that configures a console (stdout) handler active in all environments. The configuration SHALL set `disable_existing_loggers` to `False`. The format SHALL be `%(asctime)s %(levelname)-8s %(name)s %(message)s`.

#### Scenario: Django internals produce no noise below WARNING
- **WHEN** a Django internal event at level DEBUG or INFO is emitted
- **THEN** nothing is written to the console

#### Scenario: Unhandled request errors are logged
- **WHEN** a view raises an unhandled exception (500)
- **THEN** the `django.request` logger emits an ERROR-level message to the console

#### Scenario: App loggers emit INFO and above
- **WHEN** application code calls `logger.info(...)` on any app logger
- **THEN** the message is written to the console

### Requirement: Module-level logger per app
Every module in `catalog`, `ratings`, `leaderboard`, and `accounts` that contains view or form logic SHALL declare `logger = logging.getLogger(__name__)` at module level.

#### Scenario: Logger name reflects module path
- **WHEN** a log message is emitted from `ratings/forms.py`
- **THEN** the logger name in the output is `ratings.forms`

### Requirement: Rating submission event logging
The `ratings.forms` module SHALL log an INFO event each time a rating is saved, indicating whether it was a new submission or an update.

#### Scenario: New rating logged as create
- **WHEN** a user submits a rating for a dish they have not rated before
- **THEN** `ratings.forms` emits `INFO rating.saved user_id=<id> dish_slug=<slug> action=create`

#### Scenario: Existing rating logged as update
- **WHEN** a user submits a rating for a dish they have previously rated
- **THEN** `ratings.forms` emits `INFO rating.saved user_id=<id> dish_slug=<slug> action=update`

### Requirement: Rating form validation failure logging
The `ratings.views` module SHALL log a WARNING event when a submitted rating form fails validation.

#### Scenario: Invalid form submission logged
- **WHEN** a POST to `submit_rating` results in an invalid form
- **THEN** `ratings.views` emits `WARNING rating.form_invalid user_id=<id> dish_slug=<slug> errors=<errors>`

### Requirement: Leaderboard criterion fallback logging
The `leaderboard.views` module SHALL log a WARNING when a `?criterion=` query parameter is provided but does not match any active `CriteriaTemplate` for the dish type, causing a fallback to overall scoring.

#### Scenario: Unknown criterion key triggers warning
- **WHEN** a leaderboard request includes `?criterion=nonexistent`
- **THEN** `leaderboard.views` emits `WARNING leaderboard.criterion_not_found dish_type=<slug> key=nonexistent`

#### Scenario: Known criterion key does not trigger warning
- **WHEN** a leaderboard request includes a valid `?criterion=` key
- **THEN** no WARNING is emitted for criterion resolution

### Requirement: User registration logging
The `accounts.views` module SHALL log an INFO event when a new user successfully registers.

#### Scenario: Successful registration logged
- **WHEN** a user completes registration
- **THEN** `accounts.views` emits `INFO accounts.registered user_id=<id>`

### Requirement: Profile visibility change logging
The `accounts.views` module SHALL log an INFO event when a user changes their profile visibility setting.

#### Scenario: Visibility toggled
- **WHEN** a user saves their profile settings
- **THEN** `accounts.views` emits `INFO accounts.visibility_changed user_id=<id> is_public=<True|False>`
