import tkinter as tk
from tkinter import ttk
from .signup_frame import SignupFrame
from .login_frame import LoginFrame
from ..utils.db_manager import DBManager
from ..interfaces.face_recognizer import FaceRecognizer


class FacialAuthApp:
    def __init__(self, recognizer: FaceRecognizer, db_manager: DBManager):
        self.root = tk.Tk()
        self.root.title("Reconocimiento Facial")
        self.root.geometry("800x600")

        self.recognizer = recognizer
        self.db_manager = db_manager

        self.notebook = ttk.Notebook(self.root)

        self.signup_frame = SignupFrame(self.notebook, recognizer, db_manager)
        self.login_frame = LoginFrame(self.notebook, recognizer, db_manager)

        self.notebook.add(self.signup_frame, text="Signup")
        self.notebook.add(self.login_frame, text="Login")
        self.notebook.pack()

    def run(self):
        self.root.mainloop()