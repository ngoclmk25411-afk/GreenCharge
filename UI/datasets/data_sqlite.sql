-- Drop existing tables if they exist to start fresh
DROP TABLE IF EXISTS HoaDon;
DROP TABLE IF EXISTS PhienSac;
DROP TABLE IF EXISTS LichDatCho;
DROP TABLE IF EXISTS Xe;
DROP TABLE IF EXISTS LICH_SU_BAO_TRI;
DROP TABLE IF EXISTS PHIEU_THU_GOM;
DROP TABLE IF EXISTS CONG_SAC;
DROP TABLE IF EXISTS NHAN_VIEN;
DROP TABLE IF EXISTS TRAM_SAC;
DROP TABLE IF EXISTS CHUAN_SAC;
DROP TABLE IF EXISTS KHACH_HANG;
DROP TABLE IF EXISTS CHU_DAU_TU;
DROP TABLE IF EXISTS NGUOI_DUNG;
DROP TABLE IF EXISTS BieuGiaDien;
DROP TABLE IF EXISTS LOAI_PIN;

-- Create tables
CREATE TABLE NGUOI_DUNG (
    MaNguoiDung VARCHAR(10) NOT NULL PRIMARY KEY, 
    HoTen NVARCHAR(100) NOT NULL,
    Sdt VARCHAR(15) NOT NULL UNIQUE,
    Email VARCHAR(100) NOT NULL UNIQUE,
    VaiTro NVARCHAR(100) NOT NULL CHECK (VaiTro IN ('KhachHang', 'NhanVien', 'ChuDauTu')),
    MatKhau TEXT
);

CREATE TABLE KHACH_HANG (
    MaNguoiDung VARCHAR(10) NOT NULL PRIMARY KEY,
    DiemXanh INT NOT NULL DEFAULT 0 CHECK (DiemXanh >= 0),
    FOREIGN KEY (MaNguoiDung) REFERENCES NGUOI_DUNG(MaNguoiDung) ON DELETE CASCADE
);

CREATE TABLE CHU_DAU_TU (
    MaNguoiDung VARCHAR(10) NOT NULL PRIMARY KEY,
    TenDoiTac NVARCHAR(100) NOT NULL,
    SoDuDoanhThu DECIMAL(18,2) NOT NULL DEFAULT 0 CHECK (SoDuDoanhThu >= 0),
    FOREIGN KEY (MaNguoiDung) REFERENCES NGUOI_DUNG(MaNguoiDung) ON DELETE CASCADE
);

CREATE TABLE CHUAN_SAC (
    MaChuanSac VARCHAR(10) NOT NULL PRIMARY KEY,
    TenChuan NVARCHAR(50) NOT NULL UNIQUE,
    LoaiDongDien NVARCHAR(2) NOT NULL CHECK(LoaiDongDien IN ('AC','DC'))
);

CREATE TABLE TRAM_SAC (
    MaTram VARCHAR(10) NOT NULL PRIMARY KEY,
    TenTram NVARCHAR(100) NOT NULL,
    DiaChi NVARCHAR(255) NOT NULL,
    MaNguoiDung VARCHAR(10) NOT NULL,
    TrangThaiHoatDong NVARCHAR(20) NOT NULL CHECK(TrangThaiHoatDong IN ('Hoạt động','Tạm ngừng')),
    FOREIGN KEY (MaNguoiDung) REFERENCES CHU_DAU_TU(MaNguoiDung) ON DELETE CASCADE
);

CREATE TABLE NHAN_VIEN (
    MaNguoiDung VARCHAR(10) NOT NULL PRIMARY KEY,
    MaTram VARCHAR(10) NOT NULL,
    ChucVu NVARCHAR(50) NOT NULL,
    FOREIGN KEY (MaNguoiDung) REFERENCES NGUOI_DUNG(MaNguoiDung) ON DELETE CASCADE,
    FOREIGN KEY (MaTram) REFERENCES TRAM_SAC(MaTram) ON DELETE CASCADE
);

