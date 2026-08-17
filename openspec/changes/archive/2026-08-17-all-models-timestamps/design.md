## Context

Following the pattern established for `Venue` and `VenueLocation`, we need to bring six more models up to the same standard. `RatingSubmission` is already complete. `SavedDish` has `saved_at` (auto_now_add) which semantically equals `created_at`, so only `updated_at` is added there.

## Goals / Non-Goals

**Goals:**
- `DishType`, `Dish`: add `created_at` + `updated_at`
- `SavedDish`: add `updated_at` only (keep `saved_at` as-is for backwards compat)
- `CriteriaTemplate`, `RatingCriterionScore`: add `created_at` + `updated_at`
- `UserProfile`: add `created_at` + `updated_at`
- Hand-written migrations with `default=django.utils.timezone.now` + `preserve_default=False` to avoid interactive prompts

**Non-Goals:**
- Exposing new columns in admin list views (inline/detail read-only is sufficient where already shown)
- Backfilling historical data (migration timestamp is the accepted default for existing rows)
- Changing any public-facing views or APIs

## Decisions

- Same `auto_now_add` / `auto_now` pattern used throughout — no custom signal or override logic.
- `SavedDish.updated_at` added even though records are rarely mutated — keeps the contract uniform.
- No admin list changes — `DishType`, `Dish`, `CriteriaTemplate`, `RatingCriterionScore`, `UserProfile` admin classes get `created_at`/`updated_at` added to `readonly_fields` only where an admin class already defines `fields`/`readonly_fields`. Others get no admin change (Django auto-excludes uneditable fields).

## Risks / Trade-offs

- Six models × hand-written migrations: low risk, purely additive columns.
- `auto_now` won't fire on `queryset.update()` — accepted trade-off consistent with existing models.
