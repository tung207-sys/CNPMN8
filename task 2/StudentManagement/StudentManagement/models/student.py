class Student:
    def __init__(self, student_id, full_name, dob, gender, address, email, class_id):
        self.student_id = student_id
        self.full_name = full_name
        self.dob = dob
        self.gender = gender
        self.address = address
        self.email = email
        self.class_id = class_id

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
