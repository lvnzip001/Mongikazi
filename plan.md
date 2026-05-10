# MongiKazi Development Plan

## Project Overview

**MongiKazi** is a two-sided marketplace platform connecting employers/households with verified domestic workers in South Africa. The platform is built on Django 6.0.5 with Tailwind CSS for a mobile-first, trust-driven user experience.

### Platform Value Proposition
- **For Employers**: Find and book trusted, verified domestic workers within 60 seconds
- **For Helpers**: Get verified, visible, and receive consistent work opportunities with digital reputation building
- **For Platform**: Build trust infrastructure for domestic work with verification, payments, and dispute resolution

### Core Brand Pillars
1. **Trust** - ID verification, reference checks, ratings, audit trails
2. **Speed** - Quick booking flow, easy rebooking of trusted helpers
3. **Fairness** - Workers build digital reputation, transparent pricing
4. **Scalability** - Start simple, add features iteratively

---

## Technical Stack

| Layer | Technology |
|-------|-----------|
| **Backend** | Django 6.0.5, Python 3.x |
| **Frontend** | Tailwind CSS, HTML5, JavaScript (mobile-first) |
| **Database** | SQLite (dev), PostgreSQL (production) |
| **Architecture** | Multi-app Django structure with role-based portals |
| **Package Manager** | pip (Python), npm (Frontend assets) |

### Current Project Structure
```
mongikazi/
├── accounts/          # Authentication, roles, registration
├── website/           # Public website + portals
├── mysite/            # Django project settings
├── manage.py          # Django CLI
└── db.sqlite3         # Development database
```

---

## Design System

### Brand Personality
- **Feel**: Clean, trustworthy, friendly, fast, local, professional
- **Tone**: Warm, safe, reliable, modern, simple, empowering
- **Design Principle**: Users understand what to do in 3 seconds, complete actions in 3–5 taps

### Color Palette
```css
--mk-primary: #0F766E;           /* Deep Teal - Trust, work, reliability */
--mk-primary-dark: #0B4F4A;      /* Dark Teal - Headers, navigation */
--mk-secondary: #F4EFE7;         /* Warm Beige - Human, accessible */
--mk-accent: #D9A441;            /* Gold - Ratings, highlights */
--mk-bg: #FAFAF7;                /* Off-white - Mobile background */
--mk-surface: #FFFFFF;           /* White - Cards, forms */
--mk-text: #1F2933;              /* Charcoal - Primary text */
--mk-muted: #6B7280;             /* Grey - Secondary text */
--mk-border: #E5E7EB;            /* Light Grey - Borders */
--mk-success: #15803D;           /* Green - Success states */
--mk-warning: #B45309;           /* Amber - Warning states */
--mk-danger: #B91C1C;            /* Red - Error states */
```

### Design Inspiration
- **Uber**: Simple booking, location-first, fast action
- **Airbnb**: Profile trust, reviews, human-centered browsing
- **Fintech Apps**: Clean hierarchy, status clarity, payment confidence
- **LinkedIn**: Professional profiles with credibility

---

## Core Platform Modules

### 1. Accounts & Roles
**Purpose**: Manage user authentication, roles, and role-based redirects

**User Roles**:
- **Employer**: Households, businesses finding and booking helpers
- **Helper**: Domestic workers, cleaners offering services
- **Admin**: Platform operators managing verification and disputes
- **Operator**: Support staff handling customer issues

**Key Features**:
- Multi-role user registration
- Role selection during signup
- Post-login redirect to appropriate portal
- Account pending state for verification
- Role-specific dashboard access

**Database Models**:
- `User` (extends Django User)
- `UserProfile` (role, verification status, metadata)
- `UserRole` (role assignments)
- `VerificationStatus` (ID verified, reference checked, etc.)

---

### 2. Helper Profiles & Verification
**Purpose**: Build digital profiles for domestic workers with verification and trust indicators

**Key Features**:
- Helper bio, skills, experience, hourly rate
- Availability calendar
- Verification badges (ID verified, background check, reference checked)
- Rating and review score
- Service categories (cleaning, childcare, cooking, etc.)
- Work experience and employment history
- Profile photos with verification

