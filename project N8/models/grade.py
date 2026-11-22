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