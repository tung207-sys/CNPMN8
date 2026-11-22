"""Các route của phần Người 4 (Blueprint). Gắn vào app.py bằng 2 dòng:

    from controllers.grade_routes import grades_bp
    app.register_blueprint(grades_bp)
"""
from flask import (Blueprint, render_template, request, session, redirect,
                   url_for, flash, abort)

from controllers.grade_controller import GradeManager, SEMESTERS
from models.grade import Grade
from services.gpa_service import GPAService
from services.grade_service import to_letter, to_gpa4

# Ưu tiên dùng dữ liệu chung của nhóm (data/sample_data.py); không có thì dùng dữ liệu demo.
try:
    from data import sample_data as _sd
    students, courses, grades = _sd.students, _sd.courses, _sd.grades
    assignments = getattr(_sd, "teacher_assignments", [])
except (ImportError, AttributeError):
    from data.grade_demo_data import students, courses, grades
    assignments = []

gm = GradeManager(grades, students, assignments)
gpa = GPAService(grades, courses)
grades_bp = Blueprint("grades", __name__, url_prefix="/grades")


def _fmt(v):
    """9.0 -> '9', 7.5 -> '7.5', chuỗi giữ nguyên."""
    if isinstance(v, (int, float)):
        return str(int(v)) if float(v) == int(v) else str(v)
    return v


def _calc(vals):
    """Trả về (tổng kết, hệ 4, điểm chữ) nếu đủ 3 điểm hợp lệ, ngược lại None."""
    try:
        a, m, f = (float(str(v).replace(",", ".")) for v in vals)
    except ValueError:
        return None
    if not all(0 <= x <= 10 for x in (a, m, f)):
        return None
    t = Grade("", "", "", a, m, f).calculate_total()
    return round(t, 2), to_gpa4(t), to_letter(t)


@grades_bp.route("/", methods=["GET", "POST"])
def sheet():
    if "username" not in session:
        return redirect(url_for("login"))
    role = session.get("role")
    if role not in ("teacher", "admin"):
        return redirect(url_for("grades.results"))

    classes = sorted({s.class_id for s in students})
    class_id = request.values.get("class_id", classes[0])
    semester = request.values.get("semester", SEMESTERS[0])
    subject_id = request.values.get("subject_id", courses[0].subject_id)
    if class_id not in classes:
        class_id = classes[0]
    if semester not in SEMESTERS:
        semester = SEMESTERS[0]
    if subject_id not in {c.subject_id for c in courses}:
        subject_id = courses[0].subject_id
    can_edit = role == "teacher"          # quản trị viên chỉ được xem
    course = next(c for c in courses if c.subject_id == subject_id)

    errors, posted = {}, None
    if request.method == "POST":
        if not can_edit:
            abort(403)
        posted = {s.student_id: tuple(request.form.get(f"{k}_{s.student_id}", "")
                                      for k in ("att", "mid", "fin"))
                  for s in gm.class_students(class_id)}
        errors, n = gm.save_sheet(class_id, subject_id, semester, posted)
        if not errors:
            flash(f"Đã lưu cập nhật cho {n} sinh viên." if n else "Không có thay đổi nào để lưu.")
            return redirect(url_for("grades.sheet", class_id=class_id,
                                    semester=semester, subject_id=subject_id))

    saved = {g.student_id: g for g in gm.get_grade_sheet(class_id, subject_id, semester)}
    rows = []
    for s in gm.class_students(class_id):
        g = saved.get(s.student_id)
        orig = (_fmt(g.attendance), _fmt(g.midterm), _fmt(g.final)) if g else ("", "", "")
        vals = tuple(_fmt(v) for v in posted[s.student_id]) if posted else orig
        rows.append({"id": s.student_id, "name": s.full_name, "vals": vals, "orig": orig,
                     "calc": _calc(vals), "status": "saved" if g else "none",
                     "error": errors.get(s.student_id)})
    stats = {"total": len(rows),
             "saved": sum(r["status"] == "saved" for r in rows),
             "none": sum(r["status"] == "none" for r in rows)}
    return render_template("grades.html", rows=rows, stats=stats, classes=classes,
                           class_id=class_id, semester=semester, semesters=SEMESTERS,
                           courses=courses, course=course, can_edit=can_edit,
                           role=role, errors=errors, active="sheet")


@grades_bp.route("/results")
def results():
    if "username" not in session:
        return redirect(url_for("login"))
    role = session.get("role")
    if role == "student":                 # sinh viên chỉ xem điểm của chính mình
        sid = session["username"]
    else:
        sid = request.args.get("student_id", students[0].student_id)
    student = next((s for s in students if s.student_id == sid), None)
    data = None
    if student:
        data = {"gpa": gpa.calculate_gpa(sid), "credits": gpa.total_credits(sid),
                "blocks": gpa.semester_summary(sid, SEMESTERS)}
    return render_template("results.html", student=student, data=data, role=role,
                           students=students, sid=sid, active="results")
