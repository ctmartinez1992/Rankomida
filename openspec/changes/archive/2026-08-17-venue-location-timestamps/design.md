## Context

`VenueLocation` is the per-address child of `Venue`. It can be populated manually or synced from Google Places (which already tracks its own `last_synced_at`). We want Django-managed `created_at` / `updated_at` timestamps for auditability, consistent with the `Venue` model.

## Goals / Non-Goals

**Goals:**
- Add `created_at` (`auto_now_add=True`) and `updated_at` (`auto_now=True`) to `VenueLocation`
- Non-destructive migration; existing rows receive the current timestamp as their initial value

**Non-Goals:**
- Surfacing the columns in the admin list view (the inline editor already shows all fields; these will be `readonly_fields` in the inline)
- Adding timestamps to any other model

## Decisions

- Same approach as `Venue`: `auto_now_add` + `auto_now`, hand-written migration with `default=django.utils.timezone.now` and `preserve_default=False` to avoid the interactive prompt.
- Add both fields to `VenueLocationInline.readonly_fields` in `admin.py` so they are visible (read-only) in the venue detail page.

## Risks / Trade-offs

- `auto_now` won't fire on `queryset.update()` — same accepted trade-off as for `Venue`.
- Existing rows will have `created_at` = migration timestamp. No historical data to backfill.
