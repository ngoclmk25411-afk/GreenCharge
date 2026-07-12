-- 1. XÓA CÁC BẢNG CHỨA KHÓA NGOẠI (BẢNG CON) TRƯỚC
DROP TABLE IF EXISTS HOA_DON;
DROP TABLE IF EXISTS PHIEN_SAC;
DROP TABLE IF EXISTS LICH_DAT_CHO;
DROP TABLE IF EXISTS XE;
DROP TABLE IF EXISTS LICH_SU_BAO_TRI;
DROP TABLE IF EXISTS PHIEU_THU_GOM;
DROP TABLE IF EXISTS CONG_SAC;
DROP TABLE IF EXISTS NHAN_VIEN;
DROP TABLE IF EXISTS LOAI_PIN

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
	VaiTro nvarchar(100) not null check (VaiTro in (N'KhachHang', N'NhanVien', N'ChuDauTu')) 
);
create table KHACH_HANG 
(
	MaNguoiDung varchar(10) not null primary key foreign key references NGUOI_DUNG(MaNguoiDung),
	TongDiemXanh int not null default 0 check (TongDiemXanh>=0) 
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
	NgayThuGom datetime not null,
	MaTram varchar(10) foreign key references TRAM_SAC(MaTram)
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
    TrangThaiLich nvarchar(20) not null check (TrangThaiLich in (N'Đã sạc', N'Đang sạc', N'Đã hủy', N'Hoàn thành')),
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
    TongTienGoc decimal(18,2) not null default 0 check (TongTienGoc >= 0),
    SoDiemTieuThu int not null default 0 check (SoDiemTieuThu >= 0),
    SoTienGiam decimal(18,2) not null default 0 check (SoTienGiam >= 0),
    TongTienThanhToan decimal(18,2) not null default 0 check (TongTienThanhToan >= 0),
    PhiVanHanhApp decimal(18,2) not null default 0 check (PhiVanHanhApp >= 0),
    DoanhThuCDT decimal(18,2) not null default 0 check (DoanhThuCDT >= 0),
    TrangThaiHD nvarchar(20) not null check (TrangThaiHD in (N'Chưa thanh toán', N'Đã thanh toán', N'Thất bại', N'Đã hoàn tiền')),
    NgayThanhToan datetime not null,
    PhuongThucThanhToan nvarchar(30) not null check (PhuongThucThanhToan in (N'Tiền mặt', N'Chuyển khoản', N'Ví điện tử', N'Thẻ ngân hàng'))
);
--- chèn dữ liệu vào bảng

insert NGUOI_DUNG values
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
select*from NGUOI_DUNG
---
insert KHACH_HANG (MaNguoiDung, TongDiemXanh) values
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
	('PG001', 'ND001', 'ND009', 'LP001', 5.20, 416, '2026-06-10 09:30:00','TS003'),
	('PG002', 'ND002', 'ND007', 'LP002', 3.00, 360, '2026-06-12 14:00:00','TS001'),
	('PG003', 'ND003', 'ND008', 'LP003', 2.50, 375, '2026-06-15 10:15:00','TS002'),
	('PG004', 'ND004', 'ND009', 'LP004', 1.80, 180, '2026-06-18 16:45:00','TS003'),
	('PG005', 'ND010', 'ND007', 'LP005', 4.00, 240, '2026-06-20 11:00:00','TS001');
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
---
insert into BieuGiaDien (MaBieuGia, LoaiCaySac, KhungGio, GioBatDau, GioKetThuc, DonGiaKwh, NgayApDung, TrangThai) values
-- AC
	('BG001', N'AC', N'Giờ thấp điểm',
	 '00:00:00', '05:59:59',
	 2800.00,
	 '2026-01-01',
	 N'Đang áp dụng'),

	('BG002', N'AC', N'Giờ bình thường',
	 '06:00:00', '17:59:59',
	 3300.00,
	 '2026-01-01',
	 N'Đang áp dụng'),

	('BG003', N'AC', N'Giờ cao điểm',
	 '18:00:00', '22:59:59',
	 4000.00,
	 '2026-01-01',
	 N'Đang áp dụng'),


	('BG004', N'AC', N'Giờ đêm',
	 '23:00:00', '23:59:59',
	 3000.00,
	 '2026-01-01',
	 N'Đang áp dụng'),

-- DC
	('BG005', N'DC', N'Giờ thấp điểm',
	 '00:00:00', '05:59:59',
	 4500.00,
	 '2026-01-01',
	 N'Đang áp dụng'),

	('BG006', N'DC', N'Giờ bình thường',
	 '06:00:00', '17:59:59',
	 5200.00,
	 '2026-01-01',
	 N'Đang áp dụng'),

	('BG007', N'DC', N'Giờ cao điểm',
	 '18:00:00', '22:59:59',
	 6200.00,
	 '2026-01-01',
	 N'Đang áp dụng'),

	('BG008', N'DC', N'Giờ đêm',
	 '23:00:00', '23:59:59',
	 5000.00,
	 '2026-01-01',
	 N'Đang áp dụng'),

