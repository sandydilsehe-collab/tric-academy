# TRIC Academy – School of Swimming Web Application

A complete, production-grade web application for **TRIC Academy – School of Swimming** (Tirupur, Tamil Nadu) built with Python Flask and SQLite. The application digitizes the academy's official "Application Form for Entry Pass", delivers public portal pages (Landing, Batch Timings, Fees, Rules & Regulations, Contact), role-based workflows for Members, Coaches, and Admins, competition swimmer tracking with progress analytics, and automated membership lifecycle reminders.

## User Review & Critical Decisions

> [!IMPORTANT]
> The following user preferences were confirmed during clarification:
> - **Default Sample Data**: Full demo set with pre-seeded Admin, Head Coach, Competition Swimmers, and Regular Members with varied expiry dates (1, 3, 7 days) and competition race history.
> - **Application Form Presentation**: Authentic paper form layout matching the physical printed entry pass (teal banner `#1F8A8A`, application number, date-of-birth box grid, dotted field underlines, and For Office Use section).
> - **Landing Page Visual**: High-resolution Olympic training pool with clear water and fixed full-screen backdrop.

- **Confirmed Decision 1**: Python Flask backend with Jinja2 templates, standard CSS variables for brand identity, and SQLite database with WAL mode for zero external database dependencies.
- **Confirmed Decision 2**: Strict separation of public sign-up vs admin "For Office Use" controls, with print-ready CSS (`@media print`) that renders an exact 1:1 replica of the paper entry pass.
- **Confirmed Decision 3**: Strict role-based competition tracking restricted to Competition-batch swimmers, coaches, and administrators.

---

## 1. Overview & Core Concept

- **What It Does**: Digitizes the operations of TRIC Academy, handling member onboarding through the official printed pass application format, phone OTP simulation and email verification, coach batch assignments and daily attendance, online membership renewals with clean payment abstraction, and elite competition race performance tracking.
- **Target Audience / Persona**:
  - *Applicants & Swimmers*: Prospective learners applying for entry passes, parents of minors, and swimmers tracking attendance, renewals, and race timings.
  - *Coaches*: Marking daily attendance for batches and logging race records for competitive swimmers.
  - *Academy Administrators*: Approving applications, verifying office documents, assigning batches and membership plans, running reminder jobs, and exporting data.
- **Key Value**: Replaces physical paper logs with a tamper-resistant digital registry while preserving the academy's official paper form heritage and enforcing rules, safety declarations, and batch limits.

---

## 2. User Experience & Visual Design

### Key User Flows

1. **Public Discovery & Exploration**:
   - Fixed full-screen pool background (`static/images/pool.jpg`) with dark contrast scrim.
   - Clean top navigation (About, Batches, Fees, Rules, Contact, Login, Sign Up).
   - Rules & Regulations view rendering all 32 official academy pool rules from the official documentation.
2. **Onboarding via Official Entry Pass Form (`/apply`)**:
   - Visual replica of the paper form: Teal header banner (`#1F8A8A`), logo placeholder, auto-generated Application Number (e.g. `TRIC-2026-0042`), and Date.
   - 2-column dotted-underline rows for Name, Address, PIN Code, Contact, Email.
   - Age calculation with separate DD / MM / YYYY digit boxes.
   - Conditional Guardian and Parent Occupation fields for minors (<18).
   - Pass type selection (*Learn to Swim* vs. *Competition*).
   - Department sponsorship toggle with document upload.
   - Photo upload zone with interactive square preview.
   - Mandatory health & rules declaration with dynamic >50 age medical certificate warning.
   - Submission triggers on-screen simulated OTP verification and email confirmation link.
3. **Admin Verification & Office Endorsement (`/admin/applications`)**:
   - Admin reviews pending applications with photo and uploaded sponsor certificates.
   - "For Office Use" section unlocked: Coach recommendation, Pass issued, Validity, ID card number, Section I/C signature, ₹50 ID card fee toggle, batch assignment, and plan selection.
   - One-click print button generating an official paper pass copy via `@media print`.
4. **Member Dashboard & Renewal**:
   - Digital Member ID card with validity status (Active, Expiring Soon, Expired).
   - Current batch schedule, assigned coach, and attendance calendar log.
   - Online renewal flow with plan selection (Monthly 30-day, Quarterly 90-day) and pluggable mock payment gateway.
