-- 1. XÓA CÁC BẢNG CHỨA KHÓA NGOẠI (BẢNG CON) TRƯỚC
DROP TABLE IF EXISTS HOA_DON;
DROP TABLE IF EXISTS PHIEN_SAC;
DROP TABLE IF EXISTS LICH_DAT_CHO;
DROP TABLE IF EXISTS XE;
DROP TABLE IF EXISTS LICH_SU_BAO_TRI;
DROP TABLE IF EXISTS PHIEU_THU_GOM;
DROP TABLE IF EXISTS CONG_SAC;
DROP TABLE IF EXISTS NHAN_VIEN;
DROP TABLE IF EXISTS LOAI_PIN;

-- 2. XÓA CÁC BẢNG GỐC (BẢNG CHA) SAU
DROP TABLE IF EXISTS TRAM_SAC;
DROP TABLE IF EXISTS CHUAN_SAC;
DROP TABLE IF EXISTS KHACH_HANG;
DROP TABLE IF EXISTS CHU_DAU_TU;
DROP TABLE IF EXISTS NGUOI_DUNG;
DROP TABLE IF EXISTS BieuGiaDien;
GO
--- Tạo bảng
create table NGUOI_DUNG 
(
	MaNguoiDung varchar(10) not null primary key, 
	HoTen nvarchar(100) not null,
	Sdt varchar(15) not null unique,
	Email varchar(100) not null unique,
	MatKhau varchar (255) not null,
	VaiTro nvarchar(20) not null check (VaiTro in (N'KhachHang', N'NhanVien', N'ChuDauTu'))
);
create table KHACH_HANG 
(
	MaNguoiDung varchar(10) not null primary key foreign key references NGUOI_DUNG(MaNguoiDung),
	DiemXanh int not null default 0 check (DiemXanh>=0) 
);
create table CHU_DAU_TU 
(
	MaNguoiDung varchar(10) not null primary key foreign key references NGUOI_DUNG(MaNguoiDung),
	TenDoiTac nvarchar(100) not null,
	SoDuDoanhThu decimal(18,2) not null default 0 check (SoDuDoanhThu>=0) 
);
create table CHUAN_SAC
(
	MaChuanSac varchar(10) not null primary key,
	TenChuan nvarchar(50) not null unique,
	LoaiDongDien nvarchar(2) not null, check(LoaiDongDien in (N'AC',N'DC'))
);
create table TRAM_SAC
(
	MaTram varchar(10) not null primary key,
	TenTram nvarchar(100) not null,
	DiaChi nvarchar(255) not null,
	MaNguoiDung varchar(10) not null foreign key references CHU_DAU_TU(MaNguoiDung),
	TrangThaiHoatDong nvarchar(20) not null, check(TrangThaiHoatDong in (N'Hoạt động',N'Tạm ngừng'))
);
create table NHAN_VIEN 
(
	MaNguoiDung varchar(10) not null primary key foreign key references NGUOI_DUNG(MaNguoiDung),
	MaTram varchar(10) not null foreign key references TRAM_SAC(MaTram),
	ChucVu nvarchar(50) not null
);
create table CONG_SAC
(
	MaCong varchar(10) not null primary key,
	MaTram varchar(10) not null foreign key references TRAM_SAC(MaTram),
	MaChuanSac varchar(10) not null foreign key references CHUAN_SAC(MaChuanSac),
	CongSuat decimal(6,2) not null check(CongSuat>0),
	LoaiCaySac nvarchar(30) not null check(LoaiCaySac in (N'AC',N'DC',N'Siêu nhanh')),
	TrangThaiCong nvarchar(20) not null check(TrangThaiCong in (N'Trống',N'Đang sạc',N'Bảo trì',N'Đang hỏng'))
);
create table LOAI_PIN 
(
	MaLoaiPin varchar(10) not null primary key,
	TenLoaiPin nvarchar(50) not null unique,
	HeSoQuyDoi decimal(5,2) not null check (HeSoQuyDoi>0) 
);
create table PHIEU_THU_GOM
(
	MaPhieu varchar(10) not null primary key,
	MaNguoiDung_KH varchar(10) not null foreign key references KHACH_HANG(MaNguoiDung),
	MaNguoiDung_NV varchar(10) not null foreign key references NHAN_VIEN(MaNguoiDung),
	MaLoaiPin varchar(10) not null foreign key references LOAI_PIN(MaLoaiPin),
	KhoiLuong decimal(6,2) not null check (KhoiLuong>0),
	DiemThuong int not null check (DiemThuong>=0),
	NgayThuGom datetime not null
);
create table LICH_SU_BAO_TRI
(
	MaBaoTri varchar(10) not null primary key,
	MaCong varchar (10) not null foreign key references CONG_SAC(MaCong),
	MaNguoiDung varchar(10) not null foreign key references NHAN_VIEN(MaNguoiDung),
	NgayBaoTri datetime not null,
	NoiDungBaoTri nvarchar(255) not null,
	KetQua nvarchar(100) not null
);
create table BieuGiaDien (
    MaBieuGia varchar(10) not null primary key,
    LoaiCaySac nvarchar(30) not null,
    KhungGio nvarchar(30) not null,
    GioBatDau time not null,
    GioKetThuc time not null,
    DonGiaKwh decimal(10,2) not null check (DonGiaKwh > 0),
    NgayApDung date not null,
    TrangThai nvarchar(20) not null check (TrangThai in (N'Đang áp dụng', N'Ngừng áp dụng'))
);
create table XE (
    MaXe varchar(10) not null primary key,
    BienSo varchar(15) not null unique,
    MaNguoiDung varchar(10) not null foreign key references KHACH_HANG(MaNguoiDung),
    MaChuanSac varchar(10) not null foreign key references CHUAN_SAC(MaChuanSac)
);
create table LICH_DAT_CHO (
    MaLichDat varchar(10) not null primary key,
    MaXe varchar(10) not null foreign key references Xe(MaXe),
    MaCong varchar(10) not null foreign key references CONG_SAC(MaCong),
    GioBatDau datetime not null,
    GioKetThuc datetime not null,
    TrangThaiLich nvarchar(20) not null check (TrangThaiLich in (N'Đã đặt', N'Đang sạc', N'Đã hủy', N'Hoàn thành')),
    check (GioKetThuc > GioBatDau) -- Ràng buộc so sánh giữa 2 cột bắt buộc viết riêng cuối dòng định nghĩa thuộc tính
);
create table PHIEN_SAC (
    MaPhien varchar(10) not null primary key,
    MaLichDat varchar(10) null foreign key references LICH_DAT_CHO(MaLichDat),
    GioBatDau datetime not null,
    GioKetThuc datetime null,
    SoKwhTieuThu decimal(8,2) null check (SoKwhTieuThu >= 0),
    TrangThaiPhien nvarchar(20) not null check (TrangThaiPhien in (N'Đang sạc', N'Hoàn thành', N'Đã hủy')),
    MaBieuGia varchar(10) not null foreign key references BieuGiaDien(MaBieuGia)
);
create table HOA_DON (
    MaHD varchar(10) not null primary key,
    MaPhien varchar(10) not null unique foreign key references PHIEN_SAC(MaPhien),
    MaNguoiDung varchar(10) not null foreign key references KHACH_HANG(MaNguoiDung),
    TongTienGoc decimal(18,2) not null check (TongTienGoc >= 0),
    SoDiemTieuThu int not null default 0 check (SoDiemTieuThu >= 0),
    SoTienGiam decimal(18,2) not null default 0 check (SoTienGiam >= 0),
    TongTienThanhToan decimal(18,2) not null check (TongTienThanhToan >= 0),
    PhiVanHanhApp decimal(18,2) not null check (PhiVanHanhApp >= 0),
    DoanhThuCDT decimal(18,2) not null check (DoanhThuCDT >= 0),
    TrangThaiHD nvarchar(20) not null check (TrangThaiHD in (N'Chưa thanh toán', N'Đã thanh toán', N'Thất bại', N'Đã hoàn tiền')),
    NgayThanhToan datetime not null,
    PhuongThucThanhToan nvarchar(30) not null check (PhuongThucThanhToan in (N'Tiền mặt', N'Chuyển khoản', N'Ví điện tử', N'Thẻ ngân hàng'))
);
--- chèn dữ liệu vào bảng

