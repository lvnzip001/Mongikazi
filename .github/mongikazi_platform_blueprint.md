# MongiKazi Platform Blueprint

## 1. Platform Positioning

**MongiKazi** is a two-sided marketplace connecting:

| Side | User Type | Core Goal |
|---|---|---|
| Demand side | Employers / households / businesses | Find and book trusted domestic workers or cleaners |
| Supply side | Helpers / domestic workers / cleaners | Get verified, visible, and receive consistent work opportunities |
| Platform | MongiKazi Admin / Operations | Verify users, manage bookings, resolve disputes, control marketplace quality |

The platform should not only be a booking app. It should become a **trust infrastructure layer** for domestic work.

### Core Pillars

1. **Trust**
   - ID verification
   - Criminal record / reference checks
   - Ratings and reviews
   - Booking audit trail

2. **Speed**
   - Find available helpers quickly
   - Book in under 60 seconds
   - Rebook previous helpers easily

3. **Fairness**
   - Workers build digital reputation
   - Employers get transparent pricing and service history
   - Platform enables safer work relationships

4. **Scalability**
   - Start simple
   - Add verification, payments, subscriptions, AI matching, and compliance features over time

---

## 2. Core Platform Modules

| Module | Purpose |
|---|---|
| Accounts & Roles | Manage users, authentication, employer/helper/admin roles |
| Onboarding | Capture role-specific onboarding data |
| Helper Profiles | Store worker CV, experience, verification, skills, availability |
| Employer Profiles | Store employer details, locations, preferences, booking history |
| Search & Matching | Allow employers to find helpers by location, skills, rating, availability |
| Bookings | Manage booking requests, accept/decline, status changes |
| Messaging | Enable communication between employer and helper |
| Reviews & Ratings | Build trust after completed jobs |
| Payments / Invoicing | Invoice employer, collect proof of payment, manage commission |
| Notifications | SMS/WhatsApp/email/app notifications |
| Admin Operations | Verification, disputes, bookings oversight, quality control |
| Analytics | Track growth, booking success, helper earnings, employer retention |

---

## 2A. Website and Portal Structure

MongiKazi should be structured around one public-facing website and multiple role-based portals. This ensures each user group only sees the functionality relevant to them, while the underlying Django backend remains modular and reusable.

### 2A.1 Public Website

The public website is the trust-building and conversion layer of the platform.

#### Purpose

The website should explain what MongiKazi does, build confidence, and direct users into the correct registration journey.

#### Target Audiences

| Audience | Website Goal |
|---|---|
| Employers / households | Convince them that MongiKazi is safe, fast, and reliable |
| Helpers / domestic workers | Show that MongiKazi creates access to work opportunities |
| Businesses | Position MongiKazi as a solution for office cleaning and recurring support |
| Partners | Present the platform as a scalable domestic work infrastructure solution |

#### Core Website Pages

| Page | Purpose |
|---|---|
| Home | Explain value proposition and direct users to employer/helper onboarding |
| Find Help | Explain employer benefits, how booking works, and trust features |
| Find Work | Explain helper benefits, profile creation, verification, and earnings opportunity |
| How It Works | Show the full process for both employers and helpers |
| Trust & Safety | Explain verification, ratings, reviews, identity checks, and safety rules |
| Pricing | Explain booking fees, commissions, and service pricing model |
| About | Explain MongiKazi mission and market problem |
| Contact | Support, enquiries, and business partnership contact |
| FAQs | Common questions for employers and helpers |
| Terms & Privacy | Legal policies and platform conditions |

#### Website Calls to Action

| CTA | Destination |
|---|---|
| I need help | Employer registration / onboarding |
| I want work | Helper registration / onboarding |
| Book a cleaner | Employer service selection |
| Become a helper | Helper profile setup |
| Contact us | General enquiry form |

#### Website Design Principle

The website should communicate **trust before transaction**. The user should understand that MongiKazi is not just a listing site, but a controlled marketplace with verification, reviews, and operational oversight.

---

### 2A.2 Employer Portal

The Employer Portal is the self-service workspace for households and businesses that need domestic help.

#### Purpose

Allow employers to search, book, manage, pay, review, and rebook helpers.

#### Key Employer Portal Areas

| Area | Functionality |
|---|---|
| Employer Dashboard | Upcoming bookings, quick booking CTA, favourite helpers, payment reminders |
| Search Helpers | Search by location, availability, category, rating, price, verification status |
| Helper Profile View | View helper bio, skills, rating, work history, availability, verification badges |
| Booking Management | Create booking, view booking status, cancel, reschedule, complete booking |
| Messages | Chat with helper after booking request or confirmation |
| Favourite Helpers | Save trusted helpers for future bookings |
| Rebook | Quickly repeat a past booking |
| Payments & Invoices | View invoices, upload proof of payment, track payment status |
| Reviews | Rate helpers after completed work |
| Employer Profile | Manage contact information, locations, preferences, and account settings |
| Support / Disputes | Raise issues, view dispute status, contact admin |

#### Employer Dashboard Widgets

