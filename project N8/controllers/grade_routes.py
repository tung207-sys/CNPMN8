from types import SimpleNamespace
from flask import (Blueprint, render_template, request, session, redirect,
                   url_for, flash, abort)

from controllers.grade_controller import GradeManager, SEMESTERS
from models.grade import Grade
from services.gpa_service import GPAService
from services.grade_service import to_letter, to_gpa4

# Dùng dữ liệu dùng chung của project N8 (data/shared_data.py)
from data import shared_data as _sd

students = _sd.students
courses = _sd.MON_HOCS
grades = _sd.GRADES
assignments = getattr(_sd, "PHAN_CONGS", [])

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


def _get_semesters():
    """Giữ danh sách học kỳ chuẩn và tự bổ sung nếu shared_data có học kỳ khác."""
    sems = list(SEMESTERS)
    for g in grades:
        if g.semester and g.semester not in sems:
            sems.append(g.semester)
    return sems


@grades_bp.route("/", methods=["GET", "POST"])
def sheet():
    if "username" not in session:
        return redirect(url_for("login"))
    role = session.get("role")
    if role not in ("teacher", "admin"):
        return redirect(url_for("grades.results"))

    ref_id = session.get("ref_id") or session.get("username")
    can_edit = (role == "teacher")  # quản trị viên chỉ được xem

    # Lọc lớp & môn theo phân công nếu là giảng viên; admin xem toàn bộ
    if role == "teacher":
        my_assigns = [a for a in assignments if a.teacher_id == ref_id]
        classes = sorted({a.class_id for a in my_assigns})
    else:
        my_assigns = []
        classes = sorted({s.class_id for s in students})

    semesters = _get_semesters()
    class_id = request.values.get("class_id", classes[0] if classes else "")
    if classes and class_id not in classes:
        class_id = classes[0]

    if role == "teacher":
        class_subj_ids = {a.subject_id for a in my_assigns if a.class_id == class_id}
        all_subj_ids = {a.subject_id for a in my_assigns}
        target_ids = class_subj_ids or all_subj_ids
        avail_courses = [c for c in courses if c.subject_id in target_ids]
    else:
        avail_courses = list(courses)

    semester = request.values.get("semester", semesters[0] if semesters else "")
    if semesters and semester not in semesters:
        semester = semesters[0]

    default_subj = avail_courses[0].subject_id if avail_courses else ""
    subject_id = request.values.get("subject_id", default_subj)
    if avail_courses and subject_id not in {c.subject_id for c in avail_courses}:
        subject_id = avail_courses[0].subject_id

    course = next(
        (c for c in avail_courses if c.subject_id == subject_id),
        SimpleNamespace(subject_id="", subject_name="Chưa có học phần phân công", credits=0),
    )

    errors, posted = {}, None
    if request.method == "POST":
        if not can_edit:
            abort(403)
        posted = {
            s.student_id: tuple(request.form.get(f"{k}_{s.student_id}", "")
                                for k in ("att", "mid", "fin"))
            for s in gm.class_students(class_id)
        }
        try:
            errors, n = gm.save_sheet(class_id, subject_id, semester, posted, teacher_id=ref_id)
        except PermissionError as err:
            flash(str(err))
            return redirect(url_for("grades.sheet", class_id=class_id,
                                    semester=semester, subject_id=subject_id))
        if not errors:
            flash(f"Đã lưu cập nhật cho {n} sinh viên." if n else "Không có thay đổi nào để lưu.")
            return redirect(url_for("grades.sheet", class_id=class_id,
                                    semester=semester, subject_id=subject_id))

    saved = {g.student_id: g for g in gm.get_grade_sheet(class_id, subject_id, semester)} if class_id and subject_id else {}
    rows = []
    for s in (gm.class_students(class_id) if class_id else []):
        g = saved.get(s.student_id)
        orig = (_fmt(g.attendance), _fmt(g.midterm), _fmt(g.final)) if g else ("", "", "")
        vals = tuple(_fmt(v) for v in posted[s.student_id]) if posted else orig
        rows.append({
            "id": s.student_id,
            "name": s.full_name,
            "vals": vals,
            "orig": orig,
            "calc": _calc(vals),
            "status": "saved" if g else "none",
            "error": errors.get(s.student_id),
        })
    stats = {
        "total": len(rows),
        "saved": sum(r["status"] == "saved" for r in rows),
        "none": sum(r["status"] == "none" for r in rows),
    }

    teacher = None
    if role == "teacher":
        gv = next(
            (g for g in getattr(_sd, "GIANG_VIENS", []) if g.ma_gv == ref_id),
            None,
        )
        if gv:
            teacher = SimpleNamespace(
                teacher_id=gv.ma_gv,
                full_name=gv.ho_ten,
                department=f"Khoa {gv.khoa}",
            )

    return render_template(
        "grades.html",
        rows=rows,
        stats=stats,
        classes=classes,
        class_id=class_id,
        semester=semester,
        semesters=semesters,
        courses=avail_courses,
        course=course,
        can_edit=can_edit,
        role=role,
        errors=errors,
        teacher=teacher,
        active="sheet",
        active_tab="grade_edit",
        breadcrumb_title="Nhập điểm & bảng điểm",
    )


@grades_bp.route("/results")
def results():
    if "username" not in session:
        return redirect(url_for("login"))
    role = session.get("role")
    if role == "student":  # sinh viên chỉ xem điểm của chính mình
        sid = session.get("ref_id") or session["username"]
    else:
        sid = request.args.get("student_id", students[0].student_id if students else "")
    student = next((s for s in students if s.student_id == sid), None)
    data = None
    if student:
        semesters = _get_semesters()
        data = {
            "gpa": gpa.calculate_gpa(sid),
            "credits": gpa.total_credits(sid),
            "blocks": gpa.semester_summary(sid, semesters),
        }
    return render_template(
        "results.html",
        student=student,
        data=data,
        role=role,
        students=students,
        sid=sid,
        active="results",
    )