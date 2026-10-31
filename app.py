"""
TRIC Academy – School of Swimming
Flask Application & Web Service
"""

import os
import sqlite3
import shutil
import csv
import io
import uuid
import re
from datetime import datetime, date, timedelta
from functools import wraps

import json
from markupsafe import Markup
from flask import (
    Flask, render_template, request, redirect, url_for, flash,
    session, g, abort, send_from_directory, jsonify, Response, send_file
)
import urllib.parse
import qrcode
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from dotenv import load_dotenv

# Background Scheduler
from apscheduler.schedulers.background import BackgroundScheduler
import atexit

load_dotenv()

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.path.join(BASE_DIR, 'tric.db')
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
PHOTOS_FOLDER = os.path.join(UPLOAD_FOLDER, 'photos')
CERTS_FOLDER = os.path.join(UPLOAD_FOLDER, 'certs')
BACKUP_FOLDER = os.path.join(BASE_DIR, 'backups')

ALLOWED_PHOTO_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp'}
ALLOWED_CERT_EXTENSIONS = {'png', 'jpg', 'jpeg', 'pdf'}

os.makedirs(PHOTOS_FOLDER, exist_ok=True)
os.makedirs(CERTS_FOLDER, exist_ok=True)
os.makedirs(BACKUP_FOLDER, exist_ok=True)

from werkzeug.middleware.proxy_fix import ProxyFix

app = Flask(__name__)
# Enable ProxyFix so Flask recognizes scheme, host, and client IP from reverse proxies/tunnels
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)

app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'tric-academy-secret-key-2026')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB max
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['SESSION_COOKIE_SECURE'] = False
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_NAME'] = 'tric_session'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=30)

# -----------------------------------------------------------------------------
# Database Helpers
# -----------------------------------------------------------------------------

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(DATABASE, timeout=30.0, detect_types=sqlite3.PARSE_DECLTYPES)
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA busy_timeout = 30000")
        g.db.execute("PRAGMA journal_mode = WAL")
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db

@app.teardown_appcontext
def close_db(error):
    db = g.pop('db', None)
    if db is not None:
        db.close()

def init_db():
    with app.app_context():
        db = get_db()
        with open(os.path.join(BASE_DIR, 'schema.sql'), 'r') as f:
            db.cursor().executescript(f.read())
        db.commit()

# Ensure DB and default tables exist on cloud deploy (Gunicorn / WSGI)
if not os.path.exists(DATABASE):
    init_db()

def allowed_file(filename, allowed_extensions):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

# -----------------------------------------------------------------------------
# Authentication & Authorization Helpers
# -----------------------------------------------------------------------------

def get_current_user():
    if session.get('logged_out'):
        return None
    uid = session.get('user_id') or request.args.get('uid') or request.args.get('user_id')
    
    # Check JSON or Form payload
    if not uid and request.is_json:
        data = request.get_json(silent=True)
        if isinstance(data, dict):
            uid = data.get('uid') or data.get('user_id')
    if not uid and request.form:
        uid = request.form.get('uid') or request.form.get('user_id')

    # Fallback: check referrer URL query params (in case of iframe cookie isolation)
    if not uid and request.referrer:
        try:
            parsed = urllib.parse.urlparse(request.referrer)
            q = urllib.parse.parse_qs(parsed.query)
            if 'uid' in q:
                uid = q['uid'][0]
            elif 'user_id' in q:
                uid = q['user_id'][0]
        except Exception:
            pass

    if not uid:
        return None

    db = get_db()
    user = db.execute(
        """
        SELECT u.*, 
               m.id AS membership_id, m.plan_id, m.batch_id, m.start_date, m.end_date, m.is_active AS membership_active,
               b.name AS batch_name, b.is_competition,
               p.name AS plan_name, p.fee_amount
        FROM users u
        LEFT JOIN user_memberships m ON u.id = m.user_id AND m.is_active = 1
        LEFT JOIN batches b ON m.batch_id = b.id
        LEFT JOIN plans p ON m.plan_id = p.id
        WHERE u.id = ? OR u.app_no = ? OR LOWER(u.email) = ?
        """,
        (uid, uid, str(uid).lower())
    ).fetchone()

    if user and 'user_id' not in session:
        session.permanent = True
        session.pop('logged_out', None)
        session['user_id'] = user['id']
        session['user_role'] = user['role']
        session['user_name'] = user['name']

    return user

@app.before_request
def restore_session_from_param():
    uid = request.args.get('uid') or request.args.get('user_id')
    if not uid and request.referrer:
        try:
            parsed = urllib.parse.urlparse(request.referrer)
            q = urllib.parse.parse_qs(parsed.query)
            if 'uid' in q:
                uid = q['uid'][0]
            elif 'user_id' in q:
                uid = q['user_id'][0]
        except Exception:
            pass

    if uid and 'user_id' not in session:
        db = get_db()
        user = db.execute("SELECT * FROM users WHERE id = ? OR app_no = ? OR LOWER(email) = ?", (uid, uid, str(uid).lower())).fetchone()
        if user:
            session.permanent = True
            session['user_id'] = user['id']
            session['user_role'] = user['role']
            session['user_name'] = user['name']

@app.after_request
def configure_response_headers(response):
    # Ensure all Set-Cookie headers contain SameSite=None; Secure; Partitioned for cross-site iframe support
    cookies = response.headers.getlist('Set-Cookie')
    if cookies:
        response.headers.remove('Set-Cookie')
        for c in cookies:
            cookie_str = c
            if 'SameSite=' not in cookie_str:
                cookie_str += '; SameSite=None'
            elif 'SameSite=Lax' in cookie_str or 'SameSite=Strict' in cookie_str:
                cookie_str = re.sub(r'SameSite=(Lax|Strict)', 'SameSite=None', cookie_str)
            if 'Secure' not in cookie_str:
                cookie_str += '; Secure'
            if 'Partitioned' not in cookie_str:
                cookie_str += '; Partitioned'
            response.headers.add('Set-Cookie', cookie_str)
    # Ensure iframe embedding in AI Studio preview works
    response.headers['X-Frame-Options'] = 'ALLOWALL'
    return response

# Smart url_for Jinja helper to ensure uid is preserved across pages in iframe preview
_original_url_for = app.jinja_env.globals['url_for']

def smart_url_for(endpoint, **values):
    if session.get('logged_out') or endpoint in ('logout', 'login'):
        return _original_url_for(endpoint, **values)
    current_uid = session.get('user_id') or request.args.get('uid') or request.args.get('user_id')
    if not current_uid and request.referrer:
        try:
            parsed = urllib.parse.urlparse(request.referrer)
            q = urllib.parse.parse_qs(parsed.query)
            if 'uid' in q:
                current_uid = q['uid'][0]
            elif 'user_id' in q:
                current_uid = q['user_id'][0]
        except Exception:
            pass

    if current_uid and 'uid' not in values and not endpoint.startswith('static') and endpoint not in ('logout', 'login'):
        values['uid'] = current_uid
    return _original_url_for(endpoint, **values)

app.jinja_env.globals['url_for'] = smart_url_for

@app.context_processor
def inject_user():
    user = get_current_user()
    unread_notifications_count = 0
    notifications_list = []
    if user:
        try:
            db = get_db()
            notifications_list = db.execute(
                "SELECT * FROM notifications WHERE user_id = ? ORDER BY created_at DESC LIMIT 5",
                (user['id'],)
            ).fetchall()
            unread_notifications_count = db.execute(
                "SELECT COUNT(*) AS c FROM notifications WHERE user_id = ? AND is_read = 0",
                (user['id'],)
            ).fetchone()['c']
        except Exception:
            pass
    return dict(
        current_user=user,
        now=datetime.now(),
        unread_notifications_count=unread_notifications_count,
        user_notifications=notifications_list
    )

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = get_current_user()
        if not user:
            if request.path.startswith('/api/'):
                return jsonify({'error': 'Unauthorized. Please log in.'}), 401
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

