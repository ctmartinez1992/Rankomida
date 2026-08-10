## Why

Users browsing Rank O Mida can rate dishes they have tried, but they have no way to bookmark dishes they want to try later. A single private “saved” list (like YouTube Watch Later) lets people park dishes without rating them yet, then return to that queue from a dedicated page.

## What Changes

- Add a per-user system list of saved dishes (one list only; not named playlists)
- Let logged-in users save and unsave a dish from the dish detail page
- Add a dedicated private page at `/saved/` listing the current user’s saved dishes
- Auto-remove a dish from the saved list when that user successfully rates it
- Add a nav link to `/saved/` for authenticated users
- Do not show Save on dish detail if the user already has a rating for that dish

## Capabilities

### New Capabilities

- `saved-dishes`: Login-required save/unsave of dishes, private `/saved/` list page, and auto-removal when the user rates the dish

### Modified Capabilities

- (none)

## Impact

- **catalog**: new `SavedDish` model, migration, admin, save/unsave and `/saved/` views/URLs, dish detail CTA, saved list template, nav link in `base.html`
- **ratings**: after a successful rating save in `submit_rating`, delete matching `SavedDish` for that user and dish
- **tests**: auth, uniqueness, ownership of `/saved/`, and auto-remove on rate
- **auth**: same login gate as rating submission; anonymous users cannot save