-- Siêu nhanh
	('BG009', N'Siêu nhanh', N'Giờ thấp điểm',
	 '00:00:00', '05:59:59',
	 6000.00,
	 '2026-01-01',
	 N'Đang áp dụng'),

	('BG010', N'Siêu nhanh', N'Giờ bình thường',
	 '06:00:00', '17:59:59',
	 7000.00,
	 '2026-01-01',
	 N'Đang áp dụng'),

	('BG011', N'Siêu nhanh', N'Giờ cao điểm',
	 '18:00:00', '22:59:59',
	 8500.00,
	 '2026-01-01',
	 N'Đang áp dụng'),

	('BG012', N'Siêu nhanh', N'Giờ đêm',
	 '23:00:00', '23:59:59',
	 6500.00,
	 '2026-01-01',
	 N'Đang áp dụng'),

	 ('BG013', N'AC', N'Giờ bình thường',
	 '06:00:00', '17:59:59',
	 3300.00,
	 '2025-01-01',
	 N'Ngừng áp dụng');
select * from BieuGiaDien
---
insert into XE (MaXe, BienSo, MaNguoiDung, MaChuanSac) values
	('XE001', '51A-12345', 'ND001', 'CS001'),
	('XE002', '59B-23456', 'ND002', 'CS002'),
	('XE003', '61C-34567', 'ND003', 'CS002'),
	('XE004', '50D-45678', 'ND004', 'CS003'),
	('XE005', '51H-56789', 'ND010', 'CS001');
select * from XE
---
insert into LICH_DAT_CHO values
	('LD001','XE001','CG001',
	'2026-06-10 09:00',
	'2026-06-10 10:00',
	N'Đã sạc'),

	('LD002','XE002','CG002',
	'2026-06-12 14:00',
	'2026-06-12 15:30',
	N'Đã sạc'),

	('LD003','XE003','CG003',
	'2026-06-15 10:00',
	'2026-06-15 11:00',
	N'Đã sạc'),

	('LD004','XE004','CG004',
	'2026-06-18 16:00',
	'2026-06-18 17:00',
	N'Đã sạc'),

	('LD005','XE005','CG001',
	'2026-06-20 08:30',
	'2026-06-20 09:30',
	N'Đã sạc');
select * from LICH_DAT_CHO
---
insert into PHIEN_SAC (MaPhien, MaLichDat, GioBatDau, GioKetThuc, 
					SoKwhTieuThu, TrangThaiPhien, MaBieuGia) values

	('PS001',
	 'LD001',
	 '2026-06-10 09:03:00',
	 '2026-06-10 09:56:00',
	 49.80,
	 N'Hoàn thành',
	 'BG010'),

	('PS002',
	 'LD002',
	 '2026-06-12 14:02:00',
	 '2026-06-12 15:22:00',
	 24.60,
	 N'Hoàn thành',
	 'BG002'),

	('PS003',
	 'LD003',
	 '2026-06-15 10:04:00',
	 '2026-06-15 10:58:00',
	 41.30,
	 N'Hoàn thành',
	 'BG006'),

	('PS004',
	 'LD004',
	 '2026-06-18 16:05:00',
	 '2026-06-18 16:54:00',
	 36.90,
	 N'Hoàn thành',
	 'BG006'),

	('PS005',
	 'LD005',
	 '2026-06-20 08:32:00',
	 '2026-06-20 09:27:00',
	 53.50,
	 N'Hoàn thành',
	 'BG010');
select * from PHIEN_SAC
--- FUNCTION LẤY ĐƠN GIÁ THEO LOẠI CÂY SẠC VÀ THỜI GIAN ---
go
create or alter function fn_LayDonGia (@LoaiCaySac nvarchar(30), @ThoiDiem datetime)
returns decimal(18,2) 
as
begin
	declare @DonGia decimal (18,2)
	select top 1
		@DonGia = DonGiaKwh
	from BieuGiaDien
	where LoaiCaySac = @LoaiCaySac
		and TrangThai = N'Đang Áp dụng'
		and cast(@ThoiDiem as time)
			between GioBatDau and GioKetThuc
	return @DonGia
end
go
--- TẠO STORED PROCEDURE Đặt lịch sạc
--- Quy tắc kiểm tra: 
	-- Giờ bắt đầu > hiện tại
	-- Giờ kết thúc > giờ bắt đầu
	-- Chuẩn sạc đúng
	-- Cổng phải đang Trống
	-- Không trùng lịch
	-- Insert thành công
go
create or alter PROC SP_DatlichSac
	@MaLichDat varchar(10),
	@MaXe varchar(10),
	@MaCong varchar(10),
	@GioBatDau datetime,
	@GioKetThuc datetime
