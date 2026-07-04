import re
import os

# 1. Update lich.py
with open(r'd:\uiData\main\lich.py', 'r', encoding='utf-8') as f:
    content_lich = f.read()

# Add QLineEdit for filtering before cmb_tram
loc_tram_code = """
            self.txt_loc_tram = QLineEdit()
            self.txt_loc_tram.setPlaceholderText("🔍 Nhập tên hoặc địa chỉ trạm để lọc...")
            self.txt_loc_tram.setStyleSheet(self._input_style())
            self.txt_loc_tram.textChanged.connect(self.load_tram)
            
            form_layout.addRow("Lọc trạm:", self.txt_loc_tram)
            form_layout.addRow("Trạm sạc:", self.cmb_tram)
"""
content_lich = re.sub(r'form_layout\.addRow\("Trạm sạc:", self\.cmb_tram\)', loc_tram_code.strip('\n'), content_lich)

# Update load_tram
new_load_tram = """
    def load_tram(self):
        conn = get_conn()
        cur = conn.cursor()
        
        keyword = ""
        if hasattr(self, 'txt_loc_tram'):
            keyword = self.txt_loc_tram.text().strip()
            
        if keyword:
            cur.execute("SELECT MaTram, TenTram, DiaChi FROM TRAM_SAC WHERE TrangThaiHoatDong='Hoạt động' AND (TenTram LIKE ? OR DiaChi LIKE ?)", (f"%{keyword}%", f"%{keyword}%"))
        else:
            cur.execute("SELECT MaTram, TenTram, DiaChi FROM TRAM_SAC WHERE TrangThaiHoatDong='Hoạt động'")
            
        rows = cur.fetchall()
        conn.close()
        self.tram_data = rows
        self.cmb_tram.clear()
        for r in rows:
            self.cmb_tram.addItem(f"{r[1]} - {r[2]} ({r[0]})", r[0])
"""
content_lich = re.sub(r'    def load_tram\(self\):.*?            self\.cmb_tram\.addItem\(f"\{r\[1\]\} \(\{r\[0\]\}\)", r\[0\]\)', new_load_tram.strip('\n'), content_lich, flags=re.DOTALL)

with open(r'd:\uiData\main\lich.py', 'w', encoding='utf-8') as f:
    f.write(content_lich)


# 2. Update phiensac.py
with open(r'd:\uiData\main\phiensac.py', 'r', encoding='utf-8') as f:
    content_phien = f.read()

khach_ngat_button = """
            self.tbl_phien = self._make_table(cols)
            box_layout.addWidget(self.tbl_phien)
            
            btn_row = QHBoxLayout()
            btn_rf = QPushButton("🔄 Làm mới")
            btn_rf.setStyleSheet(self._btn_style("#0ea5e9"))
            btn_rf.clicked.connect(self.load_data)
            btn_row.addWidget(btn_rf)
            
            if role == "KhachHang":
                btn_ngat = QPushButton("⏹ Ngắt Kết Nối & Thanh Toán")
                btn_ngat.setStyleSheet(self._btn_style("#ef4444"))
                btn_ngat.clicked.connect(self.khach_ngat_ket_noi)
                btn_row.addWidget(btn_ngat)
            
            btn_row.addStretch()
            box_layout.addLayout(btn_row)
"""
content_phien = re.sub(r'            self\.tbl_phien = self\._make_table\(cols\).*?            box_layout\.addWidget\(btn_rf\)', khach_ngat_button.strip('\n'), content_phien, flags=re.DOTALL)

khach_ngat_method = """
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
        
        import random
        kwh = round(random.uniform(10.0, 30.0), 2)
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        conn = get_conn()
        cur = conn.cursor()
        cur.execute("SELECT MaLichDat, MaBieuGia FROM PhienSac WHERE MaPhien=?", (ma_phien,))
        phien = cur.fetchone()
        if not phien:
            conn.close()
            return
        ma_lich, ma_bg = phien

        cur.execute("SELECT DonGiaKwh FROM BieuGiaDien WHERE MaBieuGia=?", (ma_bg,))
        gia = cur.fetchone()
        don_gia = gia[0] if gia else 3000

        tong_tien = round(kwh * float(don_gia), 2)
        phi_app = round(tong_tien * 0.05, 2)
        doanh_thu = round(tong_tien * 0.95, 2)

        cur.execute(\"\"\"
            UPDATE PhienSac SET GioKetThuc=?, SoKwhTieuThu=?, TrangThaiPhien='Hoàn thành'
            WHERE MaPhien=?
        \"\"\", (now, kwh, ma_phien))

        ma_kh = self.user["MaNguoiDung"]
        cur.execute("SELECT COUNT(*) FROM HoaDon")
        n_hd = cur.fetchone()[0]
        ma_hd = f"HD{n_hd+1:03d}"
        cur.execute(\"\"\"
            INSERT INTO HoaDon
            (MaHD, MaPhien, MaNguoiDung, TongTienGoc, SoDiemTieuThu, SoTienGiam,
             TongTienThanhToan, PhiVanHanhApp, DoanhThuCDT, TrangThaiHD, NgayThanhToan, PhuongThucThanhToan)
            VALUES (?,?,?,?,0,0,?,?,?,'Chưa thanh toán',?,'Tiền mặt')
        \"\"\", (ma_hd, ma_phien, ma_kh, tong_tien, tong_tien, phi_app, doanh_thu, now))

        if ma_lich:
            cur.execute("SELECT MaCong FROM LichDatCho WHERE MaLichDat=?", (ma_lich,))
            cong = cur.fetchone()
            if cong:
                cur.execute("UPDATE CONG_SAC SET TrangThaiCong='Trống' WHERE MaCong=?", (cong[0],))
            cur.execute("UPDATE LichDatCho SET TrangThaiLich='Hoàn thành' WHERE MaLichDat=?", (ma_lich,))

        conn.commit()
        conn.close()
        
        QMessageBox.information(self, "Thành công", f"Đã ngắt kết nối phiên sạc!\\nTiêu thụ: {kwh} kWh.\\nVui lòng chuyển sang tab Hóa Đơn để thanh toán.")
        self.load_data()

    def _make_table"""

