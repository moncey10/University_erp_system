import tkinter as tk
from tkinter import messagebox, simpledialog, ttk

from course_service import CourseService
from Professor.professor_task import Professor
from Student.student import Student

# ------------------ BACKEND SERVICES ------------------
service = CourseService()
professor_service = Professor(service)
student_service = Student(service)

# Will be set by init_ui(root)
vcmd_person = None
vcmd_course = None


def init_ui(root: tk.Tk):
    """Call once from each entry file after root = tk.Tk()"""
    global vcmd_person, vcmd_course
    vcmd_person = (root.register(validate_person_name_input), "%P")
    vcmd_course = (root.register(validate_course_name_input), "%P")


def cap(text: str) -> str:
    return text.strip().title()


# ============== REAL-TIME INPUT VALIDATION ==============
def validate_person_name_input(P):
    """Allow only letters and spaces"""
    if P == "":
        return True
    return all(ch.isalpha() or ch.isspace() for ch in P)


def validate_course_name_input(P):
    """
    Allow letters, spaces, hyphens, colons, underscores.
    Digits allowed BUT must contain at least one letter.
    """
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


def askValidatedInput(parent, title, prompt, is_course=False):
    """Custom dialog with validation."""
    dialog = tk.Toplevel(parent)
    dialog.title(title)
    dialog.transient(parent)
    dialog.grab_set()

    dialog.geometry("+{}+{}".format(parent.winfo_x() + 150, parent.winfo_y() + 150))

    tk.Label(dialog, text=prompt, font=("Arial", 11)).pack(pady=10, padx=20)

    if is_course:
        entry = tk.Entry(dialog, width=35, validate="key", validatecommand=vcmd_course)
        hint = "Must contain at least one letter (digits, spaces, -, :, _ allowed)"
    else:
        entry = tk.Entry(dialog, width=35, validate="key", validatecommand=vcmd_person)
        hint = "Letters and spaces only (NO digits)"

    entry.pack(pady=5, padx=20)
    entry.focus_set()
    tk.Label(dialog, text=hint, font=("Arial", 8), fg="red").pack(pady=2)

    result = {"value": None, "validated": False}

    def on_ok():
        value = entry.get().strip()
        if value:
            result["value"] = value
            result["validated"] = True
        dialog.destroy()

    def on_cancel():
        dialog.destroy()

    btn_frame = tk.Frame(dialog)
    btn_frame.pack(pady=15)

    tk.Button(btn_frame, text="OK", width=10, command=on_ok).pack(side="left", padx=10)
    tk.Button(btn_frame, text="Cancel", width=10, command=on_cancel).pack(side="left", padx=10)

    dialog.wait_window()
    return result["value"], result["validated"]


def select_course_dialog(parent, title="Select Course"):
    """Dropdown dialog for selecting an existing course from DB."""
    courses = service.show_courses()  # list of tuples [(name,), ...]
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
        val = combo.get().strip()
        result["value"] = val if val else None
        dialog.destroy()

    def on_cancel():
        dialog.destroy()

    btn = tk.Frame(dialog)
    btn.pack(pady=15)
    tk.Button(btn, text="OK", width=10, command=on_ok).pack(side="left", padx=10)
    tk.Button(btn, text="Cancel", width=10, command=on_cancel).pack(side="left", padx=10)

    if not course_names:
        messagebox.showwarning(
            "No Courses",
            "No courses found.\nAsk admin to add courses first.",
            parent=dialog
        )

    dialog.wait_window()
    return result["value"]


