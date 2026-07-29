import sqlite3

conn = sqlite3.connect("database.db")
c = conn.cursor()

# ❌ DROP OLD TABLES (CLEAN RESET)
c.execute("DROP TABLE IF EXISTS hospital")
c.execute("DROP TABLE IF EXISTS donor")
c.execute("DROP TABLE IF EXISTS patient")
c.execute("DROP TABLE IF EXISTS requests")

# ✅ CREATE NEW CORRECT TABLES

c.execute("""
CREATE TABLE hospital(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    email TEXT,
    password TEXT
)
""")

c.execute("""
CREATE TABLE donor(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    email TEXT,
    phone TEXT,
    blood_group TEXT,
    last_donation TEXT,
    status TEXT
)
""")

c.execute("""
CREATE TABLE patient(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    hospital_id INTEGER,
    name TEXT,
    location TEXT,
    blood_group TEXT
)
""")

c.execute("""
CREATE TABLE requests(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_id INTEGER,
    donor_id INTEGER,
    response TEXT
)
""")

conn.commit()
conn.close()

print("✅ Database RESET SUCCESSFUL")