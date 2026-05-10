# MongiKazi Helpers App — Codex Implementation Prompt

## 1. Role and Operating Instruction

You are acting as the implementation engineer for the MongiKazi Django platform.

Treat this task as a senior-guided implementation. You have full project access, so inspect the existing project structure, settings, URLs, installed apps, templates, static files, migrations, and app conventions before making changes.

Do not stop at the first error. Diagnose issues independently and make the smallest safe correction that aligns with the MongiKazi business model, Django architecture principles, and UI direction.

When complete, report back clearly using the required Completion Report format at the end of this prompt.

---

## 2. Business Context

MongiKazi is a mobile-first, trust-driven marketplace connecting employers with verified domestic workers, cleaners, and helpers.

The product direction is:

- Airbnb-style profile trust and browsing
- Uber-style guided booking simplicity
- Fintech-grade visual quality and status clarity
- Mobile-first experience for the South African market
- Trust-first marketplace infrastructure, not just a basic directory

The platform has already completed:

1. `accounts` app
   - Custom user model
   - Role selection
   - Register/login/logout
   - Role-based redirects
   - Password reset placeholder
   - Auth UI foundation

2. `onboarding` app
   - Employer onboarding
   - Helper onboarding
   - Role-guarded setup flows
   - App-contained templates/static
   - Onboarding completion logic

The next app is:

```text
helpers
```

The purpose of the `helpers` app is to turn helper onboarding data into the first real marketplace supply-side domain model.

---

## 3. Current Build Sequence

We are following this roadmap:

```text
accounts ✅
onboarding ✅
helpers ⏭
employers
employer_portal
helper_portal
bookings
verification
reviews
payments
operations
```

Do not jump ahead into employer portal, helper portal, bookings, payments, or full verification workflows yet.

---

## 4. Helpers App Purpose

The `helpers` app owns the helper-side marketplace domain.

It should manage:

- Helper profile
- Helper service categories
- Helper skills
- Helper availability foundation
- Helper trust status foundation
- Public/helper profile readiness
- Conversion from onboarding data into a helper profile
- Profile completeness calculation
- Helper profile preview page

This app should create the foundation that later supports:

- Employer search
- Helper profile views
- Booking requests
- Verification centre
- Ratings/reviews
- Trust score
- Helper dashboard
- Worker digital CV

---

## 5. Important Architecture Rule

The `helpers` app is a domain app, not a portal app.

It should contain helper business/domain models and profile logic.

It should not become the full user-facing `helper_portal`.

Correct separation:

```text
helpers/
    Domain models, services, selectors, profile logic

helper_portal/
    Future user-facing dashboard, job requests, earnings, messages
```

For now, the `helpers` app may include basic internal/profile pages only where useful to validate and preview the helper profile, but avoid building the full portal.

---

## 6. App Structure Required

Create a self-contained Django app:

```text
helpers/
├── __init__.py
├── admin.py
├── apps.py
├── forms.py
├── models.py
├── tests.py
├── urls.py
├── views.py
│
├── migrations/
│   └── __init__.py
│
├── services/
│   ├── __init__.py
│   ├── helper_profile_service.py
│   ├── profile_completion_service.py
│   └── onboarding_handoff_service.py
│
├── selectors/
│   ├── __init__.py
│   └── helper_selectors.py
│
├── templates/
│   ├── base/
│   │   └── base_helpers.html
│   └── helpers/
│       ├── profile_detail.html
│       ├── profile_edit.html
│       ├── profile_preview.html
│       ├── availability.html
│       ├── skills.html
│       └── profile_incomplete.html
│
└── static/
    └── helpers/
        ├── css/
        │   └── helpers.css
        └── js/
            └── helpers.js
```

Do not place helper templates or static files outside the `helpers` app.

Remove any `__pycache__` folders before final reporting.

---

## 7. Models to Implement

Use `settings.AUTH_USER_MODEL` for user links.

Do not import the custom User model directly.

### 7.1 HelperProfile

Create a `HelperProfile` model.

Suggested fields:

```text
user
display_name
profile_photo
location
preferred_work_area
bio
years_experience
availability_summary
is_active
is_profile_complete
is_verified
trust_status
profile_completion_percent
average_rating
completed_jobs
created_at
updated_at
```

