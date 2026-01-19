"""
Volunteer Hub - Flask Application

Added:
- Lightweight i18n (AR/EN) via TRANSLATIONS and _()
- /lang/<code> route to switch language (session-based)
- Flash messages use translation keys where appropriate
"""

from flask import session
from werkzeug.exceptions import NotFound
import os
import csv
import io
import sqlite3
from datetime import datetime
from functools import wraps
from io import StringIO
from flask import Response
from flask import render_template


from flask import (
    Flask, render_template, request, redirect,
    url_for, session, flash, g, send_file, Response, send_from_directory
)
from werkzeug.security import generate_password_hash, check_password_hash

# Optional: PDF certificate
try:
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import cm
    REPORTLAB_AVAILABLE = True
except Exception:
    REPORTLAB_AVAILABLE = False


# Flask app & configuration

app = Flask(__name__, instance_relative_config=True)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-secret-key-CHANGE-ME")
os.makedirs(app.instance_path, exist_ok=True)
DB_PATH = os.path.join(app.instance_path, "app.db")


@app.errorhandler(404)
def not_found(e):
    return render_template("404.html"), 404


@app.template_filter('datetimeformat')
def datetimeformat(value, fmt=None):
    if not value:
        return ""
    try:
        from datetime import datetime
        dt = datetime.fromisoformat(str(value).replace("T", " "))
        if fmt:
            return dt.strftime(fmt)

        lang = session.get('lang', 'en')
        if str(lang).startswith('ar'):

            txt = dt.strftime("%d-%m-%Y %I:%M %p")
            return txt.replace("AM", "صباحًا").replace("PM", "مساءً")
        else:

            return dt.strftime("%d-%m-%Y %I:%M %p")
    except Exception:
        return value


# Database

def get_db():
    """Get a SQLite connection stored on the app context (g)."""
    if "db" not in g:
        conn = sqlite3.connect(DB_PATH, detect_types=sqlite3.PARSE_DECLTYPES)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON;")
        g.db = conn
    return g.db


@app.teardown_appcontext
def close_db(exc):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    """Initialize DB schema from schema.sql."""
    with app.open_resource("schema.sql") as f:
        get_db().executescript(f.read().decode("utf-8"))
    get_db().commit()


@app.cli.command("init-db")
def init_db_command():
    """CLI: flask --app app.py init-db"""
    init_db()
    print("Initialized the database.")


