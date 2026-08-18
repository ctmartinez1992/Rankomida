## Context

`Venue.is_published` already exists on the model (default `True`). `VenueAdmin` is registered in `catalog/admin.py` with `list_display`, `list_filter`, and `search_fields` already configured. Django's admin action system allows registering callables on `ModelAdmin` that receive the current queryset.

## Goals / Non-Goals

**Goals:**
- Add a "Publish selected venues" action to the Venue changelist that sets `is_published=True` on all selected rows.
- Add an "Unpublish selected venues" action to the Venue changelist that sets `is_published=False` on all selected rows.
- Show a translated success message with the affected count after each action.

**Non-Goals:**
- No publish/unpublish action on `DishAdmin` or `DishTypeAdmin`.
- No REST API endpoint.
- No model changes or migrations.
- No cascade publishing of related dishes.

## Decisions

- Use queryset `update()` rather than iterating and saving individual records — atomic and efficient for bulk operations.
- Register actions via the `actions` attribute on `VenueAdmin` so they appear in the changelist "Action" dropdown.
- Use `ngettext` for the success message to handle singular/plural correctly.

## Risks / Trade-offs

- `queryset.update()` bypasses model `save()` signals. This is acceptable here since `is_published` has no signal handlers.
