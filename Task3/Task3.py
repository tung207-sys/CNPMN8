import unicodedata
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = 'manager_student_system_task3_2026'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///manager_student_system.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# ================= HÀM HỖ TRỢ TÌM KIẾM TIẾNG VIỆT =================

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

# ================= MODELS =================

class GiangVien(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ma_gv = db.Column(db.String(20), unique=True, nullable=False)
    ho_ten = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    khoa = db.Column(db.String(100), nullable=False)
    hoc_vi = db.Column(db.String(50), nullable=False)
    chuyen_mon = db.Column(db.String(120), nullable=False)

    phan_congs = db.relationship('PhanCongGiangDay', backref='giang_vien', lazy=True)

    @property
    def initials(self):
        parts = self.ho_ten.strip().split()
        if len(parts) >= 2:
            return (parts[-2][0] + parts[-1][0]).upper()
        return self.ho_ten[:2].upper()

class MonHoc(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ma_mon = db.Column(db.String(20), unique=True, nullable=False)
    ten_mon = db.Column(db.String(120), nullable=False)
    so_tin_chi = db.Column(db.Integer, nullable=False)
    khoa = db.Column(db.String(100), nullable=False)
    so_tiet = db.Column(db.String(50), nullable=False)
    mo_ta = db.Column(db.String(255), default='')

    phan_congs = db.relationship('PhanCongGiangDay', backref='mon_hoc', lazy=True)

class LopHoc(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ma_lop = db.Column(db.String(20), unique=True, nullable=False)
    ten_lop = db.Column(db.String(100), nullable=False)
    nganh = db.Column(db.String(100), nullable=False)
    khoa_hoc = db.Column(db.String(80), nullable=False)
    si_so = db.Column(db.Integer, nullable=False)
    lich_hoc = db.Column(db.String(100), nullable=False)
    phong = db.Column(db.String(50), nullable=False)

    phan_congs = db.relationship('PhanCongGiangDay', backref='lop_hoc', lazy=True)

class PhanCongGiangDay(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    lop_id = db.Column(db.Integer, db.ForeignKey('lop_hoc.id'), nullable=False)
    mon_hoc_id = db.Column(db.Integer, db.ForeignKey('mon_hoc.id'), nullable=False)
    giang_vien_id = db.Column(db.Integer, db.ForeignKey('giang_vien.id'), nullable=False)



# 1. QUẢN LÝ LỚP HỌC (UC08, UC09, UC11, UC12)
@app.route('/lop-hoc', methods=['GET', 'POST'])
def quan_ly_lop():
    if request.method == 'POST':
        ma_lop = request.form['ma_lop'].strip()
        if LopHoc.query.filter_by(ma_lop=ma_lop).first():
            flash('Mã lớp đã tồn tại!', 'danger')
        else:
            db.session.add(LopHoc(
                ma_lop=ma_lop,
                ten_lop=request.form['ten_lop'].strip(),
                nganh=request.form['nganh'].strip(),
                khoa_hoc=request.form['khoa_hoc'].strip(),
                si_so=int(request.form['si_so']),
                lich_hoc=request.form['lich_hoc'].strip(),
                phong=request.form['phong'].strip()
            ))
            db.session.commit()
            flash('Thêm lớp học thành công!', 'success')
        return redirect(url_for('quan_ly_lop'))

    q = request.args.get('q', '').strip()
    selected_code = request.args.get('selected', '')

    all_lops = LopHoc.query.all()
    ds_lop = [l for l in all_lops if match_keyword(q, l.ma_lop, l.ten_lop)]

    selected_lop = LopHoc.query.filter_by(ma_lop=selected_code).first() if selected_code else None
    if not selected_lop and ds_lop:
        selected_lop = ds_lop[0]

    for lop in ds_lop:
        lop.row_class = 'bg-light' if (selected_lop and selected_lop.id == lop.id) else ''

    ds_mon = MonHoc.query.all()
    ds_gv = GiangVien.query.all()

    return render_template('class.html', ds_lop=ds_lop, selected_lop=selected_lop,
                           ds_mon=ds_mon, ds_gv=ds_gv, q=q)

@app.route('/lop-hoc/sua/<int:id>', methods=['POST'])
def sua_lop(id):
    lop = LopHoc.query.get_or_404(id)
    ma_lop = request.form['ma_lop'].strip()

    if LopHoc.query.filter(LopHoc.ma_lop == ma_lop, LopHoc.id != id).first():
        flash('Mã lớp mới bị trùng với lớp khác!', 'danger')
        return redirect(url_for('quan_ly_lop', selected=lop.ma_lop))

    lop.ma_lop = ma_lop
    lop.ten_lop = request.form['ten_lop'].strip()
    lop.nganh = request.form['nganh'].strip()
    lop.khoa_hoc = request.form['khoa_hoc'].strip()
    lop.si_so = int(request.form['si_so'])
    lop.lich_hoc = request.form['lich_hoc'].strip()
    lop.phong = request.form['phong'].strip()
    db.session.commit()

    flash('Đã cập nhật thông tin lớp học!', 'success')
    return redirect(url_for('quan_ly_lop', selected=lop.ma_lop))

@app.route('/lop-hoc/xoa/<int:id>')
def xoa_lop(id):
    lop = LopHoc.query.get_or_404(id)
    if lop.phan_congs:
        flash('Không thể xóa lớp học đang có môn học được phân công! Hãy gỡ các môn học trước.', 'warning')
        return redirect(url_for('quan_ly_lop', selected=lop.ma_lop))
    db.session.delete(lop)
    db.session.commit()
    flash('Đã xóa lớp học.', 'info')
    return redirect(url_for('quan_ly_lop'))

# 2. PHÂN CÔNG MÔN HỌC & GIẢNG VIÊN VÀO LỚP (UC28)
@app.route('/lop-hoc/phan-cong', methods=['POST'])
def them_phan_cong():
    lop_id = int(request.form['lop_id'])
    mon_hoc_id = int(request.form['mon_hoc_id'])
    giang_vien_id = int(request.form['giang_vien_id'])

    lop = LopHoc.query.get_or_404(lop_id)
    mon = MonHoc.query.get_or_404(mon_hoc_id)
    gv = GiangVien.query.get_or_404(giang_vien_id)

    trung = PhanCongGiangDay.query.filter_by(lop_id=lop.id, mon_hoc_id=mon.id).first()
    if trung:
        flash(f'Môn "{mon.ten_mon}" đã được phân công cho lớp {lop.ma_lop} rồi!', 'warning')
        return redirect(url_for('quan_ly_lop', selected=lop.ma_lop))

    db.session.add(PhanCongGiangDay(
        lop_id=lop.id,
        mon_hoc_id=mon.id,
        giang_vien_id=gv.id
    ))
    db.session.commit()
    flash(f'Đã thêm môn {mon.ten_mon} ({gv.ho_ten}) vào lớp {lop.ma_lop}!', 'success')
    return redirect(url_for('quan_ly_lop', selected=lop.ma_lop))

@app.route('/lop-hoc/sua-phan-cong/<int:id>', methods=['POST'])
def sua_phan_cong(id):
    pc = PhanCongGiangDay.query.get_or_404(id)
    mon_hoc_id = int(request.form['mon_hoc_id'])
    giang_vien_id = int(request.form['giang_vien_id'])

    trung = PhanCongGiangDay.query.filter(
        PhanCongGiangDay.lop_id == pc.lop_id,
        PhanCongGiangDay.mon_hoc_id == mon_hoc_id,
        PhanCongGiangDay.id != id
    ).first()
    if trung:
        flash('Lớp này đã có môn học đó trong danh sách phân công!', 'warning')
        return redirect(url_for('quan_ly_lop', selected=pc.lop_hoc.ma_lop))

    pc.mon_hoc_id = mon_hoc_id
    pc.giang_vien_id = giang_vien_id
    db.session.commit()

    flash('Đã cập nhật môn học & giảng viên của lớp!', 'success')
    return redirect(url_for('quan_ly_lop', selected=pc.lop_hoc.ma_lop))

@app.route('/lop-hoc/xoa-phan-cong/<int:id>')
def xoa_phan_cong(id):
    pc = PhanCongGiangDay.query.get_or_404(id)
    ma_lop = pc.lop_hoc.ma_lop
    db.session.delete(pc)
    db.session.commit()
    flash('Đã gỡ môn học khỏi lớp.', 'info')
    return redirect(url_for('quan_ly_lop', selected=ma_lop))

# 3. QUẢN LÝ GIẢNG VIÊN (UC27 + SỬA GIẢNG VIÊN)
@app.route('/giang-vien', methods=['GET', 'POST'])
def quan_ly_giang_vien():
    if request.method == 'POST':
        ma_gv = request.form['ma_gv'].strip()
        if GiangVien.query.filter_by(ma_gv=ma_gv).first():
            flash('Mã giảng viên đã tồn tại!', 'danger')
        else:
            db.session.add(GiangVien(
                ma_gv=ma_gv,
                ho_ten=request.form['ho_ten'].strip(),
                email=request.form['email'].strip(),
                khoa=request.form['khoa'].strip(),
                hoc_vi=request.form['hoc_vi'].strip(),
                chuyen_mon=request.form['chuyen_mon'].strip()
            ))
            db.session.commit()
            flash('Thêm giảng viên thành công!', 'success')
        return redirect(url_for('quan_ly_giang_vien'))

    q = request.args.get('q', '').strip()
    khoa_q = request.args.get('khoa', '').strip()

    all_gvs = GiangVien.query.all()
    ds_gv = [
        g for g in all_gvs
        if match_keyword(q, g.ma_gv, g.ho_ten) and match_department(khoa_q, g.khoa)
    ]

    tong_gv = len(all_gvs)
    ds_khoa = sorted(list(set(g.khoa for g in all_gvs)))
    so_khoa = len(ds_khoa)

    return render_template('teacher.html', ds_gv=ds_gv, tong_gv=tong_gv,
                           so_khoa=so_khoa, ds_khoa=ds_khoa, q=q, khoa_q=khoa_q)

@app.route('/giang-vien/sua/<int:id>', methods=['POST'])
def sua_giang_vien(id):
    gv = GiangVien.query.get_or_404(id)
    ma_gv = request.form['ma_gv'].strip()

    if GiangVien.query.filter(GiangVien.ma_gv == ma_gv, GiangVien.id != id).first():
        flash('Mã giảng viên mới bị trùng với giảng viên khác!', 'danger')
        return redirect(url_for('quan_ly_giang_vien'))

    gv.ma_gv = ma_gv
    gv.ho_ten = request.form['ho_ten'].strip()
    gv.email = request.form['email'].strip()
    gv.khoa = request.form['khoa'].strip()
    gv.hoc_vi = request.form['hoc_vi'].strip()
    gv.chuyen_mon = request.form['chuyen_mon'].strip()
    db.session.commit()

    flash('Đã cập nhật thông tin giảng viên!', 'success')
    return redirect(url_for('quan_ly_giang_vien'))

@app.route('/giang-vien/xoa/<int:id>')
def xoa_giang_vien(id):
    gv = GiangVien.query.get_or_404(id)
    if gv.phan_congs:
        flash('Không thể xóa giảng viên đang có lịch phân công giảng dạy!', 'warning')
        return redirect(url_for('quan_ly_giang_vien'))
    db.session.delete(gv)
    db.session.commit()
    flash('Đã xóa giảng viên.', 'info')
    return redirect(url_for('quan_ly_giang_vien'))

# 4. QUẢN LÝ MÔN HỌC (UC32, UC33, UC34, UC35)
@app.route('/mon-hoc', methods=['GET', 'POST'])
def quan_ly_mon_hoc():
    if request.method == 'POST':
        ma_mon = request.form['ma_mon'].strip()
        if MonHoc.query.filter_by(ma_mon=ma_mon).first():
            flash('Mã môn học đã tồn tại!', 'danger')
        else:
            db.session.add(MonHoc(
                ma_mon=ma_mon,
                ten_mon=request.form['ten_mon'].strip(),
                so_tin_chi=int(request.form['so_tin_chi']),
                khoa=request.form['khoa'].strip(),
                so_tiet=request.form['so_tiet'].strip(),
                mo_ta=request.form['mo_ta'].strip()
            ))
            db.session.commit()
            flash('Thêm môn học thành công!', 'success')
        return redirect(url_for('quan_ly_mon_hoc'))

    q = request.args.get('q', '').strip()
    selected_code = request.args.get('selected', '')

    all_mons = MonHoc.query.all()
    ds_mon = [m for m in all_mons if match_keyword(q, m.ma_mon, m.ten_mon)]

    selected_mon = MonHoc.query.filter_by(ma_mon=selected_code).first() if selected_code else None
    if not selected_mon and ds_mon:
        selected_mon = ds_mon[0]

    tong_tin_chi = sum(m.so_tin_chi for m in all_mons)

    for m in ds_mon:
        m.row_class = 'bg-light' if (selected_mon and selected_mon.id == m.id) else ''

    return render_template('courses.html', ds_mon=ds_mon, selected_mon=selected_mon, tong_tin_chi=tong_tin_chi, q=q)

@app.route('/mon-hoc/sua/<int:id>', methods=['POST'])
def sua_mon_hoc(id):
    mon = MonHoc.query.get_or_404(id)
    ma_mon = request.form['ma_mon'].strip()

    if MonHoc.query.filter(MonHoc.ma_mon == ma_mon, MonHoc.id != id).first():
        flash('Mã môn học mới bị trùng với môn học khác!', 'danger')
        return redirect(url_for('quan_ly_mon_hoc', selected=mon.ma_mon))

    mon.ma_mon = ma_mon
    mon.ten_mon = request.form['ten_mon'].strip()
    mon.so_tin_chi = int(request.form['so_tin_chi'])
    mon.khoa = request.form['khoa'].strip()
    mon.so_tiet = request.form['so_tiet'].strip()
    mon.mo_ta = request.form['mo_ta'].strip()
    db.session.commit()

    flash('Đã cập nhật thông tin môn học!', 'success')
    return redirect(url_for('quan_ly_mon_hoc', selected=mon.ma_mon))

@app.route('/mon-hoc/xoa/<int:id>')
def xoa_mon_hoc(id):
    mon = MonHoc.query.get_or_404(id)
    if mon.phan_congs:
        flash('Không thể xóa môn học đang có phân công giảng viên cho lớp!', 'warning')
        return redirect(url_for('quan_ly_mon_hoc', selected=mon.ma_mon))
    db.session.delete(mon)
    db.session.commit()
    flash('Đã xóa môn học.', 'info')
    return redirect(url_for('quan_ly_mon_hoc'))

if __name__ == '__main__':
    app.run(debug=True)