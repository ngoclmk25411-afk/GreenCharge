import sys
import sqlite3
import random
import hashlib
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QComboBox, QTabWidget, QFrame, QSizePolicy,
    QStackedWidget, QStatusBar, QLineEdit, QMessageBox, QScrollArea,
    QGraphicsDropShadowEffect
)
from PyQt6.QtCore import Qt, QSize, QTimer, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QFont, QColor, QPalette, QIcon, QLinearGradient, QPainter

from main.tramsac import TramSacWidget
from main.lich import LichDatChoWidget
from main.phiensac import PhienSacWidget
from main.ttoan import ThanhToanWidget
from main.pin import ThuGomPinWidget
from main.baotri import BaoTriWidget
from main.vehicle import QuanLyXeWidget

DB_PATH = "datasets/data.db"

# ── Màu chủ đạo (Modern Emerald Theme) ──
G1  = "#059669"   # Emerald 600 (Primary)
G2  = "#10b981"   # Emerald 500 (Hover/Gradient)
G3  = "#34d399"   # Emerald 400 (Light)
G_L = "#f6fbf9"   # Nền rất nhạt (App Background)
G_M = "#d1fae5"   # Xanh nhạt (Selection/Highlight)
G_B = "#a7f3d0"   # Border xanh
# ────────────────────────────────────────


def get_conn():
    return sqlite3.connect(DB_PATH)


def hash_pw(pw: str) -> str:
    return hashlib.sha256(pw.encode()).hexdigest()


def shadow(widget, blur=20, color="#059669", alpha=40, dx=0, dy=4):
    eff = QGraphicsDropShadowEffect()
    eff.setBlurRadius(blur)
    c = QColor(color)
    c.setAlpha(alpha)
    eff.setColor(c)
    eff.setOffset(dx, dy)
    widget.setGraphicsEffect(eff)
    return eff


# ══════════════════════════════════════════════
#  GLOBAL STYLESHEET — Light Green Theme
# ══════════════════════════════════════════════
APP_STYLE = f"""
/* ── Base ── */
QMainWindow, QDialog, QWidget {{
    background-color: {G_L};
    color: #1f2937;
    font-family: 'Inter', 'Segoe UI', 'Helvetica Neue', sans-serif;
    font-size: 13px;
}}

/* ── Tab bar ── */
QTabWidget::pane {{
    border: none;
    background-color: transparent;
    top: -1px;
}}
QTabBar::tab {{
    background-color: transparent;
    color: #6b7280;
    padding: 10px 24px;
    border: none;
    border-bottom: 2px solid transparent;
    font-size: 14px;
    font-weight: 600;
    margin-right: 4px;
}}
QTabBar::tab:selected {{
    color: {G1};
    border-bottom: 2px solid {G1};
}}
QTabBar::tab:hover:!selected {{
    color: {G2};
    border-bottom: 2px solid {G_B};
}}

/* ── Labels ── */
QLabel {{ color: #1f2937; }}

/* ── ScrollBar ── */
QScrollBar:vertical {{
    background: transparent; width: 8px; border-radius: 4px; margin: 2px;
}}
QScrollBar::handle:vertical {{
    background: #cbd5e1; border-radius: 4px; min-height: 30px;
}}
QScrollBar::handle:vertical:hover {{ background: #94a3b8; }}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0px; }}

/* ── Status bar ── */
QStatusBar {{
    background-color: #ffffff;
    color: #4b5563;
    border-top: 1px solid #e2e8f0;
    font-size: 11px;
    padding: 4px 12px;
}}

/* ── Table / Tree ── */
QTableWidget, QTreeWidget {{
    background-color: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 10px;
    gridline-color: #f1f5f9;
    color: #1f2937;
    selection-background-color: {G_M};
    selection-color: {G1};
}}
QHeaderView::section {{
    background-color: #f8fafc;
    color: #475569;
    font-weight: 600;
    padding: 10px;
    border: none;
    border-bottom: 1px solid #e2e8f0;
    border-right: 1px solid #f1f5f9;
}}

/* ── General buttons ── */
QPushButton {{
    background-color: {G1};
    color: #ffffff;
    border: none;
    border-radius: 8px;
    padding: 8px 18px;
    font-weight: 600;
    font-size: 13px;
}}
QPushButton:hover {{ background-color: {G2}; }}
QPushButton:pressed {{ background-color: #047857; }}

/* ── Input ── */
QLineEdit, QTextEdit, QSpinBox, QDoubleSpinBox, QDateEdit, QTimeEdit, QDateTimeEdit {{
    background-color: #ffffff;
    color: #1f2937;
    border: 1px solid #d1d5db;
    border-radius: 8px;
    padding: 10px 14px;
    font-size: 13px;
}}
QLineEdit:focus, QTextEdit:focus {{
    border: 1.5px solid {G2};
    background-color: #ffffff;
}}

/* ── ComboBox ── */
QComboBox {{
    background-color: #ffffff;
    color: #1f2937;
    border: 1px solid #d1d5db;
    border-radius: 8px;
    padding: 10px 14px;
    font-size: 13px;
}}
QComboBox:focus {{ border: 1.5px solid {G2}; }}
QComboBox::drop-down {{ border: none; width: 30px; }}
QComboBox::down-arrow {{
    image: none;
    border-left: 5px solid transparent;
    border-right: 5px solid transparent;
    border-top: 6px solid #6b7280;
    margin-right: 10px;
}}
QComboBox::down-arrow:on {{
    border-top: 6px solid {G1};
}}
QComboBox QAbstractItemView {{
    background-color: #ffffff;
    color: #1f2937;
    selection-background-color: {G_M};
    selection-color: {G1};
    border: 1px solid #e2e8f0;
    border-radius: 8px;
    outline: none;
}}

/* ── Message box ── */
QMessageBox {{
    background-color: #ffffff;
}}
QMessageBox QLabel {{ color: #1f2937; font-size: 13px; }}
QMessageBox QPushButton {{
    background-color: {G1}; color: #fff;
    border-radius: 8px; padding: 8px 20px; min-width: 80px;
    font-weight: 600;
}}
QMessageBox QPushButton:hover {{ background-color: {G2}; }}
"""

