## Context

Rank O Mida already has catalog browsing (`Dish`, `DishType`, `Venue`) and login-required rating via `RatingSubmission` (one per user+dish). There is no favorites/bookmarks feature. Users need a lightweight “want to try later” queue distinct from rating.

Constraints from product decisions:
- One system list only (not named playlists)
- Auto-remove on successful rate
- Dedicated private `/saved/` page
- Auth same as ratings (`@login_required`)

## Goals / Non-Goals

**Goals:**

- Persist a unique (user, dish) save with timestamp
- Save/unsave from dish detail; list and unsave from `/saved/`
- Remove saved row when the user successfully submits a rating for that dish
- Keep the list private (owner-only; not on public profile)

**Non-Goals:**

- Multiple or named playlists
- Public visibility of saved lists
- Anonymous / session-based saves
- Manual reorder or “mark visited” without rating
- Saving unpublished dishes

## Decisions

### 1. Model lives in `catalog` as `SavedDish`

**Choice:** `catalog.SavedDish` with FKs to `User` and `Dish`, `saved_at`, `unique_together = ("user", "dish")`, ordering `-saved_at`.

**Why:** The entity is dish-centric browse intent; catalog already owns `Dish`. A separate app is overkill for one join table. Mirrors the simplicity of ratings’ join without putting save semantics inside `ratings`.

**Alternatives considered:** `accounts.SavedDish` (more user-centric but farther from dish queries); a full `Playlist` model (premature given one-list scope).

### 2. Auto-remove in `submit_rating` after successful form save

**Choice:** Explicit `SavedDish.objects.filter(user=request.user, dish=dish).delete()` in [`ratings/views.py`](ratings/views.py) after `form.save(...)`.

**Why:** Idempotent, obvious, only runs on the user-facing success path. No new signal complexity.

**Alternatives considered:** `post_save` on `RatingSubmission` (also covers admin creates; slightly more magic); delete inside the rating form (couples form to catalog save model more tightly).

### 3. Separate POST endpoints for save and unsave

**Choice:** `POST /dishes/<slug>/save/` and `POST /dishes/<slug>/unsave/` with login required; redirect back to dish detail or `next` (e.g. `/saved/`).

**Why:** Matches the existing form-POST style of rating submit; CSRF-safe; easy to test. HTMX toggle is optional later polish.

### 4. Hide Save when the user already rated the dish

**Choice:** On dish detail, if a `RatingSubmission` exists for the current user and dish, omit the Save control (rating already “completed” the visit intent).

**Why:** Aligns with auto-remove semantics and avoids a dead-end save of something already rated.

### 5. `/saved/` shows published dishes only

**Choice:** Filter `dish__is_published=True`. If a dish is later unpublished, it disappears from the list (row may remain until unsave/rate; list query hides it).

**Why:** Consistent with the rest of catalog browse surfaces.

## Risks / Trade-offs

- **[Risk] Orphan SavedDish rows for unpublished dishes** → Mitigation: list query filters published; optional cleanup later; CASCADE on dish delete removes rows.
- **[Risk] Ratings app depends on catalog SavedDish** → Mitigation: one-line delete is acceptable; catalog already is a dependency of ratings for `Dish`.
- **[Trade-off] No playlists yet** → Starting with one list keeps schema and UX small; playlists can wrap this later if needed.

## Migration Plan

1. Add model + migration; deploy (no user-visible change until views ship).
2. Ship endpoints, templates, nav, and auto-remove together.
3. Rollback: reverse migration removes `SavedDish` table; remove views/templates.

## Open Questions

- None blocking; naming of the CTA (“Save” vs “Want to try”) can follow existing button tone (“Save” / “Unsave”).
