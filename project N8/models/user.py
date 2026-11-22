from datetime import datetime


class User:
    def __init__(self, user_id, username, password, full_name, role, is_active=True, ref_id=None):
        self.user_id = user_id
        self.username = username
        self.password = password
        self.full_name = full_name
        self.role = role  # "student", "teacher" hoặc "admin"
        self.is_active = is_active
        self.ref_id = ref_id or username  # Mã SV hoặc mã GV tương ứng
        self.failed_attempts = 0
        self.locked_until = None

    def is_locked_temp(self):
        if self.locked_until and datetime.now() < self.locked_until:
            return True
        self.locked_until = None
        return False