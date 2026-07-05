import sqlite3
from datetime import datetime
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTableWidget,
    QTableWidgetItem, QPushButton, QComboBox, QHeaderView,
    QMessageBox, QGroupBox, QDateTimeEdit, QFormLayout, QSplitter, QFrame, QLineEdit,
    QSizePolicy
)
from PyQt6.QtCore import Qt, QDateTime
from PyQt6.QtGui import QColor, QFont
from main.shared_theme import (
    GROUP_STYLE, TABLE_STYLE, COMBO_STYLE, INPUT_STYLE,
    DIALOG_STYLE, TITLE_STYLE, LBL_STYLE, btn_style, status_color, G1, G2, G_M, G_B, G_L
)


DB_PATH = "datasets/data.db"


def get_conn():
    return sqlite3.connect(DB_PATH)


class LichDatChoWidget(QWidget):
    def __init__(self, user_info, parent=None):
        super().__init__(parent)
        self.user = user_info
        self.setup_ui()
        self.load_data()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(16, 16, 16, 16)

        title = QLabel("📅 Quản lý Đặt Lịch Sạc")
        title.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        title.setStyleSheet("color: #059669;")
        layout.addWidget(title)

        role = self.user["VaiTro"]

        if role == "KhachHang":
            # Form đặt lịch
            form_box = QGroupBox("Đặt lịch mới")
            form_box.setStyleSheet(self._group_style())
            form_box.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
            form_layout = QFormLayout(form_box)
            form_layout.setSpacing(10)
            form_layout.setContentsMargins(16, 20, 16, 16)

            self.cmb_xe = QComboBox()
            self.cmb_xe.setStyleSheet(self._combo_style())
            self.cmb_xe.setMinimumHeight(38)
            self.cmb_tram = QComboBox()
            self.cmb_tram.setStyleSheet(self._combo_style())
            self.cmb_tram.setMinimumHeight(38)
            self.cmb_tram.currentIndexChanged.connect(self.load_cong)
            self.cmb_cong = QComboBox()
            self.cmb_cong.setStyleSheet(self._combo_style())
            self.cmb_cong.setMinimumHeight(38)

            self.dt_bat_dau = QDateTimeEdit(QDateTime.currentDateTime())
            self.dt_bat_dau.setDisplayFormat("yyyy-MM-dd HH:mm")
            self.dt_bat_dau.setStyleSheet(self._input_style())
            self.dt_bat_dau.setCalendarPopup(True)
            self.dt_bat_dau.setMinimumHeight(38)
            self.dt_bat_dau.dateTimeChanged.connect(self.on_start_time_changed)

            self.dt_ket_thuc = QDateTimeEdit(QDateTime.currentDateTime().addSecs(3600))
            self.dt_ket_thuc.setDisplayFormat("yyyy-MM-dd HH:mm")
            self.dt_ket_thuc.setStyleSheet(self._input_style())
            self.dt_ket_thuc.setCalendarPopup(True)
            self.dt_ket_thuc.setMinimumHeight(38)

            form_layout.addRow("Xe của bạn:", self.cmb_xe)
            form_layout.addRow("Trạm sạc:", self.cmb_tram)
            form_layout.addRow("Cổng sạc:", self.cmb_cong)
            form_layout.addRow("Giờ bắt đầu:", self.dt_bat_dau)
            form_layout.addRow("Giờ kết thúc:", self.dt_ket_thuc)

            btn_dat = QPushButton("✅ Đặt Lịch")
            btn_dat.setMinimumHeight(38)
            btn_dat.setStyleSheet(self._btn_style("#10b981"))
            btn_dat.clicked.connect(self.dat_lich)
            form_layout.addRow("", btn_dat)

            self.load_xe()
            self.load_tram()
            layout.addWidget(form_box)

            # Bảng lịch đã đặt
            list_box = QGroupBox("Lịch đã đặt")
            list_box.setStyleSheet(self._group_style())
            list_box.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
            list_layout = QVBoxLayout(list_box)
            list_layout.setContentsMargins(12, 20, 12, 12)
            list_layout.setSpacing(10)
            self.tbl_lich = self._make_table(["Mã Lịch", "Xe", "Cổng", "Bắt đầu", "Kết thúc", "Trạng thái"])
            list_layout.addWidget(self.tbl_lich, 1)

            btn_huy = QPushButton("❌ Hủy Lịch Đã Chọn")
            btn_huy.setMinimumHeight(38)
            btn_huy.setStyleSheet(self._btn_style("#ef4444"))
            btn_huy.clicked.connect(self.huy_lich)
            list_layout.addWidget(btn_huy)
            layout.addWidget(list_box, 1)

        else:
            # Staff / Investor: chỉ xem danh sách lịch đặt
            box = QGroupBox("Danh sách lịch đặt tại trạm")
            box.setStyleSheet(self._group_style())
            box.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
            box_layout = QVBoxLayout(box)
            box_layout.setContentsMargins(12, 20, 12, 12)
            box_layout.setSpacing(10)
            cols = ["Mã Lịch", "Biển Số Xe", "Khách Hàng", "Cổng", "Bắt đầu", "Kết thúc", "Trạng thái"]
            self.tbl_lich = self._make_table(cols)
            box_layout.addWidget(self.tbl_lich, 1)

            btn_row = QHBoxLayout()

            btn_refresh = QPushButton("🔄 Làm mới")
            btn_refresh.setMinimumHeight(38)
            btn_refresh.setStyleSheet(self._btn_style("#0ea5e9"))
            btn_refresh.clicked.connect(self.load_data)
            btn_row.addWidget(btn_refresh)

            if role == "NhanVien":
                btn_xn = QPushButton("✔ Xác nhận khách")
                btn_xn.setMinimumHeight(38)
                btn_xn.setStyleSheet(self._btn_style("#10b981"))
                btn_xn.clicked.connect(self.xac_nhan_khach)
                btn_row.addWidget(btn_xn)

                btn_start = QPushButton("▶ Bắt đầu sạc")
                btn_start.setMinimumHeight(38)
                btn_start.setStyleSheet(self._btn_style("#f59e0b"))
                btn_start.clicked.connect(self.bat_dau_sac)
                btn_row.addWidget(btn_start)

            btn_row.addStretch()

            box_layout.addLayout(btn_row)
            layout.addWidget(box, 1)

    def on_start_time_changed(self, dt):
        self.dt_ket_thuc.setDateTime(dt.addSecs(3600))

    def load_xe(self):
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("SELECT MaXe, BienSo FROM Xe WHERE MaNguoiDung=?", (self.user["MaNguoiDung"],))
        rows = cur.fetchall()
        conn.close()
        self.xe_data = rows
        self.cmb_xe.clear()
        for r in rows:
            self.cmb_xe.addItem(f"{r[1]} ({r[0]})", r[0])

    def load_tram(self):
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("SELECT MaTram, TenTram, DiaChi FROM TRAM_SAC WHERE TrangThaiHoatDong='Hoạt động'")
        rows = cur.fetchall()
        conn.close()
        self.tram_data = rows
        self.cmb_tram.clear()
        for r in rows:
            self.cmb_tram.addItem(f"{r[1]} - {r[2]} ({r[0]})", r[0])

    def load_cong(self):
        ma_tram = self.cmb_tram.currentData()
        if not ma_tram:
            return

        conn = get_conn()
        cur = conn.cursor()

        cur.execute("""
            SELECT
                cs.MaCong,
                ch.TenChuan,
                cs.LoaiCaySac
            FROM CONG_SAC cs
            JOIN CHUAN_SAC ch
                ON cs.MaChuanSac = ch.MaChuanSac
            WHERE
                cs.MaTram = ?
                AND cs.TrangThaiCong = 'Trống'
            ORDER BY cs.MaCong
        """, (ma_tram,))

        rows = cur.fetchall()
        conn.close()

        self.cmb_cong.clear()

        if not rows:
            self.cmb_cong.addItem("Không còn cổng trống", None)
            return

        for ma_cong, chuan, loai in rows:
            self.cmb_cong.addItem(
                f"{ma_cong} | {chuan} | {loai}",
                ma_cong
            )

    def dat_lich(self):
        if self.cmb_xe.count() == 0:
            QMessageBox.warning(self, "Lỗi", "Bạn chưa đăng ký xe.")
            return

        if self.cmb_cong.count() == 0:
            QMessageBox.warning(self, "Lỗi", "Không còn cổng sạc khả dụng.")
            return

        ma_xe = self.cmb_xe.currentData()
        ma_cong = self.cmb_cong.currentData()

        if not ma_xe:
            QMessageBox.warning(self, "Lỗi", "Vui lòng chọn xe hợp lệ.")
            return

        if not ma_cong:
            QMessageBox.warning(self, "Lỗi", "Vui lòng chọn cổng sạc hợp lệ.")
            return

        bd = self.dt_bat_dau.dateTime().toPyDateTime()
        kt = self.dt_ket_thuc.dateTime().toPyDateTime()

        if kt <= bd:
            QMessageBox.warning(self, "Lỗi", "Giờ kết thúc phải lớn hơn giờ bắt đầu.")
            return

        conn = get_conn()
        cur = conn.cursor()

        try:
            # kiểm tra xe trùng lịch
            cur.execute("""
            SELECT COUNT(*)
            FROM LichDatCho
            WHERE MaXe=?
            AND TrangThaiLich IN ('Đã đặt','Đã xác nhận','Đang sạc')
            AND (
                (? BETWEEN GioBatDau AND GioKetThuc)
                OR
                (? BETWEEN GioBatDau AND GioKetThuc)
                OR
                (GioBatDau BETWEEN ? AND ?)
            )
            """,
                        (
                            ma_xe,
                            bd.strftime("%Y-%m-%d %H:%M:%S"),
                            kt.strftime("%Y-%m-%d %H:%M:%S"),
                            bd.strftime("%Y-%m-%d %H:%M:%S"),
                            kt.strftime("%Y-%m-%d %H:%M:%S")
                        ))

            if cur.fetchone()[0] > 0:
                QMessageBox.warning(self, "Lỗi", "Xe đã có lịch trong khoảng thời gian này.")
                return

            # kiểm tra cổng trùng lịch
            cur.execute("""
            SELECT COUNT(*)
            FROM LichDatCho
            WHERE MaCong=?
            AND TrangThaiLich IN ('Đã đặt','Đã xác nhận','Đang sạc')
            AND (
                (? BETWEEN GioBatDau AND GioKetThuc)
                OR
                (? BETWEEN GioBatDau AND GioKetThuc)
                OR
                (GioBatDau BETWEEN ? AND ?)
            )
            """,
                        (
                            ma_cong,
                            bd.strftime("%Y-%m-%d %H:%M:%S"),
                            kt.strftime("%Y-%m-%d %H:%M:%S"),
                            bd.strftime("%Y-%m-%d %H:%M:%S"),
                            kt.strftime("%Y-%m-%d %H:%M:%S")
                        ))

            if cur.fetchone()[0] > 0:
                QMessageBox.warning(self, "Lỗi", "Cổng sạc đã được đặt.")
                return

            # sinh mã lịch
            cur.execute("""
                SELECT IFNULL(MAX(CAST(SUBSTR(MaLichDat,3) AS INTEGER)),0)
                FROM LichDatCho
            """)

            stt = cur.fetchone()[0] + 1
            ma_lich = f"LD{stt:03d}"

            cur.execute("""
                INSERT INTO LichDatCho
                (
                    MaLichDat,
                    MaXe,
                    MaCong,
                    GioBatDau,
                    GioKetThuc,
                    TrangThaiLich
                )
                VALUES (?,?,?,?,?,?)
            """,
                        (
                            ma_lich,
                            ma_xe,
                            ma_cong,
                            bd.strftime("%Y-%m-%d %H:%M:%S"),
                            kt.strftime("%Y-%m-%d %H:%M:%S"),
                            "Đã đặt"
                        ))

            conn.commit()
            QMessageBox.information(
                self,
                "Thành công",
                f"Đặt lịch {ma_lich} thành công."
            )
            self.load_cong()
            self.load_data()
        except Exception as e:
            conn.rollback()
            QMessageBox.critical(self, "Lỗi", f"Không thể đặt lịch: {e}")
        finally:
            conn.close()

    def huy_lich(self):
        row = self.tbl_lich.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Chưa chọn", "Vui lòng chọn một lịch để hủy.")
            return
        ma_lich = self.tbl_lich.item(row, 0).text()
        trang_thai = self.tbl_lich.item(row, 5).text()
        if trang_thai not in ("Đã đặt", "Đã xác nhận"):
            QMessageBox.warning(self, "Không thể hủy", f"Lịch đang ở trạng thái '{trang_thai}', không thể hủy.")
            return

        reply = QMessageBox.question(self, "Xác nhận hủy", f"Hủy lịch {ma_lich}?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            conn = get_conn()
            cur = conn.cursor()
            try:
                # Lấy cổng của lịch
                cur.execute("""
                    SELECT MaCong
                    FROM LichDatCho
                    WHERE MaLichDat=?
                """, (ma_lich,))
                result = cur.fetchone()

                if result:
                    ma_cong = result[0]

                    # Hủy lịch
                    cur.execute("""
                        UPDATE LichDatCho
                        SET TrangThaiLich='Đã hủy'
                        WHERE MaLichDat=?
                    """, (ma_lich,))

                    # Trả cổng về trạng thái Trống
                    cur.execute("""
                        UPDATE CONG_SAC
                        SET TrangThaiCong='Trống'
                        WHERE MaCong=?
                    """, (ma_cong,))

                conn.commit()
                QMessageBox.information(
                    self,
                    "Đã hủy",
                    f"Lịch {ma_lich} đã được hủy."
                )
                self.load_data()
            except Exception as e:
                conn.rollback()
                QMessageBox.critical(self, "Lỗi", f"Không thể hủy lịch: {e}")
            finally:
                conn.close()

    def load_data(self):
        conn = get_conn()
        cur = conn.cursor()
        role = self.user["VaiTro"]
        ma = self.user["MaNguoiDung"]

        if role == "KhachHang":
            cur.execute("""
                SELECT l.MaLichDat, x.BienSo, l.MaCong, l.GioBatDau, l.GioKetThuc, l.TrangThaiLich
                FROM LichDatCho l
                JOIN Xe x ON l.MaXe = x.MaXe
                WHERE x.MaNguoiDung=?
                ORDER BY l.GioBatDau DESC
            """, (ma,))
            rows = cur.fetchall()
            self.tbl_lich.setRowCount(len(rows))
            color_map = {
                "Đã đặt": "#3b82f6",
                "Đã xác nhận": "#3b82f6",
                "Đã đến": "#8b5cf6",
                "Đang sạc": "#10b981",
                "Hoàn thành": "#64748b",
                "Đã hủy": "#ef4444"
            }
            for i, row in enumerate(rows):
                for j, val in enumerate(row):
                    item = QTableWidgetItem(str(val))
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    if j == 5:
                        item.setForeground(QColor(color_map.get(val, "#374151")))
                    self.tbl_lich.setItem(i, j, item)

        elif role == "NhanVien":
            cur.execute("SELECT MaTram FROM NHAN_VIEN WHERE MaNguoiDung=?", (ma,))
            r = cur.fetchone()
            if not r:
                conn.close()
                return
            ma_tram = r[0]
            cur.execute("""
                SELECT l.MaLichDat, x.BienSo, nd.HoTen, l.MaCong, l.GioBatDau, l.GioKetThuc, l.TrangThaiLich
                FROM LichDatCho l
                JOIN Xe x ON l.MaXe = x.MaXe
                JOIN NGUOI_DUNG nd ON x.MaNguoiDung = nd.MaNguoiDung
                JOIN CONG_SAC cs ON l.MaCong = cs.MaCong
                WHERE cs.MaTram=?
                ORDER BY l.GioBatDau DESC
            """, (ma_tram,))
            rows = cur.fetchall()
            self.tbl_lich.setRowCount(len(rows))
            for i, row in enumerate(rows):
                for j, val in enumerate(row):
                    item = QTableWidgetItem(str(val))
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    self.tbl_lich.setItem(i, j, item)

        elif role == "ChuDauTu":
            cur.execute("""
                SELECT l.MaLichDat, x.BienSo, nd.HoTen, l.MaCong, l.GioBatDau, l.GioKetThuc, l.TrangThaiLich
                FROM LichDatCho l
                JOIN Xe x ON l.MaXe = x.MaXe
                JOIN NGUOI_DUNG nd ON x.MaNguoiDung = nd.MaNguoiDung
                JOIN CONG_SAC cs ON l.MaCong = cs.MaCong
                JOIN TRAM_SAC ts ON cs.MaTram = ts.MaTram
                WHERE ts.MaNguoiDung=?
                ORDER BY l.GioBatDau DESC
            """, (ma,))
            rows = cur.fetchall()
            self.tbl_lich.setRowCount(len(rows))
            for i, row in enumerate(rows):
                for j, val in enumerate(row):
                    item = QTableWidgetItem(str(val))
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    self.tbl_lich.setItem(i, j, item)

        conn.close()

    def xac_nhan_khach(self):

        row = self.tbl_lich.currentRow()

        if row < 0:
            QMessageBox.warning(self, "Thông báo", "Chọn một lịch.")
            return

        ma_lich = self.tbl_lich.item(row, 0).text()

        tt = self.tbl_lich.item(row, 6).text()

        if tt != "Đã xác nhận":
            QMessageBox.warning(
                self,
                "Thông báo",
                "Chỉ xác nhận lịch đang ở trạng thái Đã xác nhận."
            )
            return

        conn = get_conn()
        cur = conn.cursor()

        cur.execute("""
            UPDATE LichDatCho
            SET TrangThaiLich='Đã đến'
            WHERE MaLichDat=?
        """, (ma_lich,))

        conn.commit()
        conn.close()

        QMessageBox.information(
            self,
            "Thành công",
            "Khách đã check in."
        )

        self.load_data()

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
        tbl.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        return tbl

    def bat_dau_sac(self):

        row = self.tbl_lich.currentRow()

        if row < 0:
            QMessageBox.warning(
                self,
                "Thông báo",
                "Chọn một lịch."
            )
            return

        ma_lich = self.tbl_lich.item(row, 0).text()

        trang_thai = self.tbl_lich.item(row, 6).text()

        if trang_thai != "Đã đến":
            QMessageBox.warning(
                self,
                "Thông báo",
                "Khách chưa check in."
            )
            return

        conn = get_conn()

        cur = conn.cursor()

        cur.execute("""
            SELECT
                MaCong
            FROM
                LichDatCho
            WHERE
                MaLichDat=?
        """, (ma_lich,))

        ma_cong = cur.fetchone()[0]

        # Get charging type
        cur.execute("SELECT LoaiCaySac FROM CONG_SAC WHERE MaCong=?", (ma_cong,))
        cong_row = cur.fetchone()
        loai_cay_sac = cong_row[0] if cong_row else "AC"

        # Find matching bieu gia
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

        cur.execute("""
            SELECT
            IFNULL(MAX(CAST(substr(MaPhien,3) AS INTEGER)),0)
            FROM
            PhienSac
        """)

        stt = cur.fetchone()[0] + 1

        ma_phien = f"PS{stt:03d}"

        cur.execute("""
            INSERT INTO PhienSac
            (
                MaPhien,
                MaLichDat,
                GioBatDau,
                TrangThaiPhien,
                MaBieuGia
            )
            VALUES
            (
                ?,
                ?,
                datetime('now', 'localtime'),
                'Đang sạc',
                ?
            )
        """, (ma_phien, ma_lich, ma_bg))

        cur.execute("""
            UPDATE LichDatCho
            SET TrangThaiLich='Đang sạc'
            WHERE MaLichDat=?
        """, (ma_lich,))

        cur.execute("""
            UPDATE CONG_SAC
            SET TrangThaiCong='Đang sạc'
            WHERE MaCong=?
        """, (ma_cong,))

        conn.commit()

        conn.close()

        QMessageBox.information(
            self,
            "Thành công",
            f"Đã tạo phiên {ma_phien}"
        )

        self.load_data()

    def _group_style(self): return GROUP_STYLE

    def _table_style(self): return TABLE_STYLE

    def _combo_style(self): return COMBO_STYLE

    def _input_style(self): return INPUT_STYLE

    def _btn_style(self, color=None): return btn_style(color)