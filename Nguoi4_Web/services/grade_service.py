# Bảng quy đổi minh họa, cần thống nhất với giảng viên trước khi chốt
def to_letter(score):
    if score >= 8.5:
        return "A"
    if score >= 7.0:
        return "B"
    if score >= 5.5:
        return "C"
    if score >= 4.0:
        return "D"
    return "F"


def to_gpa4(score):
    return {"A": 4.0, "B": 3.0, "C": 2.0, "D": 1.0, "F": 0.0}[to_letter(score)]
