## Why

Logged-in users submitting a venue suggestion are asked for a name and email address the system already knows — unnecessary friction. Worse, after submitting, they receive no feedback: the suggestion disappears into a queue with no way to track whether it was approved or rejected. Associating suggestions with user accounts eliminates the redundant fields and enables a self-service status view on the user's profile.

## What Changes

- New `submitted_by` FK (nullable) on `VenueSuggestion` links suggestions to authenticated submitters.
- Submission form hides `submitter_name` and `submitter_email` when the user is authenticated; sets `submitted_by` on save.
- Thanks page provides a link back to the user's profile for authenticated users.
- The profile page gains a "Venue Suggestions" section visible only to the profile owner, showing each suggestion's status, rejection reason (if rejected), and a link to the promoted venue (if approved).
- Admin changelist surfaces `submitted_by`.

## Capabilities

### New Capabilities

- `venue-suggestion-profile-tracking`: Owner-only profile section listing the user's submitted suggestions with status, rejection reason, and venue link.

### Modified Capabilities

- `venue-suggestion-submission`: Authenticated users skip the submitter identity fields; `submitted_by` is set on save; thanks page tailored to auth state.
- `venue-suggestion-admin`: `submitted_by` surfaced in the changelist and change page.

## Impact

- **Model change**: `submitted_by = FK(AUTH_USER_MODEL, null=True, blank=True)` on `catalog.VenueSuggestion` — new migration required.
- **View change**: `catalog/views.py` — `VenueSuggestionCreateView` branches on `request.user.is_authenticated`.
- **Form change**: `catalog/forms.py` — form omits submitter fields when authenticated (handled in view or subclass).
- **Template changes**: `catalog/suggest_venue.html`, `catalog/suggest_venue_success.html`, `accounts/profile.html`.
- **Admin change**: `catalog/admin.py` — `submitted_by` in `list_display` and `readonly_fields`.
- **No breaking changes.** Anonymous submission behaviour is unchanged.