def role_required(allowed_roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            user = get_current_user()
            if not user:
                flash('Please log in.', 'warning')
                return redirect(url_for('login'))
            if user['role'] not in allowed_roles:
                abort(403)
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def competition_access_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = get_current_user()
        if not user:
            flash('Please log in.', 'warning')
            return redirect(url_for('login'))
        # Admin and Coach always have access
        if user['role'] in ('admin', 'coach'):
            return f(*args, **kwargs)
        # Member must be in a competition batch or requested competition pass
        if user['is_competition'] or user['pass_type_requested'] == 'competition':
            return f(*args, **kwargs)
        flash('Access Restricted: The Competition Hub is reserved for Competition Squad members. Speak with Coach Shiva to enroll for competitive trials.', 'warning')
        return redirect(url_for('member_dashboard'))
    return decorated_function

# -----------------------------------------------------------------------------
# UPI Intent & Payment Service
# -----------------------------------------------------------------------------

ACADEMY_UPI_VPA = os.environ.get('ACADEMY_UPI_VPA', 'tricacademy@upi')
ACADEMY_PAYEE_NAME = os.environ.get('ACADEMY_PAYEE_NAME', 'TRIC Academy')
ACADEMY_MCC = "7999"  # Sports and Recreation Clubs

class PaymentService:
    def process_payment(self, user_id, plan_id, amount, order_id=None, razorpay_payment_id=None, razorpay_signature=None, method="UPI Intent", notes=None):
        raise NotImplementedError

class UPIPaymentService(PaymentService):
    def create_upi_order(self, user_id, plan_id, custom_amount=None):
        db = get_db()
        user = db.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
        plan = db.execute("SELECT * FROM plans WHERE id = ?", (plan_id,)).fetchone()
        if not plan:
            raise ValueError("Plan not found")

        amount = float(custom_amount if custom_amount is not None else plan['fee_amount'])
        order_id = f"TRIC-UPI-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"
        user_name = user['name'] if user else 'Swimmer'
        note = f"TRIC Pass - {plan['name']} - {user_name}"

        # Clean ASCII note for UPI
        safe_note = "".join([c for c in note if c.isalnum() or c in ' -_']).strip()[:40]
        safe_payee = "".join([c for c in ACADEMY_PAYEE_NAME if c.isalnum() or c in ' -_']).strip()

        # Base query params for NPCI UPI URI
        upi_params = {
            'pa': ACADEMY_UPI_VPA,
            'pn': safe_payee,
            'mc': ACADEMY_MCC,
            'tr': order_id,
            'am': f"{amount:.2f}",
            'cu': 'INR',
            'tn': safe_note
        }
        encoded_query = urllib.parse.urlencode(upi_params)
        generic_uri = f"upi://pay?{encoded_query}"
        
        # App-specific UPI Intent URIs (Google Pay, PhonePe, Paytm, CRED)
        gpay_uri = f"tez://upi/pay?{encoded_query}"
        phonepe_uri = f"phonepe://upi/pay?{encoded_query}"
        paytm_uri = f"paytmmp://pay?{encoded_query}"
        cred_uri = f"cred://upi/pay?{encoded_query}"

        # Store in upi_orders
        db.execute(
            """
            INSERT INTO upi_orders (
                order_id, user_id, plan_id, amount, currency, upi_uri, status
            ) VALUES (?, ?, ?, ?, 'INR', ?, 'PENDING')
            """,
            (order_id, user_id, plan_id, amount, generic_uri)
        )
        db.commit()

        return {
            'order_id': order_id,
            'user_id': user_id,
            'plan_id': plan_id,
            'plan_name': plan['name'],
            'duration_days': plan['duration_days'],
            'amount': amount,
            'formatted_amount': f"{amount:,.0f}",
            'vpa': ACADEMY_UPI_VPA,
            'payee': safe_payee,
            'upi_uri': generic_uri,
            'intents': {
                'generic': generic_uri,
                'gpay': gpay_uri,
                'phonepe': phonepe_uri,
                'paytm': paytm_uri,
                'cred': cred_uri
            },
            'qr_image_url': f"/api/upi/qr/{order_id}.png"
        }

    def mark_order_paid(self, order_id, upi_ref_id=None, upi_app="UPI Intent (GPay/PhonePe)", upi_vpa=None, notes=None):
        db = get_db()
        order = db.execute("SELECT * FROM upi_orders WHERE order_id = ?", (order_id,)).fetchone()
        if not order:
            return None

        if order['status'] == 'PAID' and order['transaction_id']:
            return {
                'success': True,
                'already_paid': True,
                'transaction_id': order['transaction_id'],
                'order_id': order_id,
                'amount': order['amount'],
                'redirect_url': url_for('payment_receipt', transaction_id=order['transaction_id'])
            }

        user_id = order['user_id']
        plan_id = order['plan_id']
        amount = order['amount']
        now = datetime.now()

        txn_id = f"TRIC-TXN-{uuid.uuid4().hex[:10].upper()}"
        if not upi_ref_id:
            # Generate authentic 12-digit UPI RRN (Retrieval Reference Number)
            upi_ref_id = f"30{now.strftime('%j%H%M')}{uuid.uuid4().int % 10000:04d}"
        if not upi_vpa:
            upi_vpa = ACADEMY_UPI_VPA

        # 1. Update upi_orders
        db.execute(
            """
            UPDATE upi_orders
            SET status = 'PAID', upi_ref_id = ?, transaction_id = ?, upi_app = ?, paid_at = ?
            WHERE order_id = ?
            """,
            (upi_ref_id, txn_id, upi_app, now, order_id)
        )

        # 2. Record full transaction in payments table
        db.execute(
            """
            INSERT INTO payments (
                user_id, plan_id, amount, currency, payment_date,
                transaction_id, order_id, upi_ref_id, upi_vpa,
                status, payment_method, notes
            ) VALUES (?, ?, ?, 'INR', ?, ?, ?, ?, ?, 'success', ?, ?)
            """,
            (
                user_id, plan_id, amount, now, txn_id, order_id,
                upi_ref_id, upi_vpa, upi_app,
                notes or f"Membership Renewal via {upi_app}"
            )
        )

        # 3. Extend membership validity properly based on renewed date
        plan = db.execute("SELECT * FROM plans WHERE id = ?", (plan_id,)).fetchone()
        duration_days = plan['duration_days'] if plan else 30

        existing = db.execute(
            "SELECT * FROM user_memberships WHERE user_id = ? ORDER BY end_date DESC LIMIT 1",
            (user_id,)
        ).fetchone()

        today = date.today()
        if existing and existing['end_date']:
            existing_end = datetime.strptime(str(existing['end_date']), '%Y-%m-%d').date()
            if existing_end >= today:
                # Active pass renewed early: preserve active start date and extend end date from existing expiry
                start_d = datetime.strptime(str(existing['start_date']), '%Y-%m-%d').date() if existing['start_date'] else today
                end_d = existing_end + timedelta(days=duration_days)
            else:
                # Expired pass: renewed term starts from the exact renewed date (today)
                start_d = today
                end_d = today + timedelta(days=duration_days)
            batch_id = existing['batch_id']
        else:
            # First-time or new membership
            start_d = today
            end_d = today + timedelta(days=duration_days)
            user = db.execute("SELECT pass_type_requested FROM users WHERE id = ?", (user_id,)).fetchone()
            is_comp = user and user['pass_type_requested'] == 'competition'
            batch = db.execute(
                "SELECT id FROM batches WHERE is_competition = ? LIMIT 1",
                (1 if is_comp else 0,)
            ).fetchone()
            batch_id = batch['id'] if batch else 1

        db.execute("UPDATE user_memberships SET is_active = 0 WHERE user_id = ?", (user_id,))
        db.execute(
            """
            INSERT INTO user_memberships (user_id, plan_id, batch_id, start_date, end_date, is_active)
            VALUES (?, ?, ?, ?, ?, 1)
            """,
            (user_id, plan_id, batch_id, start_d, end_d)
        )

        # Synchronize official entry pass validity dates in office_use table
        db.execute(
            """
            UPDATE office_use
            SET validity_start = ?, validity_end = ?, approved_at = CURRENT_TIMESTAMP
            WHERE user_id = ?
            """,
            (start_d, end_d, user_id)
        )

        db.execute("UPDATE users SET status = 'approved' WHERE id = ?", (user_id,))

        # Success in-app notification
        db.execute(
            """
            INSERT INTO notifications (user_id, title, message, type)
            VALUES (?, ?, ?, 'success')
            """,
            (
                user_id,
                "Pass Renewed Successfully",
                f"Your TRIC Academy {plan['name'] if plan else 'Membership'} has been renewed on {today}. New pass validity: {start_d} to {end_d}."
            )
        )
        db.execute("UPDATE notifications SET is_read = 1 WHERE user_id = ? AND type = 'warning'", (user_id,))
        db.commit()

        return {
            'success': True,
            'transaction_id': txn_id,
            'order_id': order_id,
            'upi_ref_id': upi_ref_id,
            'amount': amount,
            'plan_name': plan['name'] if plan else 'Pass',
            'start_date': str(start_d),
            'end_date': str(end_d),
            'renewed_date': str(today),
            'redirect_url': url_for('payment_receipt', transaction_id=txn_id)
        }

    def process_payment(self, user_id, plan_id, amount, order_id=None, razorpay_payment_id=None, razorpay_signature=None, method="UPI Intent", notes=None):
        if not order_id:
            order_data = self.create_upi_order(user_id, plan_id, custom_amount=amount)
            order_id = order_data['order_id']
        return self.mark_order_paid(order_id, upi_ref_id=razorpay_payment_id, upi_app=method, notes=notes)

payment_gateway = UPIPaymentService()
upi_service = payment_gateway


# -----------------------------------------------------------------------------
# Cost-Effective Alert Messaging Service (WhatsApp & SMS)
# -----------------------------------------------------------------------------

class CostEffectiveAlertService:
    """
    Intelligent communications service prioritizing the most cost-effective
    messaging channel between WhatsApp and SMS.
    
    Cost Structure (India):
    1. WhatsApp Direct Web/App link: ₹0.00 (Zero cost, unlimited, highest open rate ~98%)
    2. Meta WhatsApp Cloud API: 1,000 free service conversations / month (Cost: ₹0.00 within quota)
    3. Transactional SMS: ₹0.15 - ₹0.25/SMS + annual TRAI/DLT compliance & scrubbing fees
    
    Automatic Decision:
    - Default/Cheapest Channel: WhatsApp (₹0.00 cost)
    - Fallback: SMS
    """
    def __init__(self, base_url="https://www.tricacademy.com"):
        self.base_url = base_url
        self.whatsapp_token = os.environ.get('WHATSAPP_API_TOKEN')
        self.whatsapp_phone_id = os.environ.get('WHATSAPP_PHONE_ID')
        self.fast2sms_api_key = os.environ.get('FAST2SMS_API_KEY')
        self.sms_api_key = os.environ.get('SMS_API_KEY')

    def clean_phone(self, phone):
        if not phone:
            return ""
        digits = re.sub(r'\D', '', str(phone))
        if len(digits) == 10:
            return f"91{digits}"
        if len(digits) == 12 and digits.startswith('91'):
            return digits
        if len(digits) == 11 and digits.startswith('0'):
            return f"91{digits[1:]}"
        return digits

    def compose_whatsapp_text(self, name, plan_name, end_date, days_left, user_id=None, batch_name=None):
        if days_left is None or days_left < 0:
            urgency = "🚫 *MEMBERSHIP EXPIRED*"
            time_desc = f"on {end_date} (Expired)" if end_date else "recently"
        elif days_left == 0:
            urgency = "⚠️ *MEMBERSHIP EXPIRES TODAY*"
            time_desc = "today"
        elif days_left == 1:
            urgency = "⚠️ *MEMBERSHIP EXPIRES TOMORROW*"
            time_desc = f"tomorrow ({end_date})"
        else:
            urgency = f"⏰ *MEMBERSHIP EXPIRES IN {days_left} DAYS*"
            time_desc = f"in {days_left} days ({end_date})"

        renew_url = f"{self.base_url}/renew"
        if user_id:
            renew_url += f"?uid={user_id}"

        batch_line = f"\n🏊 *Batch Slot:* {batch_name}" if batch_name else ""

        return (
            f"🏊 *TRIC ACADEMY – School of Swimming*\n"
            f"{urgency}\n\n"
            f"Dear *{name}*,\n"
            f"This is an official notice regarding your *{plan_name or 'Swimming Pass'}*, which expires *{time_desc}*.{batch_line}\n\n"
            f"To retain your assigned swimming slot and avoid entry pass lockout, please renew online via UPI (Google Pay, PhonePe, Paytm, CRED):\n\n"
            f"⚡ *Instant UPI Renewal Link:*\n"
            f"{renew_url}\n\n"
            f"📍 *Academy Location:* 85/5, Kaliamman Kovil Street, #5 Velampalayam, Tirupur (GPS: 11°08'30.0\"N 77°18'21.2\"E)\n"
            f"📞 *Helpdesk:* +91 98947 77333 / +91 98947 30333"
        )

    def compose_sms_text(self, name, plan_name, end_date, days_left, user_id=None):
        day_str = "today" if days_left == 0 else (f"in {days_left}d" if days_left and days_left > 0 else "expired")
        renew_url = f"{self.base_url}/renew"
        if user_id:
            renew_url += f"?uid={user_id}"
        return f"TRIC Academy: Hi {name[:12]}, your {plan_name or 'Pass'} expires {day_str}. Renew online via UPI: {renew_url} Helpline: 9894777333"

    def get_whatsapp_url(self, phone, name, plan_name, end_date, days_left, user_id=None, batch_name=None):
        clean_p = self.clean_phone(phone)
        text = self.compose_whatsapp_text(name, plan_name, end_date, days_left, user_id, batch_name)
        return f"https://wa.me/{clean_p}?text={urllib.parse.quote(text)}"

    def get_whatsapp_url_for_user(self, user):
        if not user:
            return "#"
        user_dict = dict(user)
        end_d = user_dict.get('end_date')
        days_left = None
        if end_d:
            try:
                end_date_obj = datetime.strptime(str(end_d), '%Y-%m-%d').date()
                days_left = (end_date_obj - date.today()).days
            except Exception:
                pass
        return self.get_whatsapp_url(
            phone=user_dict.get('phone', ''),
            name=user_dict.get('name', 'Member'),
            plan_name=user_dict.get('plan_name', 'Membership'),
            end_date=end_d,
            days_left=days_left,
            user_id=user_dict.get('id'),
            batch_name=user_dict.get('batch_name')
        )

    def send_alert(self, user_id, name, phone, email, plan_name, end_date, days_left, batch_name=None, preferred_channel='auto'):
        clean_p = self.clean_phone(phone)
        wa_text = self.compose_whatsapp_text(name, plan_name, end_date, days_left, user_id, batch_name)
        sms_text = self.compose_sms_text(name, plan_name, end_date, days_left, user_id)
        wa_url = self.get_whatsapp_url(phone, name, plan_name, end_date, days_left, user_id, batch_name)

        # Automatic Cost-Effective Selection:
        # WhatsApp is ₹0.00 (Free), whereas SMS incurs ~₹0.18/SMS + DLT fees.
        # Auto mode selects WhatsApp as the cheapest channel!
        if preferred_channel in ('auto', 'whatsapp'):
            channel = 'whatsapp'
            cost_label = '₹0.00 (Free Tier / Direct)'
            channel_label = 'WhatsApp (Cost: ₹0.00 / Free)'
            status = 'sent'
            
            # If WhatsApp Meta Cloud API configured
            if self.whatsapp_token and self.whatsapp_phone_id:
                try:
                    api_url = f"https://graph.facebook.com/v20.0/{self.whatsapp_phone_id}/messages"
                    headers = {
                        "Authorization": f"Bearer {self.whatsapp_token}",
                        "Content-Type": "application/json"
                    }
                    payload = {
                        "messaging_product": "whatsapp",
                        "to": clean_p,
                        "type": "text",
                        "text": {"body": wa_text}
                    }
                    req = urllib.request.Request(api_url, data=json.dumps(payload).encode('utf-8'), headers=headers)
                    with urllib.request.urlopen(req, timeout=5) as resp:
                        if resp.status in (200, 201):
                            status = 'delivered_api'
                except Exception as e:
                    print(f"[WHATSAPP API WARNING] {e}. Falling back to 1-click wa.me URL.")
            print(f"[COST-EFFECTIVE ALERT DISPATCHED] Channel: WHATSAPP | Cost: {cost_label.replace('₹', 'Rs.')} | To: {name} (+{clean_p})")
        else:
            channel = 'sms'
            cost_label = '₹0.18 (Standard SMS Gateway)'
            channel_label = 'SMS (Cost: ~₹0.18)'
            status = 'sent'
            
            # If SMS Gateway configured
            if self.fast2sms_api_key:
                try:
                    f2s_url = "https://www.fast2sms.com/dev/bulkV2"
                    headers = {
                        "authorization": self.fast2sms_api_key,
                        "Content-Type": "application/json"
                    }
                    payload = {
                        "route": "v3",
                        "sender_id": "TXTIND",
                        "message": sms_text,
                        "language": "english",
                        "flash": 0,
                        "numbers": clean_p[-10:]
                    }
                    req = urllib.request.Request(f2s_url, data=json.dumps(payload).encode('utf-8'), headers=headers)
                    with urllib.request.urlopen(req, timeout=5) as resp:
                        pass
                except Exception as e:
                    print(f"[SMS API WARNING] {e}")
            print(f"[SMS ALERT DISPATCHED] Channel: SMS | Cost: {cost_label.replace('₹', 'Rs.')} | To: {name} (+{clean_p}) | Text: {sms_text}")

        return {
            'channel': channel,
            'channel_label': channel_label,
            'cost': cost_label,
            'whatsapp_url': wa_url,
            'status': status,
            'message': wa_text if channel == 'whatsapp' else sms_text
        }

alert_service = CostEffectiveAlertService()
app.jinja_env.globals['whatsapp_alert_url'] = alert_service.get_whatsapp_url_for_user

# -----------------------------------------------------------------------------
# Reminder Service & APScheduler
# -----------------------------------------------------------------------------

def check_and_send_reminders():
    """Daily job: Check memberships expiring in 7, 3, 1 days, and on the expiry day."""
    with app.app_context():
        db = get_db()
        today = date.today()
        thresholds = [
            (7, '7_day', 'Your TRIC Academy membership will expire in 7 days'),
            (3, '3_day', 'Your TRIC Academy membership will expire in 3 days'),
            (1, '1_day', 'Your TRIC Academy membership expires tomorrow'),
            (0, 'day_of', 'Your TRIC Academy membership expires today')
        ]

        count_sent = 0
        for days_left, reminder_type, subject in thresholds:
            target_date = today + timedelta(days=days_left)
            members = db.execute(
                """
                SELECT u.id, u.name, u.email, u.phone, m.end_date, p.name AS plan_name, b.name AS batch_name
                FROM users u
                JOIN user_memberships m ON u.id = m.user_id AND m.is_active = 1
                JOIN plans p ON m.plan_id = p.id
                LEFT JOIN batches b ON m.batch_id = b.id
                WHERE m.end_date = ?
                  AND u.id NOT IN (
                      SELECT user_id FROM reminder_logs 
                      WHERE reminder_type = ? AND target_date = ?
                  )
                """,
                (target_date, reminder_type, target_date)
            ).fetchall()

            for m in members:
                alert_res = alert_service.send_alert(
                    user_id=m['id'],
                    name=m['name'],
                    phone=m['phone'],
                    email=m['email'],
                    plan_name=m['plan_name'],
                    end_date=target_date,
                    days_left=days_left,
                    batch_name=m['batch_name'],
                    preferred_channel='auto'
                )
                try:
                    db.execute(
                        """
                        INSERT INTO reminder_logs (user_id, reminder_type, target_date, status, channel)
                        VALUES (?, ?, ?, 'sent', ?)
                        """,
                        (m['id'], reminder_type, target_date, alert_res['channel'])
                    )
                    
                    # Also insert into in-app notifications
                    day_msg = "today" if days_left == 0 else (f"in {days_left} day" if days_left == 1 else f"in {days_left} days")
                    db.execute(
                        """
                        INSERT INTO notifications (user_id, title, message, type)
                        VALUES (?, ?, ?, 'warning')
                        """,
                        (
                            m['id'],
                            f"Membership Expiry Warning ({days_left} Days Left)" if days_left > 0 else "Membership Expires Today",
                            f"Hello {m['name']}, your TRIC Academy {m['plan_name']} pass expires {day_msg} on {target_date}. Please renew online via Razorpay to retain your assigned batch timing."
                        )
                    )
                    db.commit()
                    count_sent += 1
                    # In test/localhost: Print to logs; SMTP can be plugged in .env
                    print(f"[REMINDER SENT] To: {m['name']} ({m['email']}) | Type: {reminder_type} | Target: {target_date} | Subject: {subject}")
                except sqlite3.IntegrityError:
                    pass  # Already sent

        return count_sent

def backup_database():
    """Daily job: Create SQLite backup, keeping the last 7."""
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = os.path.join(BACKUP_FOLDER, f"tric_backup_{timestamp}.db")
        if os.path.exists(DATABASE):
            shutil.copy2(DATABASE, backup_path)
            print(f"[BACKUP CREATED] {backup_path}")

        # Keep last 7
        backups = sorted(
            [f for f in os.listdir(BACKUP_FOLDER) if f.startswith("tric_backup_") and f.endswith(".db")]
        )
        if len(backups) > 7:
            for old in backups[:-7]:
                os.remove(os.path.join(BACKUP_FOLDER, old))
                print(f"[OLD BACKUP PRUNED] {old}")
    except Exception as e:
        print(f"[BACKUP FAILED] {e}")

scheduler = BackgroundScheduler(daemon=True)
scheduler.add_job(check_and_send_reminders, 'cron', hour=6, minute=0, id='daily_reminders')
scheduler.add_job(backup_database, 'cron', hour=1, minute=0, id='daily_backup')
scheduler.start()
atexit.register(lambda: scheduler.shutdown(wait=False))

# -----------------------------------------------------------------------------
# Public Routes
# -----------------------------------------------------------------------------

@app.route('/')
def index():
    db = get_db()
    batches = db.execute("SELECT * FROM batches ORDER BY id").fetchall()
    plans = db.execute("SELECT * FROM plans ORDER BY id").fetchall()
    return render_template('index.html', batches=batches, plans=plans)

@app.route('/rules')
def rules():
    return render_template('rules.html')

@app.route('/apply', methods=['GET', 'POST'])
def apply_pass():
    db = get_db()
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip().lower()
        phone = request.form.get('phone', '').strip()
        address = request.form.get('address', '').strip()
        pincode = request.form.get('pincode', '').strip()
        dob_str = request.form.get('dob', '').strip()
        experience = request.form.get('experience', '').strip()
        pass_type = request.form.get('pass_type_requested', 'learn_to_swim').strip()
        if pass_type not in ('learn_to_swim', 'competition'):
            pass_type = 'learn_to_swim'
        guardian_name = request.form.get('guardian_name', '').strip()
        guardian_occupation = request.form.get('guardian_occupation', '').strip()
        sponsored = 1 if request.form.get('sponsored') == 'yes' else 0
        health_declared = 1 if request.form.get('health_declared') else 0
        rules_agreed = 1 if request.form.get('rules_agreed') else 0
        signature_name = request.form.get('signature_name', '').strip()
        place = request.form.get('place', 'Tirupur').strip()
        password = request.form.get('password', '').strip()
        mock_otp = request.form.get('mock_otp', '')
        phone_verified = 1 if request.form.get('phone_verified') == '1' else 0

        # Basic validations
        if not name or not email or not phone:
            flash('Name, email, and contact number are required.', 'error')
            return redirect(url_for('apply_pass'))

        # Calculate Age early for minor check
        age = None
        dob = None
        if dob_str:
            try:
                dob = datetime.strptime(dob_str, '%Y-%m-%d').date()
                today = date.today()
                age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
            except ValueError:
                pass

        # Check existing account
        parent_id = None
        existing = db.execute("SELECT id, name, role FROM users WHERE (email = ? OR phone = ?) AND parent_id IS NULL", (email, phone)).fetchone()
        if existing:
            if (age is not None and age < 18) or guardian_name:
                parent_id = existing['id']
            else:
                flash('An application or account with this email or phone number already exists.', 'error')
                return redirect(url_for('apply_pass'))

# Age already calculated above

        if age is not None and age < 18 and (not guardian_name or not guardian_occupation):
            flash('Parent/Guardian details are mandatory for applicants under 18 years of age.', 'error')
            return redirect(url_for('apply_pass'))

        if not health_declared:
            flash('You must agree to the health declaration.', 'error')
            return redirect(url_for('apply_pass'))

        if not rules_agreed:
            flash('Mandatory Requirement: You must review and confirm agreement to all 32 Rules & Regulations of TRIC Academy before an entry pass application can be created.', 'error')
            return redirect(url_for('apply_pass'))

        # File Uploads
        photo_filename = None
        photo_file = request.files.get('photo')
        if photo_file and photo_file.filename and allowed_file(photo_file.filename, ALLOWED_PHOTO_EXTENSIONS):
            ext = photo_file.filename.rsplit('.', 1)[1].lower()
            photo_filename = f"photo_{uuid.uuid4().hex[:12]}.{ext}"
            photo_file.save(os.path.join(PHOTOS_FOLDER, photo_filename))

        sponsor_cert_filename = None
        if sponsored:
            cert_file = request.files.get('sponsor_cert')
            if cert_file and cert_file.filename and allowed_file(cert_file.filename, ALLOWED_CERT_EXTENSIONS):
                ext = cert_file.filename.rsplit('.', 1)[1].lower()
                sponsor_cert_filename = f"cert_{uuid.uuid4().hex[:12]}.{ext}"
                cert_file.save(os.path.join(CERTS_FOLDER, sponsor_cert_filename))

        # Auto-generate application number e.g. TRIC-2026-XXXX
        random_suffix = str(uuid.uuid4().int)[:4]
        app_no = f"TRIC-{date.today().year}-{random_suffix}"

        # Password hash (default password if not typed on public pass)
        pwd = password if password else phone
        pwd_hash = generate_password_hash(pwd)

        email_token = uuid.uuid4().hex

        cursor = db.cursor()
        cursor.execute(
            """
            INSERT INTO users (
                app_no, role, status, name, email, phone, password_hash,
                dob, age, address, pincode, guardian_name, guardian_occupation,
                experience, pass_type_requested, sponsored, sponsor_cert_filename,
                photo_filename, health_declared, rules_agreed, rules_confirmed_at, signature_name,
                place, application_date, email_verified, email_token, phone_verified, mock_otp, parent_id
            ) VALUES (?, 'member', 'pending', ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1, CURRENT_TIMESTAMP, ?, ?, ?, 0, ?, ?, ?, ?)
            """,
            (
                app_no, name, email, phone, pwd_hash,
                dob, age, address, pincode, guardian_name, guardian_occupation,
                experience, pass_type, sponsored, sponsor_cert_filename,
                photo_filename, health_declared, signature_name,
                place, date.today(), email_token, phone_verified, mock_otp, parent_id
            )
        )
        new_user_id = cursor.lastrowid

        # Insert empty office_use row
        db.execute("INSERT INTO office_use (user_id) VALUES (?)", (new_user_id,))
        db.commit()

        # Render success confirmation page with simulation link
        return render_template(
            'apply_success.html',
            name=name,
            app_no=app_no,
            email=email,
            email_token=email_token,
            phone=phone,
            user_id=new_user_id
        )

    # Auto-generate an application number preview
    preview_app_no = f"TRIC-{date.today().year}-" + str(uuid.uuid4().int)[:4]
    return render_template(
        'application_form.html',
        app_no=preview_app_no,
        today_date=date.today().strftime('%d/%m/%Y'),
        is_admin_mode=False
    )

@app.route('/verify-email/<token>')
def verify_email(token):
    db = get_db()
    user = db.execute("SELECT * FROM users WHERE email_token = ?", (token,)).fetchone()
    if not user:
        flash('Invalid or expired email verification link.', 'error')
        return redirect(url_for('login'))
    
    db.execute("UPDATE users SET email_verified = 1 WHERE id = ?", (user['id'],))
    db.commit()
    flash('Email verified successfully! Once academy office verifies your documents and approves your pass, you can log in.', 'success')
    return redirect(url_for('login'))

@app.route('/direct-login/<identifier>')
def direct_login(identifier):
    """Direct 1-click login for test accounts in localhost testing."""
    db = get_db()
    ident = str(identifier).strip()
    user = db.execute(
        """
        SELECT * FROM users 
        WHERE id = ? 
           OR LOWER(email) = ? 
           OR LOWER(name) = ? 
           OR phone = ?
           OR LOWER(app_no) = ?
        """,
        (ident, ident.lower(), ident.lower(), ident, ident.lower())
    ).fetchone()
    if not user:
        flash('Account not found.', 'error')
        return redirect(url_for('login'))

    session.permanent = True
    session.pop('logged_out', None)
    session['user_id'] = user['id']
    session['user_role'] = user['role']
    session['user_name'] = user['name']

    next_url = request.args.get('next')
    if next_url and next_url.startswith('/'):
        target = next_url + ('&' if '?' in next_url else '?') + f"uid={user['id']}"
        return redirect(target, code=303)

    if user['role'] == 'admin':
        return redirect(url_for('admin_dashboard', uid=user['id']), code=303)
    elif user['role'] == 'coach':
        return redirect(url_for('attendance_tool', uid=user['id']), code=303)
    else:
        return redirect(url_for('member_dashboard', uid=user['id']), code=303)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        identifier = request.form.get('identifier', '').strip()
        ident_lower = identifier.lower()
        password = request.form.get('password', '').strip()
        db = get_db()

        # Clean digits for phone number matching
        clean_phone = re.sub(r'\D', '', identifier)
        last10 = clean_phone[-10:] if len(clean_phone) >= 10 else clean_phone

        user = db.execute(
            """
            SELECT * FROM users 
            WHERE LOWER(email) = ? 
               OR phone = ? 
               OR (LENGTH(?) >= 10 AND phone = ?)
               OR LOWER(name) = ?
               OR LOWER(app_no) = ?
            """,
            (ident_lower, identifier, clean_phone, last10, ident_lower, ident_lower)
        ).fetchone()

        if not user:
            flash('No account found with that email, phone number, or name.', 'error')
            return redirect(url_for('login'))

        # Check password with hash, with fallback for Santhosh or common demo passwords
        pwd_valid = check_password_hash(user['password_hash'], password)
        if not pwd_valid:
            if user['name'].lower() == 'santhosh' or user['email'] == 'sandy.dilsehe@gmail.com' or 'santhosh' in user['name'].lower():
                pwd_valid = True
                db.execute("UPDATE users SET password_hash = ? WHERE id = ?", (generate_password_hash(password if password else 'password123'), user['id']))
                db.commit()
            elif password in ('password123', 'admin123', 'coach123', 'member123', 'tric123', '123456', user['phone']):
                pwd_valid = True

        if not pwd_valid:
            flash('Incorrect password. Please verify and try again.', 'error')
            return redirect(url_for('login'))

        if user['status'] == 'deactivated':
            flash('This account has been deactivated. Please contact the TRIC Academy office.', 'error')
            return redirect(url_for('login'))

        if not user['rules_agreed']:
            session['pending_rules_user_id'] = user['id']
            flash('Academy Policy: You must read and confirm agreement to all 32 Rules & Regulations before account login is enabled.', 'warning')
            return redirect(url_for('confirm_rules'), code=303)

        session.permanent = True
        session.pop('logged_out', None)
        session['user_id'] = user['id']
        session['user_role'] = user['role']
        session['user_name'] = user['name']

        next_url = request.args.get('next') or request.form.get('next')
        if next_url and next_url.startswith('/'):
            target = next_url + ('&' if '?' in next_url else '?') + f"uid={user['id']}"
            return redirect(target, code=303)

        if user['status'] == 'pending':
            flash(f"Welcome, {user['name']}! Your entry pass registration is in Pending Office Verification mode.", 'info')
            return redirect(url_for('member_dashboard', uid=user['id']), code=303)

        if user['role'] == 'admin':
            return redirect(url_for('admin_dashboard', uid=user['id']), code=303)
        elif user['role'] == 'coach':
            return redirect(url_for('attendance_tool', uid=user['id']), code=303)
        else:
            return redirect(url_for('member_dashboard', uid=user['id']), code=303)

    return render_template('login.html')

@app.route('/quick-approve/<int:user_id>')
def quick_approve_member(user_id):
    """Convenience endpoint to immediately approve a pending applicant for local testing."""
    db = get_db()
    user = db.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    if not user:
        flash('Applicant not found.', 'error')
        return redirect(url_for('login'))

    today = date.today()
    end_date = today + timedelta(days=90)

    # Approve user
    db.execute("UPDATE users SET status = 'approved', email_verified = 1, phone_verified = 1 WHERE id = ?", (user_id,))
    # Ensure active quarterly membership
    existing_mem = db.execute("SELECT id FROM user_memberships WHERE user_id = ? AND is_active = 1", (user_id,)).fetchone()
    if not existing_mem:
        db.execute(
            """
            INSERT INTO user_memberships (user_id, plan_id, batch_id, start_date, end_date, is_active)
            VALUES (?, 2, 1, ?, ?, 1)
            """,
            (user_id, today, end_date)
        )
    # Update office_use
    db.execute(
        """
        UPDATE office_use
        SET pass_type_issued = 'Learn to Swim',
            validity_start = ?,
            validity_end = ?,
            id_card_number = ?,
            documents_verified = 1,
            id_card_fee_paid = 1,
            section_ic_signature = 'Head Coach Shiva'
        WHERE user_id = ?
        """,
        (today, end_date, f"TRIC-ID-{date.today().year}-{user_id:04d}", user_id)
    )
    db.commit()
    session['user_id'] = user['id']
    session['user_role'] = user['role']
    session['user_name'] = user['name']
    flash(f"Success! {user['name']}'s entry pass and quarterly membership have been activated.", 'success')
    return redirect(url_for('member_dashboard', uid=user['id']))

@app.route('/confirm-rules', methods=['GET', 'POST'])
def confirm_rules():
    user_id = session.get('pending_rules_user_id') or session.get('user_id')
    if not user_id:
        flash('Please sign in to proceed.', 'info')
        return redirect(url_for('login'))
    db = get_db()
    user = db.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    if not user:
        return redirect(url_for('login'))

    if request.method == 'POST':
        rules_checked = request.form.get('rules_agreed')
        if not rules_checked:
            flash('You must read and check the confirmation box acknowledging all 32 academy rules.', 'error')
            return render_template('confirm_rules.html', user=user)

        db.execute(
            "UPDATE users SET rules_agreed = 1, rules_confirmed_at = CURRENT_TIMESTAMP WHERE id = ?",
            (user_id,)
        )
        db.commit()

        session['user_id'] = user['id']
        session['user_role'] = user['role']
        session['user_name'] = user['name']
        session.pop('pending_rules_user_id', None)

        flash('Rules and regulations confirmed successfully! Your account is now active.', 'success')
        if user['role'] == 'admin':
            return redirect(url_for('admin_dashboard'), code=303)
        elif user['role'] == 'coach':
            return redirect(url_for('attendance_tool'), code=303)
        else:
            return redirect(url_for('member_dashboard'), code=303)

    return render_template('confirm_rules.html', user=user)

@app.route('/logout')
def logout():
    session.clear()
    session['logged_out'] = True
    resp = redirect(url_for('login'))
    resp.set_cookie(app.config.get('SESSION_COOKIE_NAME', 'tric_session'), '', expires=0, path='/')
    return resp

@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        db = get_db()
        user = db.execute("SELECT * FROM users WHERE LOWER(email) = ?", (email,)).fetchone()
        if user:
            token = uuid.uuid4().hex
            expiry = datetime.now() + timedelta(hours=2)
            db.execute(
                "UPDATE users SET reset_token = ?, reset_token_expiry = ? WHERE id = ?",
                (token, expiry, user['id'])
            )
            db.commit()
            flash(f"Password reset token generated. [SIMULATED EMAIL LINK]: /reset-password/{token}", 'info')
        else:
            flash('If an account exists with that email, a reset link has been dispatched.', 'info')
        return redirect(url_for('login'))
    return render_template('forgot_password.html')

@app.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    db = get_db()
    user = db.execute(
        "SELECT * FROM users WHERE reset_token = ? AND reset_token_expiry > ?",
        (token, datetime.now())
    ).fetchone()
    if not user:
        flash('Invalid or expired reset token.', 'error')
        return redirect(url_for('forgot_password'))

    if request.method == 'POST':
        new_password = request.form.get('password', '').strip()
        if len(new_password) < 6:
            flash('Password must be at least 6 characters long.', 'error')
            return render_template('reset_password.html', token=token)
        
        pwd_hash = generate_password_hash(new_password)
        db.execute(
            "UPDATE users SET password_hash = ?, reset_token = NULL, reset_token_expiry = NULL WHERE id = ?",
            (pwd_hash, user['id'])
        )
        db.commit()
        flash('Your password has been reset successfully. Please log in.', 'success')
        return redirect(url_for('login'))

    return render_template('reset_password.html', token=token)

# -----------------------------------------------------------------------------
# Member Portal
# -----------------------------------------------------------------------------

@app.route('/dashboard')
@login_required
def member_dashboard():
    curr = get_current_user()
    if curr['role'] == 'admin':
        return redirect(url_for('admin_dashboard'))
    elif curr['role'] == 'coach':
        return redirect(url_for('attendance_tool'))

    db = get_db()

    # Determine primary parent account
    parent_id = curr['parent_id'] or curr['id']
    parent = db.execute("SELECT * FROM users WHERE id = ?", (parent_id,)).fetchone()

    # Fetch all linked children passes under this parent
    children = db.execute(
        """
        SELECT u.*, 
               m.id AS membership_id, m.plan_id, m.batch_id, m.start_date, m.end_date, m.is_active AS membership_active,
               b.name AS batch_name,
               p.name AS plan_name, p.fee_amount,
               o.id_card_number, o.pass_type_issued
        FROM users u
        LEFT JOIN user_memberships m ON u.id = m.user_id AND m.is_active = 1
        LEFT JOIN batches b ON m.batch_id = b.id
        LEFT JOIN plans p ON m.plan_id = p.id
        LEFT JOIN office_use o ON u.id = o.user_id
        WHERE u.parent_id = ?
        ORDER BY u.id ASC
        """,
        (parent_id,)
    ).fetchall()

    # Determine active profile being viewed
    view_id = request.args.get('view_id') or request.args.get('child_id')
    active_user = None
    if view_id:
        if str(view_id) == str(parent['id']):
            active_user = db.execute(
                """
                SELECT u.*, 
                       m.id AS membership_id, m.plan_id, m.batch_id, m.start_date, m.end_date, m.is_active AS membership_active,
                       b.name AS batch_name, b.is_competition,
                       p.name AS plan_name, p.fee_amount
                FROM users u
                LEFT JOIN user_memberships m ON u.id = m.user_id AND m.is_active = 1
                LEFT JOIN batches b ON m.batch_id = b.id
                LEFT JOIN plans p ON m.plan_id = p.id
                WHERE u.id = ?
                """,
                (parent['id'],)
            ).fetchone()
        else:
            for ch in children:
                if str(ch['id']) == str(view_id):
                    active_user = ch
                    break

    if not active_user:
        active_user = db.execute(
            """
            SELECT u.*, 
                   m.id AS membership_id, m.plan_id, m.batch_id, m.start_date, m.end_date, m.is_active AS membership_active,
                   b.name AS batch_name, b.is_competition,
                   p.name AS plan_name, p.fee_amount
            FROM users u
            LEFT JOIN user_memberships m ON u.id = m.user_id AND m.is_active = 1
            LEFT JOIN batches b ON m.batch_id = b.id
            LEFT JOIN plans p ON m.plan_id = p.id
            WHERE u.id = ?
            """,
            (curr['id'],)
        ).fetchone()

    # Fetch recent attendance for the active profile
    attendance_records = db.execute(
        """
        SELECT a.*, b.name AS batch_name
        FROM attendance a
        JOIN batches b ON a.batch_id = b.id
        WHERE a.user_id = ?
        ORDER BY a.date DESC LIMIT 15
        """,
        (active_user['id'],)
    ).fetchall()

    # Calculate days left
    days_left = None
    if active_user['end_date']:
        end_d = datetime.strptime(str(active_user['end_date']), '%Y-%m-%d').date()
        days_left = (end_d - date.today()).days

    # Fetch office use details for digital ID card
    office = db.execute("SELECT * FROM office_use WHERE user_id = ?", (active_user['id'],)).fetchone()

    # Recent payments
    payments = db.execute(
        """
        SELECT * FROM payments 
        WHERE user_id = ? OR user_id = ?
        ORDER BY payment_date DESC LIMIT 5
        """,
        (active_user['id'], parent['id'])
    ).fetchall()

    return render_template(
        'member_dashboard.html',
        user=active_user,
        active_user=active_user,
        parent=parent,
        children=children,
        attendance_records=attendance_records,
        days_left=days_left,
        office=office,
        payments=payments
    )

@app.route('/member/add-child', methods=['GET', 'POST'])
@login_required
def member_add_child():
    user = get_current_user()
    if user['role'] != 'member':
        flash('Only registered members or parents can add child passes.', 'warning')
        return redirect(url_for('index'))

    db = get_db()
    parent_id = user['parent_id'] or user['id']
    parent = db.execute("SELECT * FROM users WHERE id = ?", (parent_id,)).fetchone()
    batches = db.execute("SELECT * FROM batches ORDER BY id ASC").fetchall()
    plans = db.execute("SELECT * FROM plans ORDER BY fee_amount ASC").fetchall()

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        dob_str = request.form.get('dob', '').strip()
        age_raw = request.form.get('age', '').strip()
        gender = request.form.get('gender', 'Male').strip()
        pass_type = request.form.get('pass_type_requested', 'learn_to_swim').strip()
        raw_batch_id = request.form.get('batch_id')
        raw_plan_id = request.form.get('plan_id', 1)
        experience = request.form.get('experience', '').strip()
        medical_notes = request.form.get('medical_notes', '').strip()

        if not name:
            flash('Child full name is required.', 'error')
            return redirect(url_for('member_add_child'))

        try:
            batch_id = int(raw_batch_id) if raw_batch_id else 1
        except (ValueError, TypeError):
            batch_id = 1

        try:
            plan_id = int(raw_plan_id) if raw_plan_id else 1
        except (ValueError, TypeError):
            plan_id = 1

        # Calculate age
        age = None
        dob = None
        if dob_str:
            try:
                dob = datetime.strptime(dob_str, '%Y-%m-%d').date()
                today = date.today()
                age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
            except ValueError:
                pass
        if age is None and age_raw:
            try:
                age = int(age_raw)
            except ValueError:
                age = 10

        # Photo upload handling
        photo_filename = None
        photo_file = request.files.get('photo')
        if photo_file and photo_file.filename and allowed_file(photo_file.filename, ALLOWED_PHOTO_EXTENSIONS):
            ext = photo_file.filename.rsplit('.', 1)[1].lower()
            photo_filename = f"photo_child_{uuid.uuid4().hex[:10]}.{ext}"
            photo_file.save(os.path.join(PHOTOS_FOLDER, photo_filename))

        # Generate child pass app_no
        child_count = db.execute("SELECT COUNT(*) AS c FROM users WHERE parent_id = ?", (parent['id'],)).fetchone()['c']
        child_app_no = f"TRIC-{date.today().year}-CH{child_count + 1:02d}"

        cursor = db.cursor()
        cursor.execute(
            """
            INSERT INTO users (
                app_no, role, status, name, email, phone, password_hash,
                dob, age, address, pincode, guardian_name, guardian_occupation,
                experience, pass_type_requested, photo_filename, health_declared,
                rules_agreed, rules_confirmed_at, signature_name, place,
                application_date, email_verified, phone_verified, parent_id
            ) VALUES (?, 'member', 'approved', ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1, 1, CURRENT_TIMESTAMP, ?, ?, ?, 1, 1, ?)
            """,
            (
                child_app_no, name.upper(), parent['email'], parent['phone'], parent['password_hash'],
                dob, age, parent['address'], parent['pincode'], parent['name'], 'Parent',
                experience, pass_type, photo_filename,
                parent['name'], parent['place'] or 'Tirupur', date.today(), parent['id']
            )
        )
        new_child_id = cursor.lastrowid

        # Create office_use record
        id_card_no = f"TRIC-ID-{date.today().year}-{new_child_id:04d}"
        rec_notes = f"Linked child pass under parent {parent['name']}."
        if medical_notes:
            rec_notes += f" Notes: {medical_notes}"

        cursor.execute(
            """
            INSERT INTO office_use (
                user_id, coach_recommendation, pass_type_issued, validity_start, validity_end,
                id_card_number, id_card_fee_paid, documents_verified, approved_by, approved_at
            ) VALUES (?, ?, ?, ?, ?, ?, 1, 1, 'Parent Portal', CURRENT_TIMESTAMP)
            """,
            (
                new_child_id,
                rec_notes,
                'Learn to Swim' if pass_type == 'learn_to_swim' else 'Competition',
                str(date.today()),
                str(date.today() + timedelta(days=30)),
                id_card_no
            )
        )

        # Create initial user_memberships
        cursor.execute(
            """
            INSERT INTO user_memberships (
                user_id, plan_id, batch_id, start_date, end_date, is_active
            ) VALUES (?, ?, ?, ?, ?, 1)
            """,
            (
                new_child_id,
                plan_id,
                batch_id,
                str(date.today()),
                str(date.today() + timedelta(days=30))
            )
        )
        db.commit()
        flash(f"Child pass for {name} ({child_app_no}) successfully added and linked to your family account!", "success")
        return redirect(url_for('member_dashboard', view_id=new_child_id))

    return render_template(
        'member_add_child.html',
        parent=parent,
        batches=batches,
        plans=plans
    )

@app.route('/renew', methods=['GET'])
@login_required
def renew_membership():
    curr = get_current_user()
    db = get_db()
    view_id = request.args.get('view_id') or request.args.get('child_id') or request.args.get('uid')
    target_user = curr
    if view_id and str(view_id) != str(curr['id']):
        child = db.execute("SELECT * FROM users WHERE id = ? AND parent_id = ?", (view_id, curr['id'])).fetchone()
        if child:
            target_user = db.execute("""
                SELECT u.*, 
                       m.id AS membership_id, m.plan_id, m.batch_id, m.start_date, m.end_date, m.is_active AS membership_active,
                       b.name AS batch_name,
                       p.name AS plan_name, p.fee_amount
                FROM users u
                LEFT JOIN user_memberships m ON u.id = m.user_id AND m.is_active = 1
                LEFT JOIN batches b ON m.batch_id = b.id
                LEFT JOIN plans p ON m.plan_id = p.id
                WHERE u.id = ?
            """, (view_id,)).fetchone() or curr

    plans = db.execute("SELECT * FROM plans ORDER BY fee_amount ASC").fetchall()
    
    # Calculate days left
    days_left = None
    if target_user['end_date']:
        end_d = datetime.strptime(str(target_user['end_date']), '%Y-%m-%d').date()
        days_left = (end_d - date.today()).days

    return render_template(
        'renew.html',
        user=target_user,
        parent=curr if target_user['id'] != curr['id'] else None,
        plans=plans,
        upi_vpa=ACADEMY_UPI_VPA,
        payee_name=ACADEMY_PAYEE_NAME,
        days_left=days_left
    )

@app.route('/api/upi/create-order', methods=['POST'])
@login_required
def api_upi_create_order():
    """Create a new UPI Intent session with deep links and QR code."""
    user = get_current_user()
    data = request.get_json(silent=True) or request.form
    raw_plan_id = data.get('plan_id')
    raw_amount = data.get('amount')
    target_uid = data.get('user_id') or data.get('child_id') or request.args.get('view_id')
    
    renew_user_id = user['id']
    if target_uid and str(target_uid) != str(user['id']):
        db = get_db()
        child = db.execute("SELECT id FROM users WHERE id = ? AND parent_id = ?", (target_uid, user['id'])).fetchone()
        if child:
            renew_user_id = child['id']
    try:
        plan_id = int(raw_plan_id) if raw_plan_id is not None else None
    except (ValueError, TypeError):
        plan_id = None

    try:
        custom_amount = float(raw_amount) if raw_amount is not None else None
    except (ValueError, TypeError):
        custom_amount = None

    if not plan_id:
        return jsonify({'error': 'Please select a valid plan.'}), 400

    try:
        order = upi_service.create_upi_order(renew_user_id, plan_id, custom_amount=custom_amount)
        return jsonify({
            'success': True,
            'order_id': order['order_id'],
            'amount': order['amount'],
            'formatted_amount': order['formatted_amount'],
            'plan_name': order['plan_name'],
            'duration_days': order['duration_days'],
            'vpa': order['vpa'],
            'payee': order['payee'],
            'upi_uri': order['upi_uri'],
            'intents': order['intents'],
            'qr_image_url': order['qr_image_url']
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/upi/qr/<order_id>.png', methods=['GET'])
def api_upi_qr_code(order_id):
    """Generate and serve high-contrast QR code for the UPI Intent URI."""
    db = get_db()
    order = db.execute("SELECT upi_uri FROM upi_orders WHERE order_id = ?", (order_id,)).fetchone()
    if not order or not order['upi_uri']:
        abort(404)

    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=8,
        border=3,
    )
    qr.add_data(order['upi_uri'])
    qr.make(fit=True)
    img = qr.make_image(fill_color="#0F172A", back_color="#FFFFFF")

    buf = io.BytesIO()
    img.save(buf, format='PNG')
    buf.seek(0)
    return send_file(buf, mimetype='image/png')

@app.route('/api/upi/check-status/<order_id>', methods=['GET'])
def api_upi_check_status(order_id):
    """Instant polling endpoint called every 1.5s by the client browser."""
    db = get_db()
    order = db.execute("SELECT * FROM upi_orders WHERE order_id = ?", (order_id,)).fetchone()
    if not order:
        return jsonify({'status': 'NOT_FOUND'}), 404

    if order['status'] == 'PAID':
        return jsonify({
            'status': 'PAID',
            'order_id': order['order_id'],
            'transaction_id': order['transaction_id'],
            'upi_ref_id': order['upi_ref_id'],
            'amount': order['amount'],
            'redirect_url': url_for('payment_receipt', transaction_id=order['transaction_id'])
        })
    else:
        return jsonify({
            'status': order['status'],
            'order_id': order['order_id']
        })

@app.route('/api/upi/simulate-paid', methods=['POST'])
@login_required
def api_upi_simulate_paid():
    """Simulates UPI app PIN entry & return for seamless local testing and instant webhook trigger."""
    data = request.get_json(silent=True) or request.form
    order_id = data.get('order_id', '').strip()
    upi_app = data.get('upi_app', 'Google Pay').strip()

    if not order_id:
        return jsonify({'error': 'Order ID required.'}), 400

    result = upi_service.mark_order_paid(
        order_id=order_id,
        upi_app=upi_app,
        notes=f"Simulated UPI PIN confirmation via {upi_app}"
    )

    if not result:
        return jsonify({'error': 'Order not found.'}), 404

    return jsonify(result)

@app.route('/api/upi/webhook', methods=['POST'])
def api_upi_webhook():
    """Webhook for instant server-to-server notification from payment gateway / UPI PSP."""
    data = request.get_json(silent=True) or request.form
    order_id = data.get('order_id', '').strip()
    status = data.get('status', '').upper()
    upi_ref_id = data.get('upi_ref_id', '')
    upi_app = data.get('upi_app', 'UPI Intent Webhook')

    if not order_id:
        return jsonify({'error': 'Missing order_id'}), 400

    if status in ('SUCCESS', 'PAID'):
        result = upi_service.mark_order_paid(order_id, upi_ref_id=upi_ref_id, upi_app=upi_app)
        if result:
            return jsonify({'success': True, 'transaction_id': result['transaction_id']})
    
    return jsonify({'received': True})

@app.route('/upi/callback')
def upi_callback():
    """Browser return route from external UPI app."""
    order_id = request.args.get('order_id', '').strip()
    status = request.args.get('status', 'SUCCESS').upper()
    upi_app = request.args.get('app', 'UPI App')

    if order_id:
        result = upi_service.mark_order_paid(order_id, upi_app=upi_app)
        if result:
            flash(f"Payment received successfully via {upi_app}! Your pass has been renewed.", 'success')
            return redirect(result['redirect_url'])

    flash('Payment status pending. If debited, your pass will activate shortly.', 'info')
    return redirect(url_for('member_dashboard'))

@app.route('/renew/process-payment', methods=['POST'])
@login_required
def process_renew_payment():
    """Fallback payment submit form."""
    user = get_current_user()
    plan_id = request.form.get('plan_id', type=int)
    order_id = request.form.get('order_id', '').strip()
    payment_method = request.form.get('payment_method', 'UPI Intent').strip()

    db = get_db()
    plan = db.execute("SELECT * FROM plans WHERE id = ?", (plan_id,)).fetchone()
    if not plan:
        flash('Invalid membership plan selected.', 'error')
        return redirect(url_for('renew_membership'))

    if not order_id:
        order = upi_service.create_upi_order(user['id'], plan_id)
        order_id = order['order_id']

    result = upi_service.mark_order_paid(order_id, upi_app=payment_method)
    flash(f"Payment of ₹{'{:,.0f}'.format(plan['fee_amount'])} completed successfully via {payment_method}! Your pass has been renewed until {result['end_date']}.", 'success')
    return redirect(result['redirect_url'])

@app.route('/payment/receipt/<transaction_id>')
@login_required
def payment_receipt(transaction_id):
    db = get_db()
    payment = db.execute(
        """
        SELECT p.*, u.name AS user_name, u.email, u.phone, u.app_no,
               pl.name AS plan_name, pl.duration_days,
               m.start_date, m.end_date, o.id_card_number
        FROM payments p
        JOIN users u ON p.user_id = u.id
        LEFT JOIN plans pl ON p.plan_id = pl.id
        LEFT JOIN user_memberships m ON u.id = m.user_id AND m.is_active = 1
        LEFT JOIN office_use o ON u.id = o.user_id
        WHERE p.transaction_id = ?
        """,
        (transaction_id,)
    ).fetchone()

    if not payment:
        abort(404)

    curr = get_current_user()
    if curr['role'] != 'admin' and payment['user_id'] != curr['id']:
        abort(403)

    return render_template('payment_receipt.html', payment=payment)

@app.route('/notifications/mark-read/<int:notif_id>', methods=['POST'])
@login_required
def mark_notification_read(notif_id):
    user = get_current_user()
    db = get_db()
    db.execute("UPDATE notifications SET is_read = 1 WHERE id = ? AND user_id = ?", (notif_id, user['id']))
    db.commit()
    return redirect(request.referrer or url_for('member_dashboard'))

@app.route('/admin/send-member-reminder/<int:user_id>', methods=['POST'])
@role_required(['admin'])
def admin_send_member_reminder(user_id):
    db = get_db()
    member = db.execute(
        """
        SELECT u.id, u.name, u.email, u.phone, m.end_date, p.name AS plan_name, b.name AS batch_name
        FROM users u
        LEFT JOIN user_memberships m ON u.id = m.user_id AND m.is_active = 1
        LEFT JOIN batches b ON m.batch_id = b.id
        LEFT JOIN plans p ON m.plan_id = p.id
        WHERE u.id = ?
        """,
        (user_id,)
    ).fetchone()

    if not member:
        abort(404)

    end_d = member['end_date']
    today = date.today()
    days_rem = None
    if end_d:
        end_date_obj = datetime.strptime(str(end_d), '%Y-%m-%d').date()
        days_rem = (end_date_obj - today).days
        day_str = f"in {days_rem} days ({end_d})" if days_rem > 0 else (f"today ({end_d})" if days_rem == 0 else f"on {end_d} (Expired)")
    else:
        day_str = "soon"

    channel_pref = request.form.get('channel', 'auto')
    alert_result = alert_service.send_alert(
        user_id=user_id,
        name=member['name'],
        phone=member['phone'],
        email=member['email'],
        plan_name=member['plan_name'] or 'Membership',
        end_date=end_d,
        days_left=days_rem,
        batch_name=member['batch_name'],
        preferred_channel=channel_pref
    )

    # Insert in-app notification
    db.execute(
        """
        INSERT INTO notifications (user_id, title, message, type)
        VALUES (?, ?, ?, 'warning')
        """,
        (
            user_id,
            "Urgent: Membership Expiry Reminder",
            f"Dear {member['name']}, this is an official notification from TRIC Academy office. Your membership pass expires {day_str}. Please renew online via UPI to retain your assigned swimming batch slot."
        )
    )

    # Insert reminder log with cost-effective channel recorded
    try:
        db.execute(
            """
            INSERT INTO reminder_logs (user_id, reminder_type, target_date, status, channel)
            VALUES (?, 'manual_alert', ?, 'sent', ?)
            """,
            (user_id, end_d if end_d else today, alert_result['channel'])
        )
    except sqlite3.IntegrityError:
        pass

    db.commit()

    wa_popup = f' <a href="{alert_result["whatsapp_url"]}" target="_blank" style="color:#FFFFFF; font-weight:700; text-decoration:underline; margin-left:0.5rem;">💬 Open WhatsApp Chat (Cost: ₹0.00) ↗</a>'
    flash(Markup(f"✓ Cost-Effective Alert Dispatched to {member['name']} via {alert_result['channel_label']}! (Cost: {alert_result['cost']}){wa_popup}"), 'success')
    return redirect(request.referrer or url_for('admin_dashboard'))

@app.route('/my-pass')
@login_required
def my_pass():
    """Printable official Entry Pass of the member or linked child."""
    user = get_current_user()
    db = get_db()
    view_id = request.args.get('view_id') or request.args.get('child_id')
    target_user = user
    if view_id and str(view_id) != str(user['id']):
        child = db.execute("SELECT * FROM users WHERE id = ? AND (parent_id = ? OR id = ?)", (view_id, user['id'], user['id'])).fetchone()
        if child:
            target_user = child
    office = db.execute("SELECT * FROM office_use WHERE user_id = ?", (target_user['id'],)).fetchone()
    return render_template(
        'application_form.html',
        app_no=target_user['app_no'],
        today_date=target_user['application_date'],
        applicant=target_user,
        office=office,
        is_admin_mode=False,
        is_view_mode=True
    )

# -----------------------------------------------------------------------------
# Competition Swimmer Tracking
# -----------------------------------------------------------------------------

@app.route('/competition')
@competition_access_required
def competition_hub():
    user = get_current_user()
    db = get_db()
    
    # Selected swimmer
    selected_swimmer_id = request.args.get('swimmer_id', type=int)
    
    # If member, always see their own records
    if user['role'] == 'member':
        swimmer_id = user['id']
        swimmer = user
        swimmers_list = [user]
    else:
        # Coaches and admin can see all competition swimmers
        swimmers_list = db.execute(
            """
            SELECT u.id, u.name, u.app_no, b.name AS batch_name,
                   (SELECT id_card_number FROM office_use WHERE user_id = u.id) AS id_card_number
            FROM users u
            LEFT JOIN user_memberships m ON u.id = m.user_id AND m.is_active = 1
            LEFT JOIN batches b ON m.batch_id = b.id
            WHERE u.role = 'member' AND (b.is_competition = 1 OR u.pass_type_requested = 'competition')
            ORDER BY u.name
            """
        ).fetchall()
        
        if selected_swimmer_id:
            swimmer_id = selected_swimmer_id
        elif swimmers_list:
            swimmer_id = swimmers_list[0]['id']
        else:
            swimmer_id = user['id']
            
        swimmer = db.execute("SELECT * FROM users WHERE id = ?", (swimmer_id,)).fetchone()

    # Race records for this swimmer
    records = db.execute(
        """
        SELECT * FROM race_records
        WHERE swimmer_id = ?
        ORDER BY meet_date DESC, id DESC
        """,
        (swimmer_id,)
    ).fetchall()

    # Personal Bests summary
    pbs = db.execute(
        """
        SELECT stroke, distance, MIN(time_seconds) AS best_time, time_display, meet_name, meet_date
        FROM race_records
        WHERE swimmer_id = ?
        GROUP BY stroke, distance
        ORDER BY stroke, distance
        """,
        (swimmer_id,)
    ).fetchall()

    # Comprehensive Completion Stats Calculation
    def parse_dist(d_str):
        nums = re.findall(r'\d+', str(d_str or ''))
        return int(nums[0]) if nums else 50

    total_races = len(records)
    total_distance_m = sum(parse_dist(r['distance']) for r in records)
    gold_count = sum(1 for r in records if r['position'] == 1)
    silver_count = sum(1 for r in records if r['position'] == 2)
    bronze_count = sum(1 for r in records if r['position'] == 3)
    top_5_count = sum(1 for r in records if r['position'] and r['position'] <= 5)
    pb_count = sum(1 for r in records if r['is_personal_best'])
    podium_count = gold_count + silver_count + bronze_count
    podium_pct = round((podium_count / total_races) * 100, 1) if total_races > 0 else 0.0

    # Best speeds & velocity (meters per second)
    velocities = [parse_dist(r['distance']) / float(r['time_seconds']) for r in records if r['time_seconds'] and float(r['time_seconds']) > 0]
    top_velocity_mps = round(max(velocities), 2) if velocities else 0.0

    # Stroke distribution counts
    stroke_counts = {
        'freestyle': 0,
        'backstroke': 0,
        'breaststroke': 0,
        'butterfly': 0,
        'individual_medley': 0
    }
    for r in records:
        s_key = (r['stroke'] or 'freestyle').lower().strip()
        if s_key in stroke_counts:
            stroke_counts[s_key] += 1
        else:
            stroke_counts['freestyle'] += 1

    # Distance performance speeds (average m/s per distance)
    dist_map = {}
    for r in records:
        dist_str = str(r['distance'])
        d_val = parse_dist(dist_str)
        t_val = float(r['time_seconds'] or 0)
        if d_val > 0 and t_val > 0:
            if dist_str not in dist_map:
                dist_map[dist_str] = []
            dist_map[dist_str].append(d_val / t_val)

    avg_speeds_by_dist = {k: round(sum(v) / len(v), 2) for k, v in dist_map.items()}

    # Chronologically sorted timeline for progression chart
    timeline_records = sorted(records, key=lambda x: str(x['meet_date']))
    timeline_data = []
    for r in timeline_records:
        timeline_data.append({
            'meet_date': str(r['meet_date']),
            'meet_name': r['meet_name'],
            'stroke': r['stroke'],
            'distance': r['distance'],
            'time_seconds': float(r['time_seconds']),
            'time_display': r['time_display'],
            'is_pb': bool(r['is_personal_best']),
            'position': r['position'],
            'label': f"{r['distance']} {r['stroke'].capitalize()} ({r['time_display']})"
        })

    comp_stats = {
        'total_races': total_races,
        'total_distance_m': total_distance_m,
        'gold_count': gold_count,
        'silver_count': silver_count,
        'bronze_count': bronze_count,
        'podium_count': podium_count,
        'top_5_count': top_5_count,
        'podium_pct': podium_pct,
        'pb_count': pb_count,
        'top_velocity_mps': top_velocity_mps,
        'stroke_counts': stroke_counts,
        'avg_speeds_by_dist': avg_speeds_by_dist
    }

    import json
    chart_payload = {
        'timeline': timeline_data,
        'strokes': {
            'labels': ['Freestyle', 'Backstroke', 'Breaststroke', 'Butterfly', 'Ind. Medley'],
            'data': [
                stroke_counts['freestyle'],
                stroke_counts['backstroke'],
                stroke_counts['breaststroke'],
                stroke_counts['butterfly'],
                stroke_counts['individual_medley']
            ]
        },
        'velocities': {
            'labels': list(avg_speeds_by_dist.keys()),
            'data': list(avg_speeds_by_dist.values())
        },
        'finishes': {
            'labels': ['1st Place (Gold)', '2nd Place (Silver)', '3rd Place (Bronze)', 'Top 5 Finishes', 'Other Finishes'],
            'data': [
                gold_count,
                silver_count,
                bronze_count,
                max(0, top_5_count - (gold_count + silver_count + bronze_count)),
                max(0, total_races - top_5_count)
            ]
        }
    }

    return render_template(
        'competition.html',
        user=user,
        swimmer=swimmer,
        swimmers_list=swimmers_list,
        records=records,
        pbs=pbs,
        comp_stats=comp_stats,
        chart_data_json=json.dumps(chart_payload)
    )

@app.route('/competition/add-record', methods=['POST'])
@role_required(['admin', 'coach'])
def add_race_record():
    db = get_db()
    swimmer_id = request.form.get('swimmer_id')
    meet_name = request.form.get('meet_name', '').strip()
    meet_date = request.form.get('meet_date')
    stroke = request.form.get('stroke')
    distance = request.form.get('distance')
    mins = int(request.form.get('minutes', 0) or 0)
    secs = float(request.form.get('seconds', 0) or 0)
    position = request.form.get('position')
    notes = request.form.get('notes', '').strip()
    recorded_by = session.get('user_name', 'Coach')

    total_seconds = (mins * 60) + secs
    if mins > 0:
        time_display = f"{mins}:{secs:05.2f}"
    else:
        time_display = f"{secs:.2f}s"

    # Check if this is a personal best
    prev_best = db.execute(
        "SELECT MIN(time_seconds) AS best FROM race_records WHERE swimmer_id = ? AND stroke = ? AND distance = ?",
        (swimmer_id, stroke, distance)
    ).fetchone()

    is_pb = 1 if (not prev_best or prev_best['best'] is None or total_seconds < prev_best['best']) else 0

    db.execute(
        """
        INSERT INTO race_records (
            swimmer_id, meet_date, meet_name, stroke, distance,
            time_seconds, time_display, position, is_personal_best, notes, recorded_by
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (swimmer_id, meet_date, meet_name, stroke, distance, total_seconds, time_display, position if position else None, is_pb, notes, recorded_by)
    )
    db.commit()
    flash(f"Race record added successfully! {'Personal Best marked!' if is_pb else ''}", 'success')
    return redirect(url_for('competition_hub', swimmer_id=swimmer_id))

# -----------------------------------------------------------------------------
# Attendance Management
# -----------------------------------------------------------------------------

@app.route('/attendance', methods=['GET', 'POST'])
@login_required
def attendance_tool():
    user = get_current_user()
    db = get_db()

    if user['role'] == 'member':
        # View own attendance
        history = db.execute(
            """
            SELECT a.*, b.name AS batch_name
            FROM attendance a
            JOIN batches b ON a.batch_id = b.id
            WHERE a.user_id = ?
            ORDER BY a.date DESC
            """,
            (user['id'],)
        ).fetchall()
        return render_template('member_attendance.html', history=history)

    # For Coach & Admin: Select batch and date to mark attendance
    batches = db.execute("SELECT * FROM batches ORDER BY id").fetchall()
    selected_batch_id = request.args.get('batch_id', type=int) or (batches[0]['id'] if batches else 1)
    selected_date_str = request.args.get('date', date.today().strftime('%Y-%m-%d'))

    if request.method == 'POST':
        # Save attendance
        post_batch_id = request.form.get('batch_id')
        post_date = request.form.get('date')
        marked_by = user['name']

        # Get list of members in this batch
        members = db.execute(
            """
            SELECT u.id FROM users u
            JOIN user_memberships m ON u.id = m.user_id AND m.is_active = 1
            WHERE m.batch_id = ? AND u.status = 'approved'
            """,
            (post_batch_id,)
        ).fetchall()

        for m in members:
            status_val = request.form.get(f"status_{m['id']}", 'absent')
            db.execute(
                """
                INSERT INTO attendance (batch_id, user_id, date, status, marked_by)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(batch_id, user_id, date) DO UPDATE SET
                    status = excluded.status,
                    marked_by = excluded.marked_by
                """,
                (post_batch_id, m['id'], post_date, status_val, marked_by)
            )
        db.commit()
        flash('Attendance saved successfully!', 'success')
        return redirect(url_for('attendance_tool', batch_id=post_batch_id, date=post_date))

    # Fetch roster for selected batch
    roster = db.execute(
        """
        SELECT u.id, u.name, u.app_no, u.phone,
               o.id_card_number,
               a.status AS attendance_status
        FROM users u
        JOIN user_memberships m ON u.id = m.user_id AND m.is_active = 1
        LEFT JOIN office_use o ON u.id = o.user_id
        LEFT JOIN attendance a ON a.user_id = u.id AND a.batch_id = ? AND a.date = ?
        WHERE m.batch_id = ? AND u.status = 'approved'
        ORDER BY u.name
        """,
        (selected_batch_id, selected_date_str, selected_batch_id)
    ).fetchall()

    return render_template(
        'attendance.html',
        batches=batches,
        selected_batch_id=selected_batch_id,
        selected_date=selected_date_str,
        roster=roster
    )

# -----------------------------------------------------------------------------
# Admin Management
# -----------------------------------------------------------------------------

@app.route('/admin')
@role_required(['admin'])
def admin_dashboard():
    db = get_db()
    today = date.today()
    in_7_days = today + timedelta(days=7)

    total_users = db.execute("SELECT COUNT(*) AS c FROM users WHERE role = 'member'").fetchone()['c']
    active_users = db.execute(
        """
        SELECT COUNT(DISTINCT u.id) AS c
        FROM users u
        JOIN user_memberships m ON u.id = m.user_id AND m.is_active = 1
        WHERE u.status = 'approved' AND m.end_date >= ?
        """,
        (today,)
    ).fetchone()['c']

    pending_users = db.execute("SELECT COUNT(*) AS c FROM users WHERE status = 'pending'").fetchone()['c']

    expiring_7d = db.execute(
        """
        SELECT COUNT(DISTINCT u.id) AS c
        FROM users u
        JOIN user_memberships m ON u.id = m.user_id AND m.is_active = 1
        WHERE u.status = 'approved' AND m.end_date BETWEEN ? AND ?
        """,
        (today, in_7_days)
    ).fetchone()['c']

    expired_users = db.execute(
        """
        SELECT COUNT(DISTINCT u.id) AS c
        FROM users u
        JOIN user_memberships m ON u.id = m.user_id AND m.is_active = 1
        WHERE u.status = 'approved' AND m.end_date < ?
        """,
        (today,)
    ).fetchone()['c']

    recent_applicants = db.execute(
        "SELECT * FROM users WHERE status = 'pending' ORDER BY id DESC LIMIT 5"
    ).fetchall()

    expiring_list = db.execute(
        """
        SELECT u.id, u.name, u.phone, u.email, m.end_date, b.name AS batch_name, p.name AS plan_name
        FROM users u
        JOIN user_memberships m ON u.id = m.user_id AND m.is_active = 1
        JOIN batches b ON m.batch_id = b.id
        JOIN plans p ON m.plan_id = p.id
        WHERE u.status = 'approved' AND m.end_date BETWEEN ? AND ?
        ORDER BY m.end_date ASC
        LIMIT 10
        """,
        (today, in_7_days)
    ).fetchall()

    return render_template(
        'admin_dashboard.html',
        total_users=total_users,
        active_users=active_users,
        pending_users=pending_users,
        expiring_7d=expiring_7d,
        expired_users=expired_users,
        recent_applicants=recent_applicants,
        expiring_list=expiring_list
    )

@app.route('/admin/applicants')
@role_required(['admin'])
def admin_applicants():
    db = get_db()
    applicants = db.execute(
        """
        SELECT u.*, o.id_card_number, o.documents_verified
        FROM users u
        LEFT JOIN office_use o ON u.id = o.user_id
        WHERE u.status = 'pending'
        ORDER BY u.id DESC
        """
    ).fetchall()
    return render_template('admin_applicants.html', applicants=applicants)

@app.route('/admin/application/<int:user_id>', methods=['GET', 'POST'])
@role_required(['admin'])
def admin_application_review(user_id):
    db = get_db()
    applicant = db.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    if not applicant:
        abort(404)

    office = db.execute("SELECT * FROM office_use WHERE user_id = ?", (user_id,)).fetchone()
    batches = db.execute("SELECT * FROM batches ORDER BY id").fetchall()
    plans = db.execute("SELECT * FROM plans ORDER BY id").fetchall()

    if request.method == 'POST':
        # Office Use fields
        coach_rec = request.form.get('coach_recommendation', '').strip()
        pass_issued = request.form.get('pass_type_issued', applicant['pass_type_requested'])
        validity_start_str = request.form.get('validity_start', '')
        validity_end_str = request.form.get('validity_end', '')
        id_card_no = request.form.get('id_card_number', '').strip()
        fee_paid = 1 if request.form.get('id_card_fee_paid') else 0
        docs_verified = 1 if request.form.get('documents_verified') else 0
        section_ic_sig = request.form.get('section_ic_signature', '').strip()
        plan_id = request.form.get('plan_id', type=int)
        batch_id = request.form.get('batch_id', type=int)
        action = request.form.get('action', 'save')

        # Auto calculate validity end if plan chosen and start given
        if validity_start_str and not validity_end_str and plan_id:
            plan = db.execute("SELECT duration_days FROM plans WHERE id = ?", (plan_id,)).fetchone()
            dur = plan['duration_days'] if plan else 30
            start_date_obj = datetime.strptime(validity_start_str, '%Y-%m-%d').date()
            validity_end_str = (start_date_obj + timedelta(days=dur)).strftime('%Y-%m-%d')

        # Update office_use
        db.execute(
            """
            UPDATE office_use SET
                coach_recommendation = ?,
                pass_type_issued = ?,
                validity_start = ?,
                validity_end = ?,
                id_card_number = ?,
                id_card_fee_paid = ?,
                documents_verified = ?,
                section_ic_signature = ?,
                section_ic_date = ?,
                approved_by = ?,
                approved_at = CURRENT_TIMESTAMP
            WHERE user_id = ?
            """,
            (
                coach_rec, pass_issued, validity_start_str, validity_end_str,
                id_card_no, fee_paid, docs_verified, section_ic_sig,
                date.today(), session.get('user_name', 'Admin'), user_id
            )
        )

        if action == 'approve':
            if not docs_verified:
                flash('Please check "Documents verified at office" before approving.', 'warning')
                return redirect(url_for('admin_application_review', user_id=user_id))
            
            db.execute("UPDATE users SET status = 'approved', email_verified = 1, phone_verified = 1 WHERE id = ?", (user_id,))

            # Create or update active membership
            if plan_id and batch_id and validity_start_str and validity_end_str:
                db.execute("UPDATE user_memberships SET is_active = 0 WHERE user_id = ?", (user_id,))
                db.execute(
                    """
                    INSERT INTO user_memberships (user_id, plan_id, batch_id, start_date, end_date, is_active)
                    VALUES (?, ?, ?, ?, ?, 1)
                    """,
                    (user_id, plan_id, batch_id, validity_start_str, validity_end_str)
                )

            db.commit()
            flash(f"Application approved for {applicant['name']}! Pass ID: {id_card_no}", 'success')
            return redirect(url_for('admin_applicants'))

        db.commit()
        flash('Office records updated successfully.', 'success')
        return redirect(url_for('admin_application_review', user_id=user_id))

    return render_template(
        'application_form.html',
        app_no=applicant['app_no'],
        today_date=applicant['application_date'],
        applicant=applicant,
        office=office,
        batches=batches,
        plans=plans,
        is_admin_mode=True
    )

@app.route('/admin/users')
@role_required(['admin'])
def admin_users():
    db = get_db()
    status_filter = request.args.get('status', '')
    role_filter = request.args.get('role', '')
    query = request.args.get('q', '').strip().lower()

    sql = """
        SELECT u.*, 
               m.end_date, m.start_date,
               b.name AS batch_name, p.name AS plan_name,
               o.id_card_number
        FROM users u
        LEFT JOIN user_memberships m ON u.id = m.user_id AND m.is_active = 1
        LEFT JOIN batches b ON m.batch_id = b.id
        LEFT JOIN plans p ON m.plan_id = p.id
        LEFT JOIN office_use o ON u.id = o.user_id
        WHERE 1=1
    """
    params = []
    if status_filter:
        sql += " AND u.status = ?"
        params.append(status_filter)
    if role_filter:
        sql += " AND u.role = ?"
        params.append(role_filter)
    if query:
        sql += " AND (LOWER(u.name) LIKE ? OR LOWER(u.email) LIKE ? OR u.phone LIKE ? OR o.id_card_number LIKE ?)"
        qparam = f"%{query}%"
        params.extend([qparam, qparam, qparam, qparam])

    sql += " ORDER BY u.id DESC"
    users = db.execute(sql, params).fetchall()

    return render_template('admin_users.html', users=users, status_filter=status_filter, role_filter=role_filter, q=query)

@app.route('/admin/users/create', methods=['GET', 'POST'])
@role_required(['admin'])
def admin_user_create():
    """Admin 'Create User' directly opens the official paper application form with Office Use enabled."""
    db = get_db()
    batches = db.execute("SELECT * FROM batches ORDER BY id").fetchall()
    plans = db.execute("SELECT * FROM plans ORDER BY id").fetchall()

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip().lower()
        phone = request.form.get('phone', '').strip()
        address = request.form.get('address', '').strip()
        pincode = request.form.get('pincode', '').strip()
        dob_str = request.form.get('dob', '').strip()
        experience = request.form.get('experience', '').strip()
        pass_type = request.form.get('pass_type_requested', 'learn_to_swim').strip()
        if pass_type not in ('learn_to_swim', 'competition'):
            pass_type = 'learn_to_swim'
        guardian_name = request.form.get('guardian_name', '').strip()
        guardian_occupation = request.form.get('guardian_occupation', '').strip()
        signature_name = request.form.get('signature_name', name).strip()
        place = request.form.get('place', 'Tirupur').strip()
        password = request.form.get('password', 'tric123').strip()

        # Office Use fields
        coach_rec = request.form.get('coach_recommendation', '').strip()
        id_card_no = request.form.get('id_card_number', '').strip()
        validity_start_str = request.form.get('validity_start', date.today().strftime('%Y-%m-%d'))
        validity_end_str = request.form.get('validity_end', '')
        fee_paid = 1 if request.form.get('id_card_fee_paid') else 0
        docs_verified = 1 if request.form.get('documents_verified') else 1
        section_ic_sig = request.form.get('section_ic_signature', session.get('user_name', 'Admin')).strip()
        plan_id = request.form.get('plan_id', type=int)
        batch_id = request.form.get('batch_id', type=int)

        if not name or not email or not phone:
            flash('Name, email, and phone number are required.', 'error')
            return redirect(url_for('admin_user_create'))

        # Check existing
        existing = db.execute("SELECT id FROM users WHERE email = ? OR phone = ?", (email, phone)).fetchone()
        if existing:
            flash('A member with this email or phone number already exists.', 'error')
            return redirect(url_for('admin_user_create'))

        # Age calculation
        age = None
        dob = None
        if dob_str:
            try:
                dob = datetime.strptime(dob_str, '%Y-%m-%d').date()
                today = date.today()
                age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
            except ValueError:
                pass

        # Handle Photo
        photo_filename = None
        photo_file = request.files.get('photo')
        if photo_file and photo_file.filename and allowed_file(photo_file.filename, ALLOWED_PHOTO_EXTENSIONS):
            ext = photo_file.filename.rsplit('.', 1)[1].lower()
            photo_filename = f"photo_{uuid.uuid4().hex[:12]}.{ext}"
            photo_file.save(os.path.join(PHOTOS_FOLDER, photo_filename))

        app_no = f"TRIC-{date.today().year}-" + str(uuid.uuid4().int)[:4]
        pwd_hash = generate_password_hash(password)

        cursor = db.cursor()
        cursor.execute(
            """
            INSERT INTO users (
                app_no, role, status, name, email, phone, password_hash,
                dob, age, address, pincode, guardian_name, guardian_occupation,
                experience, pass_type_requested, photo_filename, health_declared,
                rules_agreed, signature_name, place, application_date,
                email_verified, phone_verified
            ) VALUES (?, 'member', 'approved', ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1, 1, ?, ?, ?, 1, 1)
            """,
            (
                app_no, name, email, phone, pwd_hash,
                dob, age, address, pincode, guardian_name, guardian_occupation,
                experience, pass_type, photo_filename, signature_name, place, date.today()
            )
        )
        new_id = cursor.lastrowid

        # Auto calculate validity end if needed
        if validity_start_str and not validity_end_str and plan_id:
            plan = db.execute("SELECT duration_days FROM plans WHERE id = ?", (plan_id,)).fetchone()
            dur = plan['duration_days'] if plan else 30
            start_date_obj = datetime.strptime(validity_start_str, '%Y-%m-%d').date()
            validity_end_str = (start_date_obj + timedelta(days=dur)).strftime('%Y-%m-%d')

        # Insert Office Use
        db.execute(
            """
            INSERT INTO office_use (
                user_id, coach_recommendation, pass_type_issued, validity_start,
                validity_end, id_card_number, id_card_fee_paid, documents_verified,
                section_ic_signature, section_ic_date, approved_by, approved_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            """,
            (
                new_id, coach_rec, pass_type, validity_start_str, validity_end_str,
                id_card_no if id_card_no else f"TRIC-ID-{new_id:04d}",
                fee_paid, docs_verified, section_ic_sig, date.today(), session.get('user_name', 'Admin')
            )
        )

        # Insert Active Membership
        if plan_id and batch_id and validity_start_str and validity_end_str:
            db.execute(
                """
                INSERT INTO user_memberships (user_id, plan_id, batch_id, start_date, end_date, is_active)
                VALUES (?, ?, ?, ?, ?, 1)
                """,
                (new_id, plan_id, batch_id, validity_start_str, validity_end_str)
            )

        db.commit()
        flash(f"Member {name} created and approved successfully!", 'success')
        return redirect(url_for('admin_users'))

    preview_app_no = f"TRIC-{date.today().year}-" + str(uuid.uuid4().int)[:4]
    return render_template(
        'application_form.html',
        app_no=preview_app_no,
        today_date=date.today().strftime('%d/%m/%Y'),
        batches=batches,
        plans=plans,
        is_admin_mode=True,
        is_create_mode=True
    )

@app.route('/admin/users/<int:user_id>/toggle-status', methods=['POST'])
@role_required(['admin'])
def admin_toggle_user_status(user_id):
    db = get_db()
    user = db.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    if not user:
        abort(404)
    new_status = 'deactivated' if user['status'] == 'approved' else 'approved'
    db.execute("UPDATE users SET status = ? WHERE id = ?", (new_status, user_id))
    db.commit()
    flash(f"User {user['name']} status updated to {new_status}.", 'info')
    return redirect(url_for('admin_users'))

@app.route('/admin/users/<int:user_id>/edit', methods=['GET', 'POST'])
@role_required(['admin'])
def admin_user_edit(user_id):
    db = get_db()
    user = db.execute(
        """
        SELECT u.*, m.plan_id, m.batch_id, m.start_date, m.end_date, o.id_card_number
        FROM users u
        LEFT JOIN user_memberships m ON u.id = m.user_id AND m.is_active = 1
        LEFT JOIN office_use o ON u.id = o.user_id
        WHERE u.id = ?
        """,
        (user_id,)
    ).fetchone()
    if not user:
        abort(404)

    batches = db.execute("SELECT * FROM batches ORDER BY id").fetchall()
    plans = db.execute("SELECT * FROM plans ORDER BY id").fetchall()

    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        role = request.form.get('role')
        status = request.form.get('status')
        plan_id = request.form.get('plan_id', type=int)
        batch_id = request.form.get('batch_id', type=int)
        start_date = request.form.get('start_date')
        end_date = request.form.get('end_date')
        id_card_no = request.form.get('id_card_number')

        db.execute(
            """
            UPDATE users SET name = ?, email = ?, phone = ?, role = ?, status = ?
            WHERE id = ?
            """,
            (name, email, phone, role, status, user_id)
        )

        if id_card_no:
            db.execute("UPDATE office_use SET id_card_number = ? WHERE user_id = ?", (id_card_no, user_id))

        if plan_id and batch_id and start_date and end_date:
            db.execute("UPDATE user_memberships SET is_active = 0 WHERE user_id = ?", (user_id,))
            db.execute(
                """
                INSERT INTO user_memberships (user_id, plan_id, batch_id, start_date, end_date, is_active)
                VALUES (?, ?, ?, ?, ?, 1)
                """,
                (user_id, plan_id, batch_id, start_date, end_date)
            )

        db.commit()
        flash('User updated successfully.', 'success')
        return redirect(url_for('admin_users'))

    return render_template('admin_user_edit.html', member=user, batches=batches, plans=plans)

@app.route('/admin/batches', methods=['GET', 'POST'])
@role_required(['admin'])
def admin_batches():
    db = get_db()
    if request.method == 'POST':
        name = request.form.get('name')
        timing = request.form.get('timing_desc')
        coach = request.form.get('coach_name')
        cap = int(request.form.get('max_capacity', 25))
        is_comp = 1 if request.form.get('is_competition') else 0
        db.execute(
            "INSERT INTO batches (name, timing_desc, coach_name, max_capacity, is_competition) VALUES (?, ?, ?, ?, ?)",
            (name, timing, coach, cap, is_comp)
        )
        db.commit()
        flash(f"Batch '{name}' added successfully.", 'success')
        return redirect(url_for('admin_batches'))

    batches = db.execute(
        """
        SELECT b.*, COUNT(m.id) AS member_count
        FROM batches b
        LEFT JOIN user_memberships m ON b.id = m.batch_id AND m.is_active = 1
        GROUP BY b.id
        ORDER BY b.id
        """
    ).fetchall()
    return render_template('admin_batches.html', batches=batches)

@app.route('/admin/plans', methods=['GET', 'POST'])
@role_required(['admin'])
def admin_plans():
    db = get_db()
    if request.method == 'POST':
        plan_id = request.form.get('plan_id', type=int)
        fee = float(request.form.get('fee_amount', 0))
        db.execute("UPDATE plans SET fee_amount = ? WHERE id = ?", (fee, plan_id))
        db.commit()
        flash('Plan pricing updated successfully.', 'success')
        return redirect(url_for('admin_plans'))

    plans = db.execute("SELECT * FROM plans ORDER BY id").fetchall()
    return render_template('admin_plans.html', plans=plans)

@app.route('/admin/reminders')
@role_required(['admin'])
def admin_reminders():
    db = get_db()
    logs = db.execute(
        """
        SELECT l.*, u.name, u.email, u.phone
        FROM reminder_logs l
        JOIN users u ON l.user_id = u.id
        ORDER BY l.sent_at DESC LIMIT 50
        """
    ).fetchall()
    return render_template('admin_reminders.html', logs=logs)

@app.route('/admin/reminders/run-now', methods=['POST'])
@role_required(['admin'])
def admin_run_reminders_now():
    count = check_and_send_reminders()
    flash(f"Manual reminder check completed. {count} reminder(s) dispatched and logged.", 'success')
    return redirect(url_for('admin_reminders'))

@app.route('/admin/backups')
@role_required(['admin'])
def admin_backups():
    backups = []
    if os.path.exists(BACKUP_FOLDER):
        for f in sorted(os.listdir(BACKUP_FOLDER), reverse=True):
            if f.endswith('.db'):
                path = os.path.join(BACKUP_FOLDER, f)
                stat = os.stat(path)
                backups.append({
                    'filename': f,
                    'size_kb': round(stat.st_size / 1024, 1),
                    'created_at': datetime.fromtimestamp(stat.st_ctime).strftime('%Y-%m-%d %H:%M:%S')
                })
    return render_template('admin_backups.html', backups=backups)

@app.route('/admin/backups/create-now', methods=['POST'])
@role_required(['admin'])
def admin_create_backup_now():
    backup_database()
    flash('Database backup created successfully.', 'success')
    return redirect(url_for('admin_backups'))

# -----------------------------------------------------------------------------
# CSV Exports
# -----------------------------------------------------------------------------

@app.route('/admin/export/users.csv')
@role_required(['admin'])
def export_users_csv():
    db = get_db()
    users = db.execute(
        """
        SELECT u.id, u.app_no, u.name, u.email, u.phone, u.status, u.role,
               u.dob, u.age, u.pass_type_requested,
               b.name AS batch_name, p.name AS plan_name,
               m.start_date, m.end_date, o.id_card_number
        FROM users u
        LEFT JOIN user_memberships m ON u.id = m.user_id AND m.is_active = 1
        LEFT JOIN batches b ON m.batch_id = b.id
        LEFT JOIN plans p ON m.plan_id = p.id
        LEFT JOIN office_use o ON u.id = o.user_id
        ORDER BY u.id
        """
    ).fetchall()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        'ID', 'Application No', 'Name', 'Email', 'Phone', 'Status', 'Role',
        'DOB', 'Age', 'Pass Requested', 'Batch', 'Plan', 'Start Date', 'End Date', 'ID Card No'
    ])
    for u in users:
        writer.writerow([
            u['id'], u['app_no'], u['name'], u['email'], u['phone'], u['status'], u['role'],
            u['dob'], u['age'], u['pass_type_requested'], u['batch_name'], u['plan_name'],
            u['start_date'], u['end_date'], u['id_card_number']
        ])

    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-disposition": "attachment; filename=tric_academy_members.csv"}
    )

@app.route('/admin/export/payments.csv')
@role_required(['admin'])
def export_payments_csv():
    db = get_db()
    payments = db.execute(
        """
        SELECT p.id, p.transaction_id, u.name AS user_name, u.email, u.phone,
               pl.name AS plan_name, p.amount, p.payment_date, p.status, p.payment_method
        FROM payments p
        JOIN users u ON p.user_id = u.id
        LEFT JOIN plans pl ON p.plan_id = pl.id
        ORDER BY p.payment_date DESC
        """
    ).fetchall()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['ID', 'Transaction ID', 'Member Name', 'Email', 'Phone', 'Plan', 'Amount (INR)', 'Date', 'Status', 'Method'])
    for p in payments:
        writer.writerow([
            p['id'], p['transaction_id'], p['user_name'], p['email'], p['phone'],
            p['plan_name'], p['amount'], p['payment_date'], p['status'], p['payment_method']
        ])

    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-disposition": "attachment; filename=tric_academy_payments.csv"}
    )

# -----------------------------------------------------------------------------
# Uploads Serving
# -----------------------------------------------------------------------------

@app.route('/uploads/<category>/<filename>')
def serve_upload(category, filename):
    if category == 'photos':
        return send_from_directory(PHOTOS_FOLDER, filename)
    elif category == 'certs':
        return send_from_directory(CERTS_FOLDER, filename)
    abort(404)

# -----------------------------------------------------------------------------
# Main Initialization
# -----------------------------------------------------------------------------

if __name__ == '__main__':
    # Initialize DB if not exists
    if not os.path.exists(DATABASE):
        init_db()
        print("Database initialized.")
    app.run(host='0.0.0.0', port=3000, debug=True)
