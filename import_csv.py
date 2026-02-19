import csv
import sqlite3
import os

DB_PATH = os.path.join("database", "laptops.db")
CSV_PATH = os.path.join("data", "laptops.csv")

def import_laptops():
    if not os.path.exists(CSV_PATH):
        print("CSV file not found:", CSV_PATH)
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    with open(CSV_PATH, newline="", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)

        for row in reader:
            try:
                cursor.execute("""
                    INSERT INTO laptops (
                        asset_tag,
                        serial_number,
                        brand,
                        model,
                        location,
                        status,
                        student_name,
                        student_id,
                        notes
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    row["asset_tag"],
                    row["serial_number"],
                    row["brand"],
                    row["model"],
                    row["location"],
                    row["status"],
                    row["student_name"],
                    row["student_id"],
                    row["notes"]
                ))
            except sqlite3.IntegrityError:
                # preskače duplikate ako ponovo pokreneš skriptu
                continue

    conn.commit()
    conn.close()
    print("CSV import completed successfully.")

if __name__ == "__main__":
    import_laptops()