INPUT_STYLE = f"""
QLineEdit {{
    background-color: #ffffff;
    color: #1f2937;
    border: 1px solid #d1d5db;
    border-radius: 8px;
    padding: 10px 14px;
    font-size: 13px;
}}
QLineEdit:focus {{
    border: 1.5px solid {G2};
    background-color: #ffffff;
}}
"""

CARD_STYLE = f"""
QWidget#auth_card {{
    background-color: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 20px;
}}
"""

BTN_PRIMARY = f"""
QPushButton {{
    background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
        stop:0 {G1}, stop:1 {G2});
    color: #ffffff;
    border: none;
    border-radius: 10px;
    font-size: 14px;
    font-weight: 700;
    padding: 11px;
    letter-spacing: 0.3px;
}}
QPushButton:hover {{
    background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
        stop:0 {G2}, stop:1 {G3});
}}
QPushButton:pressed {{
    background: #047857;
}}
QPushButton:disabled {{
    background: #e5e7eb;
    color: #9ca3af;
}}
"""

BTN_SECONDARY = f"""
QPushButton {{
    background-color: #ffffff;
    color: {G1};
    border: 1.5px solid {G_B};
    border-radius: 10px;
    font-size: 13px;
    font-weight: 600;
    padding: 9px;
}}
QPushButton:hover {{
    background-color: {G_L};
    border-color: {G2};
    color: {G2};
}}
"""

BTN_OUTLINE = f"""
QPushButton {{
    background-color: transparent;
    color: {G1};
    border: none;
    font-size: 12px;
    font-weight: 600;
    text-decoration: underline;
    padding: 4px;
}}
QPushButton:hover {{ color: {G2}; }}
"""

LBL_FIELD = f"color: #374151; font-weight: 700; font-size: 12px; margin-bottom: 2px;"
LBL_HINT  = f"color: #6b7280; font-size: 11px;"

