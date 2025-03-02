import tkinter as tk
from tkinter import ttk, messagebox
import cv2
import time
import numpy as np
from PIL import Image, ImageTk
from .welcome_frame import WelcomeFrame
from ..utils.db_manager import DBManager
from ..interfaces.face_recognizer import FaceRecognizer


class LoginFrame(ttk.Frame):
    def __init__(self, parent, recognizer: FaceRecognizer, db_manager: DBManager):
        super().__init__(parent)
        self.recognizer = recognizer
        self.db_manager = db_manager
        self.login_window = None
        self.verification_history = []
        self.current_face_matches = {}
        self.setup_ui()

    def setup_ui(self):
        ttk.Button(self, text="Facial Login",
                   command=self.facial_login).pack()

    def facial_login(self):
        """
        Initiates facial recognition login process.
        Opens camera feed and continuously checks for matching faces.
        """
        cap = cv2.VideoCapture(0)
        login_window = tk.Toplevel(self)
        login_window.title("Facial Login")

        video_label = ttk.Label(login_window)
        video_label.pack()

        status_label = ttk.Label(login_window, text="Looking for face...")
        status_label.pack()

        self.verification_history = []
        self.current_face_matches = {}

        required_matches = 5
        tolerance = 0.45

        def update_frame():
            ret, frame = cap.read()
            if ret:
                frame = cv2.resize(frame, (0, 0), fx=0.75, fy=0.75)

                face_locations = self.recognizer.detect_faces(frame)

                for face_location in face_locations:
                    top, right, bottom, left = face_location
                    cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)

                if face_locations:
                    face_encoding = self.recognizer.get_face_encoding(frame)
                    if face_encoding is not None:
                        best_match = None
                        lowest_distance = float('inf')

                        # Verificar coincidencias con todos los usuarios
                        for username, user_data in self.db_manager.get_all_users().items():
                            stored_encoding = user_data["face_encoding"]
                            # Calcular distancia directamente
                            if isinstance(stored_encoding, list):
                                stored_encoding = np.array(stored_encoding)

                            distance = np.linalg.norm(stored_encoding - face_encoding)

                            # Actualizar el mejor match
                            if distance < lowest_distance:
                                lowest_distance = distance
                                best_match = username

                            # Guardar resultado de verificación
                            if distance <= tolerance:
                                if username not in self.current_face_matches:
                                    self.current_face_matches[username] = 0
                                self.current_face_matches[username] += 1

                                status_label.config(
                                    text=f"Verificando: {username} ({self.current_face_matches[username]}/{required_matches})")

                                if self.current_face_matches[username] >= required_matches:
                                    cap.release()
                                    login_window.destroy()
                                    self.show_welcome_screen(username)
                                    return

                        if lowest_distance <= tolerance:
                            status_label.config(
                                text=f"Verificando: {best_match} ({self.current_face_matches.get(best_match, 0)}/{required_matches})")
                        else:
                            status_label.config(text=f"Rostro no registrado (distancia: {lowest_distance:.2f})")
                    else:
                        status_label.config(text="Buscando rostro...")
                else:
                    status_label.config(text="Buscando rostro...")

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