**Database Models**:
- `HelperProfile`
- `HelperSkills`
- `HelperAvailability`
- `VerificationBadge`
- `ServiceCategory`

**Portal Views**:
- Profile setup and editing
- Availability management
- Skill selection
- Earnings and statistics

---

### 3. Employer Profiles
**Purpose**: Store employer information, locations, and preferences

**Key Features**:
- Employer information (name, contact, location)
- Multiple service locations
- Preferences (helper skills needed, price range, availability)
- Booking history
- Favourite helpers list
- Payment methods

**Database Models**:
- `EmployerProfile`
- `ServiceLocation`
- `EmployerPreferences`

**Portal Views**:
- Profile management
- Location setup
- Preference configuration

---

### 4. Search & Matching
**Purpose**: Enable employers to find helpers efficiently

**Key Features**:
- Filter by location/radius (GPS)
- Filter by skills and service categories
- Filter by rating/review score
- Filter by verification status
- Filter by availability
- Filter by hourly rate/price range
- Sort by rating, distance, availability
- Full-text search on helper profiles

**Database Queries**:
- Location-based radius search
- Multi-filter aggregation
- Sorting and pagination

---

### 5. Bookings
**Purpose**: Manage the complete booking lifecycle

**Booking Workflow**:
1. **Employer creates booking request** - Date, time, location, description, budget
2. **Helper receives notification** - Views request details
3. **Helper accepts or declines** - Request moves to acceptance or returns to search
4. **Confirmed** - Booking confirmed, messaging enabled
5. **Completed** - Booking marked complete by either party
6. **Reviewed** - Helper and employer can rate/review each other

**Booking States**:
- `REQUESTED` - Awaiting helper response
- `ACCEPTED` - Helper accepted, employer can cancel
- `DECLINED` - Helper declined
- `CONFIRMED` - Both parties confirmed
- `STARTED` - Work in progress
- `COMPLETED` - Work finished
- `CANCELLED` - Either party cancelled
- `DISPUTED` - Dispute raised

**Key Features**:
- Real-time booking status updates
- SMS/email notifications
- Automatic timeout for pending requests
- Cancellation policies
- Dispute tracking

**Database Models**:
- `Booking`
- `BookingMessage`
- `BookingStatus` (audit trail)

---

### 6. Messaging
**Purpose**: Enable direct communication between employer and helper

**Key Features**:
- Private chat after booking confirmation
- Message history
- Attachment support (photos, documents)
- Read receipts
- Message notifications

**Database Models**:
- `Message`
- `MessageThread`

---

### 7. Reviews & Ratings
**Purpose**: Build trust through peer ratings and reviews

**Key Features**:
- 5-star rating system
- Written reviews
- Rating breakdown (communication, reliability, professionalism)
- Helper average rating display
- Employer rating (reliability, communication)
- Review moderation

**Database Models**:
- `Review`
- `Rating`
- `ReviewModeration`

---

### 8. Payments & Invoicing
**Purpose**: Track payments and manage platform commission

**Key Features**:
- Invoice generation after booking
- Proof of payment upload
- Payment status tracking
- Commission calculation
- Payment history
- Manual payment tracking (MPESA, bank transfer, cash)

**Database Models**:
- `Invoice`
- `Payment`
- `PaymentProof`

---

### 9. Notifications
**Purpose**: Keep users informed of important events

**Notification Types**:
- Booking requests
- Booking accepted/declined
- Messages received
- Payment reminders
- Verification updates
- Reviews received
- Support tickets

**Channels**:
- In-app notifications
- Email
- SMS (future)
- WhatsApp (future)

---

### 10. Admin Operations
**Purpose**: Platform operations and quality control

**Key Features**:
- User verification dashboard
- Dispute resolution interface
- Booking oversight
- Quality control metrics
- Feature flags
- Support ticket management
- Analytics dashboard

---

### 11. Analytics
**Purpose**: Track platform growth and health

**Metrics**:
- Active users (employers, helpers)
- Booking volume and success rate
- Average helper earnings
- Employer retention
- Platform commission revenue
- Verification completion rate
- User geographic distribution
- Rating trends

---

## User Journey Maps

### Employer Journey (Simplified)

