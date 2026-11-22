from models.student import Student
from data.shared_data import students, LOP_HOCS

class StudentManager:
    def __init__(self):
        self.students = students
       
    def _load_sample_data(self):
        sample_list = [
            Student("SV001", "Phạm Dương Hoàng Phúc ", "31/05/2007", "Nam", "Quận 3, TP.HCM", "hoangphuc310507@gmail.com", "CNTT01"),
            Student("SV002", "Nguyễn Thanh Vy ", "20/05/2007", "Nữ", "Tân Phú, TP.HCM", "thanhvy20052007@gmail.com", "CNTT02"),
            Student("SV003", "Nguyễn Minh Huy  ", "25/04/2007", "Nam", "Quận 3, TP.HCM", "ngminhhuy25042007@gmail.com", "CNTT03"),
            Student("SV004", "Võ Đại Phúc", "05/01/2007", "Nam", "Bình Thạnh, TP.HCM", "phucVD@gmail.com", "CNTT04"),
            Student("SV005", "Trần Thanh Tùng", "19/09/2007", "Nam", "Bình Thạnh, TP.HCM", "TungTT@gmail.com", "CNTT05"),
            Student("SV006", "Bùi Trương Vĩnh Phú", "15/07/2007", "Nam", "Bà Rịa, TP.HCM", "PhuBRVT@gmail.com", "CNTT06"),
            Student("SV007", "Đặng Gia Huy", "12/08/2007", "Nam", "Quận 7, TP.HCM", "huy.dg@gmail.com", "KTPM07"),
            Student("SV008", "Bùi Ngọc Lan", "25/12/2007", "Nữ", "Quận 10, TP.HCM", "lan.bn@gmail.com", "KTPM08"),
            Student("SV009", "Đỗ Minh Khang", "14/02/2007", "Nam", "Phú Nhuận, TP.HCM", "khang.dm@gmail.com", "KTPM09"),
            Student("SV010", "Ngô Thanh Mai", "08/06/2007", "Nữ", "Quận 5, TP.HCM", "mai.nt@gmail.com", "HTTT01"),
            Student("SV011", "Dương Văn Nam", "17/10/2007", "Nam", "Quận 12, TP.HCM", "nam.dv@gmail.com", "HTTT01"),
            Student("SV012", "Lý Thu Thảo", "29/05/2007", "Nữ", "Tân Phú, TP.HCM", "thao.lt@gmail.com", "HTTT01"),
        ]
        self.students.extend(sample_list)

    def _validate_fields(self, student_id, full_name, dob, gender, address, email, class_id):
        fields = [student_id, full_name, dob, gender, address, email, class_id]
        if any(not str(f).strip() for f in fields):
            raise ValueError("Vui lòng nhập đầy đủ tất cả thông tin bắt buộc!")
        if "@" not in email or "." not in email:
            raise ValueError("Email không đúng định dạng!")

    def add_student(self, student: Student):
        self._validate_fields(
            student.student_id,
            student.full_name,
            student.dob,
            student.gender,
            student.address,
            student.email,
            student.class_id,
        )
        if any(s.student_id.lower() == student.student_id.strip().lower() for s in self.students):
            raise ValueError(f"Mã sinh viên '{student.student_id}' đã tồn tại!")

        student.student_id = student.student_id.strip()
        student.full_name = student.full_name.strip()
        self.students.append(student)
        return True

    def get_all_students(self):
        return list(self.students)

    def get_student_by_id(self, student_id):
        for s in self.students:
            if s.student_id.lower() == str(student_id).strip().lower():
                return s
        return None

    def get_all_classes(self):
        class_codes = {l.ma_lop for l in LOP_HOCS}  # Tự động lấy lớp từ Task 3
        for s in self.students:
            class_codes.add(s.class_id)
        return sorted(class_codes)

    def update_student(self, student_id, data):
        target = self.get_student_by_id(student_id)
        if not target:
            raise ValueError(f"Không tìm thấy sinh viên có mã '{student_id}'!")

        if isinstance(data, Student):
            new_data = data.to_dict()
        elif isinstance(data, dict):
            new_data = data
        else:
            raise ValueError("Dữ liệu cập nhật không hợp lệ!")

        full_name = new_data.get("full_name", target.full_name)
        dob = new_data.get("dob", target.dob)
        gender = new_data.get("gender", target.gender)
        address = new_data.get("address", target.address)
        email = new_data.get("email", target.email)
        class_id = new_data.get("class_id", target.class_id)

        self._validate_fields(target.student_id, full_name, dob, gender, address, email, class_id)

        target.full_name = full_name.strip()
        target.dob = dob.strip()
        target.gender = gender.strip()
        target.address = address.strip()
        target.email = email.strip()
        target.class_id = class_id.strip()
        return True

    def delete_student(self, student_id):
        target = self.get_student_by_id(student_id)
        if not target:
            raise ValueError(f"Không tìm thấy sinh viên có mã '{student_id}'!")
        self.students.remove(target)
        return True

    def search_by_id(self, keyword):
        kw = str(keyword).strip().lower()
        if not kw:
            return self.get_all_students()
        return [s for s in self.students if kw in s.student_id.lower()]

    def search_by_name(self, keyword):
        kw = str(keyword).strip().lower()
        if not kw:
            return self.get_all_students()
        return [s for s in self.students if kw in s.full_name.lower()]

    def filter_by_class(self, class_id):
        cid = str(class_id).strip()
        if not cid or cid == "Tất cả":
            return self.get_all_students()
        return [s for s in self.students if s.class_id.lower() == cid.lower()]
