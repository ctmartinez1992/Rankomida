## Why

The project has zero logging infrastructure. There is no visibility into business events (rating submissions, user registrations, leaderboard criterion fallbacks) or application errors. When something goes wrong in any environment, there is nothing to inspect.

## What Changes

- Add a `LOGGING` configuration to `config/settings.py` with a console handler active in all environments
- Add a module-level `logger = logging.getLogger(__name__)` to each app's views and forms
- Instrument key business events: rating create vs. update, form validation failures, leaderboard criterion fallback, user registration, profile visibility changes

## Capabilities

### New Capabilities
- `app-logging`: Structured console logging for all Django apps — covers settings-level config and per-module logger instrumentation with defined log events per app

### Modified Capabilities
<!-- No existing specs are changing at the requirements level -->

## Impact

- `config/settings.py`: new `LOGGING` dict (no existing config to break)
- `ratings/forms.py`, `ratings/views.py`: new logger + event calls
- `leaderboard/views.py`: new logger + criterion fallback warning
- `accounts/views.py`: new logger + registration, visibility events
- `catalog/views.py`: new logger (no event calls needed yet)
- No new dependencies — Python stdlib `logging` only
- No database changes, no migrations, no API changes
