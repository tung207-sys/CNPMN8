import csv
import io
from functools import wraps
from flask import Blueprint, render_template, request, redirect, url_for, session, flash, Response
from data.sample_data import accounts, students, teachers, classes, courses, teacher_assignments, grades

portal_bp = Blueprint("portal", __name__)

#các lớp đọc từ file sample_data.py 

class StudentManager:
    def get_student_by_id(self, student_id):
        return next((s for s in students if s.student_id == student_id), None)

    def filter_by_class(self, class_id):
        return [s for s in students if s.class_id == class_id]


class ClassManager:
    def get_class_by_id(self, class_id):
        return next((c for c in classes if c.class_id == class_id), None)

    def get_course_by_id(self, subject_id):
        return next((c for c in courses if c.subject_id == subject_id), None)


class TeacherManager:
    def get_teacher_by_id(self, teacher_id):
        return next((t for t in teachers if t.teacher_id == teacher_id), None)

    def get_assignments_by_teacher(self, teacher_id):
        return [a for a in teacher_assignments if a.teacher_id == teacher_id]


class GradeManager:
    def get_grades_by_student(self, student_id, semester=None):
        result = [g for g in grades if g.student_id == student_id]
        if semester and semester != "ALL":
            result = [g for g in result if g.semester == semester]
        return result

    def get_grade_sheet(self, class_id, subject_id, semester):
        class_students = [s for s in students if s.class_id == class_id]
        sheet = []
        for st in class_students:
            g = next(
                (
                    item for item in grades
                    if item.student_id == st.student_id
                    and item.subject_id == subject_id
                    and (not semester or semester == "ALL" or item.semester == semester)
                ),
                None,
            )
            sheet.append({"student": st, "grade": g})
        return sheet


class GPAService:
    def __init__(self, grade_manager, class_manager):
        self.grade_manager = grade_manager
        self.class_manager = class_manager

    def calculate_gpa(self, student_id):
        student_grades = self.grade_manager.get_grades_by_student(student_id)
        if not student_grades:
            return {"gpa_4": 0.0, "gpa_10": 0.0, "total_credits": 0}

        total_points_4 = 0.0
        total_points_10 = 0.0
        total_credits = 0

        for g in student_grades:
            course = self.class_manager.get_course_by_id(g.subject_id)
            credits = course.credits if course else 0
            _, point_4 = g.get_letter_and_gpa4()
            total_points_4 += point_4 * credits
            total_points_10 += g.calculate_total() * credits
            total_credits += credits

        if total_credits == 0:
            return {"gpa_4": 0.0, "gpa_10": 0.0, "total_credits": 0}

        return {
            "gpa_4": round(total_points_4 / total_credits, 2),
            "gpa_10": round(total_points_10 / total_credits, 2),
            "total_credits": total_credits,
        }


student_manager = StudentManager()
class_manager = ClassManager()
teacher_manager = TeacherManager()
grade_manager = GradeManager()
gpa_service = GPAService(grade_manager, class_manager)



#các class theo đặc tả

class StudentPortal:
    def __init__(self, student, student_mgr, class_mgr, grade_mgr, gpa_srv, teacher_mgr=None):
        self.student = student
        self.student_manager = student_mgr
        self.class_manager = class_mgr
        self.grade_manager = grade_mgr
        self.gpa_service = gpa_srv
        self.teacher_manager = teacher_mgr or teacher_manager

    def view_personal_information(self):
        class_obj = self.class_manager.get_class_by_id(self.student.class_id)
        return {
            "student": self.student,
            "class_info": class_obj,
        }

    def view_enrolled_classes(self):
        class_obj = self.class_manager.get_class_by_id(self.student.class_id)
        if not class_obj:
            return []
        enrolled = []
        for idx, item in enumerate(class_obj.schedule):
            course = self.class_manager.get_course_by_id(item["subject_id"])
            teacher = self.teacher_manager.get_teacher_by_id(item["teacher_id"])
            enrolled.append({
                "index": idx,
                "class_id": class_obj.class_id,
                "class_name": class_obj.class_name,
                "subject_id": item["subject_id"],
                "subject_name": course.subject_name if course else item["subject_id"],
                "credits": course.credits if course else 0,
                "teacher_name": teacher.full_name if teacher else "Chưa phân công",
                "day": item["day"],
                "time": item["time"],
                "room": item["room"],
                "semester_label": item.get("semester_label", "Học kỳ 1"),
            })
        return enrolled

    def view_class_schedule(self):
        return self.view_enrolled_classes()

    def view_gpa(self):
        return self.gpa_service.calculate_gpa(self.student.student_id)

    def view_grades(self, semester="ALL"):
        raw_grades = self.grade_manager.get_grades_by_student(self.student.student_id, semester)
        detailed = []
        for g in raw_grades:
            course = self.class_manager.get_course_by_id(g.subject_id)
            letter, point_4 = g.get_letter_and_gpa4()
            detailed.append({
                "semester": g.semester,
                "subject_id": g.subject_id,
                "subject_name": course.subject_name if course else g.subject_id,
                "credits": course.credits if course else 0,
                "attendance": g.attendance,
                "midterm": g.midterm,
                "final": g.final,
                "total": g.calculate_total(),
                "letter": letter,
                "point_4": point_4,
            })
        return detailed

    def get_semester_summary_cards(self):
        semester_defs = [
            {"code": "HK1-2024", "short": "HK1 • 2023–2024", "full": "Học kỳ 1 - 2023–2024"},
            {"code": "HK2-2024", "short": "HK2 • 2023–2024", "full": "Học kỳ 2 - 2023–2024"},
            {"code": "HK1-2025", "short": "HK1 • 2024–2025", "full": "Học kỳ 1 - 2024–2025"},
            {"code": "HK2-2025", "short": "HK2 • 2024–2025", "full": "Học kỳ 2 - 2024–2025"},
        ]
        cards = []
        for item in semester_defs:
            sem_grades = self.view_grades(item["code"])
            if sem_grades:
                total_pts = sum(g["point_4"] * g["credits"] for g in sem_grades)
                total_cr = sum(g["credits"] for g in sem_grades)
                sem_gpa = round(total_pts / total_cr, 2) if total_cr > 0 else 0.0
            else:
                sem_gpa = 0.0
            cards.append({
                "code": item["code"],
                "short": item["short"],
                "full": item["full"],
                "gpa": f"{sem_gpa:.2f}",
                "count": len(sem_grades),
            })
        return cards