CREATE TABLE CONG_SAC (
    MaCong VARCHAR(10) NOT NULL PRIMARY KEY,
    MaTram VARCHAR(10) NOT NULL,
    MaChuanSac VARCHAR(10) NOT NULL,
    CongSuat DECIMAL(6,2) NOT NULL CHECK(CongSuat > 0),
    LoaiCaySac NVARCHAR(30) NOT NULL CHECK(LoaiCaySac IN ('AC','DC','Siêu nhanh')),
    TrangThaiCong NVARCHAR(20) NOT NULL CHECK(TrangThaiCong IN ('Trống','Đang sạc','Bảo trì','Đang hỏng')),
    FOREIGN KEY (MaTram) REFERENCES TRAM_SAC(MaTram) ON DELETE CASCADE,
    FOREIGN KEY (MaChuanSac) REFERENCES CHUAN_SAC(MaChuanSac) ON DELETE CASCADE
);

CREATE TABLE LOAI_PIN (
    MaLoaiPin VARCHAR(10) NOT NULL PRIMARY KEY,
    TenLoaiPin NVARCHAR(50) NOT NULL UNIQUE,
    HeSoQuyDoi DECIMAL(5,2) NOT NULL CHECK (HeSoQuyDoi > 0) 
);

CREATE TABLE PHIEU_THU_GOM (
    MaPhieu VARCHAR(10) NOT NULL PRIMARY KEY,
    MaNguoiDung_KH VARCHAR(10) NOT NULL,
    MaNguoiDung_NV VARCHAR(10) NOT NULL,
    MaLoaiPin VARCHAR(10) NOT NULL,
    KhoiLuong DECIMAL(6,2) NOT NULL CHECK (KhoiLuong > 0),
    DiemThuong INT NOT NULL CHECK (DiemThuong >= 0),
    NgayThuGom DATETIME NOT NULL,
    FOREIGN KEY (MaNguoiDung_KH) REFERENCES KHACH_HANG(MaNguoiDung) ON DELETE CASCADE,
    FOREIGN KEY (MaNguoiDung_NV) REFERENCES NHAN_VIEN(MaNguoiDung) ON DELETE CASCADE,
    FOREIGN KEY (MaLoaiPin) REFERENCES LOAI_PIN(MaLoaiPin) ON DELETE CASCADE
);

CREATE TABLE LICH_SU_BAO_TRI (
    MaBaoTri VARCHAR(10) NOT NULL PRIMARY KEY,
    MaCong VARCHAR(10) NOT NULL,
    MaNguoiDung VARCHAR(10) NOT NULL,
    NgayBaoTri DATETIME NOT NULL,
    NoiDungBaoTri NVARCHAR(255) NOT NULL,
    KetQua NVARCHAR(100) NOT NULL,
    FOREIGN KEY (MaCong) REFERENCES CONG_SAC(MaCong) ON DELETE CASCADE,
    FOREIGN KEY (MaNguoiDung) REFERENCES NHAN_VIEN(MaNguoiDung) ON DELETE CASCADE
);

CREATE TABLE BieuGiaDien (
    MaBieuGia VARCHAR(10) NOT NULL PRIMARY KEY,
    LoaiCaySac NVARCHAR(30) NOT NULL,
    KhungGio NVARCHAR(30) NOT NULL,
    GioBatDau TIME NOT NULL,
    GioKetThuc TIME NOT NULL,
    DonGiaKwh DECIMAL(10,2) NOT NULL CHECK (DonGiaKwh > 0),
    NgayApDung DATE NOT NULL,
    TrangThai NVARCHAR(20) NOT NULL CHECK (TrangThai IN ('Đang áp dụng', 'Ngừng áp dụng'))
);

CREATE TABLE Xe (
    MaXe VARCHAR(10) NOT NULL PRIMARY KEY,
    BienSo VARCHAR(15) NOT NULL UNIQUE,
    MaNguoiDung VARCHAR(10) NOT NULL,
    MaChuanSac VARCHAR(10) NOT NULL,
    FOREIGN KEY (MaNguoiDung) REFERENCES KHACH_HANG(MaNguoiDung) ON DELETE CASCADE,
    FOREIGN KEY (MaChuanSac) REFERENCES CHUAN_SAC(MaChuanSac) ON DELETE CASCADE
);

