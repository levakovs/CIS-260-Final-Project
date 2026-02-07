from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
import os

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
    Create table if it does not exist.
    This runs one time when app starts.
    """
    conn = get_db_connection()

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

    conn.commit()
    conn.close()


@app.route("/")
def home():
    """
    Home page. We just redirect to /laptops.
    """
    return redirect(url_for("laptops"))


@app.route("/laptops")
def laptops():
    """
    Show laptop list.
    Supports:
    - search text (q)
    - status filter (status)
    """
    search_text = request.args.get("q", "").strip()
    status_filter = request.args.get("status", "").strip()

    # Start query
    sql = "SELECT * FROM laptops WHERE 1=1"
    params = []

    # Search in multiple columns
    if search_text:
        like = f"%{search_text}%"
        sql += """
            AND (
                asset_tag LIKE ?
                OR serial_number LIKE ?
                OR brand LIKE ?
                OR model LIKE ?
            )
        """
        params.append(like)
        params.append(like)
        params.append(like)
        params.append(like)

    # Filter by status
    if status_filter:
        sql += " AND status = ?"
        params.append(status_filter)

    conn = get_db_connection()
    laptop_rows = conn.execute(sql, params).fetchall()
    conn.close()

    return render_template("laptops.html", laptops=laptop_rows)


@app.route("/scan")
def scan_barcode():
    """
    Simple scan page.
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

    # Show message based on status
    if laptop["status"] == "assigned" and laptop["student_name"]:
        flash(
            "Laptop " + laptop["asset_tag"] + " is assigned to " +
            laptop["student_name"] + " (DI: " + str(laptop["student_id"]) + ")",
            "success"
        )
    else:
        flash(
            "Laptop " + laptop["asset_tag"] + " is not assigned right now.",
            "info"
        )

    return redirect(url_for("laptops"))


@app.route("/laptops/new", methods=["GET", "POST"])
def add_laptop():
    """
    Add a new laptop.
    GET: show form
    POST: save laptop to database
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
def edit_laptop(id):
    """
    Edit one laptop by id.
    GET: show edit form with current data
    POST: update data in database
    """
    conn = get_db_connection()

    laptop = conn.execute(
        "SELECT * FROM laptops WHERE id = ?",
        (id,)
    ).fetchone()

    # If laptop does not exist, go back
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
def delete_laptop(id):
    """
    Delete laptop by id.
    """
    conn = get_db_connection()

    conn.execute("DELETE FROM laptops WHERE id = ?", (id,))
    conn.commit()
    conn.close()

    flash("Laptop deleted.", "info")
    return redirect(url_for("laptops"))


if __name__ == "__main__":
    # Make sure database folder exists
    os.makedirs("database", exist_ok=True)

    # Create table if missing
    init_db()

    # Run the app
    app.run(debug=False)
