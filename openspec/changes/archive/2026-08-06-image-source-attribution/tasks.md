## 1. Data model

- [x] 1.1 Add `photo_credit` and `photo_source_url` to DishType, Venue, and Dish
- [x] 1.2 Create and apply Django migration for the six fields

## 2. Admin

- [x] 2.1 Expose `photo_credit` and `photo_source_url` next to `photo` in DishType, Venue, and Dish admins

## 3. Templates and CSS

- [x] 3.1 Add `templates/catalog/_photo.html` partial with hover overlay for credit/source URL
- [x] 3.2 Add `.photo-with-source` hover overlay styles in `templates/base.html`
- [x] 3.3 Use the photo partial in all five catalog templates that render images
- [x] 3.4 Restructure venue list cards so the card is not wrapped in a single `<a>`

## 4. Tests

- [x] 4.1 Add tests for optional attribution fields and hover markup on a public page