COMBO_STYLE = f"""
QComboBox {{
    background-color: #ffffff; color: #1f2937;
    border: 1px solid #d1d5db; border-radius: 8px;
    padding: 9px 12px; font-size: 13px;
}}
QComboBox:focus {{ border: 1.5px solid {G2}; background: #ffffff; }}
QComboBox::drop-down {{ border: none; }}
QComboBox QAbstractItemView {{
    background-color: #ffffff; color: #1f2937;
    selection-background-color: {G_M}; selection-color: {G1};
    border: 1px solid #e2e8f0; border-radius: 6px;
}}
"""


# ══════════════════════════════════════════════
#  Cửa sổ ĐĂNG KÝ
# ══════════════════════════════════════════════
class RegisterWindow(QWidget):
    def __init__(self, back_callback):
        super().__init__()
        self.back_callback = back_callback
        self._otp_code = None
        self._otp_timer_secs = 0
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._tick_otp)

        self.setWindowTitle("EV Charge & Green — Đăng ký tài khoản")
        self.setMinimumSize(520, 760)
        self.setStyleSheet(APP_STYLE + INPUT_STYLE + CARD_STYLE)
        self.setup_ui()

    def setup_ui(self):
        # Background gradient
        self.setAutoFillBackground(True)
        p = self.palette()
        p.setColor(QPalette.ColorRole.Window, QColor(G_L))
        self.setPalette(p)

        outer = QVBoxLayout(self)
        outer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        outer.setContentsMargins(20, 20, 20, 20)

        card = QWidget(objectName="auth_card")
        card.setFixedWidth(460)
        shadow(card, blur=30, color=G1, alpha=25, dy=8)

        layout = QVBoxLayout(card)
        layout.setSpacing(0)
        layout.setContentsMargins(40, 36, 40, 36)

        # ── Header ──────────────────────────
        header_w = QWidget()
        header_w.setStyleSheet(f"""
            background: qlineargradient(x1:0,y1:0,x2:1,y2:1,
                stop:0 {G1}, stop:1 {G2});
            border-radius: 14px;
            padding: 4px;
        """)
        h_lay = QVBoxLayout(header_w)
        h_lay.setContentsMargins(16, 16, 16, 16)
        h_lay.setSpacing(4)

        logo = QLabel("⚡ EV Charge & Green")
        logo.setFont(QFont("Segoe UI", 20, QFont.Weight.Bold))
        logo.setStyleSheet("color: #ffffff; background: transparent;")
        logo.setAlignment(Qt.AlignmentFlag.AlignCenter)

        tagline = QLabel("Tạo tài khoản mới")
        tagline.setStyleSheet("color: #d1fae5; font-size: 13px; background: transparent;")
        tagline.setAlignment(Qt.AlignmentFlag.AlignCenter)

        h_lay.addWidget(logo)
        h_lay.addWidget(tagline)
        layout.addWidget(header_w)
        layout.addSpacing(24)

        # ── Fields ──────────────────────────
        def field(lbl_txt, widget):
            lbl = QLabel(lbl_txt)
            lbl.setStyleSheet(LBL_FIELD)
            layout.addWidget(lbl)
            layout.addWidget(widget)
            layout.addSpacing(10)

        # Vai trò
        lbl_role = QLabel("Vai trò")
        lbl_role.setStyleSheet(LBL_FIELD)
        self.cmb_role = QComboBox()
        self.cmb_role.addItems(["Khách hàng", "Nhân viên", "Chủ đầu tư"])
        self.cmb_role.setStyleSheet(COMBO_STYLE)
        self.cmb_role.setMinimumHeight(42)
        layout.addWidget(lbl_role)
        layout.addWidget(self.cmb_role)
        layout.addSpacing(10)

        self.txt_name = QLineEdit(); self.txt_name.setPlaceholderText("Nguyễn Văn A"); self.txt_name.setMinimumHeight(42)
        field("Họ và tên", self.txt_name)

        self.txt_email = QLineEdit(); self.txt_email.setPlaceholderText("example@email.com"); self.txt_email.setMinimumHeight(42)
        field("Email", self.txt_email)

        self.txt_sdt = QLineEdit(); self.txt_sdt.setPlaceholderText("0901 234 567"); self.txt_sdt.setMinimumHeight(42)
        field("Số điện thoại", self.txt_sdt)

        self.txt_pw = QLineEdit(); self.txt_pw.setPlaceholderText("Ít nhất 6 ký tự")
        self.txt_pw.setEchoMode(QLineEdit.EchoMode.Password); self.txt_pw.setMinimumHeight(42)
        field("Mật khẩu", self.txt_pw)

        self.txt_pw2 = QLineEdit(); self.txt_pw2.setPlaceholderText("Nhập lại mật khẩu")
        self.txt_pw2.setEchoMode(QLineEdit.EchoMode.Password); self.txt_pw2.setMinimumHeight(42)
        field("Xác nhận mật khẩu", self.txt_pw2)

        # OTP row
        lbl_otp = QLabel("Mã OTP")
        lbl_otp.setStyleSheet(LBL_FIELD)
        otp_row = QHBoxLayout()
        otp_row.setSpacing(10)
        self.txt_otp = QLineEdit(); self.txt_otp.setPlaceholderText("Nhập mã 6 số")
        self.txt_otp.setMinimumHeight(42); self.txt_otp.setMaxLength(6)
        self.btn_send_otp = QPushButton("📨 Gửi OTP")
        self.btn_send_otp.setMinimumHeight(42); self.btn_send_otp.setFixedWidth(120)
        self.btn_send_otp.setStyleSheet(BTN_SECONDARY)
        self.btn_send_otp.clicked.connect(self.send_otp)
        otp_row.addWidget(self.txt_otp)
        otp_row.addWidget(self.btn_send_otp)
        layout.addWidget(lbl_otp)
        layout.addLayout(otp_row)
        layout.addSpacing(8)

        # Message
        self.lbl_msg = QLabel("")
        self.lbl_msg.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_msg.setWordWrap(True)
        self.lbl_msg.setStyleSheet(f"color: #dc2626; font-size: 12px; background: #fef2f2; border-radius: 6px; padding: 6px;")
        self.lbl_msg.hide()
        layout.addWidget(self.lbl_msg)
        layout.addSpacing(12)

        # Nút đăng ký
        btn_reg = QPushButton("✅  Hoàn tất đăng ký")
        btn_reg.setMinimumHeight(46)
        btn_reg.setStyleSheet(BTN_PRIMARY)
        btn_reg.clicked.connect(self.do_register)
        layout.addWidget(btn_reg)
        layout.addSpacing(8)

        # Quay lại
        btn_back = QPushButton("← Đã có tài khoản? Đăng nhập")
        btn_back.setMinimumHeight(38)
        btn_back.setStyleSheet(BTN_SECONDARY)
        btn_back.clicked.connect(self.go_back)
        layout.addWidget(btn_back)

        outer.addWidget(card)

    # ── OTP ──────────────────────────────────
    def send_otp(self):
        email = self.txt_email.text().strip()
        sdt   = self.txt_sdt.text().strip()
        if not email or "@" not in email:
            return self._show_msg("⚠️ Vui lòng nhập email hợp lệ trước khi gửi OTP.")
        if not sdt:
            return self._show_msg("⚠️ Vui lòng nhập số điện thoại.")
        self._otp_code = str(random.randint(100000, 999999))
        QMessageBox.information(
            self, "OTP (Giả lập)",
            f"Mã OTP đã gửi đến:\n📧 {email}\n\n🔑  Mã của bạn: {self._otp_code}\n\n(Hiệu lực 3 phút)"
        )
        self._otp_timer_secs = 180
        self._timer.start(1000)
        self.btn_send_otp.setEnabled(False)
        self._show_msg(f"✔ OTP đã gửi — còn {self._otp_timer_secs}s", ok=True)

    def _tick_otp(self):
        self._otp_timer_secs -= 1
        if self._otp_timer_secs <= 0:
            self._timer.stop(); self.btn_send_otp.setEnabled(True)
            self._otp_code = None
            self._show_msg("OTP đã hết hạn. Vui lòng gửi lại.")
        else:
            self._show_msg(f"✔ OTP đã gửi — còn {self._otp_timer_secs}s", ok=True)

    # ── Đăng ký ──────────────────────────────
    def do_register(self):
        role_map = {
            "Khách hàng": ("KhachHang", "KH"),
            "Nhân viên":  ("NhanVien",  "NV"),
            "Chủ đầu tư": ("ChuDauTu",  "CDT"),
        }
        vai_tro, prefix = role_map[self.cmb_role.currentText()]
        ho_ten = self.txt_name.text().strip()
        email  = self.txt_email.text().strip()
        sdt    = self.txt_sdt.text().strip()
        pw     = self.txt_pw.text()
        pw2    = self.txt_pw2.text()
        otp_in = self.txt_otp.text().strip()

        if not ho_ten:          return self._show_msg("⚠️ Vui lòng nhập họ tên.")
        if not email or "@" not in email: return self._show_msg("⚠️ Email không hợp lệ.")
        if not sdt or not sdt.isdigit() or len(sdt) < 9:
            return self._show_msg("⚠️ Số điện thoại không hợp lệ.")
        if len(pw) < 6:         return self._show_msg("⚠️ Mật khẩu ít nhất 6 ký tự.")
        if pw != pw2:           return self._show_msg("⚠️ Xác nhận mật khẩu không khớp.")
        if not self._otp_code:  return self._show_msg("⚠️ Vui lòng gửi và nhập mã OTP.")
        if otp_in != self._otp_code: return self._show_msg("❌ Mã OTP không đúng.")

        conn = get_conn(); cur = conn.cursor()
        cur.execute("SELECT 1 FROM NGUOI_DUNG WHERE Email=?", (email,))
        if cur.fetchone(): conn.close(); return self._show_msg("❌ Email đã được sử dụng.")
        cur.execute("SELECT 1 FROM NGUOI_DUNG WHERE Sdt=?", (sdt,))
        if cur.fetchone(): conn.close(); return self._show_msg("❌ Số điện thoại đã được sử dụng.")

        cur.execute("SELECT COUNT(*) FROM NGUOI_DUNG WHERE VaiTro=?", (vai_tro,))
        count = cur.fetchone()[0]
        ma = f"{prefix}{count + 1:04d}"
        cur.execute(
            "INSERT INTO NGUOI_DUNG (MaNguoiDung, HoTen, Sdt, Email, VaiTro, MatKhau) VALUES (?,?,?,?,?,?)",
            (ma, ho_ten, sdt, email, vai_tro, hash_pw(pw))
        )
        conn.commit(); conn.close()
        self._timer.stop()
        QMessageBox.information(
            self, "Đăng ký thành công 🎉",
            f"Chào mừng {ho_ten}!\n\nVai trò: {self.cmb_role.currentText()}\nMã tài khoản: {ma}\n\nVui lòng đăng nhập."
        )
        self.go_back()

    def _show_msg(self, text, ok=False):
        if ok:
            self.lbl_msg.setStyleSheet(f"color: {G1}; font-size: 12px; background: {G_M}; border-radius: 6px; padding: 6px;")
        else:
            self.lbl_msg.setStyleSheet("color: #dc2626; font-size: 12px; background: #fef2f2; border-radius: 6px; padding: 6px;")
        self.lbl_msg.setText(text)
        self.lbl_msg.show()

    def go_back(self):
        self.back_callback()
        self.close()