as
begin
set nocount on;
begin try
	-- Kiểm tra thời gian --
	if @GioBatDau<=GETDATE()
	begin
		raiserror(N'Giờ bắt đầu phải lớn hơn thời gian hiện tại.',16,1)
		return
	end

	if @GioKetThuc<=@GioBatDau
	begin
		raiserror(N'Giờ kết thúc phải lớn hơn giờ bắt đầu.',16,1)
		return
	end
	-- Kiểm tra chuẩn sạc --
	declare
		@ChuanXe varchar(10),
		@ChuanCong varchar(10)
	select @ChuanXe=MaChuanSac from XE where MaXe=@MaXe
	select @ChuanCong=MaChuanSac from CONG_SAC where MaCong=@MaCong
	if @ChuanXe<>@ChuanCong
	begin
		raiserror(N'Chuẩn sạc của xe không tương thích với cổng sạc.',16,1)
		return
	end
	-- Kiểm tra trạng thái cổng --
	if not exists
	(select * from CONG_SAC where MaCong=@MaCong and TrangThaiCong=N'Trống')
	begin
		raiserror(N'Cổng sạc hiện không khả dụng.',16,1)
		return
	end
	-- Kiểm tra trùng lịch --
	if exists
	(select * from LICH_DAT_CHO where MaCong=@MaCong and TrangThaiLich<>N'Đã hủy'
								and (@GioBatDau<GioKetThuc and @GioKetThuc>GioBatDau))
	begin
		raiserror(N'Khung giờ đã được đặt.',16,1)
		return
	end
	-- Insert lịch --
	insert into LICH_DAT_CHO(MaLichDat,MaXe,MaCong,GioBatDau,GioKetThuc,TrangThaiLich)
	values
	(
		@MaLichDat,
		@MaXe,
		@MaCong,
		@GioBatDau,
		@GioKetThuc,
		N'Đã đặt'
	)
	print N'Đặt lịch thành công.'
end try
begin catch
	print ERROR_MESSAGE()
end catch
end
go
--- Tạo STORED PROCEDURE SP_ThuGomPin
go 
create or alter PROC SP_ThuGomPin
	@MaPhieu varchar(10),
	@MaNguoiDung_KH varchar(10),
	@MaNguoiDung_NV varchar(10),
	@MaLoaiPin varchar(10),
	@KhoiLuong decimal(6,2),
	@NgayThuGom datetime,
	@MaTram varchar(10)
as
begin
set nocount on;
begin try
	-- Kiểm tra dữ liệu --
	if @KhoiLuong<=0
	begin 
		raiserror(N'Khối lượng pin phải lớn hơn 0.',16,1)
		return
	end
	-- Lấy hệ số quy đổi --
	declare
		@HeSo decimal(5,2),
		@Diem int
	select @HeSo=HeSoQuyDoi from LOAI_PIN where MaLoaiPin=@MaLoaiPin
	if @HeSo is null
	begin
		raiserror(N'Không tồn tại loại pin.',16,1)
		return
	end
	-- Tính điểm --
	set @Diem=round(@KhoiLuong*@HeSo,0)
	-- Insert phiếu --
	insert into PHIEU_THU_GOM 
	(MaPhieu,MaNguoiDung_KH,MaNguoiDung_NV,
	MaLoaiPin,KhoiLuong,DiemThuong,NgayThuGom,MaTram) 
	values
	(
		@MaPhieu,
        @MaNguoiDung_KH,
        @MaNguoiDung_NV,
        @MaLoaiPin,
        @KhoiLuong,
        @Diem,
        @NgayThuGom,
        @MaTram
    )
	print N'Tạo phiếu thu gom thành công.'
end try
begin catch
	print ERROR_MESSAGE()
end catch
end
go
--- TẠO TRIGGER KHI PHIẾU THU GOM ĐƯỢC XÁC NHẬN THÀNH CÔNG THÌ CỘNG ĐIỂM
go
create or alter trigger TRG_CongDiemXanh on PHIEU_THU_GOM
after insert
as
begin
set nocount on;
update KH
set KH.TongDiemXanh = KH.TongDiemXanh + I.DiemThuong
from KHACH_HANG KH join inserted I on KH.MaNguoiDung=I.MaNguoiDung_KH
end
go
--- TẠO TRIGGER KIỂM TRA NHÂN VIÊN THUỘC ĐÚNG TRẠM
go
create or alter trigger TRG_KiemTraTramThuGom on PHIEU_THU_GOM
after insert
as
begin
set nocount on;
if exists
(
	select * from inserted I join NHAN_VIEN NV on I.MaNguoiDung_NV=NV.MaNguoiDung
	where I.MaTram<>NV.MaTram
)
begin
	raiserror(N'Nhân viên không thuộc trạm tiếp nhận.',16,1)
	rollback transaction
end
end
go
--- TẠO STORED PROCEDURE SP_ThanhToanHoaDon
go
create or alter PROC SP_ThanhToanHoaDon
	@MaHD varchar(10),
	@MaPhien varchar(10),
	@SoDiemMuonDung int,
	@PhuongThucThanhToan nvarchar(30)
