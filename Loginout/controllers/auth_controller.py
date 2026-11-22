from datetime import datetime, timedelta
from data.sample_data import accounts


class AuthController:
    def __init__(self):
        self.current_session = None

    def find_user(self, username):
        for acc in accounts:
            if acc.username.lower() == username.strip().lower():
                return acc
        return None

    def login(self, username, password, role):
        """Kiểm tra đăng nhập. Trả về: (thành_công, ô_lỗi, thông_báo)"""
        username = username.strip()

        if not username:
            return False, "username", "Vui lòng nhập tên đăng nhập."
        if not password:
            return False, "password", "Vui lòng nhập mật khẩu."

        user = self.find_user(username)
        if user is None:
            return False, "both", "Tên đăng nhập hoặc mật khẩu không chính xác."

        if not user.is_active:
            return False, "none", "Tài khoản đã bị khóa. Vui lòng liên hệ Phòng Đào tạo."

        if user.is_locked_temp():
            phut = int((user.locked_until - datetime.now()).total_seconds() // 60) + 1
            return False, "none", f"Tài khoản tạm khóa 15 phút. Vui lòng thử lại sau {phut} phút."

        role_names = {"student": "Sinh viên", "teacher": "Giảng viên", "admin": "Quản trị viên"}
        if user.role != role:
            return False, "none", f"Tài khoản này không thuộc vai trò {role_names[role]}."

        if user.password != password:
            user.failed_attempts += 1
            if user.failed_attempts >= 5:
                user.locked_until = datetime.now() + timedelta(minutes=15)
                user.failed_attempts = 0
                return False, "password", "Bạn đã nhập sai 5 lần. Tài khoản bị khóa tạm thời 15 phút."
            return False, "password", f"Mật khẩu không chính xác (còn {5 - user.failed_attempts} lần thử)."

        user.failed_attempts = 0
        self.current_session = user
        return True, "", "Đăng nhập thành công!"

    def change_password(self, username, current_pw, new_pw, confirm_pw):
        """Kiểm tra và cập nhật mật khẩu mới. Trả về: (thành_công, ô_lỗi, thông_báo)"""
        user = self.find_user(username)
        if user is None:
            return False, "none", "Không tìm thấy thông tin tài khoản."

        if not current_pw:
            return False, "current", "Vui lòng nhập mật khẩu hiện tại."
        if user.password != current_pw:
            return False, "current", "Mật khẩu hiện tại không chính xác."

        if not new_pw:
            return False, "new", "Vui lòng nhập mật khẩu mới."
        if new_pw == current_pw:
            return False, "new", "Mật khẩu mới không được trùng với mật khẩu hiện tại."

        # Kiểm tra độ mạnh: ít nhất 8 ký tự, gồm chữ hoa, chữ thường và số
        has_upper = any(c.isupper() for c in new_pw)
        has_lower = any(c.islower() for c in new_pw)
        has_digit = any(c.isdigit() for c in new_pw)
        if len(new_pw) < 8 or not (has_upper and has_lower and has_digit):
            return False, "new", "Mật khẩu mới phải có ít nhất 8 ký tự, gồm chữ hoa, chữ thường và số."

        if not confirm_pw:
            return False, "confirm", "Vui lòng xác nhận lại mật khẩu mới."
        if new_pw != confirm_pw:
            return False, "confirm", "Xác nhận mật khẩu mới không khớp."

        user.password = new_pw
        return True, "", "Đổi mật khẩu thành công!"

    def logout(self):
        self.current_session = None