import sqlite3
from datetime import datetime
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTableWidget,
    QTableWidgetItem, QPushButton, QComboBox, QHeaderView,
    QMessageBox, QGroupBox, QDoubleSpinBox, QSplitter, QFormLayout, QSizePolicy
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QColor, QFont
from main.shared_theme import (
    GROUP_STYLE, TABLE_STYLE, COMBO_STYLE, INPUT_STYLE,
    DIALOG_STYLE, TITLE_STYLE, LBL_STYLE, btn_style, status_color, G1, G2, G_M, G_B, G_L
)


DB_PATH = "datasets/data.db"


def get_conn():
    return sqlite3.connect(DB_PATH)


class PhienSacWidget(QWidget):
    def __init__(self, user_info, parent=None):
        super().__init__(parent)
        self.user = user_info
        self.setup_ui()
        self.load_data()

        if self.user["VaiTro"] == "KhachHang":
            self.auto_check_timer = QTimer(self)
            self.auto_check_timer.setInterval(10000)  # 10 giây
            self.auto_check_timer.timeout.connect(self.on_timer_timeout)
            self.auto_check_timer.start()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(16, 16, 16, 16)

        title = QLabel("⚡ Quản lý Phiên Sạc")
        title.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        title.setStyleSheet("color: #059669;")
        layout.addWidget(title)

        role = self.user["VaiTro"]

        if role == "NhanVien":
            # Panel bắt đầu phiên
            top_box = QGroupBox("Bắt đầu phiên sạc từ lịch đặt")
            top_box.setStyleSheet(self._group_style())
            top_box.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
            top_layout = QVBoxLayout(top_box)
            top_layout.setContentsMargins(14, 18, 14, 14)
            top_layout.setSpacing(10)

            cols_lich = ["Mã Lịch", "Biển Số", "Khách Hàng", "Cổng", "Giờ Đặt"]
            self.tbl_lich = self._make_table(cols_lich)
            top_layout.addWidget(self.tbl_lich, 1)

            layout.addWidget(top_box, 1)

            # Panel kết thúc phiên
            bot_box = QGroupBox("Kết thúc phiên đang sạc")
            bot_box.setStyleSheet(self._group_style())
            bot_box.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
            bot_layout = QVBoxLayout(bot_box)
            bot_layout.setContentsMargins(14, 18, 14, 14)
            bot_layout.setSpacing(10)

            cols_phien = ["Mã Phiên", "Mã Lịch", "Giờ Bắt Đầu", "Trạng Thái"]
            self.tbl_phien = self._make_table(cols_phien)
            bot_layout.addWidget(self.tbl_phien, 1)

            kwh_row = QHBoxLayout()
            kwh_row.setSpacing(10)
            kwh_row.addWidget(QLabel("Số kWh tiêu thụ:"))
            self.spin_kwh = QDoubleSpinBox()
            self.spin_kwh.setRange(0.01, 999.99)
            self.spin_kwh.setValue(10.0)
            self.spin_kwh.setSuffix(" kWh")
            self.spin_kwh.setStyleSheet(self._input_style())
            kwh_row.addWidget(self.spin_kwh)
            btn_ket_thuc = QPushButton("⏹ Kết Thúc & Tạo Hóa Đơn")
            btn_ket_thuc.setMinimumHeight(38)
            btn_ket_thuc.setStyleSheet(self._btn_style("#f59e0b"))
            btn_ket_thuc.clicked.connect(self.ket_thuc_phien)
            kwh_row.addWidget(btn_ket_thuc)
            kwh_row.addStretch()
            bot_layout.addLayout(kwh_row)

            layout.addWidget(bot_box, 1)

        elif role == "KhachHang":
            # ── Panel 1: Lịch đã đặt (chờ sạc) ──────────────
            top_box = QGroupBox("📋 Lịch đã đặt — Chờ bắt đầu sạc")
            top_box.setStyleSheet(self._group_style())
            top_box.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
            top_layout = QVBoxLayout(top_box)
            top_layout.setSpacing(10)
            top_layout.setContentsMargins(14, 18, 14, 14)

            cols_lich = ["Mã Lịch", "Biển Số Xe", "Cổng Sạc", "Giờ Bắt Đầu", "Giờ Kết Thúc", "Trạng Thái"]
            self.tbl_lich_kh = self._make_table(cols_lich)
            top_layout.addWidget(self.tbl_lich_kh, 1)
            top_layout.addSpacing(4)

            btn_top_row = QHBoxLayout()
            btn_top_row.setSpacing(10)
            btn_bat_dau = QPushButton("▶ Bắt Đầu Sạc")
            btn_bat_dau.setMinimumHeight(40)
            btn_bat_dau.setStyleSheet(self._btn_style("#10b981"))
            btn_bat_dau.clicked.connect(self.khach_bat_dau_sac)
            btn_top_row.addWidget(btn_bat_dau)
            btn_top_row.addStretch()
            top_layout.addLayout(btn_top_row)

            layout.addWidget(top_box, 45)

            # ── Panel 2: Phiên sạc (đang sạc + lịch sử) ─────
            bot_box = QGroupBox("⚡ Phiên sạc của tôi")
            bot_box.setStyleSheet(self._group_style())
            bot_box.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
            bot_layout = QVBoxLayout(bot_box)
            bot_layout.setSpacing(10)
            bot_layout.setContentsMargins(14, 18, 14, 14)

            cols = ["Mã Phiên", "Cổng Sạc", "Bắt Đầu", "Kết Thúc", "Số kWh", "Trạng Thái"]
            self.tbl_phien = self._make_table(cols)
            bot_layout.addWidget(self.tbl_phien, 1)
            bot_layout.addSpacing(4)

            btn_bot_row = QHBoxLayout()
            btn_bot_row.setSpacing(10)
            btn_ngat = QPushButton("⏹ Ngắt Kết Nối & Thanh Toán")
            btn_ngat.setMinimumHeight(40)
            btn_ngat.setStyleSheet(self._btn_style("#ef4444"))
            btn_ngat.clicked.connect(self.khach_ngat_ket_noi)
            btn_bot_row.addWidget(btn_ngat)

            btn_rf = QPushButton("🔄 Làm mới")
            btn_rf.setMinimumHeight(40)
            btn_rf.setStyleSheet(self._btn_style("#0ea5e9"))
            btn_rf.clicked.connect(self.load_data)
            btn_bot_row.addWidget(btn_rf)
            btn_bot_row.addStretch()
            bot_layout.addLayout(btn_bot_row)

            layout.addWidget(bot_box, 55)

        else:
            # Investor: chỉ xem lịch sử
            box = QGroupBox("Lịch sử phiên sạc")
            box.setStyleSheet(self._group_style())
            box.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
            box_layout = QVBoxLayout(box)
            box_layout.setContentsMargins(14, 18, 14, 14)
            box_layout.setSpacing(10)
            cols = ["Mã Phiên", "Mã Lịch", "Bắt Đầu", "Kết Thúc", "Số kWh", "Trạng Thái"]
            self.tbl_phien = self._make_table(cols)
            box_layout.addWidget(self.tbl_phien, 1)

            btn_row = QHBoxLayout()
            btn_rf = QPushButton("🔄 Làm mới")
            btn_rf.setMinimumHeight(38)
            btn_rf.setStyleSheet(self._btn_style("#0ea5e9"))
            btn_rf.clicked.connect(self.load_data)
            btn_row.addWidget(btn_rf)
            btn_row.addStretch()
            box_layout.addLayout(btn_row)
            layout.addWidget(box, 1)

    def load_data(self):
        # Tự động check và ngắt phiên quá hạn
        ended = self.auto_check_overtime_sessions(reload=False)
        if ended:
            self.switch_to_hoadon_tab()

        # Tự động hủy lịch sạc trễ quá 15 phút
        self.auto_check_late_bookings()

        conn = get_conn()
        cur = conn.cursor()

        role = self.user["VaiTro"]
        ma = self.user["MaNguoiDung"]

        if role == "NhanVien":
            # Load lịch đặt chờ sạc tại trạm nhân viên
            cur.execute("SELECT MaTram FROM NHAN_VIEN WHERE MaNguoiDung=?", (ma,))
            r = cur.fetchone()
            if not r:
                conn.close()
                return
            ma_tram = r[0]
            cur.execute("""
                SELECT l.MaLichDat, x.BienSo, nd.HoTen, l.MaCong, l.GioBatDau
                FROM LichDatCho l
                JOIN Xe x ON l.MaXe = x.MaXe
                JOIN NGUOI_DUNG nd ON x.MaNguoiDung = nd.MaNguoiDung
                JOIN CONG_SAC cs ON l.MaCong = cs.MaCong
                WHERE cs.MaTram=? AND l.TrangThaiLich='Đang sạc'
            """, (ma_tram,))
            rows = cur.fetchall()
            self.tbl_lich.setRowCount(len(rows))
            for i, row in enumerate(rows):
                for j, val in enumerate(row):
                    item = QTableWidgetItem(str(val))
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    self.tbl_lich.setItem(i, j, item)

            # Load phiên đang sạc
            cur.execute("""
                SELECT ps.MaPhien, ps.MaLichDat, ps.GioBatDau, ps.TrangThaiPhien
                FROM PhienSac ps
                LEFT JOIN LichDatCho l ON ps.MaLichDat = l.MaLichDat
                LEFT JOIN CONG_SAC cs ON l.MaCong = cs.MaCong
                WHERE ps.TrangThaiPhien='Đang sạc'
                AND (cs.MaTram=? OR ps.MaLichDat IS NULL)
            """, (ma_tram,))
            rows2 = cur.fetchall()
            self.tbl_phien.setRowCount(len(rows2))
            for i, row in enumerate(rows2):
                for j, val in enumerate(row):
                    item = QTableWidgetItem(str(val) if val else "")
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    self.tbl_phien.setItem(i, j, item)

        elif role == "KhachHang":
            # Load lịch đặt chờ sạc của khách hàng
            cur.execute("""
                SELECT l.MaLichDat, x.BienSo, l.MaCong, l.GioBatDau, l.GioKetThuc, l.TrangThaiLich
                FROM LichDatCho l
                JOIN Xe x ON l.MaXe = x.MaXe
                WHERE x.MaNguoiDung=? AND l.TrangThaiLich IN ('Đã đặt', 'Đã xác nhận')
                ORDER BY l.GioBatDau ASC
            """, (ma,))
            rows_lich = cur.fetchall()
            self.tbl_lich_kh.setRowCount(len(rows_lich))
            for i, row in enumerate(rows_lich):
                for j, val in enumerate(row):
                    item = QTableWidgetItem(str(val))
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    self.tbl_lich_kh.setItem(i, j, item)

            # Load phiên sạc
            cur.execute("""
                SELECT ps.MaPhien, l.MaCong, ps.GioBatDau, ps.GioKetThuc, ps.SoKwhTieuThu, ps.TrangThaiPhien
                FROM PhienSac ps
                JOIN LichDatCho l ON ps.MaLichDat = l.MaLichDat
                JOIN Xe x ON l.MaXe = x.MaXe
                WHERE x.MaNguoiDung=?
                ORDER BY ps.GioBatDau DESC
            """, (ma,))
            rows = cur.fetchall()
            self.tbl_phien.setRowCount(len(rows))
            color_map = {"Đang sạc": "#3b82f6", "Hoàn thành": "#10b981", "Đã hủy": "#ef4444"}
            for i, row in enumerate(rows):
                for j, val in enumerate(row):
                    item = QTableWidgetItem(str(val) if val else "")
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    if j == 5:
                        item.setForeground(QColor(color_map.get(val, "#374151")))
                    self.tbl_phien.setItem(i, j, item)

        elif role == "ChuDauTu":
            cur.execute("""
                SELECT ps.MaPhien, ps.MaLichDat, ps.GioBatDau, ps.GioKetThuc, ps.SoKwhTieuThu, ps.TrangThaiPhien
                FROM PhienSac ps
                LEFT JOIN LichDatCho l ON ps.MaLichDat = l.MaLichDat
                LEFT JOIN CONG_SAC cs ON l.MaCong = cs.MaCong
                LEFT JOIN TRAM_SAC ts ON cs.MaTram = ts.MaTram
                WHERE ts.MaNguoiDung=? OR ts.MaNguoiDung IS NULL
                ORDER BY ps.GioBatDau DESC
            """, (ma,))
            rows = cur.fetchall()
            self.tbl_phien.setRowCount(len(rows))
            for i, row in enumerate(rows):
                for j, val in enumerate(row):
                    item = QTableWidgetItem(str(val) if val else "")
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    self.tbl_phien.setItem(i, j, item)

        conn.close()

    def ket_thuc_phien(self):
        row = self.tbl_phien.currentRow()

        if row < 0:
            QMessageBox.warning(self, "Chưa chọn", "Vui lòng chọn một phiên đang sạc.")
            return

        ma_phien = self.tbl_phien.item(row, 0).text()

        conn = get_conn()
        cur = conn.cursor()

        # Lấy thông tin phiên
        cur.execute("""
            SELECT GioBatDau, MaLichDat, MaBieuGia
            FROM PhienSac
            WHERE MaPhien=?
        """, (ma_phien,))

        phien = cur.fetchone()

        if not phien:
            conn.close()
            QMessageBox.warning(self, "Lỗi", "Không tìm thấy phiên sạc.")
            return

        gio_bat_dau, ma_lich, ma_bg = phien

        bat_dau = datetime.strptime(gio_bat_dau, "%Y-%m-%d %H:%M:%S")
        gio = (datetime.now() - bat_dau).total_seconds() / 3600
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Lấy công suất cổng
        cur.execute("""
            SELECT cs.CongSuat
            FROM CONG_SAC cs
            JOIN LichDatCho l
                ON cs.MaCong = l.MaCong
            WHERE l.MaLichDat=?
        """, (ma_lich,))

        r = cur.fetchone()
        cong_suat = float(r[0]) if r else 22

        # Tính điện tiêu thụ
        kwh = round(gio * cong_suat, 2)

        # Lấy đơn giá
        cur.execute("""
            SELECT DonGiaKwh
            FROM BieuGiaDien
            WHERE MaBieuGia=?
        """, (ma_bg,))

        gia = cur.fetchone()
        don_gia = float(gia[0]) if gia else 3000

        tong_tien = round(kwh * don_gia, 2)
        phi_app = round(tong_tien * 0.05, 2)
        doanh_thu = round(tong_tien * 0.95, 2)

        # Cập nhật phiên sạc
        cur.execute("""
            UPDATE PhienSac
            SET GioKetThuc=?,
                SoKwhTieuThu=?,
                TrangThaiPhien='Hoàn thành'
            WHERE MaPhien=?
        """, (
            now,
            kwh,
            ma_phien
        ))

        # Lấy khách hàng
        cur.execute("""
            SELECT x.MaNguoiDung, l.MaCong
            FROM LichDatCho l
            JOIN Xe x
                ON l.MaXe=x.MaXe
            WHERE l.MaLichDat=?
        """, (ma_lich,))

        info = cur.fetchone()

        if info:
            ma_kh = info[0]
            ma_cong = info[1]

            # Sinh mã hóa đơn
            cur.execute("""
                SELECT IFNULL(MAX(CAST(substr(MaHD,3) AS INTEGER)),0)
                FROM HoaDon
            """)

            stt = cur.fetchone()[0] + 1
            ma_hd = f"HD{stt:03d}"

            # Tạo hóa đơn
            cur.execute("""
                INSERT INTO HoaDon
                (
                    MaHD,
                    MaPhien,
                    MaNguoiDung,
                    TongTienGoc,
                    SoDiemTieuThu,
                    SoTienGiam,
                    TongTienThanhToan,
                    PhiVanHanhApp,
                    DoanhThuCDT,
                    TrangThaiHD,
                    NgayThanhToan,
                    PhuongThucThanhToan
                )
                VALUES
                (
                    ?,?,?,?,?,?,?,?,?,?,?,?
                )
            """,
                        (
                            ma_hd,
                            ma_phien,
                            ma_kh,
                            tong_tien,
                            0,
                            0,
                            tong_tien,
                            phi_app,
                            doanh_thu,
                            "Chưa thanh toán",
                            now,
                            "Tiền mặt"
                        ))

            # Trả cổng về Trống
            cur.execute("""
                UPDATE CONG_SAC
                SET TrangThaiCong='Trống'
                WHERE MaCong=?
            """, (ma_cong,))

        # Hoàn thành lịch
        cur.execute("""
            UPDATE LichDatCho
            SET TrangThaiLich='Hoàn thành'
            WHERE MaLichDat=?
        """, (ma_lich,))

        conn.commit()
        conn.close()

        QMessageBox.information(
            self,
            "Hoàn thành",
            f"""Phiên {ma_phien} hoàn thành.

    Điện tiêu thụ: {kwh:.2f} kWh

    Đơn giá: {int(don_gia):,} đ/kWh

    Tổng tiền: {int(tong_tien):,} đ

    Hóa đơn đã được tạo."""
        )

        self.load_data()

    def khach_bat_dau_sac(self):
        row = self.tbl_lich_kh.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Chưa chọn", "Vui lòng chọn một lịch đặt chờ sạc.")
            return

        ma_lich = self.tbl_lich_kh.item(row, 0).text()
        ma_cong = self.tbl_lich_kh.item(row, 2).text()
        trang_thai = self.tbl_lich_kh.item(row, 5).text()

        if trang_thai not in ("Đã đặt", "Đã xác nhận"):
            QMessageBox.warning(self, "Lỗi", f"Lịch này đã '{trang_thai}', không thể bắt đầu sạc.")
            return

        conn = get_conn()
        cur = conn.cursor()

        # ── Kiểm tra khung giờ đặt lịch ──────────────────────────────────
        cur.execute("SELECT GioBatDau, GioKetThuc FROM LichDatCho WHERE MaLichDat=?", (ma_lich,))
        lich_time = cur.fetchone()
        if not lich_time:
            conn.close()
            QMessageBox.warning(self, "Lỗi", "Không tìm thấy thông tin lịch đặt.")
            return

        gio_bd_str, gio_kt_str = lich_time
        try:
            gio_bd = datetime.strptime(gio_bd_str, "%Y-%m-%d %H:%M:%S")
            gio_kt = datetime.strptime(gio_kt_str, "%Y-%m-%d %H:%M:%S")
        except Exception:
            conn.close()
            QMessageBox.warning(self, "Lỗi", "Dữ liệu giờ đặt lịch không hợp lệ.")
            return

        now = datetime.now()

        # 1. Chưa đến giờ đặt lịch
        if now < gio_bd:
            conn.close()
            phut_con_lai = int((gio_bd - now).total_seconds() / 60) + 1
            QMessageBox.information(
                self, "Chưa đến giờ đặt lịch",
                f"⏱ Lịch đặt {ma_lich} bắt đầu lúc {gio_bd.strftime('%H:%M %d/%m/%Y')}.\n"
                f"Còn khoảng {phut_con_lai} phút nữa mới đến giờ.\n"
                f"Vui lòng quay lại đúng khung giờ đã đặt."
            )
            return

        # 2. Đã quá giờ kết thúc đặt lịch
        if now > gio_kt:
            cur.execute("UPDATE LichDatCho SET TrangThaiLich='Đã hủy' WHERE MaLichDat=?", (ma_lich,))
            cur.execute("UPDATE CONG_SAC SET TrangThaiCong='Trống' WHERE MaCong=?", (ma_cong,))
            conn.commit()
            conn.close()
            QMessageBox.warning(
                self, "Lịch đặt đã hết hạn",
                f"⏱ Lịch đặt {ma_lich} kết thúc lúc {gio_kt.strftime('%H:%M %d/%m/%Y')}.\n"
                f"Thời gian đặt lịch đã trôi qua, hệ thống đã tự động hủy lịch\n"
                f"và giải phóng cổng sạc {ma_cong} về trạng thái 'Trống'."
            )
            self.load_data()
            return

        # 3. Trễ hơn 15 phút so với giờ bắt đầu mà khách chưa đến sạc
        # → tự động hủy lịch và giải phóng cổng sạc
        tre_phut = (now - gio_bd).total_seconds() / 60
        if tre_phut > 15:
            cur.execute("UPDATE LichDatCho SET TrangThaiLich='Đã hủy' WHERE MaLichDat=?", (ma_lich,))
            cur.execute("UPDATE CONG_SAC SET TrangThaiCong='Trống' WHERE MaCong=?", (ma_cong,))
            conn.commit()
            conn.close()
            QMessageBox.warning(
                self, "Lịch đặt đã bị hủy",
                f"⏱ Lịch đặt {ma_lich} bắt đầu lúc {gio_bd.strftime('%H:%M %d/%m/%Y')}.\n"
                f"Bạn đã đến trễ hơn 15 phút nên hệ thống đã tự động hủy lịch\n"
                f"và giải phóng cổng sạc {ma_cong} về trạng thái 'Trống'.\n\n"
                f"Vui lòng đặt lịch mới nếu vẫn muốn sạc."
            )
            self.load_data()
            return

        cur.execute("SELECT TrangThaiCong, LoaiCaySac FROM CONG_SAC WHERE MaCong=?", (ma_cong,))
        cong_row = cur.fetchone()
        if not cong_row:
            conn.close()
            QMessageBox.warning(self, "Lỗi", "Không tìm thấy thông tin cổng sạc.")
            return

        trang_thai_cong, loai_cay_sac = cong_row
        if trang_thai_cong != "Trống":
            conn.close()
            QMessageBox.warning(self, "Lỗi", f"Cổng sạc {ma_cong} đang ở trạng thái '{trang_thai_cong}', không thể sạc.")
            return

        # Tạo mã phiên tiếp theo
        cur.execute("SELECT IFNULL(MAX(CAST(substr(MaPhien,3) AS INTEGER)),0) FROM PhienSac")
        stt = cur.fetchone()[0] + 1
        ma_phien = f"PS{stt:03d}"

        # Tìm biểu giá phù hợp
        cur.execute("""
            SELECT MaBieuGia 
            FROM BieuGiaDien 
            WHERE LoaiCaySac=? AND TrangThai='Đang áp dụng'
            AND (
                (GioBatDau <= GioKetThuc AND time('now', 'localtime') >= GioBatDau AND time('now', 'localtime') <= GioKetThuc) OR
                (GioBatDau > GioKetThuc AND (time('now', 'localtime') >= GioBatDau OR time('now', 'localtime') <= GioKetThuc))
            )
        """, (loai_cay_sac,))
        r = cur.fetchone()
        if r:
            ma_bg = r[0]
        else:
            cur.execute("SELECT MaBieuGia FROM BieuGiaDien WHERE LoaiCaySac=? AND TrangThai='Đang áp dụng' LIMIT 1", (loai_cay_sac,))
            r = cur.fetchone()
            ma_bg = r[0] if r else "BG006"

        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        try:
            # Tạo phiên sạc
            cur.execute("""
                INSERT INTO PhienSac (MaPhien, MaLichDat, GioBatDau, TrangThaiPhien, MaBieuGia)
                VALUES (?, ?, ?, 'Đang sạc', ?)
            """, (ma_phien, ma_lich, now_str, ma_bg))

            # Cập nhật lịch đặt
            cur.execute("UPDATE LichDatCho SET TrangThaiLich='Đang sạc' WHERE MaLichDat=?", (ma_lich,))

            # Cập nhật trạng thái cổng sạc
            cur.execute("UPDATE CONG_SAC SET TrangThaiCong='Đang sạc' WHERE MaCong=?", (ma_cong,))

            conn.commit()
            QMessageBox.information(self, "Thành công", f"Đã bắt đầu phiên sạc {ma_phien} trên cổng {ma_cong}!")
        except Exception as e:
            conn.rollback()
            QMessageBox.critical(self, "Lỗi", f"Có lỗi xảy ra: {e}")
        finally:
            conn.close()

        self.load_data()

    def khach_ngat_ket_noi(self):
        row = self.tbl_phien.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Chưa chọn", "Vui lòng chọn một phiên đang sạc để ngắt kết nối.")
            return
        trang_thai = self.tbl_phien.item(row, 5).text()
        if trang_thai != "Đang sạc":
            QMessageBox.warning(self, "Lỗi", f"Phiên này đã '{trang_thai}', không thể ngắt kết nối.")
            return

        ma_phien = self.tbl_phien.item(row, 0).text()
        now = datetime.now()
        now_str = now.strftime("%Y-%m-%d %H:%M:%S")

        conn = get_conn()
        cur = conn.cursor()
        cur.execute("""
            SELECT ps.MaLichDat, ps.MaBieuGia, ps.GioBatDau, l.GioKetThuc
            FROM PhienSac ps
            LEFT JOIN LichDatCho l ON ps.MaLichDat = l.MaLichDat
            WHERE ps.MaPhien=?
        """, (ma_phien,))
        phien = cur.fetchone()
        if not phien:
            conn.close()
            return
        ma_lich, ma_bg, gio_bat_dau_str, gio_ket_thuc_lich_str = phien

        # Tính số giờ đã sạc
        try:
            gio_bat_dau = datetime.strptime(gio_bat_dau_str, "%Y-%m-%d %H:%M:%S")
        except:
            gio_bat_dau = now

        # Xác định mốc kết thúc sạc (tự động ngắt khi hết giờ hẹn sạc)
        actual_end = now
        if gio_ket_thuc_lich_str:
            try:
                gio_ket_thuc_lich = datetime.strptime(gio_ket_thuc_lich_str, "%Y-%m-%d %H:%M:%S")
                if now > gio_ket_thuc_lich:
                    actual_end = gio_ket_thuc_lich
            except Exception:
                pass

        elapsed_hours = max((actual_end - gio_bat_dau).total_seconds() / 3600, 0.01)
        now_str = actual_end.strftime("%Y-%m-%d %H:%M:%S")

        # Lấy công suất cổng sạc (kW) để tính kWh
        cong_suat = 7.0  # mặc định 7kW
        if ma_lich:
            cur.execute("SELECT MaCong FROM LichDatCho WHERE MaLichDat=?", (ma_lich,))
            cong_row = cur.fetchone()
            if cong_row:
                cur.execute("SELECT CongSuat FROM CONG_SAC WHERE MaCong=?", (cong_row[0],))
                cs = cur.fetchone()
                if cs:
                    cong_suat = float(cs[0])

        kwh = round(elapsed_hours * cong_suat, 2)

        # Lấy đơn giá
        cur.execute("SELECT DonGiaKwh FROM BieuGiaDien WHERE MaBieuGia=?", (ma_bg,))
        gia = cur.fetchone()
        don_gia = float(gia[0]) if gia else 3000.0

        tong_tien = round(kwh * don_gia, 2)
        phi_app = round(tong_tien * 0.05, 2)
        doanh_thu = round(tong_tien * 0.95, 2)
        conn.close()

        # Xác nhận trước khi ngắt
        elapsed_min = int(elapsed_hours * 60)
        msg = (
            f"⏱ Thời gian sạc: {elapsed_min} phút\n"
            f"⚡ Công suất cổng: {cong_suat} kW\n"
            f"🔋 Điện tiêu thụ: {kwh} kWh\n"
            f"💰 Đơn giá: {int(don_gia):,} đ/kWh\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"💵 Tổng tiền: {int(tong_tien):,} đ\n\n"
            f"Bạn có muốn ngắt kết nối và chuyển sang thanh toán?"
        )
        reply = QMessageBox.question(
            self, "Xác nhận ngắt kết nối",
            msg,
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply != QMessageBox.StandardButton.Yes:
            return

        # Thực hiện ngắt kết nối
        conn = get_conn()
        cur = conn.cursor()

        cur.execute("""
            UPDATE PhienSac SET GioKetThuc=?, SoKwhTieuThu=?, TrangThaiPhien='Hoàn thành'
            WHERE MaPhien=?
        """, (now_str, kwh, ma_phien))

        ma_kh = self.user["MaNguoiDung"]
        cur.execute("SELECT COUNT(*) FROM HoaDon")
        n_hd = cur.fetchone()[0]
        ma_hd = f"HD{n_hd+1:03d}"

        # Kiểm tra tự động quy đổi điểm xanh
        points_needed = int((tong_tien * 0.05) / 1000)
        cur.execute("SELECT DiemXanh FROM KHACH_HANG WHERE MaNguoiDung=?", (ma_kh,))
        kh_row = cur.fetchone()
        diem_hien_tai = kh_row[0] if kh_row else 0

        so_diem_tieu_thu = 0
        so_tien_giam = 0
        tong_tien_thanh_toan = tong_tien

        if points_needed > 0 and diem_hien_tai >= points_needed:
            so_diem_tieu_thu = points_needed
            so_tien_giam = points_needed * 1000
            tong_tien_thanh_toan = tong_tien - so_tien_giam
            phi_app = round(tong_tien_thanh_toan * 0.05, 2)
            doanh_thu = round(tong_tien_thanh_toan * 0.95, 2)
            cur.execute("UPDATE KHACH_HANG SET DiemXanh = DiemXanh - ? WHERE MaNguoiDung=?", (points_needed, ma_kh))

        cur.execute("""
            INSERT INTO HoaDon
            (MaHD, MaPhien, MaNguoiDung, TongTienGoc, SoDiemTieuThu, SoTienGiam,
             TongTienThanhToan, PhiVanHanhApp, DoanhThuCDT, TrangThaiHD, NgayThanhToan, PhuongThucThanhToan)
            VALUES (?,?,?,?,?,?,?,?,?,'Chưa thanh toán',?,'Tiền mặt')
        """, (ma_hd, ma_phien, ma_kh, tong_tien, so_diem_tieu_thu, so_tien_giam,
              tong_tien_thanh_toan, phi_app, doanh_thu, now_str))

        if ma_lich:
            cur.execute("SELECT MaCong FROM LichDatCho WHERE MaLichDat=?", (ma_lich,))
            cong = cur.fetchone()
            if cong:
                cur.execute("UPDATE CONG_SAC SET TrangThaiCong='Trống' WHERE MaCong=?", (cong[0],))
            cur.execute("UPDATE LichDatCho SET TrangThaiLich='Hoàn thành' WHERE MaLichDat=?", (ma_lich,))

        conn.commit()
        conn.close()

        msg_giam = ""
        if so_diem_tieu_thu > 0:
            msg_giam = f"🎁 Đã tự động dùng {so_diem_tieu_thu} điểm xanh để giảm {int(so_tien_giam):,} đ!\n"

        QMessageBox.information(
            self, "Ngắt kết nối thành công ✅",
            f"Phiên {ma_phien} đã kết thúc!\n\n"
            f"🔋 Tiêu thụ: {kwh} kWh\n"
            f"💵 Tổng tiền gốc: {int(tong_tien):,} đ\n"
            f"{msg_giam}"
            f"💰 Cần thanh toán: {int(tong_tien_thanh_toan):,} đ\n"
            f"📋 Hóa đơn: {ma_hd}\n\n"
            f"👉 Hệ thống đang tự động chuyển sang tab Hóa Đơn để bạn thanh toán."
        )
        self.load_data()
        self.switch_to_hoadon_tab()

    def switch_to_hoadon_tab(self):
        from PyQt6.QtWidgets import QTabWidget
        parent = self.parent()
        while parent:
            if isinstance(parent, QTabWidget):
                for i in range(parent.count()):
                    if "Hóa Đơn" in parent.tabText(i):
                        parent.setCurrentIndex(i)
                        return True
            parent = parent.parent()
        return False

    def auto_check_overtime_sessions(self, reload=True):
        role = self.user["VaiTro"]
        if role != "KhachHang":
            return False

        ma_kh = self.user["MaNguoiDung"]
        conn = get_conn()
        cur = conn.cursor()

        cur.execute("""
            SELECT ps.MaPhien, ps.GioBatDau, ps.MaBieuGia, l.MaLichDat, l.GioKetThuc, l.MaCong
            FROM PhienSac ps
            JOIN LichDatCho l ON ps.MaLichDat = l.MaLichDat
            JOIN Xe x ON l.MaXe = x.MaXe
            WHERE x.MaNguoiDung=?
              AND ps.TrangThaiPhien='Đang sạc'
        """, (ma_kh,))

        active_sessions = cur.fetchall()

        overtime_session = None
        from datetime import datetime
        now = datetime.now()

        for row in active_sessions:
            ma_phien, gio_bat_dau_str, ma_bg, ma_lich, gio_ket_thuc_lich_str, ma_cong = row
            try:
                gio_ket_thuc_lich = datetime.strptime(gio_ket_thuc_lich_str, "%Y-%m-%d %H:%M:%S")
                if now >= gio_ket_thuc_lich:
                    overtime_session = row
                    break
            except Exception:
                pass

        if not overtime_session:
            conn.close()
            return False

        ma_phien, gio_bat_dau_str, ma_bg, ma_lich, gio_ket_thuc_lich_str, ma_cong = overtime_session

        try:
            gio_bat_dau = datetime.strptime(gio_bat_dau_str, "%Y-%m-%d %H:%M:%S")
            gio_ket_thuc_lich = datetime.strptime(gio_ket_thuc_lich_str, "%Y-%m-%d %H:%M:%S")
        except Exception:
            conn.close()
            return False

        elapsed_hours = max((gio_ket_thuc_lich - gio_bat_dau).total_seconds() / 3600, 0.01)
        now_str = gio_ket_thuc_lich.strftime("%Y-%m-%d %H:%M:%S")

        # Lấy công suất
        cong_suat = 7.0
        cur.execute("SELECT CongSuat FROM CONG_SAC WHERE MaCong=?", (ma_cong,))
        cs = cur.fetchone()
        if cs:
            cong_suat = float(cs[0])

        kwh = round(elapsed_hours * cong_suat, 2)

        # Lấy đơn giá
        cur.execute("SELECT DonGiaKwh FROM BieuGiaDien WHERE MaBieuGia=?", (ma_bg,))
        gia = cur.fetchone()
        don_gia = float(gia[0]) if gia else 3000.0

        tong_tien = round(kwh * don_gia, 2)
        phi_app = round(tong_tien * 0.05, 2)
        doanh_thu = round(tong_tien * 0.95, 2)

        # Cập nhật phiên sạc
        cur.execute("""
            UPDATE PhienSac SET GioKetThuc=?, SoKwhTieuThu=?, TrangThaiPhien='Hoàn thành'
            WHERE MaPhien=?
        """, (now_str, kwh, ma_phien))

        # Sinh mã hóa đơn
        cur.execute("SELECT COUNT(*) FROM HoaDon")
        n_hd = cur.fetchone()[0]
        ma_hd = f"HD{n_hd+1:03d}"

        # Kiểm tra tự động quy đổi điểm xanh
        points_needed = int((tong_tien * 0.05) / 1000)
        cur.execute("SELECT DiemXanh FROM KHACH_HANG WHERE MaNguoiDung=?", (ma_kh,))
        kh_row = cur.fetchone()
        diem_hien_tai = kh_row[0] if kh_row else 0

        so_diem_tieu_thu = 0
        so_tien_giam = 0
        tong_tien_thanh_toan = tong_tien

        if points_needed > 0 and diem_hien_tai >= points_needed:
            so_diem_tieu_thu = points_needed
            so_tien_giam = points_needed * 1000
            tong_tien_thanh_toan = tong_tien - so_tien_giam
            phi_app = round(tong_tien_thanh_toan * 0.05, 2)
            doanh_thu = round(tong_tien_thanh_toan * 0.95, 2)
            cur.execute("UPDATE KHACH_HANG SET DiemXanh = DiemXanh - ? WHERE MaNguoiDung=?", (points_needed, ma_kh))

        cur.execute("""
            INSERT INTO HoaDon
            (MaHD, MaPhien, MaNguoiDung, TongTienGoc, SoDiemTieuThu, SoTienGiam,
             TongTienThanhToan, PhiVanHanhApp, DoanhThuCDT, TrangThaiHD, NgayThanhToan, PhuongThucThanhToan)
            VALUES (?,?,?,?,?,?,?,?,?,'Chưa thanh toán',?,'Tiền mặt')
        """, (ma_hd, ma_phien, ma_kh, tong_tien, so_diem_tieu_thu, so_tien_giam,
              tong_tien_thanh_toan, phi_app, doanh_thu, now_str))

        # Trả cổng về Trống
        cur.execute("UPDATE CONG_SAC SET TrangThaiCong='Trống' WHERE MaCong=?", (ma_cong,))

        # Hoàn thành lịch
        cur.execute("UPDATE LichDatCho SET TrangThaiLich='Hoàn thành' WHERE MaLichDat=?", (ma_lich,))

        conn.commit()
        conn.close()

        msg_giam = ""
        if so_diem_tieu_thu > 0:
            msg_giam = f"🎁 Đã tự động dùng {so_diem_tieu_thu} điểm xanh để giảm {int(so_tien_giam):,} đ!\n"

        QMessageBox.information(
            self, "Hệ thống tự động ngắt kết nối 🔌",
            f"Phiên sạc {ma_phien} đã tự động kết thúc do hết giờ đặt lịch!\n\n"
            f"🔋 Tiêu thụ: {kwh} kWh\n"
            f"💵 Tổng tiền gốc: {int(tong_tien):,} đ\n"
            f"{msg_giam}"
            f"💰 Cần thanh toán: {int(tong_tien_thanh_toan):,} đ\n"
            f"📋 Hóa đơn: {ma_hd}\n\n"
            f"👉 Hệ thống đang tự động chuyển sang tab Hóa Đơn để bạn thanh toán."
        )

        if reload:
            self.load_data()
            self.switch_to_hoadon_tab()

        return True

    def on_timer_timeout(self):
        # 1. Kiểm tra tự động ngắt phiên sạc quá hạn
        ended = self.auto_check_overtime_sessions(reload=False)
        if ended:
            self.load_data()
            self.switch_to_hoadon_tab()
            return

        # 2. Kiểm tra tự động hủy lịch đặt trễ > 15 phút
        cancelled = self.auto_check_late_bookings()
        if cancelled:
            self.load_data()

    def auto_check_late_bookings(self):
        conn = get_conn()
        cur = conn.cursor()
        from datetime import datetime, timedelta
        threshold = (datetime.now() - timedelta(minutes=15)).strftime("%Y-%m-%d %H:%M:%S")
        cur.execute("""
            SELECT MaLichDat, MaCong
            FROM LichDatCho
            WHERE TrangThaiLich IN ('Đã đặt', 'Đã xác nhận')
              AND GioBatDau < ?
        """, (threshold,))
        late_bookings = cur.fetchall()
        if not late_bookings:
            conn.close()
            return False
        for l_id, c_id in late_bookings:
            cur.execute("UPDATE LichDatCho SET TrangThaiLich='Đã hủy' WHERE MaLichDat=?", (l_id,))
            cur.execute("UPDATE CONG_SAC SET TrangThaiCong='Trống' WHERE MaCong=?", (c_id,))
        conn.commit()
        conn.close()
        return True

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

    def _btn_style(self, color=None): return btn_style(color)