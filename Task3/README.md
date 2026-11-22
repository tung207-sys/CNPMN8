# Manager Student System

Ứng dụng web quản lý lớp học, giảng viên và môn học, xây dựng bằng Flask với dữ liệu mẫu lưu trong bộ nhớ.

## Yêu cầu

- Python 3.10 trở lên
- pip

## Cài đặt

Mở terminal tại thư mục dự án và cài các thư viện:

```powershell
python -m pip install -r requirements.txt
```

## Chạy ứng dụng

```powershell
Set-Location .\Task3
python .\Task3.py
```

Mở [http://127.0.0.1:5000/lop-hoc](http://127.0.0.1:5000/lop-hoc) để sử dụng chức năng quản lý lớp học. Các trang khác:

- `/giang-vien` — quản lý giảng viên
- `/mon-hoc` — quản lý môn học

Ứng dụng sử dụng dữ liệu mẫu trong bộ nhớ. Các thay đổi sẽ được khởi tạo lại khi khởi động lại ứng dụng.

## Chạy trong VS Code

Mở thư mục gốc của dự án trong VS Code. Chọn cấu hình **Manager Student System** trong mục Run and Debug và nhấn F5. Có thể chạy trực tiếp lệnh ở trên trong terminal tích hợp.
