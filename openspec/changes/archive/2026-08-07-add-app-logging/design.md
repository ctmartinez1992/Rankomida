## Context

Rankomida is a Django 6 monolith with four apps (catalog, ratings, leaderboard, accounts) and a SQLite database. Currently there is no `LOGGING` configuration in `settings.py` and no `getLogger` calls anywhere in application code. When errors occur or business events happen (e.g. a user submits or updates a rating), there is no record.

The project uses `DEBUG` env var to differentiate development from production. It runs behind a standard WSGI server with stdout available in all environments.

## Goals / Non-Goals

**Goals:**
- Add a `LOGGING` dict to `settings.py` that works in all environments (dev and prod)
- Give each app module its own named logger so log output identifies the source
- Instrument the most important business events with INFO/WARNING/DEBUG calls
- Use only Python stdlib — no new dependencies

**Non-Goals:**
- Structured JSON logging (e.g. `structlog`) — out of scope for now
- Log file rotation or file-based handlers
- External log aggregation (Sentry, Datadog, etc.)
- Per-request middleware logging
- Database query logging (`django.db.backends`)

## Decisions

### 1. Console-only handler in all environments
**Decision:** Single `StreamHandler` (stdout) in all environments, no `DEBUG`-conditional branching.

**Rationale:** Deployment environments can redirect stdout to their log aggregator of choice. Keeping settings simple avoids the risk of silent logging in one environment.

**Alternatives considered:**
- File handler: adds rotation complexity, not needed when stdout is available
- `DEBUG`-conditional config: creates blind spots in production if `DEBUG=False` changes log behaviour

### 2. `logging.getLogger(__name__)` per module
**Decision:** Each module declares `logger = logging.getLogger(__name__)` at the top of the file.

**Rationale:** Module-level loggers (e.g. `ratings.forms`, `leaderboard.views`) are standard Django practice. They integrate naturally with the `LOGGING` dict's logger names and are zero-cost when no messages are emitted.

### 3. Log levels per layer
| Logger | Level | Rationale |
|---|---|---|
| `django` | `WARNING` | Suppress routine Django internals |
| `django.request` | `ERROR` | Only unhandled 500s |
| `django.security` | `WARNING` | Security events always visible |
| App loggers (`catalog`, `ratings`, `leaderboard`, `accounts`) | `INFO` | Business events visible in all envs; DEBUG calls suppressed in production |

### 4. Log format
`%(asctime)s %(levelname)-8s %(name)s %(message)s`

Readable in both dev console and prod log aggregators. No JSON — keeps it simple.

### 5. Event selection
Only events with operational value are logged:
- `ratings.forms`: rating saved (create vs update) at `INFO`
- `ratings.views`: form validation failure at `WARNING`
- `leaderboard.views`: unknown criterion key fallback at `WARNING`; criterion resolution at `DEBUG`
- `accounts.views`: user registered at `INFO`; private profile blocked at `DEBUG`; visibility changed at `INFO`
- `catalog.views`: logger declared, no events yet (read-only, low risk)

## Risks / Trade-offs

- **Log verbosity in dev** → All INFO events will print to console during tests. Acceptable since `manage.py test` suppresses logging by default.
- **`django.request` at ERROR suppresses 404s** → Intentional. 404s on a dish catalog are not actionable. If 404 monitoring is needed later, raise to `WARNING`.
- **No correlation ID** → Individual log lines aren't tied to a request. Acceptable at current scale; can add middleware later.

## Migration Plan

No migration required. Changes are additive — adding config and log calls to existing files. Rollback is trivially reverting the `LOGGING` dict and removing `getLogger` lines.
