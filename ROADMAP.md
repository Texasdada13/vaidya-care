# Vaidya Care — Product Roadmap
**Version 1.0 · March 2026**

---

## Current State (MVP — March 2026)

The app works for a single practitioner (Dr. Meenakshi / AyurRoots demo).

**Built:**
- Auth (practitioner login)
- Patient management: demographics, health profile, dosha/labs/lifestyle/complaints
- Consultation Plan Builder: supplements + recipes with dose/timing, foods, lifestyle notes
- Patient portal (5 pages): Home, Check-In, My Plan, Progress charts, Visits
- Follow-up scheduling with overdue alerts
- Supplement + Recipe libraries
- AI chat assistant (Claude, streaming)
- Dashboard: KPIs, compliance cards, sparklines
- QR code for patient portal link

**Stack**: Flask 3, SQLAlchemy (SQLite), Jinja2, Bootstrap Icons, Claude API, Flask-Mail

---

## Phase 0: Production Readiness (Before Charging Anyone)
*Estimated effort: 3–4 weeks*

These are non-negotiables before taking real practitioners' money.

### 0.1 Multi-Tenant Architecture
- [ ] Each practitioner gets their own account (currently single-practitioner)
- [ ] Practitioner registration / self-signup flow
- [ ] Data isolation: practitioner can only see their own patients
- [ ] Admin panel (super-admin view of all practitioners)

### 0.2 HIPAA Compliance Foundations
- [ ] Encryption at rest (SQLite → PostgreSQL with pgcrypto, or encrypted disk)
- [ ] Audit log table (who accessed/modified what patient record, when)
- [ ] Automatic session timeout (30 min idle)
- [ ] BAA (Business Associate Agreement) template for practitioners
- [ ] Password strength requirements + 2FA option
- [ ] Data deletion / patient record export on request

### 0.3 Payment Processing
- [ ] Stripe integration (monthly/annual subscription)
- [ ] Tier enforcement (patient count limits, feature gating)
- [ ] Trial period (14-day free trial, no credit card)
- [ ] Billing portal (upgrade/downgrade/cancel)
- [ ] Webhook handling for failed payments

### 0.4 Deployment
- [ ] Move from SQLite → PostgreSQL (Render managed DB or Supabase)
- [ ] Render or Fly.io production deploy with environment variables
- [ ] Custom domain (vaidyacare.com or app.vaidyacare.com)
- [ ] SSL, proper SECRET_KEY rotation
- [ ] Error monitoring (Sentry)
- [ ] Uptime monitoring

### 0.5 Onboarding Flow
- [ ] Practitioner signup: name, email, password, practice name, NAMA designation
- [ ] Practice profile page (name, logo, bio, location/telehealth)
- [ ] First-time wizard: "Add your first patient" guided flow
- [ ] Sample data option (vs. start fresh)
- [ ] Welcome email sequence (3-email drip: setup → first patient → invite patient to portal)

---

## Phase 1: Core Feature Completeness
*Estimated effort: 4–6 weeks*
*Target: ready for NAMA school partnerships*

### 1.1 Email Portal Link Delivery
- [ ] "Send Portal Link" button on patient detail page
- [ ] Email template: "Your AyurRoots Wellness Portal is ready" with portal URL
- [ ] Practitioner can customize the email message
- [ ] Track sent/opened status

### 1.2 Appointment Scheduling
**Option A**: Build in-house (simple)
- [ ] Calendar view of upcoming appointments
- [ ] Book new appointment (date/time/duration/type)
- [ ] Patient receives email confirmation
- [ ] Reminder email 24h before appointment

**Option B**: Integrate Calendly/Acuity (faster)
- [ ] Practitioner links their Calendly URL
- [ ] "Book Appointment" button on patient portal links to their Calendly
- [ ] Appointments pull back via Calendly webhook

*Recommendation: Option B for Phase 1, Option A for Phase 2/3*

