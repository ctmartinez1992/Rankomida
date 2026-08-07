## Why

The profile ratings list shows each rating's score, dish name, venue, and date, but omits the user's comment and the exact time of submission. Adding comment text (truncated to 100 words) and the submission time makes each entry more informative without requiring the viewer to navigate elsewhere.

## What Changes

- Display `submission.comment` below each rating entry, truncated to 100 words, when a comment is present; render nothing when the comment is empty
- Show submission time alongside the date (e.g. `12 Jul 2026, 14:32`) instead of date only

## Capabilities

### New Capabilities

- `profile-rating-comment-display`: Renders the comment text on each profile rating entry — truncated to 100 words, omitted entirely when empty.

### Modified Capabilities

<!-- None — no existing spec-level behaviour is changing -->

## Impact

- `templates/accounts/_profile_ratings.html`: date format and comment display block
- No model, view, URL, or migration changes required