as
begin
set nocount on;
begin try
begin TRAN
-- Khai báo biến
declare
	@MaKH varchar(10),
    @MaCong varchar(10),
    @LoaiCaySac nvarchar(30),
    @DonGia decimal(18,2),
    @TongTienGoc decimal(18,2),
    @TongTienThanhToan decimal(18,2),
    @SoTienGiam decimal(18,2),
    @PhiVanHanh decimal(18,2),
    @DoanhThuCDT decimal(18,2),
    @SoDuDiem int,
    @SoKwh decimal(8,2),
    @GioBatDau datetime,
    @MaChuDauTu varchar(10)
-- Lấy dữ liệu phiên sạc
select
	@SoKwh = PS.SoKwhTieuThu,
    @GioBatDau = PS.GioBatDau,
    @MaCong = LD.MaCong,
    @MaKH = XE.MaNguoiDung
from PHIEN_SAC PS join LICH_DAT_CHO LD on PS.MaLichDat=LD.MaLichDat
join XE on LD.MaXe=XE.MaXe where PS.MaPhien=@MaPhien
if @SoKwh is null
begin
	raiserror(N'Không tồn tại phiên sạc.',16,1)
	rollback
	return
end
-- Lấy loại cây sạc
select @LoaiCaySac=LoaiCaySac from CONG_SAC where MaCong=@MaCong
-- Lấy đơn giá
set @DonGia=dbo.fn_LayDonGia
(
	@LoaiCaySac,
	@GioBatDau
)
-- Tính tiền gốc
set @TongTienGoc=@SoKwh*@DonGia
-- Lấy điểm khách hàng
select @SoDuDiem=TongDiemXanh from KHACH_HANG where MaNguoiDung=@MaKH
-- Kiểm tra số điểm
if @SoDiemMuonDung>@SoDuDiem
begin
	raiserror(N'Điểm xanh không đủ.',16,1)
	rollback
	return
end
-- Tính tiền giảm
set @SoTienGiam=@SoDiemMuonDung*100 --Không vượt quá 10%
if @SoTienGiam>@TongTienGoc*0.1
begin
	set @SoTienGiam=@TongTienGoc*0.1
	set @SoDiemMuonDung=@SoTienGiam/100
end
-- Thành tiền
set @TongTienThanhToan = @TongTienGoc-@SoTienGiam
-- Phí vận hành
set @PhiVanHanh = @TongTienThanhToan*0.1
-- Doanh thu Chủ đầu tư
set @DoanhThuCDT = @TongTienThanhToan*0.9
-- Insert hóa đơn
insert into HOA_DON
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
values
(
    @MaHD,
    @MaPhien,
    @MaKH,
    @TongTienGoc,
    @SoDiemMuonDung,
    @SoTienGiam,
    @TongTienThanhToan,
    @PhiVanHanh,
    @DoanhThuCDT,
    N'Đã thanh toán',
    GETDATE(),
    @PhuongThucThanhToan
)
-- Trừ điểm xanh
update KHACH_HANG
set TongDiemXanh = TongDiemXanh-@SoDiemMuonDung
where MaNguoiDung=@MaKH
--Tìm chủ đầu tư
select @MaChuDauTu=TS.MaNguoiDung
from CONG_SAC CS join TRAM_SAC TS on CS.MaTram=TS.MaTram where CS.MaCong=@MaCong
-- Cộng doanh thu
update CHU_DAU_TU
set SoDuDoanhThu = SoDuDoanhThu+@DoanhThuCDT
where MaNguoiDung=@MaChuDauTu
update PHIEN_SAC
set TrangThaiPhien=N'Hoàn thành'
where MaPhien=@MaPhien;
commit
print N'Thanh toán thành công.'
end try
begin catch
if @@TRANCOUNT>0
rollback
print ERROR_MESSAGE()
end catch
end
go

--- TẠO TRIGGER HOÀN THÀNH PHIÊN SẠC --> GIẢI PHÓNG CỔNG SẠC
-- Khi phiên sạc chuyển sang "Hoàn thành" => cổng sạc chuyển sang Trống
go 
create or alter trigger TRG_HoanThanhPhienSac
on PHIEN_SAC
after update
as 
begin
	set nocount on;
	update CS
	set TrangThaiCong=N'Trống' 
	from CONG_SAC CS 
	join LICH_DAT_CHO L on CS.MaCong=L.MaCong
	join inserted I on L.MaLichDat=I.MaLichDat
	join deleted D on D.MaPhien=I.MaPhien
	where D.TrangThaiPhien<>N'Hoàn thành'
	and I.TrangThaiPhien=N'Hoàn thành'
end
go

--- TẠO TRIGGER KHI PHIÊN SẠC BẮT ĐẦU, CỔNG CHUYỂN SANG "ĐANG SẠC"
go
create or alter trigger TRG_BatDauSac 
on PHIEN_SAC
after insert
as 
begin
	update CS
	set TrangThaiCong=N'Đang sạc'
	from CONG_SAC CS 
	join LICH_DAT_CHO L	on CS.MaCong=L.MaCong
	join inserted I on L.MaLichDat=I.MaLichDat
	where I.TrangThaiPhien=N'Đang sạc'
