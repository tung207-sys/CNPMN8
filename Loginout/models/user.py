from datetime import datetime


class User:
    def __init__(self, user_id, username, password, full_name, role, is_active=True):
        self.user_id = user_id
        self.username = username
        self.password = password
        self.full_name = full_name
        self.role = role              # "student", "teacher" hoặc "admin"
        self.is_active = is_active    # True: hoạt động, False: bị khóa
        self.failed_attempts = 0      # Đếm số lần nhập sai mật khẩu
        self.locked_until = None      # Thời điểm mở khóa nếu sai quá 5 lần

    def is_locked_temp(self):
        """Kiểm tra tài khoản có đang bị khóa tạm thời 15 phút hay không."""
        if self.locked_until and datetime.now() < self.locked_until:
            return True
        self.locked_until = None
        return False