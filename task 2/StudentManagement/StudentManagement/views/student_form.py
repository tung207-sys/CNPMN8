import tkinter as tk
from tkinter import ttk, messagebox
from models.student import Student


class StudentForm(tk.Toplevel):
    def __init__(self, parent, manager, on_success_callback, student=None):
        super().__init__(parent)
        self.manager = manager
        self.on_success_callback = on_success_callback
        self.student = student

        self.title("Thêm Sinh Viên Mới" if student is None else f"Cập Nhật Sinh Viên - {student.student_id}")
        self.geometry("460x430")
        self.resizable(False, False)
        self.configure(bg="#F4F6F9")
        self.grab_set()

        self._build_ui()
        if self.student:
            self._fill_data()

    def _build_ui(self):
        header_text = "THÊM SINH VIÊN MỚI" if self.student is None else "CẬP NHẬT THÔNG TIN SINH VIÊN"
        header = tk.Label(
            self,
            text=header_text,
            bg="#C8102E",
            fg="white",
            font=("Arial", 13, "bold"),
            pady=10,
        )
        header.pack(fill=tk.X)

        form_frame = tk.Frame(self, bg="#F4F6F9", padx=25, pady=15)
        form_frame.pack(fill=tk.BOTH, expand=True)

        labels = [
            "Mã sinh viên (ID) *:",
            "Họ và tên *:",
            "Ngày sinh (dd/mm/yyyy) *:",
            "Giới tính *:",
            "Địa chỉ *:",
            "Email *:",
            "Lớp *:",
        ]

        for idx, text in enumerate(labels):
            tk.Label(
                form_frame,
                text=text,
                bg="#F4F6F9",
                font=("Arial", 10, "bold"),
                anchor="w",
            ).grid(row=idx, column=0, sticky="w", pady=7)

        self.entry_id = ttk.Entry(form_frame, width=30, font=("Arial", 10))
        self.entry_name = ttk.Entry(form_frame, width=30, font=("Arial", 10))
        self.entry_dob = ttk.Entry(form_frame, width=30, font=("Arial", 10))
        self.combo_gender = ttk.Combobox(
            form_frame,
            values=["Nam", "Nữ", "Khác"],
            state="readonly",
            width=28,
            font=("Arial", 10),
        )
        self.combo_gender.set("Nam")
        self.entry_address = ttk.Entry(form_frame, width=30, font=("Arial", 10))
        self.entry_email = ttk.Entry(form_frame, width=30, font=("Arial", 10))
        self.combo_class = ttk.Combobox(
            form_frame,
            values=self.manager.get_all_classes(),
            width=28,
            font=("Arial", 10),
        )
        self.combo_class.set("CNTT01")

        widgets = [
            self.entry_id,
            self.entry_name,
            self.entry_dob,
            self.combo_gender,
            self.entry_address,
            self.entry_email,
            self.combo_class,
        ]
        for idx, widget in enumerate(widgets):
            widget.grid(row=idx, column=1, pady=7, padx=(10, 0))

        btn_frame = tk.Frame(self, bg="#F4F6F9", pady=12)
        btn_frame.pack(fill=tk.X)

        btn_save = tk.Button(
            btn_frame,
            text="💾 Lưu thông tin",
            bg="#2E8B57",
            fg="white",
            font=("Arial", 10, "bold"),
            width=15,
            cursor="hand2",
            command=self._handle_save,
        )
        btn_save.pack(side=tk.LEFT, padx=(95, 15))

        btn_cancel = tk.Button(
            btn_frame,
            text="✖ Hủy",
            bg="#6C757D",
            fg="white",
            font=("Arial", 10, "bold"),
            width=12,
            cursor="hand2",
            command=self.destroy,
        )
        btn_cancel.pack(side=tk.LEFT)

    def _fill_data(self):
        self.entry_id.insert(0, self.student.student_id)
        self.entry_id.configure(state="disabled")
        self.entry_name.insert(0, self.student.full_name)
        self.entry_dob.insert(0, self.student.dob)
        self.combo_gender.set(self.student.gender)
        self.entry_address.insert(0, self.student.address)
        self.entry_email.insert(0, self.student.email)
        self.combo_class.set(self.student.class_id)

    def _handle_save(self):
        student_id = self.entry_id.get().strip()
        full_name = self.entry_name.get().strip()
        dob = self.entry_dob.get().strip()
        gender = self.combo_gender.get().strip()
        address = self.entry_address.get().strip()
        email = self.entry_email.get().strip()
        class_id = self.combo_class.get().strip()

        try:
            if self.student is None:
                new_student = Student(student_id, full_name, dob, gender, address, email, class_id)
                self.manager.add_student(new_student)
                messagebox.showinfo("Thành công", "Đã thêm sinh viên mới!", parent=self)
            else:
                updated_data = {
                    "full_name": full_name,
                    "dob": dob,
                    "gender": gender,
                    "address": address,
                    "email": email,
                    "class_id": class_id,
                }
                self.manager.update_student(self.student.student_id, updated_data)
                messagebox.showinfo("Thành công", "Đã cập nhật thông tin sinh viên!", parent=self)

            self.on_success_callback()
            self.destroy()
        except ValueError as err:
            messagebox.showwarning("Dữ liệu không hợp lệ", str(err), parent=self)
