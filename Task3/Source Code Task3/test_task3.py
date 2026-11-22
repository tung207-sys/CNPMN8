import html
import pytest
from Task3 import (
    app,
    GIANG_VIENS,
    MON_HOCS,
    LOP_HOCS,
    PHAN_CONGS,
    GiangVien,
    MonHoc,
    LopHoc,
    PhanCongGiangDay,
)

@pytest.fixture(autouse=True)
def reset_sample_data():
    """Khôi phục dữ liệu mẫu ban đầu trước mỗi test case để các test độc lập nhau."""
    GIANG_VIENS.clear()
    GIANG_VIENS.extend([
        GiangVien(1, 'GV202401', 'Lê Thu Hương', 'huong.lt@example.edu.vn',
                  'Công nghệ thông tin', 'Thạc sĩ', 'Cơ sở dữ liệu & Hệ thống thông tin'),
        GiangVien(2, 'GV202402', 'Nguyễn Văn An', 'an.nv@example.edu.vn',
                  'Công nghệ thông tin', 'Tiến sĩ', 'Công nghệ phần mềm'),
        GiangVien(3, 'GV202403', 'Trần Minh Tâm', 'tam.tm@example.edu.vn',
                  'Quản trị kinh doanh', 'Tiến sĩ', 'Quản trị chiến lược'),
        GiangVien(4, 'GV202404', 'Phạm Lan Anh', 'anh.pl@example.edu.vn',
                  'Ngôn ngữ Anh', 'Thạc sĩ', 'Tiếng Anh thương mại'),
    ])

    MON_HOCS.clear()
    MON_HOCS.extend([
        MonHoc(1, 'CSDL2601', 'Cơ sở dữ liệu', 3, 'Công nghệ thông tin',
               '30 LT | 30 TH', 'Thiết kế ERD, chuẩn hóa dữ liệu, đại số quan hệ và truy vấn SQL.'),
        MonHoc(2, 'CNPM2601', 'Công nghệ phần mềm', 3, 'Công nghệ thông tin',
               '30 LT | 30 TH', 'Quy trình phát triển phần mềm, đặc tả yêu cầu và thiết kế sơ đồ UML.'),
        MonHoc(3, 'LTW2601', 'Lập trình Web với Python', 4, 'Công nghệ thông tin',
               '30 LT | 60 TH', 'Xây dựng ứng dụng Web bằng Flask và giao diện Bootstrap.'),
        MonHoc(4, 'QTKD2602', 'Quản trị chiến lược', 3, 'Quản trị kinh doanh',
               '45 LT | 0 TH', 'Hoạch định, triển khai và đánh giá chiến lược kinh doanh doanh nghiệp.'),
    ])

    LOP_HOCS.clear()
    LOP_HOCS.extend([
        LopHoc(1, 'CNTT2401', 'Công nghệ thông tin 1', 'Công nghệ thông tin',
               'Khóa 2024 – 2028 | Hệ chính quy', 48, 'Thứ 2 | 10:15 – 11:00', 'B301'),
        LopHoc(2, 'CNTT2402', 'Công nghệ thông tin 2', 'Công nghệ thông tin',
               'Khóa 2024 – 2028 | Hệ chính quy', 46, 'Thứ 3 | 10:15 – 11:00', 'B301'),
        LopHoc(3, 'QTKD2401', 'Quản trị kinh doanh', 'Quản trị kinh doanh',
               'Khóa 2024 – 2028 | Hệ chính quy', 47, 'Thứ 4 | 10:15 – 11:00', 'B301'),
    ])

    PHAN_CONGS.clear()
    PHAN_CONGS.extend([
        PhanCongGiangDay(1, lop_id=1, mon_hoc_id=1, giang_vien_id=1),
        PhanCongGiangDay(2, lop_id=1, mon_hoc_id=2, giang_vien_id=2),
    ])


@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


def decode_html(response):
    return html.unescape(response.data.decode('utf-8'))


# 1. test quản lý môn học

def test_tc01_them_mon_hoc_hop_le(client):
    res = client.post('/mon-hoc', data={
        'ma_mon': 'INT2605',
        'ten_mon': 'Trí tuệ nhân tạo',
        'so_tin_chi': '3',
        'so_tiet': '30 LT | 30 TH',
        'khoa': 'Công nghệ thông tin',
        'mo_ta': 'Nhập môn AI',
    }, follow_redirects=True)
    text = decode_html(res)
    assert res.status_code == 200
    assert 'Thêm môn học thành công!' in text
    assert any(m.ma_mon == 'INT2605' for m in MON_HOCS)


