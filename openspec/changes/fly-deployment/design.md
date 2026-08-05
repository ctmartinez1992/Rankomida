## Context

rankomida is a Django 6 / SQLite application running locally in development. It has no production configuration — `DEBUG=True` is hardcoded, `SECRET_KEY` is committed, and `ALLOWED_HOSTS` is empty. Media files (dish/venue photos) are stored on local disk in `media/`. The goal is to deploy to Fly.io for a small community, swapping SQLite for Fly-managed PostgreSQL and retaining disk-based media storage via a Fly persistent volume.

## Goals / Non-Goals

**Goals:**
- Make the app deployable to Fly.io with a single `fly deploy`
- Use Fly Postgres as the production database
- Persist media uploads across deploys using a Fly volume
- Serve static files without a separate CDN or web server
- Keep development experience unchanged (SQLite fallback, no env vars required locally)

**Non-Goals:**
- Object storage (S3/R2) for media — disk is sufficient at this scale
- CI/CD pipeline — manual `fly deploy` is acceptable for now
- Multiple Fly machines / horizontal scaling
- Redis, Celery, or any background worker

## Decisions

### D1: gunicorn over uvicorn
rankomida uses `WSGI_APPLICATION`, not ASGI. gunicorn is the natural fit — no need to introduce async complexity. 1–2 workers is sufficient for a small community.

**Alternatives considered:** `uvicorn` — would require switching to ASGI entrypoint for no benefit at this scale.

### D2: whitenoise for static files
whitenoise serves compressed, cache-busted static files directly from the Python process. No nginx sidecar needed on Fly. For a small community the performance is acceptable, and it eliminates operational complexity.

**Alternatives considered:** Separate nginx container — more control, significantly more complexity.

### D3: dj-database-url for DB config
`dj-database-url` parses a `DATABASE_URL` connection string into Django's `DATABASES` dict. It's the de facto standard for 12-factor Django apps and works seamlessly with Fly's `fly postgres attach` which sets `DATABASE_URL` automatically.

**Alternatives considered:** Manual `DATABASES` config in settings — more verbose, harder to rotate credentials.

### D4: Fly volume for media (not object storage)
A Fly persistent volume mounted at `/app/media` is the simplest path. Media is user-uploaded content (dish/venue photos) — volumes are sufficient for a small community and avoid introducing S3/R2 dependency.

**Alternatives considered:** Cloudflare R2 — right choice at larger scale; overkill here.

### D5: Single-file settings (not split dev/prod)
Rather than a `settings/` package, production config is achieved by reading environment variables with sensible local defaults. This keeps the settings surface minimal and easy to audit.

## Risks / Trade-offs

- **Fly volume is tied to a single machine** → single point of failure for media. Acceptable for a small community; if scale grows, migrate to object storage.
- **SQLite fallback in dev, Postgres in prod** → possible subtle behaviour differences (e.g., case sensitivity, JSON operators). Mitigated by running `python manage.py test` against Postgres in CI if added later.
- **gunicorn with 2 workers, SQLite dev** → no risk; SQLite is only used locally.
- **migrate on every deploy** → safe for Django's incremental migrations; no risk of data loss on no-op deploys.

## Migration Plan

1. Update `requirements.txt` and `config/settings.py`
2. Add `Dockerfile` and `.dockerignore`
3. Run `fly launch` to create the app (or `fly apps create` if app already named)
4. Run `fly postgres create` and `fly postgres attach`
5. Set remaining secrets: `fly secrets set SECRET_KEY=... ALLOWED_HOSTS=...`
6. Create media volume: `fly volumes create media_data --size 1`
7. Add volume mount to `fly.toml`
8. Run `fly deploy` — release command runs migrations automatically

**Rollback:** `fly deploy --image <previous-image>` restores the previous version. DB migrations are additive; no rollback migration needed for this change.

## Open Questions

- App name on Fly.io — to be chosen at deploy time, not encoded in artifacts.
- Primary region — default to `lhr` (London) or `iad` (Virginia) based on expected user geography.
