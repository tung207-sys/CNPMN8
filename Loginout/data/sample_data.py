from models.user import User

accounts = [
    # Tài khoản Sinh viên
    User(1, "SV2024001", "Sv202401", "Nguyễn Minh Anh", "student", True),
    User(2, "SV2024002", "Sv202402", "Trần Đức Huy", "student", True),
    User(3, "SV2024003", "Sv202403", "Lê Hoàng Nam", "student", False),  # Tài khoản bị khóa

    # Tài khoản Giảng viên (khớp mã GV2026008 trong Figma Doc1.docx)
    User(10, "GV2026008", "Gv202608", "TS. Lê Thu Hương", "teacher", True),

    # Tài khoản Quản trị viên
    User(100, "admin", "Admin123", "Quản trị viên", "admin", True),
]