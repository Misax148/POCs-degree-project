import tkinter as tk
from tkinter import ttk

from src.interfaces.face_recognizer import FaceRecognizer
from src.ui.cnn.login_frame import LoginFrameCNN
from src.ui.cnn.registration_frame import RegistrationFrame
from src.utils.db_manager import DBManager


class FacialAuthAppCNN:
    """
    Main application class for facial recognition.
    Creates a tabbed interface with registration and login tabs.
    """

    def __init__(self, recognizer: FaceRecognizer, db_manager: DBManager):
        self.root = tk.Tk()
        self.root.title("Reconocimiento Facial con CNN")
        self.root.geometry("600x500")

        self.recognizer = recognizer
        self.db_manager = db_manager

        # Create tabbed interface
        self.notebook = ttk.Notebook(self.root)

        # Create registration and login frames
        self.registration_frame = RegistrationFrame(self.notebook, recognizer, db_manager)
        self.login_frame = LoginFrameCNN(self.notebook, recognizer, db_manager)

        # Add frames to notebook
        self.notebook.add(self.registration_frame, text="Registro")
        self.notebook.add(self.login_frame, text="Login")
        self.notebook.pack(expand=True, fill='both', padx=10, pady=10)

    def run(self):
        """Starts the main application loop."""
        self.root.mainloop()