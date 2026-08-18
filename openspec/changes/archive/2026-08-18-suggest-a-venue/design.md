## Overview

Two new capabilities: a public suggestion form and an admin review/promotion workflow. Both are self-contained within the `catalog` app. No authentication is required to submit a suggestion.

---

## Model: `VenueSuggestion`

Lives in `catalog/models.py`.

```
┌──────────────────────────────────────────────────────┐
│                   VenueSuggestion                    │
├──────────────────┬───────────────────────────────────┤
│ name             │ CharField(200) — required          │
│ city             │ CharField(120) — required          │
│ address          │ CharField(255, blank=True)         │
│ website_url      │ URLField(blank=True)               │
│ notes            │ TextField(blank=True)              │
│ submitter_name   │ CharField(120, blank=True)         │
│ submitter_email  │ EmailField(blank=True)             │
│ search_query     │ CharField(200, blank=True)         │
│ status           │ CharField, choices below           │
│ promoted_venue   │ FK(Venue, null=True, blank=True)   │
│ created_at       │ DateTimeField(auto_now_add=True)   │
│ updated_at       │ DateTimeField(auto_now=True)       │
└──────────────────┴───────────────────────────────────┘

Status choices:
  pending   → default on creation
  approved  → set by admin on promotion
  rejected  → set manually by admin
  duplicate → set manually by admin
```

`search_query` captures the original venue search term that triggered the "no results" state, providing admin context.

`promoted_venue` is set when the suggestion is approved via either admin promotion action.

---

## Submission Flow

```
Venue list (no results)
        │
        │  "Suggest a venue →" link
        │  href="/venues/suggest/?q=<search_q>"
        ▼
VenueSuggestionCreateView  GET
        │
        │  Renders form, pre-populates name from ?q=
        │  Also stores ?q= in hidden field → search_query
        ▼
VenueSuggestionCreateView  POST (valid)
        │
        │  save() → VenueSuggestion(status="pending")
        ▼
/venues/suggest/thanks/   TemplateView
```

- No authentication required.
- Form validation: `name` and `city` are required; all other fields optional.
- `search_query` is a hidden field populated by the view from `request.GET.get("q", "")`.
- No email confirmation is sent on submission (out of scope).

---

## Admin Review Flow

```
VenueSuggestion changelist
        │
        ├─── Action: "Promote to new Venue"  ─────────────────────────┐
        │         (single-item changelist action)                      │
        │                                                              ▼
        │                                              Creates Venue(name, city)
        │                                              Creates VenueLocation(city, address, website_url)
        │                                              suggestion.status = "approved"
        │                                              suggestion.promoted_venue = new_venue
        │                                              Redirects to Venue change page
        │
        └─── Action: "Add as location of existing Venue"  ────────────┐
                  (single-item, from change page button)               │
                                                                       ▼
                                                       Intermediate admin page:
                                                       - Dropdown: select existing Venue
                                                       - Submit
                                                           │
                                                           ▼
                                                       Creates VenueLocation(venue=selected,
                                                         city, address, website_url)
                                                       suggestion.status = "approved"
                                                       suggestion.promoted_venue = selected_venue
                                                       Redirects to VenueLocation change page
```

### Promote to new Venue — detail

- Creates `Venue` with `name=suggestion.name`, `city=suggestion.city`, `source="manual"`, `is_published=False` (admin publishes separately).
- Creates `VenueLocation` with `venue=new_venue`, `city=suggestion.city`, `address=suggestion.address`, `website_url=suggestion.website_url`.
- Available as a **changelist action** (works on a single selected row) and as a **button on the suggestion change page**.
- If more than one suggestion is selected in the changelist, the action is blocked with a message: "Select exactly one suggestion to promote."

### Add as location of existing Venue — detail

- Implemented as a custom admin URL: `/admin/catalog/venuesuggestion/<id>/add-location/`
- The intermediate page shows a simple form: a `ModelChoiceField` for `Venue` (all venues, ordered by name).
- On submit, creates `VenueLocation` and marks suggestion approved.
- Available only from the suggestion **change page** (a button in the submit row area).

---

## URLs

```
urlpatterns (catalog/urls.py):
  GET/POST  venues/suggest/         name="suggest_venue"
  GET       venues/suggest/thanks/  name="suggest_venue_thanks"
```

These sit alongside existing catalog URLs.

---

## Templates

| Template | Purpose |
|---|---|
| `catalog/suggest_venue.html` | Form page — extends `base.html` |
| `catalog/suggest_venue_success.html` | Thank-you page — extends `base.html` |

The venue list template `catalog/venue_list.html` gains a "Suggest a venue" link rendered only when `venues` queryset is empty.

---

## Admin Registration

`VenueSuggestionAdmin` in `catalog/admin.py`:

- `list_display`: `name`, `city`, `status`, `search_query`, `created_at`
- `list_filter`: `status`
- `search_fields`: `name`, `city`, `submitter_email`
- `readonly_fields`: `promoted_venue`, `search_query`, `created_at`, `updated_at`
- `actions`: `promote_to_new_venue` (changelist action)
- Change page: custom button "Add as location of existing Venue" rendered via `change_view` override or `object_tools` block

---

## Out of Scope

- Email notification to submitter on approval
- Spam/rate-limiting on the public form (can add reCAPTCHA later via existing `form-recaptcha` spec)
- Duplicate detection on submission
- Authenticated-only submissions
