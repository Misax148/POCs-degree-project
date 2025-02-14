import tkinter as tk
from tkinter import ttk, messagebox
import cv2
from PIL import Image, ImageTk
from .welcome_frame import WelcomeFrame
from ..utils.db_manager import DBManager
from ..interfaces.face_recognizer import FaceRecognizer


class LoginFrame(ttk.Frame):
    def __init__(self, parent, recognizer: FaceRecognizer, db_manager: DBManager):
        super().__init__(parent)
        self.recognizer = recognizer
        self.db_manager = db_manager
        self.setup_ui()

    def setup_ui(self):
        ttk.Button(self, text="Facial Login",
                  command=self.facial_login).pack()

    def facial_login(self):
        cap = cv2.VideoCapture(0)
        login_window = tk.Toplevel(self)
        login_window.title("Facial Login")

        video_label = ttk.Label(login_window)
        video_label.pack()

        def update_frame():
            ret, frame = cap.read()
            if ret:
                face_locations = self.recognizer.detect_faces(frame)

                for face_location in face_locations:
                    top, right, bottom, left = face_location
                    cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)

                if face_locations:
                    face_encoding = self.recognizer.get_face_encoding(frame)
                    if face_encoding is not None:
                        for username, user_data in self.db_manager.get_all_users().items():
                            stored_encoding = user_data["face_encoding"]
                            if self.recognizer.compare_faces(stored_encoding, face_encoding):
                                cap.release()
                                login_window.destroy()
                                self.show_welcome_screen(username)
                                return

                cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                img = Image.fromarray(cv2image)
                imgtk = ImageTk.PhotoImage(image=img)
                video_label.imgtk = imgtk
                video_label.configure(image=imgtk)

            login_window.after(10, update_frame)

        update_frame()

        def on_closing():
            cap.release()
            login_window.destroy()

        login_window.protocol("WM_DELETE_WINDOW", on_closing)

    def show_welcome_screen(self, username):
        WelcomeFrame(self, self.db_manager, username)