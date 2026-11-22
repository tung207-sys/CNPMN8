class Grade:
    def __init__(self, student_id, subject_id, semester,
                 attendance, midterm, final):
        self.student_id = student_id
        self.subject_id = subject_id
        self.semester = semester
        self.attendance = attendance
        self.midterm = midterm
        self.final = final

    def calculate_total(self):
        # Công thức minh họa (10% / 30% / 60%), cần chốt trọng số với giảng viên
        return (self.attendance * 0.1
                + self.midterm * 0.3
                + self.final * 0.6)
