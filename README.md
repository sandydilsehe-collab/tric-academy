# TRIC Academy – School of Swimming (TRIC)

A complete, locally runnable web application for **TRIC Academy – School of Swimming** (Tirupur, Tamil Nadu, India) built using **Python Flask** and **SQLite3**.

The application digitizes the official academy operations based on the printed **"Application Form for Entry Pass"**, while providing member portals, coaching staff tools, competition swimmer tracking, and automated membership lifecycle reminders.

---

## 🏊 Academy Details & Location
- **Organization**: TRIC Academy – School of Swimming
- **Address**: 85/5, Kaliamman Kovil Street, #5 Velampalayam, Tirupur - 641 652, Tamil Nadu, India
- **Email**: `goodwillshiva@gmail.com`
- **Phone Numbers**: `+91-9894777333`, `+91-9894730333`, `+91-9894757333`
- **Website**: `www.tricacademy.com`

---

## 🚀 Quick Start / Local Run Steps

### 1. Prerequisites
- Python 3.10+ installed on your system.

### 2. Set Up Virtual Environment & Dependencies
```bash
# Navigate to the project directory
cd applet

# Create a virtual environment (optional but recommended)
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies from requirements.txt
pip install -r requirements.txt
```

### 3. Initialize & Seed the Database
```bash
python3 seed.py
```
This sets up `tric.db` with the schema, batches, plans, admin, coaches, 15 realistic members (with expiries in 1, 3, 7 days, today, expired), competition race data, attendance, and sample avatars.

### 4. Run the Application
```bash
python3 app.py
```
Open your browser and navigate to:
```
http://localhost:3000
```

---

## 🔑 Demo Login Accounts

| Role | Email / Phone | Password | Features Accessible |
| :--- | :--- | :--- | :--- |
| **Super Admin** | `admin@tricacademy.com` / `9894777333` | `admin123` | Full dashboard, applicant review, office use endorsement, batch/plan management, reminders test trigger, CSV exports |
| **Head Coach** | `coach@tricacademy.com` / `9894730333` | `coach123` | Mark daily batch attendance, enter & view competition race records and PBs |
| **Competition Swimmer** | `karthik.swim@gmail.com` / `9843211001` | `karthik123` | Digital Member ID card, Competition Hub (Chart.js progress chart, PBs, race history), renew membership |
| **General Member** | `priya.learner@gmail.com` / `9843211005` | `priya123` | Digital ID card, batch schedule, attendance history, online renewal with mock payment |

*(Note: On the login page `/login`, quick 1-click buttons are provided to autofill any of these test credentials)*

---

## ✨ Key Features & Technical Highlights

### 1. Authentic Paper "Application Form for Entry Pass" (`/apply`)
- **Visual Replica**: Faithfully styled after the physical printed entry pass using teal banner (`#1F8A8A`), logo crest, auto-generated Application Number, and thin dark border box with dotted underline inputs.
- **Dynamic Age & Single-Digit DOB Boxes**: Selecting a Date of Birth automatically splits and populates individual boxes for `DD`, `MM`, `YYYY`, and calculates exact age in years.
- **Minor Guardian Fields**: If applicant is under 18, Parent/Guardian name and occupation fields are required and dynamically displayed.
- **Senior Health Notice**: If applicant is over 50, an official note alerts them that a medical fitness certificate from an authorized practitioner must be produced at the office.
- **Passport Photo Upload & Preview**: Clickable dashed photo slot with instant client preview.
- **Simulated OTP Verification**: Public submissions display a realistic on-screen mock 6-digit OTP modal to simulate phone verification before saving.
- **Print-Ready CSS (`@media print`)**: Clicking "Print / Save as PDF" strips navigation and buttons, rendering a crisp 1-page paper entry pass.

### 2. 32 Official Pool Rules & Regulations (`/rules`)
- Full, verbatim reproduction of all 32 general rules and regulations from the TRIC Academy charter (mandatory caps, costume restrictions, medical screening, diving board protocols, and declarations).

