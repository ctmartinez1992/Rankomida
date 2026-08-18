## Context

The project uses Django's admin framework. Venues were imported from Google Places as individual rows, but many represent branches of the same real-world restaurant chain. There is an existing `VenueLocation` model designed exactly for this: one `Venue` with many `VenueLocation` rows. The merge operation consolidates duplicate `Venue` rows into a single survivor, reassigning all related data.

Django admin actions normally execute immediately on a queryset with no intermediate UI. Merging requires the admin to choose a survivor, so a custom intermediate confirmation page is needed.

## Goals / Non-Goals

**Goals:**
- Allow selecting 2+ venues in the admin changelist and merging them into one
- Admin picks the survivor venue via an intermediate confirmation page
- All `VenueLocation`, `Dish`, `RatingSubmission`, `RatingCriterionScore`, and `SavedDish` rows from non-survivors are reassigned or merged into the survivor
- Dishes with the same name across merging venues are collapsed into one (the survivor's dish), with ratings merged
- The entire operation runs atomically

**Non-Goals:**
- URL redirects for deleted venue slugs
- Undo / rollback (standard admin, no audit trail)
- Merging dishes with different names into one
- UI outside Django admin

## Decisions

### Intermediate confirmation page via custom admin URL

**Decision:** The action redirects to a custom admin view (added via `VenueAdmin.get_urls()`) rather than executing immediately.

**Why:** Django's standard action POST is one-shot. The survivor selection requires a form with dynamic radio options per selection. A custom view is the standard Django pattern for this.

**Alternative considered:** Use Django's `admin/action_confirmation.html` pattern with a hidden form — rejected because it can't carry the dynamic radio input needed for survivor selection.

### Auto-merge colliding dishes by name

**Decision:** When a non-survivor has a dish whose name matches a dish in the survivor, the dishes are automatically merged (ratings reassigned, non-survivor dish deleted).

**Why:** These venues are the same real-world chain. Dishes with the same name are the same product. The admin confirmed this is the expected behavior. The alternative (blocking on conflict) would make the action unusable for the most common case.

### Survivor's rating wins on user conflict

**Decision:** If a user rated both the survivor's dish and a to-be-merged non-survivor dish, the non-survivor submission (and its `RatingCriterionScore` rows) is deleted; the survivor's submission is kept.

**Why:** We must preserve `unique_together = ("user", "dish")`. The survivor's submission is treated as authoritative. We cannot average or combine two `RatingCriterionScore` sets without business-logic risk.

### SavedDish conflict: same strategy

**Decision:** If a user saved both the survivor's dish and the to-be-merged dish, the non-survivor `SavedDish` row is deleted.

**Why:** Same uniqueness constraint. Deduplication is lossless here since the semantic outcome (dish is saved) is preserved.

## Risks / Trade-offs

- **Accidental merge is irreversible** → Mitigation: The confirmation page shows full impact (location count, dish count, dishes that will be auto-merged) before committing.
- **Rating data loss on user conflict** → Mitigation: Rare in practice (same user would have to have visited and rated the same dish at two separate venues of the same chain). Disclosed in the confirmation page summary.
- **Large venue sets could be slow** → Mitigation: All queries run in a single `transaction.atomic` block; acceptable for an admin-only operation used infrequently.

## Open Questions

None — all decisions confirmed with the product owner before implementation.
