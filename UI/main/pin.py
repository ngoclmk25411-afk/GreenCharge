import sqlite3
from datetime import datetime
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTableWidget,
    QTableWidgetItem, QPushButton, QComboBox, QHeaderView,
    QMessageBox, QGroupBox, QDoubleSpinBox, QSplitter, QFormLayout
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


class ThuGomPinWidget(QWidget):
    def __init__(self, user_info, parent=None):
        super().__init__(parent)
        self.user = user_info
        self.setup_ui()
        self.load_data()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(16, 16, 16, 16)

        title = QLabel("♻️ Thu Gom Pin & Điểm Xanh")
        title.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        title.setStyleSheet("color: #059669;")
        layout.addWidget(title)

        role = self.user["VaiTro"]

        if role == "NhanVien":
            splitter = QSplitter(Qt.Orientation.Vertical)

            # Form tạo phiếu thu gom
            form_box = QGroupBox("Tạo phiếu thu gom pin mới")
            form_box.setStyleSheet(self._group_style())
            form_layout = QFormLayout(form_box)
            form_layout.setSpacing(10)

            self.cmb_kh = QComboBox()
            self.cmb_kh.setStyleSheet(self._combo_style())
            self.cmb_loai_pin = QComboBox()
            self.cmb_loai_pin.setStyleSheet(self._combo_style())
            self.cmb_loai_pin.currentIndexChanged.connect(self.tinh_diem_preview)

            self.spin_kg = QDoubleSpinBox()
            self.spin_kg.setRange(0.1, 999.9)
            self.spin_kg.setValue(1.0)
            self.spin_kg.setSuffix(" kg")
            self.spin_kg.setStyleSheet(self._input_style())
            self.spin_kg.valueChanged.connect(self.tinh_diem_preview)

            self.lbl_preview = QLabel("Điểm thưởng dự kiến: 0 điểm")
            self.lbl_preview.setStyleSheet("color: #6ee7b7; font-weight: bold; font-size: 13px;")

            form_layout.addRow("Khách hàng:", self.cmb_kh)
            form_layout.addRow("Loại pin:", self.cmb_loai_pin)
            form_layout.addRow("Khối lượng:", self.spin_kg)
            form_layout.addRow("", self.lbl_preview)

            btn_tao = QPushButton("✅ Tạo Phiếu Thu Gom")
            btn_tao.setStyleSheet(self._btn_style("#10b981"))
            btn_tao.clicked.connect(self.tao_phieu)
            form_layout.addRow("", btn_tao)

            self.load_kh()
            self.load_loai_pin()
            splitter.addWidget(form_box)

            # Bảng lịch sử
            list_box = QGroupBox("Lịch sử thu gom")
            list_box.setStyleSheet(self._group_style())
            list_layout = QVBoxLayout(list_box)
            cols = ["Mã Phiếu", "Khách Hàng", "Loại Pin", "Khối Lượng", "Điểm Thưởng", "Ngày Thu Gom"]
            self.tbl_pin = self._make_table(cols)
            list_layout.addWidget(self.tbl_pin)
            splitter.addWidget(list_box)
            splitter.setSizes([280, 320])
            layout.addWidget(splitter)

        elif role == "KhachHang":
            # Điểm tích lũy
            self.lbl_diem = QLabel("🌿 Điểm Xanh: 0")
            self.lbl_diem.setStyleSheet("""
                background: qlineargradient(x1:0,y1:0,x2:1,y2:0,stop:0 #064e3b,stop:1 #065f46);
                color: #6ee7b7; font-size: 14px; font-weight: bold;
                border-radius: 8px; padding: 10px 16px;
            """)
            layout.addWidget(self.lbl_diem)

            box = QGroupBox("Lịch sử thu gom pin của tôi")
            box.setStyleSheet(self._group_style())
            box_layout = QVBoxLayout(box)
            cols = ["Mã Phiếu", "Loại Pin", "Khối Lượng (kg)", "Điểm Thưởng", "Ngày Thu Gom"]
            self.tbl_pin = self._make_table(cols)
            box_layout.addWidget(self.tbl_pin)
            layout.addWidget(box)

        else:
            # Investor: thống kê
            self.lbl_tong = QLabel("♻️ Tổng lượng pin đã thu gom: 0 kg")
            self.lbl_tong.setStyleSheet("""
                background: qlineargradient(x1:0,y1:0,x2:1,y2:0,stop:0 #14532d,stop:1 #166534);
                color: #bbf7d0; font-size: 14px; font-weight: bold;
                border-radius: 8px; padding: 10px 16px;
            """)
            layout.addWidget(self.lbl_tong)

            box = QGroupBox("Danh sách phiếu thu gom tại trạm của bạn")
            box.setStyleSheet(self._group_style())
            box_layout = QVBoxLayout(box)
            cols = ["Mã Phiếu", "Khách Hàng", "Nhân Viên", "Loại Pin", "Khối Lượng", "Điểm Thưởng", "Ngày"]
            self.tbl_pin = self._make_table(cols)
            box_layout.addWidget(self.tbl_pin)
            layout.addWidget(box)

    def load_kh(self):
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("""
            SELECT nd.MaNguoiDung, nd.HoTen FROM NGUOI_DUNG nd
            JOIN KHACH_HANG kh ON nd.MaNguoiDung = kh.MaNguoiDung
        """)
        rows = cur.fetchall()
        conn.close()
        self.kh_data = rows
        self.cmb_kh.clear()
        for r in rows:
            self.cmb_kh.addItem(f"{r[1]} ({r[0]})", r[0])

    def load_loai_pin(self):
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("SELECT MaLoaiPin, TenLoaiPin, HeSoQuyDoi FROM LOAI_PIN")
        rows = cur.fetchall()
        conn.close()
        self.loai_pin_data = rows
        self.cmb_loai_pin.clear()
        for r in rows:
            self.cmb_loai_pin.addItem(f"{r[1]} (×{r[2]:.0f} điểm/kg)", r[0])

    def tinh_diem_preview(self):
        idx = self.cmb_loai_pin.currentIndex()
        if idx < 0 or not self.loai_pin_data:
            return
        he_so = float(self.loai_pin_data[idx][2])
        kg = self.spin_kg.value()
        diem = int(kg * he_so)
        self.lbl_preview.setText(f"Điểm thưởng dự kiến: {diem:,} điểm 🌿")

    def tao_phieu(self):
        if self.cmb_kh.count() == 0 or self.cmb_loai_pin.count() == 0:
            QMessageBox.warning(self, "Lỗi", "Không có dữ liệu khách hàng hoặc loại pin.")
            return
        ma_kh = self.cmb_kh.currentData()
        ma_loai_pin = self.cmb_loai_pin.currentData()
        kg = self.spin_kg.value()
        idx = self.cmb_loai_pin.currentIndex()
        he_so = float(self.loai_pin_data[idx][2])
        diem = int(kg * he_so)
        ngay = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ma_nv = self.user["MaNguoiDung"]

        conn = get_conn()
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM PHIEU_THU_GOM")
        n = cur.fetchone()[0]
        ma_phieu = f"PG{n+1:03d}"

        cur.execute("""
            INSERT INTO PHIEU_THU_GOM (MaPhieu, MaNguoiDung_KH, MaNguoiDung_NV, MaLoaiPin, KhoiLuong, DiemThuong, NgayThuGom)
            VALUES (?,?,?,?,?,?,?)
        """, (ma_phieu, ma_kh, ma_nv, ma_loai_pin, kg, diem, ngay))

        cur.execute("UPDATE KHACH_HANG SET DiemXanh=DiemXanh+? WHERE MaNguoiDung=?", (diem, ma_kh))
        conn.commit()
        conn.close()

        kh_name = self.cmb_kh.currentText().split(" (")[0]
        QMessageBox.information(self, "Thành công",
                                f"Đã tạo phiếu {ma_phieu}\n"
                                f"Khách: {kh_name}\n"
                                f"{kg} kg pin → +{diem:,} điểm xanh")
        self.load_data()

    def load_data(self):
        conn = get_conn()
        cur = conn.cursor()
        role = self.user["VaiTro"]
        ma = self.user["MaNguoiDung"]

        if role == "NhanVien":
            cur.execute("""
                SELECT p.MaPhieu, nd.HoTen, lp.TenLoaiPin, p.KhoiLuong, p.DiemThuong, p.NgayThuGom
                FROM PHIEU_THU_GOM p
                JOIN NGUOI_DUNG nd ON p.MaNguoiDung_KH = nd.MaNguoiDung
                JOIN LOAI_PIN lp ON p.MaLoaiPin = lp.MaLoaiPin
                WHERE p.MaNguoiDung_NV=?
                ORDER BY p.NgayThuGom DESC
            """, (ma,))
            rows = cur.fetchall()
            self.tbl_pin.setRowCount(len(rows))
            for i, row in enumerate(rows):
                for j, val in enumerate(row):
                    text = f"{val} kg" if j == 3 else f"{int(val):,} điểm 🌿" if j == 4 else str(val)
                    item = QTableWidgetItem(text)
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    if j == 4:
                        item.setForeground(QColor("#6ee7b7"))
                    self.tbl_pin.setItem(i, j, item)

        elif role == "KhachHang":
            cur.execute("SELECT DiemXanh FROM KHACH_HANG WHERE MaNguoiDung=?", (ma,))
            r = cur.fetchone()
            diem = r[0] if r else 0
            self.lbl_diem.setText(f"🌿 Điểm Xanh tích lũy: {diem:,} điểm  (1 điểm = 1.000 đ giảm)")

            cur.execute("""
                SELECT p.MaPhieu, lp.TenLoaiPin, p.KhoiLuong, p.DiemThuong, p.NgayThuGom
                FROM PHIEU_THU_GOM p
                JOIN LOAI_PIN lp ON p.MaLoaiPin = lp.MaLoaiPin
                WHERE p.MaNguoiDung_KH=?
                ORDER BY p.NgayThuGom DESC
            """, (ma,))
            rows = cur.fetchall()
            self.tbl_pin.setRowCount(len(rows))
            for i, row in enumerate(rows):
                for j, val in enumerate(row):
                    text = f"{val} kg" if j == 2 else f"+{int(val):,} điểm 🌿" if j == 3 else str(val)
                    item = QTableWidgetItem(text)
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    if j == 3:
                        item.setForeground(QColor("#6ee7b7"))
                    self.tbl_pin.setItem(i, j, item)

        elif role == "ChuDauTu":
            cur.execute("""
                SELECT SUM(p.KhoiLuong) FROM PHIEU_THU_GOM p
                JOIN NHAN_VIEN nv ON p.MaNguoiDung_NV = nv.MaNguoiDung
                JOIN TRAM_SAC ts ON nv.MaTram = ts.MaTram
                WHERE ts.MaNguoiDung=?
            """, (ma,))
            r = cur.fetchone()
            total_kg = r[0] if r and r[0] else 0
            self.lbl_tong.setText(f"♻️ Tổng lượng pin thu gom (tại trạm của bạn): {total_kg:.2f} kg")

            cur.execute("""
                SELECT p.MaPhieu, nd_kh.HoTen, nd_nv.HoTen, lp.TenLoaiPin,
                       p.KhoiLuong, p.DiemThuong, p.NgayThuGom
                FROM PHIEU_THU_GOM p
                JOIN NGUOI_DUNG nd_kh ON p.MaNguoiDung_KH = nd_kh.MaNguoiDung
                JOIN NGUOI_DUNG nd_nv ON p.MaNguoiDung_NV = nd_nv.MaNguoiDung
                JOIN LOAI_PIN lp ON p.MaLoaiPin = lp.MaLoaiPin
                JOIN NHAN_VIEN nv ON p.MaNguoiDung_NV = nv.MaNguoiDung
                JOIN TRAM_SAC ts ON nv.MaTram = ts.MaTram
                WHERE ts.MaNguoiDung=?
                ORDER BY p.NgayThuGom DESC
            """, (ma,))
            rows = cur.fetchall()
            self.tbl_pin.setRowCount(len(rows))
            for i, row in enumerate(rows):
                for j, val in enumerate(row):
                    text = f"{val} kg" if j == 4 else f"{int(val):,} điểm" if j == 5 else str(val)
                    item = QTableWidgetItem(text)
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    self.tbl_pin.setItem(i, j, item)

        conn.close()

    def _make_table(self, headers):
        tbl = QTableWidget()
        tbl.setColumnCount(len(headers))
        tbl.setHorizontalHeaderLabels(headers)
        tbl.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        tbl.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        tbl.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        tbl.setStyleSheet(self._table_style())
        return tbl

    def _group_style(self): return GROUP_STYLE

    def _table_style(self): return TABLE_STYLE

    def _input_style(self): return INPUT_STYLE

    def _combo_style(self): return COMBO_STYLE

    def _btn_style(self, color=None): return btn_style(color)