class TeacherPortal:
    def __init__(self, teacher, teacher_mgr, student_mgr, grade_mgr, class_mgr):
        self.teacher = teacher
        self.teacher_manager = teacher_mgr
        self.student_manager = student_mgr
        self.grade_manager = grade_mgr
        self.class_manager = class_mgr

    def view_assigned_classes(self):
        assignments = self.teacher_manager.get_assignments_by_teacher(self.teacher.teacher_id)
        class_ids = sorted({a.class_id for a in assignments})
        result = []
        for cid in class_ids:
            cls = self.class_manager.get_class_by_id(cid)
            if cls:
                st_count = len(self.student_manager.filter_by_class(cid))
                result.append({
                    "class_id": cls.class_id,
                    "class_name": cls.class_name,
                    "year": cls.year,
                    "student_count": st_count,
                })
        return result

    def view_assigned_subjects(self):
        assignments = self.teacher_manager.get_assignments_by_teacher(self.teacher.teacher_id)
        result = []
        for a in assignments:
            cls = self.class_manager.get_class_by_id(a.class_id)
            course = self.class_manager.get_course_by_id(a.subject_id)
            st_count = len(self.student_manager.filter_by_class(a.class_id))

            sched_item = None
            if cls:
                sched_item = next(
                    (s for s in cls.schedule if s["subject_id"] == a.subject_id),
                    None,
                )

            result.append({
                "class_id": a.class_id,
                "class_name": cls.class_name if cls else a.class_id,
                "subject_id": a.subject_id,
                "subject_name": course.subject_name if course else a.subject_id,
                "credits": course.credits if course else 0,
                "student_count": st_count,
                "day": sched_item["day"] if sched_item else "Chưa xếp lịch",
                "time": sched_item["time"] if sched_item else "—",
                "room": sched_item["room"] if sched_item else "Chưa phân phòng",
            })
        return result

    def view_student_list(self, class_id=None, keyword=""):
        assigned_class_ids = sorted({
            a.class_id for a in self.teacher_manager.get_assignments_by_teacher(self.teacher.teacher_id)
        })
        if class_id and class_id in assigned_class_ids:
            target_classes = [class_id]
        else:
            target_classes = assigned_class_ids

        student_list = []
        for cid in target_classes:
            student_list.extend(self.student_manager.filter_by_class(cid))

        kw = keyword.strip().lower()
        if kw:
            student_list = [
                s for s in student_list
                if kw in s.student_id.lower() or kw in s.full_name.lower()
            ]
        return student_list

    def view_grade_sheet(self, class_id, subject_id, semester="ALL"):
        assignments = self.teacher_manager.get_assignments_by_teacher(self.teacher.teacher_id)
        is_authorized = any(
            a.class_id == class_id and a.subject_id == subject_id for a in assignments
        )
        if not is_authorized:
            return None

        raw_sheet = self.grade_manager.get_grade_sheet(class_id, subject_id, semester)
        formatted = []
        for row in raw_sheet:
            g = row["grade"]
            if g:
                letter, point_4 = g.get_letter_and_gpa4()
                formatted.append({
                    "student": row["student"],
                    "has_grade": True,
                    "semester": g.semester,
                    "attendance": g.attendance,
                    "midterm": g.midterm,
                    "final": g.final,
                    "total": g.calculate_total(),
                    "letter": letter,
                    "point_4": point_4,
                })
            else:
                formatted.append({
                    "student": row["student"],
                    "has_grade": False,
                })
        return formatted