| Widget | Purpose |
|---|---|
| Upcoming Booking | Shows next confirmed helper booking |
| Book Again | Promotes repeat usage |
| Favourite Helpers | Gives quick access to trusted workers |
| Pending Requests | Shows bookings awaiting helper response |
| Payment Due | Shows unpaid invoices or pending proof of payment |
| Recent Activity | Shows latest booking, message, payment, and review actions |

#### Employer Portal User Flow

```text
Employer Login
    ↓
Dashboard
    ↓
Search Helpers / Book Again
    ↓
View Helper Profile
    ↓
Create Booking Request
    ↓
Helper Accepts
    ↓
Booking Confirmed
    ↓
Job Completed
    ↓
Payment / Review / Rebook
```

---

### 2A.3 Helper / Employee Portal

The Helper Portal is the self-service workspace for domestic workers, cleaners, and service providers.

#### Naming Note

Although the business may refer to workers as “employees” operationally, the portal should probably use user-friendly wording such as **Helper Portal**, **Worker Portal**, or **My Work Portal**. This avoids confusion because many helpers may not be formal employees of MongiKazi; they are marketplace participants unless the legal model later changes.

#### Purpose

Allow helpers to build their profile, manage availability, receive booking requests, complete jobs, and track earnings.

#### Key Helper Portal Areas

| Area | Functionality |
|---|---|
| Helper Dashboard | Today’s bookings, pending requests, earnings summary, profile status |
| Profile Builder | Photo, bio, skills, experience, service categories, work preferences |
| Verification Centre | Upload ID, criminal record check, references, certificates |
| Availability | Set working days, unavailable dates, preferred hours |
| Booking Requests | Accept, decline, or message employer |
| My Jobs | View upcoming, active, completed, cancelled, and disputed jobs |
| Messages | Communicate with employers linked to booking requests |
| Earnings | View completed jobs, expected payout, paid status, platform commission impact |
| Reviews | View employer ratings and feedback |
| Employer Ratings | Rate employers after completed jobs |
| Digital CV | View platform-generated worker profile and work history |
| Support / Safety | Report unsafe environment, dispute payment, contact platform support |

#### Helper Dashboard Widgets

| Widget | Purpose |
|---|---|
| Pending Booking Requests | Helps the worker respond quickly |
| Today’s Jobs | Shows immediate work commitments |
| Weekly Earnings | Motivates usage and shows income opportunity |
| Profile Completeness | Encourages verification and better profile quality |
| Rating Summary | Shows reputation score |
| Verification Status | Shows pending/approved/rejected documents |
| Available Jobs Nearby | Optional future opportunity feed |

#### Helper Portal User Flow

```text
Helper Login
    ↓
Dashboard
    ↓
Complete Profile / Verification
    ↓
Set Availability
    ↓
Receive Booking Request
    ↓
Accept / Decline
    ↓
Complete Job
    ↓
Rate Employer
    ↓
Track Earnings / Build Reputation
```

---

### 2A.4 Admin / Operations Portal

The Admin Portal is the operational control centre for MongiKazi staff.

#### Purpose

Allow internal users to manage verification, marketplace quality, bookings, payments, disputes, content, and platform reporting.

#### Key Admin Portal Areas

| Area | Functionality |
|---|---|
| Admin Dashboard | Marketplace KPIs, pending actions, operational alerts |
| User Management | View and manage employers, helpers, staff users |
| Helper Verification Queue | Review ID documents, criminal checks, references, certificates |
| Employer Review | Review employer profiles, flagged users, suspicious activity |
| Booking Operations | View all bookings, statuses, cancellations, disputes |
| Payment Operations | View invoices, POP uploads, payment verification, helper payout status |
| Dispute Management | Manage complaints, safety issues, payment disputes, no-shows |
| Review Moderation | Monitor abusive, fraudulent, or inappropriate reviews |
| Commission Management | Configure fixed/percentage commission rules |
| Service Category Management | Manage cleaning, childcare, laundry, cooking, office cleaning categories |
| Notifications Management | Manage templates and outbound message logs |
| Reports & Analytics | Revenue, bookings, helper earnings, repeat usage, verification turnaround |
| Website Content Management | Manage FAQs, service descriptions, trust/safety content if CMS-like functionality is added |

#### Admin Dashboard Widgets

| Widget | Purpose |
|---|---|
| Pending Helper Verifications | Shows operational queue |
| Active Bookings | Tracks live marketplace activity |
| Payment Proofs Pending | Finance control |
| Disputes Open | Risk and safety control |
| New Employers | Demand-side growth |
| New Helpers | Supply-side growth |
| Booking Conversion Rate | Marketplace health |
| Revenue This Month | Commercial tracking |
| Low-Rated Users | Quality intervention |
| Cancellation / No-Show Alerts | Trust and reliability monitoring |

---

### 2A.5 Optional Business / Corporate Portal

This can be introduced once MongiKazi starts serving offices, SMEs, schools, clinics, property managers, or recurring business clients.

#### Purpose

Allow organisations to manage multiple bookings, locations, invoices, and recurring cleaning schedules.

#### Key Business Portal Areas

