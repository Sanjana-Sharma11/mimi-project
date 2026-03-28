import sqlite3

conn = sqlite3.connect("database.db")
cursor = conn.cursor()

cursor.execute("ALTER TABLE transactions ADD COLUMN date_time TEXT")

conn.commit()
conn.close()

print("date_time column added successfully")