# i18n: super-light translations
TRANSLATIONS = {
    "ar": {
        "brand": " مركز المتطوعين 🤝",
        "nav_admin": "لوحة الإدارة",
        "nav_volunteer": "لوحة المتطوع",
        "login": "تسجيل الدخول",
        "logout": "تسجيل الخروج",
        "register": "إنشاء حساب",
        "upcoming_events": "فعاليات التطوع القادمة",
        "view_all_events": "استعراض جميع الفعاليات",
        "home_hero": "شارك معنا في تنظيم فعاليات النادي، احصد ساعاتك التطوعية، واحصل على شهادات وتكريم.",
        "not_found": "الصفحة المطلوبة غير موجودة.",
        "join_to_impact": "انضم لتصنع الأثر ✨",
        "welcome": "مرحباً!",
        "already_registered": "أنتِ مسجّلة مسبقاً.",
        "registered_ok": "تم التسجيل في الفعالية.",
        "cancelled_ok": "تم إلغاء التسجيل.",
        "event_not_found": "الفعالية غير موجودة.",
        "need_login": "سجلي دخولك أولاً.",
        "admin_needed": "صلاحيات الإدارة مطلوبة.",
        "event_created": "تم إنشاء الفعالية.",
        "reg_updated": "تم تحديث السجل.",
        "event_details": "تفاصيل الفعالية",
        "no_events": "لا توجد فعاليات حالياً.",
        "vol_total_hours": "إجمالي الساعات",
        "no_records": "لا يوجد سجلات بعد.",
        "delete": "حذف",
        "delete_confirm": "هل أنت متأكد من حذف هذه الفعالية؟",
        "edit": "تعديل",
        "save_changes": "حفظ التعديلات",
        "cancel": "إلغاء",
        "event_updated": "تم تحديث الفعالية بنجاح.",
        "email": "البريد الإلكتروني",
        "password": "كلمة المرور",
        "name": "الاسم الكامل",
        "role": "الدور",
        "create_account": "إنشاء حساب",
        "role_hint": "اختر نوع الحساب: متطوع أو مسؤول",
        "role_volunteer": "متطوع",
        "role_admin": "مسؤول",
        "have_account_q": "لديك حساب؟ تسجيل الدخول",
        "no_account_q": "ليس لديك حساب؟",
        "register_btn": "تسجيل في الفعالية",
        "cancel_btn": "إلغاء التسجيل",
        "submit_hours_title": "إرسال ساعاتك",
        "base_hours_label": "الساعات الأساسية (تحسب تلقائيًا من البداية/النهاية)",
        "base_hours_hint": "المعادلة: البداية − النهاية",
        "extra_hours_label": "ساعات إضافية (مثل الطباعة أو التوزيعات)",
        "extra_desc_label": "وصف الإضافات",
        "extra_desc_ph": "ماذا فعلت بالإضافة إلى الحضور؟",
        "submit_hours": "إرسال الساعات",
        "registered_count": "عدد المسجلين",
        "submit_hours_title": "إرسال ساعاتك",
        "stats_hours": "مجموع الساعات",
        "stats_events": "عدد الفعاليات",
        "stats_volunteers": "عدد المتطوعين",
        "latest_registrations": "آخر التسجيلات",
        "status": "الحالة",
        "event": "الفعالية",
        "volunteer": "المتطوع",
        "actions": "الإجراءات",
        "hours": "الساعات",
        "update": "تحديث",
        "registered": "مسجَّل",
        "cancelled": "مُلغى",
        "create_event": "إنشاء فعالية",
        "title": "العنوان",
        "start_dt": "وقت البداية",
        "end_dt": "وقت النهاية",
        "location": "الموقع",
        "capacity": "السعة",
        "description": "الوصف",
        "create": "إنشاء",
        "st_registered": "مسجل",
        "st_attended": "حضر",
        "st_cancelled": "ملغي",
        "no_registrations": "لا توجد تسجيلات",
        "pending_hours": "ساعات بانتظار الاعتماد",
        "no_pending": "لا توجد ساعات بانتظار الاعتماد",
        "export_excel": "تصدير إلى إكسل (CSV)",
        "start_time_🕒": "وقت البداية🕒",
        "end_time_🕒": "وقت النهاية🕒",
        "pending_hour_submissions": "ساعات بانتظار المراجعة",
        "No_pending_submissions_.": ".لا توجد ساعات بانتظار المراجعة",
        "submitted": "تاريخ الإرسال",
        "description": "الوصف",
        "extra": "الإضافية",
        "base": "الأساسية",
        "event": "الفعالية",
        "volunteer": "المتطوع",
        "actions": "الإجراءات",
        "approve": "اعتماد",
        "reject": "رفض",
        "export_csv_⬇️": "تصدير إلى ملف إكسل ⬇️",
        "date": "التاريخ",
        "login_to_register": "سجّل الدخول للتسجيل في الفعالية",
        "cancel_btn": "إلغاء التسجيل",
        "register_btn": "تسجيل",
        "hours_submitted_ok": "تم إرسال الساعات بنجاح",
        "hours_rejected_ok": "تم رفض الساعات",
        "hours_approved_ok": "تم اعتماد الساعات",
        "waiting_for_admin_approval": "بانتظار موافقة المسؤول",
        "submitted_waiting": "تم الإرسال في {date} — بانتظار موافقة المشرف.",
        "approved_ok": "تم اعتماد {hours} ساعة بتاريخ {date}.",
        "h_unit": "ساعة",
        "not_found_title": "الصفحة غير موجودة",
        "not_found_msg": "يبدو أنك وصلت إلى رابط غير متوفر.",
        "back_to_dashboard": "العودة للوحة الإدارة",
        "date_time": "التاريخ والوقت",
        "dt_fmt": "%d-%m-%Y %H:%M",
        "from": "من",
        "to": "إلى",
        "event_created_duration": "تم إنشاء الفعالية ({title}) ومدتها {hours:.2f} ساعة ✅"














    },
    "en": {
        "brand": "Volunteer Hub 🤝",
        "nav_admin": "Admin Dashboard",
        "nav_volunteer": "Volunteer Dashboard",
        "login": "Log in",
        "logout": "Log out",
        "register": "Create Account",
        "upcoming_events": "Upcoming Events",
        "view_all_events": "View all events",
        "home_hero": "Join our club events, collect volunteer hours, and earn certificates.",
        "join_to_impact": "Join to make an impact ✨",
        "welcome": "Welcome back!",
        "already_registered": "You are already registered for this event.",
        "registered_ok": "You have been registered for the event.",
        "cancelled_ok": "Your registration has been cancelled.",
        "event_not_found": "Event not found.",
        "need_login": "Please log in first.",
        "admin_needed": "Admin privileges are required.",
        "event_created": "Event created successfully.",
        "reg_updated": "Registration updated.",
        "event_details": "Event Details",
        "no_events": "No events yet.",
        "vol_total_hours": "Total Hours",
        "no_records": "No records yet.",
        "delete": "Delete",
        "delete_confirm": "Are you sure you want to delete this event?",
        "edit": "Edit",
        "save_changes": "Save changes",
        "cancel": "Cancel",
        "event_updated": "Event updated successfully.",
        "hours_submitted_ok": "Your hours were submitted. Waiting for admin approval.",
        "hours_approved_ok": "Hours approved.",
        "hours_rejected_ok": "Submission rejected.",
        "not_registered_for_event": "You must be registered to submit hours for this event.",
        "event_not_found": "Event not found.",
        "not_found": "Not found.",
        "email": "Email",
        "password": "Password",
        "name": "Full Name",
        "role": "Role",
        "create_account": "Create Account",
        "role_hint": "Select account type: Volunteer or Admin",
        "role_volunteer": "Volunteer",
        "role_admin": "Admin",
        "have_account_q": "Have an account? Log in",
        "no_account_q": "Don't have an account?",
        "register_btn": "Register",
        "cancel_btn": "Cancel Registration",
        "submit_hours_title": "Submit your hours",
        "base_hours_label": "Base hours (auto from start/end)",
        "base_hours_hint": "Calculated: start − end",
        "extra_hours_label": "Extra hours (e.g., printing, giveaways)",
        "extra_desc_label": "Extra description",
        "extra_desc_ph": "What did you do in addition to attending?",
        "registered_count": "Registered count",
        "submit_hours": "Submit hours",
        "stats_hours": "Total Hours",
        "stats_events": "Total Events",
        "stats_volunteers": "Total Volunteers",
        "latest_registrations": "Latest Registrations",
        "status": "Status",
        "event": "Event",
        "volunteer": "Volunteer",
        "actions": "Actions",
        "hours": "Hours",
        "update": "Update",
        "registered": "Registered",
        "cancelled": "Cancelled",
        "create_event": "Create Event",
        "title": "Title",
        "start_dt": "Start Time",
        "end_dt": "End Time",
        "location": "Location",
        "capacity": "Capacity",
        "description": "Description",
        "create": "Create",
        "st_registered": "Registered",
        "st_attended": "Attended",
        "st_cancelled": "Cancelled",
        "start_time_🕒": "Start Time🕒",
        "end_time_🕒": "End Time🕒",
        "pending_hour_submissions": "Pending hour submissions",
        "No_pending_submissions_.": "No pending submissions.",
        "submitted": "Submitted",
        "description": "Description",
        "extra": "Extra",
        "base": "Base",
        "event": "Event",
        "volunteer": "Volunteer",
        "actions": "Actions",
        "approve": "Approve",
        "reject": "Reject",
        "export_csv_⬇️": "Export to Excel file ⬇️",
        "login_to_register": "Log in to register for the event",
        "cancel_btn": "Cancel Registration",
        "register_btn": "Register",
        "hours_submitted_ok": "Hours submitted successfully",
        "hours_rejected_ok": "Hours rejected",
        "hours_approved_ok": "Hours approved",
        "waiting_for_admin_approval": "Waiting for admin approval",
        "submitted_waiting": "Submitted on {date} — waiting for admin approval.",
        "approved_ok": "Approved {hours} hours on {date}.",
        "h_unit": "hours",
        "not_found_title": "Page not found",
        "not_found_msg": "It looks like you reached a page that doesn’t exist.",
        "back_to_dashboard": "Back to Admin Dashboard",
        "date_time": "Date & Time",
        "dt_fmt": "%Y-%m-%d %H:%M",
        "from": "From",
        "to": "To",
        "event_created_duration": "Event ({title}) created successfully with a duration of {hours:.2f} hours ✅"












    },
}


