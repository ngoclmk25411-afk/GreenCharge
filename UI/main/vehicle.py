import sqlite3
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTableWidget,
    QTableWidgetItem, QPushButton, QComboBox, QHeaderView,
    QMessageBox, QGroupBox, QLineEdit, QFormLayout, QSplitter,
    QAbstractItemView, QDialog, QDialogButtonBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QFont
from main.shared_theme import (
    GROUP_STYLE, TABLE_STYLE, COMBO_STYLE, INPUT_STYLE,
    DIALOG_STYLE, TITLE_STYLE, LBL_STYLE, btn_style, status_color, G1, G2, G_M, G_B, G_L
)


DB_PATH = "datasets/data.db"


def get_conn():
    return sqlite3.connect(DB_PATH)


class XeDialog(QDialog):
    """Dialog thêm / sửa xe."""
    def __init__(self, parent=None, title="Thêm xe mới", bien_so="", ma_chuan_sac=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setFixedSize(420, 280)
        self.setStyleSheet(DIALOG_STYLE)

        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(28, 24, 28, 24)

        # Title
        lbl_title = QLabel(f"🚗 {title}")
        lbl_title.setFont(QFont("Segoe UI", 15, QFont.Weight.Bold))
        lbl_title.setStyleSheet(f"color: {G1}; font-weight: 800;")
        lbl_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(lbl_title)

        # Biển số
        lbl_bien = QLabel("Biển số xe")
        self.txt_bien = QLineEdit()
        self.txt_bien.setPlaceholderText("VD: 29A-12345")
        self.txt_bien.setText(bien_so)
        self.txt_bien.setMinimumHeight(40)
        layout.addWidget(lbl_bien)
        layout.addWidget(self.txt_bien)

        # Chuẩn sạc
        lbl_chuan = QLabel("Chuẩn sạc")
        self.cmb_chuan = QComboBox()
        self.cmb_chuan.setMinimumHeight(40)
        self._load_chuan_sac()
        if ma_chuan_sac:
            idx = self.cmb_chuan.findData(ma_chuan_sac)
            if idx >= 0:
                self.cmb_chuan.setCurrentIndex(idx)
        layout.addWidget(lbl_chuan)
        layout.addWidget(self.cmb_chuan)

        # Buttons
        btn_layout = QHBoxLayout()
        btn_save = QPushButton("✅ Lưu")
        btn_save.setMinimumHeight(40)
        btn_save.setStyleSheet(f"""
            QPushButton {{
                background: qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 {G1}, stop:1 {G2});
                color: #ffffff; border: none; border-radius: 10px;
                font-size: 14px; font-weight: 700; padding: 10px 24px;
            }}
            QPushButton:hover {{ background: {G2}; }}
        """)
        btn_save.clicked.connect(self.accept)

        btn_cancel = QPushButton("Hủy")
        btn_cancel.setMinimumHeight(40)
        btn_cancel.setStyleSheet(f"""
            QPushButton {{
                background: #ffffff; color: {G1};
                border: 1.5px solid {G_B}; border-radius: 10px;
                font-size: 13px; font-weight: 600; padding: 10px 24px;
            }}
            QPushButton:hover {{ background: {G_L}; border-color: {G2}; color: {G2}; }}
        """)
        btn_cancel.clicked.connect(self.reject)

        btn_layout.addWidget(btn_cancel)
        btn_layout.addWidget(btn_save)
        layout.addLayout(btn_layout)

    def _load_chuan_sac(self):
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("SELECT MaChuanSac, TenChuan, LoaiDongDien FROM CHUAN_SAC")
        rows = cur.fetchall()
        conn.close()
        for r in rows:
            self.cmb_chuan.addItem(f"{r[1]} ({r[2]})", r[0])

    def get_data(self):
        return self.txt_bien.text().strip(), self.cmb_chuan.currentData()


class QuanLyXeWidget(QWidget):
    """Widget quản lý xe của khách hàng — CRUD đầy đủ."""
    def __init__(self, user_info, parent=None):
        super().__init__(parent)
        self.user = user_info
        self.setup_ui()
        self.load_data()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(14)
        layout.setContentsMargins(16, 16, 16, 16)

        # ── Title ────────────────────────────
        title = QLabel("🚗 Quản lý Xe của tôi")
        title.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {G1};")
        layout.addWidget(title)

        desc = QLabel("Đăng ký, chỉnh sửa và xóa xe điện của bạn. Chuẩn sạc của xe sẽ được kiểm tra khi đặt lịch sạc.")
        desc.setWordWrap(True)
        desc.setStyleSheet("color: #6b7280; font-size: 12px; margin-bottom: 6px;")
        layout.addWidget(desc)

        # ── Table ────────────────────────────
        box = QGroupBox("Danh sách xe đã đăng ký")
        box.setStyleSheet(GROUP_STYLE)
        box_layout = QVBoxLayout(box)

        self.tbl = QTableWidget()
        self.tbl.setColumnCount(4)
        self.tbl.setHorizontalHeaderLabels(["Mã Xe", "Biển Số", "Chuẩn Sạc", "Loại Dòng Điện"])
        self.tbl.horizontalHeader().setDefaultAlignment(Qt.AlignmentFlag.AlignCenter)
        self.tbl.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.tbl.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.tbl.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.tbl.setStyleSheet(TABLE_STYLE)
        self.tbl.setAlternatingRowColors(True)
        box_layout.addWidget(self.tbl)

        # ── Buttons ──────────────────────────
        btn_row = QHBoxLayout()
        btn_row.setSpacing(10)

        self.btn_add = QPushButton("➕ Đăng ký xe mới")
        self.btn_add.setMinimumHeight(42)
        self.btn_add.setStyleSheet(btn_style(G1))
        self.btn_add.clicked.connect(self.them_xe)
        btn_row.addWidget(self.btn_add)

        self.btn_edit = QPushButton("✏️ Sửa thông tin xe")
        self.btn_edit.setMinimumHeight(42)
        self.btn_edit.setStyleSheet(btn_style("#f59e0b"))
        self.btn_edit.clicked.connect(self.sua_xe)
        btn_row.addWidget(self.btn_edit)

        self.btn_del = QPushButton("🗑️ Xóa xe")
        self.btn_del.setMinimumHeight(42)
        self.btn_del.setStyleSheet(btn_style("#ef4444"))
        self.btn_del.clicked.connect(self.xoa_xe)
        btn_row.addWidget(self.btn_del)

        btn_row.addStretch()

        btn_rf = QPushButton("🔄 Làm mới")
        btn_rf.setMinimumHeight(42)
        btn_rf.setStyleSheet(btn_style("#0ea5e9"))
        btn_rf.clicked.connect(self.load_data)
        btn_row.addWidget(btn_rf)

        box_layout.addLayout(btn_row)
        layout.addWidget(box)
        layout.addStretch()

    def load_data(self):
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("""
            SELECT x.MaXe, x.BienSo, cs.TenChuan, cs.LoaiDongDien
            FROM Xe x
            JOIN CHUAN_SAC cs ON x.MaChuanSac = cs.MaChuanSac
            WHERE x.MaNguoiDung=?
            ORDER BY x.MaXe
        """, (self.user["MaNguoiDung"],))
        rows = cur.fetchall()
        conn.close()

        self.tbl.setRowCount(len(rows))
        color_dc = "#059669"
        color_ac = "#0ea5e9"
        for i, row in enumerate(rows):
            for j, val in enumerate(row):
                item = QTableWidgetItem(str(val))
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                if j == 3:  # Loại dòng điện
                    color = color_dc if val == "DC" else color_ac
                    item.setForeground(QColor(color))
                    item.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
                self.tbl.setItem(i, j, item)

    def them_xe(self):
        dlg = XeDialog(self, title="Đăng ký xe mới")
        if dlg.exec() != QDialog.DialogCode.Accepted:
            return
        bien_so, ma_chuan = dlg.get_data()
        if not bien_so:
            QMessageBox.warning(self, "Thiếu thông tin", "Vui lòng nhập biển số xe.")
            return
        if not ma_chuan:
            QMessageBox.warning(self, "Thiếu thông tin", "Vui lòng chọn chuẩn sạc.")
            return

        conn = get_conn()
        cur = conn.cursor()

        # Kiểm tra biển số trùng
        cur.execute("SELECT 1 FROM Xe WHERE BienSo=?", (bien_so,))
        if cur.fetchone():
            conn.close()
            QMessageBox.warning(self, "Trùng lặp", f"Biển số '{bien_so}' đã tồn tại trong hệ thống.")
            return

        # Tạo mã xe mới
        cur.execute("SELECT COUNT(*) FROM Xe")
        n = cur.fetchone()[0]
        ma_xe = f"XE{n+1:03d}"
        # Đảm bảo mã không trùng
        while True:
            cur.execute("SELECT 1 FROM Xe WHERE MaXe=?", (ma_xe,))
            if not cur.fetchone():
                break
            n += 1
            ma_xe = f"XE{n+1:03d}"

        try:
            cur.execute(
                "INSERT INTO Xe (MaXe, BienSo, MaNguoiDung, MaChuanSac) VALUES (?,?,?,?)",
                (ma_xe, bien_so, self.user["MaNguoiDung"], ma_chuan)
            )
            conn.commit()
            QMessageBox.information(self, "Thành công 🎉", f"Đã đăng ký xe {bien_so} (Mã: {ma_xe}).")
            self.load_data()
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Không thể thêm xe: {e}")
        finally:
            conn.close()

    def sua_xe(self):
        row = self.tbl.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Chưa chọn", "Vui lòng chọn một xe để sửa.")
            return
        ma_xe = self.tbl.item(row, 0).text()
        old_bien = self.tbl.item(row, 1).text()

        # Tìm mã chuẩn sạc hiện tại
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("SELECT MaChuanSac FROM Xe WHERE MaXe=?", (ma_xe,))
        r = cur.fetchone()
        conn.close()
        old_chuan = r[0] if r else None

        dlg = XeDialog(self, title=f"Sửa xe {ma_xe}", bien_so=old_bien, ma_chuan_sac=old_chuan)
        if dlg.exec() != QDialog.DialogCode.Accepted:
            return
        bien_so, ma_chuan = dlg.get_data()
        if not bien_so or not ma_chuan:
            QMessageBox.warning(self, "Thiếu thông tin", "Vui lòng nhập đầy đủ biển số và chuẩn sạc.")
            return

        conn = get_conn()
        cur = conn.cursor()
        # Kiểm tra biển số trùng (trừ xe hiện tại)
        cur.execute("SELECT 1 FROM Xe WHERE BienSo=? AND MaXe!=?", (bien_so, ma_xe))
        if cur.fetchone():
            conn.close()
            QMessageBox.warning(self, "Trùng lặp", f"Biển số '{bien_so}' đã được đăng ký cho xe khác.")
            return

        try:
            cur.execute(
                "UPDATE Xe SET BienSo=?, MaChuanSac=? WHERE MaXe=?",
                (bien_so, ma_chuan, ma_xe)
            )
            conn.commit()
            QMessageBox.information(self, "Thành công", f"Đã cập nhật thông tin xe {ma_xe}.")
            self.load_data()
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Không thể sửa xe: {e}")
        finally:
            conn.close()

    def xoa_xe(self):
        row = self.tbl.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Chưa chọn", "Vui lòng chọn một xe để xóa.")
            return
        ma_xe = self.tbl.item(row, 0).text()
        bien_so = self.tbl.item(row, 1).text()

        # Kiểm tra xe có đang trong phiên sạc không
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("""
            SELECT COUNT(*) FROM LichDatCho l
            WHERE l.MaXe=? AND l.TrangThaiLich IN ('Đã đặt', 'Đang sạc')
        """, (ma_xe,))
        active = cur.fetchone()[0]
        conn.close()
        if active > 0:
            QMessageBox.warning(self, "Không thể xóa",
                                f"Xe {bien_so} đang có {active} lịch đặt/phiên sạc hoạt động.\n"
                                "Hãy hoàn tất hoặc hủy các lịch trước khi xóa.")
            return

        reply = QMessageBox.question(
            self, "Xác nhận xóa",
            f"Bạn có chắc muốn xóa xe:\n\n🚗 {bien_so}  (Mã: {ma_xe})\n\nThao tác này không thể hoàn tác!",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply != QMessageBox.StandardButton.Yes:
            return

        conn = get_conn()
        cur = conn.cursor()
        try:
            cur.execute("DELETE FROM Xe WHERE MaXe=?", (ma_xe,))
            conn.commit()
            QMessageBox.information(self, "Đã xóa", f"Xe {bien_so} đã được xóa khỏi hệ thống.")
            self.load_data()
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Không thể xóa xe: {e}")
        finally:
            conn.close()
