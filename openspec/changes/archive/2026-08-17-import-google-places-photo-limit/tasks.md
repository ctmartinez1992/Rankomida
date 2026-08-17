## 1. Command Argument

- [x] 1.1 Add `--max-photos` argument to `add_arguments()` in `import_google_places.py` with `type=int`, `default=20`, and help text explaining it caps Places Photo API calls per run and that `0` disables photo fetching

## 2. Counter Logic

- [x] 2.1 In `handle()`, read `max_photos = options["max_photos"]` and initialise `photos_fetched = 0`; pass both to `_process()`
- [x] 2.2 Update `_process()` signature to accept `max_photos` and `photos_fetched` (use a `list` of one int as a mutable counter so it can be incremented inside `_fetch_and_save_photo`)
- [x] 2.3 In `_fetch_and_save_photo()`, skip and return immediately when `max_photos > 0` and `photos_fetched[0] >= max_photos`; also skip when `max_photos == 0`
- [x] 2.4 After a successful photo save, increment `photos_fetched[0]`; log a one-time warning via `logger.warning` and `self.stdout.write` on the first skip due to limit

## 3. Tests

- [x] 3.1 Add tests to `ImportGooglePlacesPhotoTests`: limit of 1 saves photo for first venue only and skips second; `--max-photos 0` saves no photos; venues beyond the limit are still created as venues/locations without photos