def login_required(role):
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            if "user_id" not in session or session.get("role") != role:
                return redirect(url_for("portal.quick_switch", role=role))
            return f(*args, **kwargs)
        return wrapped
    return decorator


@portal_bp.route("/")
def index():
    return redirect(url_for("portal.student_profile"))


@portal_bp.route("/switch/<role>")
def quick_switch(role):
    acc = next((a for a in accounts if a.role == role and a.is_active), None)
    if not acc:
        return "Không tìm thấy tài khoản test cho vai trò này", 404
    session["user_id"] = acc.user_id
    session["role"] = acc.role
    session["ref_id"] = acc.ref_id
    if role == "teacher":
        return redirect(url_for("portal.teacher_dashboard"))
    return redirect(url_for("portal.student_profile"))


@portal_bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("portal.index"))

#routes student portal
@portal_bp.route("/student/profile")
@login_required("student")
def student_profile():
    st = student_manager.get_student_by_id(session["ref_id"])
    portal = StudentPortal(st, student_manager, class_manager, grade_manager, gpa_service, teacher_manager)
    info = portal.view_personal_information()
    gpa_info = portal.view_gpa()
    enrolled_classes = portal.view_enrolled_classes()
    semester_cards = portal.get_semester_summary_cards()

    selected_sem = request.args.get("sem", "HK2-2025")
    active_sem_obj = next((c for c in semester_cards if c["code"] == selected_sem), semester_cards[-1])
    grade_list = portal.view_grades(active_sem_obj["code"])
    if not grade_list:
        grade_list = portal.view_grades("ALL")

    return render_template(
        "student/profile.html",
        active_tab="profile",
        breadcrumb_title="Thông tin cá nhân",
        student=info["student"],
        class_info=info["class_info"],
        gpa_info=gpa_info,
        enrolled_classes=enrolled_classes,
        semester_cards=semester_cards,
        selected_sem=active_sem_obj["code"],
        active_sem_full=active_sem_obj["full"],
        grade_list=grade_list,
    )


@portal_bp.route("/student/classes")
@login_required("student")
def student_classes():
    st = student_manager.get_student_by_id(session["ref_id"])
    portal = StudentPortal(st, student_manager, class_manager, grade_manager, gpa_service, teacher_manager)
    info = portal.view_personal_information()
    enrolled_classes = portal.view_enrolled_classes()
    schedules = portal.view_class_schedule()
    return render_template(
        "student/classes_schedule.html",
        active_tab="classes",
        breadcrumb_title="Lớp đang học",
        student=info["student"],
        class_info=info["class_info"],
        enrolled_classes=enrolled_classes,
        schedules=schedules,
    )


@portal_bp.route("/student/grades")
@login_required("student")
def student_grades():
    st = student_manager.get_student_by_id(session["ref_id"])
    portal = StudentPortal(st, student_manager, class_manager, grade_manager, gpa_service, teacher_manager)
    selected_semester = request.args.get("semester", "ALL")
    semester_cards = portal.get_semester_summary_cards()
    grade_list = portal.view_grades(selected_semester)
    gpa_info = portal.view_gpa()
    return render_template(
        "student/academic_results.html",
        active_tab="grades",
        breadcrumb_title="Kết quả học tập",
        student=st,
        semester_cards=semester_cards,
        selected_semester=selected_semester,
        grade_list=grade_list,
        gpa_info=gpa_info,
    )


@portal_bp.route("/student/grades/export")
@login_required("student")
def student_export_grades():
    st = student_manager.get_student_by_id(session["ref_id"])
    portal = StudentPortal(st, student_manager, class_manager, grade_manager, gpa_service, teacher_manager)
    all_grades = portal.view_grades("ALL")

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Ma SV", "Ho Ten", "Hoc Ky", "Ma Hoc Phan", "Ten Hoc Phan", "Tin Chi", "Diem He 10", "Diem He 4", "Diem Chu"])
    for g in all_grades:
        writer.writerow([
            st.student_id, st.full_name, g["semester"], g["subject_id"],
            g["subject_name"], g["credits"], g["total"], g["point_4"], g["letter"]
        ])

    return Response(
        "\ufeff" + output.getvalue(),
        mimetype="text/csv; charset=utf-8",
        headers={"Content-Disposition": f"attachment; filename=BangDiem_{st.student_id}.csv"},
    )


