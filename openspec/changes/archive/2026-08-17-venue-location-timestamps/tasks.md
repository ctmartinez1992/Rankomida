## 1. Model Changes

- [x] 1.1 Add `created_at = models.DateTimeField(auto_now_add=True)` and `updated_at = models.DateTimeField(auto_now=True)` to `VenueLocation` in `catalog/models.py`

## 2. Migration

- [x] 2.1 Hand-write migration `0011_venuelocation_created_at_updated_at.py` using `default=django.utils.timezone.now` and `preserve_default=False` for `created_at`

## 3. Admin Changes

- [x] 3.1 Add `created_at` and `updated_at` to `VenueLocationInline.readonly_fields` in `catalog/admin.py`
- [x] 3.2 Add `created_at` and `updated_at` to `VenueLocationInline.fields` so they appear in the inline form

## 4. Verification

- [x] 4.1 Run `python manage.py migrate` and confirm no errors
- [x] 4.2 Run `python manage.py test catalog` and confirm all tests pass