content_phien = content_phien.replace("    def _make_table", khach_ngat_method.strip('\n'))
with open(r'd:\uiData\main\phiensac.py', 'w', encoding='utf-8') as f:
    f.write(content_phien)


# 3. Update tramsac.py cho NhanVien ("thiết kế lại")
with open(r'd:\uiData\main\tramsac.py', 'r', encoding='utf-8') as f:
    content_tram = f.read()

nhanvien_layout = """
        elif role == "NhanVien":
            grp_tram = QGroupBox("Cập nhật trạng thái Trạm")
            grp_tram.setStyleSheet(self._group_style())
            lay_tram = QHBoxLayout(grp_tram)
            self.cmb_tt_tram = QComboBox()
            self.cmb_tt_tram.addItems(["Hoạt động", "Tạm ngừng", "Bảo trì"])
            self.cmb_tt_tram.setStyleSheet(self._combo_style())
            btn_tt = QPushButton("Cập nhật")
            btn_tt.setStyleSheet(self._btn_style("#f59e0b"))
            btn_tt.clicked.connect(self.update_tram_status)
            lay_tram.addWidget(self.cmb_tt_tram)
            lay_tram.addWidget(btn_tt)
            left_layout.addWidget(grp_tram)
"""
content_tram = re.sub(r'        elif role == "NhanVien":.*?            left_layout\.addLayout\(btn_row\)', nhanvien_layout.strip('\n'), content_tram, flags=re.DOTALL)

nhanvien_cong_layout = """
        if role == "NhanVien":
            grp_cong = QGroupBox("Cập nhật Cổng (Chọn cổng ở trên)")
            grp_cong.setStyleSheet(self._group_style())
            lay_cong = QHBoxLayout(grp_cong)
            self.cmb_tt_cong = QComboBox()
            self.cmb_tt_cong.addItems(["Trống", "Đang sạc", "Bảo trì", "Đang hỏng"])
            self.cmb_tt_cong.setStyleSheet(self._combo_style())
            btn_cong = QPushButton("Cập nhật")
            btn_cong.setStyleSheet(self._btn_style("#10b981"))
            btn_cong.clicked.connect(self.update_cong_status)
            lay_cong.addWidget(self.cmb_tt_cong)
            lay_cong.addWidget(btn_cong)
            right_layout.addWidget(grp_cong)
"""
content_tram = re.sub(r'        if role == "NhanVien":.*?            right_layout\.addLayout\(btn_row2\)', nhanvien_cong_layout.strip('\n'), content_tram, flags=re.DOTALL)

them_cong_btn = """
        if role in ["NhanVien", "ChuDauTu"]:
            btn_them_cong = QPushButton("➕ Thêm Cổng Sạc Mới")
            btn_them_cong.setStyleSheet(self._btn_style("#0ea5e9"))
            btn_them_cong.clicked.connect(self.them_cong)
            right_layout.addWidget(btn_them_cong)
"""
content_tram = content_tram.replace('        splitter.addWidget(right)', them_cong_btn + '\n        splitter.addWidget(right)')

them_cong_method = """
    def them_cong(self):
        row = self.tbl_tram.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Chưa chọn", "Vui lòng chọn một trạm để thêm cổng.")
            return
        ma_tram = self.tbl_tram.item(row, 0).text()
        
        from PyQt6.QtWidgets import QInputDialog
        chuan, ok1 = QInputDialog.getItem(self, "Thêm cổng", "Chuẩn sạc:", ["CCS2", "CHAdeMO", "Type 2", "GB/T"], 0, False)
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
        ma_cong = f"CS{n+1:03d}"
        
        cur.execute("INSERT INTO CONG_SAC (MaCong, MaTram, MaChuanSac, CongSuat, LoaiCaySac, TrangThaiCong) VALUES (?,?,?,?,?,?)", (ma_cong, ma_tram, ma_chuan, cong_suat, loai, 'Trống'))
        conn.commit()
        conn.close()
        QMessageBox.information(self, "Thành công", f"Đã thêm cổng {ma_cong} cho trạm {ma_tram}.")
        self.load_cong(ma_tram)

    def load_data"""

content_tram = content_tram.replace("    def load_data", them_cong_method.strip('\n'))

with open(r'd:\uiData\main\tramsac.py', 'w', encoding='utf-8') as f:
    f.write(content_tram)

print("Updates applied.")