#routes teacher portal
@portal_bp.route("/teacher/dashboard")
@login_required("teacher")
def teacher_dashboard():
    gv = teacher_manager.get_teacher_by_id(session["ref_id"])
    portal = TeacherPortal(gv, teacher_manager, student_manager, grade_manager, class_manager)
    assigned_classes = portal.view_assigned_classes()
    assigned_subjects = portal.view_assigned_subjects()

    total_credits = sum(s["credits"] for s in assigned_subjects)
    total_students = sum(c["student_count"] for c in assigned_classes)
    if assigned_classes:
        breakdown_parts = [str(c["student_count"]) for c in assigned_classes]
        student_breakdown = f"{' + '.join(breakdown_parts)} sinh viên"
    else:
        student_breakdown = "0 sinh viên"

    return render_template(
        "teacher/profile_classes.html",
        active_tab="profile",
        breadcrumb_title="Thông tin & phân công",
        teacher=gv,
        assigned_classes=assigned_classes,
        assigned_subjects=assigned_subjects,
        total_credits=total_credits,
        total_students=total_students,
        student_breakdown=student_breakdown,
    )


@portal_bp.route("/teacher/students")
@login_required("teacher")
def teacher_students():
    gv = teacher_manager.get_teacher_by_id(session["ref_id"])
    portal = TeacherPortal(gv, teacher_manager, student_manager, grade_manager, class_manager)
    assigned_classes = portal.view_assigned_classes()
    assigned_subjects = portal.view_assigned_subjects()

    default_subject = assigned_subjects[0]["subject_id"] if assigned_subjects else ""
    selected_class = request.args.get("class_id", "")
    selected_subject = request.args.get("subject_id", default_subject)
    keyword = request.args.get("keyword", "")

    student_list = portal.view_student_list(selected_class, keyword)

    banner_class = selected_class if selected_class else (assigned_classes[0]["class_id"] if assigned_classes else "")
    matched_subj = next(
        (s for s in assigned_subjects if s["subject_id"] == selected_subject and (not banner_class or s["class_id"] == banner_class)),
        assigned_subjects[0] if assigned_subjects else None,
    )
    active_banner = None
    if banner_class and matched_subj:
        active_banner = {
            "class_id": banner_class,
            "subject_id": matched_subj["subject_id"],
            "subject_name": matched_subj["subject_name"],
            "credits": matched_subj["credits"],
        }

    return render_template(
        "teacher/student_list.html",
        active_tab="students",
        breadcrumb_title="Danh sách sinh viên",
        teacher=gv,
        assigned_classes=assigned_classes,
        assigned_subjects=assigned_subjects,
        selected_class=selected_class,
        selected_subject=selected_subject,
        keyword=keyword,
        student_list=student_list,
        active_banner=active_banner,
    )


@portal_bp.route("/teacher/students/export")
@login_required("teacher")
def teacher_export_students():
    gv = teacher_manager.get_teacher_by_id(session["ref_id"])
    portal = TeacherPortal(gv, teacher_manager, student_manager, grade_manager, class_manager)
    selected_class = request.args.get("class_id", "")
    keyword = request.args.get("keyword", "")
    student_list = portal.view_student_list(selected_class, keyword)

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["STT", "Ma Sinh Vien", "Ho Va Ten", "Lop", "Email"])
    for idx, st in enumerate(student_list, start=1):
        writer.writerow([idx, st.student_id, st.full_name, st.class_id, st.email])

    return Response(
        "\ufeff" + output.getvalue(),
        mimetype="text/csv; charset=utf-8",
        headers={"Content-Disposition": f"attachment; filename=DanhSachSinhVien_{gv.teacher_id}.csv"},
    )


@portal_bp.route("/teacher/grade-sheet")
@login_required("teacher")
def teacher_grade_sheet():
    gv = teacher_manager.get_teacher_by_id(session["ref_id"])
    portal = TeacherPortal(gv, teacher_manager, student_manager, grade_manager, class_manager)
    assigned_classes = portal.view_assigned_classes()
    assigned_subjects = portal.view_assigned_subjects()

    default_class = assigned_subjects[0]["class_id"] if assigned_subjects else ""
    default_subject = assigned_subjects[0]["subject_id"] if assigned_subjects else ""

    selected_class = request.args.get("class_id", default_class)
    selected_subject = request.args.get("subject_id", default_subject)
    selected_semester = request.args.get("semester", "ALL")

    grade_sheet = None
    if selected_class and selected_subject:
        grade_sheet = portal.view_grade_sheet(selected_class, selected_subject, selected_semester)

    return render_template(
        "teacher/grade_sheet.html",
        active_tab="grade_sheet",
        breadcrumb_title="Điểm & bảng điểm",
        teacher=gv,
        assigned_classes=assigned_classes,
        assigned_subjects=assigned_subjects,
        selected_class=selected_class,
        selected_subject=selected_subject,
        selected_semester=selected_semester,
        grade_sheet=grade_sheet,
    )