## 1. Dependencies

- [x] 1.1 Add `gunicorn`, `psycopg[binary]`, `whitenoise`, and `dj-database-url` to `requirements.txt`

## 2. Production Settings

- [x] 2.1 Read `SECRET_KEY` from environment variable; raise `ImproperlyConfigured` if absent when `DEBUG=False`
- [x] 2.2 Read `DEBUG` from environment variable, defaulting to `False`
- [x] 2.3 Read `ALLOWED_HOSTS` from environment variable (comma-separated), falling back to `["localhost", "127.0.0.1"]` when `DEBUG=True`
- [x] 2.4 Configure `DATABASES` using `dj-database-url.parse(DATABASE_URL)`, falling back to SQLite when `DATABASE_URL` is unset
- [x] 2.5 Add `WhiteNoiseMiddleware` immediately after `SecurityMiddleware` in `MIDDLEWARE`
- [x] 2.6 Set `STATIC_ROOT = BASE_DIR / "staticfiles"` and configure whitenoise compressed manifest storage
- [x] 2.7 Fix `MEDIA_URL` to `"/media/"` (absolute path with leading slash)

## 3. Docker

- [x] 3.1 Create `Dockerfile` using a slim Python 3.14 base image; install deps, run `collectstatic`, set gunicorn as entrypoint (2 workers, port 8000)
- [x] 3.2 Create `.dockerignore` excluding `media/`, `db.sqlite3`, `__pycache__`, `.venv`, `openspec/`, `.git`

## 4. Fly.io Configuration

- [x] 4.1 Create `fly.toml` with app config: Dockerfile build, port 8000, HTTP service, health check on `/`
- [x] 4.2 Add `[deploy]` release command in `fly.toml`: `python manage.py migrate --noinput`
- [x] 4.3 Add `[mounts]` section in `fly.toml` mounting volume `media_data` at `/app/media`

## 5. Verification

- [x] 5.1 Build the Docker image locally and confirm it starts with `DATABASE_URL` and `SECRET_KEY` set
- [x] 5.2 Run `python manage.py check --deploy` and resolve any warnings