Guidance:

- `user` should be a `OneToOneField` to `settings.AUTH_USER_MODEL`.
- `display_name` should default from onboarding data or user first/last name where possible.
- `is_verified` should default to `False`.
- `average_rating` should default to `0`.
- `completed_jobs` should default to `0`.
- `trust_status` should be a controlled choice, e.g.:
  - `NEW`
  - `PROFILE_STARTED`
  - `READY_FOR_REVIEW`
  - `VERIFIED`
  - `SUSPENDED`

Do not implement the full verification app here. Only provide status foundations.

### 7.2 ServiceCategory

Create service categories used by helpers.

Suggested fields:

```text
name
slug
description
is_active
sort_order
created_at
updated_at
```

Seed/default categories should be available through a service function or migration-safe mechanism:

- Cleaning
- Laundry
- Cooking
- Childcare
- Office cleaning

Avoid hardcoding categories in templates.

### 7.3 HelperSkill

Create a model linking helpers to categories.

Suggested fields:

```text
helper
category
years_experience
skill_note
is_primary
created_at
updated_at
```

### 7.4 HelperAvailability

Create a simple availability foundation.

Suggested fields:

```text
helper
day_of_week
start_time
end_time
is_available
created_at
updated_at
```

Day choices:

- Monday
- Tuesday
- Wednesday
- Thursday
- Friday
- Saturday
- Sunday

This does not need to become a full calendar engine yet. It only needs to support early profile completeness and future booking logic.

### 7.5 HelperTrustSignal

Create a lightweight trust-signal foundation.

Suggested fields:

```text
helper
signal_type
status
notes
created_at
updated_at
```

Signal types:

- ID document
- Criminal record check
- References
- Experience captured
- Profile photo

Statuses:

- Not provided
- Ready
- Pending review
- Approved
- Rejected

Do not implement document upload yet unless very simple and local-file-safe. Full document verification belongs to the future `verification` app.

---

## 8. Onboarding Handoff Requirement

This is important.

When a helper completes onboarding, the `helpers` app should be able to create or update a `HelperProfile` using data from `onboarding.HelperOnboardingProfile`.

Implement a service:

```text
helpers/services/onboarding_handoff_service.py
```

Suggested functions:

```python
create_or_update_helper_profile_from_onboarding(user)
sync_helper_skills_from_onboarding(user)
sync_helper_trust_signals_from_onboarding(user)
ensure_default_service_categories()
```

The handoff should:

1. Read the helper onboarding profile.
2. Create or update `HelperProfile`.
3. Copy:
   - display_name
   - location
   - years_experience
   - bio
   - preferred_work_area
   - availability_summary
4. Convert selected categories into `HelperSkill` records.
5. Create initial `HelperTrustSignal` records based on onboarding readiness answers.
6. Calculate profile completeness.

Important:

- The service must be idempotent.
- Running it more than once must not create duplicate skills or duplicate trust signals.
- It should be safe if onboarding data is incomplete.
- It should not crash if the onboarding app is missing data; instead, return a clear result or raise a controlled validation error.

---

## 9. Profile Completion Logic

Implement a service:

```text
helpers/services/profile_completion_service.py
```

Suggested function:

```python
calculate_helper_profile_completion(helper_profile)
```

Suggested scoring:

```text
Basic profile fields complete: 30%
At least one service category/skill: 20%
Availability summary or availability rows: 15%
Trust readiness signals captured: 20%
Profile photo uploaded: 15%
```

Total should cap at 100%.

Update:

```text
helper.profile_completion_percent
helper.is_profile_complete
helper.trust_status
```

Suggested rule:

```text
is_profile_complete = profile_completion_percent >= 70
trust_status = READY_FOR_REVIEW if profile is sufficiently complete but not verified
```

Do not overcomplicate this. Keep it transparent and testable.

---

## 10. Forms

Create forms for:

1. `HelperProfileForm`
2. `HelperSkillForm`
3. `HelperAvailabilityForm`
4. Optional formset for availability rows if practical

Form UX should support app-contained templates later.

Validation:

- Only helper users may edit helper profiles.
- Required fields should be clear.
- Years of experience cannot be negative.
- Availability end time must be after start time.

