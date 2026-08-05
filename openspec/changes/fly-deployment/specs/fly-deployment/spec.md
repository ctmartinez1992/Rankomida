## ADDED Requirements

### Requirement: Application is containerised with Docker
The project SHALL include a `Dockerfile` that builds a production-ready image.

- The image SHALL use a slim Python base image matching the project's Python version (3.14).
- The image SHALL install all dependencies from `requirements.txt`.
- The image SHALL run `collectstatic` at build time.
- The image SHALL use `gunicorn` as the entrypoint WSGI server, binding to `0.0.0.0:8000`.
- A `.dockerignore` file SHALL exclude `media/`, `db.sqlite3`, `__pycache__`, `.venv`, and other dev artefacts.

#### Scenario: Docker image builds successfully
- **WHEN** `docker build` is run in the project root
- **THEN** the image builds without errors and `staticfiles/` is populated

#### Scenario: Container starts and serves requests
- **WHEN** the container is run with required environment variables set
- **THEN** the application responds to HTTP requests on port 8000

### Requirement: Fly.io application is configured via fly.toml
The project SHALL include a `fly.toml` file that configures the Fly.io application.

- The config SHALL specify the app name, primary region, and build source (Dockerfile).
- The config SHALL expose port 8000 internally and map it to HTTP/HTTPS via Fly's proxy.
- The config SHALL define a health check on `/` (or a dedicated `/health/` path if available).
- The config SHALL mount a persistent Fly volume at `/app/media` for user-uploaded media files.
- The config SHALL define a `[deploy]` release command to run `python manage.py migrate` automatically on each deploy.

#### Scenario: Fly deploy runs migrations
- **WHEN** `fly deploy` is executed
- **THEN** the release command runs `python manage.py migrate` before traffic is cut over

#### Scenario: Uploaded media persists across deploys
- **WHEN** a user uploads a dish photo and a new deploy is performed
- **THEN** the photo is still accessible after the deploy

### Requirement: Fly Postgres is provisioned and linked
The application SHALL use a Fly-managed PostgreSQL cluster as its production database.

- `DATABASE_URL` SHALL be set as a Fly secret referencing the Fly Postgres connection string.
- The application SHALL be able to connect to Postgres using the `psycopg` adapter.

#### Scenario: Application connects to Fly Postgres on startup
- **WHEN** the deployed app starts with `DATABASE_URL` pointing to Fly Postgres
- **THEN** Django connects successfully and migrations can run

### Requirement: Secrets are managed via Fly secrets
All sensitive configuration SHALL be stored as Fly secrets, not in `fly.toml` or the Docker image.

- `SECRET_KEY` SHALL be set via `fly secrets set SECRET_KEY=...`
- `DATABASE_URL` SHALL be set via `fly secrets set` (typically auto-set by `fly postgres attach`)
- `ALLOWED_HOSTS` SHALL be set via `fly secrets set ALLOWED_HOSTS=<app-domain>`

#### Scenario: Secrets not present in source control
- **WHEN** the repository is inspected
- **THEN** no secret values (SECRET_KEY, DATABASE_URL) appear in any committed file
