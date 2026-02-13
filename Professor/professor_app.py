import tkinter as tk
from panels import init_ui, open_professor_panel

root = tk.Tk()
root.title("Professor App")
root.geometry("300x200")
root.resizable(False, False)

init_ui(root)

root.withdraw()
open_professor_panel(root)

root.mainloop()
