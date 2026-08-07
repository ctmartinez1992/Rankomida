## Context

Photos live as optional `ImageField`s on `DishType`, `Venue`, and `Dish`. There is no separate Image model and no attribution metadata. Images are uploaded via Django admin and rendered in catalog templates.

## Goals / Non-Goals

**Goals:**

- Store optional human-readable credit and source URL alongside each entity photo
- Edit attribution in admin next to the photo field
- Show attribution on hover for every public catalog image that has credit and/or URL
- Keep attribution optional even when a photo is present

**Non-Goals:**

- Standalone Image model or multi-image galleries
- Required attribution validation
- User-facing photo upload outside admin
- Licensing / rights workflow beyond credit + URL

## Decisions

1. **Companion fields on existing models** instead of a new Image model — matches the current 1:1 photo pattern and keeps the change small.
2. **Shared `_photo.html` partial** — one place for hover markup so all five templates stay consistent.
3. **Hover overlay with real `<a>`** — credit text visible on hover; if URL is set, link text is the credit (or “Source” when credit is empty). Opens in a new tab.
4. **Venue list card restructure** — stop wrapping the whole card in `<a>` so source links are valid HTML; link the venue name like other list pages.

## Risks / Trade-offs

- [Existing rows with photos lack attribution] → Fields are blank by default; images still render without overlay until staff fill them in.
- [Touch devices have no hover] → Overlay still appears on focus/hover where CSS supports it; acceptable for this scope.
- [Duplicated field names across three models] → Acceptable trade-off vs introducing an Image abstraction.

## Migration Plan

1. Add fields via Django migration (nullable/blank, no data backfill required).
2. Deploy migration, then staff can fill credits/URLs in admin over time.
3. Rollback: reverse migration removes the six fields; templates must revert together.
