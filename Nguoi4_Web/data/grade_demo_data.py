"""Dữ liệu demo để chạy riêng phần Người 4.
Khi ghép project, grade_routes.py sẽ ưu tiên dùng data/sample_data.py của nhóm."""
from types import SimpleNamespace as NS
from models.grade import Grade

HK1, HK2 = "HK1 2026-2027", "HK2 2025-2026"
_names = ["Nguyễn Minh Anh", "Trần Đức Huy", "Nguyễn Tuấn Kiệt", "Lê Bảo Ngọc",
          "Phạm Hải Đăng", "Võ Thùy Dương", "Đặng Quốc Bảo", "Trương Ngọc Hân",
          "Hoàng Gia Bảo", "Bùi Thanh Tâm", "Lý Khánh Vy", "Đỗ Minh Quân"]

students = [NS(student_id=f"SV2024{i + 1:03d}", full_name=n, class_id="CNTT2401")
            for i, n in enumerate(_names)]
courses = [NS(subject_id="CTDL2401", subject_name="Cấu trúc dữ liệu và giải thuật", credits=3),
           NS(subject_id="CSDL2401", subject_name="Cơ sở dữ liệu", credits=3)]
grades = [
    Grade("SV2024001", "CTDL2401", HK1, 10, 9, 9),
    Grade("SV2024002", "CTDL2401", HK1, 9, 8, 7.5),
    Grade("SV2024003", "CTDL2401", HK1, 9, 8, 8.5),
    Grade("SV2024004", "CTDL2401", HK1, 8, 7, 8),
    Grade("SV2024005", "CTDL2401", HK1, 8, 6, 6.5),
    Grade("SV2024001", "CTDL2401", HK2, 9, 8, 8.5),
    Grade("SV2024001", "CSDL2401", HK2, 10, 9, 9),
    Grade("SV2024002", "CTDL2401", HK2, 8, 6, 6),
]
