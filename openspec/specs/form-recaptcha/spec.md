## Purpose

Define Google reCAPTCHA on user-facing mutating forms: v2 checkbox on auth, v2 Invisible on authenticated forms, with server-side verification and env-based keys.

## Requirements

### Requirement: Auth forms require Google reCAPTCHA v2 checkbox
Account registration and login SHALL present Google reCAPTCHA v2 checkbox and SHALL verify the response server-side before creating an account or authenticating a session.

#### Scenario: Registration requires checkbox captcha
- **WHEN** a visitor submits the registration form without a valid reCAPTCHA response
- **THEN** the system SHALL NOT create a user account
- **AND** the form SHALL display a captcha validation error

#### Scenario: Login requires checkbox captcha
- **WHEN** a visitor submits the login form without a valid reCAPTCHA response
- **THEN** the system SHALL NOT authenticate the session
- **AND** the form SHALL display a captcha validation error

#### Scenario: Auth forms show a checkbox challenge
- **WHEN** a visitor opens the registration or login page
- **THEN** the page SHALL include a visible reCAPTCHA v2 checkbox widget

#### Scenario: Valid auth captcha allows success
- **WHEN** a visitor submits registration or login with a valid reCAPTCHA response and otherwise valid credentials/fields
- **THEN** the system SHALL proceed with the existing success behavior (create account or log in)

### Requirement: Authenticated mutating forms require invisible reCAPTCHA
Dish rating submission and profile visibility settings SHALL require Google reCAPTCHA without a checkbox (v2 Invisible) and SHALL verify the response server-side before saving. These forms MUST NOT present a persistent “I’m not a robot” checkbox.

#### Scenario: Rating requires invisible captcha
- **WHEN** an authenticated user submits the dish rating form without a valid reCAPTCHA response
- **THEN** the system SHALL NOT create or update a rating submission
- **AND** the form SHALL display a captcha validation error

#### Scenario: Profile settings require invisible captcha
- **WHEN** an authenticated user submits the profile settings form without a valid reCAPTCHA response
- **THEN** the system SHALL NOT update profile visibility
- **AND** the form SHALL display a captcha validation error

#### Scenario: Rating and settings have no checkbox widget
- **WHEN** an authenticated user opens the dish rating or profile settings page
- **THEN** the page SHALL NOT show a reCAPTCHA v2 checkbox
- **AND** the form SHALL still obtain and submit an invisible reCAPTCHA token on submit

#### Scenario: Valid invisible captcha allows success
- **WHEN** an authenticated user submits rating or profile settings with a valid reCAPTCHA response and otherwise valid field data
- **THEN** the system SHALL proceed with the existing success behavior (save rating or update settings)

### Requirement: Server-side verification is mandatory
The application MUST validate the reCAPTCHA token with Google’s verification API (or the equivalent provided by the Django reCAPTCHA integration) during form validation. Client-side widget presence alone is not sufficient.

#### Scenario: Forged or empty token is rejected
- **WHEN** a POST includes form fields but an empty, missing, or forged reCAPTCHA token
- **THEN** form validation SHALL fail
- **AND** no success side effect SHALL occur

### Requirement: reCAPTCHA keys are configured via environment
The application SHALL read reCAPTCHA public and private keys from the process environment (including values loaded from project-root `.env` for local development). Secrets MUST NOT be hardcoded in source.

#### Scenario: Production keys from environment
- **WHEN** `RECAPTCHA_PUBLIC_KEY` and `RECAPTCHA_PRIVATE_KEY` are set in the process environment
- **THEN** the reCAPTCHA widgets and server verification SHALL use those keys

#### Scenario: Local development with documented keys
- **WHEN** a developer configures reCAPTCHA keys in `.env` (including Google’s published test keys)
- **THEN** covered forms SHALL render and accept submissions according to those keys’ behavior without requiring committed secrets

### Requirement: Out-of-scope surfaces remain unchanged
Logout, GET-only filter/search forms, HTMX GET fragments, and Django admin SHALL NOT require reCAPTCHA as part of this capability.

#### Scenario: Venue filter GET does not require captcha
- **WHEN** a user submits the venue list filter/search as a GET request
- **THEN** the request SHALL succeed without a reCAPTCHA token

#### Scenario: Logout does not require captcha
- **WHEN** an authenticated user submits the logout POST form
- **THEN** the session SHALL end without reCAPTCHA verification