insert NGUOI_DUNG values
('ND001', N'Nguyễn Văn An', '0901234567', 'an.nguyen@email.com','123456', N'KhachHang'),
('ND002', N'Trần Thị Bình', '0912345678', 'binh.tran@email.com', '123456', N'KhachHang'),
('ND003', N'Lê Hoàng Cường', '0923456789', 'cuong.le@email.com','123456', N'KhachHang'),
('ND004', N'Phạm Thị Dung', '0934567890', 'dung.pham@email.com','123456', N'KhachHang'),
('ND005', N'Hoàng Minh Đức', '0945678901', 'duc.hoang@email.com', '123456', N'ChuDauTu'),
('ND006', N'Vũ Thành Long', '0956789012', 'long.vu@email.com', '123456', N'ChuDauTu'),
('ND007', N'Đặng Quang Trung', '0967890123', 'trung.dang@email.com', '123456',N'NhanVien'),
('ND008', N'Bùi Thị Hương', '0978901234', 'huong.bui@email.com','123456', N'NhanVien'),
('ND009', N'Ngô Thị Lan', '0989012345', 'lan.ngo@email.com', '123456',N'NhanVien'),
('ND010', N'Trịnh Văn Khoa', '0990123456', 'khoa.trinh@email.com','123456', N'KhachHang');
select*from NGUOI_DUNG
---
insert KHACH_HANG (MaNguoiDung, DiemXanh) values
	('ND001', 350),
	('ND002', 0),
	('ND003', 120),
	('ND004', 75),
	('ND010', 500)
