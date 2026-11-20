import unicodedata
from flask import Flask, render_template, request, redirect, url_for, flash, abort

app = Flask(__name__)
app.secret_key = 'manager_student_system_task3_2026'

def normalize_vi(text):
    if not text:
        return '', ''
    lower_text = str(text).lower().strip()
    nfkd = unicodedata.normalize('NFKD', lower_text.replace('đ', 'd'))
    no_accent = ''.join(c for c in nfkd if not unicodedata.combining(c))
    return lower_text, no_accent

def match_keyword(keyword, *fields):
    kw_lower, kw_no_accent = normalize_vi(keyword)
    if not kw_lower:
        return True
    for field in fields:
        f_lower, f_no_accent = normalize_vi(field)
        if kw_lower in f_lower or kw_no_accent in f_no_accent:
            return True
    return False

def match_department(khoa_keyword, khoa_field):
    kw_lower, kw_no_accent = normalize_vi(khoa_keyword)
    if not kw_lower:
        return True
    if kw_lower.startswith('khoa '):
        kw_lower = kw_lower[5:].strip()
    if kw_no_accent.startswith('khoa '):
        kw_no_accent = kw_no_accent[5:].strip()
    f_lower, f_no_accent = normalize_vi(khoa_field)
    return (kw_lower in f_lower) or (kw_no_accent in f_no_accent)

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
        return [pc for pc in PHAN_CONGS if pc.mon_hoc_id == self.id]

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
        return [pc for pc in PHAN_CONGS if pc.lop_id == self.id]

class PhanCongGiangDay:
    def __init__(self, id, lop_id, mon_hoc_id, giang_vien_id):
        self.id = id
        self.lop_id = lop_id
        self.mon_hoc_id = mon_hoc_id
        self.giang_vien_id = giang_vien_id

    @property
    def lop_hoc(self):
        return next((l for l in LOP_HOCS if l.id == self.lop_id), None)

    @property
    def mon_hoc(self):
        return next((m for m in MON_HOCS if m.id == self.mon_hoc_id), None)

    @property
    def giang_vien(self):
        return next((g for g in GIANG_VIENS if g.id == self.giang_vien_id), None)

GIANG_VIENS = [
    GiangVien(1, 'GV202401', 'Lê Thu Hương', 'huong.lt@example.edu.vn',
              'Công nghệ thông tin', 'Thạc sĩ', 'Cơ sở dữ liệu & Hệ thống thông tin'),
    GiangVien(2, 'GV202402', 'Nguyễn Văn An', 'an.nv@example.edu.vn',
              'Công nghệ thông tin', 'Tiến sĩ', 'Công nghệ phần mềm'),
    GiangVien(3, 'GV202403', 'Trần Minh Tâm', 'tam.tm@example.edu.vn',
              'Quản trị kinh doanh', 'Tiến sĩ', 'Quản trị chiến lược'),
    GiangVien(4, 'GV202404', 'Phạm Lan Anh', 'anh.pl@example.edu.vn',
              'Ngôn ngữ Anh', 'Thạc sĩ', 'Tiếng Anh thương mại'),
]

MON_HOCS = [
    MonHoc(1, 'CSDL2601', 'Cơ sở dữ liệu', 3, 'Công nghệ thông tin',
           '30 LT | 30 TH', 'Thiết kế ERD, chuẩn hóa dữ liệu, đại số quan hệ và truy vấn SQL.'),
    MonHoc(2, 'CNPM2601', 'Công nghệ phần mềm', 3, 'Công nghệ thông tin',
           '30 LT | 30 TH', 'Quy trình phát triển phần mềm, đặc tả yêu cầu và thiết kế sơ đồ UML.'),
    MonHoc(3, 'LTW2601', 'Lập trình Web', 4, 'Công nghệ thông tin',
           '30 LT | 60 TH', 'Xây dựng ứng dụng Web bằng Flask và giao diện Bootstrap.'),
    MonHoc(4, 'QTKD2602', 'Quản trị chiến lược', 3, 'Quản trị kinh doanh',
           '45 LT | 0 TH', 'Hoạch định, triển khai và đánh giá chiến lược kinh doanh doanh nghiệp.'),
]

