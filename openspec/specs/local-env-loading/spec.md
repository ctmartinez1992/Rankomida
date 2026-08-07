## Purpose

Define local `.env` loading without changing production platform configuration precedence.

## Requirements

### Requirement: Optional project-root .env is loaded into process environment
On settings import, the application SHALL load environment variables from a `.env` file at the project root (`BASE_DIR / '.env'`) into the process environment when that file exists.

#### Scenario: Local .env present
- **WHEN** a `.env` file exists at the project root containing `DEBUG=true`
- **AND** `DEBUG` is not already set in the process environment
- **THEN** Django settings SHALL treat `DEBUG` as `True`

#### Scenario: .env file absent
- **WHEN** no `.env` file exists at the project root
- **THEN** settings import SHALL succeed without error
- **AND** configuration SHALL come only from the process environment and existing settings defaults

### Requirement: Platform environment variables are not overridden by .env
Values already present in the process environment SHALL take precedence over values in `.env`. Loading `.env` MUST NOT overwrite Dokku-, Docker-, or CI-injected variables.

#### Scenario: Dokku env var wins over .env
- **WHEN** the process environment has `DEBUG=false`
- **AND** `.env` contains `DEBUG=true`
- **THEN** Django settings SHALL treat `DEBUG` as `False`

#### Scenario: Production without .env uses Dokku config
- **WHEN** the application runs with `SECRET_KEY`, `DATABASE_URL`, and `ALLOWED_HOSTS` set in the process environment
- **AND** no `.env` file is present
- **THEN** the application SHALL start using those process environment values
