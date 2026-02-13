import tkinter as tk
from panels import init_ui, open_student_panel

root = tk.Tk()
root.title("Student App")
root.geometry("300x200")
root.resizable(False, False)

init_ui(root)
root.withdraw()
open_student_panel(root)

root.mainloop()