```
1. DISCOVER → Visit public website (home.html)
   ↓
2. UNDERSTAND → Read Find Help, How It Works, Trust & Safety
   ↓
3. SIGN UP → Click "I need help" → Register → Verify email → Set up profile
   ↓
4. SEARCH → Go to portal → Search helpers by location, skills, rating
   ↓
5. BROWSE → View helper profiles, read reviews, check verification
   ↓
6. BOOK → Create booking → Select date, time, description → Submit
   ↓
7. WAIT → Helper accepts or declines → Receive notification
   ↓
8. CONFIRM → Once helper accepts, booking is confirmed → Chat opens
   ↓
9. PAYMENT → After service, upload proof of payment or mark complete
   ↓
10. REVIEW → Rate helper → Write review → Complete booking
   ↓
11. REBOOK → Option to rebook same helper or search new ones
```

### Helper Journey (Simplified)

```
1. DISCOVER → Visit public website (home.html)
   ↓
2. UNDERSTAND → Read Find Work, How It Works, Trust & Safety
   ↓
3. SIGN UP → Click "I want work" → Register → Verify email
   ↓
4. PROFILE SETUP → Add bio, skills, rate, photos → Start verification
   ↓
5. VERIFICATION → Complete ID check, reference check (admin approves)
   ↓
6. AVAILABILITY → Set working hours and preferred locations
   ↓
7. WAIT → Bookings come in as notifications
   ↓
8. RESPOND → Accept or decline booking requests
   ↓
9. CHAT → Once accepted, message employer about details
   ↓
10. WORK → Perform the service
   ↓
11. COMPLETE → Mark booking complete → Receive payment
   ↓
12. REVIEW → Employer rates you → See feedback → Build reputation
   ↓
13. REPEAT → Rebook with returning employers or accept new bookings
```

---

## Website Structure

### Public Website Pages

| Page | URL | Purpose |
|------|-----|---------|
| Home | `/` | Value prop, hero CTA, platform overview |
| Find Help | `/find-help/` | Employer benefits, how booking works, trust features |
| Find Work | `/find-work/` | Helper benefits, earnings potential, verification process |
| How It Works | `/how-it-works/` | Full employer and helper workflows illustrated |
| Trust & Safety | `/trust-safety/` | Verification, ratings, identity checks, safety rules |
| Pricing | `/pricing/` | Booking fees, commissions, service pricing model |
| About | `/about/` | MongiKazi mission, team, market problem |
| Contact | `/contact/` | Support enquiry form, partnerships |
| FAQs | `/faqs/` | Common employer and helper questions |
| Business | `/business/` | B2B positioning for office cleaning contracts |
| Portals Entry | `/portals/` | Links to employer portal, helper portal, admin |
| Terms & Privacy | `/terms/`, `/privacy/` | Legal policies |

### Authentication Pages

| Page | URL | Purpose |
|------|-----|---------|
| Login | `/accounts/login/` | User login |
| Register | `/accounts/register/` | Initial registration |
| Role Select | `/accounts/role-select/` | Choose Employer or Helper |
| Account Pending | `/accounts/pending/` | Verification in progress |

### Portal Pages (Authenticated)

#### Employer Portal
| Feature | URL | Purpose |
|---------|-----|---------|
| Dashboard | `/employer/dashboard/` | Overview, upcoming bookings, CTA |
| Search Helpers | `/employer/search/` | Search interface with filters |
| Helper Profile | `/employer/helpers/{id}/` | View helper details, reviews |
| Create Booking | `/employer/bookings/new/` | Booking form |
| Manage Bookings | `/employer/bookings/` | View all bookings, status |
| Favourite Helpers | `/employer/favourites/` | Saved helpers for quick rebook |
| Messages | `/employer/messages/` | Chat with helpers |
| Payments | `/employer/payments/` | Invoices, proof of payment |
| Reviews | `/employer/reviews/` | Rate helpers after booking |
| Profile | `/employer/profile/` | Account settings, locations |

#### Helper Portal
| Feature | URL | Purpose |
|---------|-----|---------|
| Dashboard | `/helper/dashboard/` | Incoming bookings, earnings |
| Profile | `/helper/profile/` | Bio, skills, rate, verification |
| Availability | `/helper/availability/` | Working hours, locations |
| Bookings | `/helper/bookings/` | Pending, accepted, completed |
| Earnings | `/helper/earnings/` | Total earned, payment tracking |
| Messages | `/helper/messages/` | Chat with employers |
| Reviews | `/helper/reviews/` | Ratings and feedback received |
| Settings | `/helper/settings/` | Account, preferences |

