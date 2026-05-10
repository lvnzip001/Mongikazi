# MongiKazi Accounts App — Codex Implementation Prompt

## Context

You are improving the existing `accounts` Django app for the MongiKazi platform. MongiKazi is a mobile-first, trust-driven marketplace connecting employers with verified domestic workers/helpers. The public website already exists, and the `accounts` app is the next foundation layer for role-based access into the future Employer Portal, Helper Portal, and Operations Portal.

The current `accounts` app already includes:

```text
accounts/
├── admin.py
├── apps.py
├── forms.py
├── models.py
├── tests.py
├── urls.py
├── views.py
├── migrations/0001_initial.py
├── selectors/__init__.py
├── services/
│   ├── redirect_service.py
│   └── registration_service.py
├── static/website/css/app.css
├── static/website/js/theme.js
└── templates/
    ├── accounts/
    │   ├── account_pending.html
    │   ├── login.html
    │   ├── register.html
    │   └── role_select.html
    └── base/base_auth.html
```

Keep this app-self-contained structure going forward. Do **not** move templates/static back to project-level folders.

## Critical UI Direction

The UI must feel:

```text
Elegant
Fintech-grade
Airbnb-like product quality
Mobile-first
Trust-first
Clean and premium
```

Rules:

1. Keep Tailwind via CDN only for now.
2. Do not introduce a Tailwind build process, `package.json`, `tailwind.config.js`, or `input.css`.
3. Keep custom styling in `accounts/static/website/css/app.css`.
4. Keep JS small and focused in `accounts/static/website/js/theme.js` or clearly named small JS files.
5. Font weight must not exceed `800`. Replace any `font-extrabold` Tailwind class with `font-bold` or a custom class capped at 800.
6. Do not make the UI look like generic Bootstrap/Django admin.
7. Remove all `__pycache__` files/folders from generated output.

## Current Error / Important Model Note

The previous system check error was:

```text
accounts.User.groups reverse accessor Group.user_set clashes with auth.User.groups
accounts.User.user_permissions reverse accessor Permission.user_set clashes with auth.User.user_permissions
```

The current model has attempted to fix this by explicitly defining `groups` and `user_permissions` with custom `related_name` values.

Review and preserve this fix unless the project is confirmed to use `AUTH_USER_MODEL = "accounts.User"` before first migration. The safest implementation for this codebase is to keep the explicit related names because it avoids clashes while the project is being assembled.

Also ensure installation notes clearly state:

```python
AUTH_USER_MODEL = "accounts.User"
```

This must be configured before running migrations in a fresh database.

## Current Gaps to Fix

### 1. App installation documentation is missing or insufficient

Create or update:

```text
accounts/ACCOUNTS_APP_INSTALL_NOTES.md
```

It must include:

- Add `accounts` to `INSTALLED_APPS` before apps that reference the user model.
- Add `AUTH_USER_MODEL = "accounts.User"` before first migration.
- Add `path("accounts/", include("accounts.urls"))` to root `urls.py`.
- Confirm `APP_DIRS=True` in `TEMPLATES`.
- Confirm `django.contrib.staticfiles` is enabled.
- Confirm the website app has URL namespace `website` if templates use `{% url 'website:home' %}`.
- Migration reset warning for early development if `auth.User` tables already exist.
- Test commands.

### 2. Template references are too dependent on `website:home`

Several templates and views use:

```django
{% url 'website:home' %}
```

and:

```python
reverse("website:home")
```

This can break if the accounts app is tested before the website app is wired.

Implement a safer approach:

- Add a helper in `services/redirect_service.py`, for example `get_public_home_url()`.
- It should use a setting fallback:

```python
MONGIKAZI_PUBLIC_HOME_URL = "/"
```

- Views should redirect to this safe URL instead of hard-failing on `website:home`.
- Templates should receive `public_home_url` through context, or use a small context processor if already present. Keep it simple: pass it from account views where needed.
- `base_auth.html` must not hard-fail if `website:home` is not available.

### 3. Logout should not allow GET mutation

Current `logout_view` accepts both GET and POST. Improve this.

Required:

- Make logout POST-only.
- Add a simple `logout_confirm.html` only if needed, otherwise use POST forms from templates.
- For now, support a safe redirect page or keep URL available but do not mutate session on GET.
- Update tests accordingly.

Preferred:

```python
@require_POST
def logout_view(request):
    logout(request)
    return redirect(get_public_home_url())
```

### 4. Missing `next` parameter handling

Login should support a safe `next` parameter.

Required:

- If a user is redirected to login from a protected page, successful login should send them back to the safe `next` URL.
- Use Django’s safety utilities, for example `url_has_allowed_host_and_scheme`.
- Do not redirect to external URLs.
- If `next` is absent or unsafe, use role-based redirect.

### 5. Registration should timestamp terms acceptance reliably

The model has:

```python
accepted_terms
accepted_terms_at
```

Ensure `accepted_terms_at` is set exactly once on registration when terms are accepted.

Also consider adding:

```python
terms_version = models.CharField(max_length=20, blank=True, default="v1")
```

Only add this field if you also create and update the migration cleanly. If you decide not to add it now, mention it as a later enhancement in install notes.

### 6. Admin registration needs improvement

Enhance `accounts/admin.py`.

Required:

- Register the custom `User` model properly.
- Use a custom `UserAdmin`.
- Display useful fields:
  - username
  - email
  - phone_number
  - role
  - is_phone_verified
  - is_onboarding_complete
  - accepted_terms
  - is_staff
  - is_active
- Add filters:
  - role
  - is_phone_verified
  - is_onboarding_complete
  - accepted_terms
  - is_staff
  - is_active
- Add search:
  - username
  - email
  - phone_number
  - first_name
  - last_name
- Add fieldsets for MongiKazi-specific fields.

### 7. Registration form needs stronger validation

Improve `RegisterForm`.

Required:

- Normalize email to lowercase.
- Normalize phone number.
- Prevent duplicate email case-insensitively.
- Prevent duplicate phone numbers.
- Ensure role is one of `EMPLOYER` or `HELPER` only.
- Add clean error messages.

Preferred phone behaviour for MVP:

- Accept South African style numbers without being too strict.
- Remove spaces and hyphens.
- Keep `+` if supplied.
- Do not over-engineer with external libraries yet.

### 8. Login form should remain email/phone/username capable

Preserve login using:

- email
- phone number
- username

But make it robust and tested.

### 9. Missing password reset placeholder route

Add password reset placeholder support without building full email flow yet.

Required:

- Add URL: `/accounts/password-reset/`
- Add view: `password_reset_placeholder`
- Add template: `password_reset.html`
- The page should explain that password reset will be activated soon and offer contact/support wording.
- Update login template link from “Password reset coming soon” to actual page link.

Do not implement email sending yet unless the existing project already has an email service.

### 10. Account pending page should be clearer and portal-ready

Improve `account_pending.html`.

Required:

- Show different copy for employer/helper/operations.
- Show the prepared next endpoint.
- Explain that this will route into onboarding once the next app exists.
- Include two actions:
  - Continue setup
  - Back to website/public home

Use `public_home_url` instead of hardcoded `website:home`.

### 11. Tests need to be expanded

Add meaningful tests in `accounts/tests.py`.

Required tests:

1. Custom user role helper properties.
2. Permission related names do not clash.
3. Employer registration creates user with role `EMPLOYER`.
4. Helper registration creates user with role `HELPER`.
5. Duplicate email validation is case-insensitive.
6. Duplicate phone number validation works after normalization.
7. Login works with email.
8. Login works with phone number.
9. Incomplete employer redirects to account pending.
10. Completed employer redirects to employer portal URL setting.
11. Completed helper redirects to helper portal URL setting.
12. Staff/superuser redirects to operations URL setting.
13. Unsafe `next` URL is ignored.
14. Safe `next` URL is honoured.
15. Logout requires POST.
16. Password reset placeholder renders successfully.

Do not over-test CSS.

### 12. URL names must remain stable

Preserve these names:

```text
accounts:role_select
accounts:register
accounts:login
accounts:logout
accounts:account_pending
```

Add:

```text
accounts:password_reset
```

Do not rename existing URLs unless there is a compatibility wrapper.

### 13. Base/auth templates need slight cleanup

Current templates use `font-extrabold`. Replace with `font-bold` to respect the project rule that font weight must not exceed 800.

Ensure all auth templates remain elegant and mobile-first.

### 14. Dark mode should stay stable

The current `theme.js` is acceptable, but improve it if needed:

- Avoid flash where practical.
- Persist `mk-theme` in localStorage.
- Toggle the `dark` class on `<html>`.
- Keep the code small.