5. **Competition Swimmer Hub (`/competition`)**:
   - Access-restricted to Competition-batch members, coaches, and admins.
   - Swimmer view: Personal Bests showcase across strokes (Freestyle, Backstroke, Breaststroke, Butterfly, IM) and distances (50m, 100m, 200m, 400m).
   - Interactive Chart.js timeline showing time progression per stroke.
   - Coach/Admin race record entry: Meet name, event, split/final time, position, personal best flag.
6. **Attendance Management (`/attendance`)**:
   - Batch selector, date picker, and quick toggle roster (Present / Absent / Excused).
   - Swimmers can view their personal attendance percentage and log.

### Visual Identity & Theme

- **Aesthetic Direction**: Athletic aquatic elegance paired with institutional heritage. Clean, disciplined layout with zero visual slop.
- **Color Palette (CSS Variables in `static/css/theme.css`)**:
  - `--brand-primary`: `#1F8A8A` (TRIC Academy Heritage Teal)
  - `--brand-primary-dark`: `#135B5B`
  - `--brand-accent`: `#0284C7` (Clear Water Cyan)
  - `--canvas-bg`: `#F8FAFC` (Crisp light neutral)
  - `--surface-card`: `#FFFFFF`
  - `--text-main`: `#0F172A`
  - `--text-muted`: `#64748B`
  - `--border-hairline`: `rgba(15, 23, 42, 0.12)`
  - `--form-border`: `#1E293B`
- **Typography**:
  - Display / Headings: `Plus Jakarta Sans`, bold athletic tracking.
  - Body & Form Elements: `DM Sans` / `Public Sans` for legibility.
  - Form Number Boxes & Metrics: Tabular monospace (`font-mono tabular-nums`).
- **Paper Form Styling**:
  - Exact border styling with thin dark outer frame, teal top banner with white typography, dotted underline inputs, and dedicated photo preview frame.
  - Print stylesheet stripping navigation, backgrounds, and interactive controls to print crisp monochrome/teal physical certificates.

---

## 3. Key Product Decisions & Trade-Offs

- **Decision 1: Standalone Python Flask Architecture on Port 3000**
  - *Chosen Approach*: Pure Flask app with Jinja2 templates, native CSS, vanilla JavaScript for Chart.js and photo preview, and SQLite3 database.
  - *Why*: Explicitly required by user prompt ("using Python Flask and SQLite. Do NOT use React or Node. Deliver a full project..."). Runs directly on port 3000 for the preview iframe and can be executed locally with `python3 app.py`.
  - *Alternatives Considered*: Hybrid React/Flask was explicitly banned.
- **Decision 2: Dual-Mode Application Form Template**
  - *Chosen Approach*: A single master Jinja2 template (`templates/application_form.html`) that adapts seamlessly for public applicant registration, admin user creation, and official print pass generation.
  - *Why*: Prevents field drift between the public form and the official office record; allows instant printing of the exact paper pass seen in the user's reference photograph.
- **Decision 3: Mock Payment Service Architecture**
  - *Chosen Approach*: Clean abstract interface `PaymentService` with a working `MockPaymentService` storing transactions in `payments` table, designed for drop-in Razorpay integration (`RazorpayPaymentService`).
  - *Why*: Allows immediate end-to-end testing of membership extensions without requiring live bank credentials or merchant keys on localhost.
- **Decision 4: Automated Reminders with Duplicate Prevention**
  - *Chosen Approach*: APScheduler background job checking expiry thresholds (7, 3, 1 days, and day 0). Every dispatched reminder is recorded in `reminder_logs` with a unique constraint on `(user_id, reminder_type, target_date)` to guarantee zero duplicate emails. Admin UI includes an immediate "Run Reminders Now" testing trigger.

---

## 4. Technical Architecture & Data Strategy

### System Architecture Diagram