select*from KHACH_HANG
---
insert CHU_DAU_TU values
	('ND005', N'Công ty TNHH GreenPark Investment', 45000000.00),
	('ND006', N'Tập đoàn Smart Energy Vietnam', 128500000.00)
select*from CHU_DAU_TU
---
insert into CHUAN_SAC (MaChuanSac, TenChuan, LoaiDongDien) values
	('CS001', N'CCS2', N'DC'),
	('CS002', N'Type 2', N'AC'),
	('CS003', N'CHAdeMO', N'DC');
select * from CHUAN_SAC
---
insert into TRAM_SAC (MaTram, TenTram, DiaChi, MaNguoiDung, TrangThaiHoatDong) values
	('TS001',N'Trạm sạc thông minh Landmark 81',N'720A Điện Biên Phủ, Bình Thạnh, TP.HCM','ND005',N'Hoạt động'),
	('TS002',N'Trạm sạc Vincom Center Đồng Khởi',N'72 Lê Thánh Tôn, Quận 1, TP.HCM','ND005',N'Hoạt động'),
	('TS003',N'Trạm sạc AEON Mall Bình Dương',N'Đại lộ Bình Dương, Thuận An, Bình Dương','ND006',N'Tạm ngừng');
select*from TRAM_SAC
---
insert NHAN_VIEN values
	('ND007', 'TS001', N'Nhân viên quản lý trạm'),
	('ND008', 'TS002', N'Kỹ thuật viên cổng sạc'),
	('ND009', 'TS003', N'Nhân viên tiếp nhận thu gom pin')
