import sqlite3
import hashlib
from typing import Optional, Dict

from .shared_theme import G1, G2

DB_PATH = "datasets/data.db"

def get_conn():
    return sqlite3.connect(DB_PATH)

def hash_pw(pw: str) -> str:
    return hashlib.sha256(pw.encode()).hexdigest()

class UserManager:
    """Simple user management helper used by the UI.
    
    Provides login, logout, profile update and password change.
    All methods raise ``ValueError`` with a user‑friendly message on failure.
    """
    def __init__(self):
        self.current_user: Optional[Dict] = None

    def login(self, email: str, password: str, role: str) -> Dict:
        """Authenticate a user.
        
        Args:
            email: Email entered by the user.
            password: Plain password.
            role: Human‑readable role string as shown in the UI ("Khách hàng", "Nhân viên", "Chủ đầu tư").
        Returns:
            A dict with user fields.
        Raises:
            ValueError: If credentials are invalid.
        """
        if not email or not password:
            raise ValueError("⚠️ Vui lòng nhập email và mật khẩu.")
        role_map = {"Khách hàng": "KhachHang", "Nhân viên": "NhanVien", "Chủ đầu tư": "ChuDauTu"}
        role_key = role_map.get(role)
        if role_key is None:
            raise ValueError("⚠️ Vai trò không hợp lệ.")
        conn = get_conn()
        cur = conn.cursor()
        cur.execute(
            "SELECT MaNguoiDung, HoTen, Sdt, Email, MatKhau FROM NGUOI_DUNG WHERE Email=? AND VaiTro=?",
            (email, role_key),
        )
        row = cur.fetchone()
        conn.close()
        if row is None:
            raise ValueError("❌ Email không tồn tại hoặc sai vai trò.")
        stored_hash = row[4]
        if stored_hash is not None and stored_hash != hash_pw(password):
            raise ValueError("❌ Mật khẩu không đúng.")
        user_info = {
            "MaNguoiDung": row[0],
            "HoTen": row[1],
            "Sdt": row[2],
            "Email": row[3],
            "VaiTro": role_key,
        }
        self.current_user = user_info
        return user_info

    def logout(self):
        self.current_user = None

    def update_profile(self, user_id: str, ho_ten: str, email: str, sdt: str):
        if not ho_ten or not email or not sdt:
            raise ValueError("⚠️ Tất cả trường thông tin bắt buộc.")
        conn = get_conn()
        cur = conn.cursor()
        cur.execute(
            "UPDATE NGUOI_DUNG SET HoTen=?, Email=?, Sdt=? WHERE MaNguoiDung=?",
            (ho_ten, email, sdt, user_id),
        )
        conn.commit()
        conn.close()
        # refresh the cached user info if logged in
        if self.current_user and self.current_user["MaNguoiDung"] == user_id:
            self.current_user.update({"HoTen": ho_ten, "Email": email, "Sdt": sdt})

    def change_password(self, user_id: str, old_pw: str, new_pw: str):
        if len(new_pw) < 6:
            raise ValueError("⚠️ Mật khẩu mới ít nhất 6 ký tự.")
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("SELECT MatKhau FROM NGUOI_DUNG WHERE MaNguoiDung=?", (user_id,))
        stored = cur.fetchone()
        if stored is None:
            conn.close()
            raise ValueError("❌ Không tìm thấy người dùng.")
        if stored[0] != hash_pw(old_pw):
            conn.close()
            raise ValueError("❌ Mật khẩu hiện tại chưa đúng.")
        cur.execute(
            "UPDATE NGUOI_DUNG SET MatKhau=? WHERE MaNguoiDung=?",
            (hash_pw(new_pw), user_id),
        )
        conn.commit()
        conn.close()
        # if currently logged in, we keep the session alive
        return True
