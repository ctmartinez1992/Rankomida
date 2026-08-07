## Why

Local development needs a convenient way to set `DEBUG`, `SECRET_KEY`, `DATABASE_URL`, and related settings via a project-root `.env` file. Django does not load `.env` automatically, so those values never reach `os.environ` and settings fall back to production-safe defaults. Dokku (and similar platforms) already inject real process environment variables; any local-loading solution must leave that path untouched.

## What Changes

- Load a project-root `.env` file into the process environment when Django settings are imported
- Add `python-dotenv` as a dependency
- Keep platform-injected env vars (Dokku `config:set`, Docker `-e`, CI) authoritative — never override them from `.env`
- Treat a missing `.env` as normal (no-op), so production deploys without the file continue to work
- Remove the temporary debug print of `DEBUG` from settings

## Capabilities

### New Capabilities
- `local-env-loading`: Load optional project-root `.env` into process env for local development without overriding platform-provided environment variables

### Modified Capabilities
- (none — `openspec/specs/` has no archived capabilities yet; this complements the existing env-driven settings pattern from `fly-deployment`)

## Impact

- `requirements.txt`: add `python-dotenv`
- `config/settings.py`: call `load_dotenv` after `BASE_DIR`, before reading env vars; remove debug print
- Dokku / Docker / CI: no config changes required; `.env` remains gitignored and should not be present in deployed images
- Local developers: can rely on `.env` for the same variable names already used in production (`DEBUG`, `SECRET_KEY`, `ALLOWED_HOSTS`, `DATABASE_URL`)
