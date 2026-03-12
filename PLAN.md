# Vaidya Care — Architecture & Build Plan

## Project Overview
Ayurvedic practice management tool for practitioners (initially Dr. Meenakshi).
Enables patient intake, personalized protocol management, daily habit tracking via shareable links, follow-up scheduling, and AI-assisted consultation review.

**Built by:** Shuva Mukhopadhyay + Claude Code
**Stack:** Python 3.11+, Flask 3.x, SQLAlchemy (SQLite), Jinja2, Bootstrap Icons, Anthropic Claude API
**Design language:** Reused from TRH Solutions field service app (same CSS system, sidebar pattern, card grid)

---

## Running the App

```bash
cd vaidya-care
venv/Scripts/activate      # Windows
# source venv/bin/activate  # Mac/Linux
cd web
python app.py
# Visit http://127.0.0.1:5001
# First run: go to /setup to create practitioner account
```

---

## Directory Structure

```
vaidya-care/
├── venv/                      # Python virtual environment (not committed)
├── web/
│   ├── app.py                 # Flask app, all routes
│   ├── models.py              # SQLAlchemy models + seed data
│   ├── static/
│   │   └── css/style.css      # Design system (copied + adapted from TRH)
│   └── templates/
│       ├── base.html          # Layout shell (sidebar, flash, chat panel)
│       ├── dashboard.html     # Home: KPIs, follow-ups due, recent check-ins
│       ├── patients.html      # Patient list with search + compliance
│       ├── patient_new.html   # New patient intake form
│       ├── patient_detail.html# Full profile, check-ins, plan, follow-ups
│       ├── followups.html     # All follow-ups (upcoming + completed)
│       ├── recipes.html       # Master recipe library
│       ├── supplements.html   # Master supplement library
│       ├── checkin.html       # PUBLIC — no login, patient daily form
│       ├── checkin_thankyou.html # Public post-submit confirmation
│       ├── auth/
│       │   ├── login.html
│       │   └── setup.html     # First-run account creation
│       └── partials/
│           ├── sidebar.html
│           └── chat_panel.html # AI assistant (floating, all pages)
├── vaidya.db                  # SQLite database (auto-created, not committed)
├── .env                       # Secrets (not committed — see .env.example)
├── .env.example               # Template for required env vars
├── requirements.txt
├── PLAN.md                    # ← YOU ARE HERE
└── .gitignore
```

---

## Database Models

### Practitioner
Single login user (the doctor). Email + password hash.

### Patient
Core client record: demographics, lifestyle, contact info.
Relationships: → HealthProfile (1:1), → ConsultationPlan (1:many), → DailyCheckIn (1:many), → CheckInToken (1:1), → FollowUp (1:many)

### HealthProfile
Lab values (lipid panel, metabolic, hormonal), chief complaints, medical history, Ayurvedic dosha/agni/ama observations. One per patient.

### ConsultationPlan
Personalized protocol: title, duration, start/end dates, foods to avoid/include, lifestyle notes. Has many PlanSupplements and PlanRecipes.

### Supplement (master library — pre-seeded)
Name, brand, category (Herbal/Tea/Tablet), purpose, source URL. Pre-loaded from Shuva's spreadsheet (7 items).

### PlanSupplement
Junction: Plan → Supplement with dose, timing, frequency, special notes.

### Recipe (master library — pre-seeded)
Name, meal_type (Breakfast/Lunch/Dinner/Tea/Snack), ingredients, instructions. Pre-loaded (9 recipes from spreadsheet).

### PlanRecipe
Junction: Plan → Recipe with meal_slot.

### CheckInToken
UUID token per patient for public shareable URL: `/checkin/<token>`. Active flag for revocation.

### DailyCheckIn
Daily log submitted by patient: 14 boolean habit fields + 4 symptom ratings (1-5) + free text notes. Computed properties: `habit_completion_pct`, `avg_symptom_score`.

### FollowUp
Scheduled practitioner reminder: patient, date, reason, notes, completed flag.

---

## Routes Map

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET/POST | `/login` | No | Practitioner login |
| GET/POST | `/setup` | No | First-run account creation (disabled after first user) |
| GET | `/logout` | Yes | Logout |
| GET | `/` | Yes | Dashboard |
| GET | `/patients` | Yes | Patient list |
| GET/POST | `/patients/new` | Yes | New patient form |
| GET | `/patients/<id>` | Yes | Patient detail |
| GET | `/followups` | Yes | Follow-up list |
| POST | `/api/followups` | Yes | Create follow-up (JSON) |
| POST | `/api/followups/<id>/complete` | Yes | Mark follow-up done (JSON) |
| GET/POST | `/checkin/<token>` | No | Public daily check-in form |
| GET | `/recipes` | Yes | Recipe library |
| GET | `/supplements` | Yes | Supplement library |
| POST | `/api/chat` | Yes | AI chat (SSE streaming) |
| GET | `/api/chat/suggestions` | Yes | AI suggestion chips |

