import unicodedata
from flask import Blueprint, render_template, request, redirect, url_for, flash, abort, session
from models.academic import GiangVien, MonHoc, LopHoc, PhanCongGiangDay
from data.shared_data import GIANG_VIENS, MON_HOCS, LOP_HOCS, PHAN_CONGS

academic_bp = Blueprint('academic', __name__)

@academic_bp.before_request
def check_admin():
    if "username" not in session or session.get("role") != "admin":
        return redirect(url_for("login"))

# dùng để tìm kiếm bằng từ khóa tiếng việt không dấu và không phân biệt hoa thường
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

def get_or_404(items, item_id):
    item = next((x for x in items if x.id == item_id), None)
    if item is None:
        abort(404)
    return item

def get_next_id(items):
    return max((x.id for x in items), default=0) + 1

@academic_bp.route('/')
def index():
    return redirect(url_for('academic.quan_ly_lop'))

# 1. quản lý lớp học
@academic_bp.route('/lop-hoc', methods=['GET', 'POST'])
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
        return redirect(url_for('academic.quan_ly_lop'))

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

@academic_bp.route('/lop-hoc/sua/<int:id>', methods=['POST'])
def sua_lop(id):
    lop = get_or_404(LOP_HOCS, id)
    ma_lop = request.form['ma_lop'].strip()

    if any(l.ma_lop == ma_lop and l.id != id for l in LOP_HOCS):
        flash('Mã lớp mới bị trùng với lớp khác!', 'danger')
        return redirect(url_for('academic.quan_ly_lop', selected=lop.ma_lop))

    lop.ma_lop = ma_lop
    lop.ten_lop = request.form['ten_lop'].strip()
    lop.nganh = request.form['nganh'].strip()
    lop.khoa_hoc = request.form['khoa_hoc'].strip()
    lop.si_so = int(request.form['si_so'])
    lop.lich_hoc = request.form['lich_hoc'].strip()
    lop.phong = request.form['phong'].strip()

    flash('Đã cập nhật thông tin lớp học!', 'success')
    return redirect(url_for('academic.quan_ly_lop', selected=lop.ma_lop))

@academic_bp.route('/lop-hoc/xoa/<int:id>')
def xoa_lop(id):
    lop = get_or_404(LOP_HOCS, id)
    if lop.phan_congs:
        flash('Không thể xóa lớp học đang có môn học được phân công! Hãy gỡ các môn học trước.', 'warning')
        return redirect(url_for('academic.quan_ly_lop', selected=lop.ma_lop))
    LOP_HOCS.remove(lop)
    flash('Đã xóa lớp học.', 'info')
    return redirect(url_for('academic.quan_ly_lop'))

# 2. thêm môn học và giảng viên vào lớp học
@academic_bp.route('/lop-hoc/phan-cong', methods=['POST'])
def them_phan_cong():
    lop_id = int(request.form['lop_id'])
    mon_hoc_id = int(request.form['mon_hoc_id'])
    giang_vien_id = int(request.form['giang_vien_id'])

    lop = get_or_404(LOP_HOCS, lop_id)
    mon = get_or_404(MON_HOCS, mon_hoc_id)
    gv = get_or_404(GIANG_VIENS, giang_vien_id)

    if any(pc.lop_id == lop.id and pc.mon_hoc_id == mon.id for pc in PHAN_CONGS):
        flash(f'Môn "{mon.ten_mon}" đã được phân công cho lớp {lop.ma_lop} rồi!', 'warning')
        return redirect(url_for('academic.quan_ly_lop', selected=lop.ma_lop))

    PHAN_CONGS.append(PhanCongGiangDay(
        id=get_next_id(PHAN_CONGS),
        lop_id=lop.id,
        mon_hoc_id=mon.id,
        giang_vien_id=gv.id
    ))
    flash(f'Đã thêm môn {mon.ten_mon} ({gv.ho_ten}) vào lớp {lop.ma_lop}!', 'success')
    return redirect(url_for('academic.quan_ly_lop', selected=lop.ma_lop))