def parse_dt(val: object):

    if not val:
        return None
    s = str(val).strip().replace("T", " ")
    try:
        return datetime.strptime(s, "%Y-%m-%d %H:%M")
    except ValueError:

        return None


def calc_event_hours(ev) -> float | None:

    keys = ev.keys() if hasattr(ev, "keys") else []
    start_raw = ev["start_dt"] if "start_dt" in keys else (ev["date"] if "date" in keys else None)
    end_raw = ev["end_dt"] if "end_dt" in keys else None

    start = parse_dt(start_raw)
    end = parse_dt(end_raw)

    if not start or not end:
        return None

    delta = end - start
    return round(delta.total_seconds() / 3600.0, 2)


def get_lang():
    """Read current language from session; default 'ar'."""
    return session.get("lang", "ar")


def _(key):
    """Translate a key using current lang; fallback to key itself."""
    return TRANSLATIONS.get(get_lang(), {}).get(key, key)


@app.context_processor
def inject_i18n():
    """Make _() and current_lang available in all templates."""
    return {"_": _, "current_lang": get_lang()}


@app.route("/lang/<lang_code>")
def set_language(lang_code):
    """Switch UI language between 'ar' and 'en' and redirect back."""
    lang_code = (lang_code or "ar").lower()
    if lang_code not in ("ar", "en"):
        lang_code = "ar"
    session["lang"] = lang_code
    flash(_("welcome"))
    return redirect(request.referrer or url_for("home"))


