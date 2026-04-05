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
## User Roles and Authentication

This application includes a role-based authentication system with two types of users:

### Administrator

The administrator has full access to the system and can:

- View all laptops
- Add, edit, and delete laptop records
- Search and filter the inventory
- Export the full inventory or filtered results to CSV format

### Student

The student has limited access and can:

- Log in to a personal dashboard
- View only laptops assigned to their student ID
- Access is read-only (no editing or deleting allowed)

Route protection is implemented to prevent unauthorized access to administrative pages.

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

## Demo Login Credentials

After starting the application and opening http://127.0.0.1:5000, use the following credentials:

### Administrator Account
- Username: `admin`
- Password: `Admin123!`

### Student Accounts
- Username: `sara`
- Password: `Student123!`

- Username: `marko`
- Password: `Student123!`

These accounts are automatically created when the application runs for the first time.

---

## AI Assistance

AI tools were used as a guided learning assistant during development.  
The author actively built, tested, and integrated the entire application.  
All final decisions and project integration were completed by the author.

---

## Future Improvements

Possible future enhancements include:

- Barcode scanning integration
- Audit log tracking system

---

## Notes

This project is intentionally designed to be simple and easy to understand, focusing on core CRUD functionality and database integration.
