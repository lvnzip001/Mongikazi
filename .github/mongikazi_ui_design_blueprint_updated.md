# MongiKazi UI Design Blueprint

## 1. Design Vision

MongiKazi should feel like a **mobile-first, trust-driven services marketplace** with the simplicity of Uber, the browsing confidence of Airbnb, and the polish of a fintech platform.

The design should not feel like a basic directory of cleaners. It should feel like a structured, safe, and professional platform where employers can confidently book help and helpers can build a trusted work profile.

### Target Design Feel

| Inspiration | What MongiKazi Should Borrow |
|---|---|
| Uber | Simple booking flow, fast action, location-first experience |
| Airbnb | Profile trust, reviews, availability, human-centred browsing |
| Fintech apps | Clean hierarchy, status clarity, payment confidence, professional polish |
| LinkedIn / CV profile | Helper profiles that feel credible and career-building |

### Design Principle

> A user should understand what to do within 3 seconds and complete their core action within 3–5 taps.

---

## 2. Design Personality

MongiKazi should feel:

| Quality | Meaning |
|---|---|
| Clean | No clutter, no overloaded screens |
| Trustworthy | Verification badges, reviews, transparent statuses |
| Friendly | Warm, human, accessible |
| Fast | Clear CTAs and short journeys |
| Local | Practical language and mobile-first behaviour for the South African market |
| Professional | Polished enough for employers, businesses, and partners to trust |

### Brand Tone

```text
Warm, safe, reliable, modern, simple, empowering.
```

---

## 3. Visual Identity Direction

### 3.1 Colour Palette

Avoid too many bright colours. The palette should feel calm, professional, and trustworthy.

Recommended palette:

| Use | Colour | Purpose |
|---|---|---|
| Primary | Deep Green / Teal | Trust, work, reliability |
| Primary Dark | Dark Teal | Headers, nav, strong contrast |
| Secondary | Warm Beige / Sand | Human, warm, accessible |
| Accent | Soft Gold / Amber | Ratings, highlights, premium actions |
| Background | Off-white | Clean mobile-friendly base |
| Surface | White | Cards, forms, content areas |
| Text | Charcoal / Dark Slate | Readability |
| Muted Text | Grey | Supporting text |
| Border | Light Grey | Clean separation |
| Success | Green | Accepted, verified, completed |
| Warning | Amber | Pending, awaiting action |
| Error | Red | Declined, cancelled, dispute |

Example CSS tokens:

```css
:root {
  --mk-primary: #0F766E;
  --mk-primary-dark: #0B4F4A;
  --mk-secondary: #F4EFE7;
  --mk-accent: #D9A441;
  --mk-bg: #FAFAF7;
  --mk-surface: #FFFFFF;
  --mk-text: #1F2933;
  --mk-muted: #6B7280;
  --mk-border: #E5E7EB;
  --mk-success: #15803D;
  --mk-warning: #B45309;
  --mk-danger: #B91C1C;
}
```

### 3.2 Colour Usage Rules

| UI Element | Recommended Colour Use |
|---|---|
| Primary buttons | Deep teal |
| Secondary buttons | White with teal border/text |
| Status badges | Green/amber/red depending status |
| Ratings | Gold/amber |
| Page backgrounds | Off-white |
| Cards | White |
| Navigation | Dark teal or white depending context |
| Critical warnings | Red, used sparingly |

### 3.3 Avoid

- Too many badge colours
- Overly bright gradients
- Heavy shadows
- Dense dashboards on mobile
- Desktop-style tables for employer/helper screens
- Generic Bootstrap look without brand treatment

---

## 4. Typography and Spacing

### Typography

Use a clean, modern sans-serif font.

Recommended options:

- Inter
- Manrope
- Nunito Sans
- Source Sans 3

### Type Scale

| Text Type | Suggested Size | Usage |
|---|---:|---|
| Page title | 24–28px | Main screen heading |
| Section title | 18–20px | Card groups and sections |
| Body text | 15–16px | General content |
| Supporting text | 13–14px | Metadata and helper text |
| Badge text | 11–12px | Status indicators |
| Button text | 15–16px | Primary actions |

### Spacing

Use generous spacing on mobile.

| Item | Suggested Spacing |
|---|---:|
| Page padding | 16px |
| Card padding | 16px |
| Section gap | 20–24px |
| Button height | 48–52px |
| Input height | 48–52px |
| Card radius | 16–20px |
| Modal radius | 20–24px |

