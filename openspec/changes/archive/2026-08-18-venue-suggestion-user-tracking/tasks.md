## 1. Model & Migration

- [x] 1.1 Add `submitted_by = ForeignKey(settings.AUTH_USER_MODEL, on_delete=SET_NULL, null=True, blank=True, related_name="venue_suggestions")` to `VenueSuggestion` in `catalog/models.py`
- [x] 1.2 Run `makemigrations catalog` and verify migration file

## 2. Form

- [x] 2.1 Update `VenueSuggestionForm.__init__` to accept an `authenticated` kwarg (default `False`); when `True`, pop `submitter_name` and `submitter_email` from `self.fields`

## 3. View

- [x] 3.1 Update `VenueSuggestionCreateView` to pass `authenticated=request.user.is_authenticated` to the form; on valid POST, set `suggestion.submitted_by = request.user` when authenticated before saving; pass `authenticated` flag to template context

## 4. Templates

- [x] 4.1 Update `templates/catalog/suggest_venue.html` — show "Submitting as \<username\>" hint when `authenticated` is true (the submitter fields are already absent from the form)
- [x] 4.2 Update `templates/catalog/suggest_venue_success.html` — when `{% if user.is_authenticated %}`, show profile link: "You can track the status of your suggestion on your profile."
- [x] 4.3 Update `templates/accounts/profile.html` — add "Venue Suggestions" section inside the `{% if request.user == profile_user %}` guard; show each suggestion (name, city, status badge, rejection reason if rejected, venue link if approved and published); skip section if no suggestions

## 5. Admin

- [x] 5.1 Add `submitted_by` to `VenueSuggestionAdmin.list_display`, `readonly_fields`, and the "Submitter" fieldset in `catalog/admin.py`

## 6. Tests

- [x] 6.1 Test authenticated submission: `submitted_by` set correctly, form has no submitter fields
- [x] 6.2 Test anonymous submission: `submitted_by` is null, submitter fields present, behaviour unchanged
- [x] 6.3 Test profile section shows suggestions for owner, hidden from other viewers
- [x] 6.4 Test approved suggestion shows venue link when `promoted_venue.is_published=True`; link hidden when unpublished
- [x] 6.5 Test rejected suggestion shows `rejection_reason` in profile section
