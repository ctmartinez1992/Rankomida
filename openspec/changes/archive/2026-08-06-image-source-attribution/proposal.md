## Why

Catalog photos on dish types, venues, and dishes have no attribution. Images need an optional human-readable credit and source URL so visitors can see where a photo came from, without blocking uploads when attribution is unknown.

## What Changes

- Add optional `photo_credit` and `photo_source_url` fields on `DishType`, `Venue`, and `Dish`
- Expose those fields next to `photo` in Django admin
- Show credit and source link on hover for every catalog image that has attribution
- Share image rendering via a catalog photo partial
- Restructure venue list cards so the whole card is not a single link (avoids nested links with the source URL)

## Capabilities

### New Capabilities

- `image-attribution`: Optional photo credit and source URL on catalog entities, admin editing, and hover attribution on public image display

### Modified Capabilities

<!-- None — no existing main specs for catalog images -->

## Impact

- `catalog/models.py`: new companion fields on three models
- New migration for the six fields
- `catalog/admin.py`: admin field lists
- Templates under `templates/catalog/` and CSS in `templates/base.html`
- `catalog/tests.py`: coverage for optional fields and hover markup
