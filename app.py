from flask import Flask, render_template, request, redirect, url_for, flash, session, abort, Response
import sqlite3
import os
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
import csv
import io

# Create Flask app
app = Flask(__name__)

# Secret key is needed for flash messages
app.secret_key = "dev"

# Path to SQLite database file
DB_PATH = os.path.join("database", "laptops.db")


def get_db_connection():
    """
    Open database connection and return it.
    row_factory makes rows behave like dictionary (row["column"]).
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """
    Create tables if they do not exist.
    This runs one time when app starts.
    """
    conn = get_db_connection()

    # Laptops table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS laptops (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            asset_tag TEXT UNIQUE NOT NULL,
            serial_number TEXT UNIQUE NOT NULL,
            brand TEXT NOT NULL,
            model TEXT NOT NULL,
            location TEXT,
            status TEXT NOT NULL,
            student_name TEXT,
            student_id TEXT,
            notes TEXT
        );
    """)

    # Users table for login
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL,
            student_id TEXT
        );
    """)

    # Seed demo users (only if they don't exist)
    conn.execute("""
        INSERT OR IGNORE INTO users (username, password_hash, role, student_id)
        VALUES (?, ?, ?, ?)
    """, ("admin", generate_password_hash("Admin123!"), "admin", None))

    conn.execute("""
        INSERT OR IGNORE INTO users (username, password_hash, role, student_id)
        VALUES (?, ?, ?, ?)
    """, ("sara", generate_password_hash("Student123!"), "student", "S1001"))

    conn.execute("""
        INSERT OR IGNORE INTO users (username, password_hash, role, student_id)
        VALUES (?, ?, ?, ?)
    """, ("marko", generate_password_hash("Student123!"), "student", "S1002"))

    conn.commit()
    conn.close()


# ---------------------------
# Login helpers (decorators)
# ---------------------------

def login_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("login"))
        return func(*args, **kwargs)
    return wrapper


def admin_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if session.get("role") != "admin":
            abort(403)
        return func(*args, **kwargs)
    return wrapper


@app.errorhandler(403)
def forbidden(e):
    flash("Access denied.", "danger")
    if session.get("role") == "student":
        return redirect(url_for("student_dashboard"))
    return redirect(url_for("login"))


# ---------------------------
# CSV helper
# ---------------------------

def rows_to_csv_response(rows, filename):
    output = io.StringIO()
    writer = csv.writer(output)

    # Header
    writer.writerow([
        "id", "asset_tag", "serial_number", "brand", "model",
        "location", "status", "student_name", "student_id", "notes"
    ])

    # Data rows
    for r in rows:
        writer.writerow([
            r["id"], r["asset_tag"], r["serial_number"], r["brand"], r["model"],
            r["location"], r["status"], r["student_name"], r["student_id"], r["notes"]
        ])

    csv_text = output.getvalue()
    output.close()

    return Response(
        csv_text,
        mimetype="text/csv",
        headers={"Content-Disposition": f"attachment;filename={filename}"}
    )


# ---------------------------
# Login routes
# ---------------------------

@app.route("/login", methods=["GET", "POST"])
def login():
    """
    Login page for admin and student.
    """
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        conn = get_db_connection()
        user = conn.execute(
            "SELECT * FROM users WHERE username = ?",
            (username,)
        ).fetchone()
        conn.close()

        if user is None or not check_password_hash(user["password_hash"], password):
            flash("Invalid username or password.", "danger")
            return render_template("login.html")

        session["user_id"] = user["id"]
        session["username"] = user["username"]
        session["role"] = user["role"]
        session["student_id"] = user["student_id"]

        flash("Login successful.", "success")
        return redirect(url_for("home"))

    return render_template("login.html")


@app.route("/logout")
def logout():
    """
    Logout and clear session.
    """
    session.clear()
    flash("You are logged out.", "info")
    return redirect(url_for("login"))


# ---------------------------
# Home routing (role-based)
# ---------------------------

@app.route("/")
def home():
    """
    If not logged in -> /login
    If admin -> /laptops
    If student -> /student
    """
    if "user_id" not in session:
        return redirect(url_for("login"))

    if session.get("role") == "admin":
        return redirect(url_for("laptops"))

    return redirect(url_for("student_dashboard"))


# ---------------------------
# Student dashboard (read-only)
# ---------------------------

@app.route("/student")
@login_required
def student_dashboard():
    """
    Student sees only laptops assigned to their student_id (read-only).
    """
    if session.get("role") != "student":
        return redirect(url_for("laptops"))

    sid = session.get("student_id", "")

    conn = get_db_connection()
    rows = conn.execute("""
        SELECT * FROM laptops
        WHERE student_id = ?
        ORDER BY id DESC
    """, (sid,)).fetchall()
    conn.close()

    return render_template("student_dashboard.html", laptops=rows, student_id=sid)


# ---------------------------
# Admin routes (protected)
# ---------------------------

@app.route("/laptops")
@login_required
@admin_required
def laptops():
    """
    Show laptop list (ADMIN).
    Supports:
    - search text (q)
    - status filter (status)
    - dashboard statistics
    """
    search_text = request.args.get("q", "").strip()
    status_filter = request.args.get("status", "").strip()

    conn = get_db_connection()

    # Dashboard statistics
    total_devices = conn.execute(
        "SELECT COUNT(*) FROM laptops"
    ).fetchone()[0]

    assigned_devices = conn.execute(
        "SELECT COUNT(*) FROM laptops WHERE status = ?",
        ("assigned",)
    ).fetchone()[0]

    available_devices = conn.execute(
        "SELECT COUNT(*) FROM laptops WHERE status = ?",
        ("available",)
    ).fetchone()[0]

    repair_devices = conn.execute(
        "SELECT COUNT(*) FROM laptops WHERE status = ?",
        ("repair",)
    ).fetchone()[0]

    lost_devices = conn.execute(
        "SELECT COUNT(*) FROM laptops WHERE status = ?",
        ("lost",)
    ).fetchone()[0]

    retired_devices = conn.execute(
        "SELECT COUNT(*) FROM laptops WHERE status = ?",
        ("retired",)
    ).fetchone()[0]

    # Laptop list query
    sql = "SELECT * FROM laptops WHERE 1=1"
    params = []

    if search_text:
        like = f"%{search_text}%"
        sql += """
            AND (
                asset_tag LIKE ?
                OR serial_number LIKE ?
                OR brand LIKE ?
                OR model LIKE ?
                OR LOWER(student_name) LIKE LOWER(?)
                OR student_id LIKE ?
            )
        """
        params.extend([like, like, like, like, like, like])

    if status_filter:
        sql += " AND status = ?"
        params.append(status_filter)

    laptop_rows = conn.execute(sql, params).fetchall()
    conn.close()

    return render_template(
        "laptops.html",
        laptops=laptop_rows,
        total_devices=total_devices,
        assigned_devices=assigned_devices,
        available_devices=available_devices,
        repair_devices=repair_devices,
        lost_devices=lost_devices,
        retired_devices=retired_devices
    )


@app.route("/scan")
@login_required
@admin_required
def scan_barcode():
    """
    Simple scan page (ADMIN).
    It reads ?code=...
    code can match asset_tag or serial_number.
    """
    code = request.args.get("code", "").strip()

    if code == "":
        return redirect(url_for("laptops"))

    conn = get_db_connection()

    laptop = conn.execute("""
        SELECT asset_tag, status, student_name, student_id
        FROM laptops
        WHERE asset_tag = ? OR serial_number = ?
    """, (code, code)).fetchone()

    conn.close()

    if laptop is None:
        flash("Laptop not found.", "danger")
        return redirect(url_for("laptops"))

    if laptop["status"] == "assigned" and laptop["student_name"]:
        flash(
            "Laptop " + laptop["asset_tag"] + " is assigned to " +
            laptop["student_name"] + " (ID: " + str(laptop["student_id"]) + ")",
            "success"
        )
    else:
        flash(
            "Laptop " + laptop["asset_tag"] + " is not assigned right now.",
            "info"
        )

    return redirect(url_for("laptops"))


@app.route("/laptops/new", methods=["GET", "POST"])
@login_required
@admin_required
def add_laptop():
    """
    Add a new laptop (ADMIN).
    """
    if request.method == "POST":
        asset_tag = request.form["asset_tag"]
        serial_number = request.form["serial_number"]
        brand = request.form["brand"]
        model = request.form["model"]
        location = request.form.get("location", "")
        status = request.form["status"]
        student_name = request.form.get("student_name", "")
        student_id = request.form.get("student_id", "")
        notes = request.form.get("notes", "")

        conn = get_db_connection()

        conn.execute("""
            INSERT INTO laptops
            (asset_tag, serial_number, brand, model, location, status, student_name, student_id, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (asset_tag, serial_number, brand, model, location, status, student_name, student_id, notes))

        conn.commit()
        conn.close()

        flash("Laptop saved.", "success")
        return redirect(url_for("laptops"))

    return render_template("add_laptop.html")


