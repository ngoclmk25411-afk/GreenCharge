import sqlite3
from typing import List, Tuple

DB_PATH = "datasets/data.db"

def get_conn():
    return sqlite3.connect(DB_PATH)

def get_vehicles_by_user(user_id: str) -> List[Tuple[int, str, str]]:
    """Return a list of vehicles for a given user.
    Returns list of (id, bien_so, chuan_sac).
    """
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT Id, BienSo, ChuanSac FROM XE WHERE MaNguoiDung=?", (user_id,))
    rows = cur.fetchall()
    conn.close()
    return rows

def add_vehicle(user_id: str, bien_so: str, chuan_sac: str) -> None:
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("INSERT INTO XE (MaNguoiDung, BienSo, ChuanSac) VALUES (?,?,?)", (user_id, bien_so, chuan_sac))
    conn.commit()
    conn.close()

def update_vehicle(vehicle_id: int, bien_so: str, chuan_sac: str) -> None:
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("UPDATE XE SET BienSo=?, ChuanSac=? WHERE Id=?", (bien_so, chuan_sac, vehicle_id))
    conn.commit()
    conn.close()

def delete_vehicle(vehicle_id: int) -> None:
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("DELETE FROM XE WHERE Id=?", (vehicle_id,))
    conn.commit()
    conn.close()