---

## 5. Mobile-First Layout Principles

### 5.1 Bottom Navigation

For mobile, bottom navigation is essential.

#### Employer Bottom Navigation

```text
Home | Search | Bookings | Messages | Profile
```

#### Helper Bottom Navigation

```text
Home | Requests | Jobs | Messages | Profile
```

Admin does not need mobile bottom navigation initially. Admin operations can be desktop/tablet-first.

### 5.2 Top Bar

Keep the top bar minimal.

Example:

```text
[MongiKazi Logo]                         [Bell Icon]
```

Optional greeting:

```text
Good morning, Zipho
```

Avoid placing too many controls in the top bar.

### 5.3 Cards Over Tables

For mobile user portals, use cards instead of tables.

Bad mobile pattern:

```text
Booking ID | Helper | Date | Status | Action
```

Better mobile pattern:

```text
Booking with Nomsa
Tomorrow, 08:00 – 14:00
Cleaning · Benoni
Status: Awaiting response

[View details]
```

Tables should mainly be used in the admin portal.

---

## 6. Website Design

The public website is the trust-building and conversion layer.

### 6.1 Website Purpose

The website should:

1. Explain what MongiKazi does.
2. Build trust.
3. Split users into the correct journey.
4. Convert employers and helpers into registered users.
5. Position the platform as safe, professional, and locally relevant.

### 6.2 Homepage Mobile Layout

```text
------------------------------------------------
MongiKazi Logo
------------------------------------------------

Find trusted help.
Get reliable work.

Book verified domestic workers and cleaners near you.

[ I need help ]
[ I want work ]

Verified profiles · Reviews · Safe bookings

------------------------------------------------
How it works
1. Choose what you need
2. View trusted helpers
3. Send a booking request
4. Confirm and review

------------------------------------------------
Popular services
[Cleaning] [Laundry] [Childcare] [Cooking]

------------------------------------------------
Why MongiKazi?
✓ Verified helpers
✓ Ratings and reviews
✓ Clear booking process
✓ Support when something goes wrong
------------------------------------------------
```

### 6.3 Website Core Pages

| Page | Purpose |
|---|---|
| Home | Explain value proposition and split employer/helper journeys |
| Find Help | Explain employer benefits and booking process |
| Find Work | Explain helper benefits and profile setup |
| How It Works | Explain process for both user types |
| Trust & Safety | Verification, ratings, reviews, support, safety rules |
| Pricing | Platform fees, commission model, payment expectations |
| About | Mission and platform story |
| Contact | Support and business enquiries |
| FAQs | Common questions |
| Terms & Privacy | Legal and platform policies |

### 6.4 Website Calls to Action

| CTA | Destination |
|---|---|
| I need help | Employer onboarding |
| I want work | Helper onboarding |
| Book a cleaner | Employer service selection |
| Become a helper | Helper profile setup |
| Contact us | General enquiry form |

### 6.5 Website Design Rule

The website should communicate **trust before transaction**.

The user should understand that MongiKazi is not merely a listing site, but a controlled marketplace with verification, reviews, bookings, and operational oversight.

---

## 7. Employer Portal Design

The Employer Portal should be action-driven, simple, and booking-focused.

### 7.1 Employer Home Screen

```text
Good morning, Zipho

What do you need today?

[ Once-off cleaning ]
[ Recurring help ]
[ Office cleaning ]
[ Laundry ]
[ Cooking ]

Upcoming booking
Nomsa M.
Tomorrow · 08:00
Status: Confirmed

[ View booking ]

Book again
[ Thandi N. ★ 4.8 ]
[ Rebook ]

Bottom Nav:
Home | Search | Bookings | Messages | Profile
```

### Key Principle

The employer home screen should answer:

1. What can I book?
2. What is already scheduled?
3. Can I rebook someone I trust?

---

### 7.2 Search Helpers Screen

```text
Find trusted help

Location: Benoni
Date: Today
Service: Cleaning

[ Filter ]

Available helpers

--------------------------------
[Photo] Nomsa M.       ★ 4.8
Verified Helper
3 years experience
Available today · 2.4 km away

[ View Profile ] [ Book ]
--------------------------------

[Photo] Thandi N.      ★ 4.7
ID Verified
5 years experience
Available tomorrow · 3.1 km away

[ View Profile ] [ Book ]
--------------------------------
```

### Helper Card Must Show

