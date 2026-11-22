"""Chạy thử riêng phần Người 4:   python demo_app.py   rồi mở http://127.0.0.1:5000
(Khi ghép vào project nhóm thì KHÔNG dùng file này, chỉ dùng grades_bp trong app.py.)"""
from flask import Flask, session, redirect, url_for, abort
from controllers.grade_routes import grades_bp

app = Flask(__name__)
app.secret_key = "demo_nguoi4"
app.register_blueprint(grades_bp)

USERS = {"teacher": "GV2026008", "admin": "admin", "student": "SV2024001"}


@app.route("/")
def login():       # giả lập trang đăng nhập của Người 1
    return ('<h3>Demo Người 4</h3><p>Đăng nhập thử với vai trò:</p>'
            '<a href="/demo-login/teacher">Giảng viên (nhập/sửa điểm)</a><br>'
            '<a href="/demo-login/admin">Quản trị viên (chỉ xem)</a><br>'
            '<a href="/demo-login/student">Sinh viên SV2024001 (xem GPA)</a>')


@app.route("/portal")
def portal():
    return redirect(url_for("grades.sheet"))


@app.route("/change-password")
def change_password():
    return "Trang đổi mật khẩu (của Người 1)"


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.route("/demo-login/<role>")
def demo_login(role):
    if role not in USERS:
        abort(404)
    session["role"], session["username"] = role, USERS[role]
    return redirect(url_for("grades.sheet"))


if __name__ == "__main__":
    app.run(debug=True)
