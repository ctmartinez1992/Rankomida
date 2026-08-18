## 1. Implement bulk publish/unpublish admin actions

- [x] 1.1 Add `publish_venues` action function to `VenueAdmin` in `catalog/admin.py`: calls `queryset.update(is_published=True)` and adds a success message using `ngettext`.
- [x] 1.2 Add `unpublish_venues` action function to `VenueAdmin` in `catalog/admin.py`: calls `queryset.update(is_published=False)` and adds a success message using `ngettext`.
- [x] 1.3 Register both actions on `VenueAdmin` via the `actions` attribute.

## 2. Verify

- [x] 2.1 Run `python manage.py test catalog` and confirm all tests pass.
