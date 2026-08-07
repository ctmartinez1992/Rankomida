## 1. Settings Configuration

- [x] 1.1 Add `LOGGING` dict to `config/settings.py` with a single `StreamHandler` console handler, format `%(asctime)s %(levelname)-8s %(name)s %(message)s`, `disable_existing_loggers: False`, Django loggers at WARNING/ERROR, and app loggers (`catalog`, `ratings`, `leaderboard`, `accounts`) at INFO

## 2. Ratings App Logging

- [x] 2.1 Add `import logging` and `logger = logging.getLogger(__name__)` to `ratings/forms.py`; capture the `created` bool from `update_or_create` in `save()` and emit `logger.info("rating.saved user_id=%s dish_slug=%s action=%s", user.id, self.dish.slug, "create" if created else "update")`
- [x] 2.2 Add `import logging` and `logger = logging.getLogger(__name__)` to `ratings/views.py`; emit `logger.warning("rating.form_invalid user_id=%s dish_slug=%s errors=%s", request.user.id, dish.slug, form.errors)` in the invalid POST branch

## 3. Leaderboard App Logging

- [x] 3.1 Add `import logging` and `logger = logging.getLogger(__name__)` to `leaderboard/views.py`; in `_get_criterion` emit `logger.debug("leaderboard.criterion_resolved dish_type=%s key=%s", ...)` on success and `logger.warning("leaderboard.criterion_not_found dish_type=%s key=%s", ...)` when the key is non-empty but the template lookup returns `None`

## 4. Accounts App Logging

- [x] 4.1 Add `import logging` and `logger = logging.getLogger(__name__)` to `accounts/views.py`; emit `logger.info("accounts.registered user_id=%s", user.id)` after successful `form.save()` in `register`; emit `logger.debug("accounts.profile_private_blocked viewer=%s target=%s", request.user, profile_user.username)` in the private-profile guard; emit `logger.info("accounts.visibility_changed user_id=%s is_public=%s", request.user.id, form.instance.is_public)` after saving `ProfileVisibilityForm`

## 5. Catalog App Logging

- [x] 5.1 Add `import logging` and `logger = logging.getLogger(__name__)` to `catalog/views.py` (no event calls needed — logger presence only)

## 6. Verification

- [x] 6.1 Run `python manage.py test` and confirm all existing tests pass
- [x] 6.2 Start the dev server and manually submit a rating; confirm `rating.saved ... action=create` appears in the console
