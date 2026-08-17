## Context

`search_text()` is a generator that issues one POST per page. `fetch_photo()` issues two GETs (metadata then binary). Both currently accept a `session` parameter for testability. The command constructs a shared counter for photos today; that pattern extends cleanly to a richer `RequestBudget` object covering all request types.

## Goals / Non-Goals

**Goals:**
- Single `--max-requests N` cap (default 60, 0 = unlimited) covering all Google API HTTP calls in a run.
- `RequestBudget` lives in the service layer so it can be tested independently.
- `search_text` stops paging (silently) when budget is exhausted — no partial-page loss, all results from the current page are yielded first.
- `fetch_photo` raises `PlacesError("request budget exhausted")` when budget is gone — the command already handles this gracefully.
- `--max-photos` removed (one control is better than two).

**Non-Goals:**
- Persistent budget across multiple command invocations.
- Per-SKU budgets (search vs. photo separately).
- Rate limiting / throttling (this is a count limit, not a rate limit).

## Decisions

### 1. `RequestBudget` class in `google_places.py`

```python
class RequestBudget:
    def __init__(self, limit: int):  # 0 = unlimited
        self._limit = limit
        self._used = 0

    def consume(self, n: int = 1) -> bool:
        """Attempt to consume n requests. Returns True if allowed, False if exhausted."""
        if self._limit == 0:
            self._used += n
            return True
        if self._used + n > self._limit:
            return False
        self._used += n
        return True

    @property
    def used(self) -> int:
        return self._used
```

**Alternative — mutable list `[remaining]`**: Already used for `photos_fetched`; works but lacks encapsulation. `RequestBudget` is clearer to read and test.

### 2. `search_text` checks budget before each page POST (not mid-results)

After yielding all results from the current page, before fetching the next page, call `budget.consume(1)`. If it returns `False`, break — the generator simply stops. This is safe: callers already handle the generator ending early (they `list()` it or iterate it).

The first page: consume before the first POST too, so `--max-requests 0` (unlimited) and a budget of exactly 0 both work correctly.

### 3. `fetch_photo` consumes 2 for its two GETs

Call `budget.consume(2)` before the first GET. If denied, raise `PlacesError("request budget exhausted")`. This is conservative (consumes both upfront) but avoids a partial state where metadata was fetched but binary cannot be.

### 4. Default of 60

With defaults (2 queries × 3 pages = 6 search + 20 photos × 2 = 40 photo): 46 total. 60 gives comfortable headroom for retries (`PAGE_TOKEN_ATTEMPTS`) without risking runaway costs.

### 5. Remove `--max-photos`

Two overlapping limits confuse operators. `--max-requests` is strictly more powerful: setting it to `6` allows search only, `46` allows full default behaviour. Document the mapping in the help text.

## Risks / Trade-offs

- **Breaking change**: `--max-photos` is removed. Any scripts using it will need updating to `--max-requests`. Mitigation: note in commit message; it was only added in this session.
- **Photo fetch consumes 2 upfront**: If the metadata call succeeds but binary fails for non-budget reasons, those 2 requests are still counted. Mitigation: acceptable — we want a conservative (upper-bound) count.