| Area | Functionality |
|---|---|
| Company Profile | Business details, billing details, authorised users |
| Multiple Locations | Office branches, sites, or properties |
| Recurring Bookings | Daily, weekly, monthly cleaning schedules |
| Team Access | Multiple users under one company account |
| Bulk Booking | Request multiple helpers for one job |
| Business Invoices | Consolidated invoice history and payment status |
| Preferred Helper Pool | Approved workers for the organisation |
| Service Level Tracking | Attendance, completion, complaints, recurring performance |

This portal should not be in the first MVP unless there is a clear business client pipeline, but the architecture should allow it later.

---

## 2B. Portal-to-Module Mapping

The portals should not duplicate business logic. They should consume the same underlying platform modules through views, services, selectors, and later APIs.

| Functionality | Website | Employer Portal | Helper Portal | Admin Portal | Business Portal |
|---|---:|---:|---:|---:|---:|
| Register / Login | Yes | Yes | Yes | Yes | Yes |
| Role-Based Onboarding | Yes | Yes | Yes | No | Yes |
| Helper Profile Creation | No | No | Yes | Yes | No |
| Employer Profile Management | No | Yes | No | Yes | Yes |
| Search Helpers | Marketing CTA only | Yes | No | Yes | Yes |
| Booking Requests | No | Yes | Yes | Yes | Yes |
| Accept / Decline Booking | No | No | Yes | Admin override only | No |
| Messaging | No | Yes | Yes | Oversight only | Yes |
| Reviews | Trust display only | Yes | Yes | Moderation | Yes |
| Verification Documents | Trust explanation | No | Yes | Yes | No |
| Invoices / POP Upload | No | Yes | Earnings view only | Yes | Yes |
| Payout Tracking | No | No | Yes | Yes | No |
| Disputes | Contact form | Yes | Yes | Yes | Yes |
| Analytics | Public stats only | Personal history | Personal earnings | Full platform | Company-level |
| CMS / Public Content | Yes | No | No | Yes | No |

---

## 2C. Recommended Django App Alignment for Portals

The portal layer should mainly contain views, templates, and routing. Business logic should stay inside the domain apps.

### Suggested Portal Apps

```text
portals/
│
├── website/
│   ├── views.py
│   ├── urls.py
│   └── templates/website/
│
├── employer_portal/
│   ├── views.py
│   ├── urls.py
│   └── templates/employer_portal/
│
├── helper_portal/
│   ├── views.py
│   ├── urls.py
│   └── templates/helper_portal/
│
├── admin_portal/
│   ├── views.py
│   ├── urls.py
│   └── templates/admin_portal/
│
└── business_portal/
    ├── views.py
    ├── urls.py
    └── templates/business_portal/
```

Alternative simpler MVP structure:

```text
website/
employer_portal/
helper_portal/
operations/
```

The second option is easier for the MVP. The first option is more structured if you want a very clean separation between portals.

### Recommended MVP Approach

Use this structure first:

```text
website/
employer_portal/
helper_portal/
operations/
```

Then add `business_portal/` later when B2B demand is validated.

---

## 2D. Portal Architecture Principle

The portals should be **presentation and orchestration layers**, not business logic containers.

Good pattern:

```text
Employer Portal View
    ↓
bookings.services.create_booking_request()
    ↓
notifications.services.notify_helper()
    ↓
bookings.events.record_booking_event()
```

Bad pattern:

```text
Employer Portal View
    ↓
Directly updates booking status
Directly sends notification
Directly calculates commission
Directly creates audit log
```

This is important because the same booking logic may later be used by:

- Employer web portal
- Helper mobile app
- Admin dashboard
- Business portal
- WhatsApp booking assistant
- Public website lead form

---


## 3. Expected Business Processes

### 3.1 User Registration Process

#### Objective

Allow a user to create an account and choose whether they are looking for help or looking for work.

#### Process

1. User lands on welcome screen.
2. User selects:
   - “I’m looking for help”
   - “I’m looking for work”
3. User enters:
   - Phone number
   - OTP verification
   - Name and surname
   - Location
4. System creates the account.
5. System assigns the user role:
   - Employer
   - Helper
6. User is redirected into the correct onboarding flow.

#### Key Rule

The role split should happen early because employer and helper workflows are fundamentally different.

---

### 3.2 Helper Onboarding Process

#### Objective

Allow a helper to build a trusted profile that employers can view.

#### Process

1. Helper uploads profile photo.
2. Helper captures personal details.
3. Helper uploads ID document.
4. Helper selects work categories:
   - Cleaning
   - Childcare
   - Laundry
   - Cooking
   - Office cleaning
5. Helper captures experience:
   - Years of experience
   - Short work description
   - Previous roles
6. Helper uploads supporting documents:
   - Criminal record check
   - References
   - Certificates, where applicable
7. Helper sets availability.
8. Helper previews public profile.
9. Helper submits profile for review.
10. Admin verifies the profile.
11. Profile becomes active and searchable.

#### Important Design Principle

This should feel like the helper is **building a digital CV**, not filling out a compliance form.

---

### 3.3 Employer Onboarding Process

#### Objective

Allow the employer to define their needs and start browsing available helpers.

#### Process

1. Employer confirms location.
2. Employer selects service type:
   - Once-off cleaning
   - Recurring domestic help
   - Office cleaning
   - Laundry support
   - Cooking support