```
┌────────────────────────────────────────────────────────────────────────┐
│                     TRIC Academy Web Application                       │
└────────────────────────────────────────────────────────────────────────┘
                                    │
       ┌────────────────────────────┼────────────────────────────┐
       ▼                            ▼                            ▼
┌──────────────┐             ┌──────────────┐             ┌──────────────┐
│ Public Pages │             │ Member/Coach │             │  Admin Hub   │
│ - Home/Hero  │             │  Dashboard   │             │ - Applicants │
│ - Rules (32) │             │ - Digital ID │             │ - Office Use │
│ - Batches    │             │ - Attendance │             │ - Batches    │
│ - Fees       │             │ - Renewals   │             │ - Reminders  │
│ - Apply Form │             │ - Race Times │             │ - CSV Export │
└──────────────┘             └──────────────┘             └──────────────┘
       │                            │                            │
       └────────────────────────────┼────────────────────────────┘
                                    ▼
       ┌─────────────────────────────────────────────────────────┐
       │                 Flask Application (app.py)              │
       │  - Authentication (Werkzeug Password Hash, Sessions)    │
       │  - Form & File Upload Validation (Photo & Sponsor Cert) │
       │  - Access Control Decorators (@login_required, @role)   │
       │  - APScheduler Expiry Job + Reminder Mailer Service     │
       │  - Clean Payment Service Interface                      │
       └─────────────────────────────────────────────────────────┘
                                    │
       ┌────────────────────────────┴────────────────────────────┐
       ▼                                                         ▼
┌──────────────┐                                          ┌──────────────┐
│ SQLite DB    │                                          │ File Storage │
│ (tric.db)    │                                          │ /uploads/    │
│ - Users      │                                          │ - photos/    │
│ - Batches    │                                          │ - certs/     │
│ - Attendance │                                          │ - backups/   │
│ - Races      │                                          └──────────────┘
│ - Payments   │
│ - Reminders  │
└──────────────┘
```

### Data Schema Overview

1. `users`: ID, app_no, role (`member`, `coach`, `admin`), status (`pending`, `approved`, `deactivated`), name, email, phone, password_hash, dob, age, address, pincode, guardian_name, guardian_occupation, experience, pass_type_requested (`learn_to_swim`, `competition`), sponsored (bool), sponsor_cert_path, photo_path, health_declared (bool), rules_agreed (bool), signature_name, place, application_date, email_verified (bool), phone_verified (bool).
2. `office_use`: user_id, coach_recommendation, pass_type_issued, validity_start, validity_end, id_card_number, id_card_fee_paid (bool), documents_verified (bool), section_ic_signature, approved_at, approved_by.
3. `batches`: id, name (e.g. "Morning Batch A", "Evening Batch B", "Competition"), start_time, end_time, days, coach_id, max_capacity.
4. `plans`: id, name ("Monthly", "Quarterly"), duration_days (30, 90), fee_amount, description.
5. `user_memberships`: id, user_id, plan_id, batch_id, start_date, end_date, is_active.
6. `attendance`: id, batch_id, user_id, date, status (`present`, `absent`, `excused`), marked_by.
7. `race_records`: id, swimmer_id, meet_date, meet_name, stroke (`freestyle`, `backstroke`, `breaststroke`, `butterfly`, `individual_medley`), distance (`50m`, `100m`, `200m`, `400m`, `800m`, `1500m`), time_seconds, time_display, position, is_personal_best (bool), notes, recorded_by.
8. `payments`: id, user_id, plan_id, amount, payment_date, transaction_id, status, payment_method.
9. `reminder_logs`: id, user_id, reminder_type (`7_day`, `3_day`, `1_day`, `day_of`), sent_at, target_date, status.

### Delivery File Inventory

- `app.py`: Full Flask application with route handlers, authentication, scheduler, and payment service.
- `schema.sql`: Complete DDL schema with indexing.
- `seed.py`: Seeding script with realistic admin, coach, competition swimmers, regular learners, sample batches, attendance logs, and race records.
- `requirements.txt`: Python dependencies (`flask`, `apscheduler`, `werkzeug`, `python-dotenv`).
- `templates/`: Jinja2 templates for layout, landing, rules, application form, login, dashboards, attendance, competition, and admin management.
- `static/css/`: `theme.css` with CSS custom properties and `paper_form.css` with dedicated print styles.
- `static/js/`: Client interactions, Chart.js race charts, dynamic age calculation, and OTP modal logic.
- `static/images/`: `pool.jpg` (high-res training pool), `logo.png` placeholder.
- `README.md`: Step-by-step local setup, virtualenv creation, running the server, and testing credentials.
