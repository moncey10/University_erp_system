import tkinter as tk
from tkinter import simpledialog, messagebox
from course_service import CourseService

service = CourseService()

root = tk.Tk()
root.title("Course Manager (DB)")
root.geometry("300x300")

listbox = tk.Listbox(root)
listbox.pack(pady=10, fill="both", expand=True)


def is_valid_course_name(text):
    """
    Allow letters, numbers, spaces, and - : _
    BUT reject names that contain no letters (e.g., '45' should be invalid).
    """
    if not text or not text.strip():
        return False

    allowed_symbols = set("-:_")
    has_letter = False

    for ch in text.strip():
        if ch.isalpha():
            has_letter = True
        elif ch.isdigit() or ch.isspace() or ch in allowed_symbols:
            pass
        else:
            return False

    return has_letter


def refresh():
    listbox.delete(0, tk.END)
    courses = service.show_courses()
    for c in courses:
        listbox.insert(tk.END, c[0])


def add_course():
    name = simpledialog.askstring("Add Course", "Course name:")
    if name:
        if not is_valid_course_name(name):
            messagebox.showwarning(
                "Invalid Input",
                "Course name must contain at least ONE letter.\n"
                "Allowed: letters, numbers, spaces, hyphens (-), colons (:), underscores (_)."
            )
            return

        ok = service.add_course(name)
        if ok:
            refresh()
            messagebox.showinfo("Saved", "Saved in database (db1).")
        else:
            messagebox.showwarning("Error", "Could not save (maybe duplicate).")


tk.Button(root, text="Add Course", command=add_course).pack(pady=5)
tk.Button(root, text="Refresh", command=refresh).pack(pady=5)

refresh()
root.mainloop()
