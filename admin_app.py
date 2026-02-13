import tkinter as tk
from panels import init_ui, open_admin_panel

root = tk.Tk()
root.title("Admin App")
root.geometry("300x200")
root.resizable(False, False)

init_ui(root)

root.withdraw()
open_admin_panel(root)

root.mainloop()
