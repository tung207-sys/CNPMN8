from models.user import User
from models.student import Student
from models.academic import GiangVien, MonHoc, LopHoc, PhanCongGiangDay
from models.grade import Grade

# 1. Dữ liệu tài khoản (Task 1 - khớp ref_id với SV001, SV002, GV202401, GV202402)
accounts = [
    User(1, "SV001", "Sv202401", "Phạm Dương Hoàng Phúc", "student", True, ref_id="SV001"),
    User(2, "SV002", "Sv202402", "Nguyễn Thanh Vy", "student", True, ref_id="SV002"),
    User(3, "SV003", "Sv202403", "Nguyễn Minh Huy", "student", False, ref_id="SV003"),  # Tài khoản bị khóa
    User(10, "GV202401", "Gv202401", "ThS. Lê Thu Hương", "teacher", True, ref_id="GV202401"),
    User(11, "GV202402", "Gv202402", "TS. Nguyễn Văn An", "teacher", True, ref_id="GV202402"),
    User(100, "admin", "Admin123", "Quản trị viên", "admin", True, ref_id="AD001"),
]

# 2. Dữ liệu sinh viên (Task 2 - giữ nguyên danh sách & mã lớp của project N8)
students = [
    Student(
        "SV001", "Phạm Dương Hoàng Phúc", "31/05/2007", "Nam",
        "Quận 3, TP.HCM", "hoangphuc310507@gmail.com", "CNTT2401",
        phone="0912 345 678", major="Công nghệ thông tin", advisor="ThS. Lê Thu Hương"
    ),
    Student(
        "SV002", "Nguyễn Thanh Vy", "20/05/2007", "Nữ",
        "Tân Phú, TP.HCM", "thanhvy20052007@gmail.com", "CNTT2402",
        phone="0908 112 233", major="Công nghệ thông tin", advisor="TS. Nguyễn Văn An"
    ),
    Student(
        "SV003", "Nguyễn Minh Huy", "25/04/2007", "Nam",
        "Quận 3, TP.HCM", "ngminhhuy25042007@gmail.com", "QTKD2401",
        faculty="Khoa Quản trị kinh doanh", major="Quản trị kinh doanh", advisor="TS. Trần Minh Tâm"
    ),
    Student("SV004", "Võ Đại Phúc", "05/01/2007", "Nam", "Bình Thạnh, TP.HCM", "phucVD@gmail.com", "CNTT2401"),
    Student("SV005", "Trần Thanh Tùng", "19/09/2007", "Nam", "Bình Thạnh, TP.HCM", "TungTT@gmail.com", "CNTT2401"),
    Student("SV006", "Bùi Trương Vĩnh Phú", "15/07/2007", "Nam", "Bà Rịa, TP.HCM", "PhuBRVT@gmail.com", "CNTT2402"),
    Student("SV007", "Đặng Gia Huy", "12/08/2007", "Nam", "Quận 7, TP.HCM", "huy.dg@gmail.com", "CNTT2402"),
    Student(
        "SV008", "Bùi Ngọc Lan", "25/12/2007", "Nữ",
        "Quận 10, TP.HCM", "lan.bn@gmail.com", "QTKD2401",
        faculty="Khoa Quản trị kinh doanh", major="Quản trị kinh doanh", advisor="TS. Trần Minh Tâm"
    ),
]

# 3. Dữ liệu giảng viên, môn học, lớp học, phân công (Task 3)
GIANG_VIENS = [
    GiangVien(1, 'GV202401', 'Lê Thu Hương', 'huong.lt@gmail.com',
              'Công nghệ thông tin', 'Thạc sĩ', 'Cơ sở dữ liệu & Hệ thống thông tin'),
    GiangVien(2, 'GV202402', 'Nguyễn Văn An', 'an.nv@gmail.com',
              'Công nghệ thông tin', 'Tiến sĩ', 'Công nghệ phần mềm'),
    GiangVien(3, 'GV202403', 'Trần Minh Tâm', 'tam.tm@gmail.com',
              'Quản trị kinh doanh', 'Tiến sĩ', 'Quản trị chiến lược'),
    GiangVien(4, 'GV202404', 'Phạm Lan Anh', 'anh.pl@gmail.com',
              'Ngôn ngữ Anh', 'Thạc sĩ', 'Tiếng Anh thương mại'),
]

MON_HOCS = [
    MonHoc(1, 'CSDL2601', 'Cơ sở dữ liệu', 3, 'Công nghệ thông tin',
           '30 LT | 30 TH', 'Thiết kế ERD, chuẩn hóa dữ liệu, đại số quan hệ và truy vấn SQL.'),
    MonHoc(2, 'CNPM2601', 'Công nghệ phần mềm', 3, 'Công nghệ thông tin',
           '30 LT | 30 TH', 'Quy trình phát triển phần mềm, đặc tả yêu cầu và thiết kế sơ đồ UML.'),
    MonHoc(3, 'LTW2601', 'Lập trình Web', 4, 'Công nghệ thông tin',
           '30 LT | 60 TH', 'Xây dựng ứng dụng Web bằng Flask và giao diện Bootstrap.'),
    MonHoc(4, 'QTKD2602', 'Quản trị chiến lược', 3, 'Quản trị kinh doanh',
           '45 LT | 0 TH', 'Hoạch định, triển khai và đánh giá chiến lược kinh doanh doanh nghiệp.'),
]

LOP_HOCS = [
    LopHoc(1, 'CNTT2401', 'Công nghệ thông tin 1', 'Công nghệ thông tin',
           'Khóa 2024 | Hệ chính quy', 48, 'Thứ 2 | 10:15 – 11:00', 'B301'),
    LopHoc(2, 'CNTT2402', 'Công nghệ thông tin 2', 'Công nghệ thông tin',
           'Khóa 2024 | Hệ chính quy', 46, 'Thứ 3 | 10:15 – 11:00', 'D107'),
    LopHoc(3, 'QTKD2401', 'Quản trị kinh doanh', 'Quản trị kinh doanh',
           'Khóa 2024 | Hệ chính quy', 47, 'Thứ 4 | 10:15 – 11:00', 'C103'),
]

PHAN_CONGS = [
    PhanCongGiangDay(1, lop_id=1, mon_hoc_id=1, giang_vien_id=1),
    PhanCongGiangDay(2, lop_id=1, mon_hoc_id=2, giang_vien_id=2),
    PhanCongGiangDay(3, lop_id=2, mon_hoc_id=3, giang_vien_id=1),
]

# 4. Dữ liệu điểm mẫu (Task 5 - khớp mã SV và mã môn của project N8)
GRADES = [
    Grade("SV001", "CSDL2601", "HK1-2024", 9.0, 8.5, 8.8),
    Grade("SV001", "CNPM2601", "HK2-2024", 8.5, 8.0, 8.2),
    Grade("SV001", "LTW2601", "HK2-2025", 9.5, 9.0, 9.2),
    Grade("SV004", "CSDL2601", "HK1-2025", 8.0, 7.5, 8.0),
    Grade("SV005", "CSDL2601", "HK1-2025", 8.5, 8.5, 8.5),
    Grade("SV002", "LTW2601", "HK1-2025", 8.0, 7.0, 7.5),
    Grade("SV006", "LTW2601", "HK1-2025", 7.5, 6.5, 7.0),
]