3. Employer selects preferred date and time.
4. Employer adds special instructions.
5. System recommends matching helpers.
6. Employer browses helper profiles.
7. Employer can book immediately or save favourite helpers.

---

### 3.4 Search and Matching Process

#### Objective

Help employers find suitable helpers quickly.

#### Basic Search Filters

| Filter | Description |
|---|---|
| Location | Helpers near employer |
| Service type | Cleaning, childcare, laundry, cooking |
| Availability | Available today, this week, specific date |
| Rating | Minimum star rating |
| Experience | Years of experience |
| Verification status | ID verified, criminal check uploaded |
| Price range | Hourly/daily rate range |

#### Basic Matching Logic

The system should rank helpers based on:

1. Distance from employer
2. Availability
3. Service category match
4. Rating
5. Completed jobs
6. Verification strength
7. Response rate

MVP can use rule-based matching. AI matching should come later.

---

### 3.5 Booking Request Process

#### Objective

Allow an employer to request a helper and allow the helper to accept or decline.

#### Process

1. Employer selects helper.
2. Employer chooses:
   - Date
   - Start time
   - Duration
   - Location
   - Service type
   - Special instructions
3. System calculates estimated price.
4. Employer submits booking request.
5. Helper receives notification.
6. Helper can:
   - Accept
   - Decline
   - Ask a question through messaging
7. If accepted:
   - Booking status becomes confirmed.
   - Employer and helper see booking details.
8. If declined:
   - Employer is prompted to choose another helper.

#### Suggested Booking Statuses

| Status | Meaning |
|---|---|
| Draft | Employer has started but not submitted |
| Pending Helper Response | Booking sent to helper |
| Accepted | Helper accepted |
| Declined | Helper declined |
| Cancelled by Employer | Employer cancelled |
| Cancelled by Helper | Helper cancelled |
| In Progress | Job is happening |
| Completed | Job completed |
| Disputed | Issue raised |
| Closed | Review/payment/admin closure complete |

---

### 3.6 Job Completion Process

#### Objective

Confirm that work was completed and trigger reviews/payment process.

#### Process

1. Booking date arrives.
2. Helper marks “I’m on my way”.
3. Helper marks “Arrived”.
4. Employer can confirm arrival.
5. Helper marks “Job completed”.
6. Employer confirms completion.
7. System opens review flow.
8. Payment/invoice workflow is triggered depending on payment model.

For MVP, this can be simplified to:

1. Booking accepted.
2. Booking date passes.
3. Employer marks completed.
4. Review becomes available.

---

### 3.7 Review and Rating Process

#### Objective

Build a trust engine for both employers and helpers.

#### Process

1. After completion, employer rates helper.
2. Employer provides:
   - Star rating
   - Written review
   - Optional tags: punctual, professional, thorough, friendly
3. Helper rates employer.
4. Helper provides:
   - Star rating
   - Optional tags: respectful, paid on time, clear instructions, safe environment
5. Ratings update user profiles.

#### Important

Helpers should also rate employers. This is important for worker safety and platform fairness.

---

### 3.8 Payment and Commission Process

The current payment model is semi-manual, which is suitable for MVP.

#### Process

1. Booking is confirmed or completed.
2. Platform generates invoice to employer.
3. Invoice shows:
   - Worker fee
   - Platform commission
   - Total payable
   - Banking details
4. Employer pays via EFT.
5. Employer uploads proof of payment.
6. Admin verifies payment.
7. Platform deducts commission.
8. Platform records payout amount to helper.
9. Helper payment is marked as paid.

#### Commission Rules

| Work Type | Commission Model |
|---|---|
| Helper placement / longer-term domestic work | Fixed R500 |
| Temporary / once-off work | 10%–25% commission |

#### Payment Statuses

| Status | Meaning |
|---|---|
| Invoice Pending | Invoice not yet generated |
| Invoice Sent | Invoice sent to employer |
| Awaiting Payment | Waiting for employer payment |
| POP Uploaded | Employer uploaded proof of payment |
| Payment Verified | Admin verified payment |
| Helper Paid | Helper payout completed |
| Payment Disputed | Payment issue exists |

---

## 4. MVP Feature Scope

The MVP should validate marketplace demand first. Avoid overbuilding payments, subscriptions, and AI too early.

### MVP Must-Have Features

| Feature | Reason |
|---|---|
| User registration | Required for both sides |
| Role-based onboarding | Critical to split employer/helper journeys |
| Helper profile creation | Core supply-side asset |
| Employer profile | Required for booking context |
| Search and browse helpers | Core employer value |
| Booking requests | Core marketplace transaction |
| Accept/decline flow | Required for helper control |
| Basic messaging | Needed for coordination |
| Reviews and ratings | Trust layer |
| Admin verification | Quality control |
| Admin booking oversight | Operations control |

### MVP Should Avoid Initially

| Feature | Reason |
|---|---|
| Fully automated payments | Complex; can be manual at first |
| AI matching | Rule-based matching is enough initially |
| Subscriptions | Better after usage patterns are proven |
| Insurance layer | Phase 2/3 feature |
| Complex dispute automation | Admin-managed initially |
| Multi-language support | Important, but not first release unless target users require it immediately |

