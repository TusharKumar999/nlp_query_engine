import os
import sqlite3

# Get the absolute path of backend folder
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "demo.db")

# Connect to database at backend folder
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Drop old table if exists
cursor.execute("DROP TABLE IF EXISTS employees")

# Create table
cursor.execute("""
CREATE TABLE employees (
    id INTEGER PRIMARY KEY,
    name TEXT,
    salary REAL
)
""")

# Insert sample data
cursor.execute("INSERT INTO employees (id, name, salary) VALUES (1, 'Aman', 50000), (2, 'Riya', 60000)")

conn.commit()
conn.close()
print(f"Database created at {DB_PATH}")
