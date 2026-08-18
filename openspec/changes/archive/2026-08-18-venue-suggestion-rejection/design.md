## Overview

Extends the existing `VenueSuggestionAdmin` with a structured rejection workflow. The design mirrors the existing "add as location" pattern: a changelist action redirects to an intermediate admin page, the admin fills in an optional reason, submits, and the records are updated.

---

## Model Change

Add to `VenueSuggestion` in `catalog/models.py`:

```python
rejection_reason = models.TextField(blank=True)
```

No other field or status value changes are needed — `STATUS_REJECTED = "rejected"` already exists.

---

## Reject Flow

```
Changelist: select 1–N pending suggestions
        │
        │  Action: "Reject suggestion(s)"
        ▼
GET /admin/catalog/venuesuggestion/reject/?ids=1,2,3
        │
        │  Renders intermediate confirmation page:
        │    - List of suggestions being rejected (name, city)
        │    - Optional "Reason" textarea
        │    - Submit ("Confirm rejection") + Cancel buttons
        ▼
POST /admin/catalog/venuesuggestion/reject/
        │
        │  For each suggestion ID:
        │    suggestion.status = "rejected"
        │    suggestion.rejection_reason = reason
        │    suggestion.save()
        ▼
Redirect → VenueSuggestion changelist
           + success message: "N suggestion(s) rejected."
```

**Change-page button flow:**

The "Reject" button on the change page links to the same intermediate URL but with a single ID:
```
/admin/catalog/venuesuggestion/reject/?ids=<pk>
```

This keeps both paths using the same view and template.

---

## Guard: block rejection of approved suggestions

Before rendering or processing the form, check all supplied IDs:
- If any suggestion has `status="approved"`: abort with an error message listing the affected names.
- Only then render the confirmation form or process the POST.

---

## Admin URL

```
GET   /admin/catalog/venuesuggestion/reject/   → render confirmation form
POST  /admin/catalog/venuesuggestion/reject/   → process and redirect
```

IDs are passed as a comma-separated `ids` query parameter (GET) or hidden field (POST).

---

## Change Page Updates

The "Context" fieldset gains `rejection_reason`:

```python
fieldsets = (
    ...
    ("Context", {
        "fields": ("search_query", "promoted_venue_link", "rejection_reason", "created_at", "updated_at"),
    }),
)
```

`rejection_reason` is **not** in `readonly_fields` — admins can edit it directly on the change page if needed. It is displayed only when relevant (non-empty), though it remains in the fieldset regardless.

---

## Templates

| Template | Purpose |
|---|---|
| `admin/catalog/venuesuggestion/reject_confirmation.html` | Intermediate rejection form (extends `admin/base_site.html`) |
| `admin/catalog/venuesuggestion/change_form.html` | Updated to add "Reject" button in object-tools block |

---

## Out of Scope

- Email notification to submitter on rejection
- Per-suggestion individual reasons when bulk-rejecting (single shared reason applies to all)
- Undo / revert rejected status
