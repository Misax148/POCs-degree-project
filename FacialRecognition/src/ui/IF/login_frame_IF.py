import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import cv2
import numpy as np
from PIL import Image, ImageTk
import os

from src.ui.cnn.result_frame import ResultFrame
from ...interfaces.face_recognizer import FaceRecognizer
from ...utils.db_manager import DBManager


class LoginFrameIF(ttk.Frame):
    """
    Frame for user login using facial recognition with InsightFace.
    Allows uploading a photo and verifying identity.
    """

    def __init__(self, parent, recognizer: FaceRecognizer, db_manager: DBManager):
        super().__init__(parent)
        self.recognizer = recognizer
        self.db_manager = db_manager
        self.current_image_path = None
        self.setup_ui()

    def setup_ui(self):
        """Sets up the user interface elements."""
        # Photo upload
        photo_frame = ttk.Frame(self)
        photo_frame.pack(fill='x', padx=20, pady=20)

        self.upload_btn = ttk.Button(photo_frame, text="Subir Foto",
                                     command=self.upload_image)
        self.upload_btn.pack(side=tk.LEFT, padx=5)

        self.photo_label = ttk.Label(photo_frame, text="No se ha seleccionado ninguna foto")
        self.photo_label.pack(side=tk.LEFT, padx=5)

        # Image preview
        self.image_frame = ttk.Frame(self)
        self.image_frame.pack(fill='both', expand=True, padx=20, pady=10)

        self.image_label = ttk.Label(self.image_frame)
        self.image_label.pack(pady=10)

        # Verify button
        self.verify_btn = ttk.Button(self, text="Verificar Identidad",
                                     command=self.verify_identity)
        self.verify_btn.pack(pady=20)

    def upload_image(self):
        """Handles image upload for login."""
        file_path = filedialog.askopenfilename(
            filetypes=[("Archivos de imagen", "*.jpg *.jpeg *.png")]
        )
        if file_path:
            self.current_image_path = file_path
            self.photo_label.config(text=os.path.basename(file_path))

            # Show image preview
            image = Image.open(file_path)
            image = image.resize((200, 200))
            photo = ImageTk.PhotoImage(image)
            self.image_label.configure(image=photo)
            self.image_label.image = photo

    def verify_identity(self):
        """
        Verifies user identity using facial recognition.
        Compares the uploaded photo with stored user data.
        """
        if not self.current_image_path:
            messagebox.showerror("Error", "Por favor suba una foto")
            return

        # Show processing message
        processing_window = tk.Toplevel(self)
        processing_window.title("Procesando")
        processing_window.geometry("300x100")
        processing_label = ttk.Label(processing_window, text="Procesando imagen...")
        processing_label.pack(padx=20, pady=20)
        processing_window.update()

        # Detect face in the image using InsightFace
        face_encoding = self.recognizer.get_face_encoding(self.current_image_path)

        processing_window.destroy()

        if face_encoding is None:
            messagebox.showerror("Error", "No se detecto ningun rostro en la imagen")
            return

        # Find matching user
        best_match = None
        lowest_distance = float('inf')
        match_distance = 0

        # Check all users
        for username, user_data in self.db_manager.get_all_users().items():
            stored_encoding = user_data["face_encoding"]
            if isinstance(stored_encoding, list):
                stored_encoding = np.array(stored_encoding)

            # Normalizar vectores para similitud de coseno
            stored_norm = stored_encoding / np.linalg.norm(stored_encoding)
            face_norm = face_encoding / np.linalg.norm(face_encoding)

            # Calcular similitud de coseno
            similarity = np.dot(stored_norm, face_norm)
            distance = 1.0 - similarity  # Convertir similitud a distancia

            # Update best match
            if distance < lowest_distance:
                lowest_distance = distance
                best_match = username
                match_distance = distance

        # Show result
        tolerance = self.recognizer.default_tolerance
        if best_match and lowest_distance <= tolerance:
            # Show successful login screen
            ResultFrame(self, self.db_manager, best_match, match_distance, tolerance)
        else:
            message = f"No se encontro coincidencia. "
            if best_match:
                message += f"La mas cercana fue '{best_match}' con distancia {lowest_distance:.4f} (umbral: {tolerance})"
            else:
                message += "No hay usuarios registrados."
            messagebox.showerror("Error", message)