def test_tc02_them_mon_hoc_trung_ma(client):
    res = client.post('/mon-hoc', data={
        'ma_mon': 'CSDL2601',
        'ten_mon': 'Cơ sở dữ liệu nâng cao',
        'so_tin_chi': '3',
        'so_tiet': '30 LT | 30 TH',
        'khoa': 'Công nghệ thông tin',
        'mo_ta': '',
    }, follow_redirects=True)
    text = decode_html(res)
    assert 'Mã môn học đã tồn tại!' in text
    assert len(MON_HOCS) == 4


def test_tc05_sua_mon_hoc_hop_le(client):
    res = client.post('/mon-hoc/sua/1', data={
        'ma_mon': 'CSDL2601',
        'ten_mon': 'Cơ sở dữ liệu ứng dụng',
        'so_tin_chi': '4',
        'so_tiet': '30 LT | 30 TH',
        'khoa': 'Công nghệ thông tin',
        'mo_ta': 'Cập nhật mới',
    }, follow_redirects=True)
    text = decode_html(res)
    assert 'Đã cập nhật thông tin môn học!' in text
    assert MON_HOCS[0].ten_mon == 'Cơ sở dữ liệu ứng dụng'
    assert MON_HOCS[0].so_tin_chi == 4


def test_tc06_sua_mon_hoc_trung_ma_khac(client):
    res = client.post('/mon-hoc/sua/1', data={
        'ma_mon': 'CNPM2601',
        'ten_mon': 'Cơ sở dữ liệu',
        'so_tin_chi': '3',
        'so_tiet': '30 LT | 30 TH',
        'khoa': 'Công nghệ thông tin',
        'mo_ta': '',
    }, follow_redirects=True)
    assert 'Mã môn học mới bị trùng với môn học khác!' in decode_html(res)


def test_tc07_xoa_mon_hoc_hop_le(client):
    # Môn id=3 (LTW2601) chưa được phân công cho lớp nào
    res = client.get('/mon-hoc/xoa/3', follow_redirects=True)
    assert 'Đã xóa môn học.' in decode_html(res)
    assert all(m.id != 3 for m in MON_HOCS)


def test_tc08_xoa_mon_hoc_dang_co_phan_cong(client):
    # Môn id=1 (CSDL2601) đang được phân công cho lớp CNTT2401
    res = client.get('/mon-hoc/xoa/1', follow_redirects=True)
    assert 'Không thể xóa môn học đang có phân công giảng viên cho lớp!' in decode_html(res)
    assert any(m.id == 1 for m in MON_HOCS)


def test_tc09_tim_kiem_mon_hoc_khong_dau(client):
    res = client.get('/mon-hoc?q=co so du lieu')
    text = decode_html(res)
    assert 'CSDL2601' in text
    assert 'CNPM2601' not in text


def test_tc10_tim_kiem_mon_hoc_khong_ton_tai(client):
    res = client.get('/mon-hoc?q=XYZ9999')
    assert 'Hiển thị 0 môn học' in decode_html(res)


# 2. test quản lý giảng viên

def test_tc11_them_giang_vien_hop_le(client):
    res = client.post('/giang-vien', data={
        'ma_gv': 'GV202405',
        'ho_ten': 'Phạm Minh Tuấn',
        'email': 'tuan.pm@gmail.com',
        'khoa': 'Công nghệ thông tin',
        'hoc_vi': 'Thạc sĩ',
        'chuyen_mon': 'Trí tuệ nhân tạo',
    }, follow_redirects=True)
    assert 'Thêm giảng viên thành công!' in decode_html(res)
    assert len(GIANG_VIENS) == 5


def test_tc12_them_giang_vien_trung_ma(client):
    res = client.post('/giang-vien', data={
        'ma_gv': 'GV202401',
        'ho_ten': 'Đỗ Hoàng Nam',
        'email': 'nam.dh@gmail.com',
        'khoa': 'Công nghệ thông tin',
        'hoc_vi': 'Tiến sĩ',
        'chuyen_mon': 'Mạng máy tính',
    }, follow_redirects=True)
    assert 'Mã giảng viên đã tồn tại!' in decode_html(res)
    assert len(GIANG_VIENS) == 4


def test_tc15_sua_giang_vien_hop_le(client):
    res = client.post('/giang-vien/sua/1', data={
        'ma_gv': 'GV202401',
        'ho_ten': 'Lê Thu Hương',
        'email': 'huong.lt@gmail.com',
        'khoa': 'Công nghệ thông tin',
        'hoc_vi': 'Tiến sĩ',
        'chuyen_mon': 'Cơ sở dữ liệu',
    }, follow_redirects=True)
    assert 'Đã cập nhật thông tin giảng viên!' in decode_html(res)
    assert GIANG_VIENS[0].hoc_vi == 'Tiến sĩ'