---

## 5. Expert Features / Advanced Platform Capabilities

These are the features that would make MongiKazi more than a basic marketplace.

### 5.1 Trust Score

Each helper can have a trust score based on:

| Factor | Weight Example |
|---|---|
| ID verified | High |
| Criminal check uploaded | High |
| References provided | Medium |
| Completed jobs | High |
| Average rating | High |
| Cancellation rate | Medium |
| Response time | Medium |
| Repeat bookings | High |

Example:

```text
Trust Score = Verification + Reviews + Reliability + Experience + Repeat Usage
```

This can be displayed as:

- Verified
- Highly trusted
- Top rated
- New but verified
- Needs more reviews

---

### 5.2 Helper Reliability Score

This is different from reviews. It measures behaviour.

Inputs:

- Acceptance rate
- Late cancellation rate
- No-show count
- Average response time
- On-time arrival confirmations
- Completed booking count

This helps protect employer experience.

---

### 5.3 Employer Safety Score

Helpers also need protection.

Inputs:

- Helper ratings of employer
- Payment behaviour
- Cancellation history
- Dispute history
- Address verification
- Repeat booking behaviour

This helps identify risky employers.

---

### 5.4 Smart Matching Engine

Initially rule-based, later AI-assisted.

Matching factors:

1. Distance
2. Availability
3. Skill match
4. Prior booking history
5. Employer preference
6. Helper preference
7. Ratings
8. Price fit
9. Language preference
10. Reliability score

Example matching result:

```text
Recommended because:
- Available on your selected date
- 4.8 star rating
- 3 years cleaning experience
- 2.3 km away
- Completed 18 jobs
```

This explanation builds trust.

---

### 5.5 Rebooking Engine

Rebooking is key for retention.

Features:

- Favourite helpers
- “Book again” button
- Recurring schedule
- Preferred helper list
- Monthly household help plan

This can become a major revenue driver.

---

### 5.6 Subscription Plans

#### Potential Employer Plans

| Plan | Description |
|---|---|
| Pay-as-you-go | Pay commission per booking |
| Household Plan | Monthly access to preferred helpers |
| Business Plan | Office cleaning / recurring business support |
| Premium Trust Plan | Priority verified helpers and support |

#### Helper Monetisation Note

Potential helper plans should be handled carefully. Charging workers too early can damage adoption.

Better options:

- Free basic listing
- Optional featured profile
- Optional CV verification badge
- Optional training/certification support

---

### 5.7 Admin Quality Control Dashboard

Admin should be able to monitor:

| Metric | Purpose |
|---|---|
| Pending helper verifications | Operational queue |
| Booking acceptance rate | Marketplace health |
| Declined bookings | Supply-demand mismatch |
| Cancellation rate | Reliability |
| Disputes | Risk control |
| Top helpers | Quality recognition |
| Low-rated helpers | Intervention |
| Revenue by commission type | Financial tracking |
| Employer repeat rate | Retention |
| Helper earnings | Worker impact |

---

### 5.8 Worker Development Features

This is a strong differentiator.

Future features:

- Digital helper CV
- Downloadable work history
- Training badges
- Skills certification
- Reference management
- Worker earnings history
- Financial wellness tools
- Savings or insurance partnerships

This positions MongiKazi as an empowerment platform, not just a gig marketplace.

---

## 6. Recommended Django Project Architecture

The Django structure should be modular from the start. Avoid putting everything into one large app.

### 6.1 Suggested Django Apps

```text
mongikazi/
│
├── config/
│   ├── settings/
│   │   ├── base.py
│   │   ├── local.py
│   │   ├── production.py
│   ├── urls.py
│   ├── celery.py
│   └── wsgi.py / asgi.py
│
├── website/
│   ├── views.py
│   ├── urls.py
│   └── templates/website/
│
├── employer_portal/
│   ├── views.py
│   ├── urls.py
│   └── templates/employer_portal/
│
├── helper_portal/
│   ├── views.py
│   ├── urls.py
│   └── templates/helper_portal/
│
├── operations/
│   ├── dashboards.py
│   ├── admin_views.py
│   ├── reports.py
│   └── templates/operations/
│
├── accounts/
│   ├── models.py
│   ├── views.py
│   ├── services/
│   ├── selectors/
│   └── permissions.py
│
├── onboarding/
│   ├── models.py
│   ├── services/
│   ├── workflows.py
│   └── views.py
│
├── helpers/
│   ├── models.py
│   ├── services/
│   ├── selectors/
│   └── views.py
│
├── employers/
│   ├── models.py
│   ├── services/
│   ├── selectors/
│   └── views.py
│
├── bookings/
│   ├── models.py
│   ├── services/
│   ├── workflows.py
│   ├── selectors/
│   └── views.py
│
├── messaging/
│   ├── models.py
│   ├── services/
│   └── consumers.py
│
├── reviews/
│   ├── models.py
│   ├── services/
│   └── selectors.py
│
├── payments/
│   ├── models.py
│   ├── services/
│   ├── invoices.py
│   └── views.py
│
├── verification/
│   ├── models.py
│   ├── services/
│   ├── checks.py
│   └── admin_views.py
│
├── notifications/
│   ├── models.py
│   ├── services/
│   ├── channels.py
│   └── tasks.py
│
├── marketplace/
│   ├── matching.py
│   ├── search.py
│   ├── ranking.py
│   └── recommendations.py
│
└── common/
    ├── models.py
    ├── utils.py
    ├── constants.py
    └── mixins.py
```

