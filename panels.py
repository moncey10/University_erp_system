import tkinter as tk
from tkinter import messagebox, simpledialog, ttk

from course_service import CourseService

service = CourseService()

vcmd_person = None
vcmd_course = None


def init_ui(root: tk.Tk):
    global vcmd_person, vcmd_course
    vcmd_person = (root.register(validate_person_name_input), "%P")
    vcmd_course = (root.register(validate_course_name_input), "%P")


def cap(text: str) -> str:
    return (text or "").strip().title()


def validate_person_name_input(P):
    if P == "":
        return True
    return all(ch.isalpha() or ch.isspace() for ch in P)


def validate_course_name_input(P):
    if P == "":
        return True
    allowed_symbols = set("-:_ ")
    has_letter = False
    for ch in P:
        if ch.isalpha():
            has_letter = True
        elif ch.isdigit() or ch in allowed_symbols:
            pass
        else:
            return False
    return has_letter


# -------------------- Dropdown dialogs --------------------
def select_course_dialog(parent, title="Select Course"):
    courses = service.show_courses()
    course_names = [c[0] for c in courses] if courses else []

    dialog = tk.Toplevel(parent)
    dialog.title(title)
    dialog.transient(parent)
    dialog.grab_set()
    dialog.geometry("+{}+{}".format(parent.winfo_x() + 150, parent.winfo_y() + 150))

    tk.Label(dialog, text="Select a course:", font=("Arial", 11)).pack(pady=10, padx=20)

    combo = ttk.Combobox(dialog, values=course_names, state="readonly", width=32)
    combo.pack(pady=5, padx=20)
    if course_names:
        combo.current(0)

    result = {"value": None}

    def on_ok():
        v = combo.get().strip()
        result["value"] = v if v else None
        dialog.destroy()

    def on_cancel():
        dialog.destroy()

    btn = tk.Frame(dialog)
    btn.pack(pady=15)
    tk.Button(btn, text="OK", width=10, command=on_ok).pack(side="left", padx=10)
    tk.Button(btn, text="Cancel", width=10, command=on_cancel).pack(side="left", padx=10)

    if not course_names:
        messagebox.showwarning("No Courses", "No courses found. Ask admin to add courses first.", parent=dialog)

    dialog.wait_window()
    return result["value"]


def select_user_dialog(parent, title, role, only_approved_professors=True):
    users = service.get_users_by_role(role, only_approved_professors=only_approved_professors)

    dialog = tk.Toplevel(parent)
    dialog.title(title)
    dialog.transient(parent)
    dialog.grab_set()
    dialog.geometry("+{}+{}".format(parent.winfo_x() + 150, parent.winfo_y() + 150))

    tk.Label(dialog, text=f"Select {role}:", font=("Arial", 11)).pack(pady=10, padx=20)

    values = [f"{u[1]}  <{u[2]}>  (ID:{u[0]})" for u in users]
    combo = ttk.Combobox(dialog, values=values, state="readonly", width=45)
    combo.pack(pady=5, padx=20)
    if values:
        combo.current(0)

    result = {"sel": None}

    def on_ok():
        idx = combo.current()
        if 0 <= idx < len(users):
            result["sel"] = users[idx]
        dialog.destroy()

    def on_cancel():
        dialog.destroy()

    btn = tk.Frame(dialog)
    btn.pack(pady=15)
    tk.Button(btn, text="OK", width=10, command=on_ok).pack(side="left", padx=10)
    tk.Button(btn, text="Cancel", width=10, command=on_cancel).pack(side="left", padx=10)

    if not users:
        messagebox.showwarning("No Users", f"No {role} users found.", parent=dialog)

    dialog.wait_window()
    return result["sel"]


