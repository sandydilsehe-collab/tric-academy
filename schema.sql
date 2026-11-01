-- TRIC Academy - School of Swimming
-- SQLite Database Schema

PRAGMA foreign_keys = ON;

-- Users Table
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    app_no TEXT UNIQUE NOT NULL,
    role TEXT CHECK(role IN ('member', 'coach', 'admin')) NOT NULL DEFAULT 'member',
    status TEXT CHECK(status IN ('pending', 'approved', 'deactivated')) NOT NULL DEFAULT 'pending',
    name TEXT NOT NULL,
    email TEXT NOT NULL,
    phone TEXT NOT NULL,
    password_hash TEXT NOT NULL,
    dob DATE,
    age INTEGER,
    address TEXT,
    pincode TEXT,
    guardian_name TEXT,
    guardian_occupation TEXT,
    experience TEXT,
    pass_type_requested TEXT CHECK(pass_type_requested IN ('learn_to_swim', 'competition')) DEFAULT 'learn_to_swim',
    sponsored INTEGER DEFAULT 0,
    sponsor_cert_filename TEXT,
    photo_filename TEXT,
    health_declared INTEGER DEFAULT 0,
    rules_agreed INTEGER DEFAULT 0,
    dpdp_consent INTEGER DEFAULT 0,
    signature_name TEXT,
    place TEXT,
    application_date DATE DEFAULT (DATE('now')),
    email_verified INTEGER DEFAULT 0,
    email_token TEXT,
    phone_verified INTEGER DEFAULT 0,
    mock_otp TEXT,
    reset_token TEXT,
    reset_token_expiry DATETIME,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    rules_confirmed_at DATETIME,
    parent_id INTEGER REFERENCES users(id)
);

-- Batches Table
CREATE TABLE IF NOT EXISTS batches (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    timing_desc TEXT NOT NULL,
    coach_name TEXT,
    max_capacity INTEGER DEFAULT 25,
    is_competition INTEGER DEFAULT 0
);

-- Plans Table
CREATE TABLE IF NOT EXISTS plans (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    duration_days INTEGER NOT NULL,
    fee_amount REAL NOT NULL,
    description TEXT
);