#### Admin Portal
| Feature | URL | Purpose |
|---------|-----|---------|
| Dashboard | `/admin/` | Overview, metrics, alerts |
| Verification | `/admin/verification/` | Approve/reject user verifications |
| Disputes | `/admin/disputes/` | Resolve booking disputes |
| Bookings | `/admin/bookings/` | Monitor all bookings |
| Users | `/admin/users/` | Manage user accounts |
| Analytics | `/admin/analytics/` | Growth, revenue, retention metrics |

---

## Development Roadmap

### Phase 1: Foundation (Weeks 1-2)
**Goals**: Set up core authentication and website

**Tasks**:
- [ ] Configure Tailwind CSS in Django
- [ ] Create Employer, Helper, Admin user roles
- [ ] Build registration service with role selection
- [ ] Build redirect service for post-login routing
- [ ] Create account pending state
- [ ] Build base templates (base_public.html, base_auth.html)
- [ ] Build all public website pages (home, find-help, find-work, etc.)
- [ ] Setup responsive mobile-first layout
- [ ] Create component library (buttons, cards, badges, forms)

**Database Schema**:
- User model with role system
- UserProfile with role and status
- VerificationStatus tracking

**Success Criteria**:
- Registration works with role selection
- Post-login redirect to correct portal
- All public pages responsive on mobile/tablet/desktop
- Design system properly applied

---

### Phase 2: Trust Infrastructure (Weeks 3-4)
**Goals**: Build helper profiles and verification system

**Tasks**:
- [ ] Create HelperProfile model (bio, skills, rate, availability)
- [ ] Create ServiceCategory model
- [ ] Create VerificationBadge system
- [ ] Build helper profile editor (portal)
- [ ] Build availability calendar
- [ ] Create verification dashboard (admin)
- [ ] Build verification badge display on helper profiles
- [ ] Create rating/review models
- [ ] Build review submission form

**Database Schema**:
- HelperProfile
- HelperSkills
- HelperAvailability
- ServiceCategory
- VerificationBadge
- Review
- Rating

**Success Criteria**:
- Helpers can create and edit profiles
- Admin can verify and approve helpers
- Verification badges display on profiles
- Rating system tracks 5-star scores

---

### Phase 3: Employer & Search (Weeks 5-6)
**Goals**: Enable employer search and filtering

**Tasks**:
- [ ] Create EmployerProfile model
- [ ] Create employer profile editor
- [ ] Build helper search interface with filters
- [ ] Implement location-based filtering
- [ ] Implement skill-based filtering
- [ ] Implement rating-based filtering
- [ ] Add sorting options
- [ ] Build helper detail/preview pages
- [ ] Add favourite helpers feature

**Database Schema**:
- EmployerProfile
- ServiceLocation
- EmployerPreferences
- FavouriteHelper

**Success Criteria**:
- Employers can search helpers by multiple criteria
- Search results show verification badges and ratings
- Can add helpers to favourites
- Mobile search interface is intuitive

---

### Phase 4: Booking System (Weeks 7-9)
**Goals**: Implement complete booking workflow

**Tasks**:
- [ ] Create Booking model with state machine
- [ ] Build booking request form
- [ ] Build booking acceptance/decline interface
- [ ] Create booking status tracking
- [ ] Build booking history/list views
- [ ] Implement booking notifications
- [ ] Build booking cancellation flow
- [ ] Create booking timeline view
- [ ] Implement dispute system basics

**Database Schema**:
- Booking with state field
- BookingStatus (audit trail)
- BookingMessage (associated messages)

**Success Criteria**:
- Employers can create booking requests
- Helpers receive notifications and can accept/decline
- Booking status updates are tracked
- Users can view booking history

---

### Phase 5: Messaging & Communication (Weeks 10-11)
**Goals**: Enable real-time employer-helper communication

**Tasks**:
- [ ] Create Message model
- [ ] Build messaging interface
- [ ] Implement message notifications
- [ ] Build message thread view
- [ ] Add read receipts
- [ ] Create in-app notification system
- [ ] Setup notification preferences