# ======================= AUTH WINDOW =======================
def open_auth_window(root, role: str):
    win = tk.Toplevel(root)
    win.title(f"{cap(role)} Login / Register")
    win.geometry("420x330")
    win.resizable(False, False)
    win.protocol("WM_DELETE_WINDOW", root.destroy)

    tk.Label(win, text=f"{cap(role)} Authentication", font=("Arial", 15, "bold")).pack(pady=12)

    switch = tk.Frame(win)
    switch.pack(pady=5)

    body = tk.Frame(win)
    body.pack(fill="both", expand=True, padx=18, pady=10)

    def clear_body():
        for w in body.winfo_children():
            w.destroy()

    def show_login():
        clear_body()
        tk.Label(body, text="Login", font=("Arial", 12, "bold")).grid(row=0, column=0, columnspan=2, pady=6)

        tk.Label(body, text="Email:").grid(row=1, column=0, sticky="e", pady=6)
        e_email = tk.Entry(body, width=30)
        e_email.grid(row=1, column=1, pady=6)

        tk.Label(body, text="Password:").grid(row=2, column=0, sticky="e", pady=6)
        e_pass = tk.Entry(body, width=30, show="*")
        e_pass.grid(row=2, column=1, pady=6)

        def do_login():
            ok, res = service.login_user(e_email.get(), e_pass.get(), role)
            if not ok:
                messagebox.showwarning("Login Failed", str(res), parent=win)
                return

            win.destroy()
            if role == "admin":
                open_admin_panel(root, res)
            elif role == "professor":
                open_professor_panel(root, res)
            else:
                open_student_panel(root, res)

        tk.Button(body, text="Login", width=16, command=do_login).grid(row=3, column=0, columnspan=2, pady=12)

    def show_register():
        clear_body()
        tk.Label(body, text="Register", font=("Arial", 12, "bold")).grid(row=0, column=0, columnspan=2, pady=6)

        tk.Label(body, text="Name:").grid(row=1, column=0, sticky="e", pady=6)
        e_name = tk.Entry(body, width=30, validate="key", validatecommand=vcmd_person)
        e_name.grid(row=1, column=1, pady=6)

        tk.Label(body, text="Email:").grid(row=2, column=0, sticky="e", pady=6)
        e_email = tk.Entry(body, width=30)
        e_email.grid(row=2, column=1, pady=6)

        tk.Label(body, text="Mobile:").grid(row=3, column=0, sticky="e", pady=6)
        e_mobile = tk.Entry(body, width=30)
        e_mobile.grid(row=3, column=1, pady=6)

        tk.Label(body, text="Password:").grid(row=4, column=0, sticky="e", pady=6)
        e_pass = tk.Entry(body, width=30, show="*")
        e_pass.grid(row=4, column=1, pady=6)

        def do_register():
            ok, res = service.register_user(
                e_name.get(),
                e_email.get(),
                e_pass.get(),
                role,
                e_mobile.get()
            )
            if not ok:
                messagebox.showwarning("Register Failed", str(res), parent=win)
                return

            if role == "professor":
                messagebox.showinfo("Registered", "Professor account created.\nStatus: waiting (admin must approve).", parent=win)
            else:
                messagebox.showinfo("Registered", "Account created. Now login.", parent=win)

            show_login()

        tk.Button(body, text="Register", width=16, command=do_register).grid(row=5, column=0, columnspan=2, pady=12)

    tk.Button(switch, text="Login", width=12, command=show_login).pack(side="left", padx=8)
    tk.Button(switch, text="Register", width=12, command=show_register).pack(side="left", padx=8)

    show_login()


