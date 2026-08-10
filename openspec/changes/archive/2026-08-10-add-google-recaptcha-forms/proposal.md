## Why

Public and authenticated POST forms (register, login, rating, profile settings) currently rely only on Django CSRF. That stops cross-site forgery but does not stop bots from creating accounts, stuffing credentials, or spamming ratings and comments. Adding Google reCAPTCHA on every state-changing user form reduces automated abuse before it hits the database.

## What Changes

- Add Google reCAPTCHA verification to all user-facing state-changing POST forms: registration, login, dish rating, and profile visibility settings
- Use **v2 checkbox** captcha on auth forms only (register, login)
- Use **invisible** (no-checkbox) captcha on other mutating forms (dish rating, profile settings)
- Load reCAPTCHA site/secret keys from environment variables (compatible with existing `.env` / Dokku config)
- Reject submissions that fail server-side reCAPTCHA verification and surface a clear form error
- Document local/test key usage so development can run without production Google keys
- Leave logout, GET filter/search forms, HTMX GET fragments, and Django admin out of scope

## Capabilities

### New Capabilities
- `form-recaptcha`: Google reCAPTCHA on all user-facing mutating forms — checkbox on auth, invisible on authenticated forms — with server-side verification and env-based configuration

### Modified Capabilities
- (none)

## Impact

- Dependencies: add a Django reCAPTCHA integration package (e.g. `django-recaptcha`)
- Settings: `RECAPTCHA_PUBLIC_KEY` / `RECAPTCHA_PRIVATE_KEY` (or package-equivalent names) via env
- Forms / templates: `RegistrationForm`, login (`AuthenticationForm` / `LoginView`), `RatingSubmissionForm`, `ProfileVisibilityForm`, and their templates
- Deploy: Dokku (or equivalent) must set reCAPTCHA keys; local `.env` for developers
- UX: register/login show an explicit checkbox; rating and profile settings verify invisibly on submit; failed verification blocks save/login