**Database Schema**:
- Message
- MessageThread
- InAppNotification

**Success Criteria**:
- Users can message after booking confirmation
- Messages load quickly
- Notifications alert users to new messages
- Message history is persistent

---

### Phase 6: Payments & Invoicing (Weeks 12-13)
**Goals**: Track payments and manage invoices

**Tasks**:
- [ ] Create Invoice model
- [ ] Create Payment model
- [ ] Build invoice generation after booking completion
- [ ] Build proof of payment upload
- [ ] Create payment status tracking views
- [ ] Build invoice history
- [ ] Create payment reminders
- [ ] Build helper earnings view
- [ ] Implement commission calculation

**Database Schema**:
- Invoice
- Payment
- PaymentProof

**Success Criteria**:
- Invoices auto-generate after booking completion
- Users can upload payment proof
- Payment status is tracked accurately
- Helpers can view their earnings

---

### Phase 7: Admin & Moderation (Weeks 14-15)
**Goals**: Build admin interfaces for operations

**Tasks**:
- [ ] Create admin verification dashboard
- [ ] Build dispute resolution interface
- [ ] Create quality control metrics
- [ ] Build user management interface
- [ ] Create feature flag system
- [ ] Build support ticket system
- [ ] Create admin-only reporting views

**Database Schema**:
- DisputeTicket
- SupportTicket
- AdminAction (audit log)

**Success Criteria**:
- Admin can verify users efficiently
- Disputes can be tracked and resolved
- Quality metrics are visible
- User management is streamlined

---

### Phase 8: Analytics & Reporting (Weeks 16-17)
**Goals**: Build insights and metrics

**Tasks**:
- [ ] Create analytics dashboard
- [ ] Build growth metrics views
- [ ] Create revenue/commission tracking
- [ ] Build user cohort analysis
- [ ] Create booking success rate metrics
- [ ] Build geographic heatmaps
- [ ] Create export functionality

**Success Criteria**:
- Admin can see key platform metrics
- Growth trends are visible
- Revenue is tracked accurately
- Data can be exported for analysis

---

### Phase 9: Mobile Optimization & Polish (Weeks 18-19)
**Goals**: Refine UX across all devices

**Tasks**:
- [ ] Audit mobile responsiveness
- [ ] Optimize form inputs for mobile
- [ ] Test on actual devices
- [ ] Performance optimization
- [ ] Accessibility audit
- [ ] Error message review
- [ ] Help/documentation review

**Success Criteria**:
- All pages work seamlessly on mobile
- Forms are optimized for touch
- Load times are acceptable
- Accessibility standards met

---

### Phase 10: Launch Preparation (Weeks 20+)
**Goals**: Prepare for production deployment

**Tasks**:
- [ ] Security audit
- [ ] Switch to PostgreSQL
- [ ] Setup production settings
- [ ] Configure email/SMS providers
- [ ] Setup error tracking
- [ ] Create backup procedures
- [ ] Setup monitoring/alerts
- [ ] Create deployment playbook
- [ ] User documentation
- [ ] Admin onboarding materials

---

## Key Technical Decisions

### Architecture Patterns
- **Service Layer**: Business logic lives in `services/` modules
- **Selector Pattern**: Complex queries in optional `selectors/` (vs. model methods)
- **Django ORM**: Used for all database access, no raw SQL
- **Template Inheritance**: Base templates for consistent structure
- **Form Validation**: Validation done in forms before model save

### Security Considerations
- Role-based access control on all views
- CSRF protection on all forms
- SQL injection prevention via ORM
- XSS prevention with template escaping
- Password hashing with Django defaults
- HTTPS required in production

### Performance Considerations
- Database indexing on frequently filtered fields (location, rating)
- Query optimization with select_related/prefetch_related
- Caching for helper search results
- Static file optimization with Tailwind compression
- Pagination on list views

### Scalability Path
1. **Start**: SQLite, single Django instance
2. **Growth**: PostgreSQL, Gunicorn + Nginx
3. **Scale**: Redis caching, Celery async tasks
4. **Enterprise**: Load balancing, database replicas

---

## Testing Strategy