# ======================= ADMIN PANEL =======================
def open_admin_panel(root, user_ctx):
    win = tk.Toplevel(root)
    win.title("Admin Panel")
    win.geometry("920x640")
    win.resizable(False, False)
    win.protocol("WM_DELETE_WINDOW", root.destroy)

    tk.Label(win, text=f"Admin Panel | Logged in: {user_ctx['user_name']}", font=("Arial", 14, "bold")).pack(pady=10)

    # -------- Courses --------
    tk.Label(win, text="Courses", font=("Arial", 12, "bold")).pack(pady=(6, 0))
    course_list = tk.Listbox(win, width=90, height=7)
    course_list.pack(pady=8)

    def refresh_courses():
        course_list.delete(0, tk.END)
        rows = service.show_courses() or []
        if not rows:
            course_list.insert(tk.END, "No courses available")
        else:
            for r in rows:
                course_list.insert(tk.END, r[0])

    def add_course():
        name = simpledialog.askstring("Add Course", "Course name:", parent=win)
        if not name:
            return
        if service.add_course(cap(name)):
            messagebox.showinfo("Success", "Course added.", parent=win)
        else:
            messagebox.showwarning("Failed", "Course exists / DB error.", parent=win)
        refresh_courses()

    def delete_course():
        course = select_course_dialog(win, "Delete Course")
        if not course:
            return
        if service.delete_course(cap(course)):
            messagebox.showinfo("Success", "Course deleted.", parent=win)
        else:
            messagebox.showwarning("Failed", "Course not found / DB error.", parent=win)
        refresh_courses()

    def enroll_student_dropdown():
        sel = select_user_dialog(win, "Select Student", "student", only_approved_professors=False)
        if not sel:
            return
        student_id, student_name, _ = sel

        course = select_course_dialog(win, "Select Course")
        if not course:
            return

        if service.enroll_student_by_id(student_id, cap(course)):
            messagebox.showinfo("Success", f"{student_name} enrolled in {cap(course)}.", parent=win)
        else:
            messagebox.showwarning("Failed", "Course not found / DB error.", parent=win)

    def assign_professor_dropdown():
        sel = select_user_dialog(win, "Select Professor", "professor", only_approved_professors=True)
        if not sel:
            return
        prof_id, prof_name, _ = sel

        course = select_course_dialog(win, "Select Course")
        if not course:
            return

        if service.assign_professor_to_course_by_id(prof_id, cap(course)):
            messagebox.showinfo("Success", f"{prof_name} assigned to {cap(course)}.", parent=win)
        else:
            messagebox.showwarning("Failed", "Course not found / DB error.", parent=win)

    btn_frame = tk.Frame(win)
    btn_frame.pack(pady=8)
    tk.Button(btn_frame, text="Add Course", width=24, command=add_course).grid(row=0, column=0, padx=10, pady=6)
    tk.Button(btn_frame, text="Delete Course", width=24, command=delete_course).grid(row=0, column=1, padx=10, pady=6)
    tk.Button(btn_frame, text="Enroll Student (Dropdown)", width=24, command=enroll_student_dropdown).grid(row=1, column=0, padx=10, pady=6)
    tk.Button(btn_frame, text="Assign Professor (Dropdown)", width=24, command=assign_professor_dropdown).grid(row=1, column=1, padx=10, pady=6)

    # -------- Professor approvals --------
    tk.Label(win, text="Professor Accounts (waiting)", font=("Arial", 12, "bold")).pack(pady=(14, 0))
    prof_list = tk.Listbox(win, width=90, height=6)
    prof_list.pack(pady=8)

    def refresh_prof_waiting():
        prof_list.delete(0, tk.END)
        rows = service.get_professors_by_status("waiting")
        if not rows:
            prof_list.insert(tk.END, "No waiting professors")
            return
        for uid, name, email, status in rows:
            prof_list.insert(tk.END, f"{uid} | {name} | {email} | {status}")

    def _selected_prof_id():
        if not prof_list.curselection():
            return None
        text = prof_list.get(prof_list.curselection()[0])
        if "|" not in text:
            return None
        return int(text.split("|")[0].strip())

    def approve_prof():
        pid = _selected_prof_id()
        if not pid:
            return
        service.set_professor_account_status(pid, "approved")
        refresh_prof_waiting()
        messagebox.showinfo("Approved", "Professor approved.", parent=win)

    def reject_prof():
        pid = _selected_prof_id()
        if not pid:
            return
        service.set_professor_account_status(pid, "rejected")
        refresh_prof_waiting()
        messagebox.showinfo("Rejected", "Professor rejected.", parent=win)

    prof_btn = tk.Frame(win)
    prof_btn.pack(pady=4)
    tk.Button(prof_btn, text="Approve", width=12, command=approve_prof).pack(side="left", padx=10)
    tk.Button(prof_btn, text="Reject", width=12, command=reject_prof).pack(side="left", padx=10)

    tk.Button(win, text="Logout", width=12, command=lambda: [win.destroy(), open_auth_window(root, "admin")]).pack(pady=12)

    refresh_courses()
    refresh_prof_waiting()