### 1.3 Classical Supplement Library Expansion
- [ ] Expand from 7 → 50+ classical formulas
- [ ] Add: Triphala, Ashwagandha, Shatavari, Brahmi, Neem, Guduchi, Punarnava, Trikatu, Dashamula, Chyavanprash, Arjuna, Amalaki, Haritaki, Bibhitaki, Pippali, Gokshura, Manjistha, Vidanga, etc.
- [ ] Classical name + common name + Sanskrit
- [ ] Typical dosing ranges (not just free text)
- [ ] Cautions/contraindications field
- [ ] Link to common brands (Banyan Botanicals, Organic India, Kottakkal, Dhootpapeshwar)

### 1.4 Print / PDF Plan
- [ ] Printable `/portal/<token>/plan/print` page (clean, no nav)
- [ ] "Download as PDF" using browser print or WeasyPrint
- [ ] Practitioner can also print from patient detail
- [ ] Branded with practice logo and name

### 1.5 Patient Contact Info Edit (Portal)
- [ ] Simple form in portal: name, phone, email
- [ ] Practitioner is notified of changes
- [ ] Audit log entry

### 1.6 Practice Profile / Branding
- [ ] Practitioner uploads their practice logo
- [ ] Practice name replaces "AyurRoots" in patient-facing UI
- [ ] Custom tagline
- [ ] This makes the tool feel white-label for each practitioner

---

## Phase 2: Clinic Tier Features
*Estimated effort: 6–8 weeks*
*Unlocks $149/mo Clinic tier*

### 2.1 Panchakarma Scheduling
- [ ] Treatment room model (name, capacity, therapies supported)
- [ ] Therapist model (name, specialties, schedule)
- [ ] Panchakarma therapy catalog (Abhyanga, Shirodhara, Nasya, Basti, Virechana, Vamana, etc.)
- [ ] Room + therapist booking grid (prevents double-booking)
- [ ] Day view: all rooms, all therapists, all appointments
- [ ] Treatment package builder (e.g., "7-day Panchakarma" with daily sessions)
- [ ] Patient receives daily schedule

### 2.2 Multi-Practitioner Support
- [ ] Invite team members (practitioner + assistant/receptionist roles)
- [ ] Role-based access: admin can see all patients; associate sees only assigned
- [ ] Shared supplement/recipe library across practice
- [ ] Per-seat billing for Clinic tier

### 2.3 Inventory Management (Herbs & Oils)
- [ ] Track in-house herb/oil inventory
- [ ] Alert when stock is low
- [ ] Link to suppliers (Banyan Botanicals, Mountain Rose Herbs)
- [ ] Usage log tied to treatments

### 2.4 Intake Forms (Customizable)
- [ ] Practitioner creates custom intake questionnaires
- [ ] Patient fills out via portal before first appointment
- [ ] Responses auto-populate health profile fields
- [ ] Dosha quiz embedded in intake

---

## Phase 3: AI-First Features
*Estimated effort: 4–6 weeks*
*Strongest differentiator from all competitors*

### 3.1 AI Plan Draft
- [ ] Practitioner clicks "Draft Plan with AI"
- [ ] AI reads patient health profile, chief complaints, dosha assessment, check-in history
- [ ] Generates a full draft consultation plan: recommended supplements, dietary guidance, lifestyle notes, recipes
- [ ] Practitioner reviews and edits before activating
- [ ] AI explains its reasoning (e.g., "Recommended Avipattikar because of Pitta-aggravated digestion")

### 3.2 AI Check-In Insights
- [ ] After 7+ check-ins, AI generates a trend summary
- [ ] "Kajori's digestion scores have improved 40% since starting Avipattikar. Energy remains low on days she skips morning routine."
- [ ] Visible on practitioner dashboard per patient
- [ ] AI suggests follow-up topics based on trends

### 3.3 AI Follow-Up Notes
- [ ] Before a follow-up, AI drafts "Session prep" based on patient history
- [ ] Highlights what changed since last visit, what to ask about, what to adjust
- [ ] After session, AI helps draft SOAP notes from practitioner input

