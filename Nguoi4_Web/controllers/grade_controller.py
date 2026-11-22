SEMESTERS = ["HK1 2026-2027", "HK2 2025-2026"]


class GradeManager:
    """Quản lý điểm (UC16 nhập điểm, UC17 sửa điểm, UC39 bảng điểm)."""

    def __init__(self, grades, students, teacher_assignments=None):
        self.grades = grades              # list dùng chung từ data (không tạo list riêng)
        self.students = students
        self.teacher_assignments = teacher_assignments or []

    # ---- kiểm tra
    @staticmethod
    def _validate(grade):
        for v in (grade.attendance, grade.midterm, grade.final):
            if not isinstance(v, (int, float)) or not (0 <= v <= 10):
                raise ValueError("Điểm phải là số từ 0 đến 10")

    def _find(self, student_id, subject_id, semester=None):
        for g in self.grades:
            if (g.student_id == student_id and g.subject_id == subject_id
                    and (semester is None or g.semester == semester)):
                return g
        return None

    def _is_assigned(self, teacher_id, class_id, subject_id):
        return any(a.teacher_id == teacher_id and a.class_id == class_id
                   and a.subject_id == subject_id for a in self.teacher_assignments)

    # ---- thao tác từng bản ghi
    def add_grade(self, grade, teacher_id=None, class_id=None):
        self._validate(grade)
        if teacher_id is not None and not self._is_assigned(
                teacher_id, class_id, grade.subject_id):
            raise PermissionError("Giảng viên không được phân công môn/lớp này")
        if self._find(grade.student_id, grade.subject_id, grade.semester):
            raise ValueError("Đã có điểm của sinh viên này (môn, học kỳ này)")
        self.grades.append(grade)

    def update_grade(self, student_id, subject_id, data):
        g = self._find(student_id, subject_id, data.get("semester"))
        if g is None:
            raise ValueError("Không tìm thấy bản ghi điểm")
        old = (g.attendance, g.midterm, g.final)
        for k, v in data.items():
            setattr(g, k, v)
        try:
            self._validate(g)
        except ValueError:
            g.attendance, g.midterm, g.final = old
            raise

    def delete_grade(self, student_id, subject_id, semester):
        g = self._find(student_id, subject_id, semester)
        if g:
            self.grades.remove(g)

    # ---- bảng điểm
    def class_students(self, class_id):
        return [s for s in self.students if s.class_id == class_id]

    def get_grade_sheet(self, class_id, subject_id, semester):
        ids = {s.student_id for s in self.class_students(class_id)}
        return [g for g in self.grades
                if g.student_id in ids and g.subject_id == subject_id
                and g.semester == semester]

    def save_sheet(self, class_id, subject_id, semester, raw):
        """Lưu cả bảng điểm một lần từ form.

        raw: {student_id: (chuyên cần, giữa kỳ, cuối kỳ)} dạng chuỗi.
        Trả về (errors, số_dòng_thay_đổi). Có lỗi ở bất kỳ dòng nào thì không lưu gì cả.
        """
        from models.grade import Grade
        errors, parsed, to_delete = {}, {}, []
        for s in self.class_students(class_id):
            sid = s.student_id
            vals = [str(v).strip().replace(",", ".") for v in raw.get(sid, ("", "", ""))]
            existing = self._find(sid, subject_id, semester)
            if all(v == "" for v in vals):
                if existing:
                    to_delete.append(sid)
                continue
            if any(v == "" for v in vals):
                errors[sid] = "Nhập đủ 3 cột điểm (chuyên cần, giữa kỳ, cuối kỳ)."
                continue
            try:
                nums = tuple(float(v) for v in vals)
            except ValueError:
                errors[sid] = "Điểm phải là số."
                continue
            if any(not 0 <= n <= 10 for n in nums):
                errors[sid] = "Điểm phải nằm trong khoảng 0 đến 10."
                continue
            parsed[sid] = nums
        if errors:
            return errors, 0

        changed = 0
        for sid in to_delete:
            self.delete_grade(sid, subject_id, semester)
            changed += 1
        for sid, nums in parsed.items():
            existing = self._find(sid, subject_id, semester)
            if existing is None:                                   # UC16
                self.add_grade(Grade(sid, subject_id, semester, *nums))
                changed += 1
            elif nums != (existing.attendance, existing.midterm, existing.final):
                self.update_grade(sid, subject_id, {              # UC17
                    "semester": semester, "attendance": nums[0],
                    "midterm": nums[1], "final": nums[2]})
                changed += 1
        return {}, changed
