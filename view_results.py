import sqlite3

conn = sqlite3.connect('database.db')
cur = conn.cursor()

# عرض أسماء الجداول
cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
print("🗂️ الجداول الموجودة:", cur.fetchall())

# عرض أول 5 نتائج من جدول النتائج
cur.execute("SELECT * FROM results LIMIT 5;")
print("📊 بعض النتائج:", cur.fetchall())

conn.close()