# Auth & roles

def current_user():
    uid = session.get("user_id")
    if not uid:
        return None
    return get_db().execute("SELECT * FROM users WHERE id = ?", (uid,)).fetchone()


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if "user_id" not in session:
            flash(_("need_login"))
            return redirect(url_for("login", next=request.path))
        return view(*args, **kwargs)
    return wrapped


def admin_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if session.get("role") != "admin":
            flash(_("admin_needed"))
            return redirect(url_for("home"))
        return view(*args, **kwargs)
    return wrapped


# Filters

@app.template_filter("fmt_dt")
def format_datetime(value, fmt="%Y-%m-%d %H:%M"):
    if not value:
        return ""
    for p in ("%Y-%m-%d %H:%M", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d"):
        try:
            dt = datetime.strptime(str(value), p)
            return dt.strftime(fmt)
        except ValueError:
            continue
    return str(value)


# Auth routes

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        role = request.form.get("role", "volunteer")

        if not name or not email or not password:
            flash("Please fill in all required fields.")
            return redirect(url_for("register"))

        db = get_db()
        try:
            db.execute(
                "INSERT INTO users (name, email, role, password_hash) VALUES (?, ?, ?, ?)",
                (name, email, role, generate_password_hash(password)),
            )
            db.commit()
        except sqlite3.IntegrityError:
            flash("This email is already registered.")
            return redirect(url_for("register"))

        flash(_("welcome"))
        return redirect(url_for("login"))
    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        db = get_db()
        user = db.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
        if user and check_password_hash(user["password_hash"], password):
            session["user_id"] = user["id"]
            session["role"] = user["role"]
            flash(_("welcome"))
            next_url = request.args.get("next")
            if next_url and next_url.startswith("/"):
                return redirect(next_url)
            return redirect(url_for("home"))

        flash("Invalid email or password.")
        return redirect(url_for("login"))
    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    flash(_("welcome"))
    return redirect(url_for("home"))


# Public pages

@app.route("/")
def home():
    db = get_db()
    events = db.execute("SELECT * FROM events ORDER BY date ASC").fetchall()
    return render_template("home.html", events=events)


@app.route("/events")
def events():
    db = get_db()
    events = db.execute("SELECT * FROM events ORDER BY date ASC").fetchall()
    return render_template("events.html", events=events)


@app.route("/events/<int:event_id>")
def event_detail(event_id: int):
    db = get_db()
    ev = db.execute("SELECT * FROM events WHERE id = ?", (event_id,)).fetchone()
    if not ev:
        flash(_("event_not_found"))
        return redirect(url_for("events"))

    reg = None
    if session.get("user_id"):
        reg = db.execute(
            "SELECT * FROM registrations WHERE user_id = ? AND event_id = ?",
            (session["user_id"], event_id),
        ).fetchone()

    counts = db.execute(
        "SELECT COUNT(*) AS c FROM registrations WHERE event_id = ? AND status != 'cancelled'",
        (event_id,),
    ).fetchone()
    total_registered = counts["c"] if counts else 0

    return render_template("event_detail.html", ev=ev, reg=reg, total_registered=total_registered)


# Registration


@app.route("/events/<int:event_id>/register", methods=["POST"])
@login_required
def register_event(event_id: int):
    db = get_db()
    ev = db.execute("SELECT * FROM events WHERE id = ?", (event_id,)).fetchone()
    if not ev:
        flash(_("event_not_found"))
        return redirect(url_for("events"))

    base_hours = calc_event_hours(ev)

    reg = None

    if ev["capacity"] is not None:
        cnt = db.execute(
            "SELECT COUNT(*) AS c FROM registrations WHERE event_id = ? AND status != 'cancelled'",
            (event_id,),
        ).fetchone()["c"]
        if cnt >= ev["capacity"]:
            flash("This event has reached its capacity.")
            return redirect(url_for("event_detail", event_id=event_id))

    try:
        db.execute(
            "INSERT INTO registrations (user_id, event_id) VALUES (?, ?)",
            (session["user_id"], event_id),
        )
        db.commit()
        flash(_("registered_ok"))
    except sqlite3.IntegrityError:
        flash(_("already_registered"))

    return redirect(url_for("event_detail", event_id=event_id, base_hours=base_hours, reg=reg))


@app.route("/events/<int:event_id>/submit_hours", methods=["POST"])
@login_required
def submit_hours(event_id: int):
    db = get_db()

    # Ensure event exists
    ev = db.execute("SELECT * FROM events WHERE id=?", (event_id,)).fetchone()
    if not ev:
        flash(_("event_not_found"))
        return redirect(url_for("events"))

    # Ensure user is registered for this event
    reg = db.execute(
        "SELECT * FROM registrations WHERE user_id=? AND event_id=?",
        (session["user_id"], event_id),
    ).fetchone()
    if not reg:
        flash(_("not_registered_for_event"))
        return redirect(url_for("event_detail", event_id=event_id))

    # Read form
    extra_hours = request.form.get("extra_hours", "").strip()
    extra_desc = request.form.get("extra_desc", "").strip() or None

    # Base hours from event start/end
    self_hours = calc_event_hours(ev) or 0.0

    # Parse extra hours
    try:
        extra_val = float(extra_hours) if extra_hours else 0.0
        if extra_val < 0:
            extra_val = 0.0
    except ValueError:
        extra_val = 0.0

    # Save into the registration row
    now = datetime.utcnow().strftime("%Y-%m-%d %H:%M")
    db.execute(
        """
        UPDATE registrations
           SET self_hours=?,
               extra_hours=?,
               extra_desc=?,
               submitted_at=?,
               approved_hours=NULL,
               status=CASE WHEN status='cancelled' THEN status ELSE 'registered' END
         WHERE id=?
        """,
        (self_hours, extra_val, extra_desc, now, reg["id"])
    )
    db.commit()

    flash(_("hours_submitted_ok"))
    return redirect(url_for("event_detail", event_id=event_id))


@app.route("/events/<int:event_id>/cancel", methods=["POST"])
@login_required
def cancel_registration(event_id: int):
    db = get_db()
    db.execute(
        "UPDATE registrations SET status = 'cancelled' WHERE user_id = ? AND event_id = ?",
        (session["user_id"], event_id),
    )
    db.commit()
    flash(_("cancelled_ok"))
    return redirect(url_for("event_detail", event_id=event_id))


# Dashboards

@app.route("/dashboard")
@login_required
def dashboard_volunteer():
    db = get_db()
    regs = db.execute(
        """
        SELECT r.*, e.title, e.date, e.location
        FROM registrations r
        JOIN events e ON e.id = r.event_id
        WHERE r.user_id = ?
        ORDER BY e.date DESC
        """,
        (session["user_id"],),
    ).fetchall()

    total_hours = db.execute(
        "SELECT COALESCE(SUM(hours), 0) AS h FROM registrations WHERE user_id = ?",
        (session["user_id"],),
    ).fetchone()["h"]

    return render_template("dashboard_volunteer.html", regs=regs, total_hours=total_hours)


@app.route("/admin")
@admin_required
def dashboard_admin():
    db = get_db()
    stats = {
        "volunteers": db.execute("SELECT COUNT(*) AS c FROM users WHERE role = 'volunteer'").fetchone()["c"],
        "events": db.execute("SELECT COUNT(*) AS c FROM events").fetchone()["c"],
        "hours": db.execute("SELECT COALESCE(SUM(hours), 0) AS h FROM registrations").fetchone()["h"],
    }

    latest_regs = db.execute(
        """
        SELECT r.*, u.name AS user_name, e.title AS event_title
          FROM registrations r
          JOIN users u ON u.id = r.user_id
          JOIN events e ON e.id = r.event_id
         ORDER BY r.registered_at DESC
         LIMIT 12
        """
    ).fetchall()

    events = db.execute(
        "SELECT * FROM events ORDER BY start_dt ASC NULLS LAST, date ASC LIMIT 50").fetchall()

    pending = db.execute(
        """
        SELECT r.*, u.name AS user_name, e.title AS event_title
          FROM registrations r
          JOIN users u ON u.id=r.user_id
          JOIN events e ON e.id=r.event_id
         WHERE r.submitted_at IS NOT NULL AND r.approved_hours IS NULL
         ORDER BY r.submitted_at DESC
        """
    ).fetchall()

    return render_template("dashboard_admin.html",
                           stats=stats, latest_regs=latest_regs, events=events, pending=pending)


@app.route("/admin/registrations/<int:reg_id>/approve", methods=["POST"])
@admin_required
def approve_hours(reg_id: int):
    db = get_db()
    r = db.execute("SELECT * FROM registrations WHERE id=?", (reg_id,)).fetchone()
    if not r:
        flash(_("not_found"))
        return redirect(url_for("dashboard_admin"))

    total = (r["self_hours"] or 0.0) + (r["extra_hours"] or 0.0)
    now = datetime.utcnow().strftime("%Y-%m-%d %H:%M")
    db.execute(
        """
        UPDATE registrations
           SET approved_hours=?,
               approved_by=?,
               approved_at=?,
               hours=?,
               status=CASE WHEN status='cancelled' THEN status ELSE 'attended' END
         WHERE id=?
        """,
        (total, session["user_id"], now, total, reg_id)
    )
    db.commit()
    flash(_("hours_approved_ok"))
    return redirect(url_for("dashboard_admin"))


@app.route("/admin/hours/<int:reg_id>/reject", methods=["POST"])
@admin_required
def reject_hours(reg_id: int):
    db = get_db()
    db.execute("""
        UPDATE registrations
           SET status         = 'cancelled',
               hours          = 0,
               self_hours     = NULL,
               extra_hours    = NULL,
               extra_desc     = NULL,
               submitted_at   = NULL,
               approved_hours = NULL,
               approved_at    = NULL

         WHERE id = ?
    """, (reg_id,))
    db.commit()
    flash(_("hours_rejected_ok"))
    return redirect(url_for("dashboard_admin"))


@app.route("/admin/export_hours")
@admin_required
def export_hours():
    db = get_db()
    rows = db.execute(
        """
        SELECT u.name AS volunteer,
               u.email AS email,
               e.title AS event,
               e.start_dt AS start,
               e.end_dt   AS end,
               r.self_hours,
               r.extra_hours,
               r.extra_desc,
               r.approved_hours,
               r.approved_at
          FROM registrations r
          JOIN users u ON u.id=r.user_id
          JOIN events e ON e.id=r.event_id
         WHERE r.approved_hours IS NOT NULL
         ORDER BY r.approved_at DESC
        """
    ).fetchall()

    output = StringIO(newline="")
    writer = csv.writer(output)
    writer.writerow([
        "Volunteer", "Email", "Event", "Start", "End",
        "Self Hours", "Extra Hours", "Extra Description",
        "Approved Hours", "Approved At"
    ])
    for r in rows:
        writer.writerow([
            r["volunteer"], r["email"], r["event"], r["start"], r["end"],
            r["self_hours"], r["extra_hours"], r["extra_desc"],
            r["approved_hours"], r["approved_at"]
        ])

    csv_text = output.getvalue()
    output.close()

    # BOM + UTF-8
    csv_bytes = ("\ufeff" + csv_text).encode("utf-8-sig")

    return Response(
        csv_bytes,
        mimetype="text/csv; charset=utf-8",
        headers={"Content-Disposition": "attachment; filename=hours.csv"}
    )


@app.route("/admin/events/create", methods=["POST"])
@admin_required
def create_event():
    f = request.form
    title = (f.get("title") or "").strip()
    start_dt = (f.get("start_dt") or "").strip()
    end_dt = (f.get("end_dt") or "").strip()
    location = (f.get("location") or "").strip()
    description = (f.get("description") or "").strip() or None
    capacity = (f.get("capacity") or "").strip()

    if not title or not start_dt or not end_dt or not location:
        flash("Title, start time, end time, and location are required.")
        return redirect(url_for("dashboard_admin"))

    fmt = "%Y-%m-%dT%H:%M"

    try:
        start = datetime.strptime(start_dt, fmt)
        end = datetime.strptime(end_dt, fmt)
    except ValueError:

        flash("Invalid date format. Use browser datetime picker (YYYY-MM-DDTHH:MM).")
        return redirect(url_for("dashboard_admin"))

    if end <= start:
        flash("End time must be after start time.")
        return redirect(url_for("dashboard_admin"))

    duration_hours = (end - start).total_seconds() / 3600.0

    capacity_val = int(capacity) if capacity.isdigit() else None

    db = get_db()
    db.execute(
        """
        INSERT INTO events (title, description, start_dt, end_dt, location, capacity, created_by, date)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (title, description, start_dt, end_dt, location,
         capacity_val, session["user_id"], start_dt),
    )
    db.commit()

    flash(_("event_created_duration").format(title=title, hours=duration_hours))

    return redirect(url_for("dashboard_admin"))


def admin_required_view():
    if session.get("role") != "admin":
        flash(_("admin_needed"))
        return redirect(url_for("home"))


@app.route("/admin/events/<int:event_id>/edit", methods=["GET"])
def edit_event_form(event_id):
    # Admin check
    if session.get("role") != "admin":
        flash(_("admin_needed"))
        return redirect(url_for("home"))

    db = get_db()
    ev = db.execute("SELECT * FROM events WHERE id = ?", (event_id,)).fetchone()
    if not ev:
        raise NotFound(_("event_not_found"))
    return render_template("event_edit.html", ev=ev)


@app.route("/admin/events/<int:event_id>/edit", methods=["POST"])
def edit_event_submit(event_id):
    # Admin check
    if session.get("role") != "admin":
        flash(_("admin_needed"))
        return redirect(url_for("home"))

    title = request.form.get("title", "").strip()
    description = request.form.get("description", "").strip()
    date = request.form.get("date", "").strip()      # "YYYY-MM-DD HH:MM"
    location = request.form.get("location", "").strip()
    capacity = request.form.get("capacity", "").strip()

    if not title or not date or not location:
        flash(_("not_found"))
        return redirect(url_for("edit_event_form", event_id=event_id))

    cap_val = None
    if capacity:
        try:
            cap_val = int(capacity)
        except ValueError:
            cap_val = None

    db = get_db()
    db.execute("""
        UPDATE events
           SET title = ?, description = ?, date = ?, location = ?, capacity = ?
         WHERE id = ?
    """, (title, description, date, location, cap_val, event_id))
    db.commit()

    flash(_("event_updated"))
    return redirect(url_for("dashboard_admin"))


@app.route("/admin/events/<int:event_id>/delete", methods=["POST"])
def delete_event(event_id):
    if session.get("role") != "admin":
        flash(_("admin_needed"))
        return redirect(url_for("home"))

    db = get_db()

    db.execute("DELETE FROM registrations WHERE event_id = ?", (event_id,))

    db.execute("DELETE FROM events WHERE id = ?", (event_id,))
    db.commit()
    flash("Event deleted successfully.")
    return redirect(url_for("dashboard_admin"))


@app.route("/admin/registrations/<int:reg_id>/mark", methods=["POST"])
@admin_required
def mark_attendance(reg_id: int):
    status = request.form.get("status", "registered").strip()
    hours_str = request.form.get("hours", "0").strip()
    try:
        hours = max(0.0, float(hours_str))
    except ValueError:
        hours = 0.0
    if status not in ("registered", "attended", "cancelled"):
        status = "registered"
    db = get_db()
    db.execute("UPDATE registrations SET status = ?, hours = ? WHERE id = ?", (status, hours, reg_id))
    db.commit()
    flash(_("reg_updated"))
    return redirect(url_for("dashboard_admin"))


# Exports & misc

@app.route("/admin/export.csv")
@admin_required
def export_csv():
    db = get_db()
    rows = db.execute(
        """
        SELECT u.name AS volunteer_name, u.email,
               e.title AS event_title, e.date AS event_date,
               r.status, r.hours, r.registered_at
        FROM registrations r
        JOIN users u ON u.id = r.user_id
        JOIN events e ON e.id = r.event_id
        ORDER BY e.date DESC, u.name ASC
        """
    ).fetchall()
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Volunteer", "Email", "Event", "Event Date",
                    "Status", "Hours", "Registered At"])
    for row in rows:
        writer.writerow([row["volunteer_name"], row["email"], row["event_title"],
                        row["event_date"], row["status"], row["hours"], row["registered_at"]])
    output.seek(0)
    return Response(output.getvalue(), mimetype="text/csv",
                    headers={"Content-Disposition": "attachment; filename=registrations_export.csv"})


@app.route("/certificate/<int:reg_id>.pdf")
@login_required
def certificate_pdf(reg_id: int):
    if not REPORTLAB_AVAILABLE:
        flash("PDF generation is not available on this server.")
        return redirect(url_for("dashboard_volunteer"))
    db = get_db()
    reg = db.execute(
        """
        SELECT r.*, u.name AS user_name, e.title AS event_title, e.date AS event_date
        FROM registrations r
        JOIN users u ON u.id = r.user_id
        JOIN events e ON e.id = r.event_id
        WHERE r.id = ?
        """, (reg_id,)
    ).fetchone()
    if not reg:
        flash(_("event_not_found"))
        return redirect(url_for("dashboard_volunteer"))
    if session.get("role") != "admin" and reg["user_id"] != session.get("user_id"):
        flash("Not allowed.")
        return redirect(url_for("dashboard_volunteer"))

    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    c.setTitle("Volunteer Certificate")
    c.setLineWidth(4)
    c.rect(1.2 * cm, 1.2 * cm, width - 2.4 * cm, height - 2.4 * cm)
    c.setFont("Helvetica-Bold", 28)
    c.drawCentredString(width / 2, height - 4 * cm, "Certificate of Appreciation")
    c.setFont("Helvetica", 14)
    c.drawCentredString(width / 2, height - 6 * cm, "This certificate is proudly presented to")
    c.setFont("Helvetica-Bold", 20)
    c.drawCentredString(width / 2, height - 7.2 * cm, reg["user_name"])
    c.setFont("Helvetica", 14)
    c.drawCentredString(width / 2, height - 8.6 * cm, f"For volunteering in: {reg['event_title']}")
    c.drawCentredString(width / 2, height - 9.8 * cm, f"Hours credited: {reg['hours']:.2f}")
    c.drawCentredString(width / 2, height - 11.0 * cm, f"Event date: {reg['event_date']}")
    c.line(width / 2 - 4 * cm, 3.5 * cm, width / 2 + 4 * cm, 3.5 * cm)
    c.setFont("Helvetica-Oblique", 12)
    c.drawCentredString(width / 2, 2.9 * cm, "Authorized Signature")
    c.showPage()
    c.save()
    buffer.seek(0)
    return send_file(buffer, as_attachment=True, download_name=f"certificate_{reg_id}.pdf", mimetype="application/pdf")


@app.route("/events/<int:event_id>/ics")
@login_required
def event_ics(event_id: int):
    db = get_db()
    ev = db.execute("SELECT * FROM events WHERE id = ?", (event_id,)).fetchone()
    if not ev:
        flash(_("event_not_found"))
        return redirect(url_for("events"))
    raw = str(ev["date"])
    dtstart = None
    for p in ("%Y-%m-%d %H:%M", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d"):
        try:
            dtstart = datetime.strptime(raw, p)
            break
        except ValueError:
            continue
    uid = f"event-{event_id}@volunteer-hub"
    lines = ["BEGIN:VCALENDAR", "VERSION:2.0", "PRODID:-//VolunteerHub//EN", "BEGIN:VEVENT"]
    if dtstart:
        lines.append("DTSTART:" + dtstart.strftime("%Y%m%dT%H%M%S"))
        dtend = dtstart.replace(hour=min(dtstart.hour + 2, 23))
        lines.append("DTEND:" + dtend.strftime("%Y%m%dT%H%M%S"))
    else:
        lines.append("DTSTART;VALUE=DATE:" + raw.replace("-", ""))
    lines += [f"UID:{uid}", f"SUMMARY:{ev['title']}",
              f"LOCATION:{ev['location']}", "END:VEVENT", "END:VCALENDAR"]
    ics = "\r\n".join(lines)
    return Response(ics, mimetype="text/calendar",
                    headers={"Content-Disposition": f"attachment; filename=event_{event_id}.ics"})


@app.route("/favicon.ico")
def favicon():
    """Serve favicon if present under static/; avoids double 404s."""
    return send_from_directory(os.path.join(app.root_path, "static"), "favicon.ico",
                               mimetype="image/vnd.microsoft.icon")


@app.errorhandler(500)
def server_error(e):
    flash("An unexpected error occurred. Please try again.")
    return redirect(url_for("home"))


# Entrypoint
if __name__ == "__main__":
    if not os.path.exists(DB_PATH):
        with app.app_context():
            init_db()
            print("Database created at:", DB_PATH)
    app.run(debug=True)
