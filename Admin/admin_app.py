import tkinter as tk
from panels import init_ui, open_auth_window

root = tk.Tk()
root.title("Admin App")
root.geometry("300x200")
root.resizable(False, False)

init_ui(root)

root.withdraw()
open_auth_window(root, "admin")

root.mainloop()
