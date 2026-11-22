import os

from flask import Flask, render_template, request, redirect, url_for, session, make_response
from controllers.auth_controller import AuthController

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY")
if not app.secret_key:
    raise RuntimeError("Set the FLASK_SECRET_KEY environment variable before starting the app.")
auth = AuthController()

# Dữ liệu thống kê mẫu cho trang Tổng quan của Quản trị viên
CLASS_STATS = [
    {"code": "CNTT2401", "name": "Công nghệ thông tin 1", "total": 48, "active": 47, "reserved": 1, "ratio": "25.8%"},
    {"code": "CNTT2402", "name": "Công nghệ thông tin 2", "total": 46, "active": 45, "reserved": 1, "ratio": "24.7%"},
    {"code": "QTKD2401", "name": "Quản trị kinh doanh",   "total": 47, "active": 45, "reserved": 2, "ratio": "25.3%"},
    {"code": "NNA2401",  "name": "Ngôn ngữ Anh",          "total": 45, "active": 43, "reserved": 2, "ratio": "24.2%"},
]


@app.route("/")
def home():
    if "username" in session:
        return redirect(url_for("portal"))
    return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if "username" in session:
        return redirect(url_for("portal"))

    remembered_user = request.cookies.get("remembered_user", "")
    remembered_role = request.cookies.get("remembered_role", "student")

    role = remembered_role
    username = remembered_user
    error_field = ""
    error_msg = ""

    if request.method == "POST":
        role = request.form.get("role", "student")
        username = request.form.get("username", "")
        password = request.form.get("password", "")
        remember = request.form.get("remember") == "on"

        ok, error_field, error_msg = auth.login(username, password, role)

        if ok:
            session["username"] = auth.current_session.username
            session["role"] = auth.current_session.role

            resp = make_response(redirect(url_for("portal")))
            if remember:
                resp.set_cookie("remembered_user", auth.current_session.username, max_age=7 * 24 * 3600)
                resp.set_cookie("remembered_role", auth.current_session.role, max_age=7 * 24 * 3600)
            else:
                resp.delete_cookie("remembered_user")
                resp.delete_cookie("remembered_role")
            return resp

    return render_template(
        "login.html",
        role=role,
        username=username,
        remembered=bool(remembered_user),
        error_field=error_field,
        error_msg=error_msg
    )


@app.route("/portal")
def portal():
    if "username" not in session:
        return redirect(url_for("login"))

    user = auth.find_user(session["username"])
    if user is None:
        session.clear()
        return redirect(url_for("login"))

    summary = {
        "total_students": sum(c["total"] for c in CLASS_STATS),
        "total_classes": len(CLASS_STATS),
        "active_students": sum(c["active"] for c in CLASS_STATS),
        "reserved_students": sum(c["reserved"] for c in CLASS_STATS),
    }

    resp = make_response(render_template("portal.html", user=user, classes=CLASS_STATS, summary=summary))
    resp.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    return resp


@app.route("/change-password", methods=["GET", "POST"])
def change_password():
    if "username" not in session:
        return redirect(url_for("login"))

    error_field = ""
    msg = ""
    success = False

    if request.method == "POST":
        current_pw = request.form.get("current_pw", "")
        new_pw = request.form.get("new_pw", "")
        confirm_pw = request.form.get("confirm_pw", "")

        success, error_field, msg = auth.change_password(
            session["username"], current_pw, new_pw, confirm_pw
        )

    return render_template(
        "change_password.html",
        error_field=error_field,
        msg=msg,
        success=success
    )


@app.route("/logout")
def logout():
    auth.logout()
    session.clear()
    resp = make_response(redirect(url_for("login")))
    resp.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    return resp


if __name__ == "__main__":
    app.run(debug=True)