@app.route("/laptops/<int:id>/edit", methods=["GET", "POST"])
@login_required
@admin_required
def edit_laptop(id):
    """
    Edit one laptop by id (ADMIN).
    """
    conn = get_db_connection()

    laptop = conn.execute(
        "SELECT * FROM laptops WHERE id = ?",
        (id,)
    ).fetchone()

    if laptop is None:
        conn.close()
        flash("Laptop not found.", "danger")
        return redirect(url_for("laptops"))

    if request.method == "POST":
        asset_tag = request.form["asset_tag"]
        serial_number = request.form["serial_number"]
        brand = request.form["brand"]
        model = request.form["model"]
        location = request.form.get("location", "")
        status = request.form["status"]
        student_name = request.form.get("student_name", "")
        student_id = request.form.get("student_id", "")
        notes = request.form.get("notes", "")

        conn.execute("""
            UPDATE laptops
            SET asset_tag = ?,
                serial_number = ?,
                brand = ?,
                model = ?,
                location = ?,
                status = ?,
                student_name = ?,
                student_id = ?,
                notes = ?
            WHERE id = ?
        """, (asset_tag, serial_number, brand, model, location, status, student_name, student_id, notes, id))

        conn.commit()
        conn.close()

        flash("Laptop updated.", "success")
        return redirect(url_for("laptops"))

    conn.close()
    return render_template("edit_laptop.html", laptop=laptop)


