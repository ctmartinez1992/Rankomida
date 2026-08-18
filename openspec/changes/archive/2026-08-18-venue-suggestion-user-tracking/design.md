## Overview

Three focused changes: a model field, a form/view auth branch, and a profile section. All existing anonymous submission behaviour is preserved.

---

## Model Change

Add to `VenueSuggestion` in `catalog/models.py`:

```python
submitted_by = models.ForeignKey(
    settings.AUTH_USER_MODEL,
    on_delete=models.SET_NULL,
    null=True,
    blank=True,
    related_name="venue_suggestions",
)
```

`SET_NULL` means suggestions survive if a user account is deleted. The existing `submitter_name` and `submitter_email` fields are kept for anonymous submissions.

---

## Submission Form & View

`VenueSuggestionCreateView` branches on `request.user.is_authenticated`:

```
GET /venues/suggest/
        │
        ├─ authenticated ──▶ VenueSuggestionForm(exclude submitter fields)
        │                    Hint text: "Submitting as <username>"
        │
        └─ anonymous    ──▶ VenueSuggestionForm (full, current behaviour)

POST /venues/suggest/
        │
        ├─ authenticated ──▶ form.save(commit=False)
        │                    suggestion.submitted_by = request.user
        │                    suggestion.save()
        │
        └─ anonymous    ──▶ form.save() (current behaviour)
```

Implementation: use a single `VenueSuggestionForm` with an `__init__` parameter `authenticated=False` that pops `submitter_name` and `submitter_email` when `True`.

---

## Thanks Page

```
/venues/suggest/thanks/

  If authenticated:
    "Thanks! You can track the status of your suggestion on your profile."
    [View your profile →]   → {% url 'profile' user.username %}

  If anonymous:
    Current message (unchanged)
```

The template receives `user` from the request context automatically; no view change needed beyond passing an `authenticated` flag or relying on `{% if user.is_authenticated %}`.

---

## Profile Section

Added to `templates/accounts/profile.html`, inside the existing `{% if request.user == profile_user %}` guard:

```
Venue Suggestions
─────────────────────────────────────────────────
El Faro · Madrid           ● Pending
Casa Botín · Madrid        ✓ Approved → Casa Botín ↗
Mesón del Jamón · Madrid   ✗ Rejected
                             "Venue already in catalog"
─────────────────────────────────────────────────
```

**Data source:** `profile_user.venue_suggestions.all().order_by("-created_at")`

The view (`accounts/views.py`) needs to pass this queryset (or it can be accessed directly in the template via `profile_user.venue_suggestions.all`).

**Status presentation:**

| Status    | Badge style          | Extra info                                          |
|-----------|----------------------|-----------------------------------------------------|
| pending   | neutral (muted)      | —                                                   |
| approved  | success (green-ish)  | Link to `promoted_venue` if published               |
| rejected  | error (red-ish)      | `rejection_reason` if non-empty                     |
| duplicate | neutral (muted)      | —                                                   |

**Venue link guard:** only shown when `suggestion.promoted_venue` is not null **and** `suggestion.promoted_venue.is_published` is True. A venue promoted from a suggestion is created unpublished — the link appears once admin publishes it.

**Section visibility:** rendered only when `request.user == profile_user`. Not affected by `is_public`.

**Empty state:** section is not rendered if `profile_user.venue_suggestions.count() == 0`.

---

## Admin Change

`VenueSuggestionAdmin`:
- Add `submitted_by` to `list_display` (after `name`)
- Add `submitted_by` to `readonly_fields`
- Add `submitted_by` to the fieldset (in the "Submitter" section alongside `submitter_name`/`submitter_email`)

---

## Out of Scope

- Email notifications when suggestion status changes
- Merging an anonymous suggestion with a user account after login
- Public suggestion history (e.g. "suggested by carlosmartinez" shown to all visitors)
