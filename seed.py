"""
TRIC Academy - Database Seeding Script
Populates the database with realistic demo data:
- Super Admin & Head Coach
- Batches (including Competition)
- Plans (Monthly & Quarterly)
- ~15 Members with varied statuses and expiries (in 1, 3, 7 days, today, expired, active, pending)
- Minor members (<18) with guardian info
- Senior members (>50)
- Competition swimmers with race records and Personal Bests
- Sample attendance and payment history
"""

import os
import sqlite3
import uuid
from datetime import date, datetime, timedelta
from werkzeug.security import generate_password_hash
from PIL import Image, ImageDraw, ImageFont

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.path.join(BASE_DIR, 'tric.db')
PHOTOS_DIR = os.path.join(BASE_DIR, 'uploads', 'photos')
os.makedirs(PHOTOS_DIR, exist_ok=True)

def generate_avatar(name, filename, bg_color):
    """Generate a clean colored avatar photo placeholder with initials."""
    img = Image.new('RGB', (160, 200), bg_color)
    draw = ImageDraw.Draw(img)
    initials = "".join([part[0] for part in name.split()[:2]]).upper()
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 48)
    except Exception:
        font = ImageFont.load_default()
    bbox = draw.textbbox((0, 0), initials, font=font)
    w = bbox[2] - bbox[0]
    h = bbox[3] - bbox[1]
    draw.text(((160 - w) // 2, (200 - h) // 2 - 10), initials, fill=(255, 255, 255), font=font)
    path = os.path.join(PHOTOS_DIR, filename)
    img.save(path)
    return filename

def seed():
    if os.path.exists(DATABASE):
        os.remove(DATABASE)
        print("Existing database removed for clean seeding.")

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    # Read and apply schema
    with open(os.path.join(BASE_DIR, 'schema.sql'), 'r') as f:
        cursor.executescript(f.read())

    print("Schema applied successfully.")

    today = date.today()

    # 1. Seed Batches
    batches_data = [
        ("Morning Batch A (Beginners)", "6:00 AM - 7:00 AM (Mon-Sat)", "Coach Shiva", 25, 0),
        ("Morning Batch B (Intermediate)", "7:00 AM - 8:00 AM (Mon-Sat)", "Coach Anand", 25, 0),
        ("Evening Batch (Learn to Swim)", "5:00 PM - 6:00 PM (Mon-Sat)", "Coach Shiva", 30, 0),
        ("Competition Batch", "6:00 PM - 7:30 PM (Daily)", "Head Coach Shiva", 20, 1),
    ]
    cursor.executemany(
        "INSERT INTO batches (name, timing_desc, coach_name, max_capacity, is_competition) VALUES (?, ?, ?, ?, ?)",
        batches_data
    )
    print("Batches seeded.")

    # 2. Seed Plans
    plans_data = [
        ("Monthly Pass", 30, 6000.0, "Daily training session, lane reservation & certified coach guidance."),
        ("Quarterly Pass", 90, 12000.0, "Comprehensive 3-month aquatic training, stroke refinement & priority lane access."),
    ]
    cursor.executemany(
        "INSERT INTO plans (name, duration_days, fee_amount, description) VALUES (?, ?, ?, ?)",
        plans_data
    )
    print("Plans seeded.")

    # 3. Seed Super Admin
    admin_photo = generate_avatar("Shiva Admin", "photo_admin.jpg", (31, 138, 138))
    cursor.execute(
        """
        INSERT INTO users (
            app_no, role, status, name, email, phone, password_hash,
            dob, age, address, pincode, photo_filename, health_declared, rules_agreed,
            signature_name, place, email_verified, phone_verified
        ) VALUES (
            'TRIC-ADMIN-001', 'admin', 'approved', 'Shiva (Section I/C)',
            'admin@tricacademy.com', '9894777333', ?,
            '1985-05-15', 41, 'TRIC Academy Campus, 85/5 Kaliamman Kovil St, #5 Velampalayam', '641652',
            ?, 1, 1, 'Shiva', 'Tirupur', 1, 1
        )
        """,
        (generate_password_hash('admin123'), admin_photo)
    )
    admin_id = cursor.lastrowid
    cursor.execute("INSERT INTO office_use (user_id, id_card_number, approved_by) VALUES (?, 'TRIC-ADMIN', 'TRIC Authority')", (admin_id,))

    # 4. Seed Coaches
    coach_photo = generate_avatar("Coach Shiva", "photo_coach_shiva.jpg", (19, 91, 91))
    cursor.execute(
        """
        INSERT INTO users (
            app_no, role, status, name, email, phone, password_hash,
            dob, age, address, pincode, photo_filename, health_declared, rules_agreed,
            signature_name, place, email_verified, phone_verified
        ) VALUES (
            'TRIC-COACH-001', 'coach', 'approved', 'Coach Shiva',
            'coach@tricacademy.com', '9894730333', ?,
            '1988-08-20', 38, 'Velampalayam, Tirupur', '641652',
            ?, 1, 1, 'Coach Shiva', 'Tirupur', 1, 1
        )
        """,
        (generate_password_hash('coach123'), coach_photo)
    )
    coach1_id = cursor.lastrowid
    cursor.execute("INSERT INTO office_use (user_id, id_card_number, approved_by) VALUES (?, 'TRIC-COACH-1', 'Admin')", (coach1_id,))

    coach2_photo = generate_avatar("Coach Anand", "photo_coach_anand.jpg", (2, 132, 199))
    cursor.execute(
        """
        INSERT INTO users (
            app_no, role, status, name, email, phone, password_hash,
            dob, age, address, pincode, photo_filename, health_declared, rules_agreed,
            signature_name, place, email_verified, phone_verified
        ) VALUES (
            'TRIC-COACH-002', 'coach', 'approved', 'Coach Anand',
            'coach.anand@tricacademy.com', '9894757333', ?,
            '1992-11-10', 33, 'Avinashi Road, Tirupur', '641654',
            ?, 1, 1, 'Coach Anand', 'Tirupur', 1, 1
        )
        """,
        (generate_password_hash('coach123'), coach2_photo)
    )
    coach2_id = cursor.lastrowid
    cursor.execute("INSERT INTO office_use (user_id, id_card_number, approved_by) VALUES (?, 'TRIC-COACH-2', 'Admin')", (coach2_id,))

    # 5. Seed Members with varied expiry dates and roles
    members_spec = [
        # (name, email, phone, pwd, age, dob, pass_req, batch_id, plan_id, days_remaining, status, is_comp, guardian, occup)
        # Competition Swimmers
        ("Karthik Swaminathan", "karthik.swim@gmail.com", "9843211001", "karthik123", 19, "2007-03-12", "competition", 4, 2, 45, "approved", 1, None, None),
        ("Deepak Rajan", "deepak.rajan@gmail.com", "9843211002", "deepak123", 16, "2010-06-18", "competition", 4, 1, 1, "approved", 1, "Rajan Sundaram", "Textile Manufacturer"),
        ("Ananya Venkatesh", "ananya.v@gmail.com", "9843211003", "ananya123", 15, "2011-09-24", "competition", 4, 1, 3, "approved", 1, "Venkatesh K.", "Software Engineer"),
        ("Manoj Kumar", "manoj.swim@gmail.com", "9843211004", "manoj123", 22, "2004-01-14", "competition", 4, 2, 7, "approved", 1, None, None),

        # Regular Members (Varied expiries)
        ("Priya Dharshini", "priya.learner@gmail.com", "9843211005", "priya123", 26, "2000-04-10", "learn_to_swim", 1, 1, 20, "approved", 0, None, None),
        ("Suresh Balaji", "suresh.b@gmail.com", "9843211006", "suresh123", 34, "1992-02-15", "learn_to_swim", 2, 1, 0, "approved", 0, None, None), # Expires today
        ("Vijay Anand", "vijay.anand@gmail.com", "9843211007", "vijay123", 29, "1997-07-22", "learn_to_swim", 3, 2, 60, "approved", 0, None, None),
        ("Ramesh Chandran", "ramesh.c@gmail.com", "9843211008", "ramesh123", 53, "1973-10-05", "learn_to_swim", 1, 1, -5, "approved", 0, None, None), # Senior (>50), expired
        ("Kavitha Subramaniam", "kavitha.s@gmail.com", "9843211009", "kavitha123", 24, "2002-12-08", "learn_to_swim", 2, 1, 18, "approved", 0, None, None),
        ("Gokul Krishnan", "gokul.k@gmail.com", "9843211010", "gokul123", 12, "2014-05-30", "learn_to_swim", 3, 1, 12, "approved", 0, "Krishnan S.", "Merchant"), # Minor

        # Pending Applicants (Awaiting Office Verification)
        ("Aravind Swamy", "aravind.new@gmail.com", "9843211011", "aravind123", 27, "1999-09-15", "learn_to_swim", None, None, None, "pending", 0, None, None),
        ("Divya Bharathi", "divya.comp@gmail.com", "9843211012", "divya123", 17, "2009-02-20", "competition", None, None, None, "pending", 1, "Bharathi R.", "Bank Officer"),
        ("Muruganandham S.", "murugan.senior@gmail.com", "9843211013", "murugan123", 56, "1970-04-18", "learn_to_swim", None, None, None, "pending", 0, None, None), # Senior >50
        ("Naveen Prasad", "naveen.p@gmail.com", "9843211014", "naveen123", 21, "2005-08-11", "learn_to_swim", None, None, None, "pending", 0, None, None),
        ("Subashini Devi", "subashini.d@gmail.com", "9843211015", "suba123", 31, "1995-11-03", "competition", None, None, None, "pending", 1, None, None),
        ("Santhosh", "sandy.dilsehe@gmail.com", "9843211099", "password123", 31, "1995-06-15", "learn_to_swim", 1, 2, 90, "approved", 0, None, None),
    ]

    member_ids = {}

    for idx, (name, email, phone, pwd, age, dob_s, pass_req, batch_id, plan_id, days_rem, status, is_comp, guard, occup) in enumerate(members_spec, 1):
        app_no = f"TRIC-2026-{100 + idx}"
        photo_fn = generate_avatar(name, f"photo_member_{idx}.jpg", (50 + idx * 10, 100 + idx * 5, 140 + idx * 4))
        pwd_hash = generate_password_hash(pwd)

        cursor.execute(
            """
            INSERT INTO users (
                app_no, role, status, name, email, phone, password_hash,
                dob, age, address, pincode, guardian_name, guardian_occupation,
                experience, pass_type_requested, photo_filename, health_declared,
                rules_agreed, signature_name, place, email_verified, phone_verified, mock_otp
            ) VALUES (?, 'member', ?, ?, ?, ?, ?, ?, ?, ?, '641652', ?, ?, ?, ?, ?, 1, 1, ?, 'Tirupur', 1, 1, '123456')
            """,
            (
                app_no, status, name, email, phone, pwd_hash,
                dob_s, age, f"Door No. {idx * 7}, Kaliamman Kovil Street, Velampalayam",
                guard, occup,
                "Intermediate competition experience" if is_comp else "Beginner enthusiast",
                pass_req, photo_fn, name
            )
        )
        u_id = cursor.lastrowid
        member_ids[name] = u_id

        # Office Use record
        id_card = f"TRIC-ID-2026-{u_id:04d}" if status == 'approved' else None
        start_d = None
        end_d = None
        if days_rem is not None and plan_id:
            end_d = today + timedelta(days=days_rem)
            dur = 90 if plan_id == 2 else 30
            start_d = end_d - timedelta(days=dur)

        cursor.execute(
            """
            INSERT INTO office_use (
                user_id, coach_recommendation, pass_type_issued, validity_start, validity_end,
                id_card_number, id_card_fee_paid, documents_verified, section_ic_signature,
                section_ic_date, approved_by, approved_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                u_id,
                "Strong stroke technique, approved for squad" if is_comp else "General pool fitness",
                pass_req,
                start_d, end_d, id_card,
                1 if status == 'approved' else 0,
                1 if status == 'approved' else 0,
                "Shiva" if status == 'approved' else None,
                today if status == 'approved' else None,
                "Shiva (Admin)" if status == 'approved' else None,
                datetime.now() if status == 'approved' else None
            )
        )

        # Active Membership & Payment
        if status == 'approved' and batch_id and plan_id and start_d and end_d:
            cursor.execute(
                """
                INSERT INTO user_memberships (user_id, plan_id, batch_id, start_date, end_date, is_active)
                VALUES (?, ?, ?, ?, ?, 1)
                """,
                (u_id, plan_id, batch_id, start_d, end_d)
            )
            # Payment record
            fee = 3800.0 if plan_id == 2 else 1500.0
            txn_id = f"TRIC-TXN-{uuid.uuid4().hex[:8].upper()}"
            order_id = f"order_{uuid.uuid4().hex[:12]}"
            pay_id = f"pay_{uuid.uuid4().hex[:12]}"
            cursor.execute(
                """
                INSERT INTO payments (user_id, plan_id, amount, currency, payment_date, transaction_id, order_id, razorpay_payment_id, status, payment_method, notes)
                VALUES (?, ?, ?, 'INR', ?, ?, ?, ?, 'success', 'Razorpay (Test Mode)', 'Membership Pass Issue')
                """,
                (u_id, plan_id, fee, start_d, txn_id, order_id, pay_id)
            )

            # If nearing end date (within 7 days), insert in-app notification
            if days_rem is not None and days_rem <= 7 and days_rem >= 0:
                day_text = "today" if days_rem == 0 else (f"in {days_rem} days" if days_rem > 1 else "tomorrow")
                cursor.execute(
                    """
                    INSERT INTO notifications (user_id, title, message, type, is_read)
                    VALUES (?, ?, ?, 'warning', 0)
                    """,
                    (
                        u_id,
                        f"Membership Expiry Alert ({day_text.capitalize()})",
                        f"Your TRIC Academy membership will expire {day_text} on {end_d}. Please renew online via Razorpay to continue your batch slot."
                    )
                )

    print(f"Seeded {len(members_spec)} members.")

    # 6. Seed Race Records for Competition Swimmers
    karthik_id = member_ids["Karthik Swaminathan"]
    deepak_id = member_ids["Deepak Rajan"]
    ananya_id = member_ids["Ananya Venkatesh"]

    races = [
        # Karthik
        (karthik_id, "2026-08-15", "Independence Day District Meet, Coimbatore", "freestyle", "50m", 26.42, "26.42s", 1, 0, "Good breakout and underwater kick", "Coach Shiva"),
        (karthik_id, "2026-09-20", "State Aquatic Championship, Chennai", "freestyle", "50m", 25.80, "25.80s", 1, 1, "Personal best! Gold medal finish", "Coach Shiva"),
        (karthik_id, "2026-08-15", "Independence Day District Meet, Coimbatore", "freestyle", "100m", 57.10, "57.10s", 2, 0, "Pacing was consistent on second 50m", "Coach Shiva"),
        (karthik_id, "2026-09-20", "State Aquatic Championship, Chennai", "freestyle", "100m", 55.95, "55.95s", 1, 1, "New academy record for 100m free", "Coach Shiva"),
        (karthik_id, "2026-10-10", "South Zone Inter-Club Invitation, Madurai", "butterfly", "50m", 27.65, "27.65s", 2, 1, "Quick arm turnover, tight finish", "Coach Shiva"),
        (karthik_id, "2026-10-10", "South Zone Inter-Club Invitation, Madurai", "backstroke", "100m", 64.20, "1:04.20", 3, 1, "Clean turn, solid catch", "Coach Shiva"),

        # Deepak
        (deepak_id, "2026-08-15", "Independence Day District Meet, Coimbatore", "breaststroke", "50m", 33.50, "33.50s", 2, 0, "Powerful glide, check head position", "Coach Shiva"),
        (deepak_id, "2026-09-20", "State Aquatic Championship, Chennai", "breaststroke", "50m", 32.10, "32.10s", 1, 1, "Gold medal in Boys Under-17", "Coach Shiva"),
        (deepak_id, "2026-09-20", "State Aquatic Championship, Chennai", "breaststroke", "100m", 71.40, "1:11.40", 2, 1, "Silver medal", "Coach Shiva"),
        (deepak_id, "2026-10-10", "South Zone Inter-Club Invitation, Madurai", "freestyle", "50m", 27.80, "27.80s", 4, 1, "Sprint training showing progress", "Coach Shiva"),

        # Ananya
        (ananya_id, "2026-08-15", "Independence Day District Meet, Coimbatore", "backstroke", "50m", 34.20, "34.20s", 1, 0, "Strong backstroke dolphin kicks", "Coach Shiva"),
        (ananya_id, "2026-09-20", "State Aquatic Championship, Chennai", "backstroke", "50m", 32.90, "32.90s", 1, 1, "State champion in Girls U-17", "Coach Shiva"),
        (ananya_id, "2026-09-20", "State Aquatic Championship, Chennai", "backstroke", "100m", 72.10, "1:12.10", 1, 1, "Controlled tempo throughout", "Coach Shiva"),
        (ananya_id, "2026-10-10", "South Zone Inter-Club Invitation, Madurai", "freestyle", "100m", 63.80, "1:03.80", 2, 1, "Good second half split", "Coach Shiva"),
    ]

    cursor.executemany(
        """
        INSERT INTO race_records (
            swimmer_id, meet_date, meet_name, stroke, distance,
            time_seconds, time_display, position, is_personal_best, notes, recorded_by
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        races
    )
    print("Race records seeded.")

    # 7. Seed Sample Attendance for Approved Members over last 5 days
    approved_members = cursor.execute(
        """
        SELECT u.id, m.batch_id
        FROM users u
        JOIN user_memberships m ON u.id = m.user_id AND m.is_active = 1
        WHERE u.status = 'approved'
        """
    ).fetchall()

    for day_offset in range(1, 6):
        att_date = today - timedelta(days=day_offset)
        # Skip Sundays
        if att_date.weekday() == 6:
            continue
        for mem_id, b_id in approved_members:
            status_val = 'present' if (mem_id + day_offset) % 7 != 0 else 'absent'
            cursor.execute(
                """
                INSERT OR IGNORE INTO attendance (batch_id, user_id, date, status, marked_by)
                VALUES (?, ?, ?, ?, 'Coach Shiva')
                """,
                (b_id, mem_id, att_date, status_val)
            )

    print("Attendance seeded.")

    conn.commit()
    conn.close()
    print("Database seeding completed successfully! All demo users ready.")

if __name__ == '__main__':
    seed()
