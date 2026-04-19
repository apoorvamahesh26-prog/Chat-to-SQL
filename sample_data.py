# sample_data.py
# Creates a simple SQLite database with realistic sample data

import sqlite3
import os

def create_sample_database(db_path="company.db"):
    """
    Creates a SQLite database with 3 tables:
    - employees
    - departments
    - sales
    """
    # Remove existing DB so we start fresh every time
    if os.path.exists(db_path):
        print("✅ Database already exists, keeping it!")
    return db_path

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # ─────────────────────────────────────────
    # TABLE 1: departments
    # ─────────────────────────────────────────
    cursor.execute("""
        CREATE TABLE departments (
            dept_id     INTEGER PRIMARY KEY,
            dept_name   TEXT NOT NULL,
            location    TEXT NOT NULL,
            budget      REAL NOT NULL
        )
    """)

    departments = [
        (1, "Engineering",  "Bangalore",  1500000.0),
        (2, "Marketing",    "Mumbai",      800000.0),
        (3, "Sales",        "Delhi",      1200000.0),
        (4, "HR",           "Chennai",     500000.0),
        (5, "Finance",      "Hyderabad",   900000.0),
    ]
    cursor.executemany("INSERT INTO departments VALUES (?,?,?,?)", departments)

    # ─────────────────────────────────────────
    # TABLE 2: employees
    # ─────────────────────────────────────────
    cursor.execute("""
        CREATE TABLE employees (
            emp_id      INTEGER PRIMARY KEY,
            name        TEXT NOT NULL,
            age         INTEGER NOT NULL,
            gender      TEXT NOT NULL,
            dept_id     INTEGER NOT NULL,
            salary      REAL NOT NULL,
            join_date   TEXT NOT NULL,
            city        TEXT NOT NULL,
            FOREIGN KEY (dept_id) REFERENCES departments(dept_id)
        )
    """)

    employees = [
        (1,  "Arjun Sharma",     29, "Male",   1, 75000,  "2021-03-15", "Bangalore"),
        (2,  "Priya Nair",       34, "Female", 2, 62000,  "2019-07-01", "Mumbai"),
        (3,  "Rohit Verma",      27, "Male",   3, 55000,  "2022-01-20", "Delhi"),
        (4,  "Sneha Reddy",      31, "Female", 1, 82000,  "2020-11-10", "Bangalore"),
        (5,  "Karan Mehta",      40, "Male",   5, 95000,  "2017-06-25", "Hyderabad"),
        (6,  "Divya Iyer",       26, "Female", 4, 48000,  "2023-02-14", "Chennai"),
        (7,  "Amit Patel",       35, "Male",   3, 68000,  "2018-09-05", "Delhi"),
        (8,  "Anjali Singh",     30, "Female", 1, 78000,  "2021-08-19", "Bangalore"),
        (9,  "Vikram Bose",      44, "Male",   5, 105000, "2015-04-30", "Hyderabad"),
        (10, "Meera Pillai",     28, "Female", 2, 59000,  "2022-05-11", "Mumbai"),
        (11, "Saurabh Joshi",    33, "Male",   1, 88000,  "2019-12-01", "Bangalore"),
        (12, "Ritu Kapoor",      37, "Female", 3, 72000,  "2018-03-22", "Delhi"),
        (13, "Nikhil Desai",     25, "Male",   4, 45000,  "2023-08-07", "Chennai"),
        (14, "Pooja Agarwal",    32, "Female", 2, 63000,  "2020-10-15", "Mumbai"),
        (15, "Rajesh Kumar",     50, "Male",   5, 120000, "2013-01-08", "Hyderabad"),
    ]
    cursor.executemany("INSERT INTO employees VALUES (?,?,?,?,?,?,?,?)", employees)

    # ─────────────────────────────────────────
    # TABLE 3: sales
    # ─────────────────────────────────────────
    cursor.execute("""
        CREATE TABLE sales (
            sale_id     INTEGER PRIMARY KEY,
            emp_id      INTEGER NOT NULL,
            product     TEXT NOT NULL,
            amount      REAL NOT NULL,
            sale_date   TEXT NOT NULL,
            region      TEXT NOT NULL,
            FOREIGN KEY (emp_id) REFERENCES employees(emp_id)
        )
    """)

    sales = [
        (1,  3,  "Laptop",      85000,  "2024-01-05", "North"),
        (2,  7,  "Phone",       25000,  "2024-01-12", "North"),
        (3,  12, "Tablet",      35000,  "2024-02-03", "North"),
        (4,  3,  "Laptop",      90000,  "2024-02-18", "North"),
        (5,  7,  "Accessories", 8000,   "2024-03-01", "North"),
        (6,  12, "Phone",       28000,  "2024-03-14", "North"),
        (7,  3,  "Laptop",      87000,  "2024-04-07", "North"),
        (8,  7,  "Tablet",      32000,  "2024-04-22", "North"),
        (9,  12, "Accessories", 9500,   "2024-05-10", "North"),
        (10, 3,  "Phone",       24000,  "2024-05-28", "North"),
        (11, 1,  "Software",    45000,  "2024-01-09", "South"),
        (12, 4,  "Software",    52000,  "2024-02-14", "South"),
        (13, 8,  "Hardware",    67000,  "2024-03-20", "South"),
        (14, 11, "Software",    48000,  "2024-04-05", "South"),
        (15, 1,  "Hardware",    71000,  "2024-05-17", "South"),
    ]
    cursor.executemany("INSERT INTO sales VALUES (?,?,?,?,?,?)", sales)

    conn.commit()
    conn.close()
    print(f"✅ Database '{db_path}' created with tables: departments, employees, sales")
    return db_path


def get_schema_description():
    """Returns a human-readable + LLM-friendly schema description."""
    return """
DATABASE SCHEMA (SQLite):

TABLE: employees
  - emp_id    INTEGER  (Primary Key)
  - name      TEXT     (Full name of employee)
  - age       INTEGER  (Age in years)
  - gender    TEXT     (Male / Female)
  - dept_id   INTEGER  (Foreign Key → departments.dept_id)
  - salary    REAL     (Monthly salary in INR)
  - join_date TEXT     (Date joined, format: YYYY-MM-DD)
  - city      TEXT     (City of work)

TABLE: departments
  - dept_id   INTEGER  (Primary Key)
  - dept_name TEXT     (Name of department)
  - location  TEXT     (City of department HQ)
  - budget    REAL     (Annual budget in INR)

TABLE: sales
  - sale_id   INTEGER  (Primary Key)
  - emp_id    INTEGER  (Foreign Key → employees.emp_id)
  - product   TEXT     (Product sold: Laptop / Phone / Tablet / Accessories / Software / Hardware)
  - amount    REAL     (Sale amount in INR)
  - sale_date TEXT     (Date of sale, format: YYYY-MM-DD)
  - region    TEXT     (North / South)

RELATIONSHIPS:
  - employees.dept_id → departments.dept_id
  - sales.emp_id → employees.emp_id
"""


if __name__ == "__main__":
    create_sample_database()
    print(get_schema_description())