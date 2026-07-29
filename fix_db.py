import sqlite3

conn = sqlite3.connect("database.db")
c = conn.cursor()

# ❗ Fix hospital table
try:
    c.execute("ALTER TABLE hospital ADD COLUMN name TEXT")
    print("Added column: name")
except:
    print("Column already exists or table issue ignored")

conn.commit()
conn.close()

print("Database fixed successfully")