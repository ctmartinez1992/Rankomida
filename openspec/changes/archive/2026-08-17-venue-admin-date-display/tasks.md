## 1. Model Changes

- [x] 1.1 Add `created_at = models.DateTimeField(auto_now_add=True)` and `updated_at = models.DateTimeField(auto_now=True)` fields to the `Venue` model in `catalog/models.py`

## 2. Migration

- [x] 2.1 Run `python manage.py makemigrations catalog` to generate the migration for the two new `Venue` fields

## 3. Admin Changes

- [x] 3.1 In `catalog/admin.py`, update `VenueAdmin.list_display` to replace `"source"` with `"created_at"` and `"updated_at"`
- [x] 3.2 Add `created_at` and `updated_at` to `VenueAdmin.readonly_fields` (required because `auto_now`/`auto_now_add` fields are not editable)

## 4. Verification

- [x] 4.1 Run `python manage.py migrate` and confirm no errors
- [x] 4.2 Run `python manage.py test catalog` and confirm all tests pass
