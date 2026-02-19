# Laptop Inventory System

## Project Overview
This project is a simple laptop inventory web application built with Flask and SQLite.  
It was created as a final project for the CIS 260 course.

The main goal of the application is to help a school keep track of laptops, their status, and student assignments.

---

## What the Application Does

The application allows users to:

- View a list of all laptops
- Search laptops by asset tag, serial number, brand, model, or student information
- Filter laptops by status (Available, Assigned, Repair, Lost, Retired)
- Add new laptops
- Edit existing laptop information
- Delete laptops from the inventory

Each laptop record includes:

- Asset tag
- Serial number
- Brand
- Model
- Location
- Status
- Optional student details

---

## Technologies Used

- Python
- Flask
- SQLite
- HTML
- Bootstrap

---

## How to Run the Application

1. Make sure Python is installed on your computer.
2. Open a terminal inside the project folder.
3. Install required packages:

```bash
pip install -r requirements.txt
```

4. Start the application:

```bash
python app.py
```

5. Open your browser and go to:

```text
http://127.0.0.1:5000
```

The application runs locally and uses a local SQLite database.

---

## AI Assistance

AI tools were used as a guided learning assistant during development.  
The author actively built, tested, and integrated the entire application.  
All final decisions and project integration were completed by the author.

---

## Future Improvements

Possible future enhancements include:

- User authentication system (Admin / Staff login)
- Role-based access control
- Export inventory data to CSV
- Dashboard with statistics (Total Devices, Assigned, Available, etc.)
- Barcode scanning integration
- Cloud database integration
- Audit log tracking system

---

## Notes

This project is intentionally designed to be simple and easy to understand, focusing on core CRUD functionality and database integration.