select*from NHAN_VIEN
---
insert LOAI_PIN values
	('LP001', N'Pin Lithium-ion ô tô điện hỏng', 80.00),
	('LP002', N'Pin LFP xe máy điện chai', 120.00),
	('LP003', N'Pin xe đạp điện cũ gỉ sét', 150.00),
	('LP004', N'Pin Hybrid NiMH xe ô tô cũ', 100.00),
	('LP005', N'Ắc quy chì axit xe điện hỏng', 60.00)
select*from LOAI_PIN
---
insert PHIEU_THU_GOM values
	('PG001', 'ND001', 'ND009', 'LP001', 5.20, 416, '2026-06-10 09:30:00'),
	('PG002', 'ND002', 'ND007', 'LP002', 3.00, 360, '2026-06-12 14:00:00'),
	('PG003', 'ND003', 'ND008', 'LP003', 2.50, 375, '2026-06-15 10:15:00'),
	('PG004', 'ND004', 'ND009', 'LP004', 1.80, 180, '2026-06-18 16:45:00'),
	('PG005', 'ND010', 'ND007', 'LP005', 4.00, 240, '2026-06-20 11:00:00')
select*from PHIEU_THU_GOM
---
insert into CONG_SAC (MaCong, MaTram, MaChuanSac, CongSuat, LoaiCaySac, TrangThaiCong) values
	('CG001','TS001','CS001',120.00,N'Siêu nhanh',N'Trống'),
	('CG002','TS001','CS002',22.00,N'AC',N'Đang sạc'),
	('CG003','TS002','CS001',60.00,N'DC',N'Trống'),
	('CG004','TS002','CS003',50.00,N'DC',N'Bảo trì'),
	('CG005','TS003','CS002',22.00,N'AC',N'Đang hỏng');
select * from CONG_SAC
---
insert into LICH_SU_BAO_TRI (MaBaoTri, MaCong, MaNguoiDung, NgayBaoTri, NoiDungBaoTri, KetQua) values
	('BT001','CG004','ND008','2026-06-15 09:00:00',N'Kiểm tra bộ chuyển đổi nguồn',N'Đã sửa chữa'),
	('BT002','CG005','ND009','2026-06-18 14:30:00',N'Thay thế đầu cắm sạc',N'Đang chờ linh kiện'),
	('BT003','CG002','ND007','2026-06-22 10:15:00',N'Bảo trì định kỳ',N'Hoàn thành');
select * from LICH_SU_BAO_TRI

-- NHÓM: ĐẶT LỊCH & PHIÊN SẠC
-- câu 1: Khách hàng Nguyễn Văn An muốn xem tất cả các lịch đặt trong tháng 6 năm 2026
select
    ldc.MaLichDat,
    x.BienSo,
    ts.TenTram,
    cs.MaCong,
    ldc.GioBatDau,
    ldc.GioKetThuc,
    ldc.TrangThaiLich
from LICH_DAT_CHO ldc
inner join XE x
    on ldc.MaXe = x.MaXe
inner join KHACH_HANG kh
    on x.MaNguoiDung = kh.MaNguoiDung
inner join NGUOI_DUNG nd
    on kh.MaNguoiDung = nd.MaNguoiDung
inner join CONG_SAC cs
    on ldc.MaCong = cs.MaCong
inner join TRAM_SAC ts
    on cs.MaTram = ts.MaTram
WHERE nd.HoTen = N'Nguyễn Văn An'
    AND ldc.GioBatDau BETWEEN
        '2026-06-01'
        AND '2026-06-30 23:59:59'
ORDER BY ldc.GioBatDau;
-- Câu 2 (thống kê) Thống kê số lần sử dụng của từng cổng sạc.
select
    cs.MaCong,
    ts.TenTram,
    count(ps.MaPhien) as TongSoPhienSac,
    sum(ps.SoKwhTieuThu) as TongDienNang
from CONG_SAC cs
inner join TRAM_SAC ts
    on cs.MaTram = ts.MaTram
left join LICH_DAT_CHO ldc
    on cs.MaCong = ldc.MaCong
left join PHIEN_SAC ps
    on ldc.MaLichDat = ps.MaLichDat
group by
    cs.MaCong,
    ts.TenTram
order by TongSoPhienSac desc;
-- câu 3. (Thống kê có điều kiện having) Liệt kê các khách hàng đã thực hiện từ 3 phiên sạc trở lên
select
    nd.HoTen,
    COUNT(ps.MaPhien) as TongSoPhien,
    SUM(ps.SoKwhTieuThu) as TongDienNang
from NGUOI_DUNG nd
inner join KHACH_HANG kh
    on nd.MaNguoiDung = kh.MaNguoiDung
inner join XE x
    on kh.MaNguoiDung = x.MaNguoiDung
inner join LICH_DAT_CHO ldc
    on x.MaXe = ldc.MaXe
inner join PHIEN_SAC ps
    on ldc.MaLichDat = ps.MaLichDat
group by nd.HoTen
having count(ps.MaPhien) >= 3
order by TongDienNang desc;
-- Câu 4:(Dạng 4 - Bảng cha không có dữ liệu ở bảng con) Liệt kê các khách hàng đã đăng ký tài khoản nhưng chưa từng đặt lịch sạc.
select
    kh.MaNguoiDung,
    nd.HoTen,
    nd.Email
from KHACH_HANG kh
inner join NGUOI_DUNG nd
    on kh.MaNguoiDung = nd.MaNguoiDung
left join XE x
    on kh.MaNguoiDung = x.MaNguoiDung
left join LICH_DAT_CHO ldc
    on x.MaXe = ldc.MaXe
where ldc.MaLichDat is NULL;
-- câu 5: (Dạng 5 - Subquery) Tìm khách hàng có tổng điện năng tiêu thụ lớn hơn mức tiêu thụ trung bình của tất cả khách hàng.
select
    nd.HoTen,
    sum(ps.SoKwhTieuThu) as TongDienNang
from NGUOI_DUNG nd
inner join KHACH_HANG kh
    on nd.MaNguoiDung = kh.MaNguoiDung
inner join XE x
    on kh.MaNguoiDung = x.MaNguoiDung
inner join LICH_DAT_CHO ldc
    on x.MaXe = ldc.MaXe
inner join PHIEN_SAC ps
    on ldc.MaLichDat = ps.MaLichDat
group by
    nd.HoTen
having SUM(ps.SoKwhTieuThu) >
(
    select AVG(TongKwh) from
    (
        select SUM(ps2.SoKwhTieuThu) as TongKwh from XE x2
        inner join LICH_DAT_CHO ldc2
            on x2.MaXe = ldc2.MaXe
        inner join PHIEN_SAC ps2
            on ldc2.MaLichDat = ps2.MaLichDat
        group by x2.MaNguoiDung
    ) as TB
);
-- câu 6:(Dạng 6 - View) Tạo View lưu thông tin lịch sử phiên sạc của khách hàng. 
drop view if exists VW_LICH_SU_SAC;
go
create view  VW_LICH_SU_SAC as
select
    nd.HoTen,
    x.BienSo,
    ts.TenTram,
    cs.MaCong,
    ps.GioBatDau,
    ps.GioKetThuc,
    ps.SoKwhTieuThu,
    hd.TongTienThanhToan
from PHIEN_SAC ps
inner join LICH_DAT_CHO ldc
    on ps.MaLichDat = ldc.MaLichDat
inner join XE x
    on ldc.MaXe = x.MaXe
inner join KHACH_HANG kh
    on x.MaNguoiDung = kh.MaNguoiDung
inner join NGUOI_DUNG nd
    on kh.MaNguoiDung = nd.MaNguoiDung
inner join CONG_SAC cs
    on ldc.MaCong = cs.MaCong
inner join TRAM_SAC ts
    on cs.MaTram = ts.MaTram
inner join HOA_DON hd
    on ps.MaPhien = hd.MaPhien;
go