@academic_bp.route('/lop-hoc/sua-phan-cong/<int:id>', methods=['POST'])
def sua_phan_cong(id):
    pc = get_or_404(PHAN_CONGS, id)
    mon_hoc_id = int(request.form['mon_hoc_id'])
    giang_vien_id = int(request.form['giang_vien_id'])

    if any(p.lop_id == pc.lop_id and p.mon_hoc_id == mon_hoc_id and p.id != id for p in PHAN_CONGS):
        flash('Lớp này đã có môn học đó trong danh sách phân công!', 'warning')
        return redirect(url_for('academic.quan_ly_lop', selected=pc.lop_hoc.ma_lop))

    pc.mon_hoc_id = mon_hoc_id
    pc.giang_vien_id = giang_vien_id

    flash('Đã cập nhật môn học & giảng viên của lớp!', 'success')
    return redirect(url_for('academic.quan_ly_lop', selected=pc.lop_hoc.ma_lop))

@academic_bp.route('/lop-hoc/xoa-phan-cong/<int:id>')
def xoa_phan_cong(id):
    pc = get_or_404(PHAN_CONGS, id)
    ma_lop = pc.lop_hoc.ma_lop
    PHAN_CONGS.remove(pc)
    flash('Đã gỡ môn học khỏi lớp.', 'info')
    return redirect(url_for('academic.quan_ly_lop', selected=ma_lop))

# 3. quản lý giảng viên
@academic_bp.route('/giang-vien', methods=['GET', 'POST'])
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
        return redirect(url_for('academic.quan_ly_giang_vien'))

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

@academic_bp.route('/giang-vien/sua/<int:id>', methods=['POST'])
def sua_giang_vien(id):
    gv = get_or_404(GIANG_VIENS, id)
    ma_gv = request.form['ma_gv'].strip()

    if any(g.ma_gv == ma_gv and g.id != id for g in GIANG_VIENS):
        flash('Mã giảng viên mới bị trùng với giảng viên khác!', 'danger')
        return redirect(url_for('academic.quan_ly_giang_vien'))

    gv.ma_gv = ma_gv
    gv.ho_ten = request.form['ho_ten'].strip()
    gv.email = request.form['email'].strip()
    gv.khoa = request.form['khoa'].strip()
    gv.hoc_vi = request.form['hoc_vi'].strip()
    gv.chuyen_mon = request.form['chuyen_mon'].strip()

    flash('Đã cập nhật thông tin giảng viên!', 'success')
    return redirect(url_for('academic.quan_ly_giang_vien'))

@academic_bp.route('/giang-vien/xoa/<int:id>')
def xoa_giang_vien(id):
    gv = get_or_404(GIANG_VIENS, id)
    if gv.phan_congs:
        flash('Không thể xóa giảng viên đang có lịch phân công giảng dạy!', 'warning')
        return redirect(url_for('academic.quan_ly_giang_vien'))
    GIANG_VIENS.remove(gv)
    flash('Đã xóa giảng viên.', 'info')
    return redirect(url_for('academic.quan_ly_giang_vien'))

# 4. quản lý môn học
@academic_bp.route('/mon-hoc', methods=['GET', 'POST'])
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
        return redirect(url_for('academic.quan_ly_mon_hoc'))

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

@academic_bp.route('/mon-hoc/sua/<int:id>', methods=['POST'])
def sua_mon_hoc(id):
    mon = get_or_404(MON_HOCS, id)
    ma_mon = request.form['ma_mon'].strip()

    if any(m.ma_mon == ma_mon and m.id != id for m in MON_HOCS):
        flash('Mã môn học mới bị trùng với môn học khác!', 'danger')
        return redirect(url_for('academic.quan_ly_mon_hoc', selected=mon.ma_mon))

    mon.ma_mon = ma_mon
    mon.ten_mon = request.form['ten_mon'].strip()
    mon.so_tin_chi = int(request.form['so_tin_chi'])
    mon.khoa = request.form['khoa'].strip()
    mon.so_tiet = request.form['so_tiet'].strip()
    mon.mo_ta = request.form['mo_ta'].strip()

    flash('Đã cập nhật thông tin môn học!', 'success')
    return redirect(url_for('academic.quan_ly_mon_hoc', selected=mon.ma_mon))

@academic_bp.route('/mon-hoc/xoa/<int:id>')
def xoa_mon_hoc(id):
    mon = get_or_404(MON_HOCS, id)
    if mon.phan_congs:
        flash('Không thể xóa môn học đang có phân công giảng viên cho lớp!', 'warning')
        return redirect(url_for('academic.quan_ly_mon_hoc', selected=mon.ma_mon))
    MON_HOCS.remove(mon)
    flash('Đã xóa môn học.', 'info')
    return redirect(url_for('academic.quan_ly_mon_hoc'))