@app.route("/laptops/<int:id>/delete", methods=["POST"])
@login_required
@admin_required
def delete_laptop(id):
    """
    Delete laptop by id (ADMIN).
    """
    conn = get_db_connection()

    conn.execute("DELETE FROM laptops WHERE id = ?", (id,))
    conn.commit()
    conn.close()

    flash("Laptop deleted.", "info")
    return redirect(url_for("laptops"))


# ---------------------------
# CSV Export routes (ADMIN ONLY)
# ---------------------------

@app.route("/export/all")
@login_required
@admin_required
def export_all():
    conn = get_db_connection()
    rows = conn.execute("SELECT * FROM laptops ORDER BY id DESC").fetchall()
    conn.close()
    return rows_to_csv_response(rows, "laptops_all.csv")


@app.route("/export/filtered")
@login_required
@admin_required
def export_filtered():
    search_text = request.args.get("q", "").strip()
    status_filter = request.args.get("status", "").strip()

    sql = "SELECT * FROM laptops WHERE 1=1"
    params = []

    if search_text:
        like = f"%{search_text}%"
        sql += """
            AND (
                asset_tag LIKE ?
                OR serial_number LIKE ?
                OR brand LIKE ?
                OR model LIKE ?
                OR student_name LIKE ?
                OR student_id LIKE ?
            )
        """
        params.extend([like, like, like, like, like, like])

    if status_filter:
        sql += " AND status = ?"
        params.append(status_filter)

    sql += " ORDER BY id DESC"

    conn = get_db_connection()
    rows = conn.execute(sql, params).fetchall()
    conn.close()

    return rows_to_csv_response(rows, "laptops_filtered.csv")


if __name__ == "__main__":
    os.makedirs("database", exist_ok=True)
    init_db()
    app.run(debug=False)