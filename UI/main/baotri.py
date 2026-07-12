import sqlite3
from datetime import datetime
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTableWidget,
    QTableWidgetItem, QPushButton, QComboBox, QHeaderView,
    QMessageBox, QGroupBox, QLineEdit, QSplitter, QFormLayout,
    QPlainTextEdit, QSizePolicy
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


class BaoTriWidget(QWidget):
    def __init__(self, user_info, parent=None):
        super().__init__(parent)
        self.user = user_info
        self.setup_ui()
        self.load_data()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(16, 16, 16, 16)

        title = QLabel("🔧 Lịch Sử Bảo Trì Cổng Sạc")
        title.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        title.setStyleSheet(TITLE_STYLE)
        layout.addWidget(title)

        splitter = QSplitter(Qt.Orientation.Vertical)

        # ── Form ghi nhận bảo trì mới ──────────────────────────────────────
        form_box = QGroupBox("Ghi nhận bảo trì mới")
        form_box.setStyleSheet(self._group_style())
        form_box.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        form_layout = QFormLayout(form_box)
        form_layout.setVerticalSpacing(18)
        form_layout.setHorizontalSpacing(12)
        form_layout.setContentsMargins(16, 20, 16, 16)

        self.cmb_cong = QComboBox()
        self.cmb_cong.setStyleSheet(self._combo_style())

        self.txt_noi_dung = QPlainTextEdit()
        self.txt_noi_dung.setPlaceholderText("Mô tả nội dung bảo trì...")
        self.txt_noi_dung.setFixedHeight(70)
        self.txt_noi_dung.setStyleSheet(self._input_style())

        self.txt_ket_qua = QLineEdit()
        self.txt_ket_qua.setPlaceholderText("Ví dụ: Đã sửa chữa, Đang chờ linh kiện, Hoàn thành...")
        self.txt_ket_qua.setStyleSheet(self._input_style())

        form_layout.addRow("Cổng sạc:", self.cmb_cong)
        form_layout.addRow("Nội dung bảo trì:", self.txt_noi_dung)
        form_layout.addRow("Kết quả:", self.txt_ket_qua)

        btn_row = QHBoxLayout()
        btn_ghi = QPushButton("✅ Ghi nhận bảo trì")
        btn_ghi.setMinimumHeight(38)
        btn_ghi.setStyleSheet(self._btn_style("#10b981"))
        btn_ghi.clicked.connect(self.ghi_bao_tri)
        btn_row.addStretch()
        btn_row.addWidget(btn_ghi)
        form_layout.addRow("", btn_row)

        layout.addWidget(form_box)

        # ── Bảng lịch sử bảo trì ───────────────────────────────────────────
        list_box = QGroupBox("Lịch sử bảo trì")
        list_box.setStyleSheet(self._group_style())
        list_box.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        list_layout = QVBoxLayout(list_box)
        list_layout.setContentsMargins(12, 20, 12, 12)
        list_layout.setSpacing(10)

        self.tbl = QTableWidget()
        self.tbl.setColumnCount(6)
        self.tbl.setHorizontalHeaderLabels(
            ["Mã Bảo Trì", "Cổng Sạc", "Trạm", "Ngày Bảo Trì", "Nội Dung", "Kết Quả"]
        )
        self.tbl.horizontalHeader().setDefaultAlignment(Qt.AlignmentFlag.AlignCenter)
        self.tbl.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.tbl.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.tbl.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.tbl.setStyleSheet(self._table_style())
        self.tbl.setAlternatingRowColors(True)
        self.tbl.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        list_layout.addWidget(self.tbl, 1)

        btn_refresh = QPushButton("🔄 Làm mới")
        btn_refresh.setMinimumHeight(38)
        btn_refresh.setStyleSheet(self._btn_style("#475569"))
        btn_refresh.clicked.connect(self.load_data)
        btn_rf_row = QHBoxLayout()
        btn_rf_row.addStretch()
        btn_rf_row.addWidget(btn_refresh)
        list_layout.addLayout(btn_rf_row)

        layout.addWidget(list_box, 1)

        self.load_cong_list()

    def load_cong_list(self):
        ma_nv = self.user["MaNguoiDung"]
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("""
            SELECT cs.MaCong, ch.TenChuan, cs.LoaiCaySac, cs.TrangThaiCong
            FROM CONG_SAC cs
            JOIN CHUAN_SAC ch ON cs.MaChuanSac = ch.MaChuanSac
            JOIN TRAM_SAC ts ON cs.MaTram = ts.MaTram
            JOIN NHAN_VIEN nv ON ts.MaTram = nv.MaTram
            WHERE nv.MaNguoiDung=?
        """, (ma_nv,))
        rows = cur.fetchall()
        conn.close()
        self.cong_data = rows
        self.cmb_cong.clear()
        for r in rows:
            self.cmb_cong.addItem(f"{r[0]} — {r[1]} ({r[2]}) | {r[3]}", r[0])

    def ghi_bao_tri(self):
        if self.cmb_cong.count() == 0:
            QMessageBox.warning(self, "Lỗi", "Không tìm thấy cổng sạc được phân công.")
            return
        ma_cong = self.cmb_cong.currentData()
        noi_dung = self.txt_noi_dung.toPlainText().strip()
        ket_qua = self.txt_ket_qua.text().strip()
        if not noi_dung or not ket_qua:
            QMessageBox.warning(self, "Thiếu thông tin", "Vui lòng nhập Nội dung và Kết quả bảo trì.")
            return

        ma_nv = self.user["MaNguoiDung"]
        ngay = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        conn = get_conn()
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM LICH_SU_BAO_TRI")
        n = cur.fetchone()[0]
        ma_bt = f"BT{n+1:03d}"

        cur.execute("""
            INSERT INTO LICH_SU_BAO_TRI (MaBaoTri, MaCong, MaNguoiDung, NgayBaoTri, NoiDungBaoTri, KetQua)
            VALUES (?,?,?,?,?,?)
        """, (ma_bt, ma_cong, ma_nv, ngay, noi_dung, ket_qua))

        # Tự động cập nhật trạng thái cổng sang Trống sau khi bảo trì
        cur.execute("UPDATE CONG_SAC SET TrangThaiCong='Trống' WHERE MaCong=?", (ma_cong,))
        conn.commit()
        conn.close()

        QMessageBox.information(self, "Đã ghi nhận",
                                f"Phiếu bảo trì {ma_bt} đã được tạo.\nCổng {ma_cong} → Trống.")
        self.txt_noi_dung.clear()
        self.txt_ket_qua.clear()
        self.load_cong_list()
        self.load_data()

    def load_data(self):
        ma_nv = self.user["MaNguoiDung"]
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("""
            SELECT bt.MaBaoTri, bt.MaCong, ts.TenTram, bt.NgayBaoTri,
                   bt.NoiDungBaoTri, bt.KetQua
            FROM LICH_SU_BAO_TRI bt
            JOIN CONG_SAC cs ON bt.MaCong = cs.MaCong
            JOIN TRAM_SAC ts ON cs.MaTram = ts.MaTram
            JOIN NHAN_VIEN nv ON ts.MaTram = nv.MaTram
            WHERE nv.MaNguoiDung=?
            ORDER BY bt.NgayBaoTri DESC
        """, (ma_nv,))
        rows = cur.fetchall()
        conn.close()

        self.tbl.setRowCount(len(rows))
        ket_qua_colors = {
            "Hoàn thành": "#10b981",
            "Đã sửa chữa": "#10b981",
            "Đang chờ linh kiện": "#f59e0b",
        }
        for i, row in enumerate(rows):
            for j, val in enumerate(row):
                item = QTableWidgetItem(str(val) if val else "")
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                if j == 5:
                    clr = ket_qua_colors.get(val, "#94a3b8")
                    item.setForeground(QColor(clr))
                self.tbl.setItem(i, j, item)

    def _group_style(self): return GROUP_STYLE

    def _table_style(self): return TABLE_STYLE

    def _combo_style(self): return COMBO_STYLE

    def _input_style(self): return INPUT_STYLE

    def _btn_style(self, color=None): return btn_style(color)