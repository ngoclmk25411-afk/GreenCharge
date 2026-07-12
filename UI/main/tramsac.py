import sqlite3
from datetime import datetime
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTableWidget,
    QTableWidgetItem, QPushButton, QComboBox, QHeaderView,
    QMessageBox, QGroupBox, QLineEdit, QSplitter, QFormLayout, QDialog,
    QDialogButtonBox, QSizePolicy
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


# ─── Dialog thêm / sửa trạm ─────────────────────────────────────────────────
class TramDialog(QDialog):
    def __init__(self, parent=None, tram_data=None):
        super().__init__(parent)
        self.tram_data = tram_data  # None = thêm mới, dict = chỉnh sửa
        self.setWindowTitle("Thêm trạm sạc mới" if not tram_data else "Chỉnh sửa trạm sạc")
        self.setMinimumWidth(420)
        self.setStyleSheet(DIALOG_STYLE)
        self.setup_ui()

    def setup_ui(self):
        layout = QFormLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(20, 20, 20, 20)

        self.txt_ma = QLineEdit()
        self.txt_ten = QLineEdit()
        self.txt_dia_chi = QLineEdit()
        self.cmb_trang_thai = QComboBox()
        self.cmb_trang_thai.addItems(["Hoạt động", "Tạm ngừng"])

        if self.tram_data:
            self.txt_ma.setText(self.tram_data[0])
            self.txt_ma.setEnabled(False)
            self.txt_ten.setText(self.tram_data[1])
            self.txt_dia_chi.setText(self.tram_data[2])
            idx = 0 if self.tram_data[3] == "Hoạt động" else 1
            self.cmb_trang_thai.setCurrentIndex(idx)

        layout.addRow("Mã trạm:", self.txt_ma)
        layout.addRow("Tên trạm:", self.txt_ten)
        layout.addRow("Địa chỉ:", self.txt_dia_chi)
        layout.addRow("Trạng thái:", self.cmb_trang_thai)

        btns = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        btns.accepted.connect(self.accept)
        btns.rejected.connect(self.reject)
        layout.addRow(btns)

    def get_data(self):
        return {
            "ma": self.txt_ma.text().strip(),
            "ten": self.txt_ten.text().strip(),
            "dia_chi": self.txt_dia_chi.text().strip(),
            "trang_thai": self.cmb_trang_thai.currentText()
        }