### 3.4 Patient-Facing AI (Portal)
- [ ] "Ask about your plan" — patient can ask questions about their supplements, foods, protocol
- [ ] AI only answers within scope of their active plan (not general medical advice)
- [ ] "Why was this supplement recommended for me?" queries
- [ ] Practitioner can review patient's questions

---

## Phase 4: Growth & Distribution Features
*Enables go-to-market at scale*

### 4.1 Practitioner Directory (Public)
- [ ] `/practitioners` — searchable public directory
- [ ] Each practitioner gets a public profile page
- [ ] "Book a consultation" links to their Calendly
- [ ] SEO value: "Find an Ayurvedic practitioner in [city]"
- [ ] Free for all paying practitioners; premium placement for higher tiers

### 4.2 Patient Referral / Sharing
- [ ] Patient can share their portal link with a family member
- [ ] Referral: "Referred by [patient name]" tracked on new patient intake

### 4.3 Content Library (Practitioner-Contributed)
- [ ] Practitioners can mark recipes/supplements as "public to community"
- [ ] Community library grows over time
- [ ] Network effects: more practitioners = richer library

### 4.4 Analytics Dashboard
- [ ] Practitioner sees aggregate stats: avg habit compliance, top complaints, most prescribed supplements
- [ ] Patient cohort comparisons
- [ ] Export to CSV

### 4.5 Integrations
- [ ] Calendly / Acuity (appointment booking)
- [ ] Stripe (payments — already in Phase 0)
- [ ] Zoom (telehealth link in follow-up)
- [ ] WhatsApp Business API (for India market / diaspora)
- [ ] Google Calendar sync

---

## Phase 5: India / Global Expansion
*Year 2+*

### 5.1 BAMS Diaspora Tier
- [ ] $25/mo pricing tier targeting diaspora practitioners
- [ ] Enhanced classical formula library (full Ashtanga Hridayam / Charaka references)
- [ ] Ayurveda-native SOAP note structure (Nadi, Jihwa, Mutra, Mala, Shabda, Sparsha, Drika, Akriti)
- [ ] Pulse (Nadi) diagnosis documentation

### 5.2 India Market Entry
- [ ] Hindi UI translation
- [ ] INR billing (Razorpay)
- [ ] GST-compliant invoicing
- [ ] WhatsApp integration (primary communication channel in India)
- [ ] ABDM / Ayush Grid compatibility for government-mandated interoperability

---

## Feature Priority Matrix

| Feature | Impact | Effort | Phase |
|---|---|---|---|
| Multi-tenant / practitioner signup | ★★★★★ | High | 0 |
| Stripe billing | ★★★★★ | Medium | 0 |
| HIPAA basics (audit log, encryption) | ★★★★★ | Medium | 0 |
| Render production deploy | ★★★★★ | Low | 0 |
| Email portal link | ★★★★★ | Low | 1 |
| Onboarding wizard | ★★★★ | Medium | 0 |
| Classical supplement library (50+) | ★★★★ | Low | 1 |
| Print/PDF plan | ★★★★ | Low | 1 |
| Practice branding/logo | ★★★★ | Low | 1 |
| Calendly integration | ★★★★ | Low | 1 |
| AI plan draft | ★★★★★ | Medium | 3 |
| Panchakarma scheduling | ★★★★ | High | 2 |
| AI check-in insights | ★★★★ | Medium | 3 |
| Practitioner directory | ★★★ | Medium | 4 |
| India market | ★★★★ | High | 5 |

---

## Tech Debt to Address

- **SQLite → PostgreSQL** (required before multi-tenant and production)
- **Jinja2 templates → consider React/HTMX** for richer AI interactions (Phase 3)
- **Background job queue** (Celery or similar) for email sending, AI tasks
- **File storage** (S3 or Cloudflare R2) for practice logos, patient images
- **Rate limiting** on AI chat endpoint

---

*Product Roadmap v1.0 · March 2026*
*Maintained by the Vaidya Care development team*