---

## AI Chat Integration

**Library:** `anthropic` SDK, streaming via SSE
**Model:** `claude-sonnet-4-6`
**Context engine:** Builds a system prompt from:
- Practitioner role description
- Current patient context (if `patient_id` passed)
- Patient's health profile (complaints, dosha notes)
- Last check-in summary (habit %, avg symptom score)

**Frontend:** `chat_panel.html` partial, floating FAB on all pages.
**API Key:** `ANTHROPIC_API_KEY` in `.env`

---

## Email Notifications

**Library:** `flask-mail`
**Trigger 1:** Patient submits check-in → email to `PRACTITIONER_EMAIL`
**Trigger 2 (TODO):** Daily digest of follow-ups due → morning email
**Config:** SMTP via Gmail (app password). Set in `.env`.

---

## Shareable Check-In Flow

1. Create patient → `CheckInToken` auto-generated with UUID
2. Doctor visits `/patients/<id>` → copies link from sidebar card
3. Patient opens `/checkin/<token>` → fills daily form (no login)
4. Submission creates `DailyCheckIn` record → email sent to practitioner
5. Doctor sees check-ins in patient detail and dashboard

---

## CSS Design System

Reused from TRH Solutions. Key variables in `:root`:
- `--primary`: #2563eb (blue)
- `--success`: #059669 (green)
- `--danger`: #dc2626 (red)
- `--warning`: #f59e0b (amber)
- `--sidebar-bg`: #0f172a (dark navy)
- `--content-bg`: #f1f5f9 (light gray)
- `--border`: #e2e8f0

Key component classes: `.card`, `.kpi-card`, `.kpi-grid`, `.data-table`, `.badge`, `.btn`, `.page-header`, `.flash`, `.chat-panel`, `.chat-fab`, `.sidebar-*`

---

## Build Phases & GitHub Issues

### Phase 1 — Foundation (DONE)
- [x] #1 Project scaffold, venv, Flask app structure
- [x] #2 Database models (10 models + seed data)
- [x] #3 Auth — practitioner login/logout + setup
- [x] #4 Base template + sidebar + CSS

### Phase 2 — Core Pages (DONE)
- [x] #5 Dashboard (KPIs, follow-ups, recent check-ins)
- [x] #6 Patients list with search + compliance
- [x] #7 Patient new form
- [x] #8 Patient detail (profile, check-ins, plan, follow-ups)

### Phase 3 — Plans (TODO)
- [ ] #9 Plan builder — assign supplements, recipes, notes to patient
- [ ] #10 Plan detail page with full protocol view
- [ ] #11 Edit health profile (lab values, Ayurvedic observations)

### Phase 4 — Check-In (DONE)
- [x] #12 Public check-in page (`/checkin/<token>`)
- [x] #13 Check-in results table in patient detail
- [ ] #14 Symptom trend charts (SVG line chart, 14-day window)

### Phase 5 — Follow-Ups & Email (PARTIAL)
- [x] #15 Follow-up list + complete action
- [x] #16 Email to doctor on check-in submission
- [ ] #17 Daily digest email — follow-ups due today (cron/scheduler)

### Phase 6 — AI Chat (DONE)
- [x] #18 AI assistant panel (streaming, floating)
- [x] #19 Patient context injected into AI prompt
- [ ] #20 Symptom trend summary in AI context

---

## Environment Variables Required

```
SECRET_KEY=                    # Flask session secret
ANTHROPIC_API_KEY=sk-ant-...   # Claude API key
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your@gmail.com
MAIL_PASSWORD=your-app-password
MAIL_DEFAULT_SENDER=your@gmail.com
PRACTITIONER_EMAIL=            # Where notifications go
```

---

## Key Design Decisions

1. **SQLite** — Sufficient for 15-40 patients. Easy to backup (single file). Upgrade to PostgreSQL if needed.
2. **No patient accounts** — Shareable token link avoids auth friction for patients. UUID tokens are per-patient and revocable.
3. **Single practitioner** — Setup route disabled after first user. Multi-practitioner can be added later via org/team model.
4. **Seeded data** — Supplements and recipes pre-loaded from Shuva's spreadsheet so Dr. Meenakshi starts with a populated library.
5. **SSE streaming for chat** — Same pattern as TRH Solutions. Real-time response feels more responsive for long AI answers.

---

## Next Session Checklist

When starting a new session on this project:
1. Read this file (`PLAN.md`)
2. Check open GitHub issues for current priorities
3. Run `git log --oneline -10` to see recent commits
4. Start Flask: `cd web && python app.py` → http://127.0.0.1:5001
5. First run: visit `/setup` to create account
