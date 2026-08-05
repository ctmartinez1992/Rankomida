## ADDED Requirements

### Requirement: Settings are driven by environment variables
The application SHALL read all environment-sensitive configuration from environment variables so that the same codebase runs in development and production without code changes.

- `SECRET_KEY` SHALL be read from the `SECRET_KEY` environment variable. The application SHALL refuse to start if this variable is absent in production.
- `DEBUG` SHALL default to `False`. It SHALL be set to `True` only when the `DEBUG` environment variable is explicitly set to `"true"`.
- `ALLOWED_HOSTS` SHALL be populated from the `ALLOWED_HOSTS` environment variable (comma-separated list). In development (DEBUG=True) it SHALL fall back to `["localhost", "127.0.0.1"]`.

#### Scenario: Production startup with required vars set
- **WHEN** the application starts with `SECRET_KEY`, `DATABASE_URL`, and `ALLOWED_HOSTS` set
- **THEN** the application starts successfully

#### Scenario: Production startup missing SECRET_KEY
- **WHEN** the application starts without `SECRET_KEY` set and `DEBUG=False`
- **THEN** the application raises an `ImproperlyConfigured` error and does not start

### Requirement: Database is configured via DATABASE_URL
The application SHALL use `dj-database-url` to parse the `DATABASE_URL` environment variable into Django's `DATABASES` setting.

- In development, the `DATABASE_URL` SHALL fall back to a local SQLite file (`db.sqlite3`) so no env var is required locally.
- In production, `DATABASE_URL` SHALL point to a PostgreSQL connection string.

#### Scenario: DATABASE_URL set to Postgres connection string
- **WHEN** `DATABASE_URL=postgres://...` is set
- **THEN** Django connects to PostgreSQL

#### Scenario: DATABASE_URL absent (development)
- **WHEN** `DATABASE_URL` is not set
- **THEN** Django falls back to `db.sqlite3`

### Requirement: Static files are served by whitenoise
The application SHALL use `whitenoise` middleware to serve static files directly from the WSGI process without requiring a separate static file server.

- `STATIC_ROOT` SHALL be set to `BASE_DIR / "staticfiles"`.
- `WhiteNoiseMiddleware` SHALL be inserted immediately after `SecurityMiddleware` in `MIDDLEWARE`.
- `STATICFILES_STORAGE` SHALL use whitenoise's compressed manifest storage in production.

#### Scenario: Static file request in production
- **WHEN** a browser requests a static asset (CSS, JS, image)
- **THEN** whitenoise serves the file with appropriate cache headers

### Requirement: Media URL uses an absolute path
The application SHALL set `MEDIA_URL = "/media/"` (with leading slash) so that media URLs resolve correctly in production.

#### Scenario: Dish photo URL rendered in template
- **WHEN** a dish with a photo is displayed
- **THEN** the photo URL begins with `/media/` and resolves to a valid path