end
go
--- TẠO TRIGGER CHẶN TỒN TẠI ĐỒNG THỜI NHIỀU PHIÊN SẠC ĐANG SẠC TRÊN CÙNG MỘT CỔNG
go
create or alter trigger TRG_MotCongMotPhien
on PHIEN_SAC
after insert,update
as
begin
if exists (select L.MaCong from PHIEN_SAC P join LICH_DAT_CHO L on P.MaLichDat=L.MaLichDat
			where P.TrangThaiPhien=N'Đang sạc'
			group by L.MaCong
			having count(*)>1)
	begin
		raiserror(N'Mỗi cổng chỉ được có một phiên đang sạc!',16,1)
		rollback
	end
end
go
--- 30 CÂU TRUY VẤN ---
--- MỨC 1 ---
--1. Liệt kê khách hàng có Điểm Xanh > 100 AND
--(số điện thoại bắt đầu bằng '090' OR họ tên chứa 'Nguyễn')
go
select kh.MaNguoiDung, nd.HoTen, nd.Sdt, kh.TongDiemXanh
from KHACH_HANG kh
    join NGUOI_DUNG nd on kh.MaNguoiDung = nd.MaNguoiDung
where kh.TongDiemXanh > 100
  and (nd.Sdt like '090%' or nd.HoTen like N'%Nguyễn%')
go
--2. Liệt kê các cổng sạc loại 'AC' hoặc 'DC' có công suất từ 50.00kW trở lên kèm tên trạm sạc tương ứng.
--Thông tin gồm MaCong, TenTram, CongSuat, LoaiCaySac. 
go
SELECT cs.MaCong, ts.TenTram, cs.CongSuat, cs.LoaiCaySac 
FROM CONG_SAC cs JOIN TRAM_SAC ts ON cs.MaTram = ts.MaTram 
WHERE (cs.LoaiCaySac = N'AC' OR cs.LoaiCaySac = N'DC') AND cs.CongSuat >= 50.00; 
go
--3.Khách hàng Nguyễn Văn An muốn xem tất cả các lịch đặt trong tháng 6 năm 2026.
--Hiển thị: Mã lịch đặt, Biển số xe,Tên trạm,Mã Cổng sạc,Thời gian bắt đầu,Thời gian kết thúc,Trạng thái
go
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
go
--4. Hiển thị danh sách các hóa đơn đã được khách hàng thanh toán thành công trong tháng 06/2026 bằng hình thức trực tuyến (Ví điện tử hoặc Thẻ ngân hàng).
-- Thông tin gồm: MaHD, HoTen, TongTienThanhToan, PhuongThucThanhToan, NgayThanhToan
go
select hd.MaHD,
       nd.HoTen,
       hd.TongTienThanhToan,
       hd.PhuongThucThanhToan,
       hd.NgayThanhToan
from HOA_DON hd
join NGUOI_DUNG nd on hd.MaNguoiDung = nd.MaNguoiDung
where hd.TrangThaiHD = N'Đã thanh toán'
  and (hd.NgayThanhToan between '2026-05-01' and '2026-06-30 23:59:59')
  and (hd.PhuongThucThanhToan = N'Ví điện tử' or hd.PhuongThucThanhToan = N'Thẻ ngân hàng')
order by hd.NgayThanhToan desc;
go
--5. Liệt kê các khách hàng đã tham gia thu gom pin trong năm 2026, thông tin gồm [MaNguoiDung], [HoTen]
go
select nd.MaNguoiDung, HoTen
from NGUOI_DUNG nd
where nd.MaNguoiDung in ( select MaNguoiDung_KH
				   from PHIEU_THU_GOM
				   where YEAR(NgayThuGom)=2026)
go
--- Mức độ 2 - Thống kê chứa các hàng biểu thức (SUM, COUNT, MIN, MAX, AVG)
--1. Với mỗi khách hàng, tính số lần thanh toán, tổng tiền, trung bình, thấp nhất, cao nhất
go
select nd.MaNguoiDung, nd.HoTen, 
	SoLanThanhToan = count(hd.MaHD), 
	TongTien = isnull(sum(hd.TongTienThanhToan), 0), 
	TrungBinh = isnull(avg(hd.TongTienThanhToan), 0), 
	ThapNhat = isnull(min(hd.TongTienThanhToan), 0), 
	CaoNhat = isnull(max(hd.TongTienThanhToan), 0) 
from KHACH_HANG kh 
	join NGUOI_DUNG nd on kh.MaNguoiDung = nd.MaNguoiDung 
	left join HOA_DON hd on kh.MaNguoiDung = hd.MaNguoiDung 
group by nd.MaNguoiDung, nd.HoTen 
go
--2. Thống kê hiệu suất cấp điện của từng cổng sạc trong hệ thống mạng lưới.
--Thông tin gồm MaCong, MaTram, SoLuotSac, TongKwh, TrungBinhKwh, ThapNhatKwh, CaoNhatKwh. 
go
SELECT
    cs.MaCong,
    cs.MaTram,
    SoLuotSac = COUNT(ps.MaPhien),
    TongKwh = ISNULL(SUM(ps.SoKwhTieuThu), 0),
    TrungBinhKwh = ISNULL(AVG(ps.SoKwhTieuThu), 0),
    ThapNhatKwh = ISNULL(MIN(ps.SoKwhTieuThu), 0),
    CaoNhatKwh = ISNULL(MAX(ps.SoKwhTieuThu), 0)