# ======================= ADMIN WINDOW =======================
def open_admin_panel(root):
    win = tk.Toplevel(root)
    win.title("Admin Panel")
    win.geometry("800x560")
    win.resizable(False, False)

    win.protocol("WM_DELETE_WINDOW", root.destroy)

    tk.Label(win, text="Admin Panel", font=("Arial", 16, "bold")).pack(pady=10)

    # ---- Courses list ----
    tk.Label(win, text="Courses", font=("Arial", 12, "bold")).pack(pady=(5, 0))

    course_list = tk.Listbox(win, width=65, height=10)
    course_list.pack(pady=8)

    def refresh_courses():
        course_list.delete(0, tk.END)
        courses = service.show_courses()
        if not courses:
            course_list.insert(tk.END, "No courses available")
        else:
            for c in courses:
                course_list.insert(tk.END, c[0])

    def add_course():
        name, ok = askValidatedInput(win, "Add Course", "Enter course name:", is_course=True)
        if not ok or not name:
            return
        name = cap(name)
        if service.add_course(name):
            messagebox.showinfo("Success", f"Course '{name}' added.", parent=win)
        else:
            messagebox.showwarning("Warning", f"Course '{name}' already exists or DB error.", parent=win)
        refresh_courses()

    def delete_course():
        course = select_course_dialog(win, "Delete Course")
        if not course:
            return
        course = cap(course)
        if service.delete_course(course):
            messagebox.showinfo("Success", f"Course '{course}' deleted.", parent=win)
        else:
            messagebox.showwarning("Warning", f"Course '{course}' not found.", parent=win)
        refresh_courses()

    def assign_professor_direct():
        prof, ok = askValidatedInput(win, "Assign Professor", "Enter professor name:")
        if not ok or not prof:
            return

        course = select_course_dialog(win, "Select Course")
        if not course:
            return

        prof = cap(prof)
        course = cap(course)

        if service.assign_professor_to_course(prof, course):
            messagebox.showinfo("Success", f"{prof} assigned to {course}.", parent=win)
        else:
            messagebox.showwarning("Error", "Could not assign (course may not exist).", parent=win)
        refresh_courses()

    def enroll_student():
        student, ok = askValidatedInput(win, "Enroll Student", "Enter student name:")
        if not ok or not student:
            return

        course = select_course_dialog(win, "Select Course")
        if not course:
            return

        student = cap(student)
        course = cap(course)

        if service.enroll_student(student, course):
            messagebox.showinfo("Success", f"{student} enrolled in {course}.", parent=win)
        else:
            messagebox.showwarning("Error", "Course not found or enrollment failed.", parent=win)

    # ---- Course action buttons ----
    btn_frame = tk.Frame(win)
    btn_frame.pack(pady=8)

    tk.Button(btn_frame, text="Add Course", width=20, command=add_course).grid(row=0, column=0, padx=10, pady=6)
    tk.Button(btn_frame, text="Delete Course", width=20, command=delete_course).grid(row=0, column=1, padx=10, pady=6)
    tk.Button(btn_frame, text="Assign Professor (Direct)", width=20, command=assign_professor_direct).grid(row=1, column=0, padx=10, pady=6)
    tk.Button(btn_frame, text="Enroll Student", width=20, command=enroll_student).grid(row=1, column=1, padx=10, pady=6)

    # ---- Pending Requests ----
    tk.Label(win, text="Pending Professor Requests", font=("Arial", 12, "bold")).pack(pady=(18, 0))

    req_list = tk.Listbox(win, width=65, height=7)
    req_list.pack(pady=8)

    def refresh_requests():
        req_list.delete(0, tk.END)
        try:
            reqs = service.get_pending_professor_requests()
        except Exception as e:
            req_list.insert(tk.END, f"Request feature not ready: {e}")
            return

        if not reqs:
            req_list.insert(tk.END, "No pending requests")
            return

        for prof, course, status in reqs:
            req_list.insert(tk.END, f"{prof}  ->  {course}  [{status}]")

    def _selected_request():
        if not req_list.curselection():
            return None
        text = req_list.get(req_list.curselection()[0])
        if "->" not in text:
            return None
        left, right = text.split("->")
        prof = left.strip()
        course = right.split("[")[0].strip()
        return prof, course

    def accept_request():
        sel = _selected_request()
        if not sel:
            return
        prof, course = sel

        ok = service.set_professor_request_status(prof, course, "accepted")
        if ok:
            messagebox.showinfo("Accepted", f"Accepted: {prof} assigned to {course}", parent=win)
        else:
            messagebox.showwarning("Failed", "Could not accept request.", parent=win)

        refresh_courses()
        refresh_requests()

    def reject_request():
        sel = _selected_request()
        if not sel:
            return
        prof, course = sel

        ok = service.set_professor_request_status(prof, course, "rejected")
        if ok:
            messagebox.showinfo("Rejected", f"Rejected: {prof} for {course}", parent=win)
        else:
            messagebox.showwarning("Failed", "Could not reject request.", parent=win)

        refresh_requests()

    req_btn = tk.Frame(win)
    req_btn.pack(pady=6)
    tk.Button(req_btn, text="Accept", width=12, command=accept_request).pack(side="left", padx=10)
    tk.Button(req_btn, text="Reject", width=12, command=reject_request).pack(side="left", padx=10)

    tk.Button(win, text="Close", command=root.destroy, width=12).pack(pady=10)

    refresh_courses()
    refresh_requests()