CREATE TABLE LichDatCho (
    MaLichDat VARCHAR(10) NOT NULL PRIMARY KEY,
    MaXe VARCHAR(10) NOT NULL,
    MaCong VARCHAR(10) NOT NULL,
    GioBatDau DATETIME NOT NULL,
    GioKetThuc DATETIME NOT NULL,
    TrangThaiLich NVARCHAR(20) NOT NULL CHECK (TrangThaiLich IN ('Đã đặt', 'Đang sạc', 'Đã hủy', 'Hoàn thành')),
    CHECK (GioKetThuc > GioBatDau),
    FOREIGN KEY (MaXe) REFERENCES Xe(MaXe) ON DELETE CASCADE,
    FOREIGN KEY (MaCong) REFERENCES CONG_SAC(MaCong) ON DELETE CASCADE
);

CREATE TABLE PhienSac (
    MaPhien VARCHAR(10) NOT NULL PRIMARY KEY,
    MaLichDat VARCHAR(10) NULL,
    GioBatDau DATETIME NOT NULL,
    GioKetThuc DATETIME NULL,
    SoKwhTieuThu DECIMAL(8,2) NULL CHECK (SoKwhTieuThu >= 0),
    TrangThaiPhien NVARCHAR(20) NOT NULL CHECK (TrangThaiPhien IN ('Đang sạc', 'Hoàn thành', 'Đã hủy')),
    MaBieuGia VARCHAR(10) NOT NULL,
    FOREIGN KEY (MaLichDat) REFERENCES LichDatCho(MaLichDat) ON DELETE SET NULL,
    FOREIGN KEY (MaBieuGia) REFERENCES BieuGiaDien(MaBieuGia) ON DELETE CASCADE
);

CREATE TABLE HoaDon (
    MaHD VARCHAR(10) NOT NULL PRIMARY KEY,
    MaPhien VARCHAR(10) NOT NULL UNIQUE,
    MaNguoiDung VARCHAR(10) NOT NULL,
    TongTienGoc DECIMAL(18,2) NOT NULL CHECK (TongTienGoc >= 0),
    SoDiemTieuThu INT NOT NULL DEFAULT 0 CHECK (SoDiemTieuThu >= 0),
    SoTienGiam DECIMAL(18,2) NOT NULL DEFAULT 0 CHECK (SoTienGiam >= 0),
    TongTienThanhToan DECIMAL(18,2) NOT NULL CHECK (TongTienThanhToan >= 0),
    PhiVanHanhApp DECIMAL(18,2) NOT NULL CHECK (PhiVanHanhApp >= 0),
    DoanhThuCDT DECIMAL(18,2) NOT NULL CHECK (DoanhThuCDT >= 0),
    TrangThaiHD NVARCHAR(20) NOT NULL CHECK (TrangThaiHD IN ('Chưa thanh toán', 'Đã thanh toán', 'Thất bại', 'Đã hoàn tiền')),
    NgayThanhToan DATETIME NOT NULL,
    PhuongThucThanhToan NVARCHAR(30) NOT NULL CHECK (PhuongThucThanhToan IN ('Tiền mặt', 'Chuyển khoản', 'Ví điện tử', 'Thẻ ngân hàng')),
    FOREIGN KEY (MaPhien) REFERENCES PhienSac(MaPhien) ON DELETE CASCADE,
    FOREIGN KEY (MaNguoiDung) REFERENCES KHACH_HANG(MaNguoiDung) ON DELETE CASCADE
);

-- Insert data
INSERT INTO NGUOI_DUNG (MaNguoiDung, HoTen, Sdt, Email, VaiTro) VALUES
('ND001', 'Nguyễn Văn An', '0901234567', 'an.nguyen@email.com', 'KhachHang'),
('ND002', 'Trần Thị Bình', '0912345678', 'binh.tran@email.com', 'KhachHang'),
('ND003', 'Lê Hoàng Cường', '0923456789', 'cuong.le@email.com', 'KhachHang'),
('ND004', 'Phạm Thị Dung', '0934567890', 'dung.pham@email.com', 'KhachHang'),
('ND005', 'Hoàng Minh Đức', '0945678901', 'duc.hoang@email.com', 'ChuDauTu'),
('ND006', 'Vũ Thành Long', '0956789012', 'long.vu@email.com', 'ChuDauTu'),
('ND007', 'Đặng Quang Trung', '0967890123', 'trung.dang@email.com', 'NhanVien'),
('ND008', 'Bùi Thị Hương', '0978901234', 'huong.bui@email.com', 'NhanVien'),
('ND009', 'Ngô Thị Lan', '0989012345', 'lan.ngo@email.com', 'NhanVien'),
('ND010', 'Trịnh Văn Khoa', '0990123456', 'khoa.trinh@email.com', 'KhachHang');

