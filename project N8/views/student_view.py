from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from models.student import Student
from controllers.student_controller import StudentManager

student_bp = Blueprint("student_view", __name__)
manager = StudentManager()

@student_bp.before_request
def check_admin():
    if "username" not in session or session.get("role") != "admin":
        flash("Vui lòng đăng nhập tài khoản Quản trị viên.", "error")
        return redirect(url_for("login"))

@student_bp.route("/", methods=["GET"])
def index():
    search_type = request.args.get("search_type", "id")
    keyword = request.args.get("keyword", "").strip()
    selected_class = request.args.get("class_id", "Tất cả")

    all_students = manager.get_all_students()
    classes = manager.get_all_classes()

    # Thống kê số lượng sinh viên theo từng lớp cho thẻ tổng quan 
    class_stats = []
    for cls in classes:
        count = len(manager.filter_by_class(cls))
        class_stats.append({"class_id": cls, "count": count})

    # Xử lý tìm kiếm (UC05, UC06) và lọc theo lớp (UC07)
    if keyword:
        if search_type == "id":
            students = manager.search_by_id(keyword)
        else:
            students = manager.search_by_name(keyword)
        if selected_class and selected_class != "Tất cả":
            students = [s for s in students if s.class_id.lower() == selected_class.lower()]
    elif selected_class and selected_class != "Tất cả":
        students = manager.filter_by_class(selected_class)
    else:
        students = all_students

    return render_template(
        "students.html",
        students=students,
        total_students=len(all_students),
        classes=classes,
        class_stats=class_stats,
        search_type=search_type,
        keyword=keyword,
        selected_class=selected_class,
    )


@student_bp.route("/add", methods=["POST"])
def add_student():
    try:
        new_student = Student(
            student_id=request.form.get("student_id", ""),
            full_name=request.form.get("full_name", ""),
            dob=request.form.get("dob", ""),
            gender=request.form.get("gender", ""),
            address=request.form.get("address", ""),
            email=request.form.get("email", ""),
            class_id=request.form.get("class_id", ""),
        )
        manager.add_student(new_student)
        flash("Thêm sinh viên mới thành công!", "success")
    except ValueError as err:
        flash(str(err), "error")
    return redirect(url_for("student_view.index"))


@student_bp.route("/update", methods=["POST"])
def update_student():
    student_id = request.form.get("student_id", "").strip()
    if not student_id:
        flash("Không xác định được mã sinh viên cần cập nhật!", "error")
        return redirect(url_for("student_view.index"))

    try:
        updated_data = {
            "full_name": request.form.get("full_name", ""),
            "dob": request.form.get("dob", ""),
            "gender": request.form.get("gender", ""),
            "address": request.form.get("address", ""),
            "email": request.form.get("email", ""),
            "class_id": request.form.get("class_id", ""),
        }
        manager.update_student(student_id, updated_data)
        flash(f"Đã cập nhật thông tin sinh viên '{student_id}'!", "success")
    except ValueError as err:
        flash(str(err), "error")
    return redirect(url_for("student_view.index"))


@student_bp.route("/delete", methods=["POST"])
def delete_student():
    student_id = request.form.get("student_id", "").strip()
    try:
        manager.delete_student(student_id)
        flash(f"Đã xóa sinh viên '{student_id}' khỏi danh sách!", "success")
    except ValueError as err:
        flash(str(err), "error")
    return redirect(url_for("student_view.index"))