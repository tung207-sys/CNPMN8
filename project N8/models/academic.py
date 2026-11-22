class GiangVien:
    def __init__(self, id, ma_gv, ho_ten, email, khoa, hoc_vi, chuyen_mon):
        self.id = id
        self.ma_gv = ma_gv
        self.ho_ten = ho_ten
        self.email = email
        self.khoa = khoa
        self.hoc_vi = hoc_vi
        self.chuyen_mon = chuyen_mon

    @property
    def initials(self):
        parts = self.ho_ten.strip().split()
        if len(parts) >= 2:
            return (parts[-2][0] + parts[-1][0]).upper()
        return self.ho_ten[:2].upper()

    @property
    def phan_congs(self):
        from data.shared_data import PHAN_CONGS
        return [pc for pc in PHAN_CONGS if pc.giang_vien_id == self.id]


class MonHoc:
    def __init__(self, id, ma_mon, ten_mon, so_tin_chi, khoa, so_tiet, mo_ta=''):
        self.id = id
        self.ma_mon = ma_mon
        self.ten_mon = ten_mon
        self.so_tin_chi = so_tin_chi
        self.khoa = khoa
        self.so_tiet = so_tiet
        self.mo_ta = mo_ta
        self.row_class = ''

    @property
    def phan_congs(self):
        from data.shared_data import PHAN_CONGS
        return [pc for pc in PHAN_CONGS if pc.mon_hoc_id == self.id]
    @property
    def subject_id(self):
        return self.ma_mon

    @property
    def subject_name(self):
        return self.ten_mon

    @property
    def credits(self):
        return self.so_tin_chi


class LopHoc:
    def __init__(self, id, ma_lop, ten_lop, nganh, khoa_hoc, si_so, lich_hoc, phong):
        self.id = id
        self.ma_lop = ma_lop
        self.ten_lop = ten_lop
        self.nganh = nganh
        self.khoa_hoc = khoa_hoc
        self.si_so = si_so
        self.lich_hoc = lich_hoc
        self.phong = phong
        self.row_class = ''

    @property
    def phan_congs(self):
        from data.shared_data import PHAN_CONGS
        return [pc for pc in PHAN_CONGS if pc.lop_id == self.id]


class PhanCongGiangDay:
    def __init__(self, id, lop_id, mon_hoc_id, giang_vien_id):
        self.id = id
        self.lop_id = lop_id
        self.mon_hoc_id = mon_hoc_id
        self.giang_vien_id = giang_vien_id

    @property
    def lop_hoc(self):
        from data.shared_data import LOP_HOCS
        return next((l for l in LOP_HOCS if l.id == self.lop_id), None)

    @property
    def mon_hoc(self):
        from data.shared_data import MON_HOCS
        return next((m for m in MON_HOCS if m.id == self.mon_hoc_id), None)

    @property
    def giang_vien(self):
        from data.shared_data import GIANG_VIENS
        return next((g for g in GIANG_VIENS if g.id == self.giang_vien_id), None)
    @property
    def teacher_id(self):
        return self.giang_vien.ma_gv if self.giang_vien else ""

    @property
    def class_id(self):
        return self.lop_hoc.ma_lop if self.lop_hoc else ""

    @property
    def subject_id(self):
        return self.mon_hoc.ma_mon if self.mon_hoc else ""