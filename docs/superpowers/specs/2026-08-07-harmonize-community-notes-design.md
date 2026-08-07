# Design: Harmonize Community Notes with Profile Ratings

**Date:** 2026-08-07  
**Scope:** Single template change — `templates/catalog/_community_notes.html`

## Goal

Make community notes rating cards look identical to profile ratings cards in visual structure, layout, and information density.

## Changes

### `_community_notes.html`

| Element | Before | After |
|---|---|---|
| `.rank-entry` | No flex-wrap | Add `style="flex-wrap:wrap;"` |
| Star score | `Score: {{ score\|score_as_stars }}` | `{{ score\|score_as_stars }}` (no "Score:" prefix) |
| Date | Not shown | Add `<span class="score-badge">{{ submission.created_at\|date:"d M Y, H:i" }}</span>` |
| Comment | `<div class="venue-name community-comment">` | `<p class="rating-comment" style="width:100%;margin:0.4rem 0 0;overflow-wrap:break-word;word-break:break-word;">` |

### No view changes needed

`created_at` is already present on every `RatingSubmission` object. Sort options are already identical across both fragments.

## Out of Scope

- Dish type filter (community notes is scoped to a single dish already)
- Any backend/API changes