# ══════════════════════════════════════════════
#  Cửa sổ ĐĂNG NHẬP
# ══════════════════════════════════════════════
class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("EV Charge & Green — Đăng nhập")
        self.setMinimumSize(500, 580)
        self.setStyleSheet(APP_STYLE + INPUT_STYLE + CARD_STYLE)
        self.setup_ui()

    def setup_ui(self):
        outer = QVBoxLayout(self)
        outer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        outer.setContentsMargins(20, 20, 20, 20)

        card = QWidget(objectName="auth_card")
        card.setFixedWidth(440)
        shadow(card, blur=30, color=G1, alpha=25, dy=8)

        layout = QVBoxLayout(card)
        layout.setSpacing(0)
        layout.setContentsMargins(44, 40, 44, 40)

        # ── Header banner ────────────────────
        banner = QWidget()
        banner.setStyleSheet(f"""
            background: qlineargradient(x1:0,y1:0,x2:1,y2:1,
                stop:0 {G1}, stop:1 {G2});
            border-radius: 14px;
        """)
        b_lay = QVBoxLayout(banner)
        b_lay.setContentsMargins(16, 18, 16, 18)
        b_lay.setSpacing(6)

        logo = QLabel("⚡ EV Charge & Green")
        logo.setFont(QFont("Segoe UI", 21, QFont.Weight.Bold))
        logo.setStyleSheet("color: #ffffff; background: transparent;")
        logo.setAlignment(Qt.AlignmentFlag.AlignCenter)

        sub = QLabel("Hệ thống đặt lịch sạc & thu gom pin đổi điểm xanh")
        sub.setStyleSheet("color: #bbf7d0; font-size: 12px; background: transparent;")
        sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sub.setWordWrap(True)

        b_lay.addWidget(logo)
        b_lay.addWidget(sub)
        layout.addWidget(banner)
        layout.addSpacing(28)

        # ── Vai trò ──────────────────────────
        lbl_role = QLabel("Vai trò")
        lbl_role.setStyleSheet(LBL_FIELD)
        self.cmb_role = QComboBox()
        self.cmb_role.addItems(["Khách hàng", "Nhân viên", "Chủ đầu tư"])
        self.cmb_role.setStyleSheet(COMBO_STYLE)
        self.cmb_role.setMinimumHeight(42)
        self.cmb_role.currentIndexChanged.connect(self._on_role_changed)
        layout.addWidget(lbl_role)
        layout.addWidget(self.cmb_role)
        layout.addSpacing(14)

        # ── Email ────────────────────────────
        lbl_email = QLabel("Email")
        lbl_email.setStyleSheet(LBL_FIELD)
        self.txt_email = QLineEdit()
        self.txt_email.setPlaceholderText("example@email.com")
        self.txt_email.setMinimumHeight(42)
        layout.addWidget(lbl_email)
        layout.addWidget(self.txt_email)
        layout.addSpacing(14)

        # ── Mật khẩu ─────────────────────────
        lbl_pw = QLabel("Mật khẩu")
        lbl_pw.setStyleSheet(LBL_FIELD)
        self.txt_pw = QLineEdit()
        self.txt_pw.setPlaceholderText("Nhập mật khẩu")
        self.txt_pw.setEchoMode(QLineEdit.EchoMode.Password)
        self.txt_pw.setMinimumHeight(42)
        self.txt_pw.returnPressed.connect(self.login)
        layout.addWidget(lbl_pw)
        layout.addWidget(self.txt_pw)
        layout.addSpacing(6)

        # ── Message ──────────────────────────
        self.lbl_msg = QLabel("")
        self.lbl_msg.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_msg.setWordWrap(True)
        self.lbl_msg.setStyleSheet("color: #dc2626; font-size: 12px; background: #fef2f2; border-radius: 6px; padding: 6px;")
        self.lbl_msg.hide()
        layout.addWidget(self.lbl_msg)
        layout.addSpacing(18)

        # ── Nút đăng nhập ────────────────────
        btn_login = QPushButton("🔐  Đăng nhập")
        btn_login.setMinimumHeight(46)
        btn_login.setStyleSheet(BTN_PRIMARY)
        btn_login.clicked.connect(self.login)
        layout.addWidget(btn_login)
        layout.addSpacing(10)

        # ── Đường kẻ ─────────────────────────
        div = QFrame()
        div.setFrameShape(QFrame.Shape.HLine)
        div.setStyleSheet(f"color: {G_B}; margin: 4px 0;")
        layout.addWidget(div)
        layout.addSpacing(6)

        # ── Nút đăng ký ──────────────────────
        self.btn_register = QPushButton("Chưa có tài khoản? Đăng ký ngay →")
        self.btn_register.setMinimumHeight(40)
        self.btn_register.setStyleSheet(BTN_SECONDARY)
        self.btn_register.clicked.connect(self.open_register)
        layout.addWidget(self.btn_register)

        outer.addWidget(card)
        self._on_role_changed()

    def _on_role_changed(self):
        is_kh = (self.cmb_role.currentText() == "Khách hàng")
        self.btn_register.setVisible(is_kh)
        self.lbl_msg.hide()
        self.lbl_msg.setText("")

    def login(self):
        self.lbl_msg.hide()
        role_map = {"Khách hàng": "KhachHang", "Nhân viên": "NhanVien", "Chủ đầu tư": "ChuDauTu"}
        vai_tro = role_map[self.cmb_role.currentText()]
        email = self.txt_email.text().strip()
        pw    = self.txt_pw.text()

        if not email or not pw:
            return self._show_msg("⚠️ Vui lòng nhập email và mật khẩu.")

        conn = get_conn(); cur = conn.cursor()
        cur.execute(
            "SELECT MaNguoiDung, HoTen, Sdt, Email, MatKhau FROM NGUOI_DUNG WHERE Email=? AND VaiTro=?",
            (email, vai_tro)
        )
        nd = cur.fetchone(); conn.close()

        if nd is None:
            return self._show_msg("❌ Email không tồn tại hoặc sai vai trò.")
        if nd[4] is not None and nd[4] != hash_pw(pw):
            return self._show_msg("❌ Mật khẩu không đúng.")

        user_info = {"MaNguoiDung": nd[0], "HoTen": nd[1], "Sdt": nd[2], "Email": nd[3], "VaiTro": vai_tro}
        self.main_win = MainWindow(user_info)
        self.main_win.show()
        self.hide()

    def open_register(self):
        self.reg_win = RegisterWindow(back_callback=self.show)
        self.reg_win.show()
        self.hide()

    def _show_msg(self, text):
        self.lbl_msg.setText(text)
        self.lbl_msg.show()


