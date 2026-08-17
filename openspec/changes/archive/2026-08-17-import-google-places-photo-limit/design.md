## Context

The import command calls `_fetch_and_save_photo()` for each newly created venue. There is currently no guard against running this for every place in a large batch. The `handle()` method orchestrates all per-place work; `_fetch_and_save_photo()` is a method on the command class, making it straightforward to thread a counter through.

## Goals / Non-Goals

**Goals:**
- Add `--max-photos N` argument (default `20`) that caps photo API calls per run.
- `--max-photos 0` disables photo fetching entirely.
- Log a one-time warning at the point the limit is reached.

**Non-Goals:**
- Per-query limits (limit is global for the whole run).
- Persisting the counter across runs (each invocation starts fresh).
- Changing the default for existing callers who pass `--max-photos` explicitly.

## Decisions

### 1. Counter lives in `handle()`, passed to `_process()` / `_fetch_and_save_photo()`

The simplest approach: add a `photos_fetched: int` counter in `handle()` and pass `max_photos` down into `_process()`. `_fetch_and_save_photo()` receives both and increments the counter (via a mutable container or by returning a bool).

**Alternative — instance variable on the command:** Would work but makes the command stateful across multiple `handle()` calls in tests; passing it explicitly is safer.

### 2. Default of 20

20 photos costs $0.14 — well within a single run's free-tier budget even if the command is run daily. Operators who want more can raise it explicitly. `0` is the clean opt-out.

### 3. Warning logged once when limit is first hit

A single `logger.warning` + `self.stdout.write` when `photos_fetched == max_photos` avoids spamming the output for every skipped place.

## Risks / Trade-offs

- **Under-fetching on large first imports**: If a run has 60 new venues and `--max-photos 20`, 40 will have no photo. Operators can re-run (the guard skips already-photographed venues, so only the 40 unphotographed ones incur fetches). Mitigation: document this in the help text.