-- Office Use / Admin Endorsement Table
CREATE TABLE IF NOT EXISTS office_use (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER UNIQUE NOT NULL,
    coach_recommendation TEXT,
    pass_type_issued TEXT,
    validity_start DATE,
    validity_end DATE,
    id_card_number TEXT,
    id_card_fee_paid INTEGER DEFAULT 0,
    documents_verified INTEGER DEFAULT 0,
    section_ic_signature TEXT,
    section_ic_date DATE,
    approved_by TEXT,
    approved_at DATETIME,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- User Memberships Table
CREATE TABLE IF NOT EXISTS user_memberships (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    plan_id INTEGER NOT NULL,
    batch_id INTEGER NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    is_active INTEGER DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (plan_id) REFERENCES plans(id),
    FOREIGN KEY (batch_id) REFERENCES batches(id)
);

-- Attendance Table
CREATE TABLE IF NOT EXISTS attendance (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    batch_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    date DATE NOT NULL,
    status TEXT CHECK(status IN ('present', 'absent', 'excused')) NOT NULL DEFAULT 'present',
    marked_by TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(batch_id, user_id, date),
    FOREIGN KEY (batch_id) REFERENCES batches(id),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Competition Race Records Table
CREATE TABLE IF NOT EXISTS race_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    swimmer_id INTEGER NOT NULL,
    meet_date DATE NOT NULL,
    meet_name TEXT NOT NULL,
    stroke TEXT CHECK(stroke IN ('freestyle', 'backstroke', 'breaststroke', 'butterfly', 'individual_medley')) NOT NULL,
    distance TEXT NOT NULL,
    time_seconds REAL NOT NULL,
    time_display TEXT NOT NULL,
    position INTEGER,
    is_personal_best INTEGER DEFAULT 0,
    notes TEXT,
    recorded_by TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (swimmer_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Payments Table
CREATE TABLE IF NOT EXISTS payments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    plan_id INTEGER,
    amount REAL NOT NULL,
    currency TEXT DEFAULT 'INR',
    payment_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    transaction_id TEXT UNIQUE NOT NULL,
    invoice_no TEXT UNIQUE,
    invoice_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    order_id TEXT,
    upi_ref_id TEXT,
    upi_vpa TEXT,
    razorpay_payment_id TEXT,
    razorpay_signature TEXT,
    status TEXT CHECK(status IN ('success', 'failed', 'pending')) DEFAULT 'success',
    payment_method TEXT DEFAULT 'UPI Intent',
    reconciled INTEGER DEFAULT 0,
    reconciled_at DATETIME,
    reconciled_by INTEGER,
    reconciled_notes TEXT,
    receipt_sent_whatsapp INTEGER DEFAULT 0,
    receipt_sent_email INTEGER DEFAULT 0,
    notes TEXT,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (plan_id) REFERENCES plans(id),
    FOREIGN KEY (reconciled_by) REFERENCES users(id) ON DELETE SET NULL
);

-- Financial Audit Trail Table (Tamper-evident record of all revenues, receipts & reconciliations)
CREATE TABLE IF NOT EXISTS financial_audit_trail (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    payment_id INTEGER,
    invoice_no TEXT,
    action TEXT NOT NULL,
    amount REAL,
    performed_by INTEGER,
    performed_by_name TEXT,
    details TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (payment_id) REFERENCES payments(id) ON DELETE SET NULL,
    FOREIGN KEY (performed_by) REFERENCES users(id) ON DELETE SET NULL
);
CREATE INDEX IF NOT EXISTS idx_audit_created ON financial_audit_trail(created_at);
CREATE INDEX IF NOT EXISTS idx_audit_action ON financial_audit_trail(action);
CREATE INDEX IF NOT EXISTS idx_audit_invoice ON financial_audit_trail(invoice_no);
CREATE INDEX IF NOT EXISTS idx_payments_invoice_no ON payments(invoice_no);
CREATE INDEX IF NOT EXISTS idx_payments_reconciled ON payments(reconciled, payment_date);

-- UPI Intent Orders Table (tracks in-flight UPI intent sessions & polling status)
CREATE TABLE IF NOT EXISTS upi_orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id TEXT UNIQUE NOT NULL,
    user_id INTEGER NOT NULL,
    plan_id INTEGER NOT NULL,
    amount REAL NOT NULL,
    currency TEXT DEFAULT 'INR',
    upi_uri TEXT,
    upi_app TEXT,
    status TEXT CHECK(status IN ('PENDING', 'PAID', 'FAILED', 'EXPIRED')) DEFAULT 'PENDING',
    upi_ref_id TEXT,
    transaction_id TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    paid_at DATETIME,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (plan_id) REFERENCES plans(id)
);
CREATE INDEX IF NOT EXISTS idx_upi_orders_order_id ON upi_orders(order_id);


-- In-App Notifications Table
CREATE TABLE IF NOT EXISTS notifications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    message TEXT NOT NULL,
    type TEXT CHECK(type IN ('warning', 'info', 'success', 'danger')) DEFAULT 'warning',
    is_read INTEGER DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Automated Reminder Logs (prevents duplicate emails)
CREATE TABLE IF NOT EXISTS reminder_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    reminder_type TEXT CHECK(reminder_type IN ('7_day', '3_day', '1_day', 'day_of', 'manual_alert')) NOT NULL,
    target_date DATE NOT NULL,
    sent_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    status TEXT DEFAULT 'sent',
    channel TEXT DEFAULT 'email_sms',
    UNIQUE(user_id, reminder_type, target_date),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Application Settings Table
CREATE TABLE IF NOT EXISTS app_settings (
    key TEXT PRIMARY KEY,
    value TEXT
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_phone ON users(phone);
CREATE INDEX IF NOT EXISTS idx_users_role_status ON users(role, status);
CREATE INDEX IF NOT EXISTS idx_memberships_end_date ON user_memberships(end_date, is_active);
CREATE INDEX IF NOT EXISTS idx_race_swimmer ON race_records(swimmer_id, stroke);
CREATE INDEX IF NOT EXISTS idx_attendance_date ON attendance(date, batch_id);

-- Partial unique indexes for parent primary accounts (allowing linked child passes to share parent phone & email)
CREATE UNIQUE INDEX IF NOT EXISTS idx_users_primary_email ON users(email) WHERE parent_id IS NULL;
CREATE UNIQUE INDEX IF NOT EXISTS idx_users_primary_phone ON users(phone) WHERE parent_id IS NULL;
CREATE INDEX IF NOT EXISTS idx_users_parent_id ON users(parent_id);

-- Automated End-of-Day (EOD) Director Reports Archive
CREATE TABLE IF NOT EXISTS eod_reports (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    report_date DATE UNIQUE NOT NULL,
    total_revenue REAL DEFAULT 0.0,
    transaction_count INTEGER DEFAULT 0,
    attendance_count INTEGER DEFAULT 0,
    pending_applications INTEGER DEFAULT 0,
    approved_today INTEGER DEFAULT 0,
    expiring_tomorrow INTEGER DEFAULT 0,
    summary_text TEXT NOT NULL,
    sent_to_phone TEXT,
    sent_to_name TEXT,
    sent_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    status TEXT DEFAULT 'sent'
);
CREATE INDEX IF NOT EXISTS idx_eod_date ON eod_reports(report_date);