| Element | Why |
|---|---|
| Photo | Human trust |
| Name | Personal connection |
| Rating | Quality signal |
| Verification badge | Safety signal |
| Experience | Competence |
| Availability | Speed |
| Distance/location | Practicality |
| Book button | Conversion |

---

### 7.3 Helper Profile Screen

This screen should feel like a trusted digital CV.

```text
[Large photo]
Nomsa M.
★ 4.8 rating · 24 completed jobs

[Verified Badge]
ID verified · Criminal check uploaded

About
Reliable cleaner with 3 years of experience in household and office cleaning.

Skills
[Cleaning] [Laundry] [Cooking]

Experience
3 years

Availability
Today: Available
Tomorrow: Available

Reviews
“Very professional and punctual.”
- Employer review

[ Book Nomsa ]
[ Message ]
```

### Sticky CTA

The booking action should remain visible at the bottom.

```text
--------------------------------
Total estimate from R350
[ Book Now ]
--------------------------------
```

---

### 7.4 Booking Flow

The booking flow should feel Uber-like: short, clear, and guided.

#### Step 1: Select Service

```text
What do you need?

[ Cleaning ]
[ Laundry ]
[ Cooking ]
[ Childcare ]
```

#### Step 2: Select Date and Time

```text
When do you need help?

Date
[ Today ] [ Tomorrow ] [ Pick date ]

Start time
[ 08:00 ]

Duration
[ 4 hours ]
```

#### Step 3: Confirm Location

```text
Where should the helper come?

[ Use my saved location ]
[ Add new address ]

Special instructions
[ Text box ]
```

#### Step 4: Review Booking

```text
Booking Summary

Helper: Nomsa M.
Service: Cleaning
Date: Tomorrow
Time: 08:00 – 12:00
Location: Benoni

Estimated worker fee: R300
Platform fee: R50
Total estimate: R350

[ Send Booking Request ]
```

#### Booking Confirmation Screen

```text
Request sent

Nomsa has been notified.
You will receive a response once she accepts or declines.

[ View Booking ]
[ Find Another Helper ]
```

---

## 8. Helper Portal Design

The Helper Portal should be income-focused, confidence-building, and simple.

### 8.1 Helper Home Screen

```text
Good morning, Nomsa

Profile status
80% complete
[ Complete verification ]

Pending requests
2 new booking requests

[ View Requests ]

Today’s jobs
No jobs scheduled today

Weekly earnings
R750 completed this week

Bottom Nav:
Home | Requests | Jobs | Messages | Profile
```

### Key Principle

The helper home screen should answer:

1. Do I have work?
2. Do I need to respond to anything?
3. How much have I earned?
4. Is my profile strong enough?

---

### 8.2 Helper Profile Builder

This should feel like guided profile progress.

```text
Build your work profile

Profile completeness: 60%

✓ Basic details
✓ Profile photo
✓ Work categories
□ ID verification
□ Criminal record check
□ References
□ Availability

[ Continue Setup ]
```

Use progress indicators to encourage completion.

---

### 8.3 Booking Request Screen

```text
New Booking Request

Employer: Zipho L.
Service: Cleaning
Date: Tomorrow
Time: 08:00 – 12:00
Location: Benoni
Estimated pay: R300

Special instructions:
Please focus on kitchen and lounge.

[ Accept Booking ]
[ Decline ]
[ Message Employer ]
```

### Design Note

Make **Accept Booking** the primary action, but keep **Decline** visible and respectful. Helpers need control over their work.

---

### 8.4 My Jobs Screen

```text
My Jobs

Tabs:
[Upcoming] [Completed] [Cancelled]

Upcoming

Cleaning with Zipho L.
Tomorrow · 08:00 – 12:00
Benoni

[ View Details ]
```

---

### 8.5 Earnings Screen

For Phase 2, keep earnings simple.

```text
Earnings

This week
R750

This month
R2,400

Completed jobs
8

Pending payout
R500

Recent earnings
Cleaning · 3 May · R300
Laundry · 1 May · R250
Office cleaning · 29 Apr · R500
```

Avoid complex financial reporting at first.

---

## 9. Phase 2 Trust and Payment Screens

Phase 2 introduces verification, invoices, payment proof, and review flows.

### 9.1 Verification Centre

```text
Verification Centre

Become a verified helper to improve your chances of getting booked.

ID Document
Status: Pending review
[ Uploaded ]

Criminal Record Check
Status: Not uploaded
[ Upload ]

References
Status: Optional
[ Add reference ]

[ Submit for Review ]
```

