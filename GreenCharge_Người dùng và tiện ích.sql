create table Nguoidung (
	MaNguoiDung varchar(10) not null primary key, 
	HoTen nvarchar(100) not null,
	Sdt varchar(15) not null unique,
	Email varchar(100) not null unique,
	VaiTro nvarchar(100) not null check (VaiTro in (N'KhachHang', N'NhanVien', N'ChuDauTu')) )
create table Khachhang (
	MaNguoiDung varchar(10) not null primary key foreign key references Nguoidung(MaNguoiDung),
	DiemXanh int not null default 0 check (DiemXanh>=0) )
create table Chudautu (
	MaNguoiDung varchar(10) not null primary key foreign key references Nguoidung(MaNguoiDung),
	TenDoiTac nvarchar(100) not null,
	SoDuDoanhThu decimal(18,2) not null default 0 check (SoDuDoanhThu>=0) )

--- Bảng Tramsac được tạo trước (rút gọn) để Nhanvien có thể tham chiếu MaTram
--- (Tramsac đầy đủ thuộc nhóm Quản lý Hạ tầng, không nằm trong 2 nhóm yêu cầu lần này)
create table Tramsac (
	MaTram varchar(10) not null primary key,
	TenTram nvarchar(100) not null )

create table Nhanvien (
	MaNguoiDung varchar(10) not null primary key foreign key references Nguoidung(MaNguoiDung),
	MaTram varchar(10) not null foreign key references Tramsac(MaTram),
	ChucVu nvarchar(50) not null )

create table Loaipin (
	MaLoaiPin varchar(10) not null primary key,
	TenLoaiPin nvarchar(50) not null unique,
	HeSoQuyDoi decimal(5,2) not null check (HeSoQuyDoi>0) )

create table Phieuthugom (
	MaPhieu varchar(10) not null primary key,
	MaNguoiDung_KH varchar(10) not null foreign key references Khachhang(MaNguoiDung),
	MaNguoiDung_NV varchar(10) not null foreign key references Nhanvien(MaNguoiDung),
	MaLoaiPin varchar(10) not null foreign key references Loaipin(MaLoaiPin),
	KhoiLuong decimal(6,2) not null check (KhoiLuong>0),
	DiemThuong int not null check (DiemThuong>=0),
	NgayThuGom datetime not null )

--- chèn dữ liệu vào bảng
insert Nguoidung values
('ND001', N'Nguyễn Văn An', '0901234567', 'an.nguyen@email.com', N'KhachHang'),
('ND002', N'Trần Thị Bình', '0912345678', 'binh.tran@email.com', N'KhachHang'),
('ND003', N'Lê Hoàng Cường', '0923456789', 'cuong.le@email.com', N'KhachHang'),
('ND004', N'Phạm Thị Dung', '0934567890', 'dung.pham@email.com', N'KhachHang'),
('ND005', N'Hoàng Minh Đức', '0945678901', 'duc.hoang@email.com', N'ChuDauTu'),
('ND006', N'Vũ Thành Long', '0956789012', 'long.vu@email.com', N'ChuDauTu'),
('ND007', N'Đặng Quang Trung', '0967890123', 'trung.dang@email.com', N'NhanVien'),
('ND008', N'Bùi Thị Hương', '0978901234', 'huong.bui@email.com', N'NhanVien'),
('ND009', N'Ngô Thị Lan', '0989012345', 'lan.ngo@email.com', N'NhanVien'),
('ND010', N'Trịnh Văn Khoa', '0990123456', 'khoa.trinh@email.com', N'KhachHang')
--- xem kết quả
select*from Nguoidung
---
insert Khachhang values
('ND001', 350),
('ND002', 0),
('ND003', 120),
('ND004', 75),
('ND010', 500)
--- xem kết quả
select*from Khachhang
---
insert Chudautu values
('ND005', N'Công ty TNHH GreenPark Investment', 45000000.00),
('ND006', N'Tập đoàn Smart Energy Vietnam', 128500000.00)
--- xem kết quả
select*from Chudautu
---
insert Tramsac values
('TS001', N'Trạm sạc thông minh Landmark 81'),
('TS002', N'Trạm sạc Vincom Center Đồng Khởi'),
('TS003', N'Trạm sạc AEON Mall Bình Dương')
--- xem kết quả
select*from Tramsac
---
insert Nhanvien values
('ND007', 'TS001', N'Nhân viên quản lý trạm'),
('ND008', 'TS002', N'Kỹ thuật viên cổng sạc'),
('ND009', 'TS003', N'Nhân viên tiếp nhận thu gom pin')
--- xem kết quả
select*from Nhanvien
---
insert Loaipin values
('LP001', N'Pin Lithium-ion ô tô điện hỏng', 80.00),
('LP002', N'Pin LFP xe máy điện chai', 120.00),
('LP003', N'Pin xe đạp điện cũ gỉ sét', 150.00),
('LP004', N'Pin Hybrid NiMH xe ô tô cũ', 100.00),
('LP005', N'Ắc quy chì axit xe điện hỏng', 60.00)
--- xem kết quả
select*from Loaipin
---
insert Phieuthugom values
('PG001', 'ND001', 'ND009', 'LP001', 5.20, 416, '2026-06-10 09:30:00'),
('PG002', 'ND002', 'ND007', 'LP002', 3.00, 360, '2026-06-12 14:00:00'),
('PG003', 'ND003', 'ND008', 'LP003', 2.50, 375, '2026-06-15 10:15:00'),
('PG004', 'ND004', 'ND009', 'LP004', 1.80, 180, '2026-06-18 16:45:00'),
('PG005', 'ND010', 'ND007', 'LP005', 4.00, 240, '2026-06-20 11:00:00')
--- xem kết quả
select*from Phieuthugom