import sqlite3

conn = sqlite3.connect('database.db')
cur = conn.cursor()

cur.execute('''
    CREATE TABLE IF NOT EXISTS results (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        filename TEXT,
        disease TEXT,
        probability REAL,
        date TEXT
    )
''')

conn.commit()
conn.close()
print("✅ تم إنشاء قاعدة البيانات بنجاح.")