FROM CONG_SAC cs
LEFT JOIN LICH_DAT_CHO ld
    ON cs.MaCong = ld.MaCong
LEFT JOIN PHIEN_SAC ps
    ON ld.MaLichDat = ps.MaLichDat
GROUP BY
    cs.MaCong,
    cs.MaTram; 
go
--3. Thống kê số lần sử dụng của từng cổng sạc. Hiển thị:Mã cổng,Tên trạm,Tổng số phiên sạc,Tổng điện năng đã cung cấp (kWh)
go
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
go
--4.Thống kê tổng số lượng hóa đơn, tổng số tiền tích lũy, số tiền sạc thấp nhất, cao nhất và trung bình của từng khách hàng đã thanh toán thành công.
-- Thông tin gồm: MaNguoiDung, HoTen, SoLuongHoaDon, TongTienTichLuy, GiaThapNhat, GiaCaoNhat, TrungBinh
go
select nd.MaNguoiDung,
       nd.HoTen,
       SoLuongHoaDon = count(hd.MaHD),
       TongTienTichLuy = sum(hd.TongTienThanhToan),
       GiaThapNhat = min(hd.TongTienThanhToan),
       GiaCaoNhat = max(hd.TongTienThanhToan),
       TrungBinh = avg(hd.TongTienThanhToan)
from NGUOI_DUNG nd
join HOA_DON hd on nd.MaNguoiDung = hd.MaNguoiDung
where hd.TrangThaiHD = N'Đã thanh toán'
group by nd.MaNguoiDung, nd.HoTen
order by TongTienTichLuy desc;
go
--5. Thống kê tổng khối lượng pin đã thu gom theo từng loại pin trong tháng 6 năm 2026, thông tin gồm [MaLoaiPin], [TenLoaiPin], [TongKhoiLuong], [TongDiemThuong]
go
select lp.MaLoaiPin, TenLoaiPin, TongKhoiLuong=sum(KhoiLuong), TongDiemThuong=sum(DiemThuong)
from LOAI_PIN lp join PHIEU_THU_GOM ptg on lp.MaLoaiPin = ptg.MaLoaiPin
where YEAR(NgayThuGom)=2026 and MONTH(NgayThuGom)=6
group by lp.MaLoaiPin,TenLoaiPin
go
--Mức 3:Thống kê có điều kiện chứa mệnh đề HAVING
--1. Liệt kê khách hàng có tổng tiền thanh toán > 500.000đ
go
select nd.MaNguoiDung, nd.HoTen,
       TongTien = sum(hd.TongTienThanhToan)
from KHACH_HANG kh
    join NGUOI_DUNG nd on kh.MaNguoiDung = nd.MaNguoiDung
    join HOA_DON hd on kh.MaNguoiDung = hd.MaNguoiDung
group by nd.MaNguoiDung, nd.HoTen
having sum(hd.TongTienThanhToan) > 500000
go
--2. Liệt kê các trạm sạc đang sở hữu từ 2 cổng sạc trở lên (>=2). 
-- Thông tin gồm [MaTram], [TenTram], countofCongSac. Liệt kê các khách hàng đã thực hiện từ 3 phiên sạc trở lên. Hiển thị: Họ tên, Tổng số phiên sạc, Tổng điện năng tiêu thụ
go
SELECT ts.MaTram, ts.TenTram, countofCongSac = COUNT(cs.MaCong) 
FROM TRAM_SAC ts JOIN CONG_SAC cs ON ts.MaTram = cs.MaTram 
GROUP BY ts.MaTram, ts.TenTram 
HAVING COUNT(cs.MaCong) >= 2;
go
--3. Liệt kê các khách hàng đã thực hiện từ 3 phiên sạc trở lên.
-- Hiển thị: Họ tên, Tổng số phiên sạc, Tổng điện năng tiêu thụ
go
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
go
--4. Thống kê tổng doanh thu thực tế mang lại cho các Chủ đầu tư từ các hóa đơn đã thanh toán, chỉ lấy các chủ đầu tư có tổng doanh thu lớn hơn 100.000 VNĐ.
-- Thông tin gồm: TenDoiTac, SoLuongHoaDon, TongDoanhThuCDT
go
select cdt.TenDoiTac,
       count(hd.MaHD) as SoLuongHoaDon,
       sum(hd.DoanhThuCDT) as TongDoanhThuCDT
