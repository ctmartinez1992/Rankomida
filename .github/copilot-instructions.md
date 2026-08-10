# Copilot Instructions

## Workflow

All changes must follow the OpenSpec flow — never implement directly:

1. **Propose** — `openspec-propose` (or `openspec-explore` first for fuzzy ideas) → produces `proposal.md`, `design.md`, `specs/`, `tasks.md` under `openspec/changes/<change-name>/`
2. **Apply** — `openspec-apply-change` to implement tasks
3. **Archive** — `openspec-archive-change` to sync specs and archive

OpenSpec artifacts live in `openspec/specs/` (main specs) and `openspec/changes/` (active changes).

## Commands

```bash
# Run the dev server
source .venv/bin/activate && python manage.py runserver

# Run all tests
source .venv/bin/activate && python manage.py test

# Run tests for a single app
source .venv/bin/activate && python manage.py test leaderboard
source .venv/bin/activate && python manage.py test ratings
source .venv/bin/activate && python manage.py test catalog

# Run a single test case
source .venv/bin/activate && python manage.py test leaderboard.tests.LeaderboardViewTests.test_overall_ranking_order

# Apply migrations
source .venv/bin/activate && python manage.py migrate

# Create migrations after model changes
source .venv/bin/activate && python manage.py makemigrations
```

Python 3.14 is used. The virtualenv is at `.venv/`.

## Environment

Copy `.env.example` to `.env` for local development. Dokku/production must set secrets via platform config, e.g.:

```bash
dokku config:set <app> \
  SECRET_KEY=... \
  RECAPTCHA_PUBLIC_KEY=... \
  RECAPTCHA_PRIVATE_KEY=...
```

`RECAPTCHA_*` are Google reCAPTCHA **v2** keys (checkbox + invisible share one key pair). If unset locally, Google's published test keys are used.

## Architecture

Django 6 project with SQLite. The config package (`config/`) holds settings, URLs, and WSGI/ASGI. Four apps:

- **`catalog`** — read-only content: `DishType`, `Venue`, `VenueLocation`, `Dish`. Dishes belong to a venue and a dish type. Venues can have multiple `VenueLocation` rows (address + lat/lng).
- **`ratings`** — user submissions: `RatingSubmission` (one per user per dish, `unique_together`), `RatingCriterionScore` (per-criterion breakdown), `CriteriaTemplate` (configures which criteria exist per dish type, with weight/min/max).
- **`leaderboard`** — query-only, no persistent model. `LeaderboardListView` annotates `Dish` with `sort_score` (either avg overall or avg of a specific criterion) and `rating_count` via Django ORM aggregation; sorted live on every request.
- **`accounts`** — `UserProfile` (OneToOne to `auth.User`, `is_public` flag). Profile is auto-created via `post_save` signal.

Templates are in the top-level `templates/` directory (not per-app). Global `base.html` is extended by all pages.

Media files (dish/venue/dish-type photos) are served locally in development from the `media/` root.

## Key Conventions

- **Slugs everywhere**: `DishType`, `Venue`, and `Dish` all have unique slugs used in URLs. URL patterns for dish detail are `/<type_slug>/<dish_slug>/`.
- **RatingSubmissionForm is not a ModelForm**: it builds criterion fields dynamically from `CriteriaTemplate` rows for the dish's type. Field names are `criterion_<template_id>`. `save()` uses `update_or_create` so re-submission updates in place.
- **Leaderboard is annotation-driven**: no `DishAggregateScore` model exists (it was removed). Rankings are computed on-the-fly using `Avg` annotations. The `?criterion=<key>` query param switches to per-criterion ranking; unknown keys fall back to overall.
- **`RANKING_OVERALL_WEIGHT`** in settings (default `1.0`) is reserved for future composite scoring logic.
- **`is_published` / `is_active` guards**: `Dish.is_published` and `DishType.is_active` control visibility. Always filter on these when querying for user-facing content.
- **One rating per user per dish**: enforced by `unique_together = ("user", "dish")` on `RatingSubmission`.
- **`UserProfile` is always get_or_created**, never assumed to exist, even with the signal in place.
