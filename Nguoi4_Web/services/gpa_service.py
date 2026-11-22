from services.grade_service import to_gpa4, to_letter


class GPAService:
    def __init__(self, grades, courses):
        self.grades = grades
        self.courses = {c.subject_id: c for c in courses}

    def _credits(self, subject_id):
        c = self.courses.get(subject_id)
        return c.credits if c else 0

    def calculate_gpa(self, student_id):
        """GPA tích lũy = tổng(điểm hệ 4 x tín chỉ) / tổng tín chỉ (UC21)."""
        pts = cr = 0
        for g in self.grades:
            if g.student_id != student_id:
                continue
            c = self._credits(g.subject_id)
            pts += to_gpa4(g.calculate_total()) * c
            cr += c
        return round(pts / cr, 2) if cr else 0.0

    def total_credits(self, student_id):
        return sum(self._credits(g.subject_id) for g in self.grades
                   if g.student_id == student_id)

    def semester_summary(self, student_id, semesters):
        """Điểm theo từng học kỳ và từng môn (UC22)."""
        out = []
        for sem in semesters:
            rows, pts, cr = [], 0, 0
            for g in self.grades:
                if g.student_id != student_id or g.semester != sem:
                    continue
                c = self.courses.get(g.subject_id)
                total = g.calculate_total()
                credits = c.credits if c else 0
                pts += to_gpa4(total) * credits
                cr += credits
                rows.append({"subject_id": g.subject_id,
                             "subject_name": c.subject_name if c else g.subject_id,
                             "credits": credits, "total": round(total, 2),
                             "g4": to_gpa4(total), "letter": to_letter(total)})
            out.append({"semester": sem, "rows": rows,
                        "gpa": round(pts / cr, 2) if cr else None})
        return out