---

## 7. Core Django Design Principles

### 7.1 Keep Views Thin

Views should not hold business logic.

Bad pattern:

```python
def accept_booking(request, booking_id):
    # lots of validation
    # update booking
    # notify employer
    # create audit record
    # update helper stats
```

Better pattern:

```python
def accept_booking(request, booking_id):
    booking_service.accept_booking(
        booking_id=booking_id,
        helper=request.user.helper_profile
    )
    return redirect("helper_bookings")
```

The real logic belongs in:

```text
bookings/services.py
bookings/workflows.py
notifications/services.py
```

---

### 7.2 Use Services for Business Logic

Example service functions:

```python
create_booking_request()
accept_booking()
decline_booking()
cancel_booking()
complete_booking()
generate_invoice_for_booking()
submit_review()
verify_helper_profile()
calculate_helper_trust_score()
```

This makes the system easier to test and maintain.

---

### 7.3 Use Selectors for Query Logic

Selectors should handle complex database reads.

Example:

```python
get_available_helpers_for_location()
get_helper_booking_history()
get_employer_upcoming_bookings()
get_admin_pending_verifications()
get_marketplace_search_results()
```

This avoids repeating query logic across views.

---

### 7.4 Use Workflow Logic for State Transitions

Bookings, verification, and payments should be treated as workflows.

Example booking transition:

```text
Pending Helper Response
    ↓ accept
Accepted
    ↓ job starts
In Progress
    ↓ complete
Completed
    ↓ reviewed/payment closed
Closed
```

Each transition should be controlled. Do not allow random status updates from templates or forms.

---

## 8. Recommended Core Models

### 8.1 User Model

Use a custom user model from the beginning.

```python
class User(AbstractUser):
    class Role(models.TextChoices):
        EMPLOYER = "EMPLOYER", "Employer"
        HELPER = "HELPER", "Helper"
        ADMIN = "ADMIN", "Admin"

    role = models.CharField(max_length=20, choices=Role.choices)
    phone_number = models.CharField(max_length=20, unique=True)
    is_phone_verified = models.BooleanField(default=False)
```

This gives you control over mobile-first authentication.

---

### 8.2 Helper Profile

```python
class HelperProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_photo = models.ImageField(upload_to="helpers/photos/", null=True, blank=True)
    bio = models.TextField(blank=True)
    years_experience = models.PositiveIntegerField(default=0)
    location = models.CharField(max_length=255)
    is_active = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    average_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    completed_jobs = models.PositiveIntegerField(default=0)
    trust_score = models.DecimalField(max_digits=5, decimal_places=2, default=0)
```

---

### 8.3 Work Category

```python
class WorkCategory(models.Model):
    name = models.CharField(max_length=100)
```

Examples:

- Cleaning
- Laundry
- Cooking
- Childcare
- Office cleaning

---

### 8.4 Helper Skill

```python
class HelperSkill(models.Model):
    helper = models.ForeignKey(HelperProfile, on_delete=models.CASCADE)
    category = models.ForeignKey(WorkCategory, on_delete=models.CASCADE)
    years_experience = models.PositiveIntegerField(default=0)
```

---

### 8.5 Employer Profile

```python
class EmployerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    display_name = models.CharField(max_length=255)
    default_location = models.CharField(max_length=255)
    is_verified = models.BooleanField(default=False)
    average_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0)
```

---

### 8.6 Booking

```python
class Booking(models.Model):
    class Status(models.TextChoices):
        DRAFT = "DRAFT", "Draft"
        PENDING = "PENDING", "Pending Helper Response"
        ACCEPTED = "ACCEPTED", "Accepted"
        DECLINED = "DECLINED", "Declined"
        CANCELLED = "CANCELLED", "Cancelled"
        IN_PROGRESS = "IN_PROGRESS", "In Progress"
        COMPLETED = "COMPLETED", "Completed"
        DISPUTED = "DISPUTED", "Disputed"
        CLOSED = "CLOSED", "Closed"

    employer = models.ForeignKey(EmployerProfile, on_delete=models.CASCADE)
    helper = models.ForeignKey(HelperProfile, on_delete=models.CASCADE)
    category = models.ForeignKey(WorkCategory, on_delete=models.PROTECT)
    status = models.CharField(max_length=30, choices=Status.choices, default=Status.DRAFT)
    scheduled_date = models.DateField()
    start_time = models.TimeField()
    duration_hours = models.DecimalField(max_digits=5, decimal_places=2)
    location = models.CharField(max_length=255)
    special_instructions = models.TextField(blank=True)
    estimated_price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
```

---

### 8.7 Booking Event / Audit Trail

This is important. Every booking action should be traceable.

