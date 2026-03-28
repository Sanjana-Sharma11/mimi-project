import sqlite3

conn = sqlite3.connect("database.db")
cursor = conn.cursor()

# users table
cursor.execute("""
CREATE TABLE IF NOT EXISTS users(
id INTEGER PRIMARY KEY AUTOINCREMENT,
username TEXT,
password TEXT
)
""")

# transactions table
cursor.execute("""
CREATE TABLE IF NOT EXISTS transactions(
id INTEGER PRIMARY KEY AUTOINCREMENT,
username TEXT,
type TEXT,
amount INTEGER
)
""")

conn.commit()
conn.close()

print("Database and tables created successfully")