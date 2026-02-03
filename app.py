from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)

DB_NAME = "inventory.db"

def get_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/laptops")
def laptops():
    return "Laptops page is coming next."


@app.route("/laptops/new", methods=["GET", "POST"])
def add_laptop():
    if request.method == "POST":
        asset_tag = request.form["asset_tag"]
        serial_number = request.form["serial_number"]
        brand = request.form["brand"]
        model = request.form["model"]
        location = request.form["location"]
        status = request.form["status"]
        notes = request.form["notes"]

        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO laptops (asset_tag, serial_number, brand, model, location, status, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (asset_tag, serial_number, brand, model, location, status, notes))

        conn.commit()
        conn.close()

        return redirect(url_for("home"))

    return render_template("add_laptop.html")


if __name__ == "__main__":
    app.run(debug=True)