```python
class BookingEvent(models.Model):
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE)
    event_type = models.CharField(max_length=50)
    description = models.TextField()
    performed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
```

Example events:

- Booking requested
- Helper accepted
- Helper declined
- Employer cancelled
- Helper marked completed
- Employer confirmed completion
- Review submitted
- Payment verified

---

### 8.8 Review

```python
class Review(models.Model):
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE)
    reviewer = models.ForeignKey(User, on_delete=models.CASCADE, related_name="reviews_given")
    reviewee = models.ForeignKey(User, on_delete=models.CASCADE, related_name="reviews_received")
    rating = models.PositiveSmallIntegerField()
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
```

---

### 8.9 Verification Document

```python
class VerificationDocument(models.Model):
    class DocumentType(models.TextChoices):
        ID_DOCUMENT = "ID_DOCUMENT", "ID Document"
        CRIMINAL_CHECK = "CRIMINAL_CHECK", "Criminal Record Check"
        REFERENCE = "REFERENCE", "Reference"
        CERTIFICATE = "CERTIFICATE", "Certificate"

    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        APPROVED = "APPROVED", "Approved"
        REJECTED = "REJECTED", "Rejected"

    helper = models.ForeignKey(HelperProfile, on_delete=models.CASCADE)
    document_type = models.CharField(max_length=50, choices=DocumentType.choices)
    file = models.FileField(upload_to="verification/")
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    reviewed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
```

---

### 8.10 Invoice / Payment

```python
class BookingInvoice(models.Model):
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE)
    worker_fee = models.DecimalField(max_digits=10, decimal_places=2)
    platform_commission = models.DecimalField(max_digits=10, decimal_places=2)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    invoice_date = models.DateField()
    due_date = models.DateField()
    is_sent = models.BooleanField(default=False)
```

```python
class PaymentProof(models.Model):
    invoice = models.ForeignKey(BookingInvoice, on_delete=models.CASCADE)
    proof_file = models.FileField(upload_to="payment_proofs/")
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    is_verified = models.BooleanField(default=False)
```

---

## 9. Suggested Architecture Layers

The project should follow this pattern:

```text
Template / API Layer
        ↓
Views / ViewSets
        ↓
Forms / Serializers
        ↓
Services
        ↓
Selectors
        ↓
Models
        ↓
Database
```

Example:

```text
Employer clicks Book Now
        ↓
booking_create_view
        ↓
BookingRequestForm
        ↓
booking_service.create_booking_request()
        ↓
Booking.objects.create()
        ↓
notification_service.notify_helper()
        ↓
BookingEvent.objects.create()
```

This is scalable and avoids messy Django views.

---

## 10. API Strategy

Since this is mobile-first, the backend should be API-ready.

### Option 1: Django Templates First

Good for fast MVP.

Use:

- Django views
- Django templates
- HTMX/AJAX for dynamic interactions
- Bootstrap/Tailwind for UI

### Option 2: Django REST Framework First

Better for mobile app and future scale.

Use:

- Django REST Framework
- Token/JWT authentication
- React Native / Flutter frontend later
- Admin dashboard still in Django templates

### Recommendation

Start with **Django templates for admin and operations**, but design the core platform services so they can later be exposed through **Django REST Framework APIs**.

---

## 11. Recommended MVP Technical Stack

| Layer | Recommendation |
|---|---|
| Backend | Django |
| API | Django REST Framework, phased in |
| Database | PostgreSQL |
| Cache / Queue | Redis |
| Background Jobs | Celery |
| File Storage | Local in development, S3-compatible storage in production |
| Notifications | Email first, then SMS/WhatsApp |
| Frontend | Django templates + Tailwind/Bootstrap initially |
| Admin | Custom Django admin dashboard |
| Maps / Location | Google Maps API or OpenStreetMap later |
| Authentication | Phone OTP eventually; email/password acceptable for internal MVP |
| Deployment | Docker + Render/Azure/App Service/DigitalOcean depending budget |

---

## 12. Scalability Considerations

### 12.1 Database Scalability

Use PostgreSQL from the start.

Important indexes:

- Helper location
- Helper active status
- Helper verification status
- Booking status
- Booking scheduled date
- Employer ID
- Helper ID
- Work category
- Created date

Example:

```python
class Meta:
    indexes = [
        models.Index(fields=["status"]),
        models.Index(fields=["scheduled_date"]),
        models.Index(fields=["helper", "status"]),
        models.Index(fields=["employer", "status"]),
    ]
```

---

### 12.2 Background Processing

Use Celery for:

- Sending notifications
- Generating invoices
- Updating trust scores
- Recalculating helper ratings
- Sending booking reminders
- Processing document verification workflows
- Generating admin reports

---

### 12.3 Auditability

For marketplace trust, audit logs are important.

Track:

- Who created a booking
- Who accepted/declined
- Who cancelled
- Who uploaded documents
- Who approved verification
- Who verified payment
- Who changed profile status

This protects the business when disputes happen.

---

### 12.4 Permissions

Do not rely only on templates hiding buttons.

You need permission checks in services and views.

Examples:

