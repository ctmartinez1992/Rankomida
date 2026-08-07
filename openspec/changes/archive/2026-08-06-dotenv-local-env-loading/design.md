## Context

Django settings already read `DEBUG`, `SECRET_KEY`, `ALLOWED_HOSTS`, and `DATABASE_URL` from `os.environ` (env-driven production config). Locally, developers keep those values in a gitignored `.env` at the project root, but nothing loads that file into the process environment. Dokku injects the same variable names via `dokku config:set`; `.env` is gitignored and listed in `.dockerignore`, so it is not present in deployed containers.

## Goals / Non-Goals

**Goals:**
- Load project-root `.env` into `os.environ` before settings read configuration
- Preserve Dokku / platform env vars as the source of truth when both exist
- Keep startup safe when `.env` is absent (production, CI)

**Non-Goals:**
- Split settings into `settings/dev.py` / `settings/prod.py`
- Commit secrets or ship `.env` to Dokku
- Change which env var names settings consume
- Add django-environ or other settings wrappers

## Decisions

### D1: Use `python-dotenv` with `load_dotenv(BASE_DIR / '.env')`
Call `load_dotenv` once in `config/settings.py` immediately after `BASE_DIR` is defined and before any `os.environ.get` for app config.

**Rationale:** Minimal change; matches existing single-file settings. Path is absolute via `BASE_DIR`, so it works regardless of cwd (gunicorn, `manage.py`, tests).

**Alternatives considered:**
- django-environ — heavier; not needed for four string vars
- Shell/`direnv` only — works for some developers, not for IDE runners or teammates who expect `.env`
- Split settings modules — out of scope

### D2: Never override existing process env (`override=False`)
`python-dotenv`'s default is `override=False`. Dokku-injected vars always win if somehow a `.env` were present.

**Rationale:** Production safety. Dokku config and Docker `-e` remain authoritative.

### D3: Missing `.env` is a no-op
Do not raise if the file is absent. Production and CI continue to rely solely on process env.

**Rationale:** `.env` is local convenience only; deploy path must not depend on it.

### D4: Keep `.env` out of git and images
Rely on existing `.gitignore` and `.dockerignore` entries for `.env`. No Dokku config changes.

## Risks / Trade-offs

- [Risk] Developer sets wrong `DATABASE_URL` in `.env` (e.g. relative SQLite path) → Mitigation: document absolute/sqlite URL patterns; default fallback in settings remains when var unset
- [Risk] Someone enables `override=True` later and shadows Dokku secrets → Mitigation: document D2; leave default `False`
- [Trade-off] Adds a small dependency for a thin load step → Acceptable vs custom file parsing

## Migration Plan

1. Add `python-dotenv` to `requirements.txt` and install locally
2. Wire `load_dotenv` in settings; remove debug print
3. Deploy as usual to Dokku — no config changes; behavior unchanged without `.env`
4. Rollback: remove the `load_dotenv` call / dependency; settings revert to process-env-only

## Open Questions

None — Dokku compatibility is covered by D2–D4 and existing ignore rules.
