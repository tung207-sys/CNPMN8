import csv
import io
import re
from functools import wraps
from types import SimpleNamespace
from flask import Blueprint, render_template, request, redirect, url_for, session, Response
from controllers.student_controller import StudentManager
from data.shared_data import GIANG_VIENS, MON_HOCS, LOP_HOCS, PHAN_CONGS, GRADES

portal_bp = Blueprint("portal", __name__)


# =========================================================
# 0. ADAPTER KẾT NỐI DỮ LIỆU CHUNG TỪ TASK 2 & TASK 3
# =========================================================
class ClassManagerAdapter:
    def get_class_by_id(self, class_id):
        lop = next((l for l in LOP_HOCS if l.ma_lop == class_id), None)
        if not lop:
            return None

        # Tự động lấy danh sách môn học & giảng viên được phân công cho lớp từ Task 3
        schedule = []
        time_slots = ["07:30–10:00", "10:15–12:30", "13:30–16:00", "15:45–18:00"]
        for idx, pc in enumerate(lop.phan_congs):
            mon = pc.mon_hoc
            gv = pc.giang_vien
            lich_parts = [p.strip() for p in str(lop.lich_hoc).split("|")]
            day_str = lich_parts[0] if lich_parts else "Thứ 2"
            time_str = lich_parts[1] if (idx == 0 and len(lich_parts) > 1) else time_slots[idx % len(time_slots)]
            schedule.append({
                "day": day_str,
                "time": time_str,
                "room": f"Phòng {lop.phong}",
                "subject_id": mon.ma_mon if mon else "",
                "teacher_id": gv.ma_gv if gv else "",
                "semester_label": "Học kỳ 1",
            })

        year_match = re.search(r"\d{4}", str(lop.khoa_hoc))
        year_val = year_match.group(0) if year_match else lop.khoa_hoc

        return SimpleNamespace(
            class_id=lop.ma_lop,
            class_name=lop.ten_lop,
            year=year_val,
            nganh=lop.nganh,
            lich_hoc=lop.lich_hoc,
            phong=lop.phong,
            schedule=schedule,
        )

    def get_course_by_id(self, subject_id):
        mon = next((m for m in MON_HOCS if m.ma_mon == subject_id), None)
        if not mon:
            return None
        return SimpleNamespace(
            subject_id=mon.ma_mon,
            subject_name=mon.ten_mon,
            credits=mon.so_tin_chi,
        )


class TeacherManagerAdapter:
    def get_teacher_by_id(self, teacher_id):
        gv = next((g for g in GIANG_VIENS if g.ma_gv == teacher_id), None)
        if not gv:
            return None
        return SimpleNamespace(
            teacher_id=gv.ma_gv,
            full_name=gv.ho_ten,
            email=gv.email,
            phone="0901 234 567",
            department=f"Khoa {gv.khoa}",
            degree_title=f"{gv.hoc_vi} - Giảng viên",
            specialization=gv.chuyen_mon,
            position_info=f"Giảng viên cơ hữu • Khoa {gv.khoa}",
        )

    def get_assignments_by_teacher(self, teacher_id):
        gv = next((g for g in GIANG_VIENS if g.ma_gv == teacher_id), None)
        if not gv:
            return []
        result = []
        for pc in PHAN_CONGS:
            if pc.giang_vien_id == gv.id and pc.lop_hoc and pc.mon_hoc:
                result.append(SimpleNamespace(
                    teacher_id=gv.ma_gv,
                    class_id=pc.lop_hoc.ma_lop,
                    subject_id=pc.mon_hoc.ma_mon,
                ))
        return result