### Unit Tests (Service Layer)
```python
# Test registration_service.py
- test_employer_registration_success
- test_helper_registration_success
- test_role_assignment
- test_duplicate_email_rejected

# Test redirect_service.py
- test_employer_redirect_to_portal
- test_helper_redirect_to_portal
- test_unverified_user_redirect
```

### Integration Tests (Forms + Models)
```python
# Test booking workflow
- test_booking_creation_and_acceptance
- test_booking_rejection_flow
- test_booking_cancellation_policy

# Test search functionality
- test_search_by_location
- test_search_by_skills
- test_combined_filters
```

### Template Tests (Views + Access)
```python
# Test role-based access
- test_employer_cannot_access_helper_portal
- test_unverified_user_sees_pending_page
- test_admin_only_views_protected
```

### Manual Testing
- User acceptance testing with sample employer and helper accounts
- Mobile device testing (iOS, Android)
- Cross-browser testing (Chrome, Safari, Firefox)
- Payment flow testing
- Notification testing

---

## Known Risks & Mitigation

| Risk | Impact | Mitigation |
|------|--------|-----------|
| Payment system complexity | Revenue tracking failure | Start with manual payment tracking, verify before integration |
| Geographic search accuracy | Poor user experience | Implement with GPS, test with actual locations |
| Verification bottleneck | Platform credibility | Build streamlined admin workflow, consider identity API integration |
| Scaling booking notifications | System overload | Queue-based notifications with Celery |
| Account fraud | Platform trust loss | Implement rate limiting, verification requirements |

---

## Success Metrics

### User Engagement
- Registration completion rate > 80%
- Booking request to acceptance conversion > 60%
- Helper profile completion on first login > 90%

### Business Health
- Employer retention after 3 bookings > 70%
- Helper retention after 5 bookings > 75%
- Average helper rating > 4.2/5 stars

### Platform Quality
- Booking completion rate > 85%
- Dispute rate < 5%
- System uptime > 99.5%

---

## Next Steps

1. **Review this plan** with stakeholders and adjust timelines
2. **Setup development environment** (Django, database, static files)
3. **Begin Phase 1** with authentication and registration
4. **Iterate with user feedback** from early testers
5. **Track progress** against milestones
6. **Adjust roadmap** based on learnings and market feedback

---

## Appendix: File Templates & Patterns

### Django Model Template
```python
from django.db import models
from django.contrib.auth.models import User

class HelperProfile(models.Model):
    """Helper profile with skills and verification status."""
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(max_length=500)
    hourly_rate = models.DecimalField(max_digits=6, decimal_places=2)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.first_name} - ${self.hourly_rate}/hr"
```

### Django View Template
```python
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.views.decorators.http import require_http_methods

@login_required
@require_http_methods(["GET", "POST"])
def booking_create(request):
    """Create a new booking request."""
    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.employer = request.user.employerprofile
            booking.save()
            return redirect('booking_detail', pk=booking.id)
    else:
        form = BookingForm()
    return render(request, 'website/booking_create.html', {'form': form})
```

### Django Form Template
```python
from django import forms
from .models import Booking

class BookingForm(forms.ModelForm):
    """Form for creating booking requests."""
    
    class Meta:
        model = Booking
        fields = ['helper', 'date', 'time', 'duration', 'description', 'budget']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'time': forms.TimeInput(attrs={'type': 'time'}),
            'description': forms.Textarea(attrs={'rows': 4}),
        }
```

### Tailwind Component Template
```html
<!-- trust_badge.html -->
<div class="inline-flex items-center gap-1 px-2 py-1 bg-green-50 border border-green-200 rounded">
    <svg class="w-4 h-4 text-green-600" fill="currentColor" viewBox="0 0 20 20">
        <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" />
    </svg>
    <span class="text-xs font-medium text-green-700">ID Verified</span>
</div>
```

---

## Contact & Support

For questions about this plan:
- Review the `.agent.md` file for role-specific context
- Refer to `mongikazi_platform_blueprint.md` for feature details
- Check `mongikazi_ui_design_blueprint_updated.md` for design specifics
- Code follows Django and Tailwind best practices

**Last Updated**: May 10, 2026  
**Status**: Development Phase 1 - Foundation
