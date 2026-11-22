import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from demo_app import app
from controllers.grade_routes import gm, gpa
from controllers.grade_controller import SEMESTERS

HK1 = SEMESTERS[0]
Q = {"class_id": "CNTT2401", "semester": HK1, "subject_id": "CTDL2401"}


def login(role):
    c = app.test_client()
    assert c.get(f"/demo-login/{role}").status_code == 302
    return c


def form(**over):
    d = dict(Q)
    for s in gm.class_students("CNTT2401"):
        g = gm._find(s.student_id, "CTDL2401", HK1)
        a, m, f = (g.attendance, g.midterm, g.final) if g else ("", "", "")
        d[f"att_{s.student_id}"], d[f"mid_{s.student_id}"], d[f"fin_{s.student_id}"] = a, m, f
    d.update(over)
    return d


def test_pages_render():
    t = login("teacher")
    r = t.get("/grades/", query_string=Q)
    assert r.status_code == 200 and "Nguyễn Minh Anh" in r.get_data(as_text=True)
    r = t.get("/grades/results", query_string={"student_id": "SV2024001"})
    assert r.status_code == 200 and "GPA tích lũy" in r.get_data(as_text=True)


def test_teacher_add_and_update():
    t = login("teacher")
    n0 = len(gm.get_grade_sheet("CNTT2401", "CTDL2401", HK1))
    r = t.post("/grades/", data=form(att_SV2024007="9", mid_SV2024007="8", fin_SV2024007="7"))
    assert r.status_code == 302                                      # UC16
    assert len(gm.get_grade_sheet("CNTT2401", "CTDL2401", HK1)) == n0 + 1
    r = t.post("/grades/", data=form(fin_SV2024007="10"))
    assert r.status_code == 302                                      # UC17
    assert gm._find("SV2024007", "CTDL2401", HK1).final == 10


def test_invalid_input_saves_nothing():
    t = login("teacher")
    before = gm._find("SV2024001", "CTDL2401", HK1).final
    r = t.post("/grades/", data=form(fin_SV2024001="11", att_SV2024008="5"))
    html = r.get_data(as_text=True)
    assert r.status_code == 200 and "0 đến 10" in html and "Nhập đủ 3 cột" in html
    assert gm._find("SV2024001", "CTDL2401", HK1).final == before
    assert gm._find("SV2024008", "CTDL2401", HK1) is None
    r = t.post("/grades/", data=form(fin_SV2024001="abc"))
    assert "Điểm phải là số" in r.get_data(as_text=True)


def test_clear_row_deletes():
    t = login("teacher")
    t.post("/grades/", data=form(att_SV2024007="", mid_SV2024007="", fin_SV2024007=""))
    assert gm._find("SV2024007", "CTDL2401", HK1) is None


def test_roles():
    a = login("admin")
    assert a.get("/grades/", query_string=Q).status_code == 200
    assert a.post("/grades/", data=form()).status_code == 403        # admin chỉ xem
    s = login("student")
    assert s.get("/grades/").status_code == 302                      # sinh viên không vào trang nhập
    r = s.get("/grades/results", query_string={"student_id": "SV2024002"})
    html = r.get_data(as_text=True)
    assert "Nguyễn Minh Anh" in html and "Trần Đức Huy" not in html  # chỉ xem điểm của mình
    assert app.test_client().get("/grades/").status_code == 302      # chưa đăng nhập


def test_gpa():
    g = gpa.calculate_gpa("SV2024001")
    assert 0 < g <= 4
    assert gpa.total_credits("SV2024001") == 9


if __name__ == "__main__":
    for n, f in list(globals().items()):
        if n.startswith("test_"):
            f(); print("OK", n)