---

## 11. Views

Keep views thin.

Use services/selectors.

Required views:

### 11.1 Profile Detail

```text
/helpers/profile/
name: helpers:profile_detail
```

Shows the logged-in helper’s profile.

If no profile exists:
- attempt to create it from onboarding data
- otherwise show profile incomplete page

### 11.2 Profile Edit

```text
/helpers/profile/edit/
name: helpers:profile_edit
```

Allows editing of basic profile fields.

### 11.3 Skills

```text
/helpers/profile/skills/
name: helpers:skills
```

Allows selecting/editing categories and skills.

### 11.4 Availability

```text
/helpers/profile/availability/
name: helpers:availability
```

Allows capturing basic weekly availability.

### 11.5 Profile Preview

```text
/helpers/profile/preview/
name: helpers:profile_preview
```

Shows how employers will eventually see the helper.

This preview is important because MongiKazi wants the helper profile to feel like a trusted digital CV.

### 11.6 Profile Incomplete

```text
/helpers/profile/incomplete/
name: helpers:profile_incomplete
```

Explains what is missing and links back to onboarding/profile editing.

---

## 12. URL Requirements

Create `helpers/urls.py`.

Expected namespace:

```python
app_name = "helpers"
```

Expected routes:

```text
/helpers/profile/
/helpers/profile/edit/
/helpers/profile/skills/
/helpers/profile/availability/
/helpers/profile/preview/
/helpers/profile/incomplete/
```

Update root `mysite/urls.py`:

```python
path("helpers/", include("helpers.urls")),
```

---

## 13. Permissions and Access Control

All helper profile views must require login.

Only users with role `HELPER` should access helper profile views.

If an employer attempts to access helper pages:
- redirect safely to account pending page or onboarding start
- do not expose helper edit pages

If a helper has not completed onboarding:
- redirect to `onboarding:start`
- or show profile incomplete page where appropriate

Be consistent with the existing accounts/onboarding redirect pattern.

---

## 14. Selectors

Create:

```text
helpers/selectors/helper_selectors.py
```

Suggested functions:

```python
get_helper_profile_for_user(user)
get_active_helper_profiles()
get_helper_skills(helper_profile)
get_helper_availability(helper_profile)
get_helper_trust_signals(helper_profile)
get_helper_profile_preview_context(helper_profile)
```

These will later support employer search and helper portal.

---

## 15. Admin

Register all helper models in `helpers/admin.py`.

Admin should support:

- search by display name, user email/phone, location
- filters for is_active, is_verified, trust_status
- inline or separate admin for skills, availability, trust signals
- read-only created/updated timestamps

Do not overbuild admin, but make it useful for operational review.

---

## 16. UI/UX Requirements

The helper profile UI must feel:

```text
Elegant
Clean
Fintech-grade
Airbnb-like
Mobile-first
Human and trust-focused
```

Use:

- Tailwind CDN in `base_helpers.html`
- App-contained CSS in `helpers/static/helpers/css/helpers.css`
- App-contained JS in `helpers/static/helpers/js/helpers.js`
- Font weight max 800
- Calm teal/dark teal/off-white palette
- Soft card UI
- Clear profile progress
- Trust badges
- Large mobile-friendly buttons and inputs
- Clean desktop width usage

Do not use Bootstrap unless already required elsewhere.

### Visual Pages

#### Profile Detail

Should show:

- display name
- location
- years experience
- profile completeness
- trust status
- selected services
- availability summary
- trust readiness
- CTA buttons:
  - Edit Profile
  - Manage Skills
  - Manage Availability
  - Preview Profile

#### Profile Preview

Should feel like an employer-facing digital CV:

```text
[Profile photo placeholder]
Nomsa M.
4.8 rating placeholder · 0 completed jobs

Verified status / Trust status
Location
Experience
Services
About
Availability
Trust readiness

[Future CTA placeholder: Book Helper]
```

The CTA should be visibly disabled or marked as future functionality.

#### Profile Incomplete

Should clearly guide the helper:

```text
Your profile is almost ready

Complete:
- Basic profile
- Services
- Availability
- Trust readiness

[Continue setup]
```

---

## 17. Static/Template Guardrails

