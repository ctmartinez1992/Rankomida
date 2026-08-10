## 1. Data model

- [x] 1.1 Add `SavedDish` model to `catalog/models.py` (user, dish, `saved_at`, unique together, ordering)
- [x] 1.2 Create and apply migration
- [x] 1.3 Register `SavedDish` in `catalog/admin.py`

## 2. Endpoints

- [x] 2.1 Add login-required save and unsave POST views (idempotent save; unsave respects `next`)
- [x] 2.2 Add login-required `GET /saved/` list view (own published dishes, `-saved_at`)
- [x] 2.3 Wire URLs in `catalog/urls.py`

## 3. Auto-remove on rate

- [x] 3.1 After successful `form.save` in `ratings.views.submit_rating`, delete matching `SavedDish` for user+dish

## 4. UI

- [x] 4.1 Add Save/Unsave (or login) controls on dish detail; hide Save when user already rated
- [x] 4.2 Add `templates/catalog/saved_list.html` with list, unsave actions, and empty state
- [x] 4.3 Add authenticated nav link to `/saved/` in `templates/base.html`

## 5. Tests

- [x] 5.1 Test save requires login, creates unique row, second save is no-op
- [x] 5.2 Test unsave removes row; `/saved/` lists only own published items
- [x] 5.3 Test successful rating POST removes `SavedDish` for that user+dish