- Only the assigned helper can accept a booking.
- Only the booking employer can cancel as employer.
- Only admin can approve verification documents.
- Only users involved in a booking can message each other.
- Reviews can only be submitted after completed bookings.

---

## 13. Suggested User Dashboards

### 13.1 Helper Dashboard

| Section | Purpose |
|---|---|
| Today’s bookings | Immediate work visibility |
| Pending requests | Accept/decline quickly |
| Weekly earnings | Motivation |
| Profile completeness | Encourage verification |
| Rating summary | Reputation |
| Available jobs nearby | Opportunity feed |

---

### 13.2 Employer Dashboard

| Section | Purpose |
|---|---|
| Upcoming bookings | Know what is scheduled |
| Book again | Fast rebooking |
| Favourite helpers | Retention |
| Search helpers | Core action |
| Past bookings | History |
| Payment status | Invoice/payment clarity |

---

### 13.3 Admin Dashboard

| Section | Purpose |
|---|---|
| Pending helper approvals | Verification queue |
| Active bookings | Operational oversight |
| Payment proofs pending | Finance control |
| Disputes | Risk management |
| New users | Growth |
| Revenue | Business performance |
| Low-rated profiles | Quality control |

---

## 14. Suggested Development Phases

### Phase 1: Foundation MVP

Build:

1. Custom user model
2. Employer/helper roles
3. Role-based onboarding
4. Helper profiles
5. Employer profiles
6. Basic search
7. Booking request flow
8. Accept/decline flow
9. Admin verification
10. Basic reviews

Goal:

Validate that employers are willing to book and helpers are willing to use the platform.

---

### Phase 2: Trust and Operations Layer

Build:

1. Verification document workflow
2. Helper trust score
3. Employer rating
4. Booking audit trail
5. Admin operations dashboard
6. Notifications
7. Basic invoice generation
8. Payment proof upload

Goal:

Make the platform safer and operationally manageable.

---

### Phase 3: Marketplace Intelligence

Build:

1. Advanced matching
2. Helper reliability score
3. Employer safety score
4. Rebooking engine
5. Favourite helpers
6. Recurring bookings
7. Availability calendar
8. Better search ranking

Goal:

Improve repeat usage and marketplace quality.

---

### Phase 4: Commercialisation

Build:

1. Subscription plans
2. Featured helpers
3. Business/office cleaning accounts
4. Commission analytics
5. Worker earnings dashboard
6. Automated payment integrations
7. PDF invoices and statements

Goal:

Increase revenue and prepare for scale.

---

### Phase 5: Mobile and Ecosystem Expansion

Build:

1. Mobile app
2. WhatsApp booking assistant
3. Worker training badges
4. Insurance partnerships
5. Employer contracts
6. Helper digital CV export
7. AI-assisted matching

Goal:

Become a broader domestic work infrastructure platform.

---

## 15. Critical Design Decisions to Make Early

| Decision | Recommendation |
|---|---|
| User model | Use custom user model from day one |
| Auth method | Phone-first eventually; email/password acceptable during MVP |
| Database | PostgreSQL |
| Booking status model | Define strictly early |
| Worker verification | Make it modular |
| Payments | Manual first, automated later |
| Search | Rule-based first, AI later |
| Admin | Custom dashboard, not only Django admin |
| API readiness | Keep business logic in services so APIs can be added later |
| Mobile | Design mobile-first even if web MVP comes first |

---

## 16. Proposed Initial App Build Order

Recommended Django app build order:

```text
1. accounts
2. website
3. helpers
4. employers
5. onboarding
6. employer_portal
7. helper_portal
8. bookings
9. reviews
10. verification
11. notifications
12. payments
13. marketplace
14. operations
15. business_portal
```

Reason:

- Accounts must come first.
- Website can be built early as the public conversion layer.
- Profiles must exist before bookings.
- Employer and helper portals should be introduced once role-specific profile data exists.
- Bookings must exist before payments/reviews.
- Admin operations becomes valuable once users, verifications, and transactions exist.
- Business portal should come later unless B2B demand is already validated.

---

## 17. First Technical Milestone

### Milestone: Verified Helper Marketplace MVP

Scope:

1. Employer can register.
2. Helper can register.
3. Helper can create profile.
4. Admin can verify helper.
5. Employer can browse verified helpers.
6. Employer can send booking request.
7. Helper can accept/decline.
8. Employer and helper can see booking details.
9. Employer can rate helper after completion.

This is the smallest complete marketplace loop.

---

## 18. Recommended Next Artefact

The next useful artefact would be a **technical implementation plan for Codex**, structured like this:

```text
MongiKazi Django Implementation Plan
1. Project setup
2. App structure
3. Model definitions
4. Service layer design
5. URL structure
6. Template structure
7. Admin dashboard structure
8. MVP workflows
9. Testing requirements
10. Guardrails and constraints
```

---

## 19. Architecture Recommendation

Build MongiKazi as a **modular Django monolith** with:

- Clean service layers
- Strict workflow transitions
- PostgreSQL
- Celery-ready background jobs
- API-ready business logic
- Strong audit trails
- Modular apps by business capability

Do not start with microservices. Start with a scalable monolith that can later expose mobile APIs and split services only when the platform has real operational volume.
