class Class:
    def __init__(self, class_id, class_name, year, schedule=None):
        self.class_id = class_id
        self.class_name = class_name
        self.year = year
        self.schedule = schedule or []
class Course:
    def __init__(self, subject_id, subject_name, credits):
        self.subject_id = subject_id
        self.subject_name = subject_name
        self.credits = credits
class Grade:
    def __init__(self, student_id, subject_id, semester, attendance, midterm, final):
        self.student_id = student_id
        self.subject_id = subject_id
        self.semester = semester
        self.attendance = attendance
        self.midterm = midterm
        self.final = final

    def calculate_total(self):
        return round(self.attendance * 0.1 + self.midterm * 0.3 + self.final * 0.6, 2)

    def get_letter_and_gpa4(self):
        total = self.calculate_total()
        if total >= 8.5:
            return "A", 4.0
        elif total >= 8.0:
            return "B+", 3.5
        elif total >= 7.0:
            return "B", 3.0
        elif total >= 6.5:
            return "C+", 2.5
        elif total >= 5.5:
            return "C", 2.0
        elif total >= 5.0:
            return "D+", 1.5
        elif total >= 4.0:
            return "D", 1.0
        return "F", 0.0
class Student:
    def __init__(
        self,
        student_id,
        full_name,
        dob,
        gender,
        address,
        email,
        class_id,
        ethnicity="Kinh",
        nationality="Việt Nam",
        phone="0912 345 678",
        birthplace="TP. Hồ Chí Minh",
        current_address=None,
        faculty="Khoa CNTT",
        major="Công nghệ thông tin",
        education_level="Đại học",
        training_type="Chính quy",
        cohort="K23",
        academic_year="2025–2026",
        advisor="TS. Trần Thị Mỹ Tiên",
        status="Đang học",
        target_credits=130,
    ):
        self.student_id = student_id
        self.full_name = full_name
        self.dob = dob
        self.gender = gender
        self.address = address
        self.email = email
        self.class_id = class_id
        self.ethnicity = ethnicity
        self.nationality = nationality
        self.phone = phone
        self.birthplace = birthplace
        self.current_address = current_address or address
        self.faculty = faculty
        self.major = major
        self.education_level = education_level
        self.training_type = training_type
        self.cohort = cohort
        self.academic_year = academic_year
        self.advisor = advisor
        self.status = status
        self.target_credits = target_credits
class TeacherAssignment:
    def __init__(self, teacher_id, class_id, subject_id):
        self.teacher_id = teacher_id
        self.class_id = class_id
        self.subject_id = subject_id
class Teacher:
    def __init__(
        self,
        teacher_id,
        full_name,
        email,
        phone,
        department="Khoa Công nghệ thông tin",
        degree_title="Tiến sĩ - Giảng viên",
        specialization="Cơ sở dữ liệu, Thiết kế web",
        position_info="Giảng viên cơ hữu • Bộ môn Khoa học máy tính",
    ):
        self.teacher_id = teacher_id
        self.full_name = full_name
        self.email = email
        self.phone = phone
        self.department = department
        self.degree_title = degree_title
        self.specialization = specialization
        self.position_info = position_info
class User:
    def __init__(self, user_id, username, password, role, ref_id, is_active=True):
        self.user_id = user_id
        self.username = username
        self.password = password
        self.role = role          # 'admin', 'teacher', 'student'
        self.ref_id = ref_id      # student_id hoặc teacher_id
        self.is_active = is_active