### 3. Role-Based Access Control
- **Member**: Personal dashboard, digital ID card with validity countdown, attendance calendar, and online renewal.
- **Coach**: Daily roster attendance tool (`/attendance`) with one-click "Mark All Present/Absent", and competition race logging.
- **Admin**: "For Office Use" endorsements, user deactivation/activation, plan pricing configuration, database backup management, and CSV exports (`/admin/export/users.csv` and `/admin/export/payments.csv`).

### 4. Competition Tracking (`/competition`)
- **Strict Access Control**: Restricted exclusively to Competition-batch swimmers, coaches, and administrators.
- **Swimmer Analytics**: Interactive **Chart.js** line chart displaying race time progression over time across strokes (Freestyle, Backstroke, Breaststroke, Butterfly, IM) and distances (50m, 100m, 200m).
- **Personal Bests (PB)**: Highlights individual best timings with gold badges.
- **Coach Race Logging**: Quick form to submit official meet results with minutes, seconds, hundredths, rank, and coach technique notes.

### 5. Automated Reminders & APScheduler
- Daily background job runs at 06:00 AM checking memberships expiring in **7 days, 3 days, 1 day, and on the expiry day**.
- All notifications are logged in the `reminder_logs` SQLite table with a composite unique constraint to guarantee zero duplicate emails.
- Admin dashboard includes an immediate **"Run Reminders Now"** button for on-demand testing.

### 6. Pluggable Payment Service Interface
- Implements `PaymentService` base class with a clean `MockPaymentService` that records transaction IDs and automatically extends membership end dates upon checkout (`/renew`).
- Ready for drop-in Razorpay integration (`RazorpayPaymentService`) when live API keys and webhook secrets are provided.

### 7. Automated SQLite Backups
- Automatic daily backup at 01:00 AM to `backups/`, automatically keeping the last 7 database snapshots.

---

## 📁 Project Structure

```
├── app.py                  # Main Flask application and routes
├── schema.sql              # SQLite DDL schema with indexes
├── seed.py                 # Comprehensive database seeding script
├── requirements.txt        # Python package dependencies
├── README.md               # Documentation and execution guide
├── templates/              # Jinja2 templates
│   ├── base.html           # Common layout shell and navigation
│   ├── index.html          # Public landing page with pool backdrop
│   ├── rules.html          # 32 Official Rules & Regulations
│   ├── application_form.html # Authentic paper entry pass template
│   ├── apply_success.html  # Application submission confirmation
│   ├── login.html          # Login with demo autofill buttons
│   ├── member_dashboard.html # Member digital ID card and schedule
│   ├── renew.html          # Membership renewal checkout
│   ├── member_attendance.html # Personal attendance log
│   ├── attendance.html     # Coach batch attendance roster
│   ├── competition.html    # Competition Hub & Chart.js progress
│   ├── admin_dashboard.html# Admin overview and KPI counters
│   ├── admin_applicants.html # Pending applicants review queue
│   ├── admin_users.html    # Member directory and CSV export
│   ├── admin_user_edit.html# Member edit form
│   ├── admin_batches.html  # Batches & timings management
│   ├── admin_plans.html    # Membership plan pricing
│   ├── admin_reminders.html# Reminder logs & testing trigger
│   └── admin_backups.html  # SQLite snapshot manager
├── static/
│   ├── css/
│   │   ├── theme.css       # Aquatic theme & CSS custom properties
│   │   └── paper_form.css  # Authentic printed paper form styles
│   ├── js/
│   │   └── app.js          # Age calc, digit boxes, OTP modal, charts
│   └── images/
│       ├── pool.jpg        # High-res Olympic training pool image
│       ├── logo.svg        # TRIC Academy vector crest
│       └── logo.png        # TRIC Academy badge image
└── uploads/                # User uploaded photos and certificates
```