class GradeManager:
    def __init__(self, student_mgr):
        self.student_manager = student_mgr

    def get_grades_by_student(self, student_id, semester=None):
        result = [g for g in GRADES if g.student_id == student_id]
        if semester and semester != "ALL":
            result = [g for g in result if g.semester == semester]
        return result

    def get_grade_sheet(self, class_id, subject_id, semester):
        class_students = self.student_manager.filter_by_class(class_id)
        sheet = []
        for st in class_students:
            g = next(
                (
                    item for item in GRADES
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


student_manager = StudentManager()  # Dùng trực tiếp StudentManager của Task 2
class_manager = ClassManagerAdapter()
teacher_manager = TeacherManagerAdapter()
grade_manager = GradeManager(student_manager)
gpa_service = GPAService(grade_manager, class_manager)


# =========================================================
# 1. CÁC CLASS PORTAL CỐT LÕI CỦA NGƯỜI 5
# =========================================================
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


# =========================================================
# 2. KIỂM TRA ĐĂNG NHẬP & PHÂN QUYỀN TỪ TASK 1
# =========================================================
def login_required(role):
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            if "username" not in session or session.get("role") != role:
                return redirect(url_for("login"))
            return f(*args, **kwargs)
        return wrapped
    return decorator


@portal_bp.route("/portal-logout")
def logout():
    return redirect(url_for("logout"))


# =========================================================
# 3. ROUTES GIAO DIỆN WEB (STUDENT PORTAL & TEACHER PORTAL)
# =========================================================
@portal_bp.route("/student/profile")
@login_required("student")
def student_profile():
    st = student_manager.get_student_by_id(session["ref_id"])
    portal = StudentPortal(st, student_manager, class_manager, grade_manager, gpa_service)
    info = portal.view_personal_information()
    gpa_info = portal.view_gpa()
    enrolled_classes = portal.view_enrolled_classes()
    semester_cards = portal.get_semester_summary_cards()

    # Nếu chưa bấm chọn kỳ nào (?sem=...), tự động ưu tiên chọn kỳ gần nhất có dữ liệu điểm
    default_sem = next(
        (c["code"] for c in reversed(semester_cards) if c["count"] > 0),
        semester_cards[-1]["code"]
    )
    selected_sem = request.args.get("sem", default_sem)
    active_sem_obj = next((c for c in semester_cards if c["code"] == selected_sem), semester_cards[-1])

    # Chỉ lấy đúng môn của học kỳ đang chọn, KHÔNG lấy bù môn từ kỳ khác
    grade_list = portal.view_grades(active_sem_obj["code"])

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
    ref_id = session.get("ref_id") or session.get("username")
    st = student_manager.get_student_by_id(ref_id)
    if not st:
        return "Không tìm thấy hồ sơ sinh viên.", 404

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
    ref_id = session.get("ref_id") or session.get("username")
    st = student_manager.get_student_by_id(ref_id)
    if not st:
        return "Không tìm thấy hồ sơ sinh viên.", 404

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
    ref_id = session.get("ref_id") or session.get("username")
    st = student_manager.get_student_by_id(ref_id)
    if not st:
        return "Không tìm thấy hồ sơ sinh viên.", 404

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


@portal_bp.route("/teacher/dashboard")
@login_required("teacher")
def teacher_dashboard():
    ref_id = session.get("ref_id") or session.get("username")
    gv = teacher_manager.get_teacher_by_id(ref_id)
    if not gv:
        return "Không tìm thấy hồ sơ giảng viên tương ứng với tài khoản.", 404

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
    ref_id = session.get("ref_id") or session.get("username")
    gv = teacher_manager.get_teacher_by_id(ref_id)
    if not gv:
        return "Không tìm thấy hồ sơ giảng viên.", 404

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
    ref_id = session.get("ref_id") or session.get("username")
    gv = teacher_manager.get_teacher_by_id(ref_id)
    if not gv:
        return "Không tìm thấy hồ sơ giảng viên.", 404

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
    ref_id = session.get("ref_id") or session.get("username")
    gv = teacher_manager.get_teacher_by_id(ref_id)
    if not gv:
        return "Không tìm thấy hồ sơ giảng viên.", 404

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