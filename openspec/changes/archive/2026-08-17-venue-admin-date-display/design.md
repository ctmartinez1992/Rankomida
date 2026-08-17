## Context

The Django admin `VenueAdmin` currently shows `name`, `city`, `slug`, `is_published`, and `source` in the list view. Operators want to see when venues were created and last modified so they can track recent imports and edits. The `source` column is lower priority for list scanning and will be removed from the list view (it stays on the model and form).

The `Venue` model has no timestamp fields today, so they must be added via migration.

## Goals / Non-Goals

**Goals:**
- Add `created_at` (auto-set on insert) and `updated_at` (auto-set on every save) to `Venue`
- Show both columns in the admin list view, replacing `source`
- Allow column-header sorting by both dates
- Migration is non-destructive; existing rows get the current timestamp as their `created_at`/`updated_at` value (Django default behaviour for `auto_now_add`/`auto_now` with existing rows)

**Non-Goals:**
- Changing any public-facing views
- Adding timestamps to `VenueLocation`, `Dish`, or other models
- Displaying dates in a custom formatted column (Django default datetime formatting is sufficient)

## Decisions

- Use `auto_now_add=True` for `created_at` and `auto_now=True` for `updated_at` — standard Django pattern, no manual management needed, fields are automatically `readonly` in model forms.
- Remove `source` from `list_display` only; it remains in `fields` so the edit form still exposes it.
- Add both date fields to `readonly_fields` in `VenueAdmin` since `auto_now`/`auto_now_add` fields cannot be edited.
- No explicit `date_hierarchy` or custom `list_filter` on dates — simple column sort is sufficient.

## Risks / Trade-offs

- `auto_now` means `updated_at` is always set on `.save()`, including bulk updates that call `.save()` per object; `queryset.update()` won't touch it. This is acceptable for admin use.
- Existing rows will have `created_at` = migration timestamp, not their true creation date. There is no historical data to backfill, so this is acceptable.