# ─── Widget chính ────────────────────────────────────────────────────────────
class TramSacWidget(QWidget):
    def __init__(self, user_info, parent=None):
        super().__init__(parent)
        self.user = user_info
        self.setup_ui()
        self.load_data()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(16, 16, 16, 16)

        role = self.user["VaiTro"]

        title_text = "🔌 Quản lý Trạm & Cổng Sạc" if role in ("ChuDauTu", "NhanVien") else "🔌 Trạm Sạc & Cổng Sạc"
        title = QLabel(title_text)
        title.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        title.setStyleSheet(TITLE_STYLE)
        title.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        layout.addWidget(title)

        if role == "KhachHang":
            hint = QLabel(
                "Xem trạng thái các trạm và cổng sạc hiện có. Chọn một trạm bên trái để xem cổng sạc tương ứng.")
            hint.setWordWrap(True)
            hint.setStyleSheet("color: #6b7280; font-size: 12px;")
            hint.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
            layout.addWidget(hint)

        # ── Hàng chứa 2 khối trái/phải, tỷ lệ cố định 45/55 ──────────────
        row = QHBoxLayout()
        row.setSpacing(14)

        # ── Bên trái: Danh sách trạm ──
        left = QGroupBox("Danh sách Trạm Sạc")
        left.setStyleSheet(self._group_style())
        left.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        left_layout = QVBoxLayout(left)
        left_layout.setContentsMargins(14, 20, 14, 14)
        left_layout.setSpacing(10)

        self.tbl_tram = QTableWidget()
        self.tbl_tram.setColumnCount(4)
        self.tbl_tram.setHorizontalHeaderLabels(["Mã Trạm", "Tên Trạm", "Địa Chỉ", "Trạng Thái"])
        self.tbl_tram.horizontalHeader().setDefaultAlignment(Qt.AlignmentFlag.AlignCenter)
        self.tbl_tram.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.tbl_tram.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.tbl_tram.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.tbl_tram.setStyleSheet(self._table_style())
        self.tbl_tram.setAlternatingRowColors(True)
        self.tbl_tram.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.tbl_tram.selectionModel().selectionChanged.connect(self.on_tram_selected)
        left_layout.addWidget(self.tbl_tram, 1)

        if role == "ChuDauTu":
            # Chủ đầu tư: thêm mới / chỉnh sửa trạm
            btn_row = QHBoxLayout()
            btn_row.setSpacing(10)
            btn_them = QPushButton("➕ Thêm Trạm Mới")
            btn_them.setMinimumHeight(38)
            btn_them.setStyleSheet(self._btn_style("#10b981"))
            btn_them.clicked.connect(self.them_tram)
            btn_sua = QPushButton("✏️ Chỉnh Sửa")
            btn_sua.setMinimumHeight(38)
            btn_sua.setStyleSheet(self._btn_style("#0ea5e9"))
            btn_sua.clicked.connect(self.sua_tram)
            btn_row.addWidget(btn_them)
            btn_row.addWidget(btn_sua)
            left_layout.addLayout(btn_row)

        elif role == "NhanVien":
            grp_tram = QGroupBox("Cập nhật trạng thái Trạm")
            grp_tram.setStyleSheet(self._group_style())
            lay_tram = QHBoxLayout(grp_tram)
            lay_tram.setSpacing(10)
            self.cmb_tt_tram = QComboBox()
            self.cmb_tt_tram.addItems(["Hoạt động", "Tạm ngừng", "Bảo trì"])
            self.cmb_tt_tram.setStyleSheet(self._combo_style())
            btn_tt = QPushButton("Cập nhật")
            btn_tt.setMinimumHeight(38)
            btn_tt.setStyleSheet(self._btn_style("#f59e0b"))
            btn_tt.clicked.connect(self.update_tram_status)
            lay_tram.addWidget(self.cmb_tt_tram, 1)
            lay_tram.addWidget(btn_tt)
            left_layout.addWidget(grp_tram)

        row.addWidget(left, 45)

        # ── Bên phải: Danh sách cổng sạc ──
        right = QGroupBox("Danh sách Cổng Sạc (click vào trạm để xem)")
        right.setStyleSheet(self._group_style())
        right.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        right_layout = QVBoxLayout(right)
        right_layout.setContentsMargins(14, 20, 14, 14)
        right_layout.setSpacing(10)

        self.tbl_cong = QTableWidget()
        self.tbl_cong.setColumnCount(5)
        self.tbl_cong.setHorizontalHeaderLabels(["Mã Cổng", "Chuẩn Sạc", "Công Suất (kW)", "Loại", "Trạng Thái"])
        self.tbl_cong.horizontalHeader().setDefaultAlignment(Qt.AlignmentFlag.AlignCenter)
        self.tbl_cong.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.tbl_cong.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.tbl_cong.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.tbl_cong.setStyleSheet(self._table_style())
        self.tbl_cong.setAlternatingRowColors(True)
        self.tbl_cong.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        right_layout.addWidget(self.tbl_cong, 1)

        if role == "NhanVien":
            grp_cong = QGroupBox("Cập nhật Cổng (Chọn cổng ở trên)")
            grp_cong.setStyleSheet(self._group_style())
            lay_cong = QHBoxLayout(grp_cong)
            lay_cong.setSpacing(10)
            self.cmb_tt_cong = QComboBox()
            self.cmb_tt_cong.addItems(["Trống", "Đang sạc", "Bảo trì", "Đang hỏng"])
            self.cmb_tt_cong.setStyleSheet(self._combo_style())
            btn_cong = QPushButton("Cập nhật")
            btn_cong.setMinimumHeight(38)
            btn_cong.setStyleSheet(self._btn_style("#10b981"))
            btn_cong.clicked.connect(self.update_cong_status)
            lay_cong.addWidget(self.cmb_tt_cong, 1)
            lay_cong.addWidget(btn_cong)
            right_layout.addWidget(grp_cong)

        if role in ["NhanVien", "ChuDauTu"]:
            btn_them_cong = QPushButton("➕ Thêm Cổng Sạc Mới")
            btn_them_cong.setMinimumHeight(38)
            btn_them_cong.setStyleSheet(self._btn_style("#0ea5e9"))
            btn_them_cong.clicked.connect(self.them_cong)
            right_layout.addWidget(btn_them_cong)

        row.addWidget(right, 55)

        layout.addLayout(row, 1)

    # ── Load dữ liệu ──────────────────────────────────────────────────────────
    def them_cong(self):
        row = self.tbl_tram.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Chưa chọn", "Vui lòng chọn một trạm để thêm cổng.")
            return
        ma_tram = self.tbl_tram.item(row, 0).text()

        from PyQt6.QtWidgets import QInputDialog
        chuan, ok1 = QInputDialog.getItem(self, "Thêm cổng", "Chuẩn sạc:", ["CCS2", "CHAdeMO", "Type 2", "GB/T"], 0,
                                          False)
        if not ok1: return

        cong_suat, ok2 = QInputDialog.getDouble(self, "Thêm cổng", "Công suất (kW):", 22.0, 3.0, 350.0, 1)
        if not ok2: return

        loai = "DC" if cong_suat >= 50 else "AC"

        conn = get_conn()
        cur = conn.cursor()

        cur.execute("SELECT MaChuanSac FROM CHUAN_SAC WHERE TenChuan=?", (chuan,))
        mc = cur.fetchone()
        ma_chuan = mc[0] if mc else "CH001"

        cur.execute("SELECT COUNT(*) FROM CONG_SAC")
        n = cur.fetchone()[0]
        ma_cong = f"CS{n + 1:03d}"

        cur.execute(
            "INSERT INTO CONG_SAC (MaCong, MaTram, MaChuanSac, CongSuat, LoaiCaySac, TrangThaiCong) VALUES (?,?,?,?,?,?)",
            (ma_cong, ma_tram, ma_chuan, cong_suat, loai, 'Trống'))
        conn.commit()
        conn.close()
        QMessageBox.information(self, "Thành công", f"Đã thêm cổng {ma_cong} cho trạm {ma_tram}.")
        self.load_cong(ma_tram)

    def load_data(self):
        conn = get_conn()
        cur = conn.cursor()
        role = self.user["VaiTro"]
        ma = self.user["MaNguoiDung"]

        if role == "ChuDauTu":
            cur.execute("SELECT MaTram, TenTram, DiaChi, TrangThaiHoatDong FROM TRAM_SAC WHERE MaNguoiDung=?", (ma,))
        elif role == "NhanVien":
            # Chỉ hiện trạm mà nhân viên phụ trách
            cur.execute("""
                        SELECT ts.MaTram, ts.TenTram, ts.DiaChi, ts.TrangThaiHoatDong
                        FROM TRAM_SAC ts
                                 JOIN NHAN_VIEN nv ON ts.MaTram = nv.MaTram
                        WHERE nv.MaNguoiDung = ?
                        """, (ma,))
        else:
            cur.execute("SELECT MaTram, TenTram, DiaChi, TrangThaiHoatDong FROM TRAM_SAC")

        rows = cur.fetchall()
        conn.close()

        self.tbl_tram.setRowCount(len(rows))
        for i, row in enumerate(rows):
            for j, val in enumerate(row):
                item = QTableWidgetItem(str(val))
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                if j == 3:
                    item.setForeground(QColor("#10b981") if val == "Hoạt động" else QColor("#f59e0b"))
                self.tbl_tram.setItem(i, j, item)

    def on_tram_selected(self):
        row = self.tbl_tram.currentRow()
        if row < 0:
            return
        ma_tram = self.tbl_tram.item(row, 0).text()
        self.load_cong(ma_tram)

    def load_cong(self, ma_tram):
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("""
                    SELECT cs.MaCong, ch.TenChuan, cs.CongSuat, cs.LoaiCaySac, cs.TrangThaiCong
                    FROM CONG_SAC cs
                             JOIN CHUAN_SAC ch ON cs.MaChuanSac = ch.MaChuanSac
                    WHERE cs.MaTram = ?
                    """, (ma_tram,))
        rows = cur.fetchall()
        conn.close()

        color_map = {"Trống": "#10b981", "Đang sạc": "#3b82f6", "Bảo trì": "#f59e0b", "Đang hỏng": "#ef4444"}
        self.tbl_cong.setRowCount(len(rows))
        for i, row in enumerate(rows):
            for j, val in enumerate(row):
                item = QTableWidgetItem(str(val))
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                if j == 4:
                    item.setForeground(QColor(color_map.get(val, "#374151")))
                self.tbl_cong.setItem(i, j, item)

    # ── Chủ đầu tư: thêm / sửa trạm ─────────────────────────────────────────
    def them_tram(self):
        dlg = TramDialog(self)
        if dlg.exec() != QDialog.DialogCode.Accepted:
            return
        d = dlg.get_data()
        if not d["ma"] or not d["ten"] or not d["dia_chi"]:
            QMessageBox.warning(self, "Thiếu thông tin", "Vui lòng nhập đầy đủ Mã, Tên và Địa chỉ trạm.")
            return
        conn = get_conn()
        cur = conn.cursor()
        try:
            cur.execute("""
                        INSERT INTO TRAM_SAC (MaTram, TenTram, DiaChi, MaNguoiDung, TrangThaiHoatDong)
                        VALUES (?, ?, ?, ?, ?)
                        """, (d["ma"], d["ten"], d["dia_chi"], self.user["MaNguoiDung"], d["trang_thai"]))
            conn.commit()
            QMessageBox.information(self, "Thành công", f"Đã thêm trạm {d['ma']} — {d['ten']}")
            self.load_data()
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", str(e))
        finally:
            conn.close()

    def sua_tram(self):
        row = self.tbl_tram.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Chưa chọn", "Vui lòng chọn một trạm để chỉnh sửa.")
            return
        data = [self.tbl_tram.item(row, j).text() for j in range(4)]
        dlg = TramDialog(self, tram_data=data)
        if dlg.exec() != QDialog.DialogCode.Accepted:
            return
        d = dlg.get_data()
        conn = get_conn()
        cur = conn.cursor()
        try:
            cur.execute("""
                        UPDATE TRAM_SAC
                        SET TenTram=?,
                            DiaChi=?,
                            TrangThaiHoatDong=?
                        WHERE MaTram = ?
                        """, (d["ten"], d["dia_chi"], d["trang_thai"], data[0]))
            conn.commit()
            QMessageBox.information(self, "Đã cập nhật", f"Trạm {data[0]} đã được cập nhật.")
            self.load_data()
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", str(e))
        finally:
            conn.close()

    # ── Nhân viên: cập nhật trạng thái ───────────────────────────────────────
    def update_tram_status(self):
        row = self.tbl_tram.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Chưa chọn", "Vui lòng chọn một trạm.")
            return
        ma_tram = self.tbl_tram.item(row, 0).text()
        new_st = self.cmb_tt_tram.currentText()
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("UPDATE TRAM_SAC SET TrangThaiHoatDong=? WHERE MaTram=?", (new_st, ma_tram))
        conn.commit()
        conn.close()
        QMessageBox.information(self, "Cập nhật", f"Trạm {ma_tram} → {new_st}")
        self.load_data()

    def update_cong_status(self):
        row = self.tbl_cong.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Chưa chọn", "Vui lòng chọn một cổng sạc.")
            return
        ma_cong = self.tbl_cong.item(row, 0).text()
        new_st = self.cmb_tt_cong.currentText()
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("UPDATE CONG_SAC SET TrangThaiCong=? WHERE MaCong=?", (new_st, ma_cong))
        conn.commit()
        conn.close()
        QMessageBox.information(self, "Cập nhật", f"Cổng {ma_cong} → {new_st}")
        tram_row = self.tbl_tram.currentRow()
        if tram_row >= 0:
            self.load_cong(self.tbl_tram.item(tram_row, 0).text())

    # ── Style helpers ─────────────────────────────────────────────────────────
    def _group_style(self):
        return GROUP_STYLE

    def _table_style(self):
        return TABLE_STYLE

    def _combo_style(self):
        return COMBO_STYLE

    def _btn_style(self, color=None):
        return btn_style(color)