LOP_HOCS = [
    LopHoc(1, 'CNTT2401', 'Công nghệ thông tin 1', 'Công nghệ thông tin',
           'Khóa 2024 | Hệ chính quy', 48, 'Thứ 2 | 10:15 – 11:00', 'B301'),
    LopHoc(2, 'CNTT2402', 'Công nghệ thông tin 2', 'Công nghệ thông tin',
           'Khóa 2024 | Hệ chính quy', 46, 'Thứ 3 | 10:15 – 11:00', 'B301'),
    LopHoc(3, 'QTKD2401', 'Quản trị kinh doanh', 'Quản trị kinh doanh',
           'Khóa 2024 | Hệ chính quy', 47, 'Thứ 4 | 10:15 – 11:00', 'B301'),
]

PHAN_CONGS = [
    PhanCongGiangDay(1, lop_id=1, mon_hoc_id=1, giang_vien_id=1),
    PhanCongGiangDay(2, lop_id=1, mon_hoc_id=2, giang_vien_id=2),
]

def get_or_404(items, item_id):
    item = next((x for x in items if x.id == item_id), None)
    if item is None:
        abort(404)
    return item

def get_next_id(items):
    return max((x.id for x in items), default=0) + 1

@app.route('/')
def index():
    return redirect(url_for('quan_ly_lop'))

# 1. quản lý lớp học
@app.route('/lop-hoc', methods=['GET', 'POST'])
def quan_ly_lop():
    if request.method == 'POST':
        ma_lop = request.form['ma_lop'].strip()
        if any(l.ma_lop == ma_lop for l in LOP_HOCS):
            flash('Mã lớp đã tồn tại!', 'danger')
        else:
            LOP_HOCS.append(LopHoc(
                id=get_next_id(LOP_HOCS),
                ma_lop=ma_lop,
                ten_lop=request.form['ten_lop'].strip(),
                nganh=request.form['nganh'].strip(),
                khoa_hoc=request.form['khoa_hoc'].strip(),
                si_so=int(request.form['si_so']),
                lich_hoc=request.form['lich_hoc'].strip(),
                phong=request.form['phong'].strip()
            ))
            flash('Thêm lớp học thành công!', 'success')
        return redirect(url_for('quan_ly_lop'))

    q = request.args.get('q', '').strip()
    selected_code = request.args.get('selected', '')

    ds_lop = [l for l in LOP_HOCS if match_keyword(q, l.ma_lop, l.ten_lop)]

    selected_lop = next((l for l in LOP_HOCS if l.ma_lop == selected_code), None) if selected_code else None
    if not selected_lop and ds_lop:
        selected_lop = ds_lop[0]

    for lop in ds_lop:
        lop.row_class = 'bg-light' if (selected_lop and selected_lop.id == lop.id) else ''

    return render_template('class.html', ds_lop=ds_lop, selected_lop=selected_lop,
                           ds_mon=MON_HOCS, ds_gv=GIANG_VIENS, q=q)

@app.route('/lop-hoc/sua/<int:id>', methods=['POST'])
def sua_lop(id):
    lop = get_or_404(LOP_HOCS, id)
    ma_lop = request.form['ma_lop'].strip()

    if any(l.ma_lop == ma_lop and l.id != id for l in LOP_HOCS):
        flash('Mã lớp mới bị trùng với lớp khác!', 'danger')
        return redirect(url_for('quan_ly_lop', selected=lop.ma_lop))

    lop.ma_lop = ma_lop
    lop.ten_lop = request.form['ten_lop'].strip()
    lop.nganh = request.form['nganh'].strip()
    lop.khoa_hoc = request.form['khoa_hoc'].strip()
    lop.si_so = int(request.form['si_so'])
    lop.lich_hoc = request.form['lich_hoc'].strip()
    lop.phong = request.form['phong'].strip()

    flash('Đã cập nhật thông tin lớp học!', 'success')
    return redirect(url_for('quan_ly_lop', selected=lop.ma_lop))

@app.route('/lop-hoc/xoa/<int:id>')
def xoa_lop(id):
    lop = get_or_404(LOP_HOCS, id)
    if lop.phan_congs:
        flash('Không thể xóa lớp học đang có môn học được phân công! Hãy gỡ các môn học trước.', 'warning')
        return redirect(url_for('quan_ly_lop', selected=lop.ma_lop))
    LOP_HOCS.remove(lop)
    flash('Đã xóa lớp học.', 'info')
    return redirect(url_for('quan_ly_lop'))

