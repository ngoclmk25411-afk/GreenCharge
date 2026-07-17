import sqlite3

conn = sqlite3.connect("datasets/data.db")
cur = conn.cursor()
cur.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='TRAM_SAC'")
print(cur.fetchone()[0])
cur.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='CONG_SAC'")
print(cur.fetchone()[0])