# ==================== PROFESSOR WINDOW ====================
def open_professor_panel(root):
    win = tk.Toplevel(root)
    win.title("Professor Panel")
    win.geometry("750x520")
    win.resizable(False, False)

    win.protocol("WM_DELETE_WINDOW", root.destroy)

    tk.Label(win, text="Professor Panel", font=("Arial", 16, "bold")).pack(pady=15)

    def professor_request_course():
        prof, ok = askValidatedInput(win, "Professor", "Enter your name:")
        if not ok or not prof:
            return

        course = select_course_dialog(win, "Select Course")
        if not course:
            return

        prof = cap(prof)
        course = cap(course)

        ok2 = service.request_professor_course(prof, course)
        if ok2:
            messagebox.showinfo("Requested", f"Request sent: {prof} -> {course} (pending)", parent=win)
        else:
            messagebox.showwarning("Failed", "Course not found or request failed.", parent=win)

    def professor_view_requests():
        prof, ok = askValidatedInput(win, "Professor", "Enter your name:")
        if not ok or not prof:
            return

        prof = cap(prof)
        rows = service.get_professor_requests(prof)

        if not rows:
            messagebox.showinfo("My Requests", "No requests found.", parent=win)
            return

        lines = [f"{course} : {status}" for (course, status) in rows]
        messagebox.showinfo("My Requests", "\n".join(lines), parent=win)

    def professor_view_courses():
        prof, ok = askValidatedInput(win, "Professor", "Enter your name:")
        if not ok or not prof:
            return

        prof = cap(prof)
        courses = professor_service.view_assigned_courses(prof)
        messagebox.showinfo(
            "Assigned Courses",
            "\n".join(courses) if courses else "No assigned courses.",
            parent=win
        )

    def professor_view_students():
        course = select_course_dialog(win, "Select Course")
        if not course:
            return

        course = cap(course)
        students = professor_service.view_enrolled_students(course)
        messagebox.showinfo(
            "Enrolled Students",
            "\n".join(students) if students else "No students enrolled.",
            parent=win
        )

    def professor_upload_grade():
        student, ok = askValidatedInput(win, "Grade", "Student name:")
        if not ok or not student:
            return

        course = select_course_dialog(win, "Select Course")
        if not course:
            return

        grade = simpledialog.askstring("Grade", "Grade (A/B/C or marks):", parent=win)
        if not grade:
            return

        student = cap(student)
        course = cap(course)

        ok2 = professor_service.upload_grades(student, course, grade)
        if ok2:
            messagebox.showinfo("Saved", "Grade saved.", parent=win)
        else:
            messagebox.showwarning("Failed", "Student not enrolled / wrong course / DB error.", parent=win)

    tk.Button(win, text="Request Course Assignment", command=professor_request_course, width=32).pack(pady=8)
    tk.Button(win, text="View My Request Status", command=professor_view_requests, width=32).pack(pady=8)

    tk.Button(win, text="View My Courses", command=professor_view_courses, width=32).pack(pady=8)
    tk.Button(win, text="View Students in Course", command=professor_view_students, width=32).pack(pady=8)
    tk.Button(win, text="Upload Student Grade", command=professor_upload_grade, width=32).pack(pady=8)

    tk.Button(win, text="Close", command=root.destroy, width=12).pack(pady=15)


# ====================== STUDENT WINDOW ====================
def open_student_panel(root):
    win = tk.Toplevel(root)
    win.title("Student Panel")
    win.geometry("750x480")
    win.resizable(False, False)

    win.protocol("WM_DELETE_WINDOW", root.destroy)

    tk.Label(win, text="Student Panel", font=("Arial", 16, "bold")).pack(pady=15)

    def student_register_course():
        student, ok = askValidatedInput(win, "Student Registration", "Enter your name:")
        if not ok or not student:
            return

        course = select_course_dialog(win, "Select Course")
        if not course:
            return

        student = cap(student)
        course = cap(course)

        ok2 = service.enroll_student(student, course)
        if ok2:
            messagebox.showinfo("Registered", f"{student} registered in {course}.", parent=win)
        else:
            messagebox.showwarning("Failed", "Course not found or registration failed.", parent=win)

    def student_view_courses():
        student, ok = askValidatedInput(win, "Student", "Enter your name:")
        if not ok or not student:
            return

        student = cap(student)
        courses = student_service.view_registered_courses(student)
        messagebox.showinfo(
            "My Courses",
            "\n".join(courses) if courses else "No courses found.",
            parent=win
        )

    def student_view_grade():
        student, ok = askValidatedInput(win, "Student", "Enter your name:")
        if not ok or not student:
            return

        course = select_course_dialog(win, "Select Course")
        if not course:
            return

        student = cap(student)
        course = cap(course)

        g = student_service.view_my_grade(student, course)
        messagebox.showinfo("My Grade", g if g else "No grade found yet.", parent=win)

    tk.Button(win, text="Register / Enroll in Course", command=student_register_course, width=32).pack(pady=10)
    tk.Button(win, text="View My Courses", command=student_view_courses, width=32).pack(pady=10)
    tk.Button(win, text="View My Grade", command=student_view_grade, width=32).pack(pady=10)

    tk.Button(win, text="Close", command=root.destroy, width=12).pack(pady=15)