from HOA_DON hd
join PHIEN_SAC ps on hd.MaPhien = ps.MaPhien
join LICH_DAT_CHO ld on ps.MaLichDat = ld.MaLichDat
join CONG_SAC cs on ld.MaCong = cs.MaCong
join TRAM_SAC ts on cs.MaTram = ts.MaTram
join CHU_DAU_TU cdt on ts.MaNguoiDung = cdt.MaNguoiDung
where hd.TrangThaiHD = N'Đã thanh toán'
group by cdt.TenDoiTac
having sum(hd.DoanhThuCDT) > 100000
order by TongDoanhThuCDT desc;
go
--5. Liệt kê các khách hàng có tổng điểm thưởng từ các phiếu thu gom lớn hơn 300 điểm, thông tin gồm [MaNguoiDung], [HoTen], [TongDiemThuong]
go
SELECT
    nd.MaNguoiDung,
    nd.HoTen,
    TongDiemThuong = SUM(ptg.DiemThuong)
FROM KHACH_HANG kh
JOIN NGUOI_DUNG nd
    ON kh.MaNguoiDung = nd.MaNguoiDung
JOIN PHIEU_THU_GOM ptg
    ON kh.MaNguoiDung = ptg.MaNguoiDung_KH
GROUP BY
    nd.MaNguoiDung,
    nd.HoTen
HAVING SUM(ptg.DiemThuong) > 300;
go
---Mức 4:liệt kê các dữ liệu có trong bảng cha mà không có trong bảng con
--1. Liệt kê khách hàng (bảng cha KHACH_HANG) chưa đăng ký xe điện nào (bảng con Xe)
--cách 1:
go
select nd.MaNguoiDung, nd.HoTen
from KHACH_HANG kh
    join NGUOI_DUNG nd on kh.MaNguoiDung = nd.MaNguoiDung
    left join Xe x on kh.MaNguoiDung = x.MaNguoiDung
where x.MaXe is null
go
--cách 2:
go
select nd.MaNguoiDung, nd.HoTen
from KHACH_HANG kh
    join NGUOI_DUNG nd on kh.MaNguoiDung = nd.MaNguoiDung
where kh.MaNguoiDung not in (select MaNguoiDung from Xe)
go
--2. Liệt kê danh sách các trạm sạc chưa được lắp đặt bất kỳ một cổng sạc vật lý nào. 
--cách 1:
go
SELECT ts.MaTram, ts.TenTram, ts.DiaChi 
FROM TRAM_SAC ts LEFT JOIN CONG_SAC cs ON ts.MaTram = cs.MaTram 
WHERE cs.MaCong IS NULL; 
go
--cách 2:
go
SELECT * 
FROM TRAM_SAC 
WHERE MaTram NOT IN (SELECT MaTram FROM CONG_SAC); 
go
--3. Liệt kê các khách hàng đã đăng ký tài khoản nhưng chưa từng đặt lịch sạc. 
-- Hiển thị: Mã khách hàng, Họ tên, Email
go
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
go
--4. Liệt kê danh sách các Khách hàng đã đăng ký tài khoản trên hệ thống nhưng chưa từng phát sinh bất kỳ hóa đơn sạc xe nào.
--Thông tin gồm: MaNguoiDung, HoTen, Sdt, Email
go
select kh.MaNguoiDung, nd.HoTen, nd.Sdt, nd.Email
from KHACH_HANG kh
join NGUOI_DUNG nd on kh.MaNguoiDung = nd.MaNguoiDung
left join HOA_DON hd on kh.MaNguoiDung = hd.MaNguoiDung
where hd.MaHD is null;
go
--5. Liệt kê các loại pin có tổng khối lượng thu gom lớn hơn 2kg trong năm 2026, thông tin gồm [MaLoaiPin], [TenLoaiPin], [TongKhoiLuong]
go
select lp.MaLoaiPin,TenLoaiPin, TongKhoiLuong=sum(KhoiLuong)
from LOAI_PIN lp join PHIEU_THU_GOM ptg on lp.MaLoaiPin = ptg.MaLoaiPin
where YEAR(NgayThuGom)=2026
group by lp.MaLoaiPin,TenLoaiPin
having SUM(KhoiLuong)>2
go

---Mức 5: Subquery
--1. Liệt kê khách hàng có tổng tiền thanh toán cao hơn mức trung bình của tất cả khách hàng
go
select nd.MaNguoiDung, nd.HoTen, 
          TongTien = sum(hd.TongTienThanhToan) 
