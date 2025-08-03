# main.py
import tkinter as tk
from gui import PersonalAssistantApp

if __name__ == "__main__":
    root = tk.Tk()
    app = PersonalAssistantApp(root)
    root.mainloop()