# ══════════════════════════════════════════════
#  Cửa sổ CHÍNH
# ══════════════════════════════════════════════
class MainWindow(QMainWindow):
    def __init__(self, user_info):
        super().__init__()
        self.user = user_info
        role_label = {"KhachHang": "Khách hàng", "NhanVien": "Nhân viên", "ChuDauTu": "Chủ đầu tư"}
        self.setWindowTitle(
            f"EV Charge & Green  |  {user_info['HoTen']}  [{role_label[user_info['VaiTro']]}]"
        )
        self.setMinimumSize(1150, 720)
        self.setStyleSheet(APP_STYLE)
        self.setup_ui()

    def setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # ── Top header ───────────────────────
        header = QFrame()
        header.setFixedHeight(66)
        header.setObjectName("header_frame")
        header.setStyleSheet(f"""
            QFrame#header_frame {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #064e3b, stop:0.4 #059669, stop:1 #10b981);
                border-bottom: 2px solid #047857;
            }}
            QFrame#header_frame QLabel {{
                background: transparent;
                font-family: 'Segoe UI', 'Inter', 'Helvetica Neue', sans-serif;
            }}
        """)
        h_layout = QHBoxLayout(header)
        h_layout.setContentsMargins(24, 0, 24, 0)
        h_layout.setSpacing(12)

        app_name = QLabel("⚡ EV Charge & Green")
        app_name.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        app_name.setStyleSheet("color: #ffffff;")

        role_colors = {"KhachHang": "#fbbf24", "NhanVien": "#60a5fa", "ChuDauTu": "#c084fc"}
        role_names  = {"KhachHang": "👤 Khách hàng", "NhanVien": "🔧 Nhân viên", "ChuDauTu": "🏢 Chủ đầu tư"}
        role  = self.user["VaiTro"]
        color = role_colors[role]

        badge = QLabel(f"  {role_names[role]}  ")
        badge.setStyleSheet(f"""
            background-color: rgba(255, 255, 255, 0.12);
            color: #ffffff;
            border: 1.5px solid rgba(255, 255, 255, 0.25);
            border-radius: 8px;
            padding: 6px 16px;
            font-weight: 700;
            font-size: 12px;
        """)

        name_lbl = QLabel(f"  👋  {self.user['HoTen']}")
        name_lbl.setStyleSheet("color: #ffffff; font-size: 13px; font-weight: 600; background: transparent;")

        btn_logout = QPushButton("⬅ Đăng xuất")
        btn_logout.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 255, 255, 0.12);
                color: #ffffff;
                border: 1.5px solid rgba(255, 255, 255, 0.25);
                border-radius: 8px;
                padding: 6px 16px;
                font-weight: 700;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.25);
                border-color: rgba(255, 255, 255, 0.45);
            }
            QPushButton:pressed {
                background-color: rgba(255, 255, 255, 0.35);
            }
        """)
        btn_logout.clicked.connect(self.logout)

        h_layout.addWidget(app_name, alignment=Qt.AlignmentFlag.AlignCenter)
        h_layout.addStretch()
        h_layout.addWidget(badge, alignment=Qt.AlignmentFlag.AlignCenter)
        h_layout.addWidget(name_lbl, alignment=Qt.AlignmentFlag.AlignCenter)
        h_layout.addSpacing(8)
        h_layout.addWidget(btn_logout, alignment=Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(header)

        # ── Tab content ──────────────────────
        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)

        if role == "KhachHang":
            self.tabs.addTab(QuanLyXeWidget(self.user),   "🚗  Xe Của Tôi")
            self.tabs.addTab(TramSacWidget(self.user),    "🔌  Trạm Sạc")
            self.tabs.addTab(LichDatChoWidget(self.user), "📅  Đặt Lịch")
            self.tabs.addTab(PhienSacWidget(self.user),   "⚡  Phiên Sạc")
            self.tabs.addTab(ThanhToanWidget(self.user),  "💳  Hóa Đơn")
            self.tabs.addTab(ThuGomPinWidget(self.user),  "♻️  Thu Gom Pin")
        elif role == "NhanVien":
            # Khách hàng tự thao tác Đặt Lịch & Phiên Sạc theo lịch của họ,
            # nên Nhân viên chỉ còn quản lý Trạm/Cổng, Bảo trì và Thu gom pin.
            self.tabs.addTab(TramSacWidget(self.user),    "🔌  Trạm & Cổng")
            self.tabs.addTab(BaoTriWidget(self.user),     "🔧  Bảo Trì")
            self.tabs.addTab(ThuGomPinWidget(self.user),  "♻️  Thu Gom Pin")
        elif role == "ChuDauTu":
            self.tabs.addTab(TramSacWidget(self.user),   "🏗️  Quản lý Trạm")
            self.tabs.addTab(ThanhToanWidget(self.user),  "💰  Doanh Thu")

        self.tabs.currentChanged.connect(self.on_tab_changed)

        content = QWidget()
        c_layout = QVBoxLayout(content)
        c_layout.setContentsMargins(18, 14, 18, 14)
        c_layout.addWidget(self.tabs)
        main_layout.addWidget(content)

        # ── Status bar ───────────────────────
        status = QStatusBar()
        status.setStyleSheet(f"""
            QStatusBar {{
                background: #ffffff;
                color: #4b5563;
                border-top: 1px solid #e2e8f0;
                font-size: 11px;
                padding: 4px 10px;
            }}
        """)
        status.showMessage(
            f"✅  Đăng nhập: {self.user['HoTen']}   |   📧 {self.user['Email']}   |   📞 {self.user['Sdt']}"
        )
        self.setStatusBar(status)

    def logout(self):
        self.login_win = LoginWindow()
        self.login_win.show()
        self.close()

    def on_tab_changed(self, index):
        widget = self.tabs.widget(index)
        if widget and hasattr(widget, "load_data"):
            widget.load_data()


# ══════════════════════════════════════════════
if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    # Áp palette sáng toàn cục
    pal = QPalette()
    pal.setColor(QPalette.ColorRole.Window,      QColor(G_L))
    pal.setColor(QPalette.ColorRole.WindowText,  QColor("#1a2e1a"))
    pal.setColor(QPalette.ColorRole.Base,        QColor("#ffffff"))
    pal.setColor(QPalette.ColorRole.AlternateBase, QColor(G_L))
    pal.setColor(QPalette.ColorRole.Button,      QColor(G1))
    pal.setColor(QPalette.ColorRole.ButtonText,  QColor("#ffffff"))
    pal.setColor(QPalette.ColorRole.Highlight,   QColor(G2))
    pal.setColor(QPalette.ColorRole.HighlightedText, QColor("#ffffff"))
    app.setPalette(pal)

    win = LoginWindow()
    win.show()
    sys.exit(app.exec())