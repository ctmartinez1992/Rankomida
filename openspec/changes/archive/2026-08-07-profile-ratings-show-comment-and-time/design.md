## Context

The profile ratings list template (`_profile_ratings.html`) renders a paginated list of a user's `RatingSubmission` objects. Each entry shows a star score, dish name, venue name, and creation date. The `RatingSubmission` model has a `comment` field (`TextField`, `blank=True`, `default=""`). The date is rendered with Django's `date` filter.

## Goals / Non-Goals

**Goals:**
- Show the comment text (up to 100 words) on each rating entry
- Include submission time in the date display

**Non-Goals:**
- Editing comments from the profile page
- Showing comments on the private profile view
- Pagination or expansion of truncated comments ("read more")

## Decisions

**Template-only implementation**
The data is already present on each `submission` object in the template context. No view, model, or serialiser changes are needed. Django's built-in `truncatewords` filter handles truncation without custom code.

**`{% if submission.comment %}` guard**
Using a truthiness check rather than `{% if submission.comment != "" %}` is idiomatic Django. An empty string is falsy, so no comment block renders when the field is blank.

**Date format `"d M Y, H:i"`**
Produces output like `12 Jul 2026, 14:32` — human-readable, compact, and consistent with the existing style.

## Risks / Trade-offs

- Long comments with no spaces (pathological input) won't be split by `truncatewords` — acceptable edge case, not worth extra handling.