def test_tc17_xoa_giang_vien_hop_le(client):
    # Giảng viên id=3 (GV202403) chưa có lịch phân công
    res = client.get('/giang-vien/xoa/3', follow_redirects=True)
    assert 'Đã xóa giảng viên.' in decode_html(res)
    assert all(g.id != 3 for g in GIANG_VIENS)


def test_tc18_xoa_giang_vien_dang_co_phan_cong(client):
    # Giảng viên id=1 (GV202401) đang dạy lớp CNTT2401
    res = client.get('/giang-vien/xoa/1', follow_redirects=True)
    assert 'Không thể xóa giảng viên đang có lịch phân công giảng dạy!' in decode_html(res)
    assert any(g.id == 1 for g in GIANG_VIENS)


def test_tc19_tim_kiem_giang_vien_theo_ten_va_khoa(client):
    res = client.get('/giang-vien?q=le thu huong&khoa=Khoa Công nghệ thông tin')
    text = decode_html(res)
    assert 'GV202401' in text
    assert 'Hiển thị 1 giảng viên' in text


def test_tc20_tim_kiem_giang_vien_khong_co_ket_qua(client):
    res = client.get('/giang-vien?q=Nguyen Van Z&khoa=Khoa Y Dược')
    assert 'Không tìm thấy giảng viên nào phù hợp với điều kiện tìm kiếm.' in decode_html(res)


# 3. test quản lý lớp học và phân công giảng dạy

def test_tc21_them_lop_hoc_hop_le(client):
    res = client.post('/lop-hoc', data={
        'ma_lop': 'CNTT2403',
        'ten_lop': 'Công nghệ thông tin 3',
        'nganh': 'Công nghệ thông tin',
        'khoa_hoc': 'Khóa 2024 – 2028 | Hệ chính quy',
        'si_so': '45',
        'lich_hoc': 'Thứ 6 | 10:15 – 11:00',
        'phong': 'B301',
    }, follow_redirects=True)
    assert 'Thêm lớp học thành công!' in decode_html(res)
    assert any(l.ma_lop == 'CNTT2403' for l in LOP_HOCS)


def test_tc22_them_lop_hoc_trung_ma(client):
    res = client.post('/lop-hoc', data={
        'ma_lop': 'CNTT2401',
        'ten_lop': 'Công nghệ thông tin 1',
        'nganh': 'Công nghệ thông tin',
        'khoa_hoc': 'Khóa 2024 – 2028',
        'si_so': '40',
        'lich_hoc': 'Thứ 2 | 07:30 – 09:00',
        'phong': 'B301',
    }, follow_redirects=True)
    assert 'Mã lớp đã tồn tại!' in decode_html(res)


def test_tc26_xoa_lop_hoc_hop_le(client):
    # Lớp id=2 (CNTT2402) chưa có môn học phân công
    res = client.get('/lop-hoc/xoa/2', follow_redirects=True)
    assert 'Đã xóa lớp học.' in decode_html(res)
    assert all(l.id != 2 for l in LOP_HOCS)


def test_tc27_xoa_lop_hoc_dang_co_mon_hoc(client):
    # Lớp id=1 (CNTT2401) đang có 2 môn học phân công
    res = client.get('/lop-hoc/xoa/1', follow_redirects=True)
    assert 'Không thể xóa lớp học đang có môn học được phân công! Hãy gỡ các môn học trước.' in decode_html(res)


def test_tc28_them_mon_hoc_vao_lop_hop_le(client):
    res = client.post('/lop-hoc/phan-cong', data={
        'lop_id': '1',
        'mon_hoc_id': '3',
        'giang_vien_id': '1',
    }, follow_redirects=True)
    assert 'Đã thêm môn Lập trình Web với Python (Lê Thu Hương) vào lớp CNTT2401!' in decode_html(res)
    assert len(LOP_HOCS[0].phan_congs) == 3


def test_tc29_them_mon_hoc_vao_lop_bi_trung(client):
    # Môn id=1 (CSDL2601) đã có sẵn trong lớp id=1 (CNTT2401)
    res = client.post('/lop-hoc/phan-cong', data={
        'lop_id': '1',
        'mon_hoc_id': '1',
        'giang_vien_id': '2',
    }, follow_redirects=True)
    assert 'Môn "Cơ sở dữ liệu" đã được phân công cho lớp CNTT2401 rồi!' in decode_html(res)


def test_tc30_go_mon_hoc_khoi_lop(client):
    res = client.get('/lop-hoc/xoa-phan-cong/2', follow_redirects=True)
    assert 'Đã gỡ môn học khỏi lớp.' in decode_html(res)
    assert len(LOP_HOCS[0].phan_congs) == 1