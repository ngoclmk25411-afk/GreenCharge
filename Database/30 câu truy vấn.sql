use Greencharge
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