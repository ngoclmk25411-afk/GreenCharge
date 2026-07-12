import sqlite3
from datetime import datetime
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTableWidget,
    QTableWidgetItem, QPushButton, QComboBox, QHeaderView,
    QMessageBox, QGroupBox, QSpinBox, QSplitter, QFrame, QSizePolicy
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


class ThanhToanWidget(QWidget):
    def __init__(self, user_info, parent=None):
        super().__init__(parent)
        self.user = user_info
        self.setup_ui()
        self.load_data()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(16, 16, 16, 16)

        title = QLabel("💳 Thanh Toán & Hóa Đơn")
        title.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        title.setStyleSheet(TITLE_STYLE)
        layout.addWidget(title)

        role = self.user["VaiTro"]

        if role == "KhachHang":
            # Điểm xanh banner
            self.lbl_diem = QLabel("🌿 Điểm Xanh: 0")
            self.lbl_diem.setStyleSheet("""
                background: qlineargradient(x1:0,y1:0,x2:1,y2:0,stop:0 #064e3b,stop:1 #065f46);
                color: #6ee7b7; font-size: 14px; font-weight: bold;
                border-radius: 8px; padding: 10px 16px;
            """)
            self.lbl_diem.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
            layout.addWidget(self.lbl_diem)

            # Bảng hóa đơn
            top_box = QGroupBox("Danh sách Hóa Đơn")
            top_box.setStyleSheet(self._group_style())
            top_box.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
            top_layout = QVBoxLayout(top_box)
            top_layout.setContentsMargins(14, 18, 14, 14)
            top_layout.setSpacing(10)
            cols = ["Mã HD", "Phiên Sạc", "Tổng Tiền Gốc", "Điểm Dùng", "Tiền Giảm", "Thanh Toán", "Trạng Thái", "Ngày"]
            self.tbl_hd = self._make_table(cols)
            self.tbl_hd.selectionModel().selectionChanged.connect(self.on_hd_selected)
            top_layout.addWidget(self.tbl_hd, 1)
            layout.addWidget(top_box, 1)

            # Panel thanh toán
            bot_box = QGroupBox("Thanh toán hóa đơn đã chọn")
            bot_box.setStyleSheet(self._group_style())
            bot_box.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
            bot_layout = QHBoxLayout(bot_box)
            bot_layout.setContentsMargins(14, 18, 14, 14)
            bot_layout.setSpacing(10)

            self.lbl_hd_info = QLabel("Chọn hóa đơn để thanh toán")
            self.lbl_hd_info.setStyleSheet("color: #6b7280;")
            bot_layout.addWidget(self.lbl_hd_info)

            bot_layout.addStretch()

            spin_label = QLabel("Điểm xanh dùng:")
            spin_label.setStyleSheet("color: #374151; font-weight: 600;")
            self.spin_diem = QSpinBox()
            self.spin_diem.setRange(0, 9999)
            self.spin_diem.setSingleStep(10)
            self.spin_diem.setStyleSheet(self._input_style())
            self.spin_diem.valueChanged.connect(self.tinh_tien_sau_giam)

            self.lbl_sau_giam = QLabel("Sau giảm: 0 đ")
            self.lbl_sau_giam.setStyleSheet(f"color: {G1}; font-weight: bold; font-size: 13px;")

            self.cmb_pttt = QComboBox()
            self.cmb_pttt.addItems(["Tiền mặt", "Chuyển khoản", "Ví điện tử", "Thẻ ngân hàng"])
            self.cmb_pttt.setStyleSheet(self._combo_style())

            btn_pay = QPushButton("✅ Xác nhận Thanh Toán")
            btn_pay.setMinimumHeight(38)
            btn_pay.setStyleSheet(self._btn_style("#10b981"))
            btn_pay.clicked.connect(self.thanh_toan)

            bot_layout.addWidget(spin_label)
            bot_layout.addWidget(self.spin_diem)
            bot_layout.addWidget(self.lbl_sau_giam)
            bot_layout.addWidget(self.cmb_pttt)
            bot_layout.addWidget(btn_pay)

            layout.addWidget(bot_box)

        elif role == "ChuDauTu":
            # ── Bộ lọc: chọn trạm để xem doanh thu ──────────────────────
            filter_row = QHBoxLayout()
            filter_row.setSpacing(10)
            lbl_chon = QLabel("🏗️ Xem doanh thu tại trạm:")
            lbl_chon.setStyleSheet(LBL_STYLE)
            self.cmb_tram_dt = QComboBox()
            self.cmb_tram_dt.setStyleSheet(self._combo_style())
            self.cmb_tram_dt.setMinimumHeight(38)
            self.cmb_tram_dt.currentIndexChanged.connect(self.load_data)
            filter_row.addWidget(lbl_chon)
            filter_row.addWidget(self.cmb_tram_dt, 1)
            layout.addLayout(filter_row)
            layout.addSpacing(4)

            # ── Card tổng hợp ────────────────────────────────────────────
            card_row = QHBoxLayout()
            card_row.setSpacing(14)
            self.card_doanh_thu = self._make_stat_card("💰", "Tổng Doanh Thu", "0 đ", G1)
            self.card_kwh = self._make_stat_card("⚡", "Tổng kWh Tiêu Thụ", "0 kWh", "#0ea5e9")
            self.card_phien = self._make_stat_card("🔌", "Số Phiên Sạc", "0 phiên", "#8b5cf6")
            card_row.addWidget(self.card_doanh_thu)
            card_row.addWidget(self.card_kwh)
            card_row.addWidget(self.card_phien)
            layout.addLayout(card_row)
            layout.addSpacing(4)

            # ── Bảng chi tiết doanh thu ──────────────────────────────────
            box = QGroupBox("Chi tiết Doanh Thu Theo Trạm")
            box.setStyleSheet(self._group_style())
            box.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
            box_layout = QVBoxLayout(box)
            box_layout.setContentsMargins(14, 18, 14, 14)
            box_layout.setSpacing(10)
            cols = ["Mã HD", "Trạm Sạc", "Khách Hàng", "Số kWh", "Tổng Tiền", "Phí App", "Doanh Thu CDT", "Trạng Thái", "Ngày TT"]
            self.tbl_hd = self._make_table(cols)
            box_layout.addWidget(self.tbl_hd, 1)

            btn_rf_row = QHBoxLayout()
            btn_rf_row.addStretch()
            btn_rf = QPushButton("🔄 Làm mới")
            btn_rf.setMinimumHeight(38)
            btn_rf.setStyleSheet(self._btn_style("#0ea5e9"))
            btn_rf.clicked.connect(self.load_data)
            btn_rf_row.addWidget(btn_rf)
            box_layout.addLayout(btn_rf_row)

            layout.addWidget(box, 1)

            self._load_tram_list_dt()

        else:
            # Nhân viên: xem hóa đơn
            box = QGroupBox("Hóa đơn tại trạm")
            box.setStyleSheet(self._group_style())
            box.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
            box_layout = QVBoxLayout(box)
            box_layout.setContentsMargins(14, 18, 14, 14)
            box_layout.setSpacing(10)
            cols = ["Mã HD", "Phiên", "Khách Hàng", "Tổng Tiền", "Thanh Toán", "Trạng Thái", "Ngày"]
            self.tbl_hd = self._make_table(cols)
            box_layout.addWidget(self.tbl_hd, 1)
            btn_rf = QPushButton("🔄 Làm mới")
            btn_rf.setMinimumHeight(38)
            btn_rf.setStyleSheet(self._btn_style("#0ea5e9"))
            btn_rf.clicked.connect(self.load_data)
            box_layout.addWidget(btn_rf)
            layout.addWidget(box, 1)

    def load_data(self):
        conn = get_conn()
        cur = conn.cursor()
        role = self.user["VaiTro"]
        ma = self.user["MaNguoiDung"]

        if role == "KhachHang":
            # Lấy điểm xanh
            cur.execute("SELECT DiemXanh FROM KHACH_HANG WHERE MaNguoiDung=?", (ma,))
            r = cur.fetchone()
            diem = r[0] if r else 0
            self.lbl_diem.setText(f"🌿 Điểm Xanh của bạn: {diem:,} điểm  (1 điểm = 1.000 đ)")
            self.spin_diem.setMaximum(diem)

            cur.execute("""
            SELECT
                MaHD,
                MaPhien,
                TongTienGoc,
                SoDiemTieuThu,
                SoTienGiam,
                TongTienThanhToan,
                TrangThaiHD,
                NgayThanhToan
            FROM HoaDon
            WHERE MaNguoiDung=?
            ORDER BY MaHD DESC
            """, (ma,))
            rows = cur.fetchall()
            self.tbl_hd.setRowCount(len(rows))
            color_map = {"Chưa thanh toán": "#f59e0b", "Đã thanh toán": "#10b981",
                         "Thất bại": "#ef4444", "Đã hoàn tiền": "#8b5cf6"}
            for i, row in enumerate(rows):
                for j, val in enumerate(row):
                    text = f"{int(val):,} đ" if j in (2, 4, 5) and val else str(val)
                    item = QTableWidgetItem(text)
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    if j == 6:
                        item.setForeground(QColor(color_map.get(val, "#374151")))
                    self.tbl_hd.setItem(i, j, item)

        elif role == "ChuDauTu":
            if not hasattr(self, "cmb_tram_dt"):
                conn.close()
                return

            ma_tram_sel = self.cmb_tram_dt.currentData()

            where_clause = "ts.MaNguoiDung=?"
            params = [ma]
            if ma_tram_sel:
                where_clause += " AND ts.MaTram=?"
                params.append(ma_tram_sel)

            # ── Card tổng hợp (chỉ tính hóa đơn đã thanh toán) ──────────
            cur.execute(f"""
                SELECT
                    COALESCE(SUM(hd.DoanhThuCDT), 0),
                    COALESCE(SUM(ps.SoKwhTieuThu), 0),
                    COUNT(DISTINCT ps.MaPhien)
                FROM HoaDon hd
                JOIN PhienSac ps ON hd.MaPhien = ps.MaPhien
                JOIN LichDatCho l ON ps.MaLichDat = l.MaLichDat
                JOIN CONG_SAC cs ON l.MaCong = cs.MaCong
                JOIN TRAM_SAC ts ON cs.MaTram = ts.MaTram
                WHERE {where_clause} AND hd.TrangThaiHD='Đã thanh toán'
            """, params)
            tong_dt, tong_kwh, so_phien = cur.fetchone()
            self.card_doanh_thu.value_label.setText(f"{int(tong_dt or 0):,} đ")
            self.card_kwh.value_label.setText(f"{float(tong_kwh or 0):,.1f} kWh")
            self.card_phien.value_label.setText(f"{so_phien or 0} phiên")

            # ── Bảng chi tiết doanh thu theo trạm ────────────────────────
            cur.execute(f"""
                SELECT hd.MaHD, ts.TenTram, nd.HoTen, ps.SoKwhTieuThu,
                       hd.TongTienGoc, hd.PhiVanHanhApp, hd.DoanhThuCDT,
                       hd.TrangThaiHD, hd.NgayThanhToan
                FROM HoaDon hd
                JOIN NGUOI_DUNG nd ON hd.MaNguoiDung = nd.MaNguoiDung
                JOIN PhienSac ps ON hd.MaPhien = ps.MaPhien
                JOIN LichDatCho l ON ps.MaLichDat = l.MaLichDat
                JOIN CONG_SAC cs ON l.MaCong = cs.MaCong
                JOIN TRAM_SAC ts ON cs.MaTram = ts.MaTram
                WHERE {where_clause}
                ORDER BY hd.NgayThanhToan DESC
            """, params)
            rows = cur.fetchall()
            self.tbl_hd.setRowCount(len(rows))
            color_map = {"Chưa thanh toán": "#f59e0b", "Đã thanh toán": "#10b981",
                         "Thất bại": "#ef4444", "Đã hoàn tiền": "#8b5cf6"}
            for i, row in enumerate(rows):
                for j, val in enumerate(row):
                    if j == 3 and val is not None:
                        text = f"{float(val):,.1f} kWh"
                    elif j in (4, 5, 6) and val is not None:
                        text = f"{int(val):,} đ"
                    else:
                        text = str(val) if val is not None else ""
                    item = QTableWidgetItem(text)
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    if j == 7:
                        item.setForeground(QColor(color_map.get(val, "#374151")))
                    self.tbl_hd.setItem(i, j, item)

        elif role == "NhanVien":
            cur.execute("SELECT MaTram FROM NHAN_VIEN WHERE MaNguoiDung=?", (ma,))
            r = cur.fetchone()
            if not r:
                conn.close()
                return
            ma_tram = r[0]
            cur.execute("""
                SELECT hd.MaHD, hd.MaPhien, nd.HoTen, hd.TongTienGoc,
                       hd.TongTienThanhToan, hd.TrangThaiHD, hd.NgayThanhToan
                FROM HoaDon hd
                JOIN NGUOI_DUNG nd ON hd.MaNguoiDung = nd.MaNguoiDung
                JOIN PhienSac ps ON hd.MaPhien = ps.MaPhien
                LEFT JOIN LichDatCho l ON ps.MaLichDat = l.MaLichDat
                LEFT JOIN CONG_SAC cs ON l.MaCong = cs.MaCong
                WHERE cs.MaTram=?
                ORDER BY hd.NgayThanhToan DESC
            """, (ma_tram,))
            rows = cur.fetchall()
            self.tbl_hd.setRowCount(len(rows))
            for i, row in enumerate(rows):
                for j, val in enumerate(row):
                    text = f"{int(val):,} đ" if j in (3, 4) and val else str(val) if val else ""
                    item = QTableWidgetItem(text)
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    self.tbl_hd.setItem(i, j, item)

        conn.close()

    def on_hd_selected(self):
        row = self.tbl_hd.currentRow()
        if row < 0:
            return
        ma_hd = self.tbl_hd.item(row, 0).text()
        tong = self.tbl_hd.item(row, 2).text().replace(",", "").replace(" đ", "")
        trang_thai = self.tbl_hd.item(row, 6).text()
        self.lbl_hd_info.setText(f"HĐ: {ma_hd} | Tổng tiền gốc: {self.tbl_hd.item(row, 2).text()} | Trạng thái: {trang_thai}")
        self.tinh_tien_sau_giam()

    def tinh_tien_sau_giam(self):
        row = self.tbl_hd.currentRow()
        if row < 0:
            return
        tong_str = self.tbl_hd.item(row, 2).text().replace(",", "").replace(" đ", "").strip()
        try:
            tong = float(tong_str)
        except:
            return
        diem = self.spin_diem.value()
        giam = diem * 1000
        sau_giam = max(0, tong - giam)
        self.lbl_sau_giam.setText(f"Sau giảm: {int(sau_giam):,} đ")

    def thanh_toan(self):
        row = self.tbl_hd.currentRow()

        if row < 0:
            QMessageBox.warning(self, "Thông báo", "Vui lòng chọn hóa đơn.")
            return

        ma_hd = self.tbl_hd.item(row, 0).text()

        conn = get_conn()
        cur = conn.cursor()

        cur.execute("""
            SELECT
                MaNguoiDung,
                TongTienGoc,
                TrangThaiHD
            FROM HoaDon
            WHERE MaHD=?
        """, (ma_hd,))

        hd = cur.fetchone()

        if not hd:
            conn.close()
            QMessageBox.warning(self, "Lỗi", "Không tìm thấy hóa đơn.")
            return

        ma_nd, tong_goc, trang_thai = hd

        if trang_thai == "Đã thanh toán":
            conn.close()
            QMessageBox.information(self, "Thông báo", "Hóa đơn đã được thanh toán.")
            return

        tong_goc = float(tong_goc)

        # Điểm xanh hiện có
        cur.execute("""
            SELECT DiemXanh
            FROM KHACH_HANG
            WHERE MaNguoiDung=?
        """, (ma_nd,))

        diem = cur.fetchone()
        diem_hien_co = diem[0] if diem else 0

        dung_diem = self.spin_diem.value()
        if dung_diem > diem_hien_co:
            dung_diem = diem_hien_co

        giam = dung_diem * 1000

        tong_tt = max(0, tong_goc - giam)

        # Trừ điểm
        if dung_diem > 0:
            cur.execute("""
                UPDATE KHACH_HANG
                SET DiemXanh = DiemXanh - ?
                WHERE MaNguoiDung=?
            """, (
                dung_diem,
                ma_nd
            ))

        # Cập nhật hóa đơn
        cur.execute("""
            UPDATE HoaDon
            SET
                SoDiemTieuThu=?,
                SoTienGiam=?,
                TongTienThanhToan=?,
                TrangThaiHD='Đã thanh toán',
                NgayThanhToan=datetime('now', 'localtime'),
                PhuongThucThanhToan=?
            WHERE MaHD=?
        """, (
            dung_diem,
            giam,
            tong_tt,
            self.cmb_pttt.currentText(),
            ma_hd
        ))

        conn.commit()
        conn.close()

        QMessageBox.information(
            self,
            "Thành công",
            f"""Thanh toán thành công.

    Điểm dùng: {dung_diem}

    Giảm: {int(giam):,} đ

    Thanh toán: {int(tong_tt):,} đ"""
        )

        self.load_data()
    def _load_tram_list_dt(self):
        """Nạp danh sách các trạm thuộc sở hữu của Chủ đầu tư vào combo lọc doanh thu."""
        ma = self.user["MaNguoiDung"]
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("SELECT MaTram, TenTram FROM TRAM_SAC WHERE MaNguoiDung=? ORDER BY TenTram", (ma,))
        rows = cur.fetchall()
        conn.close()

        self.cmb_tram_dt.blockSignals(True)
        self.cmb_tram_dt.clear()
        self.cmb_tram_dt.addItem("🏢  Tất cả các trạm", None)
        for r in rows:
            self.cmb_tram_dt.addItem(f"{r[1]}  ({r[0]})", r[0])
        self.cmb_tram_dt.blockSignals(False)

    def _make_stat_card(self, icon, title, value, color):
        """Tạo một card thống kê nhỏ (icon + tiêu đề + giá trị) theo theme Modern Emerald."""
        frame = QFrame()
        frame.setStyleSheet(f"""
            QFrame {{
                background-color: #ffffff;
                border: 1px solid #e2e8f0;
                border-left: 4px solid {color};
                border-radius: 10px;
            }}
        """)
        v = QVBoxLayout(frame)
        v.setContentsMargins(16, 12, 16, 12)
        v.setSpacing(4)

        lbl_top = QLabel(f"{icon}  {title}")
        lbl_top.setStyleSheet("color: #6b7280; font-size: 12px; font-weight: 600;")
        lbl_val = QLabel(value)
        lbl_val.setStyleSheet(f"color: {color}; font-size: 20px; font-weight: 800;")

        v.addWidget(lbl_top)
        v.addWidget(lbl_val)
        frame.value_label = lbl_val
        return frame

    def _make_table(self, headers):
        tbl = QTableWidget()
        tbl.setColumnCount(len(headers))
        tbl.setHorizontalHeaderLabels(headers)
        tbl.horizontalHeader().setDefaultAlignment(Qt.AlignmentFlag.AlignCenter)
        tbl.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        tbl.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        tbl.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        tbl.setStyleSheet(self._table_style())
        tbl.setAlternatingRowColors(True)
        tbl.verticalHeader().setDefaultSectionSize(34)
        return tbl

    def _group_style(self): return GROUP_STYLE

    def _table_style(self): return TABLE_STYLE

    def _input_style(self): return INPUT_STYLE

    def _combo_style(self): return COMBO_STYLE

    def _btn_style(self, color=None): return btn_style(color)