# ACCOUNTS App Install Notes

These notes ensure the custom `accounts.User` model is installed safely in MongiKazi.

## 1. Install Order

1. Add `accounts` to `INSTALLED_APPS` before apps that import or reference the user model.
2. Keep `django.contrib.staticfiles` enabled.
3. Keep `TEMPLATES` configured with `APP_DIRS = True`.

## 2. Required Settings

Set this before running first migration in a fresh database:

```python
AUTH_USER_MODEL = "accounts.User"
```

Optional URL defaults used by accounts services:

```python
MONGIKAZI_PUBLIC_HOME_URL = "/"
MONGIKAZI_EMPLOYER_PORTAL_URL = "/employer/"
MONGIKAZI_HELPER_PORTAL_URL = "/helper/"
MONGIKAZI_OPERATIONS_PORTAL_URL = "/operations/"
MONGIKAZI_EMPLOYER_ONBOARDING_URL = "/employer/onboarding/"
MONGIKAZI_HELPER_ONBOARDING_URL = "/helper/onboarding/"
```

## 3. URL Wiring

In root `urls.py`, include accounts:

```python
from django.urls import include, path

urlpatterns = [
    path("accounts/", include("accounts.urls")),
]
```

If templates or code still reference `website:home`, ensure the `website` app is included with namespace `website`.

## 4. Clash Risk Guidance (`auth.User` vs `accounts.User`)

If migrations were previously run without `AUTH_USER_MODEL = "accounts.User"`, you may have `auth_user` data and relation mismatches.

In early development only, safest recovery is usually:

1. Backup data if needed.
2. Reset local database/migrations as appropriate.
3. Ensure `AUTH_USER_MODEL` is set.
4. Re-run migrations from a clean state.

The custom `User` model also keeps explicit related names for `groups` and `user_permissions` to prevent reverse accessor clashes during assembly.

## 5. Validation and Security Notes

1. Logout is POST-only at `accounts:logout`.
2. Login supports email, phone number, and username.
3. Login `next` redirects are validated with Django safe URL checks.
4. `accepted_terms_at` is timestamped once during registration.

## 6. Test Commands

```bash
python manage.py check
python manage.py makemigrations --check --dry-run
python manage.py test accounts
```

## 7. Deferred Enhancement

`terms_version` is not yet added to the model/migrations. Add it in a dedicated migration once legal versioning is ready.