### 15. Avoid unnecessary dependencies

Do not add:

- Bootstrap
- jQuery
- npm tooling
- Tailwind build process
- DRF
- Celery
- external phone validation libraries

This is still the accounts/auth foundation.

## Expected Final App Structure

The final app must follow this shape:

```text
accounts/
├── __init__.py
├── admin.py
├── apps.py
├── forms.py
├── models.py
├── tests.py
├── urls.py
├── views.py
├── ACCOUNTS_APP_INSTALL_NOTES.md
│
├── migrations/
│   ├── 0001_initial.py
│   └── __init__.py
│
├── selectors/
│   └── __init__.py
│
├── services/
│   ├── __init__.py
│   ├── redirect_service.py
│   └── registration_service.py
│
├── static/
│   └── website/
│       ├── css/
│       │   └── app.css
│       └── js/
│           └── theme.js
│
└── templates/
    ├── accounts/
    │   ├── account_pending.html
    │   ├── login.html
    │   ├── logout_confirm.html        # only if needed
    │   ├── password_reset.html
    │   ├── register.html
    │   └── role_select.html
    │
    └── base/
        └── base_auth.html
```

## Implementation Guardrails

1. Do not move templates/static outside the `accounts` app.
2. Do not create unnecessary nested template folders.
3. Do not break existing URL names.
4. Do not introduce heavy dependencies.
5. Do not add portal business logic yet.
6. Do not build employer/helper/operations portals in this step.
7. Keep role routing prepared through settings-based URLs.
8. Keep views thin; put redirect/registration logic in services.
9. Keep the UI elegant and restrained.
10. Keep font weights at or below 800.
11. Remove `__pycache__` from the final output.

## Recommended Settings Defaults

Where useful, support these optional settings:

```python
MONGIKAZI_PUBLIC_HOME_URL = "/"
MONGIKAZI_EMPLOYER_PORTAL_URL = "/employer/"
MONGIKAZI_HELPER_PORTAL_URL = "/helper/"
MONGIKAZI_OPERATIONS_PORTAL_URL = "/operations/"
MONGIKAZI_EMPLOYER_ONBOARDING_URL = "/employer/onboarding/"
MONGIKAZI_HELPER_ONBOARDING_URL = "/helper/onboarding/"
```

Do not require these settings to exist. Use defaults in the service layer.

## Acceptance Criteria

The implementation is complete when:

1. `python manage.py check` passes.
2. `python manage.py makemigrations --check --dry-run` is clean after migrations are committed.
3. `python manage.py test accounts` passes.
4. Existing auth pages render without a `website` namespace dependency error.
5. Employer and helper registration work.
6. Login works with email and phone number.
7. Role-based redirects work.
8. Logout is POST-only.
9. Password reset placeholder page exists.
10. UI still feels premium, mobile-first, and consistent with MongiKazi.

## What Remains After This Accounts App

After this accounts app is stable, the next logical apps are:

### 1. Helper Profiles App

Purpose:

- Helper digital CV
- Skills and service categories
- Profile photo
- Experience
- Verification readiness
- Availability placeholder

### 2. Employer Profiles App

Purpose:

- Employer contact profile
- Locations/addresses
- Basic preferences
- Prepared company/business support later

### 3. Onboarding App

Purpose:

- Role-specific onboarding steps
- Profile completion status
- Employer needs capture
- Helper setup progress

### 4. Bookings App

Purpose:

- Booking request lifecycle
- Accept/decline
- Booking statuses
- Booking audit trail

### 5. Marketplace/Search App

Purpose:

- Search helper cards
- Rule-based matching
- Location/category/availability/rating filters

### 6. Reviews App

Purpose:

- Employer rates helper
- Helper rates employer
- Reputation signals

### 7. Verification App

Purpose:

- ID document upload
- Criminal record check upload
- Admin verification queue

### 8. Operations Portal

Purpose:

- Admin dashboard
- Verification review
- Booking oversight
- Payment proof review later

### 9. Payments App

Purpose:

- Invoice records
- POP uploads
- Commission calculations
- Helper payout tracking

## Final Instruction

Implement this as a careful enhancement of the existing `accounts` app, not a rewrite from scratch. Preserve working behaviour, fix the gaps, expand test coverage, and keep the app ready for the next MongiKazi portals.
