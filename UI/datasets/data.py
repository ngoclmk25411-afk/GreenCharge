import sqlite3
conn = sqlite3.connect('datasets/data.db')

# Tạo đối tượng cursor để thực thi lệnh SQL
cursor = conn.cursor()

try:
    # Chạy thử một câu lệnh SQL để lấy dữ liệu (thay 'ten_bang' bằng tên bảng của bạn)
    cursor.execute("SELECT * FROM NGUOI_DUNG LIMIT 5;")

    # Lấy và in kết quả ra màn hình
    rows = cursor.fetchall()
    for row in rows:
        print(row[0], row[2], row[3], row[4])

except sqlite3.Error as e:
    print(f"Có lỗi xảy ra: {e}")

finally:
    # Luôn đóng kết nối khi hoàn thành
    conn.close()