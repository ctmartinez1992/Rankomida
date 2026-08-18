# Spec: venue-suggestion-profile-tracking

## Purpose

Allow logged-in users to track the status of their own venue suggestions directly from their profile page.

---

## Requirements

### Visibility

- The "Venue Suggestions" section is shown on the profile page **only when the viewing user is the profile owner** (`request.user == profile_user`).
- The section is **not** affected by the profile's `is_public` setting — it is always private to the owner.
- The section is **not rendered** if the user has submitted no suggestions.

### Content

- Each suggestion is listed in order of submission (newest first).
- Each row shows: venue name, city, status indicator, and status-specific supplementary content:
  - **pending** / **duplicate**: no supplementary content.
  - **approved**: a link to the promoted venue, shown only when `promoted_venue` is set and `promoted_venue.is_published` is `True`.
  - **rejected**: the `rejection_reason` text, shown only when non-empty.

### Status indicators

Each status is visually distinct (badge or label):

| Status    | Visual treatment        |
|-----------|------------------------|
| pending   | Muted / neutral        |
| approved  | Positive / green-toned |
| rejected  | Alert / red-toned      |
| duplicate | Muted / neutral        |

---

## Out of Scope

- Public suggestion history visible to other users
- Paginating the suggestions list
- Editing or withdrawing a submitted suggestion