# ======================= PROFESSOR PANEL =======================
def open_professor_panel(root, user_ctx):
    win = tk.Toplevel(root)
    win.title("Professor Panel")
    win.geometry("760x520")
    win.resizable(False, False)
    win.protocol("WM_DELETE_WINDOW", root.destroy)

    prof_id = user_ctx["user_id"]
    prof_name = user_ctx["user_name"]

    tk.Label(win, text=f"Professor Panel | Logged in: {prof_name}", font=("Arial", 14, "bold")).pack(pady=15)

    def professor_view_courses():
        rows = service.view_professor_courses_by_id(prof_id) or []
        courses = [r[0] for r in rows]
        messagebox.showinfo("My Courses", "\n".join(courses) if courses else "No assigned courses.", parent=win)

    def professor_view_students():
        course = select_course_dialog(win, "Select Course")
        if not course:
            return
        rows = service.view_enrolled_students(cap(course)) or []
        students = [r[0] for r in rows]
        messagebox.showinfo("Enrolled Students", "\n".join(students) if students else "No students enrolled.", parent=win)

    def professor_upload_grade():
        sel = select_user_dialog(win, "Select Student", "student", only_approved_professors=False)
        if not sel:
            return
        sid, sname, _ = sel

        course = select_course_dialog(win, "Select Course")
        if not course:
            return

        grade = simpledialog.askstring("Grade", f"Enter grade for {sname}:", parent=win)
        if not grade:
            return

        ok = service.upload_student_grades_by_id(sid, cap(course), grade)
        if ok:
            messagebox.showinfo("Saved", "Grade saved.", parent=win)
        else:
            messagebox.showwarning("Failed", "Student not enrolled / wrong course / DB error.", parent=win)

    tk.Button(win, text="View My Courses", width=32, command=professor_view_courses).pack(pady=10)
    tk.Button(win, text="View Students in Course", width=32, command=professor_view_students).pack(pady=10)
    tk.Button(win, text="Upload Student Grade (Dropdown)", width=32, command=professor_upload_grade).pack(pady=10)

    tk.Button(win, text="Logout", width=12, command=lambda: [win.destroy(), open_auth_window(root, "professor")]).pack(pady=15)


# ======================= STUDENT PANEL =======================
def open_student_panel(root, user_ctx):
    win = tk.Toplevel(root)
    win.title("Student Panel")
    win.geometry("760x480")
    win.resizable(False, False)
    win.protocol("WM_DELETE_WINDOW", root.destroy)

    student_id = user_ctx["user_id"]
    student_name = user_ctx["user_name"]

    tk.Label(win, text=f"Student Panel | Logged in: {student_name}", font=("Arial", 14, "bold")).pack(pady=15)

    def student_enroll_course():
        course = select_course_dialog(win, "Select Course")
        if not course:
            return
        ok = service.enroll_student_by_id(student_id, cap(course))
        messagebox.showinfo("Enrolled" if ok else "Failed",
                            f"{student_name} -> {cap(course)}" if ok else "Course not found / DB error.",
                            parent=win)

    def student_view_courses():
        rows = service.view_student_courses_by_id(student_id) or []
        courses = [r[0] for r in rows]
        messagebox.showinfo("My Courses", "\n".join(courses) if courses else "No courses found.", parent=win)

    def student_view_grade():
        course = select_course_dialog(win, "Select Course")
        if not course:
            return
        g = service.view_student_grades_by_id(student_id, cap(course))
        messagebox.showinfo("My Grade", g if g else "No grade found yet.", parent=win)

    tk.Button(win, text="Enroll in Course", width=32, command=student_enroll_course).pack(pady=10)
    tk.Button(win, text="View My Courses", width=32, command=student_view_courses).pack(pady=10)
    tk.Button(win, text="View My Grade", width=32, command=student_view_grade).pack(pady=10)

    tk.Button(win, text="Logout", width=12, command=lambda: [win.destroy(), open_auth_window(root, "student")]).pack(pady=15)
