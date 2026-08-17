## 1. Service Layer — RequestBudget

- [x] 1.1 Add `RequestBudget` class to `catalog/services/google_places.py`: `__init__(self, limit: int)` (0 = unlimited), `consume(self, n: int = 1) -> bool`, `used` property
- [x] 1.2 Add optional `budget: RequestBudget | None = None` parameter to `search_text()`; call `budget.consume(1)` before each page POST — if it returns `False`, stop the generator (break the page loop); `None` budget means unlimited
- [x] 1.3 Add optional `budget: RequestBudget | None = None` parameter to `fetch_photo()`; call `budget.consume(2)` before the first GET — if it returns `False`, raise `PlacesError("request budget exhausted")`

## 2. Command — Replace --max-photos with --max-requests

- [x] 2.1 Remove `--max-photos` argument from `add_arguments()` and all references in `handle()`, `_process()`, and `_fetch_and_save_photo()` (revert the counter/list pattern introduced in the previous change)
- [x] 2.2 Add `--max-requests` argument with `type=int`, `default=60`, help text explaining it caps all Google Maps API HTTP calls (search pages + photo metadata + photo binary) and that `0` means unlimited
- [x] 2.3 In `handle()`, construct `budget = RequestBudget(max_requests)` and pass it to `search_text()` calls
- [x] 2.4 In `_fetch_and_save_photo()`, accept `budget` and pass it to `fetch_photo()`; remove the old `max_photos`/`photos_fetched` parameters
- [x] 2.5 Log a warning in `handle()` when a query yields no results because the budget was exhausted mid-search (detect via budget.used vs max_requests)

## 3. Tests

- [x] 3.1 Add `RequestBudget` unit tests: `consume` decrements correctly, returns `False` when exhausted, limit=0 always returns `True`
- [x] 3.2 Update `search_text` tests (if any) to pass a budget and verify it stops paging when exhausted
- [x] 3.3 Update `fetch_photo` tests to verify it raises `PlacesError` when budget is exhausted before the first GET
- [x] 3.4 Update `ImportGooglePlacesPhotoTests` to use `--max-requests` instead of `--max-photos`; add test: `--max-requests` small enough to exhaust budget mid-run stops photo fetches but still creates venues; `--max-requests 0` is unlimited