INSERT INTO KHACH_HANG (MaNguoiDung, DiemXanh) VALUES
('ND001', 350),
('ND002', 0),
('ND003', 120),
('ND004', 75),
('ND010', 500);

INSERT INTO CHU_DAU_TU VALUES
('ND005', 'Công ty TNHH GreenPark Investment', 45000000.00),
('ND006', 'Tập đoàn Smart Energy Vietnam', 128500000.00);

INSERT INTO CHUAN_SAC (MaChuanSac, TenChuan, LoaiDongDien) VALUES
('CS001', 'CCS2', 'DC'),
('CS002', 'Type 2', 'AC'),
('CS003', 'CHAdeMO', 'DC');

INSERT INTO TRAM_SAC (MaTram, TenTram, DiaChi, MaNguoiDung, TrangThaiHoatDong) VALUES
('TS001', 'Trạm sạc thông minh Landmark 81', '720A Điện Biên Phủ, Bình Thạnh, TP.HCM', 'ND005', 'Hoạt động'),
('TS002', 'Trạm sạc Vincom Center Đồng Khởi', '72 Lê Thánh Tôn, Quận 1, TP.HCM', 'ND005', 'Hoạt động'),
('TS003', 'Trạm sạc AEON Mall Bình Dương', 'Đại lộ Bình Dương, Thuận An, Bình Dương', 'ND006', 'Tạm ngừng');

INSERT INTO NHAN_VIEN VALUES
('ND007', 'TS001', 'Nhân viên quản lý trạm'),
('ND008', 'TS002', 'Kỹ thuật viên cổng sạc'),
('ND009', 'TS003', 'Nhân viên tiếp nhận thu gom pin');

INSERT INTO LOAI_PIN VALUES
('LP001', 'Pin Lithium-ion ô tô điện hỏng', 80.00),
('LP002', 'Pin LFP xe máy điện chai', 120.00),
('LP003', 'Pin xe đạp điện cũ gỉ sét', 150.00),
('LP004', 'Pin Hybrid NiMH xe ô tô cũ', 100.00),
('LP005', 'Ắc quy chì axit xe điện hỏng', 60.00);

INSERT INTO PHIEU_THU_GOM VALUES
('PG001', 'ND001', 'ND009', 'LP001', 5.20, 416, '2026-06-10 09:30:00'),
('PG002', 'ND002', 'ND007', 'LP002', 3.00, 360, '2026-06-12 14:00:00'),
('PG003', 'ND003', 'ND008', 'LP003', 2.50, 375, '2026-06-15 10:15:00'),
('PG004', 'ND004', 'ND009', 'LP004', 1.80, 180, '2026-06-18 16:45:00'),
('PG005', 'ND010', 'ND007', 'LP005', 4.00, 240, '2026-06-20 11:00:00');

INSERT INTO CONG_SAC (MaCong, MaTram, MaChuanSac, CongSuat, LoaiCaySac, TrangThaiCong) VALUES
('CG001', 'TS001', 'CS001', 120.00, 'Siêu nhanh', 'Trống'),
('CG002', 'TS001', 'CS002', 22.00, 'AC', 'Đang sạc'),
('CG003', 'TS002', 'CS001', 60.00, 'DC', 'Trống'),
('CG004', 'TS002', 'CS003', 50.00, 'DC', 'Bảo trì'),
('CG005', 'TS003', 'CS002', 22.00, 'AC', 'Đang hỏng');

INSERT INTO LICH_SU_BAO_TRI (MaBaoTri, MaCong, MaNguoiDung, NgayBaoTri, NoiDungBaoTri, KetQua) VALUES
('BT001', 'CG004', 'ND008', '2026-06-15 09:00:00', 'Kiểm tra bộ chuyển đổi nguồn', 'Đã sửa chữa'),
('BT002', 'CG005', 'ND009', '2026-06-18 14:30:00', 'Thay thế đầu cắm sạc', 'Đang chờ linh kiện'),
('BT003', 'CG002', 'ND007', '2026-06-22 10:15:00', 'Bảo trì định kỳ', 'Hoàn thành');