### Verification Status Badges

| Status | Badge Style |
|---|---|
| Not uploaded | Grey |
| Uploaded | Neutral / blue-grey |
| Pending review | Amber |
| Approved | Green |
| Rejected | Red |

---

### 9.2 Employer Payment Screen

```text
Payment

Booking with Nomsa M.
Cleaning · 8 May

Worker fee: R300
Platform fee: R50
Total due: R350

Banking details
MongiKazi Pty Ltd
Bank: FNB
Account: ****1234
Reference: MK-000123

[ Upload Proof of Payment ]
```

### Payment Status Examples

```text
Status: Awaiting payment
```

After proof upload:

```text
Status: Proof uploaded. Awaiting verification.
```

---

### 9.3 Review Screen

Employer version:

```text
How was your booking with Nomsa?

★ ★ ★ ★ ★

What went well?
[ Punctual ] [ Professional ] [ Thorough ] [ Friendly ]

Add a comment
[ Text box ]

[ Submit Review ]
```

Helper version:

```text
How was your booking with Zipho?

★ ★ ★ ★ ★

[ Respectful ] [ Clear instructions ] [ Safe environment ] [ Paid on time ]

[ Submit Review ]
```

---

## 10. Admin / Operations Portal Design

Admin can be more desktop-focused, but it should still be responsive.

### 10.1 Admin Dashboard

```text
MongiKazi Operations

KPI Cards:
Pending Verifications: 14
Active Bookings: 32
Payment Proofs Pending: 8
Open Disputes: 2

Operational Queues:
- Helper verification queue
- Payment proof review
- Booking disputes
- Low-rated users
```

### 10.2 Verification Queue

Use tables here because admin users need structured review.

```text
Helper | Document Type | Uploaded Date | Status | Action
Nomsa M. | ID Document | 10 May | Pending | Review
Thandi N. | Criminal Check | 9 May | Pending | Review
```

### 10.3 Booking Operations

```text
Booking | Employer | Helper | Date | Status | Payment | Action
MK-000123 | Zipho | Nomsa | 12 May | Accepted | Awaiting POP | View
```

---

## 11. UI Component System

Reusable components should be defined early to keep the platform consistent.

### 11.1 Core Components

| Component | Used For |
|---|---|
| Service Card | Cleaning, laundry, cooking selections |
| Helper Card | Search results |
| Booking Card | Upcoming/completed bookings |
| Status Badge | Booking, payment, verification statuses |
| Trust Badge | Verified, top rated, new helper |
| Bottom Nav | Mobile navigation |
| Profile Completion Bar | Helper onboarding |
| Sticky CTA | Book now, accept booking, submit |
| Empty State Card | No bookings, no messages, no earnings yet |
| Review Stars | Ratings |
| Upload Card | Verification and POP uploads |
| Stepper | Guided onboarding and booking flow |
| Filter Sheet | Mobile-friendly helper search filters |
| Toast Notification | Short success/error messages |
| Alert Banner | Important status warnings |
| Timeline | Booking status history |

---

## 12. Mobile Design Rules

### 12.1 Button Rules

Use large, clear buttons.

```text
Minimum height: 44px
Preferred height: 48px–52px
```

Primary actions:

- Book Now
- Send Booking Request
- Accept Booking
- Upload Proof
- Submit Review

Secondary actions:

- Message
- Cancel
- Decline
- View details

### 12.2 Form Rules

Keep forms short.

Bad:

```text
One long form with 20 fields
```

Better:

```text
Step 1: Basic details
Step 2: Skills
Step 3: Verification
Step 4: Availability
```

For mobile:

- One question per section
- Large input fields
- Clear progress
- Save and continue later
- Avoid unnecessary typing
- Use cards, chips, and toggles where possible

### 12.3 Trust Signal Rules

Trust signals should appear everywhere decisions are made.

Show trust signals on:

- Helper cards
- Helper profiles
- Booking confirmation
- Employer profiles
- Admin review screens

Examples:

```text
ID Verified
Criminal Check Uploaded
4.8 Rating
24 Completed Jobs
Repeat Helper
```

### 12.4 Empty State Rules

Do not show blank pages.

Employer example:

```text
No bookings yet

When you send a booking request, it will appear here.

[ Find Helpers ]
```

Helper example:

```text
No job requests yet

Complete your profile and set your availability to improve your chances.

[ Complete Profile ]
```

---

## 13. Page Structure by Portal

### 13.1 Website

```text
/
 /how-it-works/
 /find-help/
 /find-work/
 /trust-safety/
 /pricing/
 /about/
 /contact/
 /faq/
```

### 13.2 Employer Portal

```text
/employer/
 /employer/search/
 /employer/helpers/<id>/
 /employer/bookings/
 /employer/bookings/<id>/
 /employer/messages/
 /employer/payments/
 /employer/favourites/
 /employer/profile/
```

### 13.3 Helper Portal

```text
/helper/
 /helper/profile/
 /helper/verification/
 /helper/availability/
 /helper/requests/
 /helper/jobs/
 /helper/jobs/<id>/
 /helper/messages/
 /helper/earnings/
 /helper/reviews/
```

### 13.4 Operations Portal

```text
/operations/
 /operations/verifications/
 /operations/bookings/
 /operations/payments/
 /operations/disputes/
 /operations/users/
 /operations/reports/
```

---

## 14. Phase 1 UI Priorities

Focus on the basic marketplace loop.

### Phase 1 Screens

1. Website landing page
2. Role selection
3. Registration / login
4. Helper onboarding
5. Employer onboarding
6. Employer home
7. Helper home
8. Search helpers
9. Helper profile
10. Booking request
11. Helper accept/decline
12. Booking detail
13. Basic messages
14. Basic review screen

### Phase 1 Design Objective

Make it possible for:

```text
Employer registers
    ↓
Finds helper
    ↓
Sends booking request
    ↓
Helper accepts
    ↓
Booking is completed
    ↓
Employer reviews helper
```

---

## 15. Phase 2 UI Priorities

Focus on trust, operations, and payment handling.

### Phase 2 Screens

1. Verification centre
2. Admin verification queue
3. Verification review detail
4. Payment / invoice screen
5. POP upload screen
6. Admin payment proof review
7. Review and rating flow
8. Helper earnings summary
9. Booking status timeline
10. Admin operations dashboard

### Phase 2 Design Objective

Make the platform feel controlled, auditable, and trustworthy.

```text
Verification
    ↓
Booking audit trail
    ↓
Payment proof
    ↓
Review system
    ↓
Admin oversight
```

---

## 16. Overall UX Recommendation

For Phase 1 and 2, avoid complex marketplace UI. Focus on a guided experience.

The app should not feel like:

```text
Here are 100 helpers, figure it out.
```

It should feel like:

```text
Tell us what you need.
Here are the best available helpers.
Send a request.
Track everything clearly.
```

This is the right experience for trust, speed, and mobile usability.

---

## 17. Final Design Positioning

MongiKazi should look and feel like a serious platform from day one.

The design should communicate:

1. This is safe.
2. This is organised.
3. This is easy to use.
4. This is professional.
5. This can be trusted with real people, real homes, real work, and real payments.

The winning design direction is:

```text
Airbnb-style trust and profile browsing
+
Uber-style fast booking
+
Fintech-grade status clarity and payment confidence
+
Mobile-first simplicity for the South African market
```

---

## 18. Tailwind and Portal Base Template Strategy

MongiKazi should use **Tailwind CSS** as the primary UI framework because the product needs a custom, mobile-first, high-end interface rather than a generic admin-style layout.

The platform should also use **separate base templates per portal**. This allows the public website, employer portal, helper portal, and operations portal to feel connected through the same brand system while still supporting different user journeys.

### 18.1 Recommended Base Template Structure

