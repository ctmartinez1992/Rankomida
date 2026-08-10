## Context

Rankomida is a server-rendered Django 6 app. All user mutations go through HTML form POSTs with CSRF. There is no public JSON API and no existing bot protection (no rate limiting, honeypot, or captcha).

Protected surfaces:

| Form | Route | Auth | Captcha UX |
|------|-------|------|------------|
| Registration | `/accounts/register/` | Public | **v2 checkbox** |
| Login | `/accounts/login/` | Public | **v2 checkbox** |
| Dish rating | `/dishes/<slug>/rate/` | Login required | **Invisible** (no checkbox) |
| Profile settings | `/accounts/profile/me/settings/` | Login required | **Invisible** (no checkbox) |

Out of scope: logout POST, GET filters/search, HTMX GET fragments, Django admin.

Env loading already exists (`python-dotenv` + Dokku process env); new secrets should follow that pattern.

## Goals / Non-Goals

**Goals:**
- Require Google reCAPTCHA on every in-scope form, with **server-side** verification before any successful side effect (account create, session login, rating save, profile update)
- Put the explicit checkbox only on **auth** forms; keep rating and settings low-friction with invisible captcha
- Share one integration package and env key pair across both widget types
- Configure keys via environment variables for local `.env` and Dokku
- Fail closed: missing/invalid token → form error, no save/login

**Non-Goals:**
- reCAPTCHA Enterprise or custom risk dashboards
- reCAPTCHA v3 score thresholds (unless we later replace invisible v2)
- Rate limiting / IP throttling (complementary; separate change if needed)
- Captcha on admin, logout, or GET-only UI
- Client-only verification (widget without server check)
- Changing form field sets or rating business rules beyond adding captcha

## Decisions

### D1: Split UX — checkbox on auth, invisible elsewhere
- **Register + login:** Google reCAPTCHA **v2 checkbox** (`ReCaptchaV2Checkbox`)
- **Rating + profile settings:** Google reCAPTCHA **v2 Invisible** (`ReCaptchaV2Invisible`) — no checkbox; token obtained on submit

**Rationale:** Auth is high-abuse and infrequent, so an explicit challenge is acceptable. Rating/settings are repeated authenticated actions; invisible captcha preserves UX while still verifying server-side. Both are v2, so one site/secret key pair works.

**Alternatives considered:**
- Checkbox on all forms — rejected; too much friction on rating
- Auth-only captcha — rejected; user still wants captcha on other forms
- v3 on authenticated forms — possible later, but needs a second key pair and score tuning; invisible v2 keeps ops simple for now

### D2: Integrate via `django-recaptcha`
Add `django-recaptcha` to `requirements.txt`, enable its app in `INSTALLED_APPS`, and add a `ReCaptchaField` to each protected Django form with the widget appropriate to that form (checkbox vs invisible).

**Rationale:** Maintained Django integration; handles widget JS, token field, and server verify call to Google. Matches existing Form/`is_valid()` flow.

**Alternatives considered:**
- Hand-rolled `requests` to `siteverify` — more code, easy to get wrong
- Middleware that checks every POST — too blunt (would hit logout; harder error UX)

### D3: Keep captcha on authenticated mutating forms (invisible)
Rating and profile settings remain in scope, but use invisible captcha rather than a checkbox.

**Rationale:** User request: auth gets checkbox; other forms still get captcha without checkbox.

### D4: Keys from env; Google test keys for local/CI
Read `RECAPTCHA_PUBLIC_KEY` and `RECAPTCHA_PRIVATE_KEY` from the environment (names aligned with `django-recaptcha` settings). Document Google’s official v2 test keys for local/dev. Production/Dokku MUST set real **v2** keys (checkbox and invisible share the same key type).

**Rationale:** Fits `local-env-loading`; avoids committing secrets; one key pair for both widgets.

### D5: Login via custom `AuthenticationForm` subclass
Subclass Django’s `AuthenticationForm`, add `ReCaptchaField` with the checkbox widget, and point `LoginView` at it via `authentication_form=...`.

**Rationale:** Login is currently stock `LoginView`; captcha must live on the form for the same `is_valid()` path as other forms.

### D6: Templates render captcha fields; invisible needs `form.media`
Register/login continue to loop fields (checkbox appears as a normal field). Rating/settings must include the invisible field (and `{{ form.media }}` where required) so the script can bind to submit — even though there is no visible checkbox. Profile settings layout should not force the invisible field into the boolean checkbox row.

## Risks / Trade-offs

- [Risk] Google `siteverify` unavailable → users cannot submit forms → Mitigation: clear error message; monitor
- [Risk] Missing production keys → broken or always-failing forms → Mitigation: document Dokku `config:set`
- [Risk] Invisible captcha may still show an interstitial challenge for suspicious traffic → Mitigation: acceptable; better than a permanent checkbox on every rating
- [Risk] Automated tests need captcha bypass or test keys → Mitigation: use Google test keys in test settings
- [Trade-off] Two widgets to maintain → Small; same field type and key pair

## Migration Plan

1. Add dependency + settings + env var documentation
2. Wire checkbox captcha into register/login; invisible captcha into rating/settings; confirm templates/`form.media`
3. Set Dokku v2 keys; deploy
4. Smoke-test all four forms (checkbox visible on auth; no checkbox on rating/settings)
5. Rollback: remove fields / uninstall app; keys can remain unused

## Open Questions

None blocking. Optional follow-up: replace invisible v2 with v3 on authenticated forms if we want score-based tuning later.
