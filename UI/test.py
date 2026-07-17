import sqlite3

def test():
    try:
        conn = sqlite3.connect("datasets/data.db")
        cur = conn.cursor()
        cur.execute("INSERT INTO TRAM_SAC (MaTram, TenTram, DiaChi, MaNguoiDung, TrangThaiHoatDong) VALUES ('TS999', 'Test', 'Test', 'CDT0001', 'Hoạt động')")
        conn.commit()
        print("Inserted TRAM_SAC successfully")
        
        cur.execute("INSERT INTO CONG_SAC (MaCong, MaTram, MaChuanSac, CongSuat, LoaiCaySac, TrangThaiCong) VALUES ('CS999', 'TS999', 'CH001', 22.0, 'AC', 'Trống')")
        conn.commit()
        print("Inserted CONG_SAC successfully")
    except Exception as e:
        print("Error:", e)

test()
