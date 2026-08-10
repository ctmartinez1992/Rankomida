## 1. Dependency and settings

- [x] 1.1 Add `django-recaptcha` to `requirements.txt` and install it in the local environment
- [x] 1.2 Add `django_recaptcha` to `INSTALLED_APPS` in `config/settings.py`
- [x] 1.3 Wire `RECAPTCHA_PUBLIC_KEY` and `RECAPTCHA_PRIVATE_KEY` from `os.environ` in settings (after dotenv load), documenting Google **v2** test keys for local/CI
- [x] 1.4 Add the key names to any project env documentation or example notes used by developers (without committing real secrets)

## 2. Auth forms — v2 checkbox

- [x] 2.1 Add `ReCaptchaField` with `ReCaptchaV2Checkbox` to `RegistrationForm` in `accounts/forms.py`
- [x] 2.2 Create a custom `AuthenticationForm` subclass with `ReCaptchaField` + `ReCaptchaV2Checkbox` and pass it to `LoginView` via `authentication_form` in `accounts/urls.py`
- [x] 2.3 Confirm register/login templates render the checkbox (via field loop) and include `{{ form.media }}` if required

## 3. Authenticated forms — invisible (no checkbox)

- [x] 3.1 Add `ReCaptchaField` with `ReCaptchaV2Invisible` to `RatingSubmissionForm` in `ratings/forms.py`
- [x] 3.2 Add `ReCaptchaField` with `ReCaptchaV2Invisible` to `ProfileVisibilityForm` (keep in views or move to `accounts/forms.py` if cleaner)
- [x] 3.3 Update rating and profile settings templates to render the invisible field and `{{ form.media }}`; ensure no visible checkbox appears
- [x] 3.4 Adjust `profile_settings.html` so the invisible captcha is not forced into the boolean checkbox row layout

## 4. Tests

- [x] 4.1 Update or add accounts tests so register/login POSTs include a valid captcha token under test keys, and assert invalid/missing captcha blocks account creation and login
- [x] 4.2 Update or add ratings tests so rating POST without valid captcha does not save; with valid captcha existing success behavior still holds
- [x] 4.3 Update profile settings tests (or add) for invisible captcha required on visibility save
- [x] 4.4 Run `python manage.py test` and fix failures

## 5. Verification

- [x] 5.1 Smoke-test register and login: checkbox visible; invalid captcha blocks; valid captcha succeeds
- [x] 5.2 Smoke-test rating and profile settings: no checkbox; submit still verifies; failure surfaces an error
- [x] 5.3 Confirm logout and venue GET filters still work without captcha
- [x] 5.4 Document Dokku/production step: set v2 `RECAPTCHA_PUBLIC_KEY` and `RECAPTCHA_PRIVATE_KEY` before deploy