INSERT INTO BieuGiaDien (MaBieuGia, LoaiCaySac, KhungGio, GioBatDau, GioKetThuc, DonGiaKwh, NgayApDung, TrangThai) VALUES
('BG001', 'Siêu nhanh', 'Giờ cao điểm', '17:00:00', '20:00:00', 4500.00, '2026-01-01', 'Đang áp dụng'),
('BG002', 'Siêu nhanh', 'Giờ bình thường', '07:00:00', '17:00:00', 3800.00, '2026-01-01', 'Đang áp dụng'),
('BG003', 'Siêu nhanh', 'Giờ thấp điểm', '20:00:00', '07:00:00', 3100.00, '2026-01-01', 'Đang áp dụng'),
('BG004', 'DC', 'Giờ cao điểm', '17:00:00', '20:00:00', 3900.00, '2026-01-01', 'Đang áp dụng'),
('BG005', 'DC', 'Giờ bình thường', '07:00:00', '17:00:00', 3300.00, '2026-01-01', 'Đang áp dụng'),
('BG006', 'AC', 'Mọi khung giờ', '00:00:00', '23:59:59', 2800.00, '2026-01-01', 'Đang áp dụng');

INSERT INTO Xe (MaXe, BienSo, MaNguoiDung, MaChuanSac) VALUES
('XE001', '29A-12345', 'ND001', 'CS001'),
('XE002', '30F-67890', 'ND002', 'CS002'),
('XE003', '51G-55555', 'ND003', 'CS001'),
('XE004', '43H-99999', 'ND004', 'CS002');

-- Mock Reservations
INSERT INTO LichDatCho (MaLichDat, MaXe, MaCong, GioBatDau, GioKetThuc, TrangThaiLich) VALUES
('LD001', 'XE001', 'CG003', '2026-07-01 09:26:44', '2026-07-01 10:26:44', 'Đã hủy'),
('LD002', 'XE001', 'CG003', '2026-07-01 09:28:44', '2026-07-01 10:26:44', 'Đã đặt'),
('LD003', 'XE001', 'CG001', '2026-07-03 09:50:33', '2026-07-03 10:50:33', 'Hoàn thành'),
('LD004', 'XE001', 'CG001', '2026-07-03 10:02:22', '2026-07-03 11:02:22', 'Hoàn thành'),
('LD005', 'XE001', 'CG003', '2026-07-03 10:02:22', '2026-07-03 11:02:22', 'Đã đặt'),
('LD006', 'XE001', 'CG001', '2026-07-03 23:00:51', '2026-07-03 23:58:51', 'Đã đặt');

-- Mock Charging Sessions
INSERT INTO PhienSac (MaPhien, MaLichDat, GioBatDau, GioKetThuc, SoKwhTieuThu, TrangThaiPhien, MaBieuGia) VALUES
('PS001', 'LD003', '2026-07-03 09:50:33', '2026-07-03 10:45:00', 50.0, 'Hoàn thành', 'BG002'),
('PS002', 'LD004', '2026-07-03 10:02:22', '2026-07-03 11:00:00', 45.0, 'Hoàn thành', 'BG002');

-- Mock Invoices
INSERT INTO HoaDon (MaHD, MaPhien, MaNguoiDung, TongTienGoc, SoDiemTieuThu, SoTienGiam, TongTienThanhToan, PhiVanHanhApp, DoanhThuCDT, TrangThaiHD, NgayThanhToan, PhuongThucThanhToan) VALUES
('HD001', 'PS001', 'ND001', 190000.0, 0, 0.0, 190000.0, 9500.0, 180500.0, 'Đã thanh toán', '2026-07-03 10:50:00', 'Ví điện tử'),
('HD002', 'PS002', 'ND001', 171000.0, 0, 0.0, 171000.0, 8550.0, 162450.0, 'Chưa thanh toán', '2026-07-03 11:05:00', 'Tiền mặt');