# 2. thêm môn học và giảng viên vào lớp học
@app.route('/lop-hoc/phan-cong', methods=['POST'])
def them_phan_cong():
    lop_id = int(request.form['lop_id'])
    mon_hoc_id = int(request.form['mon_hoc_id'])
    giang_vien_id = int(request.form['giang_vien_id'])

    lop = get_or_404(LOP_HOCS, lop_id)
    mon = get_or_404(MON_HOCS, mon_hoc_id)
    gv = get_or_404(GIANG_VIENS, giang_vien_id)

    if any(pc.lop_id == lop.id and pc.mon_hoc_id == mon.id for pc in PHAN_CONGS):
        flash(f'Môn "{mon.ten_mon}" đã được phân công cho lớp {lop.ma_lop} rồi!', 'warning')
        return redirect(url_for('quan_ly_lop', selected=lop.ma_lop))

    PHAN_CONGS.append(PhanCongGiangDay(
        id=get_next_id(PHAN_CONGS),
        lop_id=lop.id,
        mon_hoc_id=mon.id,
        giang_vien_id=gv.id
    ))
    flash(f'Đã thêm môn {mon.ten_mon} ({gv.ho_ten}) vào lớp {lop.ma_lop}!', 'success')
    return redirect(url_for('quan_ly_lop', selected=lop.ma_lop))

@app.route('/lop-hoc/sua-phan-cong/<int:id>', methods=['POST'])
def sua_phan_cong(id):
    pc = get_or_404(PHAN_CONGS, id)
    mon_hoc_id = int(request.form['mon_hoc_id'])
    giang_vien_id = int(request.form['giang_vien_id'])

    if any(p.lop_id == pc.lop_id and p.mon_hoc_id == mon_hoc_id and p.id != id for p in PHAN_CONGS):
        flash('Lớp này đã có môn học đó trong danh sách phân công!', 'warning')
        return redirect(url_for('quan_ly_lop', selected=pc.lop_hoc.ma_lop))

    pc.mon_hoc_id = mon_hoc_id
    pc.giang_vien_id = giang_vien_id

    flash('Đã cập nhật môn học & giảng viên của lớp!', 'success')
    return redirect(url_for('quan_ly_lop', selected=pc.lop_hoc.ma_lop))

@app.route('/lop-hoc/xoa-phan-cong/<int:id>')
def xoa_phan_cong(id):
    pc = get_or_404(PHAN_CONGS, id)
    ma_lop = pc.lop_hoc.ma_lop
    PHAN_CONGS.remove(pc)
    flash('Đã gỡ môn học khỏi lớp.', 'info')
    return redirect(url_for('quan_ly_lop', selected=ma_lop))

# 3. quản lý giảng viên
@app.route('/giang-vien', methods=['GET', 'POST'])
def quan_ly_giang_vien():
    if request.method == 'POST':
        ma_gv = request.form['ma_gv'].strip()
        if any(g.ma_gv == ma_gv for g in GIANG_VIENS):
            flash('Mã giảng viên đã tồn tại!', 'danger')
        else:
            GIANG_VIENS.append(GiangVien(
                id=get_next_id(GIANG_VIENS),
                ma_gv=ma_gv,
                ho_ten=request.form['ho_ten'].strip(),
                email=request.form['email'].strip(),
                khoa=request.form['khoa'].strip(),
                hoc_vi=request.form['hoc_vi'].strip(),
                chuyen_mon=request.form['chuyen_mon'].strip()
            ))
            flash('Thêm giảng viên thành công!', 'success')
        return redirect(url_for('quan_ly_giang_vien'))

    q = request.args.get('q', '').strip()
    khoa_q = request.args.get('khoa', '').strip()

    ds_gv = [
        g for g in GIANG_VIENS
        if match_keyword(q, g.ma_gv, g.ho_ten) and match_department(khoa_q, g.khoa)
    ]

    tong_gv = len(GIANG_VIENS)
    ds_khoa = sorted(list(set(g.khoa for g in GIANG_VIENS)))
    so_khoa = len(ds_khoa)

    return render_template('teacher.html', ds_gv=ds_gv, tong_gv=tong_gv,
                           so_khoa=so_khoa, ds_khoa=ds_khoa, q=q, khoa_q=khoa_q)

