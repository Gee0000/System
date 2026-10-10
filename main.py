import tkinter as tk
import backend
from frontend import LoginWindow

backend.create_database()

root = tk.Tk()

app = LoginWindow(root)

root.mainloop()