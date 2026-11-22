from flask import Flask, render_template, request, redirect, url_for, session
from controllers.auth_controller import AuthController
from views.student_view import student_bp
from controllers.academic_controller import academic_bp
from controllers.portal_controller import portal_bp
from data.shared_data import students, LOP_HOCS
from controllers.grade_routes import grades_bp

app = Flask(__name__)
app.secret_key = "khoa_bao_mat_session_nhom_08"
auth = AuthController()

# Đăng ký Blueprint của Task 2, Task 3 và Task 5
app.register_blueprint(student_bp, url_prefix="/students")
app.register_blueprint(academic_bp, url_prefix="/academic")
app.register_blueprint(portal_bp)
app.register_blueprint(grades_bp)

def redirect_by_role(role):
    if role == "student":
        return redirect(url_for("portal.student_profile"))
    if role == "teacher":
        return redirect(url_for("portal.teacher_dashboard"))
    return redirect(url_for("portal"))


@app.route("/")
def index():
    if "username" in session:
        return redirect_by_role(session.get("role"))
    return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()
        user, err = auth.authenticate(username, password)
        if err:
            error = err
        else:
            session["user_id"] = user.user_id
            session["username"] = user.username
            session["role"] = user.role
            session["full_name"] = user.full_name
            session["display_name"] = user.full_name
            session["ref_id"] = user.ref_id
            return redirect_by_role(user.role)
    return render_template("login.html", error=error)


@app.route("/portal")
def portal():
    if "username" not in session:
        return redirect(url_for("login"))
    if session.get("role") != "admin":
        return redirect_by_role(session.get("role"))

    from data import shared_data
    ds_sv = getattr(shared_data, "students", [])
    ds_lop = getattr(shared_data, "LOP_HOCS", [])

    tong_sv = len(ds_sv)
    sv_dang_hoc = tong_sv
    sv_bao_luu = 0

    thong_ke_lop = []
    for lop in ds_lop:
        ma = lop.ma_lop
        ten = lop.ten_lop
        so_sv_lop = sum(1 for sv in ds_sv if sv.class_id == ma)
        ty_trong = f"{round(so_sv_lop / tong_sv * 100, 1)}%" if tong_sv > 0 else "0%"

        thong_ke_lop.append({
            "ma_lop": ma,
            "ten_lop": ten,
            "tong_so": so_sv_lop,
            "dang_hoc": so_sv_lop,
            "bao_luu": 0,
            "ty_trong": ty_trong,
        })

    return render_template(
        "portal.html",
        tong_sv=tong_sv,
        tong_lop=len(ds_lop),
        sv_dang_hoc=sv_dang_hoc,
        sv_bao_luu=sv_bao_luu,
        thong_ke_lop=thong_ke_lop,
    )


@app.route("/change-password", methods=["GET", "POST"])
def change_password():
    if "username" not in session:
        return redirect(url_for("login"))
    success = False
    error_field = ""
    msg = None
    if request.method == "POST":
        current_pw = request.form.get("current_pw", "")
        new_pw = request.form.get("new_pw", "")
        confirm_pw = request.form.get("confirm_pw", "")
        ok, err_field, message = auth.change_password(session["username"], current_pw, new_pw, confirm_pw)
        success = ok
        error_field = err_field
        msg = message
    return render_template("change_password.html", success=success, error_field=error_field, msg=msg)


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(debug=True, port=5000)