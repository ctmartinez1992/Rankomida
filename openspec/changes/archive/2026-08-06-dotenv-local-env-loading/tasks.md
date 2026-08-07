## 1. Dependency

- [x] 1.1 Add `python-dotenv` to `requirements.txt`
- [x] 1.2 Install the dependency in the local virtualenv

## 2. Settings loading

- [x] 2.1 Import `load_dotenv` and call `load_dotenv(BASE_DIR / '.env')` in `config/settings.py` immediately after `BASE_DIR` is defined
- [x] 2.2 Remove the temporary `print(os.environ.get('DEBUG'))` from `config/settings.py`

## 3. Verification

- [x] 3.1 Confirm local settings pick up `.env` values (e.g. `DEBUG=true`) when those vars are unset in the shell
- [x] 3.2 Confirm process env still wins when a var is already set (Dokku / override=False behavior)
- [x] 3.3 Confirm `.env` remains listed in `.gitignore` and `.dockerignore`