```text
templates/
│
├── base/
│   ├── base_public.html
│   ├── base_auth.html
│   ├── base_employer.html
│   ├── base_helper.html
│   └── base_operations.html
│
├── components/
│   ├── mobile_header.html
│   ├── public_navbar.html
│   ├── public_footer.html
│   ├── employer_bottom_nav.html
│   ├── helper_bottom_nav.html
│   ├── operations_sidebar.html
│   ├── operations_topbar.html
│   ├── buttons.html
│   ├── cards.html
│   ├── badges.html
│   ├── forms.html
│   ├── empty_state.html
│   ├── trust_badge.html
│   ├── status_badge.html
│   ├── helper_card.html
│   ├── booking_card.html
│   ├── service_card.html
│   ├── upload_card.html
│   ├── page_header.html
│   └── sticky_cta.html
│
├── website/
│   ├── home.html
│   ├── find_help.html
│   ├── find_work.html
│   ├── how_it_works.html
│   ├── trust_safety.html
│   ├── pricing.html
│   ├── about.html
│   ├── contact.html
│   └── faq.html
│
├── employer_portal/
│   ├── dashboard.html
│   ├── search_helpers.html
│   ├── helper_detail.html
│   ├── booking_create.html
│   ├── booking_detail.html
│   ├── bookings.html
│   ├── messages.html
│   ├── payments.html
│   ├── favourites.html
│   └── profile.html
│
├── helper_portal/
│   ├── dashboard.html
│   ├── profile_builder.html
│   ├── verification.html
│   ├── availability.html
│   ├── requests.html
│   ├── jobs.html
│   ├── job_detail.html
│   ├── messages.html
│   ├── earnings.html
│   └── reviews.html
│
└── operations/
    ├── dashboard.html
    ├── verifications.html
    ├── verification_detail.html
    ├── bookings.html
    ├── booking_detail.html
    ├── payments.html
    ├── payment_detail.html
    ├── disputes.html
    ├── users.html
    └── reports.html
```

### 18.2 Purpose of Each Base Template

| Base Template | Purpose | Design Feel |
|---|---|---|
| `base_public.html` | Public website and marketing pages | Polished startup website |
| `base_auth.html` | Login, registration, OTP, role selection, password reset | Clean, focused, low distraction |
| `base_employer.html` | Employer portal | Mobile booking app |
| `base_helper.html` | Helper / worker portal | Work, profile, and earnings app |
| `base_operations.html` | Admin / operations portal | Fintech-grade operations dashboard |

### 18.3 Why Separate Base Templates Matter

Avoid this structure:

```text
One base template trying to support:
public website + employer app + helper app + admin dashboard
```

That creates clutter and weakens the user experience.

Use this structure instead:

```text
Shared design system
    ↓
Shared reusable components
    ↓
Portal-specific base templates
    ↓
Portal-specific pages
```

This gives MongiKazi:

1. One consistent brand.
2. Different portal experiences.
3. Cleaner Django templates.
4. Easier long-term maintenance.
5. Better mobile-first usability.

---

## 19. Tailwind CSS Implementation Standard

### 19.1 Why Tailwind Is Recommended

Tailwind is the right fit for MongiKazi because the platform needs:

| Requirement | Why Tailwind Helps |
|---|---|
| Mobile-first design | Responsive utilities make mobile layouts easier |
| High-end custom UI | Avoids generic Bootstrap-style output |
| Consistent spacing | Utility classes enforce design rhythm |
| Reusable component styling | Cards, badges, buttons, navs, and CTAs can be standardised |
| Fast iteration | UI can be refined quickly during MVP |
| Brand control | Colours and tokens can be configured centrally |
| Portal flexibility | Each portal can share the same system but use different layouts |

Tailwind supports the intended product feel:

```text
Airbnb-style profile browsing
+
Uber-style booking simplicity
+
Fintech-grade status and payment clarity
```

### 19.2 Tailwind Setup Recommendation

For early prototyping, Tailwind CDN can be used temporarily:

```html
<script src="https://cdn.tailwindcss.com"></script>
```

However, the production-ready approach should use a proper Tailwind build pipeline.

Recommended structure:

```text
theme/
├── static_src/
│   └── input.css
├── static/
│   └── css/
│       └── app.css
├── tailwind.config.js
└── package.json
```

Compiled CSS should be referenced from Django templates:

```html
<link rel="stylesheet" href="{% static 'css/app.css' %}">
```

### 19.3 Tailwind Configuration

Recommended `tailwind.config.js`:

```javascript
module.exports = {
  content: [
    "./templates/**/*.html",
    "./**/templates/**/*.html",
    "./**/*.py",
  ],
  theme: {
    extend: {
      colors: {
        mk: {
          primary: "#0F766E",
          primaryDark: "#0B4F4A",
          secondary: "#F4EFE7",
          accent: "#D9A441",
          bg: "#FAFAF7",
          surface: "#FFFFFF",
          text: "#1F2933",
          muted: "#6B7280",
          border: "#E5E7EB",
          success: "#15803D",
          warning: "#B45309",
          danger: "#B91C1C",
        },
      },
      borderRadius: {
        "mk-card": "1.25rem",
        "mk-button": "0.875rem",
      },
      boxShadow: {
        "mk-card": "0 12px 30px rgba(15, 23, 42, 0.08)",
        "mk-soft": "0 8px 20px rgba(15, 23, 42, 0.06)",
      },
      fontFamily: {
        sans: ["Inter", "ui-sans-serif", "system-ui", "sans-serif"],
      },
    },
  },
  plugins: [],
};
```

