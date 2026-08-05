## Why

rankomida runs locally in development but has no production deployment. To make it available to a small community of users, it needs to be deployed to a cloud platform with proper production configuration, a persistent database, and media file storage.

## What Changes

- Add production Django settings (environment-variable-driven `SECRET_KEY`, `DEBUG`, `ALLOWED_HOSTS`, `DATABASE_URL`)
- Swap SQLite for PostgreSQL as the production database
- Add `gunicorn` as the production WSGI server
- Add `whitenoise` for serving static files
- Add `psycopg` (PostgreSQL adapter) to dependencies
- Add a `Dockerfile` for containerised deployment on Fly.io
- Add `fly.toml` to configure the Fly.io application, volume mount for media files
- Fix `MEDIA_URL` to use an absolute path (`/media/`)

## Capabilities

### New Capabilities

- `production-config`: Environment-variable-driven Django settings suitable for production (secrets, debug flag, allowed hosts, database URL, static/media configuration)
- `fly-deployment`: Fly.io application configuration — Dockerfile, fly.toml, Fly Postgres, persistent volume for media uploads

### Modified Capabilities

<!-- None — no existing spec-level behaviour changes -->

## Impact

- `requirements.txt`: add `gunicorn`, `psycopg[binary]`, `whitenoise`, `dj-database-url`
- `config/settings.py`: production settings via environment variables
- New files: `Dockerfile`, `fly.toml`, `.dockerignore`
- Media files require a persistent Fly volume mounted at `/app/media`
- Database migrations must be run on first deploy and on subsequent schema changes
