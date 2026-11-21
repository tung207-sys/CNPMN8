from models.entities import User, Student, Teacher, Class, Course, TeacherAssignment, Grade

accounts = [
    User("U001", "SV001", "123456", "student", "SV001", True),
    User("U002", "SV002", "123456", "student", "SV002", True),
    User("U003", "GV001", "123456", "teacher", "GV001", True),
    User("U004", "GV002", "123456", "teacher", "GV002", True),
]

students = [
    Student(
        "SV001",
        "Nguyễn Văn An",
        "10/01/2005",
        "Nam",
        "123 Võ Oanh, Q. Bình Thạnh, TP. Hồ Chí Minh",
        "an.sv001@uth.edu.vn",
        "CNTT01",
        ethnicity="Kinh",
        nationality="Việt Nam",
        phone="0912 345 678",
        birthplace="TP. Hồ Chí Minh",
        current_address="KTX Khu B, ĐHQG TP.HCM",
        faculty="Khoa CNTT",
        major="Công nghệ thông tin",
        education_level="Đại học",
        training_type="Chính quy",
        cohort="K23",
        academic_year="2025–2026",
        advisor="TS. Trần Thị Mỹ Tiên",
        status="Đang học",
        target_credits=130,
    ),
    Student("SV002", "Trần Thị Bình", "15/03/2005", "Nữ", "Biên Hòa, Đồng Nai", "binh.sv002@uth.edu.vn", "CNTT01"),
    Student("SV003", "Lê Hoàng Cường", "22/07/2005", "Nam", "Thủ Dầu Một, Bình Dương", "cuong.sv003@uth.edu.vn", "CNTT02"),
]

teachers = [
    Teacher(
        "GV001",
        "TS. Trần Thị Tiến",
        "tien.ttm@uth.edu.vn",
        "0901 234 567",
        department="Khoa Công nghệ thông tin",
        degree_title="Tiến sĩ - Giảng viên",
        specialization="Cơ sở dữ liệu, Thiết kế web",
        position_info="Giảng viên cơ hữu • Bộ môn Khoa học máy tính",
    ),
    Teacher(
        "GV002",
        "ThS. Phạm Minh Tuấn",
        "tuan.pm@uth.edu.vn",
        "0907 654 321",
        department="Khoa Công nghệ thông tin",
        degree_title="Thạc sĩ - Giảng viên",
        specialization="Lập trình hướng đối tượng, An toàn bảo mật",
        position_info="Giảng viên cơ hữu • Bộ môn Kỹ thuật phần mềm",
    ),
]

courses = [
    Course("CNTT202", "Cơ sở dữ liệu", 3),
    Course("CNTT205", "Lập trình hướng đối tượng", 3),
    Course("CNTT210", "Thiết kế web", 3),
    Course("CNTT215", "An toàn bảo mật", 3),
    Course("CNTT220", "Hệ điều hành", 3),
]

classes = [
    Class(
        "CNTT01",
        "Công nghệ thông tin 01 - K23",
        2023,
        schedule=[
            {"day": "Thứ 2", "time": "09:00–11:30", "room": "Phòng A.204", "subject_id": "CNTT202", "teacher_id": "GV001", "semester_label": "Học kỳ 1"},
            {"day": "Thứ 3", "time": "13:30–16:00", "room": "Phòng B.107", "subject_id": "CNTT205", "teacher_id": "GV002", "semester_label": "Học kỳ 1"},
            {"day": "Thứ 5", "time": "08:00–10:30", "room": "Phòng C.302", "subject_id": "CNTT210", "teacher_id": "GV001", "semester_label": "Học kỳ 1"},
        ],
    ),
    Class(
        "CNTT02",
        "Công nghệ thông tin 02 - K23",
        2023,
        schedule=[
            {"day": "Thứ 4", "time": "07:30–10:00", "room": "Phòng A.301", "subject_id": "CNTT215", "teacher_id": "GV002", "semester_label": "Học kỳ 1"},
        ],
    ),
]

teacher_assignments = [
    TeacherAssignment("GV001", "CNTT01", "CNTT202"),
    TeacherAssignment("GV001", "CNTT01", "CNTT210"),
    TeacherAssignment("GV002", "CNTT01", "CNTT205"),
    TeacherAssignment("GV002", "CNTT02", "CNTT215"),
]

grades = [
    Grade("SV001", "CNTT202", "HK1-2024", 9.0, 8.5, 8.8),
    Grade("SV001", "CNTT205", "HK2-2024", 8.5, 8.0, 8.2),
    Grade("SV001", "CNTT210", "HK1-2025", 9.5, 9.0, 9.2),
    Grade("SV001", "CNTT215", "HK2-2025", 8.0, 7.5, 8.0),
    Grade("SV001", "CNTT220", "HK2-2025", 8.5, 8.5, 8.5),
    Grade("SV002", "CNTT202", "HK1-2025", 8.0, 7.0, 7.5),
    Grade("SV003", "CNTT215", "HK1-2025", 7.5, 6.5, 7.0),
]