### 19.4 Global CSS Entry File

Recommended `static_src/input.css`:

```css
@tailwind base;
@tailwind components;
@tailwind utilities;

@layer components {
  .mk-card {
    @apply rounded-mk-card bg-white shadow-mk-soft border border-mk-border;
  }

  .mk-btn-primary {
    @apply inline-flex items-center justify-center rounded-mk-button bg-mk-primary px-4 py-3 text-sm font-semibold text-white shadow-sm transition hover:bg-mk-primaryDark;
  }

  .mk-btn-secondary {
    @apply inline-flex items-center justify-center rounded-mk-button border border-mk-primary bg-white px-4 py-3 text-sm font-semibold text-mk-primary transition hover:bg-mk-secondary;
  }

  .mk-input {
    @apply w-full rounded-xl border border-mk-border bg-white px-4 py-3 text-sm text-mk-text outline-none focus:border-mk-primary focus:ring-2 focus:ring-mk-primary/20;
  }

  .mk-badge-success {
    @apply inline-flex items-center rounded-full bg-green-50 px-2.5 py-1 text-xs font-semibold text-mk-success;
  }

  .mk-badge-warning {
    @apply inline-flex items-center rounded-full bg-amber-50 px-2.5 py-1 text-xs font-semibold text-mk-warning;
  }

  .mk-badge-danger {
    @apply inline-flex items-center rounded-full bg-red-50 px-2.5 py-1 text-xs font-semibold text-mk-danger;
  }
}
```

This keeps common design treatment consistent without writing long Tailwind class strings repeatedly.

---

## 20. Base Template Examples

### 20.1 `base_public.html`

```html
{% load static %}
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />

  <title>{% block title %}MongiKazi{% endblock %}</title>
  <meta name="description" content="{% block meta_description %}Find trusted help or get reliable work with MongiKazi.{% endblock %}">

  <link rel="stylesheet" href="{% static 'css/app.css' %}">
  {% block extra_css %}{% endblock %}
</head>

<body class="min-h-screen bg-mk-bg text-mk-text font-sans">

  {% include "components/public_navbar.html" %}

  <main>
    {% block content %}{% endblock %}
  </main>

  {% include "components/public_footer.html" %}

  {% block extra_js %}{% endblock %}
</body>
</html>
```

### 20.2 `base_auth.html`

```html
{% load static %}
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />

  <title>{% block title %}MongiKazi Account{% endblock %}</title>

  <link rel="stylesheet" href="{% static 'css/app.css' %}">
  {% block extra_css %}{% endblock %}
</head>

<body class="min-h-screen bg-mk-bg text-mk-text font-sans">

  <main class="flex min-h-screen items-center justify-center px-4 py-8">
    <section class="w-full max-w-md">
      <div class="mb-6 text-center">
        <img src="{% static 'img/logo.png' %}" alt="MongiKazi" class="mx-auto h-10 w-auto">
      </div>

      <div class="mk-card p-5">
        {% block content %}{% endblock %}
      </div>
    </section>
  </main>

  {% block extra_js %}{% endblock %}
</body>
</html>
```

### 20.3 `base_employer.html`

```html
{% load static %}
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />

  <title>{% block title %}MongiKazi Employer{% endblock %}</title>

  <link rel="stylesheet" href="{% static 'css/app.css' %}">
  {% block extra_css %}{% endblock %}
</head>

<body class="min-h-screen bg-mk-bg text-mk-text font-sans">

  <div class="min-h-screen pb-20">

    {% include "components/mobile_header.html" %}

    <main class="mx-auto max-w-md px-4 py-4">
      {% block content %}{% endblock %}
    </main>

    {% include "components/employer_bottom_nav.html" %}

  </div>

  {% block sticky_cta %}{% endblock %}
  {% block extra_js %}{% endblock %}
</body>
</html>
```

### 20.4 `base_helper.html`