Because previous work had duplicate template/static namespace issues, be careful.

Rules:

1. All helper templates must live under:
   ```text
   helpers/templates/
   ```

2. All helper static files must live under:
   ```text
   helpers/static/helpers/
   ```

3. Do not create helper templates under project-level templates.

4. Do not create helper static files under website/static.

5. Use unique static namespace:
   ```django
   {% static 'helpers/css/helpers.css' %}
   {% static 'helpers/js/helpers.js' %}
   ```

6. Do not reuse the generic `website/css/app.css` path for helpers.

7. `base_helpers.html` may load Tailwind CDN directly for now.

---

## 18. Settings

Update `INSTALLED_APPS`:

```text
accounts
onboarding
helpers
website
...
```

Place `helpers` after `onboarding`.

Confirm template/static resolution with:

```text
findstatic helpers/css/helpers.css
findstatic helpers/js/helpers.js
```

---

## 19. Tests Required

Add tests for:

1. helper user can access helper profile page
2. employer user cannot access helper profile page
3. anonymous user redirects to login
4. helper profile can be created from onboarding data
5. handoff service is idempotent
6. selected onboarding categories create helper skills
7. profile completion calculation works
8. trust signals created from onboarding readiness fields
9. availability validation prevents end time before start time
10. helper profile preview loads
11. `findstatic` resolves helper CSS/JS to helpers app paths if practical
12. app routes resolve correctly

Run:

```powershell
.\.env\Scripts\python.exe manage.py check
.\.env\Scripts\python.exe manage.py makemigrations --check --dry-run
.\.env\Scripts\python.exe manage.py makemigrations helpers
.\.env\Scripts\python.exe manage.py migrate
.\.env\Scripts\python.exe manage.py test accounts onboarding helpers
```

If migrations are created, explain them clearly.

---

## 20. Manual Smoke Tests Required

Manually verify:

```text
GET /helpers/profile/
GET /helpers/profile/edit/
GET /helpers/profile/skills/
GET /helpers/profile/availability/
GET /helpers/profile/preview/
GET /helpers/profile/incomplete/
```

Test as:

1. anonymous user
2. employer user
3. helper user with onboarding complete
4. helper user with onboarding incomplete

Report the route behavior.

---

## 21. Do Not Do These Things

Do not:

- build employer search yet
- build bookings yet
- build helper dashboard yet
- build earnings yet
- build full verification document upload yet
- build reviews yet
- build messaging yet
- introduce external packages
- move accounts or onboarding templates/static
- create project-level helper templates/static
- use font weight above 800
- perform broad unrelated refactors
- rename existing routes unless necessary
- break existing accounts/onboarding tests

---

## 22. Completion Report Required

When finished, report back using this exact format:

```markdown
## Completion Report

### Summary
Briefly explain what was implemented.

### Files Changed
List every file created or modified.

### Models and Migrations
Explain each model added and each migration created/applied.

### Services and Selectors
Explain the helper services/selectors added and what they do.

### URL Routes Added
List helper routes and route names.

### Onboarding Integration
Explain how helper onboarding data is converted into helper profile data.

### UI/UX Notes
Explain how the helper UI follows MongiKazi styling principles.

### Tests Run
List every command run and result.

### Manual Smoke Test Results
List each tested route and behavior for anonymous, employer, helper incomplete, and helper complete users.

### Issues Found
Flag any risks, assumptions, duplicate template/static conflicts, migration concerns, or settings issues.

### Outstanding Items
List what still needs to be done after helpers.

### Recommendation
Confirm whether the helpers app is ready for senior review and whether the next app should be employers.
```

---

## 23. Expected Senior Review Focus

After you report back, the senior review will focus on:

- Whether domain boundaries are clean
- Whether helpers does not accidentally become helper_portal
- Whether onboarding handoff is idempotent
- Whether templates/static are self-contained
- Whether UI meets MongiKazi quality standards
- Whether tests prove the key business flows
- Whether migrations are safe and explainable

---

## 24. Final Instruction

Proceed with the `helpers` app implementation now.

Be practical, careful, and product-aware. Build the smallest complete helper domain foundation that supports the next marketplace phase without overbuilding future portal, booking, payment, or verification functionality.
