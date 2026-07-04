import sqlite3
import os

db_path = os.path.join(os.path.dirname(__file__), 'data.db')
sql_path = os.path.join(os.path.dirname(__file__), 'data_sqlite.sql')

# Xóa file db cũ nếu có
if os.path.exists(db_path):
    os.remove(db_path)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

try:
    with open(sql_path, 'r', encoding='utf-8') as f:
        sql_script = f.read()
    
    # Thực thi toàn bộ mã SQL
    cursor.executescript(sql_script)
    conn.commit()
    print("Khoi tao SQLite database thanh cong tai:", db_path)
except sqlite3.Error as e:
    print("Loi khi khoi tao SQLite database:", e)
finally:
    conn.close()