```html
{% load static %}
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />

  <title>{% block title %}MongiKazi Helper{% endblock %}</title>

  <link rel="stylesheet" href="{% static 'css/app.css' %}">
  {% block extra_css %}{% endblock %}
</head>

<body class="min-h-screen bg-mk-bg text-mk-text font-sans">

  <div class="min-h-screen pb-20">

    {% include "components/mobile_header.html" %}

    <main class="mx-auto max-w-md px-4 py-4">
      {% block content %}{% endblock %}
    </main>

    {% include "components/helper_bottom_nav.html" %}

  </div>

  {% block sticky_cta %}{% endblock %}
  {% block extra_js %}{% endblock %}
</body>
</html>
```

### 20.5 `base_operations.html`

```html
{% load static %}
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />

  <title>{% block title %}MongiKazi Operations{% endblock %}</title>

  <link rel="stylesheet" href="{% static 'css/app.css' %}">
  {% block extra_css %}{% endblock %}
</head>

<body class="min-h-screen bg-slate-50 text-slate-900 font-sans">

  <div class="min-h-screen lg:flex">

    <aside class="hidden lg:block lg:w-72 bg-mk-primaryDark text-white">
      {% include "components/operations_sidebar.html" %}
    </aside>

    <div class="min-w-0 flex-1">
      {% include "components/operations_topbar.html" %}

      <main class="p-4 lg:p-8">
        {% block content %}{% endblock %}
      </main>
    </div>

  </div>

  {% block extra_js %}{% endblock %}
</body>
</html>
```

---

## 21. Portal Layout Differences

### 21.1 Website Layout

```text
Public marketing layout
Full-width hero
Public navbar
Conversion CTAs
Trust sections
Footer
```

### 21.2 Employer Portal Layout

```text
Mobile app layout
Bottom navigation
Quick booking cards
Search-first experience
Sticky booking CTAs
Booking and payment clarity
```

### 21.3 Helper Portal Layout

```text
Mobile app layout
Bottom navigation
Profile progress
Booking request queue
Earnings and job cards
Verification prompts
```

### 21.4 Operations Portal Layout

```text
Desktop-first dashboard layout
Sidebar navigation
KPI cards
Tables
Filters
Queues
Action review screens
```

The employer and helper portals should feel like mobile apps. The operations portal should feel like a fintech admin console.

---

## 22. Shared Component Philosophy

Even with separate base templates, MongiKazi should have shared components so the product feels unified.

### 22.1 Shared Component Rules

1. Components should use Tailwind classes or project-level component classes.
2. Components should avoid hardcoded business logic.
3. Components should accept context variables from the view.
4. Components should be reusable across portals where possible.
5. Status and badge styling should be centralised to avoid inconsistent colours.

### 22.2 Example Component Usage

```django
{% include "components/helper_card.html" with helper=helper %}
```

```django
{% include "components/status_badge.html" with status=booking.status %}
```

```django
{% include "components/empty_state.html" with title="No bookings yet" action_label="Find Helpers" %}
```

### 22.3 Components to Build Early

```text
1. mobile_header.html
2. employer_bottom_nav.html
3. helper_bottom_nav.html
4. status_badge.html
5. trust_badge.html
6. helper_card.html
7. booking_card.html
8. service_card.html
9. empty_state.html
10. upload_card.html
11. sticky_cta.html
12. page_header.html
13. alert_banner.html
14. review_stars.html
```

---

## 23. UI Implementation Order for Phase 1 and Phase 2

Build the UI foundation before building too many individual pages.

```text
1. Tailwind setup and theme tokens
2. Global CSS component classes
3. Shared components folder
4. base_auth.html
5. base_public.html
6. Public website landing page
7. Role selection and registration screens
8. base_employer.html
9. Employer dashboard
10. Helper search and helper profile screens
11. Booking flow screens
12. base_helper.html
13. Helper dashboard
14. Booking request screen
15. Verification centre
16. base_operations.html
17. Admin verification queue
18. Payment proof review
19. Booking operations dashboard
20. Review and rating flow
```

This order creates a clean design foundation and prevents each page from becoming a one-off design.

---

## 24. Final UI Architecture Recommendation

MongiKazi should follow this UI architecture:

```text
Tailwind design system
    ↓
Shared UI components
    ↓
Portal-specific base templates
    ↓
Portal-specific pages
```

The final design approach should be:

```text
One brand
One design system
Multiple portal experiences
```

This gives the platform the right balance:

```text
Airbnb/Uber mobile experience
+
Fintech-grade visual consistency
+
Django maintainability
+
Portal-specific usability
```