from KHACH_HANG kh 
join NGUOI_DUNG nd on kh.MaNguoiDung = nd.MaNguoiDung 
join HOA_DON hd on kh.MaNguoiDung = hd.MaNguoiDung 
group by nd.MaNguoiDung, nd.HoTen 
having sum(hd.TongTienThanhToan) > ( 
select avg(TongTienKH) 
from ( 
select sum(TongTienThanhToan) as TongTienKH 
from HOA_DON 
group by MaNguoiDung 
) as ThongKeTheoKH ) 
go
--2. Xem thông tin của trạm sạc sở hữu số lượng cổng sạc nhiều nhất trong hệ thống mạng lưới. Thông tin gồm [MaTram], [TenTram]. 
go
SELECT MaTram, TenTram 
FROM TRAM_SAC 
WHERE MaTram IN (SELECT MaTram
    FROM CONG_SAC 
    GROUP BY MaTram
    HAVING COUNT(*) >= ALL (SELECT COUNT(*) 
FROM CONG_SAC
GROUP BY MaTram)); 
go
--3. Tìm khách hàng có tổng điện năng tiêu thụ lớn hơn mức tiêu thụ trung bình của tất cả khách hàng.
-- Hiển thị: Họ tên, Tổng điện năng tiêu thụ
go
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
go
--4. Tìm những hóa đơn có tổng tiền thanh toán lớn hơn giá trị thanh toán trung bình của tất cả các hóa đơn đã hoàn thành trong hệ thống.
--Thông tin gồm: MaHD, HoTen, SoDiemTieuThu, SoTienGiam, TongTienThanhToan
go
select MaHD, MaNguoiDung, TongTienThanhToan, NgayThanhToan
from HOA_DON
where TrangThaiHD = N'Đã thanh toán'
  and TongTienThanhToan > (
      select avg(TongTienThanhToan) 
      from HOA_DON 
      where TrangThaiHD = N'Đã thanh toán'
  );
go
--5. Liệt kê các loại pin chưa được thu gom với khối lượng trên 5kg, gồm [MaLoaiPin], [TenLoaiPin]
go
select lp.MaLoaiPin, TenLoaiPin
from LOAI_PIN lp
where lp.MaLoaiPin not in ( select ptg.MaLoaiPin
	                                   from PHIEU_THU_GOM ptg
	                    		  where KhoiLuong > 5)
go
--- Mức 6: Mức độ 6 - View
--1. Yêu cầu: Nhân viên trạm sạc cần xem thông tin khách hàng + xe để hỗ trợ kỹ thuật,
--nhưng không được thấy SĐT, Email (thông tin cá nhân nhạy cảm) và không được thấy DiemXanh/số tiền (dữ liệu tài chính nội bộ)
drop view if exists vw_KhachHang_Xe;
go
create view vw_KhachHang_Xe as
select nd.MaNguoiDung,
       nd.HoTen,
       x.BienSo,
       cs.TenChuan
from KHACH_HANG kh
    join NGUOI_DUNG nd on kh.MaNguoiDung = nd.MaNguoiDung
    join Xe x on kh.MaNguoiDung = x.MaNguoiDung
    join CHUAN_SAC cs on x.MaChuanSac = cs.MaChuanSac
go
select * from vw_KhachHang_Xe;
go
--2. Tạo một View tên là 'v_CongSacSieuNhanh' hiển thị thông tin các cổng sạc loại 'Siêu nhanh' 
--kèm theo tên trạm tương ứng để phục vụ điều phối hạ tầng. 
drop view if exists v_CongSacSieuNhanh;
GO 
CREATE VIEW v_CongSacSieuNhanh 
AS 
     SELECT cs.MaCong, ts.TenTram, cs.CongSuat, cs.LoaiCaySac, cs.TrangThaiCong 
     FROM CONG_SAC cs JOIN TRAM_SAC ts ON cs.MaTram = ts.MaTram
     WHERE cs.LoaiCaySac = N'Siêu nhanh' 
     WITH CHECK OPTION; 
GO
select * from v_CongSacSieuNhanh;
go
--3. Tạo View lưu thông tin lịch sử phiên sạc của khách hàng. 
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
select * from VW_LICH_SU_SAC;
go
--4. Tạo một Khung nhìn (VIEW) có tên vw_ThongKePhuongThucThanhToan để lưu trữ báo cáo doanh thu theo từng phương thức thanh toán của hệ thống.
--Thông tin gồm: PhuongThucThanhToan, SoHoaDon, TongDoanhThu, DoanhThuTrungBinh
drop view if exists vw_ThongKePhuongThucThanhToan;
go
create view vw_ThongKePhuongThucThanhToan as
select PhuongThucThanhToan,
       SoHoaDon = count(*),
       TongDoanhThu = sum(TongTienThanhToan),
       DoanhThuTrungBinh = avg(TongTienThanhToan)
from HOA_DON
where TrangThaiHD = N'Đã thanh toán'
group by PhuongThucThanhToan;
GO
select * from vw_ThongKePhuongThucThanhToan;
go
--5. Thống kê tình hình thu gom pin theo từng loại pin, gồm [MaLoaiPin], [TenLoaiPin], [SoLanThuGom], [TongKhoiLuong], [TongDiemThuong].
drop view if exists BaoCaoLoaiPin;
go
create view BaoCaoLoaiPin
as
    select lp.MaLoaiPin, TenLoaiPin,
              SoLanThuGom = count(MaPhieu),
              TongKhoiLuong = sum(KhoiLuong),
              TongDiemThuong = sum(DiemThuong)
    from LOAI_PIN lp join PHIEU_THU_GOM ptg on lp.MaLoaiPin =ptg.MaLoaiPin
    group by lp.MaLoaiPin, TenLoaiPin
go
select * from BaoCaoLoaiPin;
go
