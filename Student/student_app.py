import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import tkinter as tk
from panels import init_ui, open_auth_window



root = tk.Tk()
root.title("Student App")
root.geometry("300x200")
root.resizable(False, False)

init_ui(root)

root.withdraw()
open_auth_window(root, "student")

root.mainloop()