@app.route('/giang-vien/sua/<int:id>', methods=['POST'])
def sua_giang_vien(id):
    gv = get_or_404(GIANG_VIENS, id)
    ma_gv = request.form['ma_gv'].strip()

    if any(g.ma_gv == ma_gv and g.id != id for g in GIANG_VIENS):
        flash('Mã giảng viên mới bị trùng với giảng viên khác!', 'danger')
        return redirect(url_for('quan_ly_giang_vien'))

    gv.ma_gv = ma_gv
    gv.ho_ten = request.form['ho_ten'].strip()
    gv.email = request.form['email'].strip()
    gv.khoa = request.form['khoa'].strip()
    gv.hoc_vi = request.form['hoc_vi'].strip()
    gv.chuyen_mon = request.form['chuyen_mon'].strip()

    flash('Đã cập nhật thông tin giảng viên!', 'success')
    return redirect(url_for('quan_ly_giang_vien'))

@app.route('/giang-vien/xoa/<int:id>')
def xoa_giang_vien(id):
    gv = get_or_404(GIANG_VIENS, id)
    if gv.phan_congs:
        flash('Không thể xóa giảng viên đang có lịch phân công giảng dạy!', 'warning')
        return redirect(url_for('quan_ly_giang_vien'))
    GIANG_VIENS.remove(gv)
    flash('Đã xóa giảng viên.', 'info')
    return redirect(url_for('quan_ly_giang_vien'))

# 4. quản lý môn học
@app.route('/mon-hoc', methods=['GET', 'POST'])
def quan_ly_mon_hoc():
    if request.method == 'POST':
        ma_mon = request.form['ma_mon'].strip()
        if any(m.ma_mon == ma_mon for m in MON_HOCS):
            flash('Mã môn học đã tồn tại!', 'danger')
        else:
            MON_HOCS.append(MonHoc(
                id=get_next_id(MON_HOCS),
                ma_mon=ma_mon,
                ten_mon=request.form['ten_mon'].strip(),
                so_tin_chi=int(request.form['so_tin_chi']),
                khoa=request.form['khoa'].strip(),
                so_tiet=request.form['so_tiet'].strip(),
                mo_ta=request.form['mo_ta'].strip()
            ))
            flash('Thêm môn học thành công!', 'success')
        return redirect(url_for('quan_ly_mon_hoc'))

    q = request.args.get('q', '').strip()
    selected_code = request.args.get('selected', '')

    ds_mon = [m for m in MON_HOCS if match_keyword(q, m.ma_mon, m.ten_mon)]

    selected_mon = next((m for m in MON_HOCS if m.ma_mon == selected_code), None) if selected_code else None
    if not selected_mon and ds_mon:
        selected_mon = ds_mon[0]

    tong_tin_chi = sum(m.so_tin_chi for m in MON_HOCS)

    for m in ds_mon:
        m.row_class = 'bg-light' if (selected_mon and selected_mon.id == m.id) else ''

    return render_template('courses.html', ds_mon=ds_mon, selected_mon=selected_mon, tong_tin_chi=tong_tin_chi, q=q)

@app.route('/mon-hoc/sua/<int:id>', methods=['POST'])
def sua_mon_hoc(id):
    mon = get_or_404(MON_HOCS, id)
    ma_mon = request.form['ma_mon'].strip()

    if any(m.ma_mon == ma_mon and m.id != id for m in MON_HOCS):
        flash('Mã môn học mới bị trùng với môn học khác!', 'danger')
        return redirect(url_for('quan_ly_mon_hoc', selected=mon.ma_mon))

    mon.ma_mon = ma_mon
    mon.ten_mon = request.form['ten_mon'].strip()
    mon.so_tin_chi = int(request.form['so_tin_chi'])
    mon.khoa = request.form['khoa'].strip()
    mon.so_tiet = request.form['so_tiet'].strip()
    mon.mo_ta = request.form['mo_ta'].strip()

    flash('Đã cập nhật thông tin môn học!', 'success')
    return redirect(url_for('quan_ly_mon_hoc', selected=mon.ma_mon))

@app.route('/mon-hoc/xoa/<int:id>')
def xoa_mon_hoc(id):
    mon = get_or_404(MON_HOCS, id)
    if mon.phan_congs:
        flash('Không thể xóa môn học đang có phân công giảng viên cho lớp!', 'warning')
        return redirect(url_for('quan_ly_mon_hoc', selected=mon.ma_mon))
    MON_HOCS.remove(mon)
    flash('Đã xóa môn học.', 'info')
    return redirect(url_for('quan_ly_mon_hoc'))

if __name__ == '__main__':
    app.run(debug=True)