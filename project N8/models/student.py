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
        faculty="Khoa Công nghệ thông tin",
        major="Công nghệ thông tin",
        education_level="Đại học",
        training_type="Chính quy",
        cohort="K24",
        academic_year="2026–2027",
        advisor="ThS. Lê Thu Hương",
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

    def to_tuple(self):
        return (
            self.student_id,
            self.full_name,
            self.dob,
            self.gender,
            self.address,
            self.email,
            self.class_id,
        )

    def to_dict(self):
        return {
            "student_id": self.student_id,
            "full_name": self.full_name,
            "dob": self.dob,
            "gender": self.gender,
            "address": self.address,
            "email": self.email,
            "class